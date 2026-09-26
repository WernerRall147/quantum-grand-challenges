"""Problem 11's swap test must estimate the overlap of the states it claims to encode.

The feature encoding applied AbsD to every amplitude, so a vector with negative entries was
encoded as its absolute values while the classical reference kept the signs. The hardware
kernel swapped two product states unrelated to any feature vector. And the demo claimed the
swap test needs O(1) measurements and gives an exponential speedup; its error falls as
1/sqrt(shots), and loading classical data costs O(d) gates. These tests pin the encoding, the
program and the hardware kernel to exact values.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest
from qdk import qsharp

REPO_ROOT = Path(__file__).resolve().parents[1]
PROBLEM = REPO_ROOT / "problems" / "archived" / "11_quantum_machine_learning"
ESTIMATOR_A = [1.0, 0.5, 0.3, 0.2]
ESTIMATOR_B = [0.8, 0.2, 0.6, 0.1]


def p_zero(a: list[float], b: list[float]) -> float:
    """Swap test: P(ancilla = 0) = (1 + |<a|b>|^2) / 2 for the normalized vectors."""
    a, b = np.array(a), np.array(b)
    overlap = float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
    return 0.5 * (1.0 + overlap * overlap)


def _within(sampled: float, exact: float, shots: int) -> bool:
    return abs(sampled - exact) < 5 * math.sqrt(max(exact * (1 - exact), 1e-4) / shots)


def test_the_encoding_keeps_the_signs():
    features = [0.5, -0.5, 0.3, -0.7]
    qsharp.init(project_root=str(PROBLEM / "qsharp"))
    dump = qsharp.run(
        f"{{ use q = Qubit[2]; Main.PrepareFeatureState({features}, q); Std.Diagnostics.DumpMachine(); ResetAll(q); }}",
        shots=1,
        save_events=True,
    )[0]["dumps"][0]
    state = np.asarray(dump.as_dense_state())
    expected = np.array(features) / np.linalg.norm(features)
    assert np.max(np.abs(state - expected)) < 1e-9


@pytest.mark.parametrize(
    "a, b",
    [
        (ESTIMATOR_A, ESTIMATOR_B),
        # With signs dropped both vectors encode the same state and P(0) would be 1.
        ([0.5, -0.5, 0.5, 0.5], [0.5, 0.5, 0.5, 0.5]),
    ],
)
def test_the_swap_test_samples_the_exact_probability(a, b):
    qsharp.init(project_root=str(PROBLEM / "qsharp"))
    shots = 1500
    sampled = qsharp.eval(f"Main.SwapTest({a}, {b}, {shots})")
    assert _within(sampled, p_zero(a, b), shots), (sampled, p_zero(a, b))


def test_the_hardware_kernel_swaps_the_estimator_vectors():
    exact = p_zero(ESTIMATOR_A, ESTIMATOR_B)
    assert exact == pytest.approx(0.9175, abs=1e-4)
    qsharp.init()
    qsharp.eval((PROBLEM / "qsharp" / "HardwareKernel.qs").read_text(encoding="utf-8"))
    shots = 2000
    zeros = sum(1 for s in qsharp.run("SwapTestKernel()", shots=shots) if str(s[0]) == "Zero")
    assert _within(zeros / shots, exact, shots), (zeros / shots, exact)


def test_the_demo_claims_no_speedup():
    qsharp.init(project_root=str(PROBLEM / "qsharp"))
    messages = " ".join(qsharp.run("Main.RunQuantumKernelEstimation()", shots=1, save_events=True)[0]["messages"])
    assert "exponential speedup" not in messages
    assert "O(1) measurements" not in messages
