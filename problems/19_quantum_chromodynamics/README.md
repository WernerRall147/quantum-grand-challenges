# Problem 19 · Quantum Chromodynamics

## Overview

Nonperturbative quantum chromodynamics (QCD) remains one of the central frontiers in high-energy physics. This scaffold pairs a classical estimate of lattice gauge observables with a Q# kernel that stands in for the quantum simulation this problem is about.

**What the code computes.** The quantum kernel is Trotterized real-time evolution of a transverse-field Ising chain, H = beta sum Z_i Z_{i+1} + h sum X_i, from |0...0>, measuring the product of Z over all sites. It is not a gauge theory: there are no gauge fields and no Gauss's law, and the 1D transverse-field Ising chain maps to free fermions, so it is classically solvable at any size. Earlier versions of this page and the site called the measured quantity a Wilson loop and printed a confinement signature (area law at small beta, perimeter law at large beta); a single fixed-size string evolved for unit time from a product state cannot show either. `tooling/test_ising_chain_kernel.py` checks the program, the hardware kernel and the OpenQASM export against exact evolution of the same circuit. The classical baseline is a separate heuristic: closed-form formulas for SU(3) plaquette, string-tension and glueball-mass proxies, not a lattice Monte Carlo and not the model the quantum kernel simulates. A kernel that models gauge dynamics (Gauss's-law constraints, then plaquettes) is the first milestone below.

## Directory Layout

```text
19_quantum_chromodynamics/
├── estimates/                        # JSON artifacts from classical and quantum workflows
├── instances/                        # Lattice sizes, spacings, and coupling constants
├── plots/                            # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py         # Heuristic SU(3) plaquette, string-tension and glueball-mass proxies
│   └── analyze.py                    # Visualization of plaquette energy and string tension trends
└── qsharp/
    ├── qsharp.json                   # Modern QDK project file
    ├── HardwareKernel.qs             # 4-site Ising-chain Trotter kernel for Azure Quantum
    └── src/Main.qs                   # Trotterized transverse-field Ising chain (see Overview)
```

## Quick Start

```bash
cd problems/19_quantum_chromodynamics

# Classical lattice baseline
python python/classical_baseline.py

# Plot plaquette energy and string tension behaviour
python python/analyze.py

# Quantum kernel (uses modern QDK  qsharp Python package)
python -c "from qdk import qsharp; qsharp.init(project_root='qsharp'); qsharp.run('Main.RunQCDSimulation()', 1)"
```

## Next Quantum Milestones

1. **Hamiltonian Encoding** – Map Kogut-Susskind Hamiltonians onto qubit registers with flux truncation.
2. **Gauge Constraints** – Integrate Gauss law projectors for SU(3) or SU(2) toy models.
3. **Spectral Estimation** – Prototype adiabatic state preparation and phase estimation for glueball spectra.
4. **Resource Estimation** – Track qubit counts and trotterisation depth as lattice volume scales.

This scaffold keeps the lattice baseline reproducible while setting up future quantum simulations of the strong force.

## Objective Maturity Gate

- **Current gate**: **Stage C complete** (hardware-aware validation evidence in place: Trotterized Ising-chain kernel runnable, calibration ensemble across runs, backend assumptions documented, dual-model estimator profile, OpenQASM export, Azure smoke validation).
- **Next gate target**: **Stage D** (advantage evidence package: fairness review against Euclidean lattice QCD for static observables, residual risks for real-time dynamics / sign problem, claim category locked). A Stage D claim would first need a kernel that models gauge dynamics: the current Ising chain is classically solvable at any size.

Stage C evidence references for this problem:

- Calibration ensemble: `estimates/quantum_calibration_ensemble.json` (the mean Z-parity of a 2-site chain, previously labelled a Wilson loop) and `estimates/calibration_evidence.json`.
- Backend assumptions: `estimates/backend_assumptions.md`.
- Estimator profile (ns-e3 + surface-code-generic): `estimates/estimator_profile_summary.md`, `estimates/latest_qubit_gate_ns_e3.json`, `estimates/latest_surface_code_generic_v1.json`.
- Cross-platform OpenQASM export: `estimates/trotter_gauge.qasm`, the same circuit as `qsharp/HardwareKernel.qs` since 2026-09-26 (it previously used angles too small to distinguish a right circuit from a wrong one).
- Azure smoke validation: `estimates/azure_smoke_report_small_d1.md`, `estimates/azure_job_manifest_small_d1.json`.

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
