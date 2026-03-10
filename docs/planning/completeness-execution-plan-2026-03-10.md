# Completeness Execution Plan (2026-03-10)

## Goal
Ensure each website update reflects a complete, policy-compliant project state with verified runnable/correctness and reporting integrity.

## Current Baseline
- Runnable/correctness: 20/20 passed (`tooling/reporting/problem_runnable_correctness_report.json`).
- Maturity stages: Stage B = 17, Stage C = 3, Stage D = 0 (`docs/objective-kpis.json`).
- Azure run-history metrics audit: resolved coverage 100%, direct metrics 91.3% (`tooling/reporting/azure_run_history_metrics_audit.json`).
- Website data schema: valid (`tooling/reporting/validate_website_data_schema.py`).

## Website Update Gate (Required)
Run these steps before committing website-facing data changes:

1. `python tooling/reporting/stage_kpis.py --out-md docs/objective-kpis.md --out-json docs/objective-kpis.json`
2. `python tooling/reporting/problem_runnable_correctness_audit.py --output tooling/reporting/problem_runnable_correctness_report.json`
3. `python tooling/reporting/audit_azure_run_history_metrics.py --min-resolved-coverage 0.85 --enforce-threshold`
4. `python tooling/reporting/validate_website_data_schema.py`
5. `cd website && npm run build`

If any step fails, do not update website data until the blocker is resolved.

## Workstreams To Reach Stage-C Complete Portfolio

### Workstream 1: Promote Stage B Problems to Stage C
Target: move 17 Stage-B problems to Stage C with reproducible kernel evidence.

Per-problem minimum exit criteria:
- Quantum kernel implemented and runnable in `qsharp/`.
- Classical baseline + quantum result comparison in `estimates/`.
- Uncertainty and error bars documented.
- Updated README with gate status and evidence links.

### Workstream 2: Stage D Advancement for Priority Problems
Target: promote active Stage-C problems (`03_qae_risk`, `05_qaoa_maxcut`, `15_database_search`) toward Stage D.

Exit criteria:
- Calibrated backend assumptions and uncertainty accounting.
- Stress/fairness evidence and reproducible decision logs.
- CI policy gates aligned with advantage-claim requirements.

### Workstream 3: Reporting Hardening
Target: keep reporting artifacts deterministic and policy-safe.

Tasks:
- Keep website mirrors free of sensitive identifiers.
- Maintain audit threshold for Azure metric resolution.
- Ensure generated markdown/json artifacts are refreshed via automation.

## Execution Cadence
- Weekly: run Website Update Gate and publish status in planning notes.
- Bi-weekly: select 2-3 Stage-B problems for Stage-C promotion sprint.
- Monthly: reassess Stage-C to Stage-D priorities based on evidence quality and backend readiness.

## Next Sprint (Recommended)
1. `02_catalysis`: Stage C chemistry kernel + benchmark evidence.
2. `04_linear_solvers`: Stage C HHL kernel + condition-number benchmark report.
3. `06_high_frequency_trading`: Stage C kernel prototype + uncertainty report.

## Definition of Done (Repository Completeness)
- All 20 problems at least Stage C.
- Priority claims at Stage D with policy-backed evidence.
- Runnable/correctness remains 20/20 in CI.
- Website build and data schema validation pass on every update.
