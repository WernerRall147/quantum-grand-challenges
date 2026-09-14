---
applyTo: "website/**"
description: "Hackathon workstream D - demo surface. Directory ownership, the manifest contract with the Blender pipeline, and which estimate data is already honest."
---

# Workstream D - demo surface

Tracking issue: [#257](https://github.com/WernerRall147/quantum-grand-challenges/issues/257).
This workstream owns the 3-minute demo end to end. It is what the judges actually watch.

## Start from what is already true

`website/data/resourceEstimates.json` **already carries real numbers** - 01_hubbard at
12 logical / 53,628 physical, 02_catalysis at 12 / 57,764, 03_qae_risk at 40 / 369,400 -
written by `tooling/generate_estimates.py`, which calls the real estimator.

So the website is **not** the thing showing fake figures. The mock artifacts under
`problems/*/estimates/` are, and those are workstream A's. You are not blocked on A: you can
build against honest data today.

Do confirm which surface reads which file before changing it. Some may read the mock path.

## You own

`website/` - components, pages, lib, data wiring.

## Do not touch

`viz/` (workstream B), `tooling/estimator/` and `problems/*/estimates/` (workstream A).

## The contract with workstream B

- **B writes** render assets and **`viz/manifest.json`**. B never edits `.tsx`.
- **D reads** the manifest and renders it.
- Agree the schema **first**, in a stub pull request. You need the schema to start, not B's
  output - so this should not block you past Monday.

`viz/manifest.json` does not exist yet; B creates it.

## The demo

Beats are in `docs/AzureFriday/script.md`, which owns them - do not restate them elsewhere.
Beat 2, the agent **declining** to send portfolio optimisation to quantum and returning
`HPC_PREFERRED`, is the money shot. Walk the whole thing end to end before Thursday; the first
honest run-through always finds something.

## Before you push

Touching `.ts` or `.tsx` trips the `depgraph-drift` check. Run
`python tooling/depgraph/build_graph.py` and commit `docs/depgraph/*` in the same pull request.
This is the most common red build here.

Shared rules are in `.github/copilot-instructions.md` and the pull request template.
