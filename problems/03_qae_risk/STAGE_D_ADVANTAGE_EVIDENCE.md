# Stage D Advantage Evidence Package - 03_qae_risk

## Scope And Claim Boundary

- Problem: Tail-risk estimation via Quantum Amplitude Estimation (QAE).
- Current claim category: `projected`.
- Claim boundary: Asymptotic query-complexity advantage only (QAE O(1/epsilon) vs Monte Carlo O(1/epsilon^2)).
- Non-claim boundary: No production-hardware demonstrated wall-clock advantage is claimed.

## Baseline Fairness Review

- Classical comparator is defined in `python/classical_baseline.py` and persisted in `estimates/classical_baseline.json`.
- Baseline outputs are compared directly to quantum estimates for the same thresholded tail-risk objective.
- Calibration reports keep estimator settings explicit (`phase_bits`, `repetitions`, `shots`) in `estimates/quantum_estimate_ensemble.json`.
- Fairness status: pass for objective-level comparison; still limited by synthetic loss-distribution assumptions.

## Uncertainty Methodology

- Primary quantum uncertainty source: ensemble variability across independent runs.
- Reported metrics include:
  - `ensemble_std_deviation`
  - `ensemble_std_error`
  - per-run `quantum_std_error`
- Evidence source: `estimates/quantum_estimate_ensemble.json` and `estimates/quantum_estimate_run*.json`.
- Current quality note: uncertainty is run-to-run stable on the calibrated small instance, but broader instance coverage remains pending.

## Sensitivity And Risk Analysis

- Calibration sensitivity:
  - Current robust evidence is strongest on `small` instance calibration sweeps.
  - Medium/large portfolio realism remains a promotion risk.
- Modeling sensitivity:
  - Tail model is parameterized and synthetic; real portfolio data-loading effects are not represented.
- Deployment sensitivity:
  - Resource estimates are fault-tolerant projections and do not by themselves demonstrate NISQ performance.

## Backend And Deployment Assumptions

- Q# workflow path is defined in `qsharp/Program.qs` with runtime mapping in `qsharp/RuntimeConfig.qs`.
- Azure smoke execution evidence is available in `estimates/azure_smoke_report_small_d1.json` and `estimates/azure_job_manifest_small_d1.json`.
- Assumption: smoke runs validate submission/collection contract, not end-to-end production tail-risk SLAs.

## Residual Limitations

- No demonstrated category promotion yet because:
  - backend-calibrated uncertainty targets are not yet locked across additional instances/seeds,
  - production data-loading/oracle costs are not yet included in a full end-to-end benchmark,
  - hardware-readout characterization is still incomplete.

## Current Generated Stage D Artifacts

- `estimates/quantum_estimate_ensemble_small.json`
- `estimates/quantum_estimate_ensemble_medium.json`
- `estimates/quantum_estimate_ensemble_large.json`
- `estimates/fairness_review_stage_d.md`

Artifact status note:

- `small` is measured from a full 20-run ensemble.
- `medium` and `large` are now measured with reduced runtime parameters (`loss_qubits=8`, `precision_bits=4`, `repetitions=24`) to avoid simulator stalls.
- Promotion still requires rerunning `medium`/`large` with full target parameters once runtime stability constraints are resolved.

## Promotion Checklist To `demonstrated`

- [ ] Extend calibration evidence across `small`, `medium`, and `large` with fixed uncertainty thresholds.
- [ ] Include oracle/state-preparation overhead in end-to-end timing and query accounting.
- [ ] Add backend-specific readout/error characterization with reproducible confidence bounds.
- [ ] Re-run fairness audit against best-known classical Monte Carlo variance-reduction baselines for the same objective.
