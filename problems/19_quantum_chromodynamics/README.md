# Problem 19 · Quantum Chromodynamics

## Overview

Nonperturbative quantum chromodynamics (QCD) remains one of the central frontiers in high-energy physics. This scaffold combines a reproducible classical baseline built on coarse lattice gauge theory energy estimation with a Q# project prepared for future Hamiltonian digitisation and quantum walk dynamics. The aim is to benchmark simple plaquette observables against quantum-inspired workflows that could capture confinement physics with reduced computational cost.

## Directory Layout

```text
19_quantum_chromodynamics/
├── estimates/                        # JSON artifacts from classical and quantum workflows
├── instances/                        # Lattice sizes, spacings, and coupling constants
├── plots/                            # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py         # Wilson plaquette energy estimator and string tension proxy
│   └── analyze.py                    # Visualization of plaquette energy and string tension trends
└── qsharp/
    ├── QuantumQcd.csproj             # Q# project placeholder for lattice gauge routines
    └── Program.qs                    # Stubbed quantum workflow
```

## Quick Start

```bash
cd problems/19_quantum_chromodynamics

# Classical lattice baseline
python python/classical_baseline.py

# Plot plaquette energy and string tension behaviour
python python/analyze.py

# Quantum placeholder (requires .NET 6)
dotnet build qsharp/QuantumQcd.csproj
 dotnet run --project qsharp/QuantumQcd.csproj
```

## Next Quantum Milestones

1. **Hamiltonian Encoding** – Map Kogut-Susskind Hamiltonians onto qubit registers with flux truncation.
2. **Gauge Constraints** – Integrate Gauss law projectors for SU(3) or SU(2) toy models.
3. **Spectral Estimation** – Prototype adiabatic state preparation and phase estimation for glueball spectra.
4. **Resource Estimation** – Track qubit counts and trotterisation depth as lattice volume scales.

This scaffold keeps the lattice baseline reproducible while setting up future quantum simulations of the strong force.

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
