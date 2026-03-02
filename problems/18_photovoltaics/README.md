# Problem 18 · Quantum Photovoltaics

## Overview

Maximizing photovoltaic conversion efficiency hinges on balancing light absorption, carrier extraction, and recombination pathways. This scaffold pairs a reproducible classical baseline based on a simplified Shockley-Queisser style radiative limit with multi-junction heuristics, while reserving space for Q# experiments that explore excitonic transport and quantum-enhanced light harvesting. The objective is to compare classical efficiency projections against quantum-inspired proposals for coherent exciton management.

## Directory Layout

```text
18_photovoltaics/
├── estimates/                        # JSON artifacts from classical / quantum workflows
├── instances/                        # Bandgap selections, temperatures, recombination parameters
├── plots/                            # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py         # Shockley–Queisser style efficiency estimator
│   └── analyze.py                    # Visualization of efficiency and voltage trends
└── qsharp/
    ├── QuantumPhotovoltaics.csproj   # Q# project placeholder for exciton transport routines
    └── Program.qs                    # Stubbed quantum workflow
```

## Quick Start

```bash
cd problems/18_photovoltaics

# Classical efficiency baseline
python python/classical_baseline.py

# Plot efficiency vs. bandgap and temperature trends
python python/analyze.py

# Quantum placeholder (requires .NET 6)
dotnet build qsharp/QuantumPhotovoltaics.csproj
 dotnet run --project qsharp/QuantumPhotovoltaics.csproj
```

## Next Quantum Milestones

1. **Excitonic Network Encoding** – Map donor-acceptor lattices into qubit graphs for coherent transport studies.
2. **Open Quantum Dynamics** – Model phonon-assisted hopping using Lindblad style channels or variational ansätze.
3. **Light-Harvesting Circuits** – Prototype quantum walk or cavity-assisted absorption kernels.
4. **Resource Estimation** – Track qubit counts and Trotter depths against realistic cell architectures.

This scaffold keeps the classical photovoltaic baseline reproducible while we explore quantum coherence for next-generation solar materials.

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
