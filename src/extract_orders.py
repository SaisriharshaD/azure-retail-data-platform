import argparse
import csv
import os

import psycopg
from dotenv import load_dotenv

from src.settings import PROJECT_ROOT, load_settings


def main():
    parser = argparse.ArgumentParser(
        description="Extract orders from the local development database."
    )
    parser.add_argument("--env", choices=["dev"], required=True)
    args = parser.parse_args()

    settings = load_settings(args.env)
    load_dotenv(PROJECT_ROOT / ".env")

    required_variables = [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]

    missing = [
        name for name in required_variables
        if not os.environ.get(name)
    ]

    if missing:
        raise ValueError(f"Missing database settings: {', '.join(missing)}")

    output_dir = settings["source_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "orders.csv"

    query = """
        SELECT
            order_id,
            customer_id,
            order_date,
            order_amount,
            currency,
            order_status,
            updated_at
        FROM orders
        ORDER BY order_id
    """

    with psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=10,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)

            fields = [column.name for column in cursor.description]
            count = 0

            with output_file.open(
                "w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.writer(file)
                writer.writerow(fields)

                for row in cursor:
                    writer.writerow(row)
                    count += 1

    print(f"Environment: {settings['environment']}")
    print(f"Extracted: {count} orders")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()