# Problem 07 · Quantum-Assisted Drug Discovery

## Overview

Drug discovery requires exploring vast chemical design spaces to identify ligands with strong binding affinity and favorable pharmacokinetics. Quantum computing promises more accurate electronic-structure evaluation and molecular similarity search. This problem sets the stage with a classical baseline that scores ligand–protein interaction energy using coarse-grained Lennard-Jones plus Coulomb terms, while preparing a Q# project to host variational quantum eigensolver (VQE) experiments for small active-site models.

## Directory Layout

```text
07_drug_discovery/
├── estimates/                  # JSON artifacts from classical/quantum workflows
├── instances/                  # Molecule parameter sets (small/medium/large)
├── plots/                      # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py   # Deterministic scoring of ligand poses
│   └── analyze.py              # Visualization of energy histograms & rankings
└── qsharp/
    ├── DrugDiscovery.csproj    # Q# project stub for VQE experiments
    └── Program.qs              # Placeholder quantum workflow
```

## Quick Start

```bash
cd problems/07_drug_discovery

# Classical scoring (writes estimates/classical_baseline.json)
python python/classical_baseline.py

# Visualize score distributions and top candidates
python python/analyze.py

# Quantum placeholder
 dotnet build qsharp/DrugDiscovery.csproj
 dotnet run --project qsharp/DrugDiscovery.csproj
```

## Next Quantum Milestones

1. **Fragment Encoding** – Map small active-site Hamiltonians (H₂, LiH, minimal basis) into qubit Hamiltonians.
2. **VQE Ansatz** – Implement adaptive VQE / UCCSD ansätze using Q# chemistry libraries.
3. **Pose Re-ranking** – Combine quantum energy estimates with classical docking scores.
4. **Resource Estimation** – Benchmark fault-tolerant requirements for chemically relevant precision.

This scaffold keeps the classical baseline reproducible while we iterate toward genuine quantum chemical modeling. 🧪⚛️
