---
applyTo: "tooling/estimator/**,tooling/azure/**,problems/*/estimates/**"
description: "Hackathon workstream A - one resource-estimate pipeline. Directory ownership, the trap that was removed, and what the guards now enforce."
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

- **The single estimate must name its estimator.** `circuits/estimate.json` carries
  `build.qdkVersion`, `estimatorVersion`, commit and timestamp; a missing, `unknown` or
  `mock` version fails. An estimate that cannot say what produced it is not evidence.
- **No second estimate store.** Nothing under an active `problems/*/estimates/` may be an
  estimate artifact (a mapping carrying `estimator_target`). Two stores is precisely how a
  fabricated constant sat unnoticed one directory away from real numbers for six months.
  Classical baselines, Azure job manifests, run results and calibration ensembles live in
  that directory, describe different things, and stay.
- The original operation-name check still applies: an estimate naming a Q# operation the
  code no longer defines is describing a ghost.

Both new guards were watched failing - mock provenance set on the surviving estimate, and
a stray `latest.json` dropped back into `estimates/` - before being trusted.

Deliberately **not** "every problem must report a different budget", which #255 proposed.
`02_catalysis` and `07_drug_discovery` genuinely coincide at
35 logical / 423,055 physical: both are two-qubit QPE instances whose fewest-qubit
configurations share one layout at code distance 25 and differ only in runtime, so a distinctness
rule would fail on true data. A check with known false positives is one people learn to
ignore.

## One pipeline (slice 2, done)

`tooling/generate_estimates.py` is the only thing that measures. It writes
`problems/<id>/circuits/estimate.json` for all 20 problems plus the website data.

`problems/<id>/estimates/` is **retired as an estimate store** for active problems.
`tooling/estimator/run_estimation.py` refuses to write there without
`--allow-retired-store`, and the consumers now read the single source:

| Consumer | Reads |
| --- | --- |
| `tooling/azure/assess_problem_readiness.py` | `circuits/estimate.json` |
| `tooling/azure/prepare_problem_manifest.py` | `circuits/estimate.json` |
| `tooling/estimator/generate_summary.py` | `circuits/estimate.json` |

Archived problems keep their historical store: they are a record of downgraded work, and
CI still regenerates `05_qaoa_maxcut` with `--mock`.

## You own

`tooling/estimator/`, `tooling/azure/`, `problems/*/estimates/`

## Do not touch

`website/` (workstream D), `viz/` (workstream B), `agents/`. If a change genuinely needs
to cross a seam, say so in the pull request rather than crossing it quietly.

## Regenerating

```
python tooling/generate_estimates.py        # the measurement, all 20 problems
python tooling/estimator/generate_summary.py  # the derived markdown summaries
```

Never pass `--mock` for an active problem. The artifacts it writes are explicitly
labelled simulated output, and both guards above will fail the build.

Shared rules - branching, the depgraph regeneration that trips most red builds,
verification expectations - are in `.github/copilot-instructions.md` and the pull request
template.
