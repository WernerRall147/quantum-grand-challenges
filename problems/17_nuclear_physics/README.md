# Problem 17 · Quantum Nuclear Physics

## Overview

Simulating few-nucleon systems requires capturing strong-interaction dynamics governed by Quantum Chromodynamics (QCD). This scaffold provides a reproducible classical baseline using a pionless effective-field-theory (EFT) toy Hamiltonian solved via exact diagonalization, while preparing a Q# project for future adiabatic state preparation and Trotterized time evolution. The goal is to compare classical bound-state energy estimates with quantum-inspired workflows.

## Directory Layout

```text
17_nuclear_physics/
├── estimates/                        # JSON artifacts from classical / quantum workflows
├── instances/                        # EFT coupling grids and cutoff parameters
├── plots/                            # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py         # Few-body EFT Hamiltonian builder + diagonalization
│   └── analyze.py                    # Visualization of binding energies and scattering lengths
└── qsharp/
    ├── QuantumNuclear.csproj         # Q# project placeholder for adiabatic/Trotter routines
    └── Program.qs                    # Stubbed quantum workflow
```

## Quick Start

```bash
cd problems/17_nuclear_physics

# Classical EFT baseline
python python/classical_baseline.py

# Plot binding energies and coupling trends
python python/analyze.py

# Quantum placeholder (requires .NET 6)
dotnet build qsharp/QuantumNuclear.csproj
 dotnet run --project qsharp/QuantumNuclear.csproj
```

## Next Quantum Milestones

1. **Hamiltonian Encoding** – Map low-energy nucleon interactions into qubit-friendly operators.
2. **Adiabatic State Prep** – Implement adiabatic ramps or variational ansätze for ground-state estimation.
3. **Phase Estimation / Spectroscopy** – Use quantum phase estimation to extract binding energies.
4. **Resource Estimation** – Track qubit counts and Trotter step complexity across cutoff scales.

This scaffold keeps the EFT baseline reproducible while we work toward quantum-enhanced nuclear simulations. ⚛️🪐
