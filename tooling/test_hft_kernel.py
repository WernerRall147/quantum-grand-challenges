"""Problem 06's kernels sample a marked-state probability; the demo must compare like with like.

The problem was presented as amplitude estimation for Value at Risk. The code never ran
amplitude estimation: it prepares a 2-qubit state, marks the states below a threshold, and
measures the marker once per shot. Its demo also printed the probability of the unmarked
states (0.0325) as the "classical VaR" beside the sampled probability of the marked ones
(about 0.97). These tests pin each kernel to its exact distribution and the demo's printed
reference to the quantity the oracle actually marks.
"""

from __future__ import annotations

import collections
import math
from pathlib import Path

import numpy as np
import pytest
from qdk import openqasm, qsharp

REPO_ROOT = Path(__file__).resolve().parents[1]
PROBLEM = REPO_ROOT / "problems" / "archived" / "06_high_frequency_trading"
WEIGHTS = [0.5, 0.35, 0.1, 0.05]


def marked_probability(weights: list[float], threshold: int) -> float:
    """P(index < threshold) for the state that encodes |i> with probability w_i^2 / sum w^2."""
    squares = np.array(weights) ** 2
    return float(squares[:threshold].sum() / squares.sum())


def _within(sampled: float, exact: float, shots: int) -> bool:
    return abs(sampled - exact) < 5 * math.sqrt(max(exact * (1 - exact), 1e-4) / shots)


def test_the_sampled_estimate_is_the_probability_of_the_marked_states():
    qsharp.init(project_root=str(PROBLEM / "qsharp"))
    shots = 2000
    sampled = qsharp.eval(f"Main.EstimateLossProbability({WEIGHTS}, 2, {shots})")
    exact = marked_probability(WEIGHTS, 2)
    assert exact == pytest.approx(0.96753, abs=1e-5)
    assert _within(sampled, exact, shots), (sampled, exact)
    # The complement, which the demo used to print as its reference, is far outside the tolerance.
    assert not _within(sampled, 1 - exact, shots)


def test_the_demo_prints_the_probability_the_oracle_marks():
    qsharp.init(project_root=str(PROBLEM / "qsharp"))
    messages = qsharp.run("Main.RunHFTAnalysis()", shots=1, save_events=True)[0]["messages"]
    exact_line = next(m for m in messages if m.startswith("Exact P(index < 2):"))
    assert float(exact_line.split(":")[1]) == pytest.approx(marked_probability(WEIGHTS, 2), abs=1e-9)
    assert not any("amplitude estimation provides" in m.lower() for m in messages)


def test_the_hardware_kernel_samples_its_exact_marker_probability():
    ry = lambda t: np.array([[math.cos(t / 2), -math.sin(t / 2)], [math.sin(t / 2), math.cos(t / 2)]])
    cx = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    psi = np.zeros(4)
    psi[0] = 1.0
    psi = cx @ np.kron(np.eye(2), ry(0.4)) @ cx @ np.kron(ry(0.8), np.eye(2)) @ psi
    exact = abs(psi[0]) ** 2
    assert abs(exact - 0.8149) < 1e-4

    qsharp.init()
    qsharp.eval((PROBLEM / "qsharp" / "HardwareKernel.qs").read_text(encoding="utf-8"))
    shots = 2000
    ones = sum(1 for s in qsharp.run("HFTKernel()", shots=shots) if str(s[0]) == "One")
    assert _within(ones / shots, exact, shots), (ones / shots, exact)


def test_the_openqasm_export_samples_p_loss_of_0_15():
    source = (PROBLEM / "estimates" / "quantum_var_3q.qasm").read_text(encoding="utf-8")
    shots = 2000
    counts = collections.Counter(str(r[2]) for r in openqasm.run(source, shots=shots))
    exact = math.sin(0.7956 / 2) ** 2
    assert abs(exact - 0.15) < 0.001
    assert _within(counts["One"] / shots, exact, shots)
