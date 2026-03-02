# Problem 10 · Post-Quantum Cryptography Security Analysis

## Overview

Post-quantum cryptography (PQC) must withstand both classical and quantum attacks. Modern lattice schemes trade performance against resistance to advanced BKZ reduction and Grover-amplified sieving. This problem installs a classical baseline that estimates the cost of state-of-the-art attacks against NIST-style parameter sets while providing a Q# scaffold for experimenting with amplitude-amplified sieving primitives and hybrid search routines.

## Directory Layout

```text
10_post_quantum_cryptography/
├── estimates/                      # JSON artifacts from classical / quantum workflows
├── instances/                      # Representative NIST parameter sets
├── plots/                          # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py       # Cost estimation for classical / quantum lattice attacks
│   └── analyze.py                  # Visualization of security margins
└── qsharp/
    ├── PostQuantum.csproj          # Q# project stub for amplitude-amplified sieving experiments
    └── Program.qs                  # Placeholder quantum workflow
```

## Quick Start

```bash
cd problems/10_post_quantum_cryptography

# Classical security estimation (writes estimates/classical_baseline.json)
python python/classical_baseline.py

# Visualize cost curves and security margins
python python/analyze.py

# Quantum placeholder
 dotnet build qsharp/PostQuantum.csproj
 dotnet run --project qsharp/PostQuantum.csproj
```

## Next Quantum Milestones

1. **Amplitude Amplification Kernel** – Prototype Grover-style boosts for nearest vector search cost models.
2. **Hybrid BKZ Simulation** – Integrate amplitude amplification with classical pruning heuristics in Q#.
3. **Adaptive Parameter Study** – Sweep lattice dimensions / modulus sizes to locate safe PQC parameters.
4. **Resource Estimation** – Quantify logical qubits and T-count for practical quantum sieving on targeted dimensions.

This scaffold keeps classical estimators reproducible while we prototype quantum-enhanced attack analyses. 🔐⚛️

## Objective Maturity Gate

- **Current gate**: **Stage B complete** (classical baseline and Q# scaffold/build path are in place).
- **Next gate target**: **Stage C** (hardware-aware validation with uncertainty-bounded comparisons).

Stage C exit criteria for this problem:

- Execute at least one non-placeholder quantum workflow path tied to the problem objective.
- Report uncertainty-bounded comparisons between classical and quantum outputs on `small` and `medium` instances.
- Document transpilation/connectivity and backend assumptions used for reported quantum runs.
- Add calibration/noise-sensitivity evidence for the reported quantum metrics.

## Advantage Claim Contract

- **Claim category (current)**: `theoretical`.
- **Problem class and regime**: Problem-specific challenge instances defined in this directory.
- **Fair baseline**: Problem-local classical baseline in `python/` outputs.
- **Quantum resource scaling claim**: Expected asymptotic advantage depends on algorithm family and implementation assumptions; no hardware-demonstrated speedup claim yet.
- **Data-loading and I/O assumptions**: Must be documented alongside future advantage claims.
- **Noise/error model assumptions**: Backend-specific model and calibration assumptions to be added at Stage C.
- **Confidence/uncertainty method**: To be reported using shot-based confidence intervals or equivalent statistical bounds.
- **Residual risks**: Oracle/state-preparation/transpilation overhead may dominate for near-term instance sizes.
