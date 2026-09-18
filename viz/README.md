# viz - Quantum run evidence and an interactive Bloch laboratory

Workstream B of the Hackathon 2026 milestone. Tracking issue:
[#254](https://github.com/WernerRall147/quantum-grand-challenges/issues/254).

One reusable Blender evidence scene, with error correction as the default showcase.
The catalog covers the original 20 problems, including the archived problems; it does
not reclassify archived work as an active advantage candidate. Batch mode applies the
same scene to any or all problems, rather than maintaining separate animations.
The standalone [Polarization atlas](interactive/index.html) adds an original browser
viewer without changing the website or requiring Blender.

## Interactive browser viewer

From the repository root:

```powershell
# Generate/validate every returned-bit marginal and the standalone local artifact.
python -m viz.build interactive

# Generate, then serve only viz\interactive on http://127.0.0.1:8765/.
python -m viz.build interactive --serve

# Also open the browser. Ctrl+C stops the server; --port 0 chooses a free port.
python -m viz.build interactive --open --port 0

# Independent output / alternate repository-local simulator-matrix snapshot.
python -m viz.build interactive --output viz\output\trial --runs path\to\matrix.json
```

Open the printed URL when serving. Alternatively open `viz\interactive\index.html`
directly: classic local scripts avoid `fetch` and module-CORS restrictions, so
`file://` works in browsers that permit adjacent local scripts. Browser/enterprise
policy can still block local files; use the HTTP option in that case. There are no
runtime CDN, network, font, library, Node, Blender, or QDK dependencies.

The generator calls the existing `build_catalog` and `z_marginal` path. Its dedicated
`interactive/evidence.js` contains the catalog's run provenance and full histograms,
plus derived marginals for every supported returned bit. It is generated, **not
hand-authored**, and checked against current sources by the tests. No simulator job
is run. The `interactive` command does **not** replace `manifest.json`, change its
schema, or touch existing render assets. It derives a fresh catalog from repository
sources rather than relying on poster metadata. With `--output`, the entire
self-contained viewer is copied to `<output>\interactive`.

### Two deliberately separate modes

- **Run evidence is the default.** The selector covers the catalog's original 20
  problems, including archived entries. A second selector chooses a zero-based
  returned measurement index when a supported run has multiple returned results.
  Missing or unsupported evidence remains selectable but shows unavailable and
  **no marker**. The default problem is error correction; default returned bit is 0.
- **Evidence geometry is not tomography.** Only `z = P(0) - P(1)` is measured.
  The marker stays at `(0, 0, z)`, including the origin for balanced counts, without
  normalization to the sphere. The X/Y zeros are a **diagonal-state display
  convention**, not measured values. Cartesian X/Y and state θ/φ readouts remain
  unknown; amplitudes are not displayed. See the
  [full evidence contract](#bloch-panel-scientific-semantics), which also applies here.
- **Pure-state sandbox is independent, and labelled in amber.** First entry uses the
  explicit `|0⟩` convention, not the selected run. Choose `|0⟩`, `|1⟩`, `|±⟩`,
  `|±i⟩`, or custom θ/φ, then press **Start selected state**. Gates X/Y/Z, H,
  S/S†, T/T† and right-hand axis rotations act only on this user-created ideal
  single-qubit pure state. Custom axes are normalized; zero axes and invalid numeric
  inputs are rejected before changing state. This is not a noisy-device or
  multi-qubit simulator, nor an animation of the problem's observed evolution.
- **Undo** removes the last gate/rotation; **Reset state** returns to the last
  explicitly chosen starting state. Choosing a new starting state clears history.
  Switching modes retains independent sandbox history and unchanged run evidence.
  Evidence values are immutable inside the browser model, and state-changing
  operations are rejected in evidence mode.
- **Readouts and export are mode-specific.** Pure-state θ is measured from +Z and φ
  from +X toward +Y, in degrees; φ is undefined at the poles. Only exploration shows
  complex amplitudes, in the convention of real nonnegative α with global phase
  omitted (at `|1⟩`, β is chosen real positive). JSON export labels its mode;
  evidence export includes the selected run/marginal, while sandbox export includes
  its initialization and applied operations, with no run association.

### Camera and accessibility

The unit sphere, equator, meridians, signed X/Y/Z axes and vector are projected onto
Canvas 2D with front/back depth cues. Mouse or single-finger drag orbits the camera;
wheel or two-finger pinch zooms. Camera changes never rotate the state or evidence.
**Reset view** affects only the camera.

With the sphere focused, arrow keys orbit, `+`/`−` zoom, and `Home` resets the view.
Equivalent labelled buttons, native selectors/forms, visible focus, text readouts,
live status/error regions and a skip link support keyboard and screen-reader use.
The layout adapts to narrow screens. There is no auto-rotation, easing, or continuous
animation; reduced-motion styles also disable transitions. The numerical readouts
remain available if Canvas rendering is unsupported.

## Blender pipeline

From the repository root, using Python 3.11+:

```powershell
# No Blender or QDK required: regenerate a pending catalog from repository evidence.
python -m viz.build prepare

# Blender 4.2+ must be installed separately. No add-ons, GPU, or cloud credentials.
python -m viz.build render --blender "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"

# Render all active and archived problems, without hand-editing scene files.
python -m viz.build render --all --blender blender

# Select exact IDs (repeat --problem), or keep trial output separate.
python -m viz.build render --problem 16_error_correction --problem 14_materials_discovery --output viz\output\trial

# Plot the second returned measurement, not an inferred physical-qubit ID.
python -m viz.build render --problem 01_hubbard --bloch-bit 1 --output viz\output\second-bit
```

`BLENDER` can also specify the executable. The default output directory is `viz`;
the default rendered problem is `16_error_correction`. `--width`, `--height`,
`--samples`, and `--timeout` control CPU rendering (defaults: 1600, 1000, 16, and
300 seconds **per problem**). Rendering uses Cycles and saves both a PNG poster
and an editable `.blend` scene. No Q# jobs are submitted or rerun.

Both `prepare` and `render` build a **fresh complete catalog**. `prepare` marks every entry
pending, even if older images exist. A selective render marks only the selected
entries rendered; it does not reuse possibly stale images from a previous manifest.
Use `--all` for a fully rendered catalog, or a separate `--output` for experiments.
New assets get unique directories so failed renders cannot accidentally reuse old
output. A failure returns nonzero and leaves the previous manifest and its assets
untouched. Unreferenced render directories are not automatically deleted.

## What the scene actually shows

- **Left panel:** the `logicalQubits`, `physicalQubits`, and `runtime` fields from
  each problem's `circuits/estimate.json`, never the mock `estimates/` artifacts.
  Both bar heights use `log10(1 + qubits)` with labelled ticks and exact counts.
  Runtime is the estimator's nanoseconds, also displayed in milliseconds—not a
  measured wall-clock duration. The source model, entry expression, and build date
  are displayed; full build provenance and source SHA-256 hashes are in the manifest.
- **Upper-right panel:** successful sampled kernel histograms from
  `website/data/simulatorMatrix.json`, read-only. The default selects local simulation.
  Counts must be nonnegative integers summing exactly to shots. Bar widths are
  `count / shots`, not amplitudes. The largest seven outcomes plus an explicit
  **Other** bin retain every shot when there are more than eight outcomes.
  Outcome order is preserved; `Zero`/`One` are shortened to `0`/`1` in the image.
- **Lower-right Bloch-sphere panel:** [measurement-derived Z polarization](#bloch-panel-scientific-semantics),
  not a reconstructed quantum state. A unit-sphere wireframe and signed Z-axis marker
  share the same layout across selected problems. Missing evidence leaves the
  reference sphere visible but has **no marker**, not a marker at zero.
- **Missing evidence stays missing.** An absent estimate or matching histogram
  produces an explicit unavailable label, not synthetic numbers or a zero result.
  Malformed evidence fails the build. No failed run is presented as successful.
- **Evidence is not interchangeable.** The resource estimator's program and the
  sampled hardware kernel are different workloads, potentially from different
  revisions and dates. They are displayed separately, not as a performance comparison.
  The run timestamp is the source snapshot's generation time, not an invented job time.
  Stage metadata comes from `docs/objective-kpis.json`; archival status comes from
  directory discovery.

For another repository-local run snapshot, use `--runs path\to\matrix.json`.
It must use the existing simulator-matrix `records` format, including `problem_id`,
`entry_point`, `execution`, `target_id`, `status`, and
`histogram: {shots, counts: {outcome: count}}`. A record is selected only when its
status is `succeeded` and its target matches. If several match, the last in file order
wins (not necessarily the newest by execution time).

Supported `--target` values are `local-simulator`, `quantinuum.sim.h2-1e`,
`rigetti.sim.qvm`, and `ionq.simulator`. Cloud results remain labelled simulators.
Syntax-checker targets are rejected: their zero outputs are not physics evidence.
Physical-device results and older unversioned emulator-export formats are not
silently inferred or converted.

This is a resource-and-outcome visualization, **not** a circuit/state evolution
animation, a physical qubit layout, or evidence of quantum advantage.

## Bloch panel: scientific semantics

The local simulator producer, `tooling/run_simulator_matrix.py`, records
`str(result)` frequencies. The catalog's local kernels return computational-basis
measurements (`M`, `MResetZ`, or `MResetEachZ`). These are **sampled outcomes**, not
amplitudes, state vectors, phase, or tomography. The panel concerns the returned
measurement at the end of the sampled kernel, not its estimator program, an
intermediate algorithm state, or the qubit's state after reset.

`--bloch-bit N` selects the **zero-based returned measurement index**, default `0`.
In `[One, Zero]`, index `0` is `One`, index `1` is `Zero`. No integer decoding,
endianness reversal, or physical-register mapping is inferred. For example,
Hubbard's returned measurements belong to its phase register, not its system
register; error correction returns the decoded data measurement.

For the selected index, all counts in the **complete, ungrouped histogram** are
marginalized over every other returned measurement:

```text
n0 = sum of counts whose selected result is Zero
n1 = sum of counts whose selected result is One
P(0) = n0 / shots; P(1) = n1 / shots
z = P(0) - P(1) = (n0 - n1) / shots
```

The probabilities shown are empirical sample frequencies, with no confidence
interval computed. Truncated counts must not be renormalized. The report records
the exact integer marginal counts and unrounded numeric values; poster labels
round to three decimal places.

The marker uses normalized **display coordinates `(0, 0, z)`** inside a unit Bloch
sphere. This is a **diagonal-state representation**, corresponding to the
measurement-derived diagonal `diag(P(0), P(1))`, not a claim that the original
state was diagonal. **X and Y remain unavailable (`null` in the report)**; drawing
them as zero is an explicit visualization convention. A balanced histogram puts
the marker at the origin, but does not establish a maximally mixed original state:
coherent states can have the same Z statistics. No purity, amplitudes, phase,
coherence, entanglement, or full Bloch vector are inferred. A wireframe is only a
reference surface; the marker is not normalized to that surface.

Only local `Zero`/`One` scalars and flat `[Zero, One, ...]` Result arrays are
interpreted. Numeric strings, nested structures, aggregated **Other** labels and
unknown encodings produce an explicit unavailable panel. Counts must be finite,
nonnegative integers totaling positive shots; mixed array widths and duplicate
decoded outcomes fail rendering. An index beyond a run's returned width produces
an unavailable panel, allowing batch selection across different widths. Negative
indices are errors. Cloud histograms remain available to the histogram panel, but
their Bloch panel is unavailable because this pipeline has no established
provider-specific basis/result-order contract. Alternative local snapshots must
preserve the producer's computational-basis Result/Result-array contract; changing
the measurement basis cannot be detected from counts alone.

## The contract with the website

The schema is versioned in `manifest.schema.json`. The seam remains:

- **This directory writes** render assets and **`viz/manifest.json`** describing them.
- Workstream D can read the manifest and render it without editing this pipeline.
- Nothing here edits `.tsx`.

`manifest.json` contains `schema_version`, a description, and a `problems` array.
Every entry has a stable problem `id`, title, stage, archival flag, estimate and run
evidence, warnings, `render_status`, and `assets`. Pending entries have no assets.
Rendered entries have a PNG poster with MIME type, dimensions, SHA-256, and accessible
alternative text. Nullable measurements mean unavailable, never zero.
The existing version `1.0` schema is unchanged: Bloch evidence is derived at render
time from `run`, rather than adding redundant state fields. The selected index and
scientific limitations are included in poster alternative text. The local scene
and report retain the selection, marginal evidence, and actual geometry.

Asset `path` values are portable forward-slash paths **relative to the manifest's
directory**, not website URLs or machine-specific absolute paths. Website integration
should copy the referenced poster assets to its own public output, preserve their
relative paths, and prepend its deployment base URL. It should skip image rendering
for pending entries and display the warnings. No website consumer is wired by this
change; `website/` is left untouched.

The manifest references posters only. The sibling `.blend`, `scene.json`,
`render-report.json`, and `render.log` are local authoring/diagnostic artifacts,
not website assets. Large `.blend` files and those intermediate files are ignored by
Git; posters and the manifest can be shared together. Reports record the actual
geometry values, histogram counts, rendered labels, input hash, and image pixel range.
Bloch reports additionally record the actual local marker/segment coordinates,
unit-sphere rings, axes, and the frame's placement, scale, and rotation.

## Validation

Use the repository's existing pytest and jsonschema dependencies:

```powershell
python -m pytest viz\test_pipeline.py -q -p no:cacheprovider
# Include browser artifact, evidence integrity, and Node behavioral checks:
python -m pytest viz\test_pipeline.py viz\test_interactive.py -q -p no:cacheprovider
# Run JavaScript tests directly (Node 18+; built-in runner, no npm install):
node --test viz\test_interactive.js
# Include real-render integration tests when Blender is not on PATH:
$env:BLENDER = "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
python -m pytest viz\test_pipeline.py -q -p no:cacheprovider
```

Without Blender, only the real-render tests skip. Those tests invoke Blender for
active and archived problems, decode/check PNG data, inspect actual scene bar
dimensions and histogram counts, and verify unavailable-data labels. Synthetic
measurement fixtures exercise positive, negative, and zero polarization, unavailable
encodings, and out-of-range indices in real renders. Tests inspect sphere geometry,
marker position, segment endpoints, and scientific labels, not only a nonempty image.
Other checks
cover discovery, source values, schema, invalid data, syntax-checker exclusion,
deterministic preparation, corrupted images, and a zero-exit renderer producing
nothing. Marginal tests distinguish output order, include counts beyond the displayed
histogram tail, and reject fabricated transverse components and incorrect signs.
Test artifacts stay under `viz/output/tests` and are removed afterward.

Interactive checks independently compare signed marginals to full source counts,
cover every catalog entry/returned bit, verify deterministic delivered data and
publication without overwriting manifests, and check local assets/accessibility
hooks. Node tests execute the actual model, Canvas drawing calls and UI event handlers
using a lightweight DOM/Canvas harness—not a real browser engine. They exercise
gates, custom rotations, undo/reset, keyboard/pointer camera controls, selectors and
JSON export, including evidence/sandbox isolation. Regression checks deliberately
inject sign errors, fabricated components and mode-mixing mutations and require
assertion failures; parse/load errors do not count as catching those regressions.
The Node portion skips in pytest if Node is absent. No browser-automation dependency
is added.

The publisher checks PNG dimensions, chunk CRCs and decompression, the saved Blender
file, matching input/report hashes, and nonuniform rendered pixels before publishing.
It also checks that Bloch report evidence matches the selected marginal, that actual
marker/segment coordinates agree with it, and that the limitation labels exist.
It does not treat a zero Blender exit code alone as success.

## Before you push

Adding `.py` here trips the `depgraph-drift` check. Run
`python tooling/depgraph/build_graph.py` and commit `docs/depgraph/*` in the same pull request.

Agent instructions for this directory are in
`.github/instructions/hackathon-workstream-b.instructions.md`; shared repository rules are in
`.github/copilot-instructions.md`.
