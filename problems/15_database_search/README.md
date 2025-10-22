# Problem 15 · Quantum Database Search

## Overview

Unstructured database search underpins many cryptographic attacks and combinatorial problems. Grover's algorithm delivers a quadratic speedup over classical exhaustive search by amplifying probability amplitudes for marked items. This scaffold provides a reproducible classical baseline that evaluates expected query complexity for varying dataset scales and marked item fractions, while preparing a Q# project where amplitude amplification routines will eventually live.

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
    ├── QuantumSearch.csproj         # Q# project placeholder for amplitude amplification routines
    └── Program.qs                   # Stubbed quantum workflow
```

## Quick Start

```bash
cd problems/15_database_search

# Classical baseline (writes estimates/classical_baseline.json)
python python/classical_baseline.py

# Visualize query complexity vs. dataset size
python python/analyze.py

# Quantum placeholder (requires .NET 6)
dotnet build qsharp/QuantumSearch.csproj
 dotnet run --project qsharp/QuantumSearch.csproj
```

## Next Quantum Milestones

1. **Oracle Construction** – Encode marked item oracles with phase kickback.
2. **Amplitude Amplification** – Implement Grover iterations with adaptive stopping.
3. **Error Analysis** – Quantify success probability under noise and imperfect oracles.
4. **Resource Estimation** – Map query depth and qubit counts to fault-tolerant costs.

This scaffold keeps the classical search baseline reproducible while paving the way for quantum-powered amplitude amplification. 🔍⚛️
