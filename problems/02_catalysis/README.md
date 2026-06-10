# 02. Quantum Catalysis Challenge

This problem explores quantum simulation of catalytic reaction mechanisms, comparing classical and quantum approaches for estimating reaction rates and energy barriers. The goal is to establish analytical baselines and prepare for quantum algorithm implementation.

## Roadmap
- [x] Scaffold directory structure
- [x] Implement classical analytical baseline (Arrhenius model)
- [x] Implement Q# analytical baseline (matching classical results)
- [x] Generate parameter instances (small/medium/large)
- [x] Validate outputs and plots
- [ ] Update documentation and website status

## Quickstart
```bash
cd problems/02_catalysis
make classical      # Run classical baseline analysis
make analyze        # Generate plots
make build          # Build Q# project (uses modern QDK — qsharp Python package)
make run            # Run quantum simulation
```

## Outputs
- `estimates/classical_baseline.json`: Structured Arrhenius rates for each instance
- `plots/rate_vs_temperature.png`: Visualization of reaction rates vs. temperature
- `qsharp/src/Main.qs`: Q# baseline source, compiled on-the-fly by the modern QDK (no DLL artifact)

## Current Results

Running `python python/classical_baseline.py` produces the following reaction rates:

| Instance | Catalyst | Temperature (K) | Rate (s^-1) |
|----------|----------|-----------------|-------------|
| small    | Pt       | 300             | 0.8727      |
| medium   | Fe       | 500             | 5.94×10^2   |
| large    | Cu       | 700             | 2.92×10^5   |

The Q# entry point `RunAnalyticalCatalysisBaseline` reports the same values, confirming parity between classical and quantum-friendly baselines.

## References
- Quantum simulation of chemical catalysis
- Analytical models for reaction rates
- Q# quantum chemistry libraries

## Objective Maturity Gate

- **Current gate**: **Stage C complete** (hardware-aware validation evidence in place: QPE chemistry kernel runnable, calibration ensemble across runs, backend assumptions documented, estimator profile produced for both ns-e3 superconducting and surface-code-generic models).
- **Next gate target**: **Stage D** (advantage evidence package hardening: fairness review against best-known classical baseline, residual risks quantified, claim category locked).

Stage C evidence references for this problem:

- Calibration ensemble: `estimates/quantum_calibration_ensemble.json` and `estimates/calibration_evidence.json`.
- Backend assumptions: `estimates/backend_assumptions.md`.
- Estimator profile (ns-e3 + surface-code-generic): `estimates/estimator_profile_summary.md`, `estimates/latest_qubit_gate_ns_e3.json`, `estimates/latest_surface_code_generic_v1.json`.
- Azure smoke validation: `estimates/azure_smoke_report_small_d1.md`, `estimates/azure_job_manifest_small_d1.json`.
- Reproducible quantum kernel: `qsharp/src/Main.qs` runnable via `qsharp.run('Main.RunCatalysisAnalysis()', 1)`.

## DiVincenzo Readiness (Stage C/D Overlay)

| Criterion | Status | Evidence / Notes |
|---|---|---|
| Scalable qubit system | partial | Current results validate analytical parity; scalable chemistry-kernel resource projections are pending Stage C implementation. |
| Initialization | partial | Reaction-parameter initialization is defined for analytical baselines; quantum state-loading fidelity work remains open. |
| Coherence vs gate time | not-yet | Backend-specific coherence and depth/runtime evidence has not yet been produced. |
| Universal gate set | partial | Q# baseline build path is validated, but gate-basis decomposition for a chemistry kernel is not finalized yet. |
| Qubit-specific measurement | partial | Output observables are defined for baseline workflows; hardware readout assumptions and uncertainty bands are pending. |

## Advantage Claim Contract

- **Claim category (current)**: `theoretical`.
- **Problem class and regime**: Problem-specific challenge instances defined in this directory.
- **Fair baseline**: Problem-local classical baseline in `python/` outputs.
- **Quantum resource scaling claim**: Expected asymptotic advantage depends on algorithm family and implementation assumptions; no hardware-demonstrated speedup claim yet.
- **Data-loading and I/O assumptions**: Must be documented alongside future advantage claims.
- **Noise/error model assumptions**: Backend-specific model and calibration assumptions to be added at Stage C.
- **Confidence/uncertainty method**: To be reported using shot-based confidence intervals or equivalent statistical bounds.
- **Residual risks**: Oracle/state-preparation/transpilation overhead may dominate for near-term instance sizes.
