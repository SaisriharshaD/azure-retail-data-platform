import argparse
import csv
from decimal import Decimal, InvalidOperation

from src.settings import load_settings


def validate_order(order):
    errors = []

    if order["customer_id"].strip() == "":
        errors.append("Missing customer ID")

    try:
        amount = Decimal(order["order_amount"])

        if not amount.is_finite():
            errors.append("Order amount must be a finite number")
        elif amount <= 0:
            errors.append("Order amount must be greater than zero")

    except InvalidOperation:
        errors.append("Invalid order amount")

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate orders for a selected environment."
    )
    parser.add_argument(
        "--env",
        choices=["dev", "uat", "prod"],
        required=True,
    )
    args = parser.parse_args()

    settings = load_settings(args.env)

    input_file = settings["source_dir"] / "orders.csv"
    output_dir = settings["validated_dir"]

    with input_file.open("r", newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        fields = reader.fieldnames

        if fields is None:
            raise ValueError("Input CSV is empty: missing header")

        required_fields = {"order_id", "customer_id", "order_amount"}
        missing_fields = required_fields - set(fields)

        if missing_fields:
            raise ValueError(
                f"Missing required columns: {sorted(missing_fields)}"
            )

        output_dir.mkdir(parents=True, exist_ok=True)

        accepted_path = output_dir / "accepted_orders.csv"
        rejected_path = output_dir / "rejected_orders.csv"

        with (
            accepted_path.open("w", newline="", encoding="utf-8") as accepted_file,
            rejected_path.open("w", newline="", encoding="utf-8") as rejected_file,
        ):
            accepted_writer = csv.DictWriter(
                accepted_file,
                fieldnames=fields,
            )
            rejected_writer = csv.DictWriter(
                rejected_file,
                fieldnames=fields + ["rejection_reasons"],
            )

            accepted_writer.writeheader()
            rejected_writer.writeheader()

            input_count = 0
            accepted_count = 0
            rejected_count = 0

            for order in reader:
                input_count += 1
                errors = validate_order(order)

                if errors:
                    rejected_writer.writerow({
                        **order,
                        "rejection_reasons": "; ".join(errors),
                    })
                    rejected_count += 1
                else:
                    accepted_writer.writerow(order)
                    accepted_count += 1

    print(f"Environment: {settings['environment']}")
    print(f"Input: {input_count}")
    print(f"Accepted: {accepted_count}")
    print(f"Rejected: {rejected_count}")

    if input_count != accepted_count + rejected_count:
        raise RuntimeError(
            "Reconciliation failed: record counts do not match"
        )

    print("Reconciliation passed")
    print(f"Files saved to: {output_dir}")


if __name__ == "__main__":
    main()