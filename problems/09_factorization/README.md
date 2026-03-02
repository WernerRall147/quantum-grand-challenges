# Problem 09 · Quantum-Accelerated Integer Factorization

## Overview

Breaking large RSA-style moduli showcases a flagship quantum advantage through Shor's algorithm. While practical quantum hardware remains distant, we can benchmark classical factoring effort and prepare a Q# scaffold for modular exponentiation, quantum Fourier transforms, and order finding experiments. This problem introduces a Pollard Rho classical baseline to estimate computational effort per instance and enables future integration with full period-finding implementations.

## Directory Layout

```text
09_factorization/
├── estimates/                  # JSON artifacts from classical / quantum workflows
├── instances/                  # Semi-prime inputs across difficulty scales
├── plots/                      # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py   # Pollard Rho factoring statistics per modulus
│   └── analyze.py              # Visualization of iterations / speed trends
└── qsharp/
    ├── Factorization.csproj    # Q# project stub for Shor-style order finding
    └── Program.qs              # Placeholder quantum workflow
```

## Quick Start

```bash
cd problems/09_factorization

# Classical factoring baseline (writes estimates/classical_baseline.json)
python python/classical_baseline.py

# Visualize iteration counts and effort
python python/analyze.py

# Quantum placeholder
 dotnet build qsharp/Factorization.csproj
 dotnet run --project qsharp/Factorization.csproj
```

## Next Quantum Milestones

1. **Modular Exponentiation Kernel** – Implement square-and-multiply circuits with controlled modular multipliers.
2. **Quantum Fourier Transform** – Integrate QFT-based phase estimation for order finding.
3. **Semi-Prime Order Finding** – Simulate Shor's algorithm for 15, 21, and 35; extend to 3–4 qubit work registers.
4. **Resource Estimation** – Analyze logical qubit counts and T-depth for RSA-1024 style moduli via Azure Quantum tools.

This scaffold keeps the classical baseline reproducible while we iterate toward full-scale quantum period finding demonstrations. 🔐⚛️

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
