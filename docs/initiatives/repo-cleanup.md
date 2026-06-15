# Initiative: Repo dependency mapping + cleanup

Living plan for mapping all dependencies and safely removing redundant files/tools,
optimized for Claude (Opus 4.8) to search, review, then clean up. Deterministic-first,
with the two core goals protected at all times.

## The two goals we must never break

1. **Solving complex quantum problems** (and ingesting future ones): `problems/**`,
   `libs/common/**`, the Q# projects (`qsharp.json` + `src/Main.qs` + `HardwareKernel.qs`),
   and the `tooling/**` scripts that compile / estimate / submit them.
2. **The Quantum Advantage Evaluator**: `agents/**` (api, orchestrator, classifier,
   code_generator, ...), `knowledge/**`, and the `website/**` UI.

Anything reachable from these is **protected**. Cleanup only ever touches code that is
provably unreachable from a protected entry point AND not on the danger list below.

## How this differs from the attached design doc

`ProjectCleanup/ProjectCleanupDependencyGraph.md` is excellent, but it is written for a
**.NET / Roslyn** repo (20 `.sln` files, `SymbolFinder`, MSBuild). This repo is
**Python + Q# + TypeScript** with ~1183 tracked files. We keep the doc's *principles* and
swap the *tools*:

| Doc (.NET) | Here (Python / Q# / TS) |
| --- | --- |
| Roslyn `SymbolFinder` | Python AST + `grimp` import graph; `vulture` dead-code; `deptry` unused deps |
| MSBuild project graph | `qsharp.json` deps + `open`/`@EntryPoint`; `requirements.txt`; `madge` (TS) |
| 20 `.sln` reachability | 5 workflows + 20 Makefiles + Dockerfile + pytest + `package.json` as roots |
| Cosmos adjacency + Azure AI Search + MCP | Same, but in-repo JSON graph is the deterministic core; Azure is the optional discovery/browse layer |

## Principles (deterministic first)

1. **The static dependency graph is the source of truth** for "what depends on what".
   Delete decisions come from reachability + reference facts, never from embeddings.
2. **Semantic / AI search is for discovery only** (find the area, help a human/Claude
   navigate). It never decides a deletion.
3. **Every deletion is gated** by: (a) not reachable from any entry point, (b) not on the
   danger list, (c) green `build + tests` after removal.
4. **Optimized-for-Claude artifacts**: the mapper emits compact, machine-readable JSON
   (graph + reverse index + candidates-with-evidence) that Claude can load directly,
   instead of rescanning 1183 files each turn.
5. **One cluster at a time, one PR at a time** (main is protected). Re-map after each merge.

## Danger list (never auto-delete; require explicit human OK)

- Q# `@EntryPoint` operations and `Main` operations; `HardwareKernel.qs` (Azure-submittable).
- Anything invoked by a **Makefile**, **GitHub workflow**, **Dockerfile CMD**, **pytest**,
  or **npm script** (these are entry points even if nothing imports them).
- FastAPI routes / `agents/api/main.py` handlers; lazy/dynamic imports (`import_module`,
  `getattr`, `__import__`), DI-style registration, plugin discovery.
- Reflection / config-bound models; JSON-schema-validated data; CLI dispatch (`sys.argv`).
- Published scientific artifacts: `docs/paper/**`, `*.pdf`, `CITATION.cff`, reference data,
  `problems/**/instances/*.yaml`, calibration/estimate JSON that the website or papers cite.
- `problems/archived/**` (kept on purpose as honest negative results) unless explicitly pruned.

## Phase 0 - Quick, obvious wins (low risk, verify then do)

- Untracked local cruft: `full_log.txt`, `job_log.txt` (CI dumps) -> add to `.gitignore`, delete locally.
- Tracked stray: `git_status_output.txt` -> remove from the repo.
- Local-only binaries (3265 `.dll`, 122 `.cs`, `.exe`, `.pdb`) -> confirm `.gitignore` covers them; never commit.
- Root one-offs to assess against the graph: `_run_baselines.py`, `run_inspect.py`.

## Phase 1 - Deterministic dependency mapping (build first, non-destructive)

New generator under `tooling/depgraph/` produces in-repo artifacts under `docs/depgraph/`:

- `graph.json` - nodes (files, Python modules, Q# projects, TS modules) + edges
  (imports, calls where feasible, Makefile-invokes, workflow-invokes, qsharp-deps, npm-deps).
- `reverse-index.json` - "who references X" for fast lookup (precomputed, like the doc's reverse edges).
- `entry-points.json` - the root set (workflows, Makefiles, Dockerfile, pytest, package.json, Q# entry points).
- `cleanup-candidates.json` - files/modules/exports unreachable from any entry point, each with
  evidence (no inbound edges) and risk flags (matches danger list -> excluded/needs-review).

Tooling (deterministic, pinned versions):
- Python: `ast` + `grimp` (module import graph), `vulture` (dead-code candidates, confidence-scored),
  `deptry` (unused/missing deps).
- Q#: parse `qsharp.json` + `open` statements + `@EntryPoint`/`Main` detection (custom small parser).
- TS: `madge` (import graph), `ts-prune` (unused exports), `depcheck` (unused npm deps).
- Cross-language entry-point tracing: parse Makefiles, workflow YAML, Dockerfile, `package.json`
  scripts, `pytest.ini` to find which scripts/modules are invoked as roots.

Output is diffable JSON so we can review the graph in PRs and Claude can read it directly.

## Phase 2 - Azure discovery layer (optional, uses existing quantum-sub resources)

Leverage what already exists (do NOT stand up new infra unless it earns its keep):
- **Azure AI Search (`qgcsearcheval`)**: add a `code_chunks` index (code + docs) for semantic
  "where is X?" discovery for humans and Claude. Discovery only - never a delete signal.
- **Cosmos DB (`qgccosmoseval`)**: optionally mirror `graph.json` + `reverse-index.json` as
  adjacency documents for fast "who uses this" queries and a future MCP tool + website browser.
- **MCP tool layer** (later): expose `find_references`, `get_unused_candidates`,
  `get_impacted`, `search_code_and_docs` so Claude asks for the exact slice it needs.

For a 1183-file repo, the in-repo JSON (Phase 1) is enough to start; Azure adds scale, human
browsing, and a live MCP. Recommend Phase 1 now, wire Azure when we want the browse/MCP UX.

## Phase 3 - Cleanup execution (evidence-gated)

1. Take one candidate cluster from `cleanup-candidates.json` (e.g., duplicate circuit scripts:
   `generate_circuits.py` vs `generate_circuit_diagrams.py` vs `write_circuit_diagrams.py` vs
   `trace_circuits.py` - confirm which are superseded via the graph).
2. Confirm: zero inbound edges from any entry point; no danger-list match.
3. Claude removes only the scoped files; update any references.
4. Run `build + tests` (per-problem `make`, `pytest`, `npm run build`, Q# compile) - must stay green.
5. One PR per cluster; re-map after merge.

Likely candidate areas to investigate (not yet confirmed): superseded migration scripts
(`migrate_to_new_qdk.py` - QDK migration is done), one-off `write_*` generators, duplicate
circuit tooling, stale generated artifacts that are regenerable.

## Phase 4 - Keep it current (so the graph never drifts)

- `tooling/depgraph/build_graph.py` is re-run on demand and in CI.
- CI drift check: a workflow step regenerates the graph and fails if `docs/depgraph/*.json`
  is out of date (so new files/changes are always reflected).
- Rule in `CONTRIBUTING.md` + `.github/copilot-instructions.md`: new files must land in the
  graph (run the mapper), and Claude must consult `cleanup-candidates.json` + the danger list
  before any deletion.

## Status

| Phase | State |
| --- | --- |
| 0 - quick wins | Identified, not yet executed |
| 1 - deterministic mapper | Designed; build next |
| 2 - Azure discovery/MCP | Optional; design ready |
| 3 - cleanup execution | Blocked on Phase 1 graph |
| 4 - keep current | Designed |

## Open decisions (for us to agree before executing)

1. How far to wire Azure now: in-repo JSON only, or also mirror to Search/Cosmos + MCP?
2. Pruning policy for `problems/archived/**` and regenerable artifacts (estimates/plots): keep,
   or move out of version control?
3. Do we want symbol/function-level edges (heavier, less deterministic in Python) or
   file/module-level edges first (lighter, fully deterministic)?
