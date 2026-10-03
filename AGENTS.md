# AGENTS.md

How to work in this repository, for any coding agent: Copilot cloud agent, Copilot in VS Code
and the CLI, Copilot code review, Claude and Codex. This file is the canonical guide; tool-specific
files (`.github/copilot-instructions.md`, `CLAUDE.md`, `REVIEW.md`) stay thin and point here.
Trust it first, and search only when it is incomplete or wrong. If it is wrong, fix it in the
same pull request.

## What this repository is

Quantum Grand Challenges works through twenty hard scientific problems with Microsoft Q#, Python
baselines and Azure resource estimates, and publishes the results as a methodology paper
(`docs/paper/`), a website (`website/`, GitHub Pages) and a Quantum Advantage Evaluator API
(`agents/`, Azure Container Apps). Its value is that every claim is checked. No problem
demonstrates quantum advantage on available hardware, and nothing here may say otherwise.

| Path | What lives there |
|---|---|
| `problems/NN_*/` | Active problems: `qsharp/` (`qsharp.json`, `src/Main.qs`, `HardwareKernel.qs`), `python/`, `instances/`, `estimates/`, `circuits/`, `Makefile` |
| `problems/archived/` | Problems kept on purpose as honest negative results |
| `agents/` | The evaluator: FastAPI app (`agents/api/main.py`), orchestrator, classifier, code generator, evaluations, tests |
| `knowledge/` | Knowledge-base client, ingesters and data the evaluator reads |
| `tooling/` | Q# runners, estimators, reporting, the dependency map, and the guard tests (`tooling/test_*.py`) |
| `website/` | Next.js static export, deployed by `.github/workflows/deploy-website.yml` |
| `viz/` | Blender visualisation pipeline |
| `libs/` | Vendored QDK samples and standard-library index used by code generation |
| `docs/` | Paper, `docs/architecture.md`, `docs/objective-kpis.json`, ADRs in `docs/adr/`, the dependency map in `docs/depgraph/` |
| `Dockerfile` | The evaluator API image, deployed by `.github/workflows/deploy-evaluator-api.yml` |

## Environment

Python 3.11, the `qdk` package pinned to 1.31.0 (no .NET), Node 18 for the website. The cloud
agent gets all of this from `.github/workflows/copilot-setup-steps.yml`, which installs exactly
what CI installs:

```bash
pip install numpy scipy matplotlib pandas pytest jsonschema pyyaml qdk==1.31.0 azure-identity openai azure-search-documents==11.6.0
cd website && npm ci
```

Import Q# from Python as `from qdk import qsharp`. On Windows, set `PYTHONIOENCODING=utf-8`
before running scripts that print symbols. `make` targets exist per problem, but Windows usually
has no `make`; the Python commands below work everywhere.

## Commands

Measured on a developer laptop; CI runners have been somewhat faster.

| What | Command | Time |
|---|---|---|
| Compile every Q# project | `python tooling/ci_validate_qsharp.py` | ~5 s |
| Run every Q# entry point | `python tooling/run_all_qsharp.py` | ~1 min |
| Compile or run one problem | `python -c "from qdk import qsharp; qsharp.init(project_root='problems/01_hubbard/qsharp'); print(qsharp.run('Main.RunTwoSiteHubbardAnalysis()', 1))"` | seconds |
| Evaluator tests | `python -m pytest agents/tests -q` | ~35 s |
| Claim, kernel and visualisation guards | `python -m pytest tooling viz -q` | ~2.5 min |
| Problem baselines | `python -m pytest test_baselines.py -q` | ~10 s |
| Everything pytest collects | `python -m pytest -q` | several minutes |
| Offline evaluator checks | `python agents/evaluations/run_eval.py --offline` and `python agents/evaluations/score_narrative.py --offline --strict` | < 1 s |
| Schemas and maturity contract | `python tooling/ci_validate_schema.py` and `python tooling/reporting/stage_kpis.py --policy tooling/reporting/maturity-policy.json --enforce` | ~2 s each |
| Dependency map | `python tooling/depgraph/build_graph.py` | seconds |
| Website | `cd website && npm ci && npm run build` (static export to `website/out/`) | ~3 min |

`.github/workflows/ci-cd.yml` is the authoritative list of what CI runs. The
[verify-change](.github/skills/verify-change/SKILL.md) skill maps a change to the checks it needs.

## Rules

1. **A green check is not evidence.** Assert behaviour, not shape: call the endpoint, run the
   build, execute the query. Watch a new check fail before you trust it. Only the returned value
   counts, not the exit code. Query a workflow run, not the pull-request summary. The history
   behind this rule is in `.github/copilot-instructions.md`.
2. **Every number, tick, path and file tree in prose is a claim.** Follow
   `.github/instructions/documentation.instructions.md`: one file owns each fact, and counts that
   go stale are either guarded by a test or left out. When you add or remove tests, update the
   count in `docs/AzureFriday/deck-notes.md`; `tooling/test_doc_claims.py` fails until you do.
3. **Scientific claims need evidence.** A number traces to an artifact in this repository or to a
   primary source. Read today's date from the system, never guess it. See the
   [scientific-claims](.github/skills/scientific-claims/SKILL.md) skill.
4. **Regenerate the dependency map** after adding, moving or removing any `.py`, `.qs`, `.ts` or
   `.tsx` file, a `Makefile`, a workflow, the `Dockerfile` or `website/package.json`: run
   `python tooling/depgraph/build_graph.py` (after `git add -N` on new files) and commit
   `docs/depgraph/`. The depgraph-drift workflow fails otherwise.
5. **The danger list is never deleted without an explicit human OK:** Q# entry points and
   `HardwareKernel.qs`, anything a Makefile, workflow, Dockerfile, pytest or npm script runs,
   `docs/paper/`, PDFs, `CITATION.cff`, problem instances, and `problems/archived/`. The full list
   is in `docs/initiatives/repo-cleanup.md`; consult `docs/depgraph/cleanup-candidates.json` first.
   `.github/hooks/agent-gates.json` denies deleting them, reading the entry points from
   `docs/depgraph/entry-points.json`.
6. **Leave other people's work alone.** Stage only the files you changed. Never push to `main`
   (it changes only through reviewed pull requests) and never force-push. On a developer's
   machine never run `git clean -f`, `git reset --hard` or a whole-tree checkout or restore.
   `.github/hooks/agent-gates.json` denies these.
7. **Deploys follow merges, not agents.** Merging to `main` deploys the website and, for files the
   image ships, the API. Do not run deploy workflows from an agent session. Never commit secrets.
8. **Style.** Plain language, no em dashes, comments only where code needs explaining.

## Definition of done

- The acceptance criteria in the issue are met, and the pull request shows the evidence: each
  command you ran and what it returned.
- The checks for what you touched pass locally, and new checks were watched failing first.
- Docs, the dependency map and the documented test count are current.
- The diff contains nothing unrelated, and every claim you added is backed.

When the agent stops, `.github/hooks/agent-gates.json` runs the cheap checks CI would fail on
(dependency map, Python syntax, workflow YAML, Q# compilation, documented test counts) and sends
the agent back once if one fails.

## How work flows

GitHub is the control plane: an issue is the specification, a pull request is the result, and CI
plus an independent review decide whether it is done. The playbook is
`docs/agentic-delivery.md`; the decision and its sources are in
`docs/adr/0001-agentic-delivery-loop.md`.

1. **Issue.** Use the Agent Task form (`.github/ISSUE_TEMPLATE/agent-task.yml`): objective,
   acceptance criteria, non-goals, verification, risk.
2. **Agent.** Assign it to Copilot and pick an agent, from GitHub Mobile, GitHub.com, VS Code or
   the CLI.
3. **Build and verify.** The agent plans, implements and runs the checks for what it changed.
4. **Review.** CI and Copilot code review (`REVIEW.md`) check the pull request in a fresh context.
   Workflows on an agent's pull request wait for a human to approve the run.
5. **Merge.** A human merges. Deploys follow, and the
   [deploy-verify](.github/skills/deploy-verify/SKILL.md) skill checks production.

### The team

| Agent | Use it to | Edits files |
|---|---|---|
| [Planner](.github/agents/planner.agent.md) | turn a vague issue into an agent-ready plan with acceptance criteria | no |
| [Builder](.github/agents/builder.agent.md) | implement an issue end to end; the default choice | yes |
| [Verifier](.github/agents/verifier.agent.md) | try to falsify a change in a fresh context before merge | no |
| [Maintainer](.github/agents/maintainer.agent.md) | clean up stale claims, dead code and drift | yes |
| [Science Reviewer](.github/agents/science-reviewer.agent.md) | audit and correct scientific claims in the paper, docs and site | yes |
| [Architect](.github/agents/architect.agent.md) | design cross-cutting changes and record them as ADRs | docs only |

### Skills

Loaded on demand by every agent, and by Copilot code review when relevant:
[verify-change](.github/skills/verify-change/SKILL.md),
[fix-ci](.github/skills/fix-ci/SKILL.md),
[prepare-pr](.github/skills/prepare-pr/SKILL.md),
[qsharp-kernel](.github/skills/qsharp-kernel/SKILL.md),
[scientific-claims](.github/skills/scientific-claims/SKILL.md),
[code-review](.github/skills/code-review/SKILL.md),
[architecture-decision](.github/skills/architecture-decision/SKILL.md),
[browser-verify](.github/skills/browser-verify/SKILL.md),
[deploy-verify](.github/skills/deploy-verify/SKILL.md).

### When you are stuck

Do not loop. If the same check fails twice for the same reason, stop and diagnose from scratch:
reread the failure, reproduce it in isolation and question the plan rather than the last edit. If
it still fails, stop. Leave the pull request as a draft, start its description with `Blocked:`,
and give the failing command, its output and what you tried. A clear stop is a good outcome; a
green-looking pull request that hides a failure is the worst one.
