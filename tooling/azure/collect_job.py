"""Collect Azure job status and stamp generic problem manifest."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

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


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def _parse_utc(raw: Any) -> Optional[datetime]:
    if not isinstance(raw, str):
        return None
    text = raw.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _delta_seconds(start: Optional[datetime], end: Optional[datetime]) -> Optional[float]:
    if start is None or end is None:
        return None
    return max(0.0, (end - start).total_seconds())


def _extract_cost_usd(payload: Dict[str, Any]) -> Optional[float]:
    candidate_keys = {
        "costusd",
        "cost_usd",
        "estimatedcostusd",
        "estimated_cost_usd",
        "billingcostusd",
        "billing_cost_usd",
        "estimatedtotal",
        "estimatedtotalcost",
        "totalcost",
        "total",
    }

    stack: list[Any] = [payload]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            for key, value in node.items():
                normalized = "".join(ch for ch in key.lower() if ch.isalnum() or ch == "_")
                if normalized in candidate_keys:
                    parsed = _safe_float(value)
                    if parsed is not None and parsed >= 0.0:
                        return parsed
                if isinstance(value, (dict, list)):
                    stack.append(value)
        elif isinstance(node, list):
            stack.extend(node)

    return None


def _extract_job_metrics(job_payload: Dict[str, Any]) -> Dict[str, Optional[float]]:
    created = _parse_utc(job_payload.get("creationTime") or job_payload.get("submittedTime") or job_payload.get("createdAt"))
    began = _parse_utc(
        job_payload.get("beginExecutionTime")
        or job_payload.get("executionBeginTime")
        or job_payload.get("executionStartedTime")
        or job_payload.get("startExecutionTime")
        or job_payload.get("startedAt")
    )
    ended = _parse_utc(
        job_payload.get("endExecutionTime")
        or job_payload.get("executionEndTime")
        or job_payload.get("executionCompletedTime")
        or job_payload.get("finishedTime")
        or job_payload.get("completedTime")
        or job_payload.get("endedAt")
    )

    queue_seconds = _delta_seconds(created, began)
    runtime_seconds = _delta_seconds(began, ended)
    duration_seconds = _delta_seconds(created, ended)

    if runtime_seconds is None:
        runtime_seconds = _safe_float(job_payload.get("executionTime"))
    if queue_seconds is None:
        queue_seconds = _safe_float(job_payload.get("queueTime"))
    if duration_seconds is None:
        duration_seconds = _safe_float(job_payload.get("duration"))

    if duration_seconds is None and runtime_seconds is not None and queue_seconds is not None:
        duration_seconds = runtime_seconds + queue_seconds

    return {
        "runtime_seconds": runtime_seconds if runtime_seconds is None or runtime_seconds >= 0.0 else None,
        "queue_seconds": queue_seconds if queue_seconds is None or queue_seconds >= 0.0 else None,
        "duration_seconds": duration_seconds if duration_seconds is None or duration_seconds >= 0.0 else None,
        "cost_usd": _extract_cost_usd(job_payload),
    }


def _fetch(job_id: str, azure_env: Dict[str, str], timeout: int) -> Dict[str, Any]:
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
    payload["normalized_status"] = _normalize(str(payload.get("status", "")))
    return payload


def _record_successful_run(payload: Dict[str, Any], manifest_path: Path, metrics: Optional[Dict[str, Optional[float]]] = None) -> None:
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

    run_row: Dict[str, Any] = {
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

    if metrics:
        for key in ("runtime_seconds", "queue_seconds", "duration_seconds", "cost_usd"):
            metric = metrics.get(key)
            if metric is not None:
                run_row[key] = round(float(metric), 6)

    runs.append(run_row)

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
            "runtime_seconds": _safe_float(entry.get("runtime_seconds")),
            "queue_seconds": _safe_float(entry.get("queue_seconds")),
            "duration_seconds": _safe_float(entry.get("duration_seconds")),
            "cost_usd": _safe_float(entry.get("cost_usd")),
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

    metrics: Optional[Dict[str, Optional[float]]] = None
    if args.fetch_from_azure:
        try:
            job_payload = _fetch(job_id, azure_env, args.az_timeout)
            status = str(job_payload.get("normalized_status", ""))
            metrics = _extract_job_metrics(job_payload)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError, ValueError) as exc:
            raise SystemExit(f"Azure status fetch failed: {exc}")
    else:
        if not args.result_status:
            raise SystemExit("Provide --result-status or pass --fetch-from-azure")
        status = args.result_status

    submission["status"] = status
    submission["result_status"] = status

    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    _record_successful_run(payload, manifest_path, metrics)
    print("Azure collect complete")
    print(f"  manifest: {manifest_path}")
    print(f"  job_id: {job_id}")
    print(f"  status: {status}")


if __name__ == "__main__":
    main()
