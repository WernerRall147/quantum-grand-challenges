# Stage D Advantage Evidence Package - 15_database_search

## Scope And Claim Boundary

- Problem: Unstructured search using canonical Grover workflow.
- Current claim category: `projected`.
- Claim boundary: Asymptotic query scaling (Grover O(sqrt(N)) vs classical O(N)).
- Non-claim boundary: No demonstrated backend wall-clock advantage is claimed.

## Baseline Fairness Review

- Classical comparator is explicit in `python/classical_baseline.py` and persisted in `estimates/classical_baseline.json`.
- Baseline quantifies expected query requirements at matched confidence assumptions.
- Fairness status: pass for query-complexity objective; still requires stronger wall-clock and implementation-overhead parity framing for deployment claims.

## Uncertainty Methodology

- Simulator empirical success rates are documented in `docs/GROVER_IMPLEMENTATION_SUMMARY.md`.
- Current limitation: backend shot-based confidence intervals are not yet persisted as a dedicated artifact for this problem.
- Stage D hardening target: add backend-specific CI bounds (for example Wilson/normal intervals with explicit shot counts) in `estimates/`.

## Sensitivity And Risk Analysis

- Oracle-synthesis sensitivity:
  - Practical benefits depend on oracle construction complexity and data-access model.
- Marked-fraction sensitivity:
  - Performance depends on item density assumptions configured in `instances/`.
- Backend sensitivity:
  - Current evidence is largely simulator-centric; hardware/transpilation effects are not yet fully quantified.

## Backend And Deployment Assumptions

- Azure execution contract artifacts are available:
  - `estimates/azure_job_manifest_small_d1.json`
  - `estimates/azure_smoke_report_small_d1.json`
- These artifacts verify submission and collection flow, but do not yet provide full production-grade quality metrics.

## Residual Limitations

- DiVincenzo overlay still has unresolved `not-yet` status for coherence-vs-gate-time in README.
- Hardware readout and uncertainty calibration remain incomplete.
- Data-oracle construction overhead for practical databases is not yet integrated in end-to-end claims.

## Promotion Checklist To `demonstrated`

- [ ] Add backend shot-based uncertainty artifacts for small/medium/large runs with reproducible scripts.
- [ ] Include transpilation/oracle construction overhead in reported end-to-end performance.
- [ ] Validate claim stability across marked-fraction regimes and backend targets.
- [ ] Complete hardware readout characterization and map residual error to claim confidence.
