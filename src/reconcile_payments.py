import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from src.settings import load_settings


def main():
    parser = argparse.ArgumentParser(
        description="Compare validated orders with validated payments."
    )
    parser.add_argument("--env", choices=["dev"], required=True)
    parser.add_argument("--orders", type=Path, required=True)
    parser.add_argument("--payments", type=Path, required=True)
    args = parser.parse_args()

    settings = load_settings(args.env)

    with args.orders.open("r", newline="", encoding="utf-8") as file:
        orders = list(csv.DictReader(file))

    with args.payments.open("r", encoding="utf-8") as file:
        payments = json.load(file)

    if not isinstance(payments, list):
        raise ValueError("Expected an accepted-payments JSON list")

    order_ids = [order["order_id"] for order in orders]

    if len(order_ids) != len(set(order_ids)):
        raise ValueError("Duplicate order IDs in input")

    payment_ids = [payment["payment_id"] for payment in payments]

    if len(payment_ids) != len(set(payment_ids)):
        raise ValueError("Duplicate payment IDs in input")

    # Group payments so one order can have multiple transactions.
    payments_by_order = defaultdict(list)

    for payment in payments:
        payments_by_order[payment["order_id"]].append(payment)

    results = []

    for order in orders:
        order_id = order["order_id"]
        order_amount = Decimal(order["order_amount"])
        linked_payments = payments_by_order.get(order_id, [])

        captured = [
            payment
            for payment in linked_payments
            if payment["status"] == "CAPTURED"
        ]

        same_currency = [
            payment
            for payment in captured
            if payment["currency"] == order["currency"]
        ]

        captured_amount = sum(
            (Decimal(payment["amount"]) for payment in same_currency),
            Decimal("0.00"),
        )

        if not linked_payments:
            status = "MISSING_PAYMENT"
        elif not captured:
            status = "NO_CAPTURED_PAYMENT"
        elif len(same_currency) != len(captured):
            status = "CURRENCY_MISMATCH"
        elif captured_amount == order_amount:
            status = "MATCHED"
        else:
            status = "AMOUNT_MISMATCH"

        results.append({
            "order_id": order_id,
            "currency": order["currency"],
            "order_amount": str(order_amount),
            "captured_amount": str(captured_amount),
            "difference": str(order_amount - captured_amount),
            "reconciliation_status": status,
        })

    known_orders = set(order_ids)
    orphan_payments = [
        payment
        for payment in payments
        if payment["order_id"] not in known_orders
    ]

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output_dir = settings["validated_dir"] / "reconciliation" / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    fields = [
        "order_id",
        "currency",
        "order_amount",
        "captured_amount",
        "difference",
        "reconciliation_status",
    ]

    with (output_dir / "order_payment_report.csv").open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    with (output_dir / "unmatched_payments.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(orphan_payments, file, indent=4)

    summary = {
        "run_id": run_id,
        "environment": settings["environment"],
        "orders_file": str(args.orders.resolve()),
        "payments_file": str(args.payments.resolve()),
        "orders_evaluated": len(results),
        "matched_orders": sum(
            row["reconciliation_status"] == "MATCHED"
            for row in results
        ),
        "orders_with_exceptions": sum(
            row["reconciliation_status"] != "MATCHED"
            for row in results
        ),
        "payments_without_accepted_order": len(orphan_payments),
        "status": "SUCCEEDED",
    }

    with (output_dir / "run_summary.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(summary, file, indent=4)

    for result in results:
        print(
            f"{result['order_id']}: "
            f"{result['reconciliation_status']}"
        )

    print(f"Payments without accepted order: {len(orphan_payments)}")
    print(f"Files saved to: {output_dir}")


if __name__ == "__main__":
    main()