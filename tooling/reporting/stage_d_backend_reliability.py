#!/usr/bin/env python3
"""Generate backend reliability/readout proxy artifacts for Stage D packages."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid JSON object in {path}")
    return payload


def wilson(successes: int, total: int, z: float = 1.96) -> Dict[str, float]:
    if total <= 0:
        return {"lower": 0.0, "upper": 0.0}
    p = successes / total
    denom = 1.0 + (z * z) / total
    center = (p + (z * z) / (2.0 * total)) / denom
    radius = (z / denom) * math.sqrt((p * (1.0 - p) / total) + (z * z) / (4.0 * total * total))
    return {"lower": max(0.0, center - radius), "upper": min(1.0, center + radius)}


def safe_mean(values: List[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def build_problem_summary(problem_id: str, runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_target: Dict[str, Dict[str, Any]] = {}

    for row in runs:
        target_id = str(row.get("target_id", "")).strip() or "unknown"
        target = by_target.setdefault(
            target_id,
            {
                "target_id": target_id,
                "run_count": 0,
                "succeeded": 0,
                "metrics_available": 0,
                "runtime_seconds": [],
                "queue_seconds": [],
                "duration_seconds": [],
            },
        )

        target["run_count"] += 1
        if str(row.get("status", "")).lower() == "succeeded":
            target["succeeded"] += 1

        if str(row.get("metrics_status", "")).lower() == "available":
            target["metrics_available"] += 1

        runtime = to_float(row.get("runtime_seconds"))
        queue = to_float(row.get("queue_seconds"))
        duration = to_float(row.get("duration_seconds"))
        if runtime is not None:
            target["runtime_seconds"].append(runtime)
        if queue is not None:
            target["queue_seconds"].append(queue)
        if duration is not None:
            target["duration_seconds"].append(duration)

    targets: List[Dict[str, Any]] = []
    for target in sorted(by_target.values(), key=lambda t: t["target_id"]):
        n = int(target["run_count"])
        succ = int(target["succeeded"])
        avail = int(target["metrics_available"])
        success_rate = succ / n if n else 0.0
        metrics_rate = avail / n if n else 0.0
        targets.append(
            {
                "target_id": target["target_id"],
                "run_count": n,
                "succeeded": succ,
                "success_rate": success_rate,
                "success_rate_ci95": wilson(succ, n),
                "metrics_available": avail,
                "metrics_available_rate": metrics_rate,
                "metrics_available_rate_ci95": wilson(avail, n),
                "avg_runtime_seconds": safe_mean(target["runtime_seconds"]),
                "avg_queue_seconds": safe_mean(target["queue_seconds"]),
                "avg_duration_seconds": safe_mean(target["duration_seconds"]),
            }
        )

    total_runs = len(runs)
    total_successes = sum(1 for r in runs if str(r.get("status", "")).lower() == "succeeded")
    total_metrics_available = sum(1 for r in runs if str(r.get("metrics_status", "")).lower() == "available")

    return {
        "problem_id": problem_id,
        "generated_utc": utc_now(),
        "artifact_type": "backend_readout_characterization_stage_d",
        "evidence_mode": "measured_backend_reliability_proxy",
        "summary": {
            "total_runs": total_runs,
            "successes": total_successes,
            "success_rate": (total_successes / total_runs) if total_runs else 0.0,
            "success_rate_ci95": wilson(total_successes, total_runs),
            "metrics_available": total_metrics_available,
            "metrics_available_rate": (total_metrics_available / total_runs) if total_runs else 0.0,
            "metrics_available_rate_ci95": wilson(total_metrics_available, total_runs),
        },
        "targets": targets,
        "notes": [
            "This artifact is derived from measured Azure run history entries for this problem.",
            "Characterization is execution/readout proxy evidence, not full hardware tomography.",
            "Use this to bound backend reliability assumptions in Stage D claim confidence mapping.",
        ],
    }


def write_markdown(path: Path, payload: Dict[str, Any]) -> None:
    summary = payload["summary"]
    lines: List[str] = []
    lines.append(f"# Backend Readout Characterization - Stage D ({payload['problem_id']})")
    lines.append("")
    lines.append(f"Generated: {payload['generated_utc']}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(
        "- Success rate: "
        f"{summary['success_rate']:.3f} "
        f"(95% CI [{summary['success_rate_ci95']['lower']:.3f}, {summary['success_rate_ci95']['upper']:.3f}])"
    )
    lines.append(
        "- Metrics-availability rate: "
        f"{summary['metrics_available_rate']:.3f} "
        f"(95% CI [{summary['metrics_available_rate_ci95']['lower']:.3f}, {summary['metrics_available_rate_ci95']['upper']:.3f}])"
    )
    lines.append(f"- Total runs: {summary['total_runs']}")
    lines.append("")
    lines.append("## Per-Target Reliability")
    lines.append("")
    lines.append(
        "| Target | Runs | Success Rate | Success CI95 | Metrics Availability | Metrics CI95 | Avg Runtime (s) | Avg Queue (s) | Avg Duration (s) |"
    )
    lines.append("|---|---:|---:|---|---:|---|---:|---:|---:|")
    for row in payload.get("targets", []):
        sr = row["success_rate_ci95"]
        mr = row["metrics_available_rate_ci95"]
        lines.append(
            f"| {row['target_id']} | {row['run_count']} | {row['success_rate']:.3f} | "
            f"[{sr['lower']:.3f}, {sr['upper']:.3f}] | {row['metrics_available_rate']:.3f} | "
            f"[{mr['lower']:.3f}, {mr['upper']:.3f}] | "
            f"{(row['avg_runtime_seconds'] if row['avg_runtime_seconds'] is not None else 0.0):.6f} | "
            f"{(row['avg_queue_seconds'] if row['avg_queue_seconds'] is not None else 0.0):.6f} | "
            f"{(row['avg_duration_seconds'] if row['avg_duration_seconds'] is not None else 0.0):.6f} |"
        )

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    for note in payload.get("notes", []):
        lines.append(f"- {note}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Stage D backend reliability artifacts.")
    parser.add_argument("--problem", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    args = parser.parse_args()

    root = repo_root()
    history = load_json(root / "tooling" / "azure" / "run_history.json")
    runs_raw = history.get("runs", [])
    if not isinstance(runs_raw, list):
        raise SystemExit("run_history.runs must be a list")

    runs = [r for r in runs_raw if isinstance(r, dict) and str(r.get("problem_id", "")).strip() == args.problem]
    if not runs:
        raise SystemExit(f"No run history entries found for problem {args.problem}")

    payload = build_problem_summary(args.problem, runs)

    out_json = (root / args.out_json).resolve()
    out_md = (root / args.out_md).resolve()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(out_md, payload)

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
