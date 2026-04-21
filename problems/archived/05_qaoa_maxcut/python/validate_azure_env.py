"""Validate manual Azure environment settings used by QAOA Azure workflows."""

from __future__ import annotations

import argparse
from pathlib import Path

from azure_env import AzureEnvError, load_azure_env


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Azure environment file for QAOA workflows.")
    parser.add_argument(
        "--env-file",
        default="problems/05_qaoa_maxcut/.env.azure.local",
        help="Path to Azure env file (manual, not committed).",
    )
    args = parser.parse_args()

    env_path = Path(args.env_file)
    if not env_path.is_absolute():
        env_path = (Path.cwd() / env_path).resolve()

    try:
        values = load_azure_env(env_path)
    except (FileNotFoundError, AzureEnvError) as exc:
        raise SystemExit(f"Azure env validation failed: {exc}")

    print("Azure env validation passed")
    print(f"  file: {env_path}")
    print(f"  subscription: {values['AZURE_SUBSCRIPTION_ID']}")
    print(f"  workspace: {values['AZURE_QUANTUM_WORKSPACE']}")
    print(f"  resource-group: {values['AZURE_RESOURCE_GROUP']}")
    print(f"  location: {values['AZURE_LOCATION']}")


if __name__ == "__main__":
    main()
