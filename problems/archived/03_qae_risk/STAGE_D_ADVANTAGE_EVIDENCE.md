# Stage D Advantage Evidence Package - 03_qae_risk

## Scope And Claim Boundary

- Problem: Tail-risk estimation via Quantum Amplitude Estimation (QAE).
- Current claim category: `theoretical`.
- Claim boundary: Asymptotic query-complexity advantage only (QAE O(1/epsilon) vs Monte Carlo O(1/epsilon^2)).
- Non-claim boundary: No production-hardware demonstrated wall-clock advantage is claimed.

## Baseline Fairness Review

- Comparator: plain Monte Carlo on the same 16-level distribution the circuit loads, at the same interval half-width and confidence as IQAE (`python/iqae_driver.py`, `estimates/iqae_analysis.json`). Both sides count applications of A (or its inverse); a Monte Carlo sample costs one.
- `python/classical_baseline.py` samples the continuous log-normal model, which has a different tail probability (0.1798 against 0.1614 on the grid), so it is not the comparator for the circuit's output.
- Fairness status: pass for query counts on the same objective; limited by the synthetic loss distribution and by ignoring loading and error-correction costs.

## Uncertainty Methodology

- IQAE reports a Clopper-Pearson-based interval that contains a with probability at least 1 − α (Grinko et al. 2021, Algorithm 1). `tooling/test_qae_kernel.py` checks that coverage by repeating the algorithm 300 times against an exact sampler.
- Canonical QAE's error is bounded by Theorem 12 of Brassard et al. (within 0.0385 with probability at least 8/π² at 6 phase bits); the phase-register distribution is checked exactly against their Theorem 11.
- The calibration ensemble of record is `estimates/quantum_calibration_ensemble.json` (`tooling/generate_calibration_ensemble.py`), hashed to the Q# sources it ran.
- Superseded: `estimates/quantum_estimate_ensemble*.json` and `estimates/quantum_estimate_run*.json` came from the canonical kernel before the 2026-09-27 correction, whose phase register peaked at 0 and 32 of 64 instead of 8 and 56. Their means (for example 19.58%) were averages over that wrong distribution.

## Sensitivity And Risk Analysis

- Calibration sensitivity:
  - Current robust evidence is strongest on `small` instance calibration sweeps.
  - Medium/large portfolio realism remains a promotion risk.
- Modeling sensitivity:
  - Tail model is parameterized and synthetic; real portfolio data-loading effects are not represented.
- Deployment sensitivity:
  - Resource estimates are fault-tolerant projections and do not by themselves demonstrate NISQ performance.

## Backend And Deployment Assumptions

- Q# workflow path is defined in `qsharp/src/Main.qs` with runtime mapping in `qsharp/RuntimeConfig.qs`.
- Azure smoke execution evidence is available in `estimates/azure_smoke_report_small_d1.json` and `estimates/azure_job_manifest_small_d1.json`.
- Assumption: smoke runs validate submission/collection contract, not end-to-end production tail-risk SLAs.

## Residual Limitations

- No demonstrated category promotion yet because:
  - backend-calibrated uncertainty targets are not yet locked across additional instances/seeds,
  - production data-loading/oracle costs are not yet included in a full end-to-end benchmark,
  - hardware-readout characterization is still incomplete.

## Current Generated Stage D Artifacts

- `estimates/iqae_analysis.json` (IQAE on the Q# kernel, Monte Carlo on the same distribution, query counts at equal half-width)
- `estimates/quantum_calibration_ensemble.json`
- `estimates/variance_and_overhead_stage_d.json`
- `estimates/variance_and_overhead_stage_d.md`
- `estimates/backend_readout_characterization_stage_d.json`
- `estimates/backend_readout_characterization_stage_d.md`

Superseded artifacts, kept for the record:

- `estimates/quantum_estimate_ensemble_small.json`, `_medium.json`, `_large.json`: produced through `python/analyze.py` by the canonical kernel before the 2026-09-27 correction. `analyze.py` still calls the retired `dotnet` toolchain, so they cannot be regenerated until it is ported.
- `estimates/fairness_review_stage_d.md`: compared those ensembles, at threshold 2.5, with a classical baseline at threshold 2.0 on the continuous distribution.

## Promotion Checklist To `demonstrated`

- [ ] Regenerate multi-instance ensembles with the corrected kernel (needs `analyze.py` ported to the `qdk` package).
- [x] Include oracle/state-preparation overhead in query accounting (applications of A or its inverse on both sides).
- [x] Add backend-specific readout/error characterization with reproducible confidence bounds.
- [x] Compare against Monte Carlo on the same objective at equal half-width and confidence.

Checklist caveat:

- Readout/error characterization is currently satisfied by measured execution/readout proxy confidence bounds from Azure run history.
- Full hardware tomography-style readout characterization remains future enhancement and is not required for the current `theoretical` claim category.
- A `demonstrated` claim would also need wall-clock evidence including error correction, which no current hardware can supply.
