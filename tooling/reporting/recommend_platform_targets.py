"""Generate per-problem Azure Quantum platform recommendations.

This report combines execute history and smoke-report compatibility evidence
to recommend a primary target for each problem.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid JSON object in {path}")
    return payload


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_problem_id_from_path(path: Path) -> Optional[str]:
    parts = path.as_posix().split("/")
    for idx, part in enumerate(parts):
        if part == "problems" and idx + 1 < len(parts):
            return parts[idx + 1]
    return None


def parse_cli_flag(command: str, flag: str) -> Optional[str]:
    # Supports --flag value and --flag 'value with spaces'.
    pattern = rf"{re.escape(flag)}\s+(?:'([^']+)'|\"([^\"]+)\"|(\S+))"
    match = re.search(pattern, command)
    if not match:
        return None
    for group in match.groups():
        if group is not None:
            return group
    return None


@dataclass
class TargetEvidence:
    target_id: str
    run_history_successes: int = 0
    smoke_successes: int = 0
    latest_recorded_utc: Optional[str] = None
    input_formats: set[str] = None
    output_formats: set[str] = None

    def __post_init__(self) -> None:
        if self.input_formats is None:
            self.input_formats = set()
        if self.output_formats is None:
            self.output_formats = set()

    @property
    def score(self) -> int:
        # Execute history is weighted higher than smoke compatibility checks.
        return (5 * self.run_history_successes) + (3 * self.smoke_successes)


def update_latest_timestamp(current: Optional[str], candidate: Optional[str]) -> Optional[str]:
    if candidate is None:
        return current
    if current is None:
        return candidate
    return max(current, candidate)


def collect_run_history_evidence(root: Path) -> tuple[Dict[str, Dict[str, TargetEvidence]], Dict[str, int]]:
    by_problem: Dict[str, Dict[str, TargetEvidence]] = defaultdict(dict)
    global_successes: Dict[str, int] = defaultdict(int)

    history = load_json(root / "tooling" / "azure" / "run_history.json")
    runs = history.get("runs", [])
    if not isinstance(runs, list):
        raise ValueError("tooling/azure/run_history.json: runs must be a list")

    for row in runs:
        if not isinstance(row, dict):
            continue
        if str(row.get("status", "")).lower() != "succeeded":
            continue

        problem_id = str(row.get("problem_id", "")).strip()
        target_id = str(row.get("target_id", "")).strip()
        if not problem_id or not target_id:
            continue

        entry = by_problem[problem_id].get(target_id)
        if entry is None:
            entry = TargetEvidence(target_id=target_id)
            by_problem[problem_id][target_id] = entry

        entry.run_history_successes += 1
        entry.latest_recorded_utc = update_latest_timestamp(entry.latest_recorded_utc, row.get("recorded_utc"))
        global_successes[target_id] += 1

    return by_problem, dict(global_successes)


def collect_smoke_evidence(root: Path, by_problem: Dict[str, Dict[str, TargetEvidence]]) -> None:
    smoke_paths = sorted(root.glob("problems/*/estimates/azure_smoke_report*.json"))

    for path in smoke_paths:
        payload = load_json(path)
        if str(payload.get("overall_status", "")).lower() != "passed":
            continue

        backend = payload.get("backend", {}) if isinstance(payload.get("backend"), dict) else {}
        submission = payload.get("submission", {}) if isinstance(payload.get("submission"), dict) else {}

        target_id = str(backend.get("target_id", "")).strip()
        if not target_id:
            continue

        # Require explicit succeeded submission/result status when present.
        status = str(submission.get("status", "")).lower()
        result_status = str(submission.get("result_status", "")).lower()
        if status not in ("", "succeeded"):
            continue
        if result_status not in ("", "succeeded"):
            continue

        problem_id = str(payload.get("problem_id", "")).strip() or parse_problem_id_from_path(path)
        if not problem_id:
            continue

        per_problem = by_problem.setdefault(problem_id, {})
        entry = per_problem.get(target_id)
        if entry is None:
            entry = TargetEvidence(target_id=target_id)
            per_problem[target_id] = entry

        entry.smoke_successes += 1
        entry.latest_recorded_utc = update_latest_timestamp(entry.latest_recorded_utc, submission.get("submitted_utc"))

        command = str(submission.get("dry_run_command", ""))
        in_fmt = parse_cli_flag(command, "--job-input-format")
        out_fmt = parse_cli_flag(command, "--job-output-format")
        if in_fmt:
            entry.input_formats.add(in_fmt)
        if out_fmt:
            entry.output_formats.add(out_fmt)


def pick_recommendation(
    target_map: Dict[str, TargetEvidence],
    global_successes: Dict[str, int],
) -> tuple[str, Optional[TargetEvidence], List[Dict[str, Any]]]:
    rows: List[TargetEvidence] = sorted(
        target_map.values(),
        key=lambda row: (
            row.score,
            global_successes.get(row.target_id, 0),
            row.run_history_successes,
            row.smoke_successes,
            row.target_id,
        ),
        reverse=True,
    )

    candidates: List[Dict[str, Any]] = []
    for row in rows:
        candidates.append(
            {
                "target_id": row.target_id,
                "score": row.score,
                "run_history_successes": row.run_history_successes,
                "smoke_successes": row.smoke_successes,
                "global_target_successes": global_successes.get(row.target_id, 0),
                "latest_recorded_utc": row.latest_recorded_utc,
                "input_formats": sorted(row.input_formats),
                "output_formats": sorted(row.output_formats),
            }
        )

    if not rows:
        return "low", None, candidates

    winner = rows[0]
    if winner.score >= 12:
        confidence = "high"
    elif winner.score >= 6:
        confidence = "medium"
    else:
        confidence = "low"

    return confidence, winner, candidates


def build_report_payload(root: Path) -> Dict[str, Any]:
    by_problem, global_successes = collect_run_history_evidence(root)
    collect_smoke_evidence(root, by_problem)

    all_problem_dirs = sorted(root.glob("problems/[0-9][0-9]_*"))
    all_problem_ids = [path.name for path in all_problem_dirs]

    recommendations: List[Dict[str, Any]] = []
    for problem_id in all_problem_ids:
        target_map = by_problem.get(problem_id, {})
        confidence, winner, candidates = pick_recommendation(target_map, global_successes)

        if winner is None:
            recommended_target = "quantinuum.sim.h2-1sc"
            rationale = "Fallback default because no succeeded evidence rows were found for this problem."
        else:
            recommended_target = winner.target_id
            rationale = (
                f"Highest weighted score ({winner.score}) from run-history successes "
                f"({winner.run_history_successes}) and smoke successes ({winner.smoke_successes})."
            )

        recommendations.append(
            {
                "problem_id": problem_id,
                "recommended_target": recommended_target,
                "confidence": confidence,
                "rationale": rationale,
                "candidates": candidates,
            }
        )

    global_targets = [
        {"target_id": tid, "succeeded_runs": count}
        for tid, count in sorted(global_successes.items(), key=lambda item: (-item[1], item[0]))
    ]

    return {
        "schema_version": "1.0",
        "generated_utc": utc_now_iso(),
        "method": {
            "scoring": "score = 5 * run_history_successes + 3 * smoke_successes",
            "tie_breakers": [
                "higher global target success count",
                "higher run-history success count",
                "higher smoke success count",
                "target id lexical order",
            ],
        },
        "global_target_summary": global_targets,
        "recommendations": recommendations,
    }


def write_markdown(payload: Dict[str, Any], path: Path) -> None:
    lines: List[str] = []
    lines.append("# Platform Target Recommendations")
    lines.append("")
    lines.append(f"Generated: {payload.get('generated_utc', '')}")
    lines.append("")
    lines.append("Scoring: `5 * run_history_successes + 3 * smoke_successes`")
    lines.append("")
    lines.append("## Global Target Summary")
    lines.append("")
    lines.append("| Target | Succeeded Runs |")
    lines.append("|---|---:|")
    for row in payload.get("global_target_summary", []):
        lines.append(f"| {row['target_id']} | {row['succeeded_runs']} |")
    lines.append("")
    lines.append("## Per-Problem Recommendation")
    lines.append("")
    lines.append("| Problem | Recommended Target | Confidence |")
    lines.append("|---|---|---|")
    for row in payload.get("recommendations", []):
        lines.append(f"| {row['problem_id']} | {row['recommended_target']} | {row['confidence']} |")
    lines.append("")

    lines.append("## Top Candidate Details")
    lines.append("")
    for row in payload.get("recommendations", []):
        lines.append(f"### {row['problem_id']}")
        lines.append("")
        lines.append(f"- Recommended target: {row['recommended_target']}")
        lines.append(f"- Confidence: {row['confidence']}")
        lines.append(f"- Rationale: {row['rationale']}")
        candidates = row.get("candidates", [])
        if candidates:
            top = candidates[0]
            lines.append(
                "- Evidence: "
                f"score={top['score']}, run_history={top['run_history_successes']}, "
                f"smoke={top['smoke_successes']}, global={top['global_target_successes']}"
            )
            if top.get("input_formats"):
                lines.append(f"- Input formats: {', '.join(top['input_formats'])}")
            if top.get("output_formats"):
                lines.append(f"- Output formats: {', '.join(top['output_formats'])}")
        else:
            lines.append("- Evidence: none (fallback recommendation)")
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Azure Quantum platform recommendations per problem.")
    parser.add_argument(
        "--out-json",
        default="tooling/reporting/platform_target_recommendations.json",
        help="Output JSON path",
    )
    parser.add_argument(
        "--out-md",
        default="docs/platform-target-recommendations.md",
        help="Output markdown path",
    )
    args = parser.parse_args()

    root = repo_root()
    payload = build_report_payload(root)

    out_json = Path(args.out_json)
    if not out_json.is_absolute():
        out_json = (root / out_json).resolve()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    out_md = Path(args.out_md)
    if not out_md.is_absolute():
        out_md = (root / out_md).resolve()
    write_markdown(payload, out_md)

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
