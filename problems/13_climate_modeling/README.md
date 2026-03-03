# Problem 13 · Quantum-Accelerated Climate Modeling

## Overview

Accurate climate projections require solving large sparse linear systems arising from discretized partial differential equations. This scaffold introduces a reproducible classical baseline based on an energy balance diffusion model while preparing a Q# project that will eventually host hybrid HHL-style solvers. The goal is to compare classical finite-difference climate propagation with future quantum linear solver accelerators.

## Directory Layout

```text
13_climate_modeling/
├── estimates/                        # JSON artifacts from classical / quantum workflows
├── instances/                        # Discretization grids and forcing scenarios (small/medium/large)
├── plots/                            # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py         # 1D energy balance diffusion solver
│   └── analyze.py                    # Visualization of temperature evolution and convergence
└── qsharp/
    ├── QuantumClimate.csproj         # Q# project placeholder for HHL-inspired routines
    └── Program.qs                    # Stubbed quantum workflow
```

## Quick Start

```bash
cd problems/13_climate_modeling

# Classical finite-difference baseline
python python/classical_baseline.py

# Plot temperature profiles and convergence diagnostics
python python/analyze.py

# Quantum placeholder (requires .NET 6)
dotnet build qsharp/QuantumClimate.csproj
 dotnet run --project qsharp/QuantumClimate.csproj
```

## Next Quantum Milestones

1. **Linear System Encoding** – Translate diffusion operators into sparse Hermitian matrices suitable for HHL.
2. **State Preparation** – Implement physically motivated right-hand-side encodings for radiative forcing profiles.
3. **Error Budgeting** – Quantify precision requirements and map to logical qubit counts.
4. **Hybrid Calibration** – Integrate quantum solvers with classical refinement loops for multi-scale climate modeling.

This scaffold keeps the classical diffusion baseline reproducible while we iterate toward quantum-enhanced climate projections. 🌍⚛️

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
