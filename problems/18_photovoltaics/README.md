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
