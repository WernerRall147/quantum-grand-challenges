#!/usr/bin/env python3
"""Compute objective-maturity KPI coverage across problem READMEs.

Usage:
  python tooling/reporting/stage_kpis.py
  python tooling/reporting/stage_kpis.py --json
    python tooling/reporting/stage_kpis.py --out-md docs/objective-kpis.md --out-json docs/objective-kpis.json
    python tooling/reporting/stage_kpis.py --policy tooling/reporting/maturity-policy.json --enforce
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


STAGE_PATTERN = re.compile(r"\bStage\s+([ABCD])\b", re.IGNORECASE)
CURRENT_GATE_PATTERN = re.compile(
    r"Current\s+gate[^\n]*?\bStage\s+([ABCD])\b",
    re.IGNORECASE,
)
STAGE_ORDER = {"A": 1, "B": 2, "C": 3, "D": 4}


@dataclass
class ProblemKpi:
    problem: str
    readme: str
    stage: Optional[str]
    has_advantage_contract: bool


@dataclass
class Summary:
    total_problems: int
    stage_counts: Dict[str, int]
    stage_pct: Dict[str, float]
    with_advantage_contract: int
    with_advantage_contract_pct: float
    advisory_targets_total: int
    advisory_targets_met: int
    advisory_targets_met_pct: float


def detect_stage(text: str) -> Optional[str]:
    """Detect the highest-confidence stage marker in README text."""
    gate_match = CURRENT_GATE_PATTERN.search(text)
    if gate_match:
        stage = gate_match.group(1).upper()
        if stage in STAGE_ORDER:
            return stage

    matches = STAGE_PATTERN.findall(text)
    if not matches:
        return None

    # Prefer first explicit stage mention in objective gate/status sections.
    for stage in matches:
        upper = stage.upper()
        if upper in {"A", "B", "C", "D"}:
            return upper
    return None


def has_advantage_contract(text: str) -> bool:
    return "## Advantage Claim Contract" in text


def summarize(records: List[ProblemKpi]) -> Summary:
    total = len(records)
    counts = {"A": 0, "B": 0, "C": 0, "D": 0, "Unknown": 0}
    contracts = 0

    for rec in records:
        key = rec.stage if rec.stage in {"A", "B", "C", "D"} else "Unknown"
        counts[key] += 1
        if rec.has_advantage_contract:
            contracts += 1

    pct = {k: round((v / total) * 100.0, 1) if total else 0.0 for k, v in counts.items()}
    contracts_pct = round((contracts / total) * 100.0, 1) if total else 0.0

    return Summary(
        total_problems=total,
        stage_counts=counts,
        stage_pct=pct,
        with_advantage_contract=contracts,
        with_advantage_contract_pct=contracts_pct,
        advisory_targets_total=0,
        advisory_targets_met=0,
        advisory_targets_met_pct=0.0,
    )


def collect_problem_kpis(repo_root: Path) -> List[ProblemKpi]:
    problems_dir = repo_root / "problems"
    records: List[ProblemKpi] = []

    for child in sorted(problems_dir.iterdir()):
        if not child.is_dir():
            continue
        if not re.match(r"^\d{2}_", child.name):
            continue

        readme = child / "README.md"
        if not readme.exists():
            records.append(
                ProblemKpi(
                    problem=child.name,
                    readme=str(readme.relative_to(repo_root)),
                    stage=None,
                    has_advantage_contract=False,
                )
            )
            continue

        text = readme.read_text(encoding="utf-8", errors="replace")
        records.append(
            ProblemKpi(
                problem=child.name,
                readme=str(readme.relative_to(repo_root)),
                stage=detect_stage(text),
                has_advantage_contract=has_advantage_contract(text),
            )
        )

    return records


def print_human(summary: Summary, records: List[ProblemKpi]) -> None:
    print("Objective Maturity KPI Report")
    print("=")
    print(f"Total problems: {summary.total_problems}")
    print()
    print("Stage coverage:")
    for stage in ["A", "B", "C", "D", "Unknown"]:
        print(f"  Stage {stage}: {summary.stage_counts[stage]} ({summary.stage_pct[stage]}%)")

    print()
    print(
        "Advantage Claim Contract coverage: "
        f"{summary.with_advantage_contract}/{summary.total_problems} "
        f"({summary.with_advantage_contract_pct}%)"
    )
    print()
    print("Per-problem status:")
    for rec in records:
        stage_label = rec.stage if rec.stage else "Unknown"
        contract_label = "yes" if rec.has_advantage_contract else "no"
        print(f"  - {rec.problem}: stage={stage_label}, contract={contract_label}")


def build_markdown(summary: Summary, records: List[ProblemKpi], advisory_gaps: Optional[List[str]] = None) -> str:
    lines: List[str] = []
    lines.append("# Objective Maturity KPI Report")
    lines.append("")
    lines.append(f"Total problems: **{summary.total_problems}**")
    lines.append("")
    lines.append("## Stage Coverage")
    lines.append("")
    lines.append("| Stage | Count | Percent |")
    lines.append("|---|---:|---:|")
    for stage in ["A", "B", "C", "D", "Unknown"]:
        lines.append(f"| {stage} | {summary.stage_counts[stage]} | {summary.stage_pct[stage]}% |")

    lines.append("")
    lines.append("## Contract Coverage")
    lines.append("")
    lines.append(
        f"Advantage Claim Contract coverage: **{summary.with_advantage_contract}/{summary.total_problems} "
        f"({summary.with_advantage_contract_pct}%)**"
    )

    if summary.advisory_targets_total:
        lines.append("")
        lines.append("## Advisory Target Progress")
        lines.append("")
        lines.append(
            f"Advisory targets met: **{summary.advisory_targets_met}/{summary.advisory_targets_total} "
            f"({summary.advisory_targets_met_pct}%)**"
        )
        if advisory_gaps:
            lines.append("")
            lines.append("Outstanding advisory gaps:")
            for gap in advisory_gaps:
                lines.append(f"- {gap}")

    lines.append("")
    lines.append("## Per-Problem Status")
    lines.append("")
    lines.append("| Problem | Stage | Advantage Contract | README |")
    lines.append("|---|---|---|---|")
    for rec in records:
        stage_label = rec.stage if rec.stage else "Unknown"
        contract_label = "yes" if rec.has_advantage_contract else "no"
        lines.append(f"| {rec.problem} | {stage_label} | {contract_label} | `{rec.readme}` |")

    lines.append("")
    return "\n".join(lines)


def _policy_required_problems(payload: Dict[str, object]) -> List[str]:
    value = payload.get("required_problems", [])
    if not isinstance(value, list):
        return []
    return [str(v) for v in value]


def _policy_require_stage(payload: Dict[str, object]) -> bool:
    return bool(payload.get("require_stage", True))


def _policy_require_advantage_contract(payload: Dict[str, object]) -> bool:
    return bool(payload.get("require_advantage_contract", True))


def _normalize_stage(value: object) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip().upper()
    if text in STAGE_ORDER:
        return text
    return None


def _policy_minimum_stage(payload: Dict[str, object]) -> Optional[str]:
    return _normalize_stage(payload.get("minimum_stage"))


def _policy_per_problem_minimum_stage(payload: Dict[str, object]) -> Dict[str, str]:
    raw = payload.get("per_problem_minimum_stage", {})
    if not isinstance(raw, dict):
        return {}
    out: Dict[str, str] = {}
    for k, v in raw.items():
        norm = _normalize_stage(v)
        if norm:
            out[str(k)] = norm
    return out


def _stage_meets_threshold(actual: Optional[str], minimum: str) -> bool:
    if actual not in STAGE_ORDER:
        return False
    return STAGE_ORDER[actual] >= STAGE_ORDER[minimum]


def _policy_advisory_target_stage(payload: Dict[str, object]) -> Dict[str, str]:
    raw = payload.get("advisory_target_stage", {})
    if not isinstance(raw, dict):
        return {}
    out: Dict[str, str] = {}
    for k, v in raw.items():
        norm = _normalize_stage(v)
        if norm:
            out[str(k)] = norm
    return out


def evaluate_policy(
    records: List[ProblemKpi],
    policy_path: Path,
) -> Tuple[List[str], Dict[str, object], List[str], Dict[str, int]]:
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    required = set(_policy_required_problems(policy))
    req_stage = _policy_require_stage(policy)
    req_contract = _policy_require_advantage_contract(policy)
    min_stage = _policy_minimum_stage(policy)
    per_problem_min_stage = _policy_per_problem_minimum_stage(policy)
    advisory_target_stage = _policy_advisory_target_stage(policy)

    by_problem = {rec.problem: rec for rec in records}
    violations: List[str] = []

    for problem in sorted(required):
        rec = by_problem.get(problem)
        if rec is None:
            violations.append(f"Missing required problem directory: {problem}")
            continue
        if req_stage and rec.stage not in {"A", "B", "C", "D"}:
            violations.append(f"{problem}: missing explicit stage marker (Stage A/B/C/D)")
        threshold = per_problem_min_stage.get(problem, min_stage)
        if threshold and not _stage_meets_threshold(rec.stage, threshold):
            actual = rec.stage if rec.stage else "Unknown"
            violations.append(
                f"{problem}: stage {actual} is below required minimum stage {threshold}"
            )
        if req_contract and not rec.has_advantage_contract:
            violations.append(f"{problem}: missing '## Advantage Claim Contract' section")

    advisory_gaps: List[str] = []
    advisory_total = 0
    advisory_met = 0
    for problem, target in sorted(advisory_target_stage.items()):
        rec = by_problem.get(problem)
        if rec is None:
            advisory_gaps.append(f"{problem}: missing problem directory/readme for advisory target {target}")
            advisory_total += 1
            continue
        advisory_total += 1
        if _stage_meets_threshold(rec.stage, target):
            advisory_met += 1
        else:
            actual = rec.stage if rec.stage else "Unknown"
            advisory_gaps.append(f"{problem}: advisory target {target} not met (current {actual})")

    meta = {
        "required_problems": sorted(required),
        "require_stage": req_stage,
        "require_advantage_contract": req_contract,
        "minimum_stage": min_stage,
        "per_problem_minimum_stage": per_problem_min_stage,
        "advisory_target_stage": advisory_target_stage,
    }
    advisory_stats = {
        "total": advisory_total,
        "met": advisory_met,
        "unmet": max(0, advisory_total - advisory_met),
    }
    return violations, meta, advisory_gaps, advisory_stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute maturity-gate KPIs.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Repository root path (default: inferred from script location).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output.",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        help="Write machine-readable JSON report to this path.",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        help="Write markdown report to this path.",
    )
    parser.add_argument(
        "--policy",
        type=Path,
        help="Path to policy JSON file for compliance checks.",
    )
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Exit with non-zero status when policy violations are found.",
    )
    args = parser.parse_args()

    records = collect_problem_kpis(args.repo_root)
    summary = summarize(records)

    payload = {
        "summary": asdict(summary),
        "records": [asdict(r) for r in records],
    }

    violations: List[str] = []
    advisory_gaps: List[str] = []
    advisory_stats = {"total": 0, "met": 0, "unmet": 0}
    if args.policy:
        violations, policy_meta, advisory_gaps, advisory_stats = evaluate_policy(records, args.policy)
        payload["policy"] = policy_meta
        payload["violations"] = violations
        payload["advisory_gaps"] = advisory_gaps
        payload["advisory"] = advisory_stats
        summary.advisory_targets_total = advisory_stats["total"]
        summary.advisory_targets_met = advisory_stats["met"]
        summary.advisory_targets_met_pct = round(
            (advisory_stats["met"] / advisory_stats["total"]) * 100.0, 1
        ) if advisory_stats["total"] else 0.0
        payload["summary"] = asdict(summary)

    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(build_markdown(summary, records, advisory_gaps), encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_human(summary, records)

    if violations:
        print()
        print("Policy violations:")
        for violation in violations:
            print(f"  - {violation}")

    if advisory_gaps:
        print()
        print("Advisory target gaps:")
        for gap in advisory_gaps:
            print(f"  - {gap}")

    if args.enforce and violations:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
