"""Regression checks for problem discovery and Quantum readiness semantics."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tooling.azure.assess_problem_readiness import build_report
from tooling.discover_problems import resolve_problem_dir
from tooling.run_simulator_matrix import discover_kernels

ROOT = Path(__file__).resolve().parents[1]


def _compile_profile(kernel: Path, profile: str) -> dict[str, str]:
    if kernel.parts[-3] == "16_error_correction" and profile == "Base":
        return {
            "status": "incompatible",
            "reason": "mid-circuit branching requires Adaptive_RI",
        }
    return {"status": "passed"}


def test_problem_resolver_finds_active_and_archived_directories():
    assert resolve_problem_dir("01_hubbard", ROOT) == ROOT / "problems" / "01_hubbard"
    assert resolve_problem_dir("03_qae_risk", ROOT) == (
        ROOT / "problems" / "archived" / "03_qae_risk"
    )

    with pytest.raises(FileNotFoundError):
        resolve_problem_dir("missing_problem", ROOT)


def test_simulator_matrix_discovers_every_kernel():
    discovered = {problem_id for problem_id, _, _, _ in discover_kernels()}

    assert "01_hubbard" in discovered
    assert "03_qae_risk" in discovered
    assert len(discovered) == 20


def test_readiness_reports_archived_paths_and_independent_evidence():
    report = build_report(ROOT, compile_profile=_compile_profile)
    rows = {row["problem_id"]: row for row in report["problems"]}
    archived = rows["03_qae_risk"]

    assert archived["archived"] is True
    assert archived["problem_path"] == "problems/archived/03_qae_risk"
    assert all(archived["artifact_checks"].values())
    assert archived["readiness"]["base_qir"]["status"] == "passed"
    assert archived["readiness"]["adaptive_qir"]["status"] == "passed"
    assert archived["readiness"]["local_correctness"]["status"] == "not_run"
    assert archived["readiness"]["provider_emulator"]["status"] == "not_run"
    assert "shared_workflow_ready" not in archived

    assert report["summary"]["artifact_sets_complete"] == 20
    assert report["summary"]["base_qir_compatible"] == 19
    assert report["summary"]["adaptive_qir_compatible"] == 20
    assert report["summary"]["qir_submission_compatible"] == 20
    assert report["summary"]["local_correctness_runs"] == 0


def test_manifest_preparation_resolves_an_archived_problem(tmp_path: Path):
    output = tmp_path / "manifest.json"
    subprocess.run(
        [
            sys.executable,
            "tooling/azure/prepare_problem_manifest.py",
            "--problem",
            "03_qae_risk",
            "--manifest",
            str(output),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    manifest = json.loads(output.read_text(encoding="utf-8"))
    assert manifest["problem_id"] == "03_qae_risk"
    assert manifest["evidence"]["primary_artifact"].startswith(
        "problems/archived/03_qae_risk/"
    )
