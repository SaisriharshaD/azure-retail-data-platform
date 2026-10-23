import argparse
import json
from datetime import datetime, timezone
from urllib.request import urlopen

from src.settings import load_settings


def main():
    parser = argparse.ArgumentParser(
        description="Extract payments from the local development API."
    )
    parser.add_argument("--env", choices=["dev"], required=True)
    args = parser.parse_args()

    settings = load_settings(args.env)
    api_url = "http://127.0.0.1:8000/payments"

    # Fetch the response before creating an output file.
    with urlopen(api_url, timeout=10) as response:
        payload = json.load(response)

    # Check the basic response structure.
    if not isinstance(payload, dict):
        raise ValueError("API response must be a JSON object")

    payments = payload.get("payments")

    if not isinstance(payments, list):
        raise ValueError("API response must contain a payments list")

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")

    output_dir = settings["source_dir"] / "payments" / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "payments.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=4)

    print(f"Environment: {settings['environment']}")
    print(f"Extracted: {len(payments)} payments")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()