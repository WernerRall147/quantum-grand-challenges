"""Archived QAOA kernels must match the toy Hamiltonians they document.

These checks use exact state-vector simulation for the four archived QAOA
problems and compare the Q# programs and hardware kernels against the same
models.  They intentionally distinguish the repository's Q# angle convention
from the textbook QAOA parameter gamma in exp(-i gamma C).
"""

from __future__ import annotations

import collections
import math
from functools import reduce
from pathlib import Path

import numpy as np
import pytest
from qdk import qsharp

REPO_ROOT = Path(__file__).resolve().parents[1]
ARCHIVED = REPO_ROOT / "problems" / "archived"
SHOTS = 1600

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.diag([1.0, -1.0]).astype(complex)

ANGLES = {
    "05": (2.827433388230814, 0.3141592653589793),
    "08": (0.47123889803846897, 1.119192382841364),
    "12": (0.3141592653589793, 1.2566370614359172),
    "20": (0.667588438887831, 1.3940817400304706),
}

W08 = np.array(
    [
        [0.0, -1.2, -0.3, 0.0],
        [-1.2, 0.0, -0.8, -0.5],
        [-0.3, -0.8, 0.0, -1.0],
        [0.0, -0.5, -1.0, 0.0],
    ]
)
W12 = np.array(
    [
        [0.0, 1.0, 0.5, 0.2],
        [1.0, 0.0, 1.2, 0.8],
        [0.5, 1.2, 0.0, 0.6],
        [0.2, 0.8, 0.6, 0.0],
    ]
)
DELTA20 = np.array([[2.5, 1.8], [1.2, 0.8], [3.1, 2.4], [1.5, 1.0]])


def _kron_all(mats: list[np.ndarray]) -> np.ndarray:
    return reduce(np.kron, mats)


def _single(pauli: np.ndarray, site: int, n: int) -> np.ndarray:
    return _kron_all([pauli if q == site else I2 for q in range(n)])


def _zz(site_a: int, site_b: int, n: int) -> np.ndarray:
    return _single(Z, site_a, n) @ _single(Z, site_b, n)


def _rotation(theta: float, generator: np.ndarray) -> np.ndarray:
    return np.cos(theta / 2.0) * np.eye(generator.shape[0]) - 1j * np.sin(theta / 2.0) * generator


def _uniform(n: int) -> np.ndarray:
    return np.ones(2**n, dtype=complex) / math.sqrt(2**n)


def _distribution_little_endian(state: np.ndarray, n: int) -> dict[int, float]:
    dist: dict[int, float] = collections.defaultdict(float)
    for index, probability in enumerate(np.abs(state) ** 2):
        bits = [(index >> (n - 1 - q)) & 1 for q in range(n)]
        dist[sum(bit << q for q, bit in enumerate(bits))] += float(probability)
    return dict(dist)


def _little_endian(shot) -> int:
    return sum(1 << i for i, result in enumerate(shot) if str(result) == "One")


def _tvd(observed: collections.Counter[int], shots: int, exact: dict[int, float]) -> float:
    keys = set(observed) | set(exact)
    return 0.5 * sum(abs(observed.get(k, 0) / shots - exact.get(k, 0.0)) for k in keys)


def _expectation(dist: dict[int, float], cost) -> float:
    return sum(prob * cost(bits) for bits, prob in dist.items())


def _apply_pairwise_qaoa(
    n: int,
    gamma: float,
    beta: float,
    terms: list[tuple[int, int, float]],
    biases: list[tuple[int, float]] | None = None,
) -> dict[int, float]:
    state = _uniform(n)
    for site, theta in biases or []:
        state = _rotation(theta, _single(Z, site, n)) @ state
    for i, j, weight in terms:
        state = _rotation(2.0 * gamma * weight, _zz(i, j, n)) @ state
    for q in range(n):
        state = _rotation(2.0 * beta, _single(X, q, n)) @ state
    return _distribution_little_endian(state, n)


def _maxcut_cost(bits: int) -> float:
    assignment = [(bits >> i) & 1 for i in range(3)]
    return float(sum(assignment[i] != assignment[j] for i, j in [(0, 1), (0, 2), (1, 2)]))


def _same_side_cost(weights: np.ndarray, bits: int) -> float:
    n = weights.shape[0]
    assignment = [(bits >> i) & 1 for i in range(n)]
    return float(sum(weights[i, j] for i in range(n) for j in range(i + 1, n) if assignment[i] == assignment[j]))


def _mission_cost(bits: int) -> float:
    n = len(DELTA20)
    assignment = [(bits >> i) & 1 for i in range(n)]
    return float(
        sum(DELTA20[i, assignment[i]] for i in range(n))
        + sum(0.5 for i in range(n) for j in range(i + 1, n) if assignment[i] == assignment[j])
    )


def _exact_05(gamma: float, beta: float) -> dict[int, float]:
    # MaxCut C=(1-ZZ)/2, but the Q# circuit applies CNOT-Rz(2 gamma)-CNOT,
    # so gamma_standard = -2 gamma up to a global phase.
    return _apply_pairwise_qaoa(3, gamma, beta, [(0, 1, 1.0), (0, 2, 1.0), (1, 2, 1.0)])


def _exact_08(gamma: float, beta: float) -> dict[int, float]:
    return _apply_pairwise_qaoa(
        4,
        gamma,
        beta,
        [(i, j, float(W08[i, j])) for i in range(4) for j in range(i + 1, 4) if abs(W08[i, j]) > 1e-12],
    )


def _exact_12(gamma: float, beta: float) -> dict[int, float]:
    return _apply_pairwise_qaoa(
        4,
        gamma,
        beta,
        [(i, j, float(W12[i, j])) for i in range(4) for j in range(i + 1, 4) if abs(W12[i, j]) > 1e-12],
    )


def _exact_20(gamma: float, beta: float) -> dict[int, float]:
    biases = [(i, 2.0 * gamma * float((DELTA20[i, 0] - DELTA20[i, 1]) / 2.0)) for i in range(4)]
    state = _uniform(4)
    for site, theta in biases:
        state = _rotation(theta, _single(Z, site, 4)) @ state
    for i in range(4):
        for j in range(i + 1, 4):
            state = _rotation(gamma * 0.5, _zz(i, j, 4)) @ state
    for q in range(4):
        state = _rotation(2.0 * beta, _single(X, q, 4)) @ state
    return _distribution_little_endian(state, 4)


def test_qsharp_fixed_angle_expectations_match_exact_statevectors():
    cases = [
        (
            "05_qaoa_maxcut",
            "Main.EvaluateQaoa([[0.0,1.0,1.0],[1.0,0.0,1.0],[1.0,1.0,0.0]], [0.5], [0.5], 1600)",
            _expectation(_exact_05(0.5, 0.5), _maxcut_cost),
        ),
        (
            "08_protein_folding",
            "Main.EvaluateFoldingQaoa([[0.0,-1.2,-0.3,0.0],[-1.2,0.0,-0.8,-0.5],[-0.3,-0.8,0.0,-1.0],[0.0,-0.5,-1.0,0.0]], 0.5, 0.5, 1600)",
            _expectation(_exact_08(0.5, 0.5), lambda b: _same_side_cost(W08, b)),
        ),
        (
            "12_quantum_optimization",
            "Main.EvaluateQaoa([[0.0,1.0,0.5,0.2],[1.0,0.0,1.2,0.8],[0.5,1.2,0.0,0.6],[0.2,0.8,0.6,0.0]], 0.5, 0.5, 1, 1600)",
            _expectation(_exact_12(0.5, 0.5), lambda b: _same_side_cost(W12, b)),
        ),
        (
            "20_space_mission_planning",
            "Main.EvaluateQaoaMission([[2.5,1.8],[1.2,0.8],[3.1,2.4],[1.5,1.0]], 0.5, 0.5, 1, 1600)",
            _expectation(_exact_20(0.5, 0.5), _mission_cost),
        ),
    ]
    for problem, expression, exact in cases:
        qsharp.init(project_root=str(ARCHIVED / problem / "qsharp"))
        sampled = qsharp.run(expression, shots=1)[0][0]
        assert sampled == pytest.approx(exact, abs=0.25), (problem, sampled, exact)


def test_optimized_angles_are_exactly_the_claimed_toy_objectives():
    g05, b05 = ANGLES["05"]
    g08, b08 = ANGLES["08"]
    g12, b12 = ANGLES["12"]
    g20, b20 = ANGLES["20"]

    assert _expectation(_exact_05(g05, b05), _maxcut_cost) == pytest.approx(1.999334805117118, abs=1e-12)
    assert _expectation(_exact_08(g08, b08), lambda b: _same_side_cost(W08, b)) == pytest.approx(
        -3.1250872910581253, abs=1e-12
    )
    assert _expectation(_exact_12(g12, b12), lambda b: _same_side_cost(W12, b)) == pytest.approx(
        1.546699034716197, abs=1e-12
    )
    assert _expectation(_exact_20(g20, b20), _mission_cost) == pytest.approx(8.567469059209166, abs=1e-12)


@pytest.mark.parametrize(
    "problem,operation,exact",
    [
        ("05_qaoa_maxcut", "QaoaMaxCutKernel()", _exact_05(*ANGLES["05"])),
        ("08_protein_folding", "FoldingQaoaKernel()", _exact_08(*ANGLES["08"])),
        ("12_quantum_optimization", "SchedulingQaoaKernel()", _exact_12(*ANGLES["12"])),
        ("20_space_mission_planning", "MissionQaoaKernel()", _exact_20(*ANGLES["20"])),
    ],
)
def test_hardware_kernels_sample_the_same_exact_distributions(problem, operation, exact):
    qsharp.init()
    qsharp.eval((ARCHIVED / problem / "qsharp" / "HardwareKernel.qs").read_text(encoding="utf-8"))
    counts = collections.Counter(_little_endian(shot) for shot in qsharp.run(operation, shots=SHOTS))
    assert _tvd(counts, SHOTS, exact) < 0.08


def test_checks_would_reject_the_old_mission_kernel_variant():
    gamma, beta = ANGLES["20"]
    correct = _exact_20(gamma, beta)
    old_chain = _apply_pairwise_qaoa(
        3,
        1.0,
        0.7,
        [(0, 1, 1.0), (1, 2, 0.8)],
        biases=[(0, 0.8), (1, 1.2), (2, 0.6)],
    )
    keys = set(correct) | set(old_chain)
    assert 0.5 * sum(abs(correct.get(k, 0.0) - old_chain.get(k, 0.0)) for k in keys) > 0.6


def test_depth_sweep_uses_the_modern_qdk_python_driver():
    source = (ARCHIVED / "05_qaoa_maxcut" / "python" / "depth_sweep.py").read_text(encoding="utf-8")
    assert "dotnet" not in source
    assert "qsharp.init" in source


def test_problem_readmes_name_toy_qubo_models_not_protein_or_speedup_claims():
    readme08 = (ARCHIVED / "08_protein_folding" / "README.md").read_text(encoding="utf-8").lower()
    readme12 = (ARCHIVED / "12_quantum_optimization" / "README.md").read_text(encoding="utf-8").lower()
    readme20 = (ARCHIVED / "20_space_mission_planning" / "README.md").read_text(encoding="utf-8").lower()
    assert "toy ising/qubo" in readme08
    assert "no protein sequence, lattice walk, or contact-map geometry" in readme08
    assert "greedy weighted tardiness" in readme12
    assert "heuristic patched-conic scoring" in readme20
    assert "proven speedup" not in readme08 + readme12 + readme20
