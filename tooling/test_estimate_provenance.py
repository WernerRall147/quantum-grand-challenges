"""An estimate that names an operation the code no longer defines is describing a ghost.

Five problems were upgraded from VQE to QPE in August 2026. The stored emulator
histograms from April still describe the kernels that were replaced, and nothing noticed
until a human read two files side by side. `circuits/estimate.json` records the exact
expressions it was produced from - `entryExpr` and `hardwareKernelEntryPoint` - so the
drift is detectable without regenerating anything.

This checks the half of provenance that already exists. Stamping a source commit at
generation time is the other half, and it is not needed to catch this defect class.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# `Main.EstimateHubbardEnergy(0.5, 2.0, 1)` and `HubbardQPEKernel()` both reduce to the
# operation name: drop any module qualifier and the argument list.
_CALLABLE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def _operation_name(expression: str) -> str | None:
    match = _CALLABLE.search(expression or "")
    return match.group(1) if match else None


def _estimates() -> list[tuple[str, Path]]:
    found = []
    for path in sorted((REPO_ROOT / "problems").rglob("circuits/estimate.json")):
        found.append((path.relative_to(REPO_ROOT).parts[-3], path))
    return found


def _defined_operations(problem_dir: Path) -> set[str]:
    """Every operation defined anywhere in the problem's Q#.

    Deliberately not tied to a filename. Q# lives in qsharp/src/Main.qs for the estimated
    program and qsharp/HardwareKernel.qs for the submitted one, and asserting that layout
    would fail on a reorganisation that broke nothing.
    """
    names: set[str] = set()
    for source in (problem_dir / "qsharp").rglob("*.qs"):
        names.update(
            re.findall(r"^\s*operation\s+([A-Za-z_][A-Za-z0-9_]*)", source.read_text(encoding="utf-8"), re.M)
        )
    return names


ESTIMATES = _estimates()


def test_every_problem_has_an_estimate_to_check():
    """Guard the guard: a glob that silently matches nothing would pass forever."""
    assert len(ESTIMATES) >= 20, f"expected at least 20 estimate.json files, found {len(ESTIMATES)}"


@pytest.mark.parametrize("problem,path", ESTIMATES, ids=[p for p, _ in ESTIMATES])
def test_estimate_names_operations_that_still_exist(problem, path):
    data = json.loads(path.read_text(encoding="utf-8"))
    defined = _defined_operations(path.parent.parent)
    assert defined, f"{problem}: no Q# operations found, cannot verify the estimate"

    missing = []
    for field in ("entryExpr", "hardwareKernelEntryPoint"):
        expression = data.get(field)
        if not expression:
            continue
        name = _operation_name(expression)
        if name and name not in defined:
            missing.append(f"{field}={expression!r} -> operation {name!r} is not defined")

    assert not missing, (
        f"{problem}: estimate.json describes code that no longer exists: "
        + "; ".join(missing)
        + ". Regenerate the estimate, or correct the field."
    )


# ---------------------------------------------------------------------------
# The other way an estimate lies: the numbers were never measured.
#
# tooling/estimator/run_estimation.py shelled out to a `qsharp-re` executable that no
# installed package provides. The FileNotFoundError was caught and answered with
# _generate_mock_output(), so every "live" run returned a fabricated constant - which is
# how nine unrelated problems came to report an identical 16 logical / 35,200 physical.
#
# That survived because there were two estimate stores. circuits/estimate.json held
# measurements; problems/<id>/estimates/ held the constant, and fed
# tooling/azure/assess_problem_readiness.py and prepare_problem_manifest.py, so the
# fabrication reached readiness claims while the real numbers sat one directory away.
#
# There is now one store. These two checks keep it that way: the survivor must carry
# real provenance, and the retired one must stay retired.
#
# Archived problems are excluded from the retirement rule: they are downgraded work
# kept as a record, and CI still regenerates 05_qaoa_maxcut with --mock.
# ---------------------------------------------------------------------------

ACTIVE_PROBLEM_DIRS = sorted(
    path.parent.parent
    for path in (REPO_ROOT / "problems").glob("*/qsharp/qsharp.json")
    if "archived" not in path.parts
)


def _problem_id(path: Path) -> str:
    return path.relative_to(REPO_ROOT).parts[1]


def test_every_active_problem_was_discovered():
    """Guard the guard: an empty glob would make both checks below vacuous."""
    assert len(ACTIVE_PROBLEM_DIRS) >= 9, (
        f"expected at least 9 active problems, found {len(ACTIVE_PROBLEM_DIRS)}"
    )


@pytest.mark.parametrize(
    "problem_dir", ACTIVE_PROBLEM_DIRS, ids=[_problem_id(p) for p in ACTIVE_PROBLEM_DIRS]
)
def test_the_single_estimate_carries_real_provenance(problem_dir):
    """circuits/estimate.json must say which estimator produced it, and not be mock."""
    problem = _problem_id(problem_dir)
    path = problem_dir / "circuits" / "estimate.json"
    assert path.exists(), (
        f"{problem}: no circuits/estimate.json. It is the single source of truth for "
        f"this problem's resource estimate - run `python tooling/generate_estimates.py`."
    )

    build = json.loads(path.read_text(encoding="utf-8-sig")).get("build", {})
    qdk_version = str(build.get("qdkVersion", ""))
    estimator_version = str(build.get("estimatorVersion", ""))

    assert qdk_version and qdk_version not in ("mock", "unknown"), (
        f"{problem}: circuits/estimate.json build.qdkVersion is {qdk_version!r}. "
        f"An estimate that cannot name the estimator that produced it is not evidence. "
        f"Regenerate with `python tooling/generate_estimates.py`."
    )
    assert not estimator_version.startswith("mock-"), (
        f"{problem}: build.estimatorVersion is {estimator_version!r}, so these numbers "
        f"are simulated output regardless of the qdkVersion recorded."
    )


@pytest.mark.parametrize(
    "problem_dir", ACTIVE_PROBLEM_DIRS, ids=[_problem_id(p) for p in ACTIVE_PROBLEM_DIRS]
)
def test_active_problems_keep_only_one_estimate_store(problem_dir):
    """No second set of resource estimates under problems/<id>/estimates/.

    Selected by shape rather than filename: an estimate artifact from the retired
    pipeline is a mapping carrying estimator_target. Classical baselines, Azure job
    manifests, run results and calibration ensembles live in the same directory,
    describe different things, and stay.
    """
    problem = _problem_id(problem_dir)
    strays = []
    for path in sorted((problem_dir / "estimates").glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (ValueError, OSError):
            continue
        if isinstance(data, dict) and "estimator_target" in data:
            strays.append(path.name)

    assert not strays, (
        f"{problem}: a second estimate store has reappeared under estimates/ - "
        + ", ".join(strays)
        + ". circuits/estimate.json is the single source of truth; two stores is how a "
        "fabricated constant went unnoticed beside real numbers for six months. "
        "tooling/estimator/run_estimation.py refuses to write here without "
        "--allow-retired-store."
    )


