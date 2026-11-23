"""Hybrid VQE workflow for the two-site Hubbard toy calculation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

import numpy as np
from scipy.optimize import minimize

from qdk import qsharp


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VQE_KERNEL = PROJECT_ROOT / "qsharp" / "VqeHardwareKernel.qs"
DEFAULT_SHOTS = 1024
PAULI_TERMS = ("XX", "YY", "ZI", "IZ")


def exact_hubbard_energy(t: float, u: float) -> float:
    """Return the analytical half-filled two-site Hubbard ground energy."""
    discriminant = np.sqrt(u**2 + 16 * t**2)
    return 0.5 * (u - discriminant)


def exact_toy_ansatz_energy(t: float, u: float) -> float:
    """Return the exact ground energy of the measured two-qubit toy Hamiltonian.

    The current VQE circuit measures
    ``-t * (XX + YY) + u / 2 * (ZI + IZ)``. It is deliberately separate from
    the four-qubit Jordan-Wigner Hubbard Hamiltonian used by the QPE path.
    """
    return -max(abs(u), 2.0 * abs(t))


def _expectation_from_results(results: Sequence[Sequence[object]]) -> float:
    """Convert one-result Q# shots into a Pauli expectation value."""
    if not results:
        raise RuntimeError("Q# term measurement returned no shots")

    sample_sum = 0
    for shot in results:
        if len(shot) != 1:
            raise RuntimeError(f"expected one measured result per shot, got {shot!r}")
        text = str(shot[0])
        if text in {"Zero", "0"}:
            sample_sum += 1
        elif text in {"One", "1"}:
            sample_sum -= 1
        else:
            raise RuntimeError(f"unrecognised Q# measurement result {shot[0]!r}")
    return sample_sum / len(results)


def run_qsharp_expectations(
    params: Sequence[float],
    shots: int = DEFAULT_SHOTS,
) -> dict[str, float]:
    """Run one fixed QIR-compatible measurement circuit per Pauli term."""
    if len(params) != 3:
        raise ValueError("the Hubbard toy ansatz requires three parameters")
    if shots < 1:
        raise ValueError("shots must be positive")

    qsharp.init()
    qsharp.eval(VQE_KERNEL.read_text(encoding="utf-8"))
    expectations: dict[str, float] = {}
    for term_index, term_name in enumerate(PAULI_TERMS):
        expression = (
            "MeasureHubbardToyTerm("
            f"{float(params[0])!r}, {float(params[1])!r}, "
            f"{float(params[2])!r}, {term_index})"
        )
        results = qsharp.run(expression, shots=shots)
        expectations[term_name] = _expectation_from_results(results)
    return expectations


def energy_from_expectations(
    t: float,
    u: float,
    expectations: dict[str, float],
) -> float:
    """Combine measured Pauli expectations into the toy Hamiltonian energy."""
    missing = set(PAULI_TERMS) - expectations.keys()
    if missing:
        raise ValueError(f"missing Pauli expectations: {sorted(missing)}")
    return (
        -t * (expectations["XX"] + expectations["YY"])
        + 0.5 * u * (expectations["ZI"] + expectations["IZ"])
    )


def run_qsharp_energy(
    t: float,
    u: float,
    params: Sequence[float],
    shots: int = DEFAULT_SHOTS,
) -> float:
    """Measure the toy VQE Hamiltonian through the QDK Python API."""
    return energy_from_expectations(
        t,
        u,
        run_qsharp_expectations(params, shots=shots),
    )


def optimize_vqe(
    t: float,
    u: float,
    method: str = "COBYLA",
    max_iter: int = 100,
    shots: int = DEFAULT_SHOTS,
) -> dict:
    """Optimize the toy VQE circuit using measured Q# objective values."""
    if shots < 1:
        raise ValueError("shots must be positive")
    if max_iter < 1:
        raise ValueError("max_iter must be positive")

    initial_params = np.array([0.5, 1.0, 0.3])
    evaluations = 0

    def energy_func(params: np.ndarray) -> float:
        nonlocal evaluations
        evaluations += 1
        energy = run_qsharp_energy(t, u, params, shots=shots)
        if not np.isfinite(energy):
            raise RuntimeError(f"Q# returned a non-finite energy: {energy}")
        return float(energy)

    result = minimize(
        energy_func,
        initial_params,
        method=method,
        options={"maxiter": max_iter},
    )
    optimal_params = result.x.tolist()
    measured = run_qsharp_energy(t, u, optimal_params, shots=shots)
    exact_toy = exact_toy_ansatz_energy(t, u)
    exact_hubbard = exact_hubbard_energy(t, u)

    return {
        "optimal_params": optimal_params,
        "vqe_energy": float(measured),
        "exact_toy_energy": float(exact_toy),
        "vqe_error": float(abs(measured - exact_toy)),
        "exact_hubbard_energy": float(exact_hubbard),
        "hubbard_model_reference": "Not a VQE estimate of the four-qubit Hubbard model",
        "iterations": int(result.get("nit", result.get("nfev", 0))),
        "evaluations": evaluations + 1,
        "shots_per_term": shots,
        "method": method,
        "success": bool(result.success),
    }


def run_vqe_benchmark() -> list[dict]:
    """Run VQE optimization across the documented toy parameter sets."""
    t_values = [0.5, 1.0]
    u_values = [0.0, 2.0, 4.0, 8.0]
    results = []

    print("VQE Optimization Benchmark for the Two-Qubit Toy Hamiltonian")
    print("=" * 70)

    for t in t_values:
        for u in u_values:
            print(f"\nOptimizing t={t}, U={u}")
            result = optimize_vqe(t, u)

            print(f"  Toy VQE energy:     {result['vqe_energy']:.6f}")
            print(f"  Exact toy energy:   {result['exact_toy_energy']:.6f}")
            print(f"  Toy VQE error:      {result['vqe_error']:.6f}")
            print(f"  Hubbard reference:  {result['exact_hubbard_energy']:.6f}")
            print(f"  Evaluations:        {result['evaluations']}")
            print(
                "  theta="
                f"{np.asarray(result['optimal_params']).round(4).tolist()}"
            )
            results.append({"t": t, "u": u, **result})

    output = PROJECT_ROOT / "estimates" / "vqe_optimization.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    print("\n" + "=" * 70)
    print(f"Results saved to {output}")
    return results


if __name__ == "__main__":
    benchmark_results = run_vqe_benchmark()

    print("\nSummary Statistics:")
    errors = [row["vqe_error"] for row in benchmark_results]
    print(f"  Mean toy VQE error: {np.mean(errors):.6f}")
