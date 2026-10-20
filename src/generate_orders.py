import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "source"
OUTPUT_FILE = OUTPUT_DIR / "orders.csv"

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
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=orders[0].keys())
        writer.writeheader()
        writer.writerows(orders)

    print(f"Generated {len(orders)} orders.")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()