"""Estimate summaries must count every non-Clifford gate the program contains.

Only the trace's CCZ was mapped to cczCount, but Q#'s CCNOT traces as CCX, so no Toffoli
was ever counted: every published estimate reported cczCount null, including problem 03's,
whose program has 10,687 Toffolis beside its 15 T gates. The paper then described that
kernel's cost as driven by rotations "rather than its 15 T gates".
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest
from qdk import qsharp

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tooling"))

from estimator_config import _logical_counts  # noqa: E402

PROGRAM = """
operation Main() : Result[] {
    use qs = Qubit[3];
    H(qs[0]);
    H(qs[1]);
    CCNOT(qs[0], qs[1], qs[2]);
    CCNOT(qs[1], qs[2], qs[0]);
    Controlled Z([qs[0], qs[1]], qs[2]);
    T(qs[0]);
    Adjoint T(qs[1]);
    Rz(0.123, qs[2]);
    Rx(0.456, qs[0]);
    return MResetEachZ(qs);
}
"""


@pytest.fixture()
def project():
    root = Path(tempfile.mkdtemp())
    (root / "qsharp.json").write_text("{}")
    (root / "src").mkdir()
    (root / "src" / "Main.qs").write_text(PROGRAM, encoding="utf-8")
    qsharp.init(project_root=str(root))


def test_toffolis_are_counted(project):
    counts = _logical_counts("Main.Main()")
    assert counts["cczCount"] == 3


def test_t_and_rotations_are_counted(project):
    counts = _logical_counts("Main.Main()")
    assert counts["tCount"] == 2
    assert counts["rotationCount"] == 2
    assert counts["measurementCount"] == 3
