# viz - Blender visualisation of quantum problem runs

Workstream B of the Hackathon 2026 milestone. Tracking issue:
[#254](https://github.com/WernerRall147/quantum-grand-challenges/issues/254).

This directory is a landing spot, deliberately created empty. Nothing here is built yet.

## The contract with the website

`viz/` and `website/` are owned by different people this week, and both have a claim on how
renders reach the page. The seam:

- **This directory writes** render assets and **`viz/manifest.json`** describing them.
- **`website/` reads** the manifest and renders it. It never edits the render pipeline.
- Nothing here edits `.tsx`.

`viz/manifest.json` **does not exist yet.** Agreeing its schema - in a stub pull request,
before either side builds against it - is the first task, because the website only needs the
schema to start, not the renders.

## Scope

One problem, rendered properly. Not a pass over all of them.

Real per-problem resource budgets are in `problems/*/circuits/estimate.json`; pick one that
reads distinctly against its neighbours. `16_error_correction` is 18 logical / 1,746 physical,
an order of magnitude cheaper than `14_materials_discovery` at 12 / 163,268.

## Before you push

Adding `.py` here trips the `depgraph-drift` check. Run
`python tooling/depgraph/build_graph.py` and commit `docs/depgraph/*` in the same pull request.

Agent instructions for this directory are in
`.github/instructions/hackathon-workstream-b.instructions.md`; shared repository rules are in
`.github/copilot-instructions.md`.
