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
