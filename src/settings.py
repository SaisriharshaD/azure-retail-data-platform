import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_settings(environment):
    allowed_environments = {"dev", "uat", "prod"}

    if environment not in allowed_environments:
        raise ValueError(
            f"Unknown environment: {environment}. "
            "Choose dev, uat, or prod."
        )

    config_file = PROJECT_ROOT / "config" / f"{environment}.json"

    with config_file.open("r", encoding="utf-8") as file:
        settings = json.load(file)

    if settings["environment"] != environment:
        raise ValueError("Configuration environment does not match")

    return {
        "environment": environment,
        "source_dir": PROJECT_ROOT / settings["source_dir"],
        "validated_dir": PROJECT_ROOT / settings["validated_dir"],
    }