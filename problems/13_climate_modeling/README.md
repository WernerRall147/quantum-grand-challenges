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
