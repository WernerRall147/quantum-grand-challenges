# Objective Maturity Gates

This document defines objective gates used across all challenge tracks to keep status claims aligned with evidence quality.

## Gate Definitions

### Stage A: Classical Baseline Validated

Required evidence:

- Deterministic or statistically stable classical baseline implementation.
- Instance coverage (`small`, `medium` at minimum).
- Reproducible command path documented in the problem README.
- Metrics persisted to `estimates/` with schema-compatible outputs.

### Stage B: Quantum Implementation Ready

Required evidence:

- Q# scaffold or canonical algorithm implemented and building under supported toolchain.
- Problem README includes algorithm assumptions and known limits.
- Build and run commands validated for local development path.
- Resource estimation path documented (even if preliminary).

### Stage C: Hardware-Aware Validation Complete

Required evidence:

- Hardware mapping or transpilation assumptions documented.
- Calibration and uncertainty evidence across multiple runs and instances.
- Quantum/classical comparison includes confidence intervals or equivalent error bars.
- QCVV-oriented checks or proxy diagnostics included where applicable.

### Stage D: Advantage Evidence Package Complete

Required evidence:

- Advantage claim template fully completed (below).
- Baseline fairness review completed (best-known classical comparator for stated scope).
- Claim category explicitly tagged: `theoretical`, `projected`, or `demonstrated`.
- Residual risks and assumption sensitivities documented.

## DiVincenzo Readiness Overlay

Use this as a hardware-realism overlay on top of Stages A-D. It does not replace stage gates; it strengthens Stage C/D evidence quality.

### Criteria Coverage

Track these criteria per problem as `met`, `partial`, `not-yet`, or `not-applicable` with one-line evidence notes:

- **Scalable physical system with well-characterized qubits**: map to logical/physical qubit counts, architecture assumptions, and calibration context.
- **Initialization capability**: document state-preparation assumptions and reset/initialization path.
- **Coherence long relative to gate/measurement times**: document noise model, depth/runtime relation, and error-budget assumptions.
- **Universal gate set**: document gate-basis assumptions, decomposition/transpilation notes, and unsupported operations.
- **Qubit-specific measurement**: document readout model, measurement fidelity assumptions, and post-processing dependence.

Optional (only when relevant to communication-oriented tracks):

- **Interconversion between stationary and flying qubits**.
- **Faithful transmission of flying qubits**.

### Stage Expectations With Overlay

- **Stage A/B**: optional qualitative notes are recommended but not blocking.
- **Stage C**: all five compute-oriented criteria should be present with at least `partial` or a justified `not-applicable` tag.
- **Stage D**: no unresolved `not-yet` entries in criteria required by the claim scope; residual gaps must appear in the Risk section of the Advantage Claim Contract.

### Minimal README Snippet

Add this section to each problem README during Stage C promotion:

```markdown
## DiVincenzo Readiness (Stage C/D Overlay)

| Criterion | Status | Evidence / Notes |
|---|---|---|
| Scalable qubit system | partial | Logical/physical qubit projections from estimator runs. |
| Initialization | met | Explicit state-preparation and reset path documented. |
| Coherence vs gate time | partial | Error budget and runtime/depth assumptions reported. |
| Universal gate set | met | Canonical gate decomposition documented in qsharp notes. |
| Qubit-specific measurement | partial | Readout assumptions and uncertainty bars included. |
```

Policy recommendation:

- Extend `tooling/reporting/maturity-policy.json` over time with DiVincenzo-compliance checks once README adoption is complete.

## Advantage Claim Template

Add this section to each problem README once Stage B is reached:

```markdown
## Advantage Claim Contract

- Claim category: theoretical | projected | demonstrated
- Problem class and instance regime:
- Baseline algorithm and fairness rationale:
- Quantum resource scaling claim:
- Data-loading and I/O assumptions:
- Noise/error model assumptions:
- Confidence/uncertainty method:
- Residual risks:
```

## Suggested Repository KPIs

Track these KPIs at repository level:

- `% problems at Stage A/B/C/D`
- `% problems with explicit Advantage Claim Contract`
- `% problems with uncertainty-bounded quantum/classical comparisons`
- `% problems with hardware-assumption sections in README`
- `% problems with paper-to-implementation traceability notes`

Automation support:

- `python tooling/reporting/stage_kpis.py` prints a human-readable KPI report.
- `python tooling/reporting/stage_kpis.py --json` emits machine-readable output for CI or dashboards.
- `python tooling/reporting/stage_kpis.py --out-md <path> --out-json <path>` writes dashboard artifacts.
- `python tooling/reporting/stage_kpis.py --policy tooling/reporting/maturity-policy.json --enforce` performs policy-gated checks.

Policy notes:

- `tooling/reporting/maturity-policy.json` currently enforces readiness-contract compliance for pilot tracks (`01_hubbard`, `03_qae_risk`, `15_database_search`).
- Expand `required_problems` as each additional problem README adopts gate + contract sections.
- CI uploads generated KPI markdown/json as the `maturity-kpis` artifact for each run.

Threshold options in policy:

- `minimum_stage`: global floor applied to every `required_problems` entry (for example `"B"` or `"C"`).
- `per_problem_minimum_stage`: optional per-problem overrides, for example:

```json
{
	"minimum_stage": "B",
	"per_problem_minimum_stage": {
		"03_qae_risk": "C",
		"15_database_search": "C"
	}
}
```

- `advisory_target_stage`: optional non-blocking target levels tracked in KPI output to highlight promotion gaps without failing CI.

Example:

```json
{
	"minimum_stage": "B",
	"per_problem_minimum_stage": {
		"03_qae_risk": "C",
		"15_database_search": "C",
		"01_hubbard": "B"
	}
}
```

Current rollout:

- All 20 problems now have explicit enforced per-problem stage thresholds in `tooling/reporting/maturity-policy.json`.
- Stage C is enforced for `03_qae_risk` and `15_database_search`; Stage B is enforced for remaining tracks.
- DiVincenzo readiness sections are now present across all 20 problem READMEs, enabling full-policy enforcement.

Persistent publication:

- `.github/workflows/objective-kpi-dashboard.yml` runs on a daily schedule and `workflow_dispatch`.
- It regenerates `docs/objective-kpis.md` and `docs/objective-kpis.json` and opens a PR if snapshots changed.

## Rollout Guidance

1. Start with pilot problems that already have complete pipelines (`03_qae_risk`, `15_database_search`, `01_hubbard`).
2. Add gate, claim, and DiVincenzo-readiness sections to each problem README.
3. Update root `README.md` status rows to use stage labels.
4. Promote stages only when evidence artifacts are committed.
