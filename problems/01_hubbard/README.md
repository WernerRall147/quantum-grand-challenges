# 01 · Hubbard Model

> Exploring strongly correlated electrons in a minimal two-site Hubbard model. This
> serves as the starting point for scaling to larger lattices and more realistic
> Hamiltonians.

## 🎯 Objectives

- Establish a reproducible **classical baseline** for the half-filled two-site Hubbard model.
- Provide a compiling **Q# analytical benchmark** that mirrors the classical calculation.
- Prepare the scaffolding for future **variational** and **phase estimation** studies on
  larger Hubbard instances.

## 🧱 Project Structure

```
01_hubbard/
├── README.md                 # This document
├── Makefile                  # Convenience targets for the workflows
├── estimates/                # Generated estimation artifacts
├── instances/                # Parameter grids (small/medium/large)
├── plots/                    # Generated visualisations
├── python/
│   ├── classical_baseline.py # Classical analytical baseline
│   └── analyze.py            # Plot charge/spin gaps
└── qsharp/
    ├── Program.qs            # Analytical Q# baseline
    └── qsharp.json            # Modern QDK project file
```

## 🚀 Quickstart

From the repository root:

```bash
cd problems/01_hubbard

# Classical workflow
make classical    # writes estimates/classical_baseline.json
make analyze      # produces plots/gaps.png

# Quantum analytical baseline (uses modern QDK  qsharp Python package)
make build
make run

# Dedicated CLI modes
python tooling/run_all_qsharp.py  # runs via qsharp Python package
python tooling/run_all_qsharp.py  # runs via qsharp Python package
```

## 📈 Current Results

The analytical baseline computes the singlet and triplet energies of the two-site
Hubbard model across a small parameter sweep. The classical and Q# implementations
share the same closed-form expressions, ensuring parity between the two workflows.

Generated artefacts:

- `estimates/classical_baseline.json`: Numerical data for ground and excited states.
- `plots/gaps.png`: Charge and spin gap trends vs interaction strength.
- `STAGE_D_ADVANTAGE_EVIDENCE.md`: Stage D claim-boundary and evidence-tracking scaffold for expansion-queue onboarding.

## Objective Maturity Gate

- **Current gate**: **Stage C complete** (hardware-aware validation evidence in place: VQE Hubbard kernel runnable, calibration ensemble across runs, backend assumptions documented, dual-model estimator profile across instance sizes, OpenQASM exports for cross-platform validation, real Azure resource estimate captured).
- **Next gate target**: **Stage D** (advantage evidence package: fairness review against tensor-network/DMRG baseline, residual risks for naturally-quantum 2D regimes, claim category locked).

Stage C evidence references for this problem:

- Calibration ensemble: `estimates/quantum_calibration_ensemble.json` and `estimates/calibration_evidence.json`.
- Backend assumptions: `estimates/backend_assumptions.md`.
- Estimator profile (multi-instance, dual-model): `estimates/estimator_profile_summary.md`, `estimates/latest_qubit_gate_ns_e3_{small,medium,large}.json`, `estimates/latest_surface_code_generic_v1_{small,medium,large}.json`.
- Real Azure resource estimate: `estimates/real_resource_estimate_2026-03-25T091444Z.json`.
- Cross-platform OpenQASM exports: `estimates/hubbard_vqe_xx.qasm`, `estimates/hubbard_vqe_zz.qasm` with Azure result captures.
- Azure smoke validation: `estimates/azure_smoke_report_small_d1.md`, `estimates/azure_job_manifest_small_d1.json`.

## DiVincenzo Readiness (Stage C/D Overlay)

| Criterion | Status | Evidence / Notes |
|---|---|---|
| Scalable qubit system | partial | Two-site model is intentionally small; scalable resource projections will be added once non-analytical quantum kernels are benchmarked. |
| Initialization | partial | Initial-state assumptions for analytical parity are clear, but hardware-ready state-preparation routines are pending. |
| Coherence vs gate time | not-yet | No backend-calibrated coherence-vs-depth evidence yet because Stage C kernel execution is still pending. |
| Universal gate set | partial | Q# scaffold compiles and runs, but full gate-level decomposition for VQE/QPE kernels is a Stage C task. |
| Qubit-specific measurement | partial | Measurement semantics are defined in the scaffold; hardware readout error characterization is pending. |

## Advantage Claim Contract

- **Claim category (current)**: `theoretical`.
- **Problem class and regime**: Two-site half-filled Hubbard baseline with parameter sweeps in `instances/`.
- **Fair baseline**: Closed-form exact diagonalization style reference in `python/classical_baseline.py`.
- **Quantum resource scaling claim**: No demonstrated speedup claim yet; current Q# path is analytical parity scaffolding.
- **Data-loading and I/O assumptions**: Small fixed-size Hamiltonian instances; no large-scale state-preparation pipeline yet.
- **Noise/error model assumptions**: Not yet characterized for a physical backend because quantum kernel is pending.
- **Confidence/uncertainty method**: Classical outputs deterministic; quantum uncertainty reporting to be added at Stage C.
- **Residual risks**: Placeholder algorithm may not preserve performance once variational or phase-estimation circuits are introduced.

## 🧭 Roadmap

- [ ] Replace analytical expressions with variational or phase-estimation circuits.
- [ ] Expand classical baselines to include finite-temperature observables.
- [ ] Integrate Azure Quantum Resource Estimator once quantum kernels are implemented.

Contributions and experiments welcome!
