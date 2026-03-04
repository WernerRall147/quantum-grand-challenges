"""Manually stamp Azure submission metadata into a QAOA manifest after real cloud submission."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from azure_env import AzureEnvError, load_azure_env


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser(description="Record Azure submission metadata in a QAOA manifest.")
    parser.add_argument(
        "--manifest",
        default="problems/05_qaoa_maxcut/estimates/azure_job_manifest_small_d3.json",
        help="Path to Azure manifest JSON.",
    )
    parser.add_argument(
        "--env-file",
        default="problems/05_qaoa_maxcut/.env.azure.local",
        help="Path to manual Azure env file.",
    )
    parser.add_argument(
        "--manual-job-id",
        required=True,
        help="Azure job id copied from the real submission (manual gate).",
    )
    parser.add_argument(
        "--status",
        default="submitted",
        choices=["submitted", "running", "succeeded", "failed", "cancelled"],
        help="Submission status to record.",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = (Path.cwd() / manifest_path).resolve()

    env_path = Path(args.env_file)
    if not env_path.is_absolute():
        env_path = (Path.cwd() / env_path).resolve()

    try:
        azure_env = load_azure_env(env_path)
    except (FileNotFoundError, AzureEnvError) as exc:
        raise SystemExit(f"Azure submission blocked: {exc}")

    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    backend = payload.setdefault("backend", {})
    backend["provider"] = azure_env.get("AZURE_QUANTUM_PROVIDER", backend.get("provider", "azure-quantum"))
    backend["target_id"] = azure_env.get("AZURE_QUANTUM_TARGET_ID", backend.get("target_id", "microsoft.estimator"))
    workspace = backend.setdefault("workspace", {})
    workspace["subscription_id"] = azure_env["AZURE_SUBSCRIPTION_ID"]
    workspace["resource_group"] = azure_env["AZURE_RESOURCE_GROUP"]
    workspace["workspace_name"] = azure_env["AZURE_QUANTUM_WORKSPACE"]
    workspace["location"] = azure_env["AZURE_LOCATION"]

    submission = payload.setdefault("submission", {})
    submission["status"] = args.status
    submission["submitted_utc"] = submission.get("submitted_utc") or utc_now()
    submission["job_id"] = args.manual_job_id
    submission["result_status"] = submission.get("result_status")

    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Updated Azure submission metadata: {manifest_path}")
    print(f"  job_id: {args.manual_job_id}")
    print(f"  status: {args.status}")


if __name__ == "__main__":
    main()
