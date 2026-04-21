# Stage D Advantage Evidence Package - 04_linear_solvers

## Scope And Claim Boundary

- Problem: Quantum linear-system solving with HHL-style workflow on small Poisson-like instances.
- Current claim category: `theoretical`.
- Claim boundary: Algorithmic and estimator-based resource expectations only.
- Non-claim boundary: No production-hardware demonstrated wall-clock advantage is claimed.

## Baseline Fairness Review

- Classical comparator: `python/classical_baseline.py` with outputs in `estimates/classical_baseline.json`.
- Quantum comparator: HHL implementation in `qsharp/Program.qs` with current resource/readiness reporting in README and summary docs.
- Fairness status: objective alignment is defined for small instances; Stage D promotion remains blocked pending calibrated uncertainty and backend evidence.

## Uncertainty Methodology

- Current state: deterministic classical residual/condition diagnostics are available.
- Gap: shot-based uncertainty bounds and confidence intervals for quantum output fidelity are not yet persisted as Stage D artifacts.
- Required progression: add uncertainty-bounded comparisons across at least `small` and `medium` instances.

## Backend And Deployment Assumptions

- Azure submit/collect contract artifacts currently available:
  - `estimates/azure_job_manifest_small_d1.json`
  - `estimates/azure_smoke_report_small_d1.json`
  - `estimates/azure_smoke_report_small_d1.md`
- Assumption boundary: smoke artifacts validate execution plumbing only and do not establish production performance claims.

## Residual Limitations

- Backend-calibrated coherence/readout characterization is not yet complete.
- Calibration/noise sensitivity evidence tied to HHL result quality is not yet locked.
- State-preparation, oracle, and transpilation overhead for larger systems may dominate any projected advantage.

## Current Generated Stage D Artifacts

- `estimates/classical_baseline.json`
- `estimates/azure_job_manifest_small_d1.json`
- `estimates/azure_smoke_report_small_d1.json`
- `estimates/azure_smoke_report_small_d1.md`

## Stage D Checklist

- [ ] Add uncertainty-bounded quantum-vs-classical comparisons on at least `small` and `medium` instances.
- [ ] Add backend readout/reliability characterization artifact for at least one measured target.
- [ ] Add calibration/noise sensitivity artifact linked to reported HHL metrics and claim boundaries.
- [ ] Re-run readiness audit with zero open checklist items and zero artifact quality issues before promotion to blocking gate scope.