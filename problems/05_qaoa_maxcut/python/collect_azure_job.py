"""Record Azure result status metadata for a previously submitted QAOA manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from azure_env import AzureEnvError, load_azure_env

ALLOWED_RESULT_STATUSES = {"running", "succeeded", "failed", "cancelled"}


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
        required=True,
        choices=sorted(ALLOWED_RESULT_STATUSES),
        help="Result status copied from Azure job details.",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = (Path.cwd() / manifest_path).resolve()

    env_path = Path(args.env_file)
    if not env_path.is_absolute():
        env_path = (Path.cwd() / env_path).resolve()

    try:
        _ = load_azure_env(env_path)
    except (FileNotFoundError, AzureEnvError) as exc:
        raise SystemExit(f"Azure result collection blocked: {exc}")

    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    submission = payload.setdefault("submission", {})

    job_id = submission.get("job_id")
    if not isinstance(job_id, str) or not job_id.strip():
        raise ValueError("Manifest does not contain submission.job_id. Run submit_azure_job.py first.")

    submission["result_status"] = args.result_status
    submission["status"] = args.result_status

    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Updated Azure result metadata: {manifest_path}")
    print(f"  job_id: {job_id}")
    print(f"  result_status: {args.result_status}")


if __name__ == "__main__":
    main()
