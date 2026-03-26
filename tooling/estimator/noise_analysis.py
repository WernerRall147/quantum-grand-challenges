#!/usr/bin/env python3
"""Noise impact analysis for Grover search.

Simulates the effect of depolarizing noise on Grover success rates.
Shows how zero-variance noiseless results degrade under realistic error rates.
"""

import json
import math
import numpy as np
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parents[2]


def simulate_grover_with_noise(n_qubits: int, target: int, iterations: int, 
                                error_rate: float, shots: int = 1000) -> float:
    """Simulate Grover search success rate with depolarizing noise.
    
    Uses a simplified noise model: after each 2-qubit gate, each qubit
    has probability `error_rate` of experiencing a random Pauli error.
    
    This is a classical Monte Carlo simulation of the noisy quantum circuit,
    not a full density matrix simulation. It provides an upper bound on
    how noise degrades the algorithm.
    """
    N = 2 ** n_qubits
    
    # In the noiseless case, Grover success probability is sin²((2k+1)θ)
    # where θ = arcsin(1/√N) and k = iterations
    theta = math.asin(1.0 / math.sqrt(N))
    noiseless_prob = math.sin((2 * iterations + 1) * theta) ** 2
    
    # Model noise impact: each 2-qubit gate introduces error
    # For n-qubit Grover with multi-controlled gates decomposed into
    # O(n) two-qubit gates per oracle+diffusion, and k iterations:
    # Total 2q gates ≈ 4 * n * k (rough estimate)
    gates_per_iteration = 4 * n_qubits  # approximate 2q gates per iteration
    total_2q_gates = gates_per_iteration * iterations
    
    # Probability that no error occurs on any gate
    # Each 2q gate has probability (1-error_rate)² that both qubits survive
    survival_per_gate = (1 - error_rate) ** 2
    circuit_survival = survival_per_gate ** total_2q_gates
    
    # Noisy success: if circuit survives, get noiseless result
    # If any error occurs, result is approximately random (1/N)
    noisy_success = circuit_survival * noiseless_prob + (1 - circuit_survival) * (1.0 / N)
    
    # Add shot noise
    rng = np.random.RandomState(42)
    successes = rng.binomial(shots, noisy_success)
    measured_rate = successes / shots
    
    return measured_rate, noiseless_prob, circuit_survival


def main():
    error_rates = [0.0, 0.0001, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1]
    qubit_sizes = [3, 4, 5, 6, 8]
    shots = 10000
    
    results = []
    
    print(f"{'n':>3} {'N':>6} {'iters':>5} {'error_rate':>10} {'noiseless':>10} {'noisy':>10} {'survival':>10}")
    print("-" * 65)
    
    for n in qubit_sizes:
        N = 2 ** n
        theta = math.asin(1.0 / math.sqrt(N))
        iters = max(1, int(math.pi / (4 * theta) - 0.5))
        target = N // 3
        
        for err in error_rates:
            noisy_rate, noiseless, survival = simulate_grover_with_noise(
                n, target, iters, err, shots
            )
            
            row = {
                "qubits": n,
                "keyspace": N,
                "iterations": iters,
                "error_rate": err,
                "noiseless_success": round(noiseless, 4),
                "noisy_success": round(noisy_rate, 4),
                "circuit_survival": round(survival, 4),
            }
            results.append(row)
            
            if err in [0.0, 0.001, 0.01, 0.05]:
                print(f"{n:>3} {N:>6} {iters:>5} {err:>10.4f} {noiseless:>10.4f} {noisy_rate:>10.4f} {survival:>10.4f}")
    
    # Key finding
    print("\n=== Key Finding ===")
    print("At error_rate=0.01 (typical current hardware):")
    for n in qubit_sizes:
        N = 2 ** n
        theta = math.asin(1.0 / math.sqrt(N))
        iters = max(1, int(math.pi / (4 * theta) - 0.5))
        noisy, noiseless, survival = simulate_grover_with_noise(n, N//3, iters, 0.01, shots)
        print(f"  n={n}: noiseless={noiseless:.3f}, noisy={noisy:.3f}, circuit_survival={survival:.3f}")
    
    # Save
    output = {
        "analysis": "grover_noise_impact",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "note": "Depolarizing noise model. Shows zero-variance noiseless results are meaningless for hardware viability.",
        "results": results,
    }
    
    out_path = REPO / "problems" / "10_post_quantum_cryptography" / "estimates" / "noise_impact_analysis.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\nSaved: {out_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
