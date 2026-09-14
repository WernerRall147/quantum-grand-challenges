---
applyTo: "tooling/estimator/**,tooling/azure/**,problems/*/estimates/**"
description: "Hackathon workstream A - retire the mock estimator pipeline. Directory ownership, the trap in this code, and what counts as done."
---

# Workstream A - retire the mock estimator

Tracking issue: [#255](https://github.com/WernerRall147/quantum-grand-challenges/issues/255).
This is the hackathon headline; the executive challenge is *Cloud Hardware Infra in the Era of AI*.

## The thing to understand before you change anything

There are **two parallel estimate pipelines**, and the fake one is the one being served.

| | Script | Writes | Real? |
| --- | --- | --- | --- |
| Real | `tooling/generate_estimates.py` | `problems/*/circuits/estimate.json`, `website/data/resourceEstimates.json` | yes - calls `qsharp.estimate` |
| Mock | `tooling/estimator/run_estimation.py` | `problems/*/estimates/*.json` | **no** - `_generate_mock_output()` |

The real one already produces defensible, genuinely different budgets. The mock one gives
all 9 active problems the identical triple 16 logical / 35,200 physical / 65,536 T.

`problems/*/estimates/latest.json` is read by `tooling/azure/assess_problem_readiness.py`
and `tooling/azure/prepare_problem_manifest.py`, so the fake numbers reach readiness and
maturity claims.

## You own

`tooling/estimator/`, `tooling/azure/`, `problems/*/estimates/`

## Do not touch

`website/` (workstream D), `viz/` (workstream B), `agents/`. If a change genuinely needs
to cross a seam, say so in the pull request rather than crossing it quietly.

## Ship in two slices

Slice 1 is independently demoable and carries the entry's thesis on its own. Land it first.

1. **Fail loudly.** `_generate_mock_output()` raises instead of fabricating when `qsharp-re`
   is unavailable, plus a guard test extending `tooling/test_estimate_provenance.py`: fail if
   any active problem carries `"qdk_version": "mock"`, and fail if two problems report
   identical logical+physical+T triples.
2. **Converge.** One pipeline. Repoint the `tooling/azure/` consumers at real figures.

## Done means

You watched the guard test fail. Reintroduce a mock artifact deliberately, confirm red,
restore. An estimator that silently substitutes invented numbers is exactly the failure in
`.github/copilot-instructions.md` under *"A green check is not evidence"* - a check measuring
something adjacent to what mattered. A guard against it that has never failed is the same bug
one level up.

Shared rules - branching, the depgraph regeneration that trips most red builds, verification
expectations - are in `.github/copilot-instructions.md` and the pull request template.
