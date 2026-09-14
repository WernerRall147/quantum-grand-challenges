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
# how nine unrelated problems came to report an identical 16 logical / 35,200 physical,
# and why problems/*/estimates/ disagreed with problems/*/circuits/estimate.json.
#
# Those artifacts feed tooling/azure/assess_problem_readiness.py and
# prepare_problem_manifest.py, so the fabrication reached readiness claims.
#
# Archived problems are excluded: they are downgraded work kept as a record, not
# something the evaluator serves.
# ---------------------------------------------------------------------------

ACTIVE_LATEST = sorted(
    path
    for path in (REPO_ROOT / "problems").glob("*/estimates/latest.json")
    if "archived" not in path.parts
)


def _result_artifacts() -> list[Path]:
    """Every estimate artifact an active problem serves.

    Not just latest.json. The fabricated numbers also sat in latest_<target>.json,
    latest_<target>_<instance>.json - which tooling/estimator/generate_summary.py
    prefers over the per-target file - and in the timestamped run records. A guard
    that read only latest.json would have passed while 30 of them were still mock.

    Selected by shape rather than filename: an estimate artifact is a mapping with an
    estimator_target. Classical baselines and Azure job manifests live in the same
    directory and are not estimates.
    """
    found = []
    for path in sorted((REPO_ROOT / "problems").glob("*/estimates/*.json")):
        if "archived" in path.parts:
            continue
        try:
            # utf-8-sig: several committed artifacts carry a BOM.
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (ValueError, OSError):
            continue
        if isinstance(data, dict) and "estimator_target" in data:
            found.append(path)
    return found


ACTIVE_ARTIFACTS = _result_artifacts()


def _active_id(path: Path) -> str:
    return path.relative_to(REPO_ROOT).parts[1]


def _artifact_id(path: Path) -> str:
    return f"{_active_id(path)}/{path.name}"


def test_every_active_problem_has_a_latest_estimate():
    """Guard the guard: an empty glob would make both checks below vacuous."""
    assert len(ACTIVE_LATEST) >= 9, (
        f"expected at least 9 active problems/*/estimates/latest.json, "
        f"found {len(ACTIVE_LATEST)}"
    )
    assert len(ACTIVE_ARTIFACTS) >= len(ACTIVE_LATEST), (
        f"found {len(ACTIVE_ARTIFACTS)} estimate artifacts but "
        f"{len(ACTIVE_LATEST)} latest.json files; the artifact selector is broken"
    )


@pytest.mark.parametrize(
    "path", ACTIVE_ARTIFACTS, ids=[_artifact_id(p) for p in ACTIVE_ARTIFACTS]
)
def test_active_estimate_was_not_fabricated(path):
    """Provenance must name a real estimator, never the mock generator."""
    build = json.loads(path.read_text(encoding="utf-8-sig")).get("build", {})
    qdk_version = str(build.get("qdk_version", ""))
    estimator_version = str(build.get("estimator_version", ""))

    assert qdk_version and qdk_version != "mock", (
        f"{_artifact_id(path)}: build.qdk_version is {qdk_version!r}. These numbers were "
        f"generated by _generate_mock_output(), not measured. Regenerate with "
        f"tooling/estimator/run_estimation.py (no --mock), or delete the artifact."
    )
    assert not estimator_version.startswith("mock-"), (
        f"{_artifact_id(path)}: build.estimator_version is {estimator_version!r}, so the "
        f"artifact is simulated output regardless of the qdk_version recorded."
    )


@pytest.mark.parametrize(
    "path", ACTIVE_LATEST, ids=[_active_id(p) for p in ACTIVE_LATEST]
)
def test_active_estimate_agrees_with_the_other_pipeline(path):
    """Two independent pipelines, one truth.

    circuits/estimate.json comes from tooling/generate_estimates.py and
    estimates/latest.json from tooling/estimator/run_estimation.py. Both now call the
    same QDK estimator, so they must agree; a fabricated value in either diverges from
    the other immediately.

    Deliberately not "every problem reports a different budget". Three active problems
    genuinely coincide at 12 logical / 57,764 physical - 02_catalysis,
    07_drug_discovery and 17_nuclear_physics share one VQE-shaped ansatz - so a
    distinctness rule would fail on true data, and a check with known false positives
    is one people learn to ignore.
    """
    problem = _active_id(path)
    reference_path = path.parent.parent / "circuits" / "estimate.json"
    if not reference_path.exists():
        pytest.skip(f"{problem}: no circuits/estimate.json to compare against")

    metrics = json.loads(path.read_text(encoding="utf-8")).get("metrics", {})
    reference = json.loads(reference_path.read_text(encoding="utf-8"))

    mismatches = [
        f"{name}: estimates/latest.json={got!r} vs circuits/estimate.json={want!r}"
        for name, got, want in (
            ("logical_qubits", metrics.get("logical_qubits"), reference.get("logicalQubits")),
            ("physical_qubits", metrics.get("physical_qubits"), reference.get("physicalQubits")),
        )
        if want is not None and got != want
    ]

    assert not mismatches, (
        f"{problem}: the two estimate pipelines disagree - " + "; ".join(mismatches)
        + ". One of them is not measuring what it claims."
    )
