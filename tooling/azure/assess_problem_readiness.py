"""Assess Azure workflow readiness across all registered problems."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(ROOT))

from tooling.discover_problems import resolve_problem_dir  # noqa: E402

ENTRY_RE = re.compile(r"@EntryPoint\(\)\s*\n\s*operation\s+(\w+)")
QIR_PROFILES = ("Base", "Adaptive_RI")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _repo_root() -> Path:
    return ROOT


def _load_registry(root: Path) -> List[Dict[str, str]]:
    registry_path = root / "tooling" / "azure" / "problem_registry.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    rows = payload.get("problems", [])
    return [r for r in rows if isinstance(r, dict) and isinstance(r.get("id"), str)]


def _candidate_evidence_paths(problem_dir: Path) -> List[Path]:
    estimates = problem_dir / "estimates"
    return [
        # The single source of truth for a resource estimate. problems/<id>/estimates/
        # is retired as an estimate store for active problems: it held a fabricated
        # constant next to these real numbers for six months.
        problem_dir / "circuits" / "estimate.json",
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


def _compile_kernel_profile(kernel: Path, profile_name: str) -> Dict[str, str]:
    from qdk import qsharp

    source = kernel.read_text(encoding="utf-8")
    match = ENTRY_RE.search(source)
    if not match:
        return {"status": "failed", "reason": "no @EntryPoint operation"}

    try:
        qsharp.init(target_profile=getattr(qsharp.TargetProfile, profile_name))
        qsharp.eval(source)
        qsharp.compile(f"{match.group(1)}()")
    except BaseException as exc:  # QDK can report compiler failures as Rust panics.
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        return {
            "status": "incompatible",
            "reason": str(exc).splitlines()[0][:300],
        }
    return {"status": "passed"}


def _assess_problem(
    root: Path,
    row: Dict[str, str],
    *,
    compile_profile: Callable[[Path, str], Dict[str, str]] | None,
) -> Dict[str, Any]:
    problem_id = row["id"]
    resolution_error = None
    try:
        problem_dir = resolve_problem_dir(problem_id, root)
    except FileNotFoundError as exc:
        problem_dir = root / "problems" / problem_id
        resolution_error = str(exc)
    qsharp_dir = problem_dir / "qsharp"
    estimates_dir = problem_dir / "estimates"
    kernel = qsharp_dir / "HardwareKernel.qs"

    evidence_candidates = _candidate_evidence_paths(problem_dir)
    evidence_path = next((p for p in evidence_candidates if p.exists()), None)
    instances_dir = problem_dir / "instances"
    artifact_checks = {
        "problem_dir": problem_dir.is_dir(),
        "qsharp_project": (qsharp_dir / "qsharp.json").is_file(),
        "hardware_kernel": kernel.is_file(),
        "instances": instances_dir.is_dir(),
        "estimates_dir": estimates_dir.is_dir(),
        "evidence": evidence_path is not None,
    }
    artifacts_status = "passed" if all(artifact_checks.values()) else "failed"

    if resolution_error:
        profile_results = {
            profile: {
                "status": "not_run" if compile_profile is None else "failed",
                "reason": resolution_error,
            }
            for profile in QIR_PROFILES
        }
    elif compile_profile is None:
        profile_results = {
            profile: {"status": "not_run"} for profile in QIR_PROFILES
        }
    elif not kernel.is_file():
        profile_results = {
            profile: {"status": "failed", "reason": "HardwareKernel.qs is missing"}
            for profile in QIR_PROFILES
        }
    else:
        profile_results = {
            profile: compile_profile(kernel, profile) for profile in QIR_PROFILES
        }

    qir_ready = profile_results["Base"]["status"] == "passed" or (
        profile_results["Adaptive_RI"]["status"] == "passed"
    )
    return {
        "problem_id": problem_id,
        "problem_name": row.get("name", problem_id),
        "problem_path": _portable(problem_dir, root),
        "resolution_error": resolution_error,
        "archived": problem_dir.parent.name == "archived",
        "artifact_checks": artifact_checks,
        "sample_evidence_path": (
            _portable(evidence_path, root) if evidence_path else None
        ),
        "readiness": {
            "artifacts": {"status": artifacts_status},
            "base_qir": profile_results["Base"],
            "adaptive_qir": profile_results["Adaptive_RI"],
            "local_correctness": {"status": "not_run"},
            "provider_syntax": {"status": "not_run"},
            "provider_emulator": {"status": "not_run"},
            "hardware": {"status": "not_run"},
        },
        "qir_submission_compatible": artifacts_status == "passed" and qir_ready,
    }


def build_report(
    root: Path,
    *,
    compile_qir: bool = True,
    compile_profile: Callable[[Path, str], Dict[str, str]] = _compile_kernel_profile,
) -> Dict[str, Any]:
    compiler = compile_profile if compile_qir else None
    report_rows = [
        _assess_problem(root, row, compile_profile=compiler)
        for row in _load_registry(root)
    ]

    def readiness_count(category: str, status: str) -> int:
        return sum(
            row["readiness"][category]["status"] == status for row in report_rows
        )

    return {
        "generated_utc": utc_now(),
        "summary": {
            "total_problems": len(report_rows),
            "artifact_sets_complete": readiness_count("artifacts", "passed"),
            "base_qir_compatible": readiness_count("base_qir", "passed"),
            "adaptive_qir_compatible": readiness_count("adaptive_qir", "passed"),
            "qir_submission_compatible": sum(
                row["qir_submission_compatible"] for row in report_rows
            ),
            "local_correctness_runs": readiness_count("local_correctness", "passed"),
            "provider_syntax_runs": readiness_count("provider_syntax", "passed"),
            "provider_emulator_runs": readiness_count("provider_emulator", "passed"),
            "hardware_runs": readiness_count("hardware", "passed"),
        },
        "problems": report_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Assess shared Azure workflow readiness for all problems.")
    parser.add_argument(
        "--output",
        default="tooling/azure/readiness_report.json",
        help="Output path for readiness report JSON.",
    )
    parser.add_argument(
        "--skip-qir",
        action="store_true",
        help="Check artifact paths only and mark QIR compilation as not_run.",
    )
    args = parser.parse_args()

    root = _repo_root()
    payload = build_report(root, compile_qir=not args.skip_qir)

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = (root / output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Azure readiness report written")
    print(f"  output: {output_path}")
    summary = payload["summary"]
    print(f"  artifacts complete: {summary['artifact_sets_complete']}/{summary['total_problems']}")
    print(f"  Base QIR compatible: {summary['base_qir_compatible']}/{summary['total_problems']}")
    print(f"  Adaptive QIR compatible: {summary['adaptive_qir_compatible']}/{summary['total_problems']}")
    print(
        "  QIR submission compatible: "
        f"{summary['qir_submission_compatible']}/{summary['total_problems']}"
    )


if __name__ == "__main__":
    main()
