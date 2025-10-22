# Problem 14 · Quantum Materials Discovery

## Overview

Designing next-generation battery cathodes requires exploring a vast space of material compositions and crystal structures. This scaffold provides a reproducible classical baseline that scores candidate compositions using simplified cluster expansions and builds a Q# project for future hybrid VQE and phase-estimation workflows that evaluate band gaps and defect energetics.

## Directory Layout

```text
14_materials_discovery/
├── estimates/                        # JSON artifacts from classical / quantum workflows
├── instances/                        # Candidate composition grids (small/medium/large)
├── plots/                            # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py         # Surrogate energy/stability scoring for battery materials
│   └── analyze.py                    # Visualization of Pareto fronts and composition trends
└── qsharp/
    ├── QuantumMaterials.csproj       # Q# project placeholder for VQE-style band gap estimation
    └── Program.qs                    # Stubbed quantum workflow
```

## Quick Start

```bash
cd problems/14_materials_discovery

# Classical surrogate baseline
env PYTHONPATH=../../.. python python/classical_baseline.py

# Visualize stability vs. voltage trends
python python/analyze.py

# Quantum placeholder (requires .NET 6)
dotnet build qsharp/QuantumMaterials.csproj
 dotnet run --project qsharp/QuantumMaterials.csproj
```

## Next Quantum Milestones

1. **Hamiltonian Construction** – Encode tight-binding or Hubbard-like operators for candidate lattices.
2. **Variational Ansätze** – Develop chemistry-informed ansätze for defect and conduction band evaluations.
3. **Cost Function Calibration** – Integrate quantum outputs with classical thermodynamic models.
4. **Resource Estimation** – Quantify qubit counts and logical depth for realistic band-gap predictions.

This scaffold keeps the classical materials-surrogate baseline reproducible while laying the groundwork for quantum-assisted materials discovery. 🔋⚛️
