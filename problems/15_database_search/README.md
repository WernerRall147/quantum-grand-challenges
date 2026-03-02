# Problem 15 · Quantum Database Search

## Overview

Unstructured database search underpins many cryptographic attacks and combinatorial problems. Grover's algorithm delivers a quadratic speedup over classical exhaustive search by amplifying probability amplitudes for marked items. This problem now includes a canonical Grover workflow in Q# plus classical query-complexity baselines and analysis plots for cross-checking scaling behavior.

## Directory Layout

```text
15_database_search/
├── estimates/                       # JSON artifacts from classical / quantum workflows
├── instances/                       # Dataset sizes and marked item distributions (small/medium/large)
├── plots/                           # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py        # Exhaustive search complexity and success probability estimates
│   └── analyze.py                   # Visualization of query budgets and scaling behavior
└── qsharp/
    ├── QuantumSearch.csproj         # Q# project configuration
    ├── Program.qs                   # Canonical Grover implementation
    └── GroverEstimation.qs          # Resource-estimation variant
```

## Quick Start

```bash
cd problems/15_database_search

# Classical baseline (writes estimates/classical_baseline.json)
python python/classical_baseline.py

# Visualize query complexity vs. dataset size
python python/analyze.py

# Quantum workflow (requires .NET 6)
dotnet build qsharp/QuantumSearch.csproj
dotnet run --project qsharp/QuantumSearch.csproj
```

## Validation Highlights

- Canonical Grover implementation details and demonstrations are documented in `docs/GROVER_IMPLEMENTATION_SUMMARY.md`.
- Reported simulator success rates include:
    - 93% for 16-item single-target search,
    - 71% for 32-item multi-target search,
    - 100% for 4096-item benchmark case.
- Classical-vs-quantum query scaling artifacts are generated in `plots/` and `estimates/classical_baseline.json`.

## Objective Maturity Gate

- **Current gate**: **Stage C complete** (canonical Grover workflow implemented with simulator-backed validation and scaling analysis artifacts).
- **Next gate target**: **Stage D** (advantage evidence package hardening with backend-specific uncertainty methodology and deployment assumptions).

Stage C evidence references for this problem:

- Executable Grover workflow in `qsharp/Program.qs` and estimator variant in `qsharp/GroverEstimation.qs`.
- Simulator validation and empirical success-rate results in `docs/GROVER_IMPLEMENTATION_SUMMARY.md`.
- Classical comparison artifacts in `python/classical_baseline.py`, `estimates/classical_baseline.json`, and `plots/`.
- Circuit construction and control assumptions documented in the implementation summary and problem-local Q# sources.

## Advantage Claim Contract

- **Claim category (current)**: `projected`.
- **Problem class and regime**: Unstructured search with configurable dataset size and marked-item fractions.
- **Fair baseline**: Classical exhaustive-search query model in `python/classical_baseline.py`.
- **Quantum resource scaling claim**: Grover scaling O(sqrt(N)) versus classical O(N) with simulator-backed behavior; hardware-specific performance still pending.
- **Data-loading and I/O assumptions**: Oracle construction cost and data-oracle assumptions must be included with future claims.
- **Noise/error model assumptions**: Current evidence is simulator-centric; backend-calibrated noise models remain pending.
- **Confidence/uncertainty method**: Simulator trials reported in implementation summary; backend shot-based confidence intervals remain a Stage D hardening task.
- **Residual risks**: Oracle synthesis and transpilation overhead can erode practical speedup for near-term sizes.
