"""Collect Azure job status and stamp generic problem manifest."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from azure_env import AzureEnvError, load_azure_env

ALLOWED = {"running", "succeeded", "failed", "cancelled"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def _run_az(args: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
    cmdline = subprocess.list2cmdline(["az", *args])
    return subprocess.run(cmdline, shell=True, capture_output=True, text=True, check=True, timeout=timeout)


def _fetch(job_id: str, azure_env: Dict[str, str], timeout: int) -> str:
    cmd = [
        "quantum", "job", "show",
        "--workspace-name", azure_env["AZURE_QUANTUM_WORKSPACE"],
        "--resource-group", azure_env["AZURE_RESOURCE_GROUP"],
        "--job-id", job_id,
        "--output", "json",
    ]
    result = _run_az(cmd, timeout)
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise ValueError("Azure CLI returned invalid job payload")
    return _normalize(str(payload.get("status", "")))


def _record_successful_run(payload: Dict[str, Any], manifest_path: Path) -> None:
    submission = payload.get("submission", {}) if isinstance(payload.get("submission"), dict) else {}
    status = str(submission.get("status", "")).strip().lower()
    result_status = str(submission.get("result_status", "")).strip().lower()
    if status != "succeeded" and result_status != "succeeded":
        return

    job_id = str(submission.get("job_id", "")).strip()
    if not job_id:
        return

    backend = payload.get("backend", {}) if isinstance(payload.get("backend"), dict) else {}
    workspace = backend.get("workspace", {}) if isinstance(backend.get("workspace"), dict) else {}
    history_path = Path(__file__).resolve().parent / "run_history.json"

    if history_path.exists():
        history = json.loads(history_path.read_text(encoding="utf-8"))
        if not isinstance(history, dict):
            history = {}
    else:
        history = {}

    runs = history.get("runs") if isinstance(history.get("runs"), list) else []
    if any(isinstance(entry, dict) and str(entry.get("job_id", "")).strip() == job_id for entry in runs):
        return

    runs.append(
        {
            "recorded_utc": utc_now(),
            "job_id": job_id,
            "problem_id": str(payload.get("problem_id", "")),
            "problem_name": str(payload.get("problem_name", "")),
            "instance_id": str(payload.get("instance_id", "")),
            "depth": int(payload.get("depth", 0) or 0),
            "provider": str(backend.get("provider", "azure-quantum")),
            "target_id": str(backend.get("target_id", "")),
            "workspace": {
                "subscription_id": str(workspace.get("subscription_id", "")),
                "resource_group": str(workspace.get("resource_group", "")),
                "workspace_name": str(workspace.get("workspace_name", "")),
                "location": str(workspace.get("location", "")),
            },
            "submitted_utc": str(submission.get("submitted_utc", "")),
            "status": "succeeded",
            "manifest_path": manifest_path.as_posix(),
        }
    )

    history["schema_version"] = "1.0"
    history["updated_utc"] = utc_now()
    history["runs"] = runs
    history_path.write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")

    # Mirror sanitized fields for website import to avoid exposing sensitive identifiers.
    website_runs = [
        {
            "recorded_utc": str(entry.get("recorded_utc", "")),
            "problem_id": str(entry.get("problem_id", "")),
            "instance_id": str(entry.get("instance_id", "")),
            "depth": int(entry.get("depth", 0) or 0),
            "target_id": str(entry.get("target_id", "")),
            "status": str(entry.get("status", "")),
        }
        for entry in runs
        if isinstance(entry, dict)
    ]
    website_history = {
        "schema_version": "1.0",
        "updated_utc": history.get("updated_utc", utc_now()),
        "runs": website_runs,
    }

    web_history_path = Path(__file__).resolve().parents[2] / "website" / "data" / "azureRunHistory.json"
    web_history_path.parent.mkdir(parents=True, exist_ok=True)
    web_history_path.write_text(json.dumps(website_history, indent=2) + "\n", encoding="utf-8")


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
    _record_successful_run(payload, manifest_path)
    print("Azure collect complete")
    print(f"  manifest: {manifest_path}")
    print(f"  job_id: {job_id}")
    print(f"  status: {status}")


if __name__ == "__main__":
    main()
