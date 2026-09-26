# Stage D Advantage Evidence Package - 04_linear_solvers

## Scope and claim boundary

- Problem: quantum linear-system solving with a corrected 2x2 HHL workflow.
- Current claim category: `theoretical`.
- Claim boundary: algorithmic correctness for the toy circuit and classical baseline only.
- Non-claim boundary: no production-hardware wall-clock advantage is claimed.

## Baseline fairness review

- Classical comparator: `python/classical_baseline.py` with outputs in `estimates/classical_baseline.json`.
- Quantum comparator: corrected HHL implementation in `qsharp/src/Main.qs` and `qsharp/HardwareKernel.qs`.
- Fairness status: objective alignment is defined for the small toy circuit. Promotion remains blocked pending calibrated uncertainty and backend evidence; the resource estimate was regenerated on 2026-09-27.

## Uncertainty methodology

- Current state: `tooling/test_hhl_kernel.py` checks exact state-vector behavior and sampling tolerances for the corrected circuit.
- Gap: shot-based uncertainty bounds for problem instances beyond the toy circuit are not persisted as Stage D artifacts.
- Required progression: add uncertainty-bounded comparisons across at least `small` and `medium` instances on the corrected circuit.

## Backend and deployment assumptions

- Existing smoke artifacts validate old execution plumbing only.
- Existing `latest_*.json` estimator artifacts are mock data and are superseded for the corrected circuit.
- Backend-calibrated coherence, routing and readout characterization are not yet complete.

## Current generated Stage D artifacts

- `estimates/classical_baseline.json`
- `estimates/azure_job_manifest_small_d1.json`
- `estimates/azure_smoke_report_small_d1.json`
- `estimates/azure_smoke_report_small_d1.md`

## Stage D checklist

- [x] Regenerate resource estimates for the corrected HHL circuit (2026-09-27: 86,567 physical qubits, 23 logical).
- [ ] Add uncertainty-bounded quantum-vs-classical comparisons on at least `small` and `medium` instances.
- [ ] Add backend readout and reliability characterization for at least one measured target.
- [ ] Add calibration and noise-sensitivity artifacts linked to reported HHL metrics and claim boundaries.
- [ ] Re-run readiness audit before promotion to blocking gate scope.
