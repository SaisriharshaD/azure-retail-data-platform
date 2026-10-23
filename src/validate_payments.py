import argparse
import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

from src.settings import load_settings


def validate_payment(payment):
    errors = []

    for field in ["payment_id", "order_id"]:
        value = payment.get(field)

        if not isinstance(value, str) or not value.strip():
            errors.append(f"Missing or invalid {field}")

    amount_text = payment.get("amount")

    if not isinstance(amount_text, str):
        errors.append("Amount must be a decimal string")
    else:
        try:
            amount = Decimal(amount_text)

            if not amount.is_finite() or amount <= 0:
                errors.append("Amount must be finite and greater than zero")
        except InvalidOperation:
            errors.append("Invalid payment amount")

    if payment.get("currency") != "USD":
        errors.append("Unsupported currency: expected USD")

    if payment.get("status") not in {"CAPTURED", "FAILED", "PENDING"}:
        errors.append("Unsupported payment status")

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate an explicitly selected payment extraction."
    )
    parser.add_argument("--env", choices=["dev"], required=True)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()

    settings = load_settings(args.env)

    with args.input.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, dict):
        raise ValueError("Input must be a JSON object")

    payments = payload.get("payments")

    if not isinstance(payments, list):
        raise ValueError("Input must contain a payments list")

    accepted = []
    rejected = []
    seen_ids = set()

    for payment in payments:
        if not isinstance(payment, dict):
            rejected.append({
                "record": payment,
                "rejection_reasons": ["Payment must be a JSON object"],
            })
            continue

        errors = validate_payment(payment)
        payment_id = payment.get("payment_id")

        if isinstance(payment_id, str) and payment_id.strip():
            if payment_id in seen_ids:
                errors.append("Duplicate payment_id")
            seen_ids.add(payment_id)

        if errors:
            rejected.append({
                "record": payment,
                "rejection_reasons": errors,
            })
        else:
            accepted.append(payment)

    if len(payments) != len(accepted) + len(rejected):
        raise RuntimeError("Payment count reconciliation failed")

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output_dir = settings["validated_dir"] / "payments" / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "accepted_payments.json": accepted,
        "rejected_payments.json": rejected,
        "run_summary.json": {
            "run_id": run_id,
            "environment": settings["environment"],
            "source_file": str(args.input.resolve()),
            "status": "SUCCEEDED",
            "input_count": len(payments),
            "accepted_count": len(accepted),
            "rejected_count": len(rejected),
            "reconciliation_passed": True,
        },
    }

    for filename, content in outputs.items():
        with (output_dir / filename).open("w", encoding="utf-8") as file:
            json.dump(content, file, indent=4)

    print(f"Input: {len(payments)}")
    print(f"Accepted: {len(accepted)}")
    print(f"Rejected: {len(rejected)}")
    print(f"Files saved to: {output_dir}")


if __name__ == "__main__":
    main()