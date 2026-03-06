# Stage D Advantage Evidence Package - 05_qaoa_maxcut

## Scope And Claim Boundary

- Problem: MaxCut optimization via QAOA depth sweeps and uncertainty-bounded trials.
- Current claim category: `theoretical`.
- Claim boundary: No demonstrated hardware speedup or quality advantage is currently claimed.
- Non-claim boundary: Current evidence does not assert runtime superiority over best classical optimizers.

## Baseline Fairness Review

- Classical comparator is included in problem-local `python/` workflows and summarized in `estimates/quantum_classical_summary.md`.
- Trial outputs preserve optimizer settings and outcomes in per-instance JSON artifacts (for example `estimates/quantum_baseline_small_d3.json`).
- Fairness status: partial; baseline family is defined, but best-known industrial MaxCut baselines for each instance regime are not yet exhaustively benchmarked.

## Uncertainty Methodology

- Shot-based repeated-trial methodology is persisted in:
  - `estimates/quantum_baseline_small_d3.json`
  - `estimates/quantum_baseline_medium_d2.json`
  - `estimates/quantum_baseline_large_d2.json`
- Aggregate uncertainty fields include `mean`, `std`, and `ci95` for coarse and refined expectation metrics.
- Evidence-quality guardrails are checked and published via `estimates/evidence_quality_report.md` and `estimates/evidence_quality_report.json`.

## Sensitivity And Risk Analysis

- Depth sensitivity: documented in `estimates/depth_sweep_small.md`, `estimates/depth_sweep_medium.md`, `estimates/depth_sweep_large.md`.
- Noise sensitivity: documented in `estimates/noise_sweep_small_d3.md`, `estimates/noise_sweep_medium_d2.md`, `estimates/noise_sweep_large_d2.md`.
- Backend sensitivity: assumptions and constraints are documented in `estimates/backend_assumptions.md`.
- Risk: oracle/state-preparation and transpilation overhead can erase practical advantage at current instance sizes.

## Backend And Deployment Assumptions

- Azure submission contract evidence exists in:
  - `estimates/azure_job_manifest_small_d3.json`
  - `estimates/azure_smoke_report_small_d3.json`
- These artifacts validate execution plumbing and metadata contract, not yet complete hardware-quality benchmarking.
- Resource-estimation routes and profile summaries are available in `estimates/estimator_profile_summary.md` and `estimates/latest_*.json`.

## Residual Limitations

- DiVincenzo overlay still includes unresolved `not-yet` for coherence-vs-gate-time in README.
- Backend-calibrated, hardware-specific quality comparisons are incomplete.
- Claim remains `theoretical` until portability assumptions, fairness baselines, and hardware uncertainty evidence are all strengthened.

## Current Generated Stage D Artifacts

- `estimates/backend_calibration_stage_d.json`
- `estimates/fairness_benchmark_stage_d.json`
- `estimates/fairness_benchmark_stage_d.md`

Artifact status note:

- Backend calibration is currently a proxy composition from smoke metadata plus noise-degradation evidence.
- Promote to stronger claim only after replacing proxy calibration with backend measured coherence/readout data.

## Promotion Checklist To `projected`

- [ ] Complete coherence/readout calibration evidence on at least one named backend target.
- [ ] Expand fairness review against stronger classical MaxCut heuristics on matched instance sets.
- [ ] Maintain uncertainty-bounded superiority (or parity with explicit caveats) across small/medium/large sweeps.
- [ ] Preserve schema-stable evidence outputs and quality-report pass status in CI.
