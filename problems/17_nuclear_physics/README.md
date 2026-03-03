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
