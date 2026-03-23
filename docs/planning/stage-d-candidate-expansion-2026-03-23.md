# Stage D Candidate Expansion Plan

Generated: 2026-03-23

## Objective

Expand the Stage D promotion pipeline from 3 active candidates to a 5-candidate queue while preserving strict CI gating for current fully-ready candidates.

## Current Gate Scope (Blocking)

- 03_qae_risk
- 05_qaoa_maxcut
- 15_database_search

These remain in the required CI gate and must stay fully ready.

## Expansion Queue (Non-Blocking Onboarding)

- 01_hubbard
- 04_linear_solvers

## Why These Two Next

- 01_hubbard has mature Stage B reproducibility and stable Q# scaffolding, making Stage C and Stage D evidence progression tractable.
- 04_linear_solvers already has condition-number-aware baseline analysis, giving a clear path to Stage C kernel evidence and then Stage D claim audits.

## Onboarding Checklist

- Add `STAGE_D_ADVANTAGE_EVIDENCE.md` for each queue candidate with explicit claim category boundaries.
- Add required Stage D artifact list and quality checks before promoting each to blocking gate scope.
- Generate backend characterization and fairness/overhead artifacts aligned to claim category.
- Run `tooling/reporting/stage_d_readiness_audit.py` and ensure 6/6 readiness before moving from queue to blocking scope.

## Promotion Rule

Only move a candidate from expansion queue to blocking CI gate when:

- Readiness score is 6/6.
- Open checklist items = 0.
- Artifact issue count = 0.
- Claim category remains policy-compliant (no overclaiming).
