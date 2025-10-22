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
