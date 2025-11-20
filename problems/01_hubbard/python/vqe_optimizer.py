"""Hybrid VQE workflow for the two-site Hubbard model."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import List

import numpy as np
from scipy.optimize import minimize


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QSHARP_PROJECT = PROJECT_ROOT / "qsharp" / "Hubbard.csproj"
DEFAULT_SHOTS = 1024


def exact_hubbard_energy(t: float, u: float) -> float:
    """Calculate exact ground state energy for 2-site Hubbard model.
    
    Args:
        t: Hopping parameter
        u: On-site interaction parameter
        
    Returns:
        Exact ground state energy (singlet)
    """
    discriminant = np.sqrt(u**2 + 16 * t**2)
    return 0.5 * (u - discriminant)


def surrogate_vqe_energy(params: List[float], t: float, u: float) -> float:
    """Simulate VQE energy measurement for given ansatz parameters.
    
    In a real implementation, this would:
    1. Call Q# program with parameters
    2. Measure Hamiltonian expectation values
    3. Return estimated energy
    
    For now, we use a classical surrogate model for optimization.
    
    Args:
        params: [theta0, theta1, theta2] ansatz rotation angles
        t: Hopping parameter
        u: On-site interaction parameter
        
    Returns:
        Estimated energy (surrogate model)
    """
    # Surrogate model: mix of exact energy + parameter-dependent noise
    exact = exact_hubbard_energy(t, u)
    
    # Add realistic parameter dependence:
    # Best energy near optimal parameters (theta0 ~ pi/4, theta1 ~ pi/2, theta2 ~ pi/8)
    theta0_penalty = 0.1 * (params[0] - np.pi/4)**2
    theta1_penalty = 0.1 * (params[1] - np.pi/2)**2
    theta2_penalty = 0.05 * (params[2] - np.pi/8)**2
    
    return exact + theta0_penalty + theta1_penalty + theta2_penalty


def run_qsharp_energy(t: float, u: float, params: List[float], shots: int = DEFAULT_SHOTS) -> float:
    """Call the Q# CLI to estimate the Hubbard energy for a parameter set."""

    command = [
        "dotnet",
        "run",
        "--no-build",
        "--project",
        str(QSHARP_PROJECT),
        "--",
        "energy",
        f"{t:.15g}",
        f"{u:.15g}",
        f"{params[0]:.15g}",
        f"{params[1]:.15g}",
        f"{params[2]:.15g}",
        str(int(shots)),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=QSHARP_PROJECT.parent,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Q# energy estimation failed:\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr.strip()}"
        )

    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("Q# energy estimator returned no output.")

    return float(lines[-1])


def optimize_vqe(t: float, u: float, method: str = 'COBYLA', max_iter: int = 100, shots: int = DEFAULT_SHOTS) -> dict:
    """Run VQE optimization to find ground state energy.
    
    Args:
        t: Hopping parameter
        u: On-site interaction parameter
        method: Optimization method ('COBYLA', 'SLSQP', 'Powell')
        max_iter: Maximum iterations
        
    Returns:
        Dict with results: optimal_params, vqe_energy, exact_energy, error, iterations
    """
    # Initial guess
    initial_params = np.array([0.5, 1.0, 0.3])
    
    # Energy function to minimize
    def energy_func(params):
        return surrogate_vqe_energy(params, t, u)
    
    # Run optimization
    result = minimize(
        energy_func,
        initial_params,
        method=method,
        options={'maxiter': max_iter}
    )
    
    # Calculate exact energy for comparison
    exact = exact_hubbard_energy(t, u)
    vqe = result.fun
    
    optimal_params = result.x.tolist()
    quantum_energy = run_qsharp_energy(t, u, optimal_params, shots=shots)

    return {
        'optimal_params': optimal_params,
        'vqe_energy': float(vqe),
        'exact_energy': float(exact),
        'error': float(abs(vqe - exact)),
        'quantum_energy': float(quantum_energy),
        'quantum_error': float(abs(quantum_energy - exact)),
        'iterations': int(result.get('nit', result.get('nfev', 0))),
        'shots': shots,
        'success': bool(result.success)
    }


def run_vqe_benchmark():
    """Run VQE optimization across multiple Hubbard parameter sets."""
    t_values = [0.5, 1.0]
    u_values = [0.0, 2.0, 4.0, 8.0]
    
    results = []
    
    print("VQE Optimization Benchmark for Two-Site Hubbard Model")
    print("=" * 70)
    
    for t in t_values:
        for u in u_values:
            print(f"\nOptimizing t={t}, U={u}")
            result = optimize_vqe(t, u)
            
            print(f"  Surrogate Energy: {result['vqe_energy']:.6f}")
            print(f"  Exact Energy:     {result['exact_energy']:.6f}")
            print(f"  Surrogate Error:  {result['error']:.6f}")
            print(f"  Q# Energy:        {result['quantum_energy']:.6f} (shots={result['shots']})")
            print(f"  Q# Error:         {result['quantum_error']:.6f}")
            print(f"  Iterations:   {result['iterations']}")
            print(f"  θ₀={result['optimal_params'][0]:.4f}, "
                  f"θ₁={result['optimal_params'][1]:.4f}, "
                  f"θ₂={result['optimal_params'][2]:.4f}")
            
            results.append({
                't': t,
                'u': u,
                **result
            })
    
    # Save results
    with open('../estimates/vqe_optimization.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("Results saved to ../estimates/vqe_optimization.json")
    
    return results


if __name__ == '__main__':
    results = run_vqe_benchmark()
    
    print("\nSummary Statistics:")
    errors = [r['error'] for r in results]
    quantum_errors = [r['quantum_error'] for r in results]
    print(f"  Mean surrogate error: {np.mean(errors):.6f}")
    print(f"  Mean Q# error:        {np.mean(quantum_errors):.6f}")
