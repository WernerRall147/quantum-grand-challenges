# Problem 08 · Quantum-Assisted Protein Folding

## Overview

Protein folding encodes how linear amino-acid chains spontaneously organize into three-dimensional structures that dictate biological function. Quantum resources promise tighter coupling between electronic interactions and conformational search compared to classical heuristics. This scaffold provides a deterministic classical baseline using knowledge-based contact potentials while preparing a Q# project for future amplitude-encoded folding experiments and quantum Boltzmann sampling.

## Directory Layout

```text
08_protein_folding/
├── estimates/                  # JSON artifacts from classical/quantum workflows
├── instances/                  # Protein sequences with coarse contact maps
├── plots/                      # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py   # Knowledge-based scoring of contact maps
│   └── analyze.py              # Visual analytics for folding metrics
└── qsharp/
    ├── ProteinFolding.csproj   # Q# project stub for quantum folding routines
    └── Program.qs              # Placeholder quantum workflow
```

## Quick Start

```bash
cd problems/08_protein_folding

# Classical evaluation (writes estimates/classical_baseline.json)
python python/classical_baseline.py

# Visualize folding metrics
python python/analyze.py

# Quantum placeholder
 dotnet build qsharp/ProteinFolding.csproj
 dotnet run --project qsharp/ProteinFolding.csproj
```

## Next Quantum Milestones

1. **Amplitude Encoding** – Load coarse-grained contact weights into amplitude registers for downstream energy estimation.
2. **Quantum Boltzmann Sampling** – Prototype a quantum-enhanced sampler over lattice conformations or fragment libraries.
3. **Hybrid Refinement** – Combine quantum-evaluated energies with classical gradient-based relaxations.
4. **Resource Estimation** – Benchmark logical qubits and T-depth for realistic fold sizes using the Azure Quantum Resource Estimator.

This scaffold keeps the classical baseline reproducible while we iterate toward chemistry-informed quantum folding simulations. 🧬⚛️
