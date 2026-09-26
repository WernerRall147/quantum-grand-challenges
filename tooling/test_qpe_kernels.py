"""QPE programs must estimate the energies of the Hamiltonians they claim to simulate.

Five active problems (01, 02, 07, 14, 17) were "upgraded from VQE to QPE" in April 2026,
but every controlled evolution was built from Rz and CNOT-conjugated Rz gates alone. That
unitary is diagonal, so from a computational basis state the phase register returned the
diagonal energy of that basis state, never the ground state, and the XX and YY terms the
comments described were not in the circuit. Nothing checked what the circuits computed.

These tests read each Hamiltonian from the Q# code itself, diagonalise it, predict the full
distribution of phase-register outcomes, and compare it with what the Q# programs sample.
They also pin the physical reference each Hamiltonian is meant to reproduce.
"""

from __future__ import annotations

import collections
from functools import reduce
from pathlib import Path

import numpy as np
import pytest
from qdk import qsharp
from scipy.linalg import expm

REPO_ROOT = Path(__file__).resolve().parents[1]
SHOTS = 300
PHASE_BITS = 4
KERNEL_PHASE_BITS = 2
ESTIMATE_PHASE_BITS = 10
# Sampling alone gives a total variation distance of about 0.05 at 300 shots; the diagonal
# circuits these replaced were above 0.4 on every problem.
TVD_LIMIT = 0.15

PAULI = {
    "I": np.eye(2),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]]),
    "Z": np.diag([1.0, -1.0]).astype(complex),
}


def _basis(bits: str) -> np.ndarray:
    psi = np.zeros(2 ** len(bits), dtype=complex)
    psi[int(bits, 2)] = 1.0
    return psi


# Register qubit i is tensor factor i (the most significant for i = 0), matching Q#'s
# order of Pauli arrays and of the reference bits.
PROBLEMS = {
    "01_hubbard": {
        "hamiltonian": "Main.HubbardHamiltonian(1.0, 4.0)",
        "steps": "Main.HubbardTrotterSteps()",
        "outcome": "Main.HubbardQPEOutcome(1.0, 4.0, {bits})",
        "kernel": "HubbardQPEKernel",
        "reference": (_basis("1001") + _basis("0110")) / np.sqrt(2),
    },
    "02_catalysis": {
        "hamiltonian": "Main.MolecularHamiltonian()",
        "steps": "Main.MolecularTrotterSteps()",
        "outcome": "Main.MolecularQPEOutcome({bits})",
        "kernel": "CatalysisQPEKernel",
        "reference": _basis("10"),
    },
    "07_drug_discovery": {
        "hamiltonian": "Main.BindingHamiltonian()",
        "steps": "Main.BindingTrotterSteps()",
        "outcome": "Main.BindingQPEOutcome({bits})",
        "kernel": "DrugBindingQPEKernel",
        "reference": _basis("10"),
    },
    "14_materials_discovery": {
        "hamiltonian": "Main.BandHamiltonian(1.0, -0.5, 0.8, 0.3)",
        "steps": "Main.BandTrotterSteps()",
        "outcome": "Main.BandQPEOutcome(1.0, -0.5, 0.8, 0.3, [1, 0], {bits})",
        "kernel": "MaterialsQPEKernel",
        "reference": _basis("10"),
    },
    "17_nuclear_physics": {
        "hamiltonian": "Main.DeuteronHamiltonian()",
        "steps": "Main.DeuteronTrotterSteps()",
        "outcome": "Main.NuclearQPEOutcome({bits})",
        "kernel": "NuclearQPEKernel",
        "reference": _basis("10"),
    },
}


def _project(pid: str) -> None:
    qsharp.init(project_root=str(REPO_ROOT / "problems" / pid / "qsharp"))


def _terms(pid: str) -> tuple[list[tuple[str, float]], float]:
    _project(pid)
    paulis, coeffs, offset = qsharp.eval(PROBLEMS[pid]["hamiltonian"])
    strings = ["".join(str(p)[-1] for p in row) for row in paulis]
    return list(zip(strings, coeffs)), offset


def _matrix(terms: list[tuple[str, float]]) -> np.ndarray:
    return sum(c * reduce(np.kron, [PAULI[ch] for ch in s]) for s, c in terms)


def _evolution(terms: list[tuple[str, float]], steps: int) -> tuple[np.ndarray, float]:
    """U = exp(-i H' tau) from the same symmetric Trotter steps the Q# code applies."""
    tau = np.pi / (2 * sum(abs(c) for _, c in terms))
    halves = [expm(-0.5j * c * (tau / steps) * _matrix([(s, 1.0)])) for s, c in terms]
    step = reduce(np.matmul, halves) @ reduce(np.matmul, halves[::-1])
    return np.linalg.matrix_power(step, steps), tau


def _predicted(terms, psi, bits: int, steps: int) -> np.ndarray:
    """Exact QPE outcome distribution: P(m) = |2^-n sum_x exp(-2 pi i x m / 2^n) U^x psi|^2."""
    unitary, _ = _evolution(terms, steps)
    n = 2 ** bits
    powers = [psi]
    for _ in range(n - 1):
        powers.append(unitary @ powers[-1])
    return np.array([
        np.linalg.norm(sum(np.exp(-2j * np.pi * x * m / n) * powers[x] for x in range(n)) / n) ** 2
        for m in range(n)
    ])


def _tvd(samples: list[int], predicted: np.ndarray) -> float:
    counts = collections.Counter(samples)
    empirical = np.array([counts.get(m, 0) / len(samples) for m in range(len(predicted))])
    return 0.5 * float(np.abs(empirical - predicted).sum())


def _reachable_ground(pid: str) -> tuple[float, np.ndarray, np.ndarray]:
    """Lowest energy the reference state can reach, with the spectrum and overlaps."""
    terms, offset = _terms(pid)
    energies, vectors = np.linalg.eigh(_matrix(terms))
    overlaps = np.abs(vectors.conj().T @ PROBLEMS[pid]["reference"]) ** 2
    reachable = energies[overlaps > 1e-9]
    return float(reachable.min()) + offset, energies + offset, overlaps


def test_hubbard_hamiltonian_is_the_two_site_hubbard_model() -> None:
    t, u = 1.0, 4.0
    ground, _, _ = _reachable_ground("01_hubbard")
    assert ground == pytest.approx((u - np.sqrt(u * u + 16 * t * t)) / 2, abs=1e-9)


def test_h2_hamiltonian_reproduces_the_full_ci_energy() -> None:
    ground, _, _ = _reachable_ground("02_catalysis")
    assert qsharp.eval("Main.NuclearRepulsionEnergy()") == pytest.approx(0.7199689944489797)
    assert ground + 0.7199689944489797 == pytest.approx(-1.137306, abs=1e-6)


def test_binding_hamiltonian_ground_energy_is_the_value_the_demo_prints() -> None:
    ground, _, _ = _reachable_ground("07_drug_discovery")
    assert ground == pytest.approx(-1.024708, abs=1e-6)


def test_band_gap_is_the_bonding_antibonding_splitting() -> None:
    _, energies, overlaps = _reachable_ground("14_materials_discovery")
    levels = sorted(energies[overlaps > 1e-9])
    assert levels[-1] - levels[0] == pytest.approx(4.386342, abs=1e-6)


def test_deuteron_hamiltonian_reproduces_the_published_two_state_energy() -> None:
    ground, _, _ = _reachable_ground("17_nuclear_physics")
    assert ground == pytest.approx(-1.749, abs=1e-3)


@pytest.mark.parametrize("pid", sorted(PROBLEMS))
def test_reference_state_overlaps_the_ground_state_most(pid: str) -> None:
    """The QPE estimate is the most frequent outcome, so the ground state must dominate."""
    ground, energies, overlaps = _reachable_ground(pid)
    best = int(np.argmax(overlaps))
    assert energies[best] == pytest.approx(ground), (
        f"{pid}: the reference overlaps E={energies[best]:.4f} most, not the ground state"
    )


@pytest.mark.parametrize("pid", sorted(PROBLEMS))
def test_trotter_error_is_below_half_a_phase_bin(pid: str) -> None:
    terms, offset = _terms(pid)
    steps = qsharp.eval(PROBLEMS[pid]["steps"])
    ground, _, _ = _reachable_ground(pid)
    unitary, tau = _evolution(terms, steps)
    trotter = -np.angle(np.linalg.eigvals(unitary)) / tau + offset
    resolution = 4 * sum(abs(c) for _, c in terms) / 2 ** ESTIMATE_PHASE_BITS
    assert np.min(np.abs(trotter - ground)) < resolution / 2


@pytest.mark.parametrize("pid", sorted(PROBLEMS))
def test_qpe_samples_the_predicted_outcome_distribution(pid: str) -> None:
    terms, _ = _terms(pid)
    steps = qsharp.eval(PROBLEMS[pid]["steps"])
    samples = qsharp.run(PROBLEMS[pid]["outcome"].format(bits=PHASE_BITS), shots=SHOTS)
    predicted = _predicted(terms, PROBLEMS[pid]["reference"], PHASE_BITS, steps)
    assert _tvd(samples, predicted) < TVD_LIMIT


@pytest.mark.parametrize("pid", sorted(PROBLEMS))
def test_hardware_kernel_samples_the_predicted_outcome_distribution(pid: str) -> None:
    terms, _ = _terms(pid)
    kernel = REPO_ROOT / "problems" / pid / "qsharp" / "HardwareKernel.qs"
    qsharp.init()
    qsharp.eval(kernel.read_text(encoding="utf-8"))
    results = qsharp.run(f"{PROBLEMS[pid]['kernel']}()", shots=SHOTS)
    samples = [sum(1 << i for i, r in enumerate(bits) if str(r) == "One") for bits in results]
    predicted = _predicted(terms, PROBLEMS[pid]["reference"], KERNEL_PHASE_BITS, 1)
    assert _tvd(samples, predicted) < TVD_LIMIT
