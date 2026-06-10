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
    ├── qsharp.json            # Modern QDK project file
    └── Program.qs                    # Stubbed quantum workflow
```

## Quick Start

```bash
cd problems/19_quantum_chromodynamics

# Classical lattice baseline
python python/classical_baseline.py

# Plot plaquette energy and string tension behaviour
python python/analyze.py

# Quantum placeholder (uses modern QDK  qsharp Python package)
python -c "import qsharp; qsharp.init(project_root='qsharp'); print('Build OK')"
 python tooling/run_all_qsharp.py  # runs via qsharp Python package
```

## Next Quantum Milestones

1. **Hamiltonian Encoding** – Map Kogut-Susskind Hamiltonians onto qubit registers with flux truncation.
2. **Gauge Constraints** – Integrate Gauss law projectors for SU(3) or SU(2) toy models.
3. **Spectral Estimation** – Prototype adiabatic state preparation and phase estimation for glueball spectra.
4. **Resource Estimation** – Track qubit counts and trotterisation depth as lattice volume scales.

This scaffold keeps the lattice baseline reproducible while setting up future quantum simulations of the strong force.

## Objective Maturity Gate

- **Current gate**: **Stage C complete** (hardware-aware validation evidence in place: Trotter lattice gauge kernel runnable, calibration ensemble across runs, backend assumptions documented, dual-model estimator profile, OpenQASM export, Azure smoke validation).
- **Next gate target**: **Stage D** (advantage evidence package: fairness review against Euclidean lattice QCD for static observables, residual risks for real-time dynamics / sign problem, claim category locked).

Stage C evidence references for this problem:

- Calibration ensemble: `estimates/quantum_calibration_ensemble.json` and `estimates/calibration_evidence.json`.
- Backend assumptions: `estimates/backend_assumptions.md`.
- Estimator profile (ns-e3 + surface-code-generic): `estimates/estimator_profile_summary.md`, `estimates/latest_qubit_gate_ns_e3.json`, `estimates/latest_surface_code_generic_v1.json`.
- Cross-platform OpenQASM export: `estimates/trotter_gauge.qasm`.
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
