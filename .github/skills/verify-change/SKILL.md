---
name: verify-change
description: Maps a change in this repository to the checks that prove it works and the evidence to report. Use after editing Python, Q# kernels, docs, workflows, agent files or the website, and before opening or updating a pull request.
---

# Verify a change

Run the checks for what you touched, read what they return, and keep each command with its result
for the pull request. A check you have never seen fail proves little: for new behaviour, write the
test first, run it on the old code and watch it fail, then make it pass.

## Which checks

| You changed | Run |
|---|---|
| `agents/**`, `knowledge/**` | `python -m pytest agents/tests -q`, then `python agents/evaluations/run_eval.py --offline` and `python agents/evaluations/score_narrative.py --offline --strict` |
| `problems/<p>/qsharp/**` | `python tooling/ci_validate_qsharp.py`, the problem's entry point (see `AGENTS.md`), its kernel test `tooling/test_<name>_kernel.py` if one exists, and the [qsharp-kernel](../qsharp-kernel/SKILL.md) skill |
| a `HardwareKernel.qs` | also `python -m pytest tooling/test_hardware_kernels_compile.py -q` |
| `problems/<p>/python/**`, `problems/<p>/instances/**` | `python -m pytest test_baselines.py -q` and `python tooling/reporting/stage_kpis.py --policy tooling/reporting/maturity-policy.json --enforce` |
| `docs/**`, a `README.md`, `CITATION.cff` | `python -m pytest tooling/test_doc_claims.py tooling/test_citation_claims.py tooling/test_architecture_claims.py tooling/test_advantage_claims.py -q`, and the [scientific-claims](../scientific-claims/SKILL.md) skill |
| `tooling/**`, `viz/**` | `python -m pytest tooling viz -q` |
| `website/**` | `cd website && npm ci && npm run build`, `python tooling/reporting/validate_website_data_schema.py`, `python -m pytest tooling/test_website_claims.py -q`, and the [browser-verify](../browser-verify/SKILL.md) skill |
| `Dockerfile`, `.dockerignore`, `.github/workflows/deploy-evaluator-api.yml`, anything the API image copies | `python -m pytest agents/tests/test_container_contents.py -q` |
| `.github/agents/**`, `.github/skills/**`, `.github/hooks/**`, `.github/workflows/**`, `.github/ISSUE_TEMPLATE/**`, `AGENTS.md`, `REVIEW.md` | `python -m pytest tooling/test_agent_harness.py tooling/test_agent_hooks.py -q` |
| added or removed any tracked file (`graph.json` counts them all, Markdown included); moved a file; changed what a `.py`, `.qs`, `.ts` or `.tsx` file imports or runs; changed a `Makefile`, a workflow, `Dockerfile`, `website/package.json`, a `qsharp.json` or `tooling/depgraph/manual_entrypoints.txt` | `git add -N <new files>`, then `python tooling/depgraph/build_graph.py`, and commit `docs/depgraph/` |
| added or removed a test | set the count in `docs/AzureFriday/deck-notes.md` to what `python -m pytest --collect-only -q` reports, then `python -m pytest tooling/test_doc_claims.py -q` |

Finish with the whole suite for each area you touched, not only the file you edited.
`.github/workflows/ci-cd.yml` is the authoritative list of what CI runs.

## Reading results

- Read pytest's summary line (passed, failed, skipped) rather than relying on the exit code, and
  say why anything was skipped.
- A script that exits 0 having written nothing has failed. When a command should produce a file,
  check that the file changed (`git diff --stat`).
- If a check cannot run in your environment, for example `make` on Windows or a production host
  behind the cloud agent's firewall, say so in the pull request instead of implying it passed.

## Evidence format

One line per check, command first:

```text
python -m pytest agents/tests -q  ->  N passed, 0 failed
python tooling/ci_validate_qsharp.py  ->  All 20 problems compiled successfully.
new test test_x failed on main (AssertionError: expected ...), passes on this branch
```
