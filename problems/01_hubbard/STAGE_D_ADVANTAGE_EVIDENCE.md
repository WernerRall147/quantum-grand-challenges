# Stage D Advantage Evidence Package - 01_hubbard

## Scope And Claim Boundary

- Problem: Two-site half-filled Hubbard model baseline with analytical parity scaffolding.
- Current claim category: `theoretical`.
- Claim boundary: Algorithmic and resource-scaling expectations only.
- Non-claim boundary: No production-hardware demonstrated wall-clock advantage is claimed.

## Baseline Fairness Review

- Classical comparator: `python/classical_baseline.py` with outputs in `estimates/classical_baseline.json`.
- Quantum comparator: analytical Q# baseline in `qsharp/Program.qs` and estimator output snapshots in `estimates/latest.json` and timestamped estimator files.
- Fairness status: objective-level parity is acceptable for Stage B; this package is not yet sufficient for Stage D claim promotion.

## Uncertainty Methodology

- Classical baseline is deterministic/analytical for the current two-site model.
- Quantum uncertainty reporting is not yet fully implemented for non-analytical kernels.
- Current gap: shot-based uncertainty bounds and backend-calibrated confidence intervals are still required for Stage C-to-D progression.

## Backend And Deployment Assumptions

- Azure submission contract artifacts currently available:
  - `estimates/azure_job_manifest_small_d1.json`
  - `estimates/azure_smoke_report_small_d1.json`
  - `estimates/azure_smoke_report_small_d1.md`
- Assumption boundary: smoke evidence validates submit/collect plumbing only, not full production performance claims.

## Residual Limitations

- Non-analytical quantum kernel evidence is incomplete for Stage C exit criteria.
- Coherence-vs-depth, readout characterization, and calibration drift evidence are not yet locked.
- Data-loading and oracle/state-preparation overheads for larger instances remain open.

## Current Generated Stage D Artifacts

- `estimates/classical_baseline.json`
- `estimates/latest.json`
- `estimates/azure_job_manifest_small_d1.json`
- `estimates/azure_smoke_report_small_d1.json`
- `estimates/azure_smoke_report_small_d1.md`

## Stage D Checklist

- [ ] Add uncertainty-bounded quantum-vs-classical comparisons on at least `small` and `medium` instances.
- [ ] Add backend readout/reliability characterization artifact for at least one measured target.
- [ ] Add calibration/noise sensitivity artifact tied to reported metrics and claim category.
- [ ] Re-run readiness audit with zero open checklist items and zero artifact quality issues before promotion to blocking gate scope.