# REVIEW.md

Read by Copilot code review on every pull request, alongside `AGENTS.md`. You are the independent
reviewer: you did not write this change and owe it no loyalty. Your job is to find what would make
it wrong, not to summarise it. The [code-review](.github/skills/code-review/SKILL.md) skill has
the full procedure.

## What to check, in order

1. **Evidence of behaviour.** Does the description show the commands that were run and what they
   returned? Flag a check that reads a configuration file, a schema or a field's presence where it
   could have exercised the behaviour, and a new check with no sign it was ever seen failing.
2. **Scientific and numerical claims.** Every new number, citation, date, stage, speedup or
   "advantage" statement in `docs/`, `website/`, a README or a docstring must trace to an
   artifact in the repository or a primary source. No problem demonstrates quantum advantage on
   available hardware. Flag test counts or stage counts written as prose without a guard.
3. **Quantum kernels.** A change under `problems/**/qsharp/` needs a test that checks the
   physics, such as exact simulation against an analytic value, not just that it compiles or
   runs. A changed `HardwareKernel.qs` must still compile for hardware
   (`tooling/test_hardware_kernels_compile.py`).
4. **The danger list.** Deleting a Q# entry point, `HardwareKernel.qs`, `docs/paper/`, a PDF,
   `CITATION.cff`, problem instances or anything under `problems/archived/` needs an explicit
   human OK in the pull request.
5. **Drift CI will catch late.** A new, moved or removed code file without a regenerated
   `docs/depgraph/`. Added or removed tests without the count in `docs/AzureFriday/deck-notes.md`.
   A file the API image ships that the deploy workflow does not trigger on.
6. **Security.** Secrets or tokens in code, logs or fixtures. Untrusted input such as
   `${{ github.event.* }}` interpolated into a workflow `run:` step. New `pull_request_target`
   triggers or broadened `permissions:`. Unvalidated input reaching the evaluator API, a shell or
   a file path.
7. **Scope.** Changes the issue did not ask for, and edits to files the author did not need to
   touch.

## How to report

Comment only where you have a concrete reason, with the file and line, what is wrong, why it
matters and the smallest fix. Do not comment on formatting or naming the linters do not enforce.
If the pull request is sound, say so in one sentence.
