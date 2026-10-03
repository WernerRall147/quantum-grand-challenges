---
name: fix-ci
description: Diagnoses and fixes a failing GitHub Actions run in this repository - find the failing step, reproduce it locally with the matching command, fix the cause and verify. Use when CI/CD, the dependency-graph drift check or another workflow fails on a pull request.
---

# Fix a failing workflow run

## 1. Find the failure

- **Locally:** `gh run list --branch <branch> --limit 5`, then `gh run view <run-id> --log-failed`.
  Query the run itself; `gh pr checks` can show a stale status.
- **In the cloud agent:** use the GitHub MCP server's Actions tools to list the runs for your
  branch and read the failed job's log.
- On a pull request opened by an agent, workflows wait for a human to approve them. "Action
  required" means waiting, not failing.

## 2. Reproduce it with the matching command

| Workflow and step | Command |
|---|---|
| CI/CD: Validate workflow YAML | `python -m pytest tooling/test_agent_harness.py -q` runs the same checks |
| CI/CD: Validate Q# compilation | `python tooling/ci_validate_qsharp.py` |
| CI/CD: Run Q# entry points | `python tooling/run_all_qsharp.py` |
| CI/CD: Validate JSON schemas | `python tooling/ci_validate_schema.py` |
| CI/CD: Run pytest baseline tests | `python -m pytest test_baselines.py -q` |
| CI/CD: Enforce maturity contract | `python tooling/reporting/stage_kpis.py --policy tooling/reporting/maturity-policy.json --enforce` |
| CI/CD: QAOA estimator smoke | `cd problems/archived/05_qaoa_maxcut && make estimate-all` (needs `make`) |
| CI/CD: Verify QAOA evidence | the three `validate_*.py` scripts in `problems/archived/05_qaoa_maxcut/python/` |
| CI/CD: Evaluator smoke tests | `python -m pytest agents/tests -q` |
| CI/CD: Claim, evidence and visualisation guards | `python -m pytest tooling viz -q` |
| CI/CD: Router and narrative evaluation | `python agents/evaluations/run_eval.py --offline`, `python agents/evaluations/score_narrative.py --offline --strict` |
| CI/CD: Verify matrix freshness and website schema | `python tooling/reporting/validate_website_data_schema.py`, `python tooling/reporting/check_homepage_stats.py` |
| Dependency Graph Drift Check | `python tooling/depgraph/build_graph.py`, then `git diff --stat -- docs/depgraph` |
| Copilot Setup Steps | the failing install command; it must match CI's install step |
| Azure Secret Hygiene | read the log. A leaked secret must be removed and rotated, not hidden |

## 3. The usual causes here

- **Dependency map drift:** a new file regenerated before `git add -N`, or not regenerated at all.
- **Documented counts:** `tooling/test_doc_claims.py` names the file and line whose test count or
  stage count no longer matches.
- **Container contents and deploy trigger:** `agents/tests/test_container_contents.py` names the
  file the image needs, or ships without a deploy trigger.
- **QDK behaviour:** `qdk` is pinned to 1.31.0; see the
  [qsharp-kernel](../qsharp-kernel/SKILL.md) skill for its known quirks.

## 4. Fix the cause, not the check

Do not skip, mark expected-to-fail, loosen or delete a failing check to get a green run. If the
check itself is wrong, fix it and show it failing on the bad case and passing on the good one.
After the fix, re-run the matching command and report what it returned.
