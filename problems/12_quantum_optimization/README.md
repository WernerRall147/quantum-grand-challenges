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
