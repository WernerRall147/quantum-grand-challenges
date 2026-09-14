<!-- Keep this short. Delete sections that do not apply. -->

## What changed, and why

<!-- One or two sentences. If it fixes an issue, write "Fixes #NNN". -->

## Hackathon workstream

<!-- A / B / C / D, or delete this section. Seams are defined in the workstream issues. -->

- [ ] I stayed inside my workstream's directories, or I said below why I had to cross a seam.

## Verification

**State what you ran and what it returned.** Not "tests pass" — the command and its result.

```
<!-- e.g. pytest agents/tests -q  ->  47 passed
     e.g. curl -s .../evaluate -d @case.json  ->  {"verdict":"HPC_PREFERRED"} -->
```

- [ ] I asserted **behaviour**, not shape. I called the endpoint / ran the build / executed the query, rather than reading a schema, a Dockerfile, or a field's presence.
- [ ] Any **new check**, I watched fail before trusting it: I broke the thing deliberately, saw it go red, then restored. A check that has never failed is not evidence.
- [ ] I confirmed the **returned value**, not just a zero exit code. A process that exits 0 having written nothing has still failed.

<!-- These three are not ceremony. Four checks in this repo passed for months while the
     thing they guarded was broken. See `.github/copilot-instructions.md`,
     "A green check is not evidence". -->

## Required before merge

- [ ] **Dependency graph regenerated** — if this PR touches any `.py`, `.qs`, `.ts`, `.tsx`, `Makefile`, `Dockerfile`, `.github/workflows/**`, or `website/package.json`:
      run `python tooling/depgraph/build_graph.py` and commit `docs/depgraph/*` **in this PR**.
      Otherwise `depgraph-drift` fails. This is the most common red build here.
- [ ] **Claims are backed.** Any number, file path, `[x]`, or file tree I wrote is true as of this commit.
      Counts go stale — prefer a check to a sentence. See `.github/instructions/documentation.instructions.md`.
- [ ] **Conversations resolved.** `main` requires resolution before merge, even though approvals required is 0.

## Deleting code?

- [ ] I checked `docs/depgraph/cleanup-candidates.json` and the danger list in `docs/initiatives/repo-cleanup.md`.

---

<!-- Approvals required is 0. CI is the gate; self-merge when green.
     Request review when you want a second pair of eyes, not because the branch demands one. -->
