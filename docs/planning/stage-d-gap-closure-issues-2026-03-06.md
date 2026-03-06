# Stage D Gap-Closure Issue Set (2026-03-06)

This issue set defines measurable promotion work for:

- `03_qae_risk`
- `05_qaoa_maxcut`
- `15_database_search`

Each issue is designed to close specific Stage D gaps called out in each problem's `STAGE_D_ADVANTAGE_EVIDENCE.md` file.

## Issue 1: 03_qae_risk - Multi-instance uncertainty lock and fairness hardening

### Goal

Promote confidence in `projected` claim quality by extending uncertainty-bounded evidence from calibrated `small` to `small/medium/large`, and by tightening fairness against stronger classical baselines.

### Scope

- Run ensemble calibration for `small`, `medium`, and `large` with fixed run counts and documented seeds.
- Persist uncertainty summary metrics in schema-compatible artifacts under `problems/03_qae_risk/estimates/`.
- Add fairness comparison against at least one variance-reduction classical Monte Carlo baseline for the same tail-risk objective.

### Acceptance Criteria

- For each instance (`small`, `medium`, `large`), produce an ensemble artifact with:
  - run count >= 20,
  - explicit `ensemble_std_error`,
  - explicit quantum vs classical difference metric.
- Add a fairness appendix markdown artifact comparing:
  - baseline Monte Carlo,
  - variance-reduced classical baseline,
  - current QAE ensemble estimate.
- Update problem README Stage D section to reference new fairness artifact and instance-coverage status.

### Required Artifacts

- `problems/03_qae_risk/estimates/quantum_estimate_ensemble_small.json`
- `problems/03_qae_risk/estimates/quantum_estimate_ensemble_medium.json`
- `problems/03_qae_risk/estimates/quantum_estimate_ensemble_large.json`
- `problems/03_qae_risk/estimates/fairness_review_stage_d.md`

### Done Definition

- Evidence artifacts committed.
- Stage D file and README references updated.
- Repository reporting checks remain green.

## Issue 2: 05_qaoa_maxcut - Backend-calibrated coherence and classical fairness expansion

### Goal

Advance `theoretical` claim to `projected` readiness by closing coherence/readout and fairness gaps on matched instance sets.

### Scope

- Add backend-calibrated coherence/readout evidence on one named backend target.
- Extend classical comparator set with stronger MaxCut heuristics and matched instance evaluation.
- Maintain existing evidence-quality pass conditions while expanding benchmark breadth.

### Acceptance Criteria

- New backend calibration artifact includes:
  - target identifier,
  - shot plan,
  - readout/coherence assumptions,
  - uncertainty bounds over repeated trials.
- Classical fairness benchmark includes at least two comparator families and reports objective gaps versus QAOA outcomes.
- `evidence_quality_report.json` remains pass with no schema drift.

### Required Artifacts

- `problems/05_qaoa_maxcut/estimates/backend_calibration_stage_d.json`
- `problems/05_qaoa_maxcut/estimates/fairness_benchmark_stage_d.md`
- `problems/05_qaoa_maxcut/estimates/fairness_benchmark_stage_d.json`

### Done Definition

- DiVincenzo coherence line in README upgraded from `not-yet` to `partial` or `met` with evidence note.
- Stage D package references new artifacts and claim-category rationale.
- Reporting and website schema checks stay green.

## Issue 3: 15_database_search - Backend CI bounds and oracle-overhead accounting

### Goal

Strengthen `projected` claim toward demonstrable readiness by adding backend uncertainty artifacts and end-to-end oracle/transpilation overhead accounting.

### Scope

- Generate backend shot-based confidence interval artifacts for `small/medium/large`.
- Add explicit oracle construction and transpilation overhead accounting in performance summaries.
- Validate claim stability across marked-fraction regimes.

### Acceptance Criteria

- New uncertainty artifact set includes per-instance:
  - total shots,
  - observed success rate,
  - confidence interval method and bounds,
  - backend target metadata.
- New performance accounting report includes:
  - oracle synthesis overhead,
  - transpilation overhead,
  - net effect on practical speedup interpretation.
- Marked-fraction sensitivity report demonstrates no unsupported claim inflation under denser marked sets.

### Required Artifacts

- `problems/15_database_search/estimates/backend_uncertainty_small.json`
- `problems/15_database_search/estimates/backend_uncertainty_medium.json`
- `problems/15_database_search/estimates/backend_uncertainty_large.json`
- `problems/15_database_search/estimates/oracle_overhead_accounting_stage_d.md`
- `problems/15_database_search/estimates/marked_fraction_sensitivity_stage_d.md`

### Done Definition

- Stage D package and README link all new uncertainty and overhead artifacts.
- DiVincenzo coherence/readout notes updated with backend evidence status.
- Reporting checks remain green after artifact integration.

## Cross-Issue Verification Checklist

- Run matrix verification:
  - `python tooling/reporting/run_problem_verification_matrix.py`
- Run runnable correctness audit:
  - `python tooling/reporting/problem_runnable_correctness_audit.py --include-qsharp`
- Run website schema validation:
  - `python tooling/reporting/validate_website_data_schema.py`

## Suggested Labels And Priority

- Labels: `stage-d`, `advantage-claim`, `evidence-hardening`, `readme`, `reporting`.
- Priority:
  - P1: Issue 1 (`03_qae_risk`)
  - P1: Issue 3 (`15_database_search`)
  - P2: Issue 2 (`05_qaoa_maxcut`)
