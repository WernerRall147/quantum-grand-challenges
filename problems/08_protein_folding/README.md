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
