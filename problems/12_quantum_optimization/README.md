# Problem 12 · Quantum-Assisted Combinatorial Optimization

## Overview

Scheduling, routing, and resource allocation problems are notoriously difficult to solve optimally. Quantum algorithms such as the Quantum Approximate Optimization Algorithm (QAOA) promise improvements by exploring large solution spaces with quantum interference. This scaffold supplies a reproducible classical baseline using greedy weighted tardiness minimization for multi-machine scheduling and prepares a Q# project where future QAOA and amplitude-encoded heuristics can be explored.

## Directory Layout

```text
12_quantum_optimization/
├── estimates/                      # JSON artifacts from classical / quantum workflows
├── instances/                      # Scheduling instances (small/medium/large)
├── plots/                          # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py       # Greedy weighted tardiness scheduler
│   └── analyze.py                  # Visualization of tardiness, utilization, and makespan
└── qsharp/
    ├── QuantumOptimization.csproj  # Q# project stub for QAOA-style routines
    └── Program.qs                  # Placeholder quantum workflow
```

## Quick Start

```bash
cd problems/12_quantum_optimization

# Classical baseline (writes estimates/classical_baseline.json)
python python/classical_baseline.py

# Visualize tardiness and utilization profiles
python python/analyze.py

# Quantum placeholder
 dotnet build qsharp/QuantumOptimization.csproj
 dotnet run --project qsharp/QuantumOptimization.csproj
```

## Next Quantum Milestones

1. **Cost Hamiltonian Encoding** – Map weighted tardiness and machine constraints into qubit operators.
2. **Mixer Design** – Implement QAOA mixers that respect machine allocation constraints.
3. **Hybrid Optimization Loop** – Couple Q# circuits with classical optimizers for parameter tuning.
4. **Resource Estimation** – Benchmark qubit counts and circuit depth for realistic scheduling workloads.

This scaffold keeps the classical scheduling baseline reproducible while we iterate toward quantum-enabled combinatorial optimization strategies. 🧮⚛️

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
