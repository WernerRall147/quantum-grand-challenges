---
applyTo: "viz/**"
description: "Hackathon workstream B - Blender visualisation of quantum problem runs. Directory ownership and the manifest contract with the website."
---

# Workstream B - Blender visualisation

Tracking issue: [#254](https://github.com/WernerRall147/quantum-grand-challenges/issues/254).

## You own

`viz/` - this directory. It is new, which is deliberate: it collides with nothing.

## Do not touch

`website/` - specifically, **do not edit `.tsx`**. That is workstream D. B and D both having
a claim on the website is the one real collision risk this week, and the manifest below is
how it is avoided.

Also off-limits: `tooling/estimator/` and `problems/*/estimates/` (workstream A).

## The contract with workstream D

- **B writes** render assets and **`viz/manifest.json`** describing them.
- **D reads** the manifest and renders it. D never edits the render pipeline.
- The manifest schema is agreed **first**, in a stub pull request, before either side builds
  against it. D only needs the schema to start, not your output.

`viz/manifest.json` does not exist yet - you create it. Until it does, any document
describing it is describing something unbuilt and should say so.

## Scope

**One problem, rendered properly**, not a pass over all of them. Three build days remain
(Mon 14 - Wed 16; Thursday is freeze and rehearsal). The original issue said "start with our
20 hardest problems" - that is the version that does not finish. Note there are **9** active
problems in any case; the other 11 were honestly downgraded and live under `problems/archived/`.

Pick one whose resource budget reads well against the others. `16_error_correction`
(18 logical / 1,746 physical) is dramatically cheaper than its neighbours, and
`14_materials_discovery` (35 / 754,715) is the expensive extreme. Real figures are in
`problems/*/circuits/estimate.json`.

## Before you push

Adding `.py` under `viz/` trips the `depgraph-drift` check. Run
`python tooling/depgraph/build_graph.py` and commit `docs/depgraph/*` in the same pull request.
This is the most common red build here.

Shared rules are in `.github/copilot-instructions.md` and the pull request template.
