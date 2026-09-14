---
applyTo: "tooling/estimator/**,tooling/azure/**,problems/*/estimates/**"
description: "Hackathon workstream A - real resource estimates. Directory ownership, the trap that was removed, and what the guards now enforce."
---

# Workstream A - resource estimates

Tracking issue: [#255](https://github.com/WernerRall147/quantum-grand-challenges/issues/255).
This is the hackathon headline; the executive challenge is *Cloud Hardware Infra in the Era of AI*.

## What was wrong, and is now fixed (slice 1)

`tooling/estimator/run_estimation.py` shelled out to a `qsharp-re` executable that **no
installed package provides**. The resulting `FileNotFoundError` was caught and answered
with `_generate_mock_output()`, so every non-`--mock` run returned a fabricated constant:
all nine active problems reported an identical 16 logical / 35,200 physical / 65,536 T.

Two further layers sat underneath it. The batch config pointed every problem at
`qsharp/Program.qs`, a path that has not existed since the QDK migration, so the loop
skipped all twenty and still exited 0; and a batch whose every target failed also exited 0.

The live path now calls the same modern-QDK estimator as `tooling/generate_estimates.py`,
failures propagate instead of being answered with invented numbers, and the CLI exits
non-zero when nothing was estimated.

## What the guards enforce

`tooling/test_estimate_provenance.py`:

- No estimate artifact under an active `problems/*/estimates/` may carry mock provenance
  (`build.qdk_version == "mock"`, or an `estimator_version` starting `mock-`). Every
  artifact is checked, not just `latest.json` - 30 of them were mock while `latest.json`
  was already real.
- `estimates/latest.json` must agree with `circuits/estimate.json` on logical and physical
  qubits. Two independently-driven pipelines, one truth; a fabricated value in either
  diverges immediately.

Deliberately **not** "every problem must report a different budget". `02_catalysis`,
`07_drug_discovery` and `17_nuclear_physics` genuinely coincide at 12 logical / 57,764
physical because they share one VQE-shaped ansatz, so a distinctness rule would fail on
true data. A check with known false positives is one people learn to ignore.

Both guards were watched failing - mock provenance restored, and a qubit count edited back
to the old 35,200 - before being trusted.

## What is left (slice 2)

One pipeline. `problems/*/estimates/` and `problems/*/circuits/estimate.json` both still
exist and are now kept consistent by a test rather than by construction. Decide whether the
former is generated from the latter or retired, and repoint
`tooling/azure/assess_problem_readiness.py` and `prepare_problem_manifest.py` accordingly.

## You own

`tooling/estimator/`, `tooling/azure/`, `problems/*/estimates/`

## Do not touch

`website/` (workstream D), `viz/` (workstream B), `agents/`. If a change genuinely needs
to cross a seam, say so in the pull request rather than crossing it quietly.

## Regenerating

```
python tooling/estimator/run_estimation.py --all \
  --problem 01_hubbard,02_catalysis,07_drug_discovery,09_factorization,14_materials_discovery,16_error_correction,17_nuclear_physics,18_photovoltaics,19_quantum_chromodynamics \
  --targets surface_code_generic_v1,qubit_gate_ns_e3
python tooling/estimator/generate_summary.py
```

Never pass `--mock` for an active problem: the artifacts it writes are explicitly labelled
simulated output, and the guard above will fail the build.

Shared rules - branching, the depgraph regeneration that trips most red builds,
verification expectations - are in `.github/copilot-instructions.md` and the pull request
template.
