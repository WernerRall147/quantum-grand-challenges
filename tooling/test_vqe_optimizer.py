"""The Hubbard VQE driver must execute Q# instead of a classical surrogate."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np
import pytest
from qdk import qsharp

ROOT = Path(__file__).resolve().parents[1]
VQE_PATH = ROOT / "problems" / "01_hubbard" / "python" / "vqe_optimizer.py"
QSHARP_ROOT = ROOT / "problems" / "01_hubbard" / "qsharp"
VQE_SOURCE = QSHARP_ROOT / "VqeHardwareKernel.qs"

spec = importlib.util.spec_from_file_location("vqe_optimizer", VQE_PATH)
assert spec and spec.loader
vqe_optimizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vqe_optimizer)

X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.diag([1.0, -1.0]).astype(complex)
I2 = np.eye(2, dtype=complex)
CNOT = np.array(
    [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0],
    ],
    dtype=complex,
)


def _ry(theta: float) -> np.ndarray:
    cosine = math.cos(theta / 2.0)
    sine = math.sin(theta / 2.0)
    return np.array([[cosine, -sine], [sine, cosine]], dtype=complex)


def _rz(theta: float) -> np.ndarray:
    return np.diag(
        [np.exp(-0.5j * theta), np.exp(0.5j * theta)]
    ).astype(complex)


def _exact_toy_expectations(params: tuple[float, float, float]) -> dict[str, float]:
    state = np.array([0, 0, 1, 0], dtype=complex)
    state = np.kron(_ry(params[0]), _ry(params[1])) @ state
    state = CNOT @ state
    state = np.kron(I2, _rz(params[2])) @ state
    state = CNOT @ state
    paulis = {
        "XX": np.kron(X, X),
        "YY": np.kron(Y, Y),
        "ZI": np.kron(Z, I2),
        "IZ": np.kron(I2, Z),
    }
    return {
        name: float(np.real(state.conj() @ operator @ state))
        for name, operator in paulis.items()
    }


@pytest.mark.parametrize("term", range(4))
def test_every_vqe_measurement_compiles_for_base(term: int):
    qsharp.init(target_profile=qsharp.TargetProfile.Base)
    qsharp.eval(VQE_SOURCE.read_text(encoding="utf-8"))
    qir = qsharp.compile(
        "MeasureHubbardToyTerm("
        f"0.5, 1.0, 0.25, {term})"
    )

    assert "__quantum__qis__" in str(qir)


def test_qdk_measurement_runner_returns_the_known_product_state_energy():
    energy = vqe_optimizer.run_qsharp_energy(
        0.0,
        2.0,
        [math.pi, 0.0, 0.0],
        shots=256,
    )

    assert energy == pytest.approx(2.0, abs=1e-12)


def test_qdk_term_measurements_match_independent_state_vector_expectations():
    params = (0.5, 1.0, 0.3)
    expected = _exact_toy_expectations(params)
    observed = vqe_optimizer.run_qsharp_expectations(params, shots=4096)

    for term in vqe_optimizer.PAULI_TERMS:
        assert observed[term] == pytest.approx(expected[term], abs=0.06)


def test_optimizer_consumes_qsharp_objective_values(monkeypatch):
    calls = []

    def objective(t, u, params, shots):
        calls.append((t, u, tuple(params), shots))
        return -1.5 + sum((float(value) - 0.25) ** 2 for value in params)

    monkeypatch.setattr(vqe_optimizer, "run_qsharp_energy", objective)
    result = vqe_optimizer.optimize_vqe(
        1.0,
        2.0,
        max_iter=5,
        shots=32,
    )

    assert calls
    assert result["evaluations"] == len(calls)
    expected = -1.5 + sum((value - 0.25) ** 2 for value in result["optimal_params"])
    assert result["vqe_energy"] == pytest.approx(expected)
    assert all(call[3] == 32 for call in calls)
    assert result["hubbard_model_reference"].startswith("Not a VQE estimate")


def test_driver_has_no_dotnet_or_surrogate_path():
    source = VQE_PATH.read_text(encoding="utf-8")

    assert ".csproj" not in source
    assert "dotnet" not in source
    assert "surrogate_vqe_energy" not in source
