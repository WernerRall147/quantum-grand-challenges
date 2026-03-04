"""Validate Azure CLI prerequisites for shared workflows."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from azure_env import AzureEnvError, load_azure_env


def _run(cmd: list[str], timeout: int) -> dict:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout)
    payload = json.loads(result.stdout) if result.stdout.strip() else {}
    return payload if isinstance(payload, dict) else {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Azure CLI login and workspace readiness.")
    parser.add_argument("--env-file", default="problems/05_qaoa_maxcut/.env.azure.local")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    env_path = Path(args.env_file)
    if not env_path.is_absolute():
        env_path = (Path.cwd() / env_path).resolve()

    try:
        azure_env = load_azure_env(env_path)
    except (FileNotFoundError, AzureEnvError) as exc:
        raise SystemExit(f"Azure CLI preflight failed: {exc}")

    try:
        account = _run(["az", "account", "show", "--output", "json"], args.timeout)
    except FileNotFoundError:
        raise SystemExit("Azure CLI preflight failed: 'az' command not found on PATH.")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        raise SystemExit(f"Azure CLI preflight failed on 'az account show': {exc}")

    current_subscription = str(account.get("id", "")).strip()
    expected_subscription = azure_env["AZURE_SUBSCRIPTION_ID"]

    if current_subscription and current_subscription.lower() != expected_subscription.lower():
        print("Warning: active Azure subscription differs from env file")
        print(f"  active:   {current_subscription}")
        print(f"  expected: {expected_subscription}")

    try:
        subprocess.run(
            [
                "az",
                "quantum",
                "workspace",
                "show",
                "--resource-group",
                azure_env["AZURE_RESOURCE_GROUP"],
                "--workspace-name",
                azure_env["AZURE_QUANTUM_WORKSPACE"],
                "--output",
                "json",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=args.timeout,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise SystemExit(f"Azure CLI preflight failed on workspace validation: {exc}")

    print("Azure CLI preflight passed")
    print(f"  workspace: {azure_env['AZURE_QUANTUM_WORKSPACE']}")
    print(f"  resource_group: {azure_env['AZURE_RESOURCE_GROUP']}")
    print(f"  location: {azure_env['AZURE_LOCATION']}")


if __name__ == "__main__":
    main()
