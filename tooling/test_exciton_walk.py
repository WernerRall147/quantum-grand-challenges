"""The photovoltaics kernels must perform the coined quantum walk they describe.

The shift swapped the two position qubits in both coin branches, so the walker moved the
same way whatever the coin said: every shot of the 10-step walk ended on site 1, and the
hardware kernel, which started from |00>, never left site 0. The calibration ensemble
recorded that as a mean site of 1.0 with zero spread, and nothing checked what the
circuit did.

These tests simulate the same walk exactly and compare it with what the Q# programs sample.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from qdk import qsharp

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT = REPO_ROOT / "problems" / "18_photovoltaics" / "qsharp"
SHOTS = 300
# Sampling alone gives a total variation distance of about 0.05 at 300 shots; the broken
# kernels were at 0.64 (10 steps) and 0.29 (hardware kernel).
TVD_LIMIT = 0.15


def exact_walk(steps: int, coupling: float, start: int = 1, sites: int = 4) -> np.ndarray:
    """Site distribution of the coined walk on a ring: coin Ry(2 * coupling), |1> steps right."""
    c, s = np.cos(coupling), np.sin(coupling)
    coin = np.array([[c, -s], [s, c]])
    psi = np.zeros((2, sites), dtype=complex)
    psi[0, start] = 1.0
    for _ in range(steps):
        psi = coin @ psi
        psi = np.stack([np.roll(psi[0], -1), np.roll(psi[1], 1)])
    return (np.abs(psi) ** 2).sum(axis=0)


def _tvd(sampled: np.ndarray, predicted: np.ndarray) -> float:
    return 0.5 * float(np.abs(sampled - predicted).sum())


@pytest.fixture()
def main_project():
    qsharp.init(project_root=str(PROJECT))


def test_the_reference_walk_spreads_over_more_than_one_site():
    predicted = exact_walk(10, 0.5)
    assert predicted.sum() == pytest.approx(1.0)
    assert (predicted > 0.05).sum() >= 2


def test_the_walk_samples_the_exact_distribution(main_project):
    counts = qsharp.eval(f"Main.RunExcitonWalk(10, 0.5, {SHOTS})")
    assert sum(counts) == SHOTS
    assert _tvd(np.array(counts) / SHOTS, exact_walk(10, 0.5)) < TVD_LIMIT


@pytest.mark.parametrize("coupling, site", [(0.0, 3), (np.pi / 2, 1)])
def test_the_coin_sets_the_direction(main_project, coupling: float, site: int):
    """Two steps from site 1: a coin that never turns steps left twice (to 3), one that
    flips every step goes right and back (to 1). The old kernel ended on 1 either way."""
    counts = qsharp.eval(f"Main.RunExcitonWalk(2, {coupling!r}, 20)")
    assert counts[site] == 20, counts


def test_hardware_kernel_samples_the_exact_distribution():
    qsharp.init()
    qsharp.eval((PROJECT / "HardwareKernel.qs").read_text(encoding="utf-8"))
    results = qsharp.run("QuantumWalkKernel()", shots=SHOTS)
    sites = [2 * (str(r[1]) == "One") + (str(r[2]) == "One") for r in results]
    sampled = np.bincount(sites, minlength=4) / SHOTS
    assert _tvd(sampled, exact_walk(3, 0.5)) < TVD_LIMIT
