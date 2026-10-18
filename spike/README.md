# Lean measurement spike (not for merging)

This branch exists to measure, on GitHub-hosted `ubuntu-latest` runners, what each option in
ADR 0002 (#293) costs: Lean 4 without Mathlib, Lean 4 with Mathlib's prebuilt cache, and Z3
called from Python. Each variant checks the same statement where it can: majority decoding of a
distance-3 repetition code fails exactly when at least two of the three bits flip.

`.github/workflows/lean-measure.yml` runs on every push to `spike/lean-ci-measure` and prints
`key=value` timings and sizes to the job log and summary. The first run is cold; a re-run with the
cache restored is warm. ADR 0002 records the numbers and links the runs.

The branch is not opened as a pull request and can be deleted once ADR 0002 has merged.
