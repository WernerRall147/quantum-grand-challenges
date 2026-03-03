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
