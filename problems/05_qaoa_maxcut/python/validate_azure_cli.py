"""Preflight checks for Azure CLI readiness in QAOA Azure workflows."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from azure_env import AzureEnvError, load_azure_env


def _run_az(args: list[str], timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["az", *args],
        capture_output=True,
        text=True,
        check=True,
        timeout=timeout_seconds,
    )


def _parse_json(stdout: str, context: str) -> dict:
    payload = json.loads(stdout)
    if not isinstance(payload, dict):
        raise ValueError(f"{context}: expected JSON object")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Azure CLI and workspace readiness for QAOA workflows.")
    parser.add_argument(
        "--env-file",
        default="problems/05_qaoa_maxcut/.env.azure.local",
        help="Path to manual Azure env file.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Timeout in seconds for each Azure CLI call.",
    )
    args = parser.parse_args()

    env_path = Path(args.env_file)
    if not env_path.is_absolute():
        env_path = (Path.cwd() / env_path).resolve()

    try:
        azure_env = load_azure_env(env_path)
    except (FileNotFoundError, AzureEnvError) as exc:
        raise SystemExit(f"Azure CLI preflight blocked: {exc}")

    try:
        account = _parse_json(_run_az(["account", "show", "--output", "json"], args.timeout).stdout, "az account show")
    except FileNotFoundError:
        raise SystemExit("Azure CLI preflight failed: 'az' command not found on PATH.")
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() if exc.stderr else str(exc)
        raise SystemExit(f"Azure CLI preflight failed: az account show error: {detail}")
    except (subprocess.TimeoutExpired, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"Azure CLI preflight failed: az account show parse/timeout error: {exc}")

    current_subscription = str(account.get("id", "")).strip()
    required_subscription = azure_env["AZURE_SUBSCRIPTION_ID"].strip()
    if current_subscription and current_subscription.lower() != required_subscription.lower():
        try:
            _run_az(["account", "set", "--subscription", required_subscription], args.timeout)
        except subprocess.CalledProcessError as exc:
            detail = exc.stderr.strip() if exc.stderr else str(exc)
            raise SystemExit(f"Azure CLI preflight failed: unable to set subscription '{required_subscription}': {detail}")
        except subprocess.TimeoutExpired as exc:
            raise SystemExit(f"Azure CLI preflight failed: setting subscription timed out: {exc}")

    try:
        _run_az(["extension", "show", "--name", "quantum", "--output", "json"], args.timeout)
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() if exc.stderr else str(exc)
        raise SystemExit(
            "Azure CLI preflight failed: 'quantum' extension is missing. "
            "Install it with 'az extension add --name quantum'. "
            f"Details: {detail}"
        )
    except subprocess.TimeoutExpired as exc:
        raise SystemExit(f"Azure CLI preflight failed: extension check timed out: {exc}")

    try:
        _run_az(
            [
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
            args.timeout,
        )
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() if exc.stderr else str(exc)
        raise SystemExit(
            "Azure CLI preflight failed: cannot access configured Azure Quantum workspace. "
            f"Details: {detail}"
        )
    except subprocess.TimeoutExpired as exc:
        raise SystemExit(f"Azure CLI preflight failed: workspace check timed out: {exc}")

    print("Azure CLI preflight passed")
    print(f"  env_file: {env_path}")
    print(f"  subscription: {required_subscription}")
    print(f"  resource_group: {azure_env['AZURE_RESOURCE_GROUP']}")
    print(f"  workspace: {azure_env['AZURE_QUANTUM_WORKSPACE']}")


if __name__ == "__main__":
    main()
