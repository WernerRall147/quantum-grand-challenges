"""Problems 04 and 13 must run the HHL circuit they claim to run.

The previous kernels used unrelated Rz/Rx rotations and bit-wise ancilla rotations. These
checks pin the textbook 2x2 HHL construction: exact controlled exp(i A t 2^k), QPE, a
clock-value controlled Ry with amplitude C/lambda, inverse QPE and post-selection.
"""

from __future__ import annotations

import collections
import math
from functools import reduce
from pathlib import Path

import numpy as np
import pytest
from qdk import qsharp
from scipy.linalg import expm

REPO_ROOT = Path(__file__).resolve().parents[1]
PROBLEM04 = REPO_ROOT / "problems" / "archived" / "04_linear_solvers"
PROBLEM13 = REPO_ROOT / "problems" / "archived" / "13_climate_modeling"

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)


def _bits(value: int, n: int) -> list[int]:
    return [(value >> (n - 1 - i)) & 1 for i in range(n)]


def _index(bits: list[int]) -> int:
    out = 0
    for bit in bits:
        out = (out << 1) | bit
    return out


def _apply_h_to_clock(vec: np.ndarray, q: int, n: int) -> np.ndarray:
    out = np.zeros_like(vec)
    for x, amp in enumerate(vec):
        bits = _bits(x, n)
        old = bits[q]
        for new in (0, 1):
            bits[q] = new
            out[_index(bits)] += H[new, old] * amp
        bits[q] = old
    return out


def _qft_matrix(n: int) -> np.ndarray:
    size = 1 << n
    mat = np.zeros((size, size), dtype=complex)
    for basis in range(size):
        vec = np.zeros(size, dtype=complex)
        vec[basis] = 1.0
        for j in range(n):
            vec = _apply_h_to_clock(vec, j, n)
            for k in range(j + 1, n):
                angle = math.pi / (1 << (k - j))
                for idx in range(size):
                    b = _bits(idx, n)
                    if b[k] and b[j]:
                        vec[idx] *= np.exp(1j * angle)
        for j in range(n // 2):
            right = n - j - 1
            swapped = np.zeros_like(vec)
            for idx, amp in enumerate(vec):
                b = _bits(idx, n)
                b[j], b[right] = b[right], b[j]
                swapped[_index(b)] += amp
            vec = swapped
        mat[:, basis] = vec
    return mat


def _hadamard_matrix(n: int) -> np.ndarray:
    return reduce(np.kron, [H] * n)


def _ry(theta: float) -> np.ndarray:
    c = math.cos(theta / 2)
    s = math.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def _axis_evolution(a: np.ndarray, time: float) -> np.ndarray:
    c = 0.5 * (a[0, 0] + a[1, 1])
    z = 0.5 * (a[0, 0] - a[1, 1])
    x = a[0, 1]
    r = math.sqrt(float(z * z + x * x))
    if r == 0:
        return np.exp(1j * c * time) * I2
    alpha = math.atan2(float(x), float(z))
    rz = np.diag([np.exp(1j * r * time), np.exp(-1j * r * time)])
    return np.exp(1j * c * time) * _ry(alpha) @ rz @ _ry(-alpha)


@pytest.mark.parametrize("matrix,bits", [
    (np.array([[4.0, -1.0], [-1.0, 3.0]]), 4),
    (np.array([[2.0, -1.0], [-1.0, 2.0]]), 3),
])
def test_controlled_evolution_formula_is_exact(matrix, bits):
    base_time = 2 * math.pi / (1 << bits)
    for power in [1, 2, 4, 1 << (bits - 1)]:
        expected = expm(1j * matrix * base_time * power)
        actual = _axis_evolution(matrix, base_time * power)
        assert np.max(np.abs(expected - actual)) < 1e-12


def hhl_state(matrix: np.ndarray, rhs: np.ndarray, bits: int, c: float = 1.0) -> np.ndarray:
    size = 1 << bits
    base_time = 2 * math.pi / size
    rhs = rhs / np.linalg.norm(rhs)
    state = np.zeros((size, 2, 2), dtype=complex)
    state[0, :, 0] = rhs

    had = _hadamard_matrix(bits)
    state = np.tensordot(had, state, axes=(1, 0))
    for y in range(size):
        state[y, :, :] = expm(1j * matrix * base_time * y) @ state[y, :, :]
    qft = _qft_matrix(bits)
    state = np.tensordot(qft.conj().T, state, axes=(1, 0))

    for y in range(1, size):
        if c <= y:
            state[y, :, :] = state[y, :, :] @ _ry(2 * math.asin(c / y)).T

    state = np.tensordot(qft, state, axes=(1, 0))
    for y in range(size):
        state[y, :, :] = expm(-1j * matrix * base_time * y) @ state[y, :, :]
    state = np.tensordot(had, state, axes=(1, 0))
    return state


def joint_distribution(state: np.ndarray) -> dict[tuple[int, int], float]:
    probs: dict[tuple[int, int], float] = collections.defaultdict(float)
    for y in range(state.shape[0]):
        for system in (0, 1):
            for ancilla in (0, 1):
                probs[(ancilla, system)] += float(abs(state[y, system, ancilla]) ** 2)
    return dict(probs)


def conditional_system_distribution(state: np.ndarray) -> np.ndarray:
    joint = joint_distribution(state)
    success = joint[(1, 0)] + joint[(1, 1)]
    return np.array([joint[(1, 0)] / success, joint[(1, 1)] / success])


def success_probability(state: np.ndarray) -> float:
    joint = joint_distribution(state)
    return joint[(1, 0)] + joint[(1, 1)]


def _result_bit(result) -> int:
    return 1 if str(result) == "One" else 0


def _tvd_counts(counts: collections.Counter, shots: int, exact: dict) -> float:
    keys = set(counts) | set(exact)
    return 0.5 * sum(abs(counts.get(k, 0) / shots - exact.get(k, 0.0)) for k in keys)


def _program_state(problem: Path, expression: str, bits: int) -> np.ndarray:
    qsharp.init(project_root=str(problem / "qsharp"))
    dump = qsharp.run(expression, shots=1, save_events=True)[0]["dumps"][0]
    dense = np.asarray(dump.as_dense_state())
    return dense.reshape((1 << bits), 2, 2)


def test_problem04_program_matches_the_exact_hhl_circuit():
    matrix = np.array([[4.0, -1.0], [-1.0, 3.0]])
    rhs = np.array([15.0, 10.0])
    exact_state = hhl_state(matrix, rhs, 3)
    exact_conditional = conditional_system_distribution(exact_state)
    rhs_distribution = (rhs / np.linalg.norm(rhs)) ** 2
    assert 0.5 * np.abs(exact_conditional - rhs_distribution).sum() > 0.15
    # The eigenvalues (7 ± √5)/2 fall between 3-bit clock values, so the output only
    # approximates A^-1 b ∝ [5, 5]: [0.479, 0.521] against [0.5, 0.5].
    true_solution = np.linalg.solve(matrix, rhs)
    true_distribution = (true_solution / np.linalg.norm(true_solution)) ** 2
    assert 0.5 * np.abs(exact_conditional - true_distribution).sum() < 0.03

    dumped = _program_state(
        PROBLEM04,
        """{
            use clock = Qubit[3]; use system = Qubit(); use ancilla = Qubit();
            Main.PrepareHHLState2x2([[4.0, -1.0], [-1.0, 3.0]], [15.0, 10.0], 3, system, clock, ancilla);
            Std.Diagnostics.DumpMachine();
            ResetAll(clock + [system, ancilla]);
        }""",
        3,
    )
    assert np.max(np.abs(np.abs(dumped) ** 2 - np.abs(exact_state) ** 2)) < 1e-9

    qsharp.init(project_root=str(PROBLEM04 / "qsharp"))
    shots = 1200
    sampled = collections.Counter(_result_bit(r) for r in qsharp.run(
        "Main.HHLSolve2x2([[4.0, -1.0], [-1.0, 3.0]], [15.0, 10.0], 3)", shots=shots
    ))
    assert _tvd_counts(sampled, shots, {0: exact_conditional[0], 1: exact_conditional[1]}) < 0.06

    success_shots = 2000
    successes = sum(_result_bit(r) for r in qsharp.run(
        "Main.HHLSuccessSample2x2([[4.0, -1.0], [-1.0, 3.0]], [15.0, 10.0], 3)", shots=success_shots
    ))
    expected_success = success_probability(exact_state)
    stderr = math.sqrt(expected_success * (1 - expected_success) / success_shots)
    assert abs(successes / success_shots - expected_success) < 5 * stderr


def test_problem13_program_matches_the_exact_diffusion_solution():
    matrix = np.array([[2.0, -1.0], [-1.0, 2.0]])
    rhs = np.array([1.0, 0.0])
    exact_state = hhl_state(matrix, rhs, 3)
    exact_conditional = conditional_system_distribution(exact_state)
    true_solution = np.linalg.solve(matrix, rhs)
    true_distribution = (true_solution / np.linalg.norm(true_solution)) ** 2
    assert np.max(np.abs(exact_conditional - true_distribution)) < 1e-12
    assert 0.5 * np.abs(true_distribution - rhs**2).sum() > 0.19

    dumped = _program_state(
        PROBLEM13,
        """{
            use clock = Qubit[3]; use system = Qubit(); use ancilla = Qubit();
            Main.PrepareHHLState2x2(Main.ClimateDiffusionMatrix(), Main.ClimateRhs(), 3, system, clock, ancilla);
            Std.Diagnostics.DumpMachine();
            ResetAll(clock + [system, ancilla]);
        }""",
        3,
    )
    assert np.max(np.abs(np.abs(dumped) ** 2 - np.abs(exact_state) ** 2)) < 1e-9

    qsharp.init(project_root=str(PROBLEM13 / "qsharp"))
    shots = 1200
    sampled = collections.Counter(_result_bit(r) for r in qsharp.run("Main.HHLClimateSolutionSample()", shots=shots))
    assert _tvd_counts(sampled, shots, {0: true_distribution[0], 1: true_distribution[1]}) < 0.06

    success = qsharp.eval("Main.RunHHLClimate(3, 2000)")
    expected_success = success_probability(exact_state)
    assert abs(success - expected_success) < 0.06


@pytest.mark.parametrize("problem,kernel,operation,matrix,rhs,bits", [
    (PROBLEM04, "HHLKernel()", "qsharp/HardwareKernel.qs", np.array([[4.0, -1.0], [-1.0, 3.0]]), np.array([15.0, 10.0]), 3),
    (PROBLEM13, "ClimateHHLKernel()", "qsharp/HardwareKernel.qs", np.array([[2.0, -1.0], [-1.0, 2.0]]), np.array([1.0, 0.0]), 3),
])
def test_hardware_kernel_samples_the_exact_joint_distribution(problem, kernel, operation, matrix, rhs, bits):
    exact = joint_distribution(hhl_state(matrix, rhs, bits))
    wrong = {(0, 0): float((rhs / np.linalg.norm(rhs))[0] ** 2), (0, 1): float((rhs / np.linalg.norm(rhs))[1] ** 2), (1, 0): 0.0, (1, 1): 0.0}
    assert 0.5 * sum(abs(exact.get(k, 0.0) - wrong.get(k, 0.0)) for k in set(exact) | set(wrong)) > 0.19

    qsharp.init()
    qsharp.eval((problem / operation).read_text(encoding="utf-8"))
    shots = 2500
    counts = collections.Counter(tuple(_result_bit(r) for r in shot) for shot in qsharp.run(kernel, shots=shots))
    assert _tvd_counts(counts, shots, exact) < 0.06
