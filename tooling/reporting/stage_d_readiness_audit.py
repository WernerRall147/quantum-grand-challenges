#!/usr/bin/env python3
"""Audit Stage D readiness for promoted candidate problems."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


CHECKBOX_PATTERN = re.compile(r"^- \[(?P<state>[ xX])\]", re.MULTILINE)
CLAIM_PATTERN = re.compile(r"Current claim category:\s*`([^`]+)`", re.IGNORECASE)
ARTIFACT_BULLET_PATTERN = re.compile(r"^-\s+`(?P<path>[^`]+)`", re.MULTILINE)


@dataclass
class CandidateSpec:
    problem_id: str
    expected_claim: str
    required_artifacts: List[str]


CANDIDATES = [
    CandidateSpec(
        problem_id="03_qae_risk",
        expected_claim="projected",
        required_artifacts=[
            "estimates/quantum_estimate_ensemble_small.json",
            "estimates/quantum_estimate_ensemble_medium.json",
            "estimates/quantum_estimate_ensemble_large.json",
            "estimates/fairness_review_stage_d.md",
        ],
    ),
    CandidateSpec(
        problem_id="05_qaoa_maxcut",
        expected_claim="theoretical",
        required_artifacts=[
            "estimates/backend_calibration_stage_d.json",
            "estimates/fairness_benchmark_stage_d.json",
            "estimates/fairness_benchmark_stage_d.md",
        ],
    ),
    CandidateSpec(
        problem_id="15_database_search",
        expected_claim="projected",
        required_artifacts=[
            "estimates/backend_uncertainty_small.json",
            "estimates/backend_uncertainty_medium.json",
            "estimates/backend_uncertainty_large.json",
            "estimates/oracle_overhead_accounting_stage_d.md",
            "estimates/marked_fraction_sensitivity_stage_d.md",
        ],
    ),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_json(path: Path) -> Dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return payload if isinstance(payload, dict) else None


def checklist_stats(stage_d_text: str) -> Dict[str, int]:
    states = [m.group("state").lower() for m in CHECKBOX_PATTERN.finditer(stage_d_text)]
    total = len(states)
    done = sum(1 for s in states if s == "x")
    open_items = total - done
    return {"total": total, "done": done, "open": open_items}


def claim_category(stage_d_text: str) -> str:
    match = CLAIM_PATTERN.search(stage_d_text)
    if not match:
        return "unknown"
    return match.group(1).strip().lower()


def listed_artifacts(stage_d_text: str) -> List[str]:
    return [m.group("path").strip() for m in ARTIFACT_BULLET_PATTERN.finditer(stage_d_text)]


def validate_artifact_quality(problem_dir: Path, rel_path: str) -> List[str]:
    issues: List[str] = []
    full_path = problem_dir / rel_path
    if not full_path.exists():
        issues.append("missing")
        return issues

    if full_path.suffix.lower() == ".json":
        payload = parse_json(full_path)
        if payload is None:
            issues.append("invalid_json")
            return issues

        # Lightweight problem-specific quality checks.
        if "quantum_estimate_ensemble_" in rel_path:
            metrics = payload.get("metrics", {}) if isinstance(payload.get("metrics"), dict) else {}
            runs = metrics.get("ensemble_runs")
            std_err = metrics.get("ensemble_std_error")
            if not isinstance(runs, int) or runs < 20:
                issues.append("ensemble_runs_below_20")
            if not isinstance(std_err, (int, float)):
                issues.append("missing_ensemble_std_error")

        if rel_path.endswith("backend_calibration_stage_d.json"):
            backend = payload.get("backend", {}) if isinstance(payload.get("backend"), dict) else {}
            if not str(backend.get("target_id", "")).strip():
                issues.append("missing_backend_target")

        if "backend_uncertainty_" in rel_path:
            observed = payload.get("observed", {}) if isinstance(payload.get("observed"), dict) else {}
            ci = payload.get("confidence_interval", {}) if isinstance(payload.get("confidence_interval"), dict) else {}
            if not isinstance(observed.get("shots"), int) or observed.get("shots") <= 0:
                issues.append("invalid_observed_shots")
            if not isinstance(ci.get("lower"), (int, float)) or not isinstance(ci.get("upper"), (int, float)):
                issues.append("missing_confidence_interval_bounds")

    return issues


def build_report(root: Path) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []

    for spec in CANDIDATES:
        problem_dir = root / "problems" / spec.problem_id
        readme_path = problem_dir / "README.md"
        stage_d_path = problem_dir / "STAGE_D_ADVANTAGE_EVIDENCE.md"

        readme_exists = readme_path.exists()
        stage_d_exists = stage_d_path.exists()
        stage_d_text = read_text(stage_d_path) if stage_d_exists else ""

        claim = claim_category(stage_d_text) if stage_d_exists else "unknown"
        checklist = checklist_stats(stage_d_text) if stage_d_exists else {"total": 0, "done": 0, "open": 0}
        artifact_listed = set(listed_artifacts(stage_d_text)) if stage_d_exists else set()

        artifacts: List[Dict[str, Any]] = []
        total_artifact_issues = 0
        for rel in spec.required_artifacts:
            checks = validate_artifact_quality(problem_dir, rel)
            artifact_record = {
                "path": rel,
                "exists": (problem_dir / rel).exists(),
                "listed_in_stage_d_file": rel in artifact_listed,
                "quality_issues": checks,
            }
            artifacts.append(artifact_record)
            total_artifact_issues += len(checks)

        score = 0
        if readme_exists:
            score += 1
        if stage_d_exists:
            score += 1
        if claim == spec.expected_claim:
            score += 1
        if checklist["open"] == 0 and checklist["total"] > 0:
            score += 1
        if all(a["exists"] for a in artifacts):
            score += 1
        if all(not a["quality_issues"] for a in artifacts):
            score += 1

        max_score = 6
        readiness_pct = round((score / max_score) * 100.0, 1)

        results.append(
            {
                "problem_id": spec.problem_id,
                "expected_claim": spec.expected_claim,
                "current_claim": claim,
                "readme_exists": readme_exists,
                "stage_d_file_exists": stage_d_exists,
                "checklist": checklist,
                "artifacts": artifacts,
                "artifact_issue_count": total_artifact_issues,
                "readiness": {
                    "score": score,
                    "max_score": max_score,
                    "percent": readiness_pct,
                },
            }
        )

    summary = {
        "candidate_count": len(results),
        "fully_ready": sum(1 for r in results if r["readiness"]["score"] == r["readiness"]["max_score"]),
        "avg_readiness_percent": round(sum(r["readiness"]["percent"] for r in results) / max(1, len(results)), 1),
        "open_checklist_items": sum(r["checklist"]["open"] for r in results),
        "artifact_issue_count": sum(r["artifact_issue_count"] for r in results),
    }

    return {
        "generated_utc": utc_now(),
        "summary": summary,
        "candidates": results,
    }


def markdown_report(payload: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Stage D Readiness Audit")
    lines.append("")
    lines.append(f"Generated: {payload['generated_utc']}")
    lines.append("")
    summary = payload["summary"]
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Candidate problems: {summary['candidate_count']}")
    lines.append(f"- Fully ready: {summary['fully_ready']}")
    lines.append(f"- Average readiness: {summary['avg_readiness_percent']}%")
    lines.append(f"- Open checklist items: {summary['open_checklist_items']}")
    lines.append(f"- Artifact quality issues: {summary['artifact_issue_count']}")
    lines.append("")

    for row in payload["candidates"]:
        lines.append(f"## {row['problem_id']}")
        lines.append("")
        lines.append(f"- Claim category: expected `{row['expected_claim']}`, current `{row['current_claim']}`")
        lines.append(
            f"- Readiness score: {row['readiness']['score']}/{row['readiness']['max_score']} "
            f"({row['readiness']['percent']}%)"
        )
        lines.append(
            f"- Checklist: total={row['checklist']['total']}, done={row['checklist']['done']}, open={row['checklist']['open']}"
        )
        lines.append("- Artifact checks:")
        for art in row["artifacts"]:
            issues = ", ".join(art["quality_issues"]) if art["quality_issues"] else "none"
            lines.append(
                f"  - {art['path']}: exists={str(art['exists']).lower()}, "
                f"listed={str(art['listed_in_stage_d_file']).lower()}, issues={issues}"
            )
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit Stage D readiness for key candidate problems.")
    parser.add_argument("--out-json", default="tooling/reporting/stage_d_readiness_report.json")
    parser.add_argument("--out-md", default="docs/planning/stage-d-readiness-2026-03-10.md")
    args = parser.parse_args()

    root = repo_root()
    payload = build_report(root)

    out_json = (root / args.out_json).resolve()
    out_md = (root / args.out_md).resolve()

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(markdown_report(payload) + "\n", encoding="utf-8")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
