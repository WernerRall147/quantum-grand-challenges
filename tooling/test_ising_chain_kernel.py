"""Problem 19's kernels must compute the Trotterized Ising-chain evolution they now claim to.

The kernel was described as a lattice gauge simulation measuring a Wilson loop, with a
printed confinement signature. It is a transverse-field Ising chain, H = beta sum Z_i Z_{i+1}
+ h sum X_i, evolved from |0...0> and measured as the product of Z over all sites; there are
no gauge fields. The circuit itself was right, so these tests pin it to exact evolution of
the same Trotter circuit, for the Q# program, the hardware kernel and the OpenQASM export.

They also pin the kernel bootstrapper, which rewrote every problem's HardwareKernel.qs from
its March templates and would have put back kernels since found to be wrong.
"""

from __future__ import annotations

import collections
import importlib.util
from functools import reduce
from pathlib import Path

import numpy as np
import pytest
from qdk import qsharp
from scipy.linalg import expm

REPO_ROOT = Path(__file__).resolve().parents[1]
PROBLEM = REPO_ROOT / "problems" / "19_quantum_chromodynamics"
SHOTS = 2000

I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.diag([1.0, -1.0]).astype(complex)


def _on(single: np.ndarray, site: int, n: int) -> np.ndarray:
    return reduce(np.kron, [single if k == site else I2 for k in range(n)])


def trotter_state(n: int, beta_dt: float, h_dt: float, steps: int) -> np.ndarray:
    """|0...0> after `steps` first-order steps: all ZZ bonds, then the transverse field."""
    zz = sum(_on(Z, i, n) @ _on(Z, i + 1, n) for i in range(n - 1))
    xx = sum(_on(X, i, n) for i in range(n))
    step = expm(-1j * h_dt * xx) @ expm(-1j * beta_dt * zz)
    psi = np.zeros(2 ** n, dtype=complex)
    psi[0] = 1.0
    for _ in range(steps):
        psi = step @ psi
    return psi


def parity(psi: np.ndarray, n: int) -> float:
    return float(np.real(psi.conj() @ reduce(np.kron, [Z] * n) @ psi))


def site_distribution(psi: np.ndarray) -> dict[int, float]:
    """Probability of each outcome, with qubit i as bit i of the index."""
    n = int(np.log2(len(psi)))
    probs = np.abs(psi) ** 2
    # numpy index: qubit 0 is the most significant bit; convert to little-endian.
    out: dict[int, float] = collections.defaultdict(float)
    for index, p in enumerate(probs):
        bits = [(index >> (n - 1 - q)) & 1 for q in range(n)]
        out[sum(b << q for q, b in enumerate(bits))] += p
    return out


def _tvd(counts: collections.Counter, shots: int, exact: dict[int, float]) -> float:
    keys = set(counts) | set(exact)
    return 0.5 * sum(abs(counts.get(k, 0) / shots - exact.get(k, 0.0)) for k in keys)


def _little_endian(shot) -> int:
    return sum(1 << i for i, r in enumerate(shot) if str(r) == "One")


@pytest.mark.parametrize("beta", [0.5, 2.0])
def test_the_program_samples_the_exact_parity(beta):
    qsharp.init(project_root=str(PROBLEM / "qsharp"))
    sampled = qsharp.eval(f"Main.SimulateLatticeGauge(4, {beta}, 0.3, 5, {SHOTS})")
    exact = parity(trotter_state(4, beta / 5, 0.3 / 5, 5), 4)
    stderr = np.sqrt(max(1 - exact ** 2, 1e-3) / SHOTS)
    assert abs(sampled - exact) < 5 * stderr, (sampled, exact)


def test_the_hardware_kernel_samples_the_exact_distribution():
    qsharp.init()
    qsharp.eval((PROBLEM / "qsharp" / "HardwareKernel.qs").read_text(encoding="utf-8"))
    counts = collections.Counter(_little_endian(s) for s in qsharp.run("LatticeGaugeKernel()", shots=SHOTS))
    exact = site_distribution(trotter_state(4, 0.5, 0.3, 3))
    _assert_discriminating(exact, trotter_state(4, 0.65, 0.3, 3))
    assert _tvd(counts, SHOTS, exact) < 0.06


def test_the_openqasm_export_samples_the_exact_distribution():
    """The same circuit as the hardware kernel."""
    from qdk import openqasm

    source = (PROBLEM / "estimates" / "trotter_gauge.qasm").read_text(encoding="utf-8")
    counts = collections.Counter(_little_endian(s) for s in openqasm.run(source, shots=SHOTS))
    exact = site_distribution(trotter_state(4, 0.5, 0.3, 3))
    assert _tvd(counts, SHOTS, exact) < 0.06


def _assert_discriminating(exact: dict[int, float], wrong: np.ndarray) -> None:
    """The check must be able to fail: a slightly wrong circuit has to land outside the tolerance.

    The previous OpenQASM export used angles so small that every candidate circuit left
    over 99% of the weight on |0000>, and a doubled coupling passed the comparison.
    """
    alternative = site_distribution(wrong)
    keys = set(exact) | set(alternative)
    assert 0.5 * sum(abs(exact.get(k, 0.0) - alternative.get(k, 0.0)) for k in keys) > 0.1
    assert max(exact.values()) < 0.9


def test_the_kernel_bootstrapper_never_overwrites_a_kernel(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("create_hardware_kernels", REPO_ROOT / "tooling" / "create_hardware_kernels.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    existing = tmp_path / "18_photovoltaics" / "qsharp"
    existing.mkdir(parents=True)
    (existing / "HardwareKernel.qs").write_text("// corrected kernel\n", encoding="utf-8")
    missing = tmp_path / "archived" / "05_qaoa_maxcut" / "qsharp"
    missing.mkdir(parents=True)

    monkeypatch.setattr(module, "PROBLEMS_DIR", tmp_path)
    module.main()

    assert (existing / "HardwareKernel.qs").read_text(encoding="utf-8") == "// corrected kernel\n"
    assert (missing / "HardwareKernel.qs").exists()
