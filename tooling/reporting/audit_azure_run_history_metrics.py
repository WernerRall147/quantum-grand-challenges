"""Audit and optionally enrich Azure run-history metric coverage."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid JSON object in {path}")
    return payload


def save_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


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


def _metrics_present(row: Dict[str, Any]) -> bool:
    return any(row.get(key) is not None for key in ("runtime_seconds", "queue_seconds", "duration_seconds", "cost_usd"))


def _run_az(job_id: str, azure_env: Dict[str, str], timeout: int) -> Dict[str, Any]:
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
    result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout)
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise ValueError("Azure CLI returned invalid job payload")
    return payload


def _load_azure_env(env_file: Path) -> Dict[str, str]:
    azure_dir = repo_root() / "tooling" / "azure"
    if str(azure_dir) not in sys.path:
        sys.path.insert(0, str(azure_dir))
    from azure_env import AzureEnvError, load_azure_env  # type: ignore

    try:
        return load_azure_env(env_file)
    except (FileNotFoundError, AzureEnvError) as exc:
        raise RuntimeError(f"Unable to load Azure env: {exc}")


def _build_website_history(runs: list[Dict[str, Any]], updated_utc: str) -> Dict[str, Any]:
    website_runs = []
    for row in runs:
        if not isinstance(row, dict):
            continue
        website_runs.append(
            {
                "recorded_utc": str(row.get("recorded_utc", "")),
                "problem_id": str(row.get("problem_id", "")),
                "instance_id": str(row.get("instance_id", "")),
                "depth": int(row.get("depth", 0) or 0),
                "target_id": str(row.get("target_id", "")),
                "status": str(row.get("status", "")),
                "runtime_seconds": _safe_float(row.get("runtime_seconds")),
                "queue_seconds": _safe_float(row.get("queue_seconds")),
                "duration_seconds": _safe_float(row.get("duration_seconds")),
                "cost_usd": _safe_float(row.get("cost_usd")),
                "metrics_status": str(row.get("metrics_status", "")) or None,
            }
        )

    return {
        "schema_version": "1.0",
        "updated_utc": updated_utc,
        "runs": website_runs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit Azure run-history metric coverage.")
    parser.add_argument("--run-history", default="tooling/azure/run_history.json")
    parser.add_argument("--website-history", default="website/data/azureRunHistory.json")
    parser.add_argument("--output-json", default="tooling/reporting/azure_run_history_metrics_audit.json")
    parser.add_argument("--probe-missing", action="store_true", default=False)
    parser.add_argument("--env-file", default=None)
    parser.add_argument("--az-timeout", type=int, default=120)
    parser.add_argument("--mark-unavailable", action="store_true", default=False)
    parser.add_argument("--unavailable-reason", default="Azure job payload did not include timing/cost fields during audit probe")
    parser.add_argument("--min-resolved-coverage", type=float, default=0.85)
    parser.add_argument("--enforce-threshold", action="store_true", default=False)
    args = parser.parse_args()

    root = repo_root()
    run_history_path = (root / args.run_history).resolve()
    website_history_path = (root / args.website_history).resolve()
    output_json_path = (root / args.output_json).resolve()

    history = load_json(run_history_path)
    raw_runs = history.get("runs", [])
    if not isinstance(raw_runs, list):
        raise SystemExit("run_history.runs must be a list")

    runs: list[Dict[str, Any]] = [row for row in raw_runs if isinstance(row, dict)]

    probed_count = 0
    backfilled_count = 0
    marked_unavailable_count = 0
    probe_errors: list[Dict[str, str]] = []

    azure_env: Optional[Dict[str, str]] = None
    if args.probe_missing:
        if not args.env_file:
            raise SystemExit("--env-file is required with --probe-missing")
        azure_env = _load_azure_env((root / args.env_file).resolve())

    for row in runs:
        if _metrics_present(row):
            row["metrics_status"] = "available"
            row["metrics_checked_utc"] = utc_now()
            row.pop("metrics_unavailable_reason", None)
            continue

        if args.probe_missing and azure_env:
            job_id = str(row.get("job_id", "")).strip()
            if job_id:
                try:
                    payload = _run_az(job_id, azure_env, args.az_timeout)
                    metrics = _extract_job_metrics(payload)
                    probed_count += 1
                    if any(value is not None for value in metrics.values()):
                        for key, value in metrics.items():
                            row[key] = round(float(value), 6) if value is not None else None
                        row["metrics_status"] = "available"
                        row["metrics_checked_utc"] = utc_now()
                        row.pop("metrics_unavailable_reason", None)
                        backfilled_count += 1
                        continue
                except Exception as exc:  # noqa: BLE001
                    probe_errors.append({"job_id": job_id, "error": str(exc)})

        if args.mark_unavailable:
            row["metrics_status"] = "unavailable"
            row["metrics_checked_utc"] = utc_now()
            row["metrics_unavailable_reason"] = args.unavailable_reason
            marked_unavailable_count += 1

    total = len(runs)
    available = sum(1 for row in runs if str(row.get("metrics_status", "")).lower() == "available")
    unavailable = sum(1 for row in runs if str(row.get("metrics_status", "")).lower() == "unavailable")
    unresolved = sum(1 for row in runs if str(row.get("metrics_status", "")).lower() not in {"available", "unavailable"})

    resolved_coverage = (available + unavailable) / total if total > 0 else 1.0
    direct_metric_coverage = sum(1 for row in runs if _metrics_present(row)) / total if total > 0 else 1.0

    history["schema_version"] = "1.0"
    history["updated_utc"] = utc_now()
    history["runs"] = runs
    save_json(run_history_path, history)

    website_history = _build_website_history(runs, history["updated_utc"])
    save_json(website_history_path, website_history)

    audit = {
        "generated_utc": utc_now(),
        "threshold": {
            "min_resolved_coverage": args.min_resolved_coverage,
            "enforce_threshold": bool(args.enforce_threshold),
        },
        "summary": {
            "total_runs": total,
            "available_metrics": available,
            "explicit_unavailable": unavailable,
            "unresolved": unresolved,
            "resolved_coverage": round(resolved_coverage, 6),
            "direct_metric_coverage": round(direct_metric_coverage, 6),
            "probed_missing_rows": probed_count,
            "backfilled_rows": backfilled_count,
            "marked_unavailable_rows": marked_unavailable_count,
        },
        "unresolved_rows": [
            {
                "job_id": str(row.get("job_id", "")),
                "problem_id": str(row.get("problem_id", "")),
                "target_id": str(row.get("target_id", "")),
            }
            for row in runs
            if str(row.get("metrics_status", "")).lower() not in {"available", "unavailable"}
        ],
        "probe_errors": probe_errors,
    }
    save_json(output_json_path, audit)

    print(f"Audit report: {output_json_path}")
    print(f"total_runs={total} available_metrics={available} explicit_unavailable={unavailable} unresolved={unresolved}")
    print(f"resolved_coverage={resolved_coverage:.4f} direct_metric_coverage={direct_metric_coverage:.4f}")

    if args.enforce_threshold and resolved_coverage < args.min_resolved_coverage:
        raise SystemExit(
            f"Resolved coverage {resolved_coverage:.4f} is below threshold {args.min_resolved_coverage:.4f}"
        )


if __name__ == "__main__":
    main()
