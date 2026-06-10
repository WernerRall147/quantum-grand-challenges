"""Parse and index the Quantum Algorithm Zoo (quantumalgorithmzoo.org).

Maps all known quantum algorithms with their speedup classes, gate requirements,
and I/O characteristics for the Classifier and Fact-Checker agents.
"""

import json
import os
from datetime import datetime, timezone
from typing import List, Dict


# Curated algorithm database based on Quantum Algorithm Zoo + Troyer analysis
# This is the authoritative reference for the Classifier Agent
ALGORITHM_DATABASE = [
    # === EXPONENTIAL / SUPERPOLYNOMIAL SPEEDUP (genuine utility candidates) ===
    {
        "name": "Shor's Algorithm",
        "category": "Number Theory",
        "speedup_class": "superpolynomial",
        "quantum_complexity": "O(n³)",
        "classical_best": "General Number Field Sieve (sub-exponential)",
        "io_bottleneck": False,
        "oracle_polynomial": True,
        "naturally_quantum": False,
        "troyer_verdict": "QUANTUM_ADVANTAGE",
        "notes": "The canonical example. Breaks RSA. Needs ~4000 logical qubits for RSA-2048.",
        "reference": "arXiv:quant-ph/9508027",
    },
    {
        "name": "Quantum Phase Estimation (QPE)",
        "category": "Eigenvalue Problems",
        "speedup_class": "exponential",
        "quantum_complexity": "O(poly(n)/ε)",
        "classical_best": "Full Configuration Interaction O(exp(n))",
        "io_bottleneck": False,
        "oracle_polynomial": True,
        "naturally_quantum": True,
        "troyer_verdict": "QUANTUM_ADVANTAGE",
        "notes": "Exponential speedup for naturally quantum Hamiltonians. Core of quantum chemistry advantage.",
        "reference": "arXiv:quant-ph/9511026",
    },
    {
        "name": "Hamiltonian Simulation (Product Formulas)",
        "category": "Quantum Simulation",
        "speedup_class": "exponential",
        "quantum_complexity": "O(poly(n, t, 1/ε))",
        "classical_best": "Exact diagonalization O(exp(n))",
        "io_bottleneck": False,
        "oracle_polynomial": True,
        "naturally_quantum": True,
        "troyer_verdict": "QUANTUM_ADVANTAGE",
        "notes": "Exponential speedup for simulating quantum systems. Feynman's original motivation.",
        "reference": "arXiv:quant-ph/0301023",
    },
    {
        "name": "Quantum Walk (Transport)",
        "category": "Graph Problems / Simulation",
        "speedup_class": "exponential",
        "quantum_complexity": "O(poly(n))",
        "classical_best": "Lindblad master equation (classical simulation of open quantum systems)",
        "io_bottleneck": False,
        "oracle_polynomial": True,
        "naturally_quantum": True,
        "troyer_verdict": "QUANTUM_ADVANTAGE",
        "notes": "Exponential speedup for naturally quantum transport. Avoids I/O problem.",
        "reference": "arXiv:quant-ph/0012090",
    },
    {
        "name": "Lattice Gauge Theory (Real-Time)",
        "category": "Quantum Field Theory",
        "speedup_class": "exponential",
        "quantum_complexity": "O(poly(V, t, 1/ε))",
        "classical_best": "Lattice QCD (Euclidean only, sign problem for real-time)",
        "io_bottleneck": False,
        "oracle_polynomial": True,
        "naturally_quantum": True,
        "troyer_verdict": "QUANTUM_ADVANTAGE",
        "notes": "Classical lattice QCD cannot do real-time dynamics (sign problem). Strongest long-term utility case.",
        "reference": "arXiv:1404.7115",
    },

    # === QUADRATIC SPEEDUP (limited by I/O, oracle cost, or QEC overhead) ===
    {
        "name": "Grover's Search",
        "category": "Search / Optimization",
        "speedup_class": "quadratic",
        "quantum_complexity": "O(√N)",
        "classical_best": "Linear scan O(N)",
        "io_bottleneck": True,
        "oracle_polynomial": False,  # Oracle cost often dominates
        "naturally_quantum": False,
        "troyer_verdict": "HPC_PREFERRED",
        "notes": "Provably optimal quadratic speedup but QRAM loading O(N) erases it. Oracle cost for real problems (AES, database) dominates.",
        "reference": "arXiv:quant-ph/9605043",
    },
    {
        "name": "Quantum Amplitude Estimation (QAE)",
        "category": "Monte Carlo / Finance",
        "speedup_class": "quadratic",
        "quantum_complexity": "O(1/ε)",
        "classical_best": "Monte Carlo O(1/ε²)",
        "io_bottleneck": True,
        "oracle_polynomial": True,
        "naturally_quantum": False,
        "troyer_verdict": "HPC_PREFERRED",
        "notes": "Quadratic speedup proven. But QEC overhead requires ε < 10⁻⁴ for net advantage. Distribution loading is O(N).",
        "reference": "arXiv:quant-ph/0005055",
    },
    {
        "name": "HHL Algorithm",
        "category": "Linear Algebra",
        "speedup_class": "exponential_core",
        "quantum_complexity": "O(polylog(N) · κ² / ε)",
        "classical_best": "Conjugate gradient O(N · κ)",
        "io_bottleneck": True,
        "oracle_polynomial": False,  # State prep is O(N)
        "naturally_quantum": False,
        "troyer_verdict": "HPC_PREFERRED",
        "notes": "Exponential core speedup but O(N) state prep and O(N) readout on both ends. Only useful if you need the quantum state, not the classical solution vector.",
        "reference": "arXiv:0811.3171",
    },

    # === HEURISTIC / NO PROVEN ADVANTAGE ===
    {
        "name": "Variational Quantum Eigensolver (VQE)",
        "category": "Chemistry / Optimization",
        "speedup_class": "none_proven",
        "quantum_complexity": "Heuristic (varies with ansatz)",
        "classical_best": "DMRG / tensor networks / coupled cluster",
        "io_bottleneck": False,
        "oracle_polynomial": True,
        "naturally_quantum": True,
        "troyer_verdict": "HPC_PREFERRED",
        "notes": "No proven speedup. Barren plateaus at scale. Classical tensor networks often competitive. Use QPE instead for fault-tolerant era.",
        "reference": "arXiv:1304.3061",
    },
    {
        "name": "QAOA (Quantum Approximate Optimization)",
        "category": "Combinatorial Optimization",
        "speedup_class": "quadratic_at_most",
        "quantum_complexity": "At most quadratic",
        "classical_best": "Goemans-Williamson SDP, branch-and-bound",
        "io_bottleneck": False,
        "oracle_polynomial": True,
        "naturally_quantum": False,
        "troyer_verdict": "HPC_PREFERRED",
        "notes": "No proven advantage beyond quadratic. Constant-depth QAOA is classically simulable. GW achieves 0.878-approx for MaxCut in poly time.",
        "reference": "arXiv:1411.4028",
    },
    {
        "name": "Quantum Machine Learning (Kernel Methods)",
        "category": "Machine Learning",
        "speedup_class": "exponential_core",
        "quantum_complexity": "O(log N) for kernel evaluation",
        "classical_best": "Classical kernel methods / random features",
        "io_bottleneck": True,
        "oracle_polynomial": False,  # Data loading is O(N)
        "naturally_quantum": False,
        "troyer_verdict": "HPC_PREFERRED",
        "notes": "Exponential kernel speedup exists but O(N) data loading negates it. Proven advantages only for specific contrived problems.",
        "reference": "arXiv:1307.0401",
    },

    # === ENABLING INFRASTRUCTURE ===
    {
        "name": "Quantum Error Correction (Surface Code)",
        "category": "Infrastructure",
        "speedup_class": "not_applicable",
        "quantum_complexity": "O(d²) physical qubits per logical qubit",
        "classical_best": "N/A  enables other algorithms",
        "io_bottleneck": False,
        "oracle_polynomial": True,
        "naturally_quantum": True,
        "troyer_verdict": "INFRASTRUCTURE",
        "notes": "Not an algorithm  enabling technology. Threshold theorem guarantees fault-tolerant computation if physical error rate < threshold.",
        "reference": "arXiv:quant-ph/9705052",
    },
]


def build_algorithm_index():
    """Build the algorithm zoo index for the knowledge base."""
    output = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Curated from quantumalgorithmzoo.org + Troyer framework analysis",
        "total_algorithms": len(ALGORITHM_DATABASE),
        "algorithms": ALGORITHM_DATABASE,
        "speedup_summary": {
            "exponential": len([a for a in ALGORITHM_DATABASE if a["speedup_class"] in ("exponential", "superpolynomial")]),
            "quadratic": len([a for a in ALGORITHM_DATABASE if "quadratic" in a["speedup_class"]]),
            "heuristic": len([a for a in ALGORITHM_DATABASE if a["speedup_class"] in ("none_proven", "exponential_core")]),
            "infrastructure": len([a for a in ALGORITHM_DATABASE if a["speedup_class"] == "not_applicable"]),
        },
    }
    return output


def main():
    index = build_algorithm_index()
    output_path = "knowledge/data/algorithm_zoo_index.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    print(f"Algorithm Zoo index: {index['total_algorithms']} algorithms")
    print(f"  Exponential/superpolynomial: {index['speedup_summary']['exponential']}")
    print(f"  Quadratic: {index['speedup_summary']['quadratic']}")
    print(f"  Heuristic/no proven: {index['speedup_summary']['heuristic']}")
    print(f"  Infrastructure: {index['speedup_summary']['infrastructure']}")


if __name__ == "__main__":
    main()
