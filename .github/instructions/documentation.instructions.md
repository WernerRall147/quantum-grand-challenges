---
applyTo: "**/*.md"
description: "Rules for editing documentation in this repo, derived from claims that turned out to be false."
---

# Editing documentation here

Four false claims shipped in one week, all the same shape: a document asserting something
the code contradicted. `CITATION.cff` said all 20 problems reached Stage C (it is 9 at C, <!-- not-a-claim -->
8 at B, 3 at D). `architecture.md` ticked two MCP servers as built while saying "Not
built" 150 lines above, and its directory tree named seven files that were never written.
A quotable table said 116 tests when there were 214, and 214 when there were 243. <!-- historical -->

Every one was fixed by editing prose, which is why they kept recurring. Prose does not
fail a build.

## Before you write a number, a tick or a path

**A file tree is a claim.** Every filename in one must exist. `tooling/test_architecture_claims.py`
enforces this. Reading the tree by eye found 2 of 7 fictional files; the test found all 7.

**A `[x]` is a claim.** If the thing was dropped, say so and why - Phase 2 of
`architecture.md` does this well: *"dropped, not built. Both were YAML that nothing
loaded."* Do not leave a tick next to something that does not exist.

**A count is a claim with a short shelf life.** Test counts, commit counts and latency
medians go stale on the next commit. Either omit them, or accept that
`tooling/test_doc_claims.py` will fail until you update them. If you are writing *about* a
past count rather than stating the current one, end the line with `<!-- historical -->`.

## Do not state the same fact in two files

The demo beat sheet lived in both `README.md` and `storyboard.md` and drifted into
describing **two different demos** - one opening live with FeMoco, the other with
portfolio optimisation. Nobody noticed until both were read side by side.

One file owns each fact; everything else links to it.

| Fact | Owner |
|---|---|
| Demo beats and clock times | `docs/AzureFriday/script.md` |
| Quotable verified numbers | `docs/AzureFriday/deck-notes.md` |
| What was submitted to the producers | `docs/AzureFriday/storyboard.md` section 0 |
| Operational runbook, failure modes | `docs/AzureFriday/README.md` |
| Maturity stage distribution | `docs/objective-kpis.json` |

## Prefer a check to a correction

If you find a false claim, ask whether it can be made checkable before you fix the words.
Two exist already and are cheap to extend:

- `tooling/test_citation_claims.py` - the abstract against `docs/objective-kpis.json`
- `tooling/test_architecture_claims.py` - the file tree against the filesystem
- `tooling/test_doc_claims.py` - test counts against what pytest collects

## Archival documents are exempt

`docs/Hackathon2026/`, `docs/AI_Expanations/`, `docs/planning/` and dated milestone notes
record what was true at a moment. Do not update them to satisfy a check - add the prefix
to `ARCHIVAL` in `tooling/test_doc_claims.py` instead.

## Things that are currently true and easy to get wrong

- Production calls the **Azure AI Foundry model-router**, not a Foundry agent.
  `QGC_USE_AGENT=0`; the agent is provisioned but not in the request path.
- There is **no MCP server in this repo**. The Foundry agent consumes Microsoft's public
  Learn MCP server.
- The API runs on **Azure Container Apps**, not Container Instances.
- **Cosmos DB is retired in code** (#156) but the account is still provisioned. Retiring
  code is not de-provisioning a resource.
- **No problem demonstrates quantum advantage** on available hardware. 11 of 20 were
  downgraded on I/O or quadratic-only speedups.
