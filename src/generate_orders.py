import argparse
import csv

from src.settings import load_settings


orders = [
    {
        "order_id": "ORD-1001",
        "customer_id": "CUST-001",
        "order_date": "2026-10-20",
        "order_amount": "200.00",
        "currency": "USD",
        "order_status": "PLACED",
    },
    {
        "order_id": "ORD-1002",
        "customer_id": "CUST-002",
        "order_date": "2026-10-20",
        "order_amount": "75.50",
        "currency": "USD",
        "order_status": "SHIPPED",
    },
    {
        "order_id": "ORD-1003",
        "customer_id": "",
        "order_date": "2026-10-20",
        "order_amount": "-25.00",
        "currency": "USD",
        "order_status": "PLACED",
    },
    {
        "order_id": "ORD-1004",
        "customer_id": "CUST-004",
        "order_date": "2026-10-20",
        "order_amount": "abc",
        "currency": "USD",
        "order_status": "PLACED",
    },
]


def main():
    parser = argparse.ArgumentParser(
        description="Generate sample orders for a selected environment."
    )
    parser.add_argument(
        "--env",
        choices=["dev", "uat", "prod"],
        required=True,
    )
    args = parser.parse_args()

    settings = load_settings(args.env)

    output_dir = settings["source_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "orders.csv"

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=orders[0].keys())
        writer.writeheader()
        writer.writerows(orders)

    print(f"Environment: {settings['environment']}")
    print(f"Generated {len(orders)} orders.")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()