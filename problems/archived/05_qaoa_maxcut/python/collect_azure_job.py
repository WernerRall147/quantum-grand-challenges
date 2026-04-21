"""Record Azure result status metadata for a previously submitted QAOA manifest."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Dict

from azure_env import AzureEnvError, load_azure_env

ALLOWED_RESULT_STATUSES = {"running", "succeeded", "failed", "cancelled"}


def _normalize_azure_status(raw: str) -> str:
    normalized = raw.strip().lower()
    if normalized in {"waiting", "queued", "executing"}:
        return "running"
    if normalized in ALLOWED_RESULT_STATUSES:
        return normalized
    raise ValueError(f"Unsupported Azure job status '{raw}'")


def _fetch_status_from_azure(job_id: str, azure_env: Dict[str, str], timeout_seconds: int) -> str:
    cmd = [
        "az",
        "quantum",
        "job",
        "show",
        "--workspace-name",
        azure_env["AZURE_QUANTUM_WORKSPACE"],
        "--resource-group",
        azure_env["AZURE_RESOURCE_GROUP"],
        "--job-id",
        job_id,
        "--output",
        "json",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
        timeout=timeout_seconds,
    )

    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise ValueError("Azure CLI returned invalid job payload")
    raw_status = str(payload.get("status", "")).strip()
    if not raw_status:
        raise ValueError("Azure CLI response did not include a job status")
    return _normalize_azure_status(raw_status)


def main() -> None:
    parser = argparse.ArgumentParser(description="Record Azure job result status in a QAOA manifest.")
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
        "--result-status",
        required=False,
        choices=sorted(ALLOWED_RESULT_STATUSES),
        help="Result status copied from Azure job details (manual mode).",
    )
    parser.add_argument(
        "--fetch-from-azure",
        action="store_true",
        default=False,
        help="Query Azure CLI (az quantum job show) for current status instead of requiring --result-status.",
    )
    parser.add_argument(
        "--az-timeout",
        type=int,
        default=120,
        help="Timeout in seconds for Azure CLI status query.",
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
        raise SystemExit(f"Azure result collection blocked: {exc}")

    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    submission = payload.setdefault("submission", {})

    job_id = submission.get("job_id")
    if not isinstance(job_id, str) or not job_id.strip():
        raise ValueError("Manifest does not contain submission.job_id. Run submit_azure_job.py first.")

    result_status = args.result_status
    if args.fetch_from_azure:
        try:
            result_status = _fetch_status_from_azure(job_id, azure_env, timeout_seconds=args.az_timeout)
        except subprocess.CalledProcessError as exc:
            detail = exc.stderr.strip() if exc.stderr else str(exc)
            raise SystemExit(f"Azure CLI status query failed: {detail}")
        except (subprocess.TimeoutExpired, json.JSONDecodeError, ValueError) as exc:
            raise SystemExit(f"Azure CLI status query failed: {exc}")
    elif not result_status:
        raise ValueError("Either provide --result-status or pass --fetch-from-azure.")

    submission["result_status"] = result_status
    submission["status"] = result_status

    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Updated Azure result metadata: {manifest_path}")
    print(f"  job_id: {job_id}")
    print(f"  result_status: {result_status}")


if __name__ == "__main__":
    main()
