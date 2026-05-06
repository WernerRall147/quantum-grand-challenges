# Problem 14 · Quantum Materials Discovery

## Overview

Designing next-generation battery cathodes requires exploring a vast space of material compositions and crystal structures. This scaffold provides a reproducible classical baseline that scores candidate compositions using simplified cluster expansions and builds a Q# project for future hybrid VQE and phase-estimation workflows that evaluate band gaps and defect energetics.

## Directory Layout

```text
14_materials_discovery/
├── estimates/                        # JSON artifacts from classical / quantum workflows
├── instances/                        # Candidate composition grids (small/medium/large)
├── plots/                            # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py         # Surrogate energy/stability scoring for battery materials
│   └── analyze.py                    # Visualization of Pareto fronts and composition trends
└── qsharp/
    ├── qsharp.json            # Modern QDK project file
    └── Program.qs                    # Stubbed quantum workflow
```

## Quick Start

```bash
cd problems/14_materials_discovery

# Classical surrogate baseline
env PYTHONPATH=../../.. python python/classical_baseline.py

# Visualize stability vs. voltage trends
python python/analyze.py

# Quantum placeholder (uses modern QDK — qsharp Python package)
python -c "import qsharp; qsharp.init(project_root='qsharp'); print('Build OK')"
 python tooling/run_all_qsharp.py  # runs via qsharp Python package
```

## Next Quantum Milestones

1. **Hamiltonian Construction** – Encode tight-binding or Hubbard-like operators for candidate lattices.
2. **Variational Ansätze** – Develop chemistry-informed ansätze for defect and conduction band evaluations.
3. **Cost Function Calibration** – Integrate quantum outputs with classical thermodynamic models.
4. **Resource Estimation** – Quantify qubit counts and logical depth for realistic band-gap predictions.

This scaffold keeps the classical materials-surrogate baseline reproducible while laying the groundwork for quantum-assisted materials discovery. 🔋⚛️

## Objective Maturity Gate

- **Current gate**: **Stage C complete** (hardware-aware validation evidence in place: QPE band-gap kernel runnable, calibration ensemble across runs, backend assumptions documented, dual-model estimator profile, OpenQASM export, Azure smoke validation).
- **Next gate target**: **Stage D** (advantage evidence package: fairness review against DFT/GW for strongly-correlated materials, residual risks for high-Tc / Mott regimes, claim category locked).

Stage C evidence references for this problem:

- Calibration ensemble: `estimates/quantum_calibration_ensemble.json` and `estimates/calibration_evidence.json`.
- Backend assumptions: `estimates/backend_assumptions.md`.
- Estimator profile (ns-e3 + surface-code-generic): `estimates/estimator_profile_summary.md`, `estimates/latest_qubit_gate_ns_e3.json`, `estimates/latest_surface_code_generic_v1.json`.
- Cross-platform OpenQASM export: `estimates/vqe_bandgap.qasm`.
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
