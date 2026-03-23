#!/usr/bin/env python3
"""Compare Stage D readiness snapshots and emit regression trend reports."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def by_problem(payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    rows = payload.get("candidates", [])
    return {str(row.get("problem_id", "")): row for row in rows if row.get("problem_id")}


def summarize(payload: Dict[str, Any]) -> Dict[str, Any]:
    summary = payload.get("summary", {}) if isinstance(payload.get("summary"), dict) else {}
    return {
        "candidate_count": int(summary.get("candidate_count", 0) or 0),
        "fully_ready": int(summary.get("fully_ready", 0) or 0),
        "avg_readiness_percent": float(summary.get("avg_readiness_percent", 0.0) or 0.0),
        "open_checklist_items": int(summary.get("open_checklist_items", 0) or 0),
        "artifact_issue_count": int(summary.get("artifact_issue_count", 0) or 0),
    }


def compare(baseline: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
    b_summary = summarize(baseline)
    c_summary = summarize(current)

    summary_deltas = {
        "fully_ready_delta": c_summary["fully_ready"] - b_summary["fully_ready"],
        "avg_readiness_delta": round(c_summary["avg_readiness_percent"] - b_summary["avg_readiness_percent"], 1),
        "open_checklist_items_delta": c_summary["open_checklist_items"] - b_summary["open_checklist_items"],
        "artifact_issue_count_delta": c_summary["artifact_issue_count"] - b_summary["artifact_issue_count"],
    }

    b_rows = by_problem(baseline)
    c_rows = by_problem(current)

    per_problem: List[Dict[str, Any]] = []
    degraded_problems: List[str] = []

    for problem_id in sorted(set(b_rows) | set(c_rows)):
        b = b_rows.get(problem_id, {})
        c = c_rows.get(problem_id, {})

        b_readiness = (b.get("readiness") or {}) if isinstance(b.get("readiness"), dict) else {}
        c_readiness = (c.get("readiness") or {}) if isinstance(c.get("readiness"), dict) else {}

        b_checklist = (b.get("checklist") or {}) if isinstance(b.get("checklist"), dict) else {}
        c_checklist = (c.get("checklist") or {}) if isinstance(c.get("checklist"), dict) else {}

        readiness_delta = float(c_readiness.get("percent", 0.0) or 0.0) - float(b_readiness.get("percent", 0.0) or 0.0)
        open_delta = int(c_checklist.get("open", 0) or 0) - int(b_checklist.get("open", 0) or 0)
        artifact_delta = int(c.get("artifact_issue_count", 0) or 0) - int(b.get("artifact_issue_count", 0) or 0)

        is_degraded = readiness_delta < 0 or open_delta > 0 or artifact_delta > 0
        if is_degraded:
            degraded_problems.append(problem_id)

        per_problem.append(
            {
                "problem_id": problem_id,
                "baseline_readiness_percent": float(b_readiness.get("percent", 0.0) or 0.0),
                "current_readiness_percent": float(c_readiness.get("percent", 0.0) or 0.0),
                "readiness_delta": round(readiness_delta, 1),
                "baseline_open_checklist": int(b_checklist.get("open", 0) or 0),
                "current_open_checklist": int(c_checklist.get("open", 0) or 0),
                "open_checklist_delta": open_delta,
                "baseline_artifact_issues": int(b.get("artifact_issue_count", 0) or 0),
                "current_artifact_issues": int(c.get("artifact_issue_count", 0) or 0),
                "artifact_issue_delta": artifact_delta,
                "degraded": is_degraded,
            }
        )

    degraded = bool(
        summary_deltas["fully_ready_delta"] < 0
        or summary_deltas["avg_readiness_delta"] < 0
        or summary_deltas["open_checklist_items_delta"] > 0
        or summary_deltas["artifact_issue_count_delta"] > 0
        or degraded_problems
    )

    return {
        "generated_utc": utc_now(),
        "baseline_generated_utc": str(baseline.get("generated_utc", "unknown")),
        "current_generated_utc": str(current.get("generated_utc", "unknown")),
        "summary": {
            "baseline": b_summary,
            "current": c_summary,
            "delta": summary_deltas,
        },
        "degraded": degraded,
        "degraded_problems": degraded_problems,
        "per_problem": per_problem,
    }


def markdown_report(payload: Dict[str, Any]) -> str:
    summary = payload["summary"]
    b = summary["baseline"]
    c = summary["current"]
    d = summary["delta"]

    lines: List[str] = []
    lines.append("# Stage D Readiness Trend")
    lines.append("")
    lines.append(f"Generated: {payload['generated_utc']}")
    lines.append(f"Baseline snapshot: {payload['baseline_generated_utc']}")
    lines.append(f"Current snapshot: {payload['current_generated_utc']}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Degraded: {str(payload['degraded']).lower()}")
    lines.append(f"- Fully ready: {b['fully_ready']} -> {c['fully_ready']} (delta {d['fully_ready_delta']})")
    lines.append(
        f"- Average readiness: {b['avg_readiness_percent']} -> {c['avg_readiness_percent']} "
        f"(delta {d['avg_readiness_delta']})"
    )
    lines.append(
        f"- Open checklist items: {b['open_checklist_items']} -> {c['open_checklist_items']} "
        f"(delta {d['open_checklist_items_delta']})"
    )
    lines.append(
        f"- Artifact issues: {b['artifact_issue_count']} -> {c['artifact_issue_count']} "
        f"(delta {d['artifact_issue_count_delta']})"
    )
    lines.append("")
    lines.append("## Per Problem")
    lines.append("")
    for row in payload["per_problem"]:
        lines.append(
            f"- {row['problem_id']}: readiness {row['baseline_readiness_percent']} -> "
            f"{row['current_readiness_percent']} (delta {row['readiness_delta']}), "
            f"open checklist {row['baseline_open_checklist']} -> {row['current_open_checklist']} "
            f"(delta {row['open_checklist_delta']}), "
            f"artifact issues {row['baseline_artifact_issues']} -> {row['current_artifact_issues']} "
            f"(delta {row['artifact_issue_delta']}), degraded={str(row['degraded']).lower()}"
        )

    if payload["degraded"]:
        lines.append("")
        lines.append("## Action")
        lines.append("")
        lines.append("- Stage D readiness has regressed; investigate the listed candidates and restore full readiness.")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare Stage D readiness snapshots.")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--current", required=True)
    parser.add_argument("--out-json", default="tooling/reporting/stage_d_readiness_trend_report.json")
    parser.add_argument("--out-md", default="docs/planning/stage-d-readiness-trend.md")
    parser.add_argument("--fail-on-degrade", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    baseline = load_json((root / args.baseline).resolve())
    current = load_json((root / args.current).resolve())

    payload = compare(baseline, current)

    out_json = (root / args.out_json).resolve()
    out_md = (root / args.out_md).resolve()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(markdown_report(payload), encoding="utf-8")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(f"degraded={str(payload['degraded']).lower()}")

    if args.fail_on_degrade and payload["degraded"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()