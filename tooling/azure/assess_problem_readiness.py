"""Assess Azure workflow readiness across all registered problems."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_registry() -> List[Dict[str, str]]:
    registry_path = Path(__file__).resolve().parent / "problem_registry.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    rows = payload.get("problems", [])
    return [r for r in rows if isinstance(r, dict) and isinstance(r.get("id"), str)]


def _candidate_evidence_paths(problem_dir: Path) -> List[Path]:
    estimates = problem_dir / "estimates"
    return [
        estimates / "quantum_estimate_ensemble.json",
        estimates / "quantum_estimate.json",
        estimates / "latest.json",
        estimates / "classical_baseline.json",
    ]


def _portable(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> None:
    parser = argparse.ArgumentParser(description="Assess shared Azure workflow readiness for all problems.")
    parser.add_argument(
        "--output",
        default="tooling/azure/readiness_report.json",
        help="Output path for readiness report JSON.",
    )
    args = parser.parse_args()

    root = _repo_root()
    report_rows: List[Dict[str, object]] = []

    for row in _load_registry():
        problem_id = row["id"]
        problem_dir = root / "problems" / problem_id
        qsharp_dir = problem_dir / "qsharp"
        estimates_dir = problem_dir / "estimates"

        evidence_candidates = _candidate_evidence_paths(problem_dir)
        evidence_path = next((p for p in evidence_candidates if p.exists()), None)

        ready_now = problem_dir.exists() and qsharp_dir.exists() and estimates_dir.exists() and evidence_path is not None

        report_rows.append(
            {
                "problem_id": problem_id,
                "problem_name": row.get("name", problem_id),
                "problem_dir": problem_dir.exists(),
                "qsharp_dir": qsharp_dir.exists(),
                "estimates_dir": estimates_dir.exists(),
                "evidence_found": evidence_path is not None,
                "sample_evidence_path": _portable(evidence_path, root) if evidence_path else None,
                "shared_workflow_ready": ready_now,
            }
        )

    ready_count = sum(1 for r in report_rows if r["shared_workflow_ready"])
    payload = {
        "generated_utc": utc_now(),
        "summary": {
            "total_problems": len(report_rows),
            "ready_now": ready_count,
            "not_ready": len(report_rows) - ready_count,
        },
        "problems": report_rows,
    }

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = (root / output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Azure readiness report written")
    print(f"  output: {output_path}")
    print(f"  ready_now: {ready_count}/{len(report_rows)}")


if __name__ == "__main__":
    main()
