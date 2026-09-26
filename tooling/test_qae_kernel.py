"""Problem 03's amplitude-estimation kernels must produce the distributions the textbook predicts.

The canonical QAE kernel reflected about A†|0> instead of A|0> (`within { statePrep }` builds
A† S_0 A) and left out the -1 in Q = -A S_0 A† S_chi, which is observable once Q is controlled.
Its phase register peaked at 0 and 32 of 64 instead of 8 and 56. The one sanity test prepared a
uniform superposition with H, its own inverse, at a = 1/2, where both mistakes are invisible.
These tests compare against Brassard, Hoyer, Mosca and Tapp (2002), Theorem 11, at amplitudes
where they are not.

The IQAE driver claimed to implement Grinko et al. (2021) but doubled k and kept the narrowest of
several candidate intervals, so its stated confidence had no basis. It now runs their Algorithm 1
with FindNextK, and the coverage test below checks the stated confidence by repetition.
"""

from __future__ import annotations

import importlib.util
import math
import re
import sys
from pathlib import Path

import numpy as np
import pytest
from qdk import qsharp

REPO_ROOT = Path(__file__).resolve().parents[1]
PROBLEM = REPO_ROOT / "problems" / "archived" / "03_qae_risk"


def _load_driver():
    spec = importlib.util.spec_from_file_location("iqae_driver", PROBLEM / "python" / "iqae_driver.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


driver = _load_driver()


def phase_distribution(a: float, bits: int) -> np.ndarray:
    """Theorem 11 of Brassard et al. applied to Q's two eigenphases, +-theta/pi, with equal weight."""
    theta = math.asin(math.sqrt(a))
    size = 1 << bits

    def fejer(delta: float) -> float:
        s = math.sin(math.pi * delta)
        return 1.0 if abs(s) < 1e-12 else (math.sin(math.pi * size * delta) / (size * s)) ** 2

    return np.array([0.5 * fejer(theta / math.pi - y / size) + 0.5 * fejer(-theta / math.pi - y / size) for y in range(size)])


def _tvd(p: np.ndarray, q: np.ndarray) -> float:
    return 0.5 * float(np.abs(p - q).sum())


def _big_endian(shot) -> int:
    return sum(1 << (len(shot) - 1 - i) for i, r in enumerate(shot) if str(r) == "One")


def _phase_register_marginal(loss_qubits: int, bits: int, threshold: float) -> np.ndarray:
    """Exact distribution of the phase register, from the simulator's state vector."""
    qsharp.init(project_root=str(PROBLEM / "qsharp"))
    expr = f"""{{
        use p = Qubit[{bits}]; use l = Qubit[{loss_qubits}]; use m = Qubit();
        Main.QuantumPhaseEstimationQAE(
            Main.PrepareDistributionState(Main.LogNormalProbabilities({loss_qubits}, 0.0, 1.0), _),
            Main.OracleTailMarking({threshold}, {loss_qubits}, _, _), p, l, m);
        Std.Diagnostics.DumpMachine();
        ResetAll(p + l + [m]);
    }}"""
    dump = qsharp.run(expr, shots=1, save_events=True)[0]["dumps"][0]
    assert dump.qubit_count == bits + loss_qubits + 1
    state = np.asarray(dump.as_dense_state())
    # The first qubit allocated is the most significant bit of the index, so the phase register
    # (allocated first, most significant qubit first) is the top `bits` bits.
    return (np.abs(state.reshape(1 << bits, -1)) ** 2).sum(axis=1)


def test_the_python_distribution_is_the_one_the_circuit_loads():
    qsharp.init(project_root=str(PROBLEM / "qsharp"))
    loaded = qsharp.eval("Main.LogNormalProbabilities(4, 0.0, 1.0)")
    probabilities, _ = driver.discrete_loss_distribution(4, 0.0, 1.0)
    assert np.allclose(loaded, probabilities, atol=1e-12)
    tail = qsharp.eval("Main.TailProbability(Main.LogNormalProbabilities(4, 0.0, 1.0), 2.5, 4)")
    assert tail == pytest.approx(driver.discrete_tail_probability(4, 2.5, 0.0, 1.0), abs=1e-12)
    assert tail == pytest.approx(0.161363, abs=1e-6)


@pytest.mark.parametrize("loss_qubits, bits, threshold", [(4, 6, 2.5), (3, 5, 5.0)])
def test_the_phase_register_follows_theorem_11(loss_qubits, bits, threshold):
    a = driver.discrete_tail_probability(loss_qubits, threshold, 0.0, 1.0)
    exact = phase_distribution(a, bits)
    # A sign error in Q moves the peaks to 1/2 +- theta/pi, the distribution for 1 - a.
    assert _tvd(exact, phase_distribution(1 - a, bits)) > 0.5
    marginal = _phase_register_marginal(loss_qubits, bits, threshold)
    assert np.max(np.abs(marginal - exact)) < 1e-9


def test_the_estimator_entry_point_reads_the_register_most_significant_bit_first():
    """Main.QAEKernel() is what the estimator and calibration run. 91% of shots fold to 7-10."""
    qsharp.init(project_root=str(PROBLEM / "qsharp"))
    shots = qsharp.run("Main.QAEKernel()", shots=40)
    near_peak = sum(1 for s in shots if min(_big_endian(s), 64 - _big_endian(s)) in (7, 8, 9, 10))
    assert near_peak >= 28, [_big_endian(s) for s in shots]


def test_the_hardware_kernel_follows_theorem_11():
    """Two phase bits: the kernel exercises the circuit, it cannot estimate a (mean decode 0.42 for a = 0.23)."""
    qsharp.init()
    qsharp.eval((PROBLEM / "qsharp" / "HardwareKernel.qs").read_text(encoding="utf-8"))
    shots = 2000
    counts = np.bincount([_big_endian(s) for s in qsharp.run("QAEKernel()", shots=shots)], minlength=4)
    a = driver.discrete_tail_probability(2, 2.5, 0.0, 1.0)
    exact = phase_distribution(a, 2)
    # At two bits a sign error only swaps outcomes 0 and 2 (distance 0.15), still over twice the tolerance.
    assert _tvd(exact, phase_distribution(1 - a, 2)) > 0.1
    assert _tvd(counts / shots, exact) < 0.05


@pytest.mark.parametrize("k", [1, 3])
def test_an_iqae_round_measures_sin_squared(k):
    qsharp.init(project_root=str(PROBLEM / "qsharp"))
    shots = 400
    results = qsharp.run(f"Main.IQAERound(Main.LogNormalProbabilities(4, 0.0, 1.0), 2.5, 4, {k})", shots=shots)
    measured = sum(1 for r in results if str(r) == "One") / shots
    theta = math.asin(math.sqrt(driver.discrete_tail_probability(4, 2.5, 0.0, 1.0)))
    expected = math.sin((2 * k + 1) * theta) ** 2
    assert abs(measured - expected) < 5 * math.sqrt(expected * (1 - expected) / shots)


def test_find_next_k_keeps_the_scaled_interval_in_one_half_circle():
    assert driver.find_next_k(0, True, (0.0, 0.25)) == (0, True)
    # By hand: K = 50, 46, 42, 38 and 34 straddle a half-circle boundary; K = 30 maps
    # [0.05, 0.06] to [1.5, 1.8] turns, the lower half-circle, so k = (30 - 2) / 4 = 7.
    assert driver.find_next_k(0, True, (0.05, 0.06)) == (7, False)


def test_iqae_intervals_hold_their_stated_confidence():
    a = driver.discrete_tail_probability(4, 2.5, 0.0, 1.0)
    rng = np.random.default_rng(2026)
    params = driver.IQAEParams(epsilon=0.01, alpha=0.05)
    runs = [driver.iterative_amplitude_estimation(driver.exact_sampler(a, rng), params) for _ in range(300)]
    misses = sum(1 for r in runs if not r.confidence_interval[0] <= a <= r.confidence_interval[1])
    assert misses <= 15, misses
    assert all(r.converged and r.epsilon_achieved <= params.epsilon for r in runs)


def test_iqae_queries_grow_as_one_over_epsilon():
    """Five times the precision costs about five times the queries; Monte Carlo would need 25."""
    a = driver.discrete_tail_probability(4, 2.5, 0.0, 1.0)
    rng = np.random.default_rng(7)

    def mean_queries(epsilon: float) -> float:
        params = driver.IQAEParams(epsilon=epsilon, alpha=0.05)
        return float(np.mean([driver.iterative_amplitude_estimation(driver.exact_sampler(a, rng), params).total_oracle_queries for _ in range(40)]))

    assert mean_queries(0.002) / mean_queries(0.01) < 10


def test_iqae_on_the_kernel_brackets_the_tail_probability():
    qsharp.init(project_root=str(PROBLEM / "qsharp"))
    result = driver.AdaptiveIQAE(driver.IQAEParams(epsilon=0.05, alpha=0.01)).run_local(verbose=False)
    lo, hi = result.confidence_interval
    assert lo <= driver.discrete_tail_probability(4, 2.5, 0.0, 1.0) <= hi, (lo, hi)
    assert result.converged


def test_calibration_decodes_the_phase_register_most_significant_bit_first():
    """The calibration read Result[] least significant bit first, recording outcome 8 as 4."""
    sys.path.insert(0, str(REPO_ROOT / "tooling"))
    import generate_calibration_ensemble as calibration

    target = calibration.CALIBRATION_TARGETS["03_qae_risk"]
    assert target["entry"] == "Main.QAEKernel()"
    eight = ["Zero", "Zero", "One", "Zero", "Zero", "Zero"]
    assert calibration.run_value([eight], target) == pytest.approx(math.sin(math.pi * 8 / 64) ** 2)


def test_the_documents_quote_the_tail_probability_the_circuit_encodes():
    """18.98% matched no computation: the circuit encodes 16.14%, the continuous model 17.98%.

    19.58% ± 1.82% was the mean of a broken kernel's outcomes; corrections may name it, not quote it as a result.
    """
    readme = (PROBLEM / "README.md").read_text(encoding="utf-8")
    assert f"{100 * driver.discrete_tail_probability(4, 2.5, 0.0, 1.0):.2f}%" in readme
    for doc in PROBLEM.glob("*.md"):
        text = doc.read_text(encoding="utf-8")
        assert "18.98" not in text, doc.name
        assert not re.search(r"19\.58%\s*±", text), doc.name
