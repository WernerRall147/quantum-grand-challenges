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
    ├── qsharp.json            # Modern QDK project file
    └── Program.qs                    # Stubbed quantum workflow
```

## Quick Start

```bash
cd problems/18_photovoltaics

# Classical efficiency baseline
python python/classical_baseline.py

# Plot efficiency vs. bandgap and temperature trends
python python/analyze.py

# Quantum placeholder (uses modern QDK — qsharp Python package)
python -c "import qsharp; qsharp.init(project_root='qsharp'); print('Build OK')"
 python tooling/run_all_qsharp.py  # runs via qsharp Python package
```

## Next Quantum Milestones

1. **Excitonic Network Encoding** – Map donor-acceptor lattices into qubit graphs for coherent transport studies.
2. **Open Quantum Dynamics** – Model phonon-assisted hopping using Lindblad style channels or variational ansätze.
3. **Light-Harvesting Circuits** – Prototype quantum walk or cavity-assisted absorption kernels.
4. **Resource Estimation** – Track qubit counts and Trotter depths against realistic cell architectures.

This scaffold keeps the classical photovoltaic baseline reproducible while we explore quantum coherence for next-generation solar materials.

## Objective Maturity Gate

- **Current gate**: **Stage C complete** (hardware-aware validation evidence in place: quantum walk exciton-transport kernel runnable, calibration ensemble across runs, backend assumptions documented, dual-model estimator profile, OpenQASM export, Azure smoke validation).
- **Next gate target**: **Stage D** (advantage evidence package: fairness review against Lindblad master-equation baseline, residual risks for naturally-quantum open-system transport, claim category locked).

Stage C evidence references for this problem:

- Calibration ensemble: `estimates/quantum_calibration_ensemble.json` and `estimates/calibration_evidence.json`.
- Backend assumptions: `estimates/backend_assumptions.md`.
- Estimator profile (ns-e3 + surface-code-generic): `estimates/estimator_profile_summary.md`, `estimates/latest_qubit_gate_ns_e3.json`, `estimates/latest_surface_code_generic_v1.json`.
- Cross-platform OpenQASM export: `estimates/quantum_walk.qasm`.
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
