"""Collect Azure job status and stamp generic problem manifest."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Dict

from azure_env import AzureEnvError, load_azure_env

ALLOWED = {"running", "succeeded", "failed", "cancelled"}


def _resolve(path_arg: str) -> Path:
    path = Path(path_arg)
    if path.is_absolute():
        return path
    return (Path.cwd() / path).resolve()


def _normalize(raw: str) -> str:
    normalized = raw.strip().lower()
    if normalized in {"waiting", "queued", "executing"}:
        return "running"
    if normalized in ALLOWED:
        return normalized
    raise ValueError(f"Unsupported Azure status '{raw}'")


def _fetch(job_id: str, azure_env: Dict[str, str], timeout: int) -> str:
    cmd = [
        "az", "quantum", "job", "show",
        "--workspace-name", azure_env["AZURE_QUANTUM_WORKSPACE"],
        "--resource-group", azure_env["AZURE_RESOURCE_GROUP"],
        "--job-id", job_id,
        "--output", "json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout)
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise ValueError("Azure CLI returned invalid job payload")
    return _normalize(str(payload.get("status", "")))


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect Azure job status into a generic problem manifest.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--result-status", choices=sorted(ALLOWED), default=None)
    parser.add_argument("--fetch-from-azure", action="store_true", default=False)
    parser.add_argument("--az-timeout", type=int, default=120)
    args = parser.parse_args()

    manifest_path = _resolve(args.manifest)
    env_path = _resolve(args.env_file)

    try:
        azure_env = load_azure_env(env_path)
    except (FileNotFoundError, AzureEnvError) as exc:
        raise SystemExit(f"Azure collect blocked: {exc}")

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    submission = payload.setdefault("submission", {})
    job_id = submission.get("job_id")
    if not isinstance(job_id, str) or not job_id.strip():
        raise SystemExit("Manifest does not contain submission.job_id")

    if args.fetch_from_azure:
        try:
            status = _fetch(job_id, azure_env, args.az_timeout)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError, ValueError) as exc:
            raise SystemExit(f"Azure status fetch failed: {exc}")
    else:
        if not args.result_status:
            raise SystemExit("Provide --result-status or pass --fetch-from-azure")
        status = args.result_status

    submission["status"] = status
    submission["result_status"] = status

    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("Azure collect complete")
    print(f"  manifest: {manifest_path}")
    print(f"  job_id: {job_id}")
    print(f"  status: {status}")


if __name__ == "__main__":
    main()
