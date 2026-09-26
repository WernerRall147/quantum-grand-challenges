"""Maturity stages must rest on evidence that exists and describes today's code.

The policy check used to confirm that a README declared a stage and contained two headings.
Five problems kept Stage C labels on calibration ensembles generated before their kernels
were rewritten, three held them on ensembles whose statistics were never parsed, and one
Stage D README stated a different claim category from its machine-readable contract.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tooling"))
sys.path.insert(0, str(REPO_ROOT / "tooling" / "reporting"))

import evidence_hashes  # noqa: E402
import stage_kpis  # noqa: E402

STAGE_KPIS = REPO_ROOT / "tooling" / "reporting" / "stage_kpis.py"
POLICY = REPO_ROOT / "tooling" / "reporting" / "maturity-policy.json"


def _copy_problem(tmp_path: Path, relative: str) -> Path:
    destination = tmp_path / relative
    shutil.copytree(REPO_ROOT / relative, destination)
    return destination


def test_policy_passes_on_the_committed_repository() -> None:
    result = subprocess.run(
        [sys.executable, str(STAGE_KPIS), "--policy", str(POLICY), "--enforce"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout[-2000:] + result.stderr[-2000:]


def test_editing_a_calibrated_kernel_makes_its_evidence_stale(tmp_path: Path) -> None:
    problem = _copy_problem(tmp_path, "problems/16_error_correction")
    assert stage_kpis.calibration_status(problem, tmp_path) == "current"

    main = problem / "qsharp" / "src" / "Main.qs"
    main.write_text(main.read_text(encoding="utf-8") + "\n// changed after calibration\n", encoding="utf-8")

    assert stage_kpis.calibration_status(problem, tmp_path) == "stale"


def test_a_readme_contradicting_its_claim_contract_is_caught(tmp_path: Path) -> None:
    problem = _copy_problem(tmp_path, "problems/archived/05_qaoa_maxcut")
    readme = (problem / "README.md").read_text(encoding="utf-8")
    assert stage_kpis.claim_category_status(problem, readme) == "consistent"

    edited = readme.replace("**Claim category (current)**: `theoretical`", "**Claim category (current)**: `projected`")
    assert edited != readme
    assert stage_kpis.claim_category_status(problem, edited).startswith("mismatch")


def test_evidence_hashes_do_not_depend_on_line_endings(tmp_path: Path) -> None:
    lf, crlf = tmp_path / "lf.qs", tmp_path / "crlf.qs"
    lf.write_bytes(b"operation A() : Unit {}\nfunction B() : Int { 1 }\n")
    crlf.write_bytes(b"operation A() : Unit {}\r\nfunction B() : Int { 1 }\r\n")
    assert evidence_hashes.file_digest(lf) == evidence_hashes.file_digest(crlf)
