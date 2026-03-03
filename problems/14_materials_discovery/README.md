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

## Objective Maturity Gate

- **Current gate**: **Stage B complete** (classical baseline and Q# scaffold/build path are in place).
- **Next gate target**: **Stage C** (hardware-aware validation with uncertainty-bounded comparisons).

Stage C exit criteria for this problem:

- Execute at least one non-placeholder quantum workflow path tied to the problem objective.
- Report uncertainty-bounded comparisons between classical and quantum outputs on `small` and `medium` instances.
- Document transpilation/connectivity and backend assumptions used for reported quantum runs.
- Add calibration/noise-sensitivity evidence for the reported quantum metrics.

## DiVincenzo Readiness (Stage C/D Overlay)

| Criterion | Status | Evidence / Notes |
|---|---|---|
| Scalable qubit system | partial | Problem-scoped instance baselines are in place; full hardware-scale projections are tracked as Stage C work. |
| Initialization | partial | Input/state initialization path is defined for current workflows, with backend-ready loading fidelity still to be hardened. |
| Coherence vs gate time | not-yet | Backend-calibrated coherence-vs-depth evidence is pending and required for Stage C/D promotion. |
| Universal gate set | partial | Q# scaffold/build path exists; gate-basis decomposition and transpilation evidence remain Stage C tasks. |
| Qubit-specific measurement | partial | Measurement outputs are defined for current validation flows; hardware readout characterization is pending. |
## Advantage Claim Contract

- **Claim category (current)**: `theoretical`.
- **Problem class and regime**: Problem-specific challenge instances defined in this directory.
- **Fair baseline**: Problem-local classical baseline in `python/` outputs.
- **Quantum resource scaling claim**: Expected asymptotic advantage depends on algorithm family and implementation assumptions; no hardware-demonstrated speedup claim yet.
- **Data-loading and I/O assumptions**: Must be documented alongside future advantage claims.
- **Noise/error model assumptions**: Backend-specific model and calibration assumptions to be added at Stage C.
- **Confidence/uncertainty method**: To be reported using shot-based confidence intervals or equivalent statistical bounds.
- **Residual risks**: Oracle/state-preparation/transpilation overhead may dominate for near-term instance sizes.
