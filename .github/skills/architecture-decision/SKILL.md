---
name: architecture-decision
description: How to make and record an architecture decision in this repository as an ADR in docs/adr/ - when one is needed, the template, weighing options for reliability, security, cost and operations, and checkable success criteria. Use for cross-cutting changes, new Azure resources, changed contracts or reversed decisions.
---

# Record an architecture decision

An ADR keeps the reasoning next to the code, so the next person, or agent, does not re-argue a
settled question or silently undo it. Adapted from the ADR practice in
[niksacdev/engineering-team-agents](https://github.com/niksacdev/engineering-team-agents) (MIT
licence).

## When to write one

- A change crosses components or changes a contract: an API response,
  `problems/reference_index.json`, the visualisation manifest, estimate file formats.
- An Azure resource is added, removed or resized, or running cost changes.
- A decision is reversed. Write a new ADR that supersedes the old one; never edit an accepted ADR
  except to mark it superseded.

## Where and how

- File: `docs/adr/NNNN-short-title.md`, numbered after the highest existing one.
- Status starts as **Proposed**. It becomes **Accepted** when a human merges it, or **Rejected**.
  Later it may be **Superseded by** another ADR.

```markdown
# ADR-NNNN: Title

Date: YYYY-MM-DD (from the system clock)
Status: Proposed
Deciders: who decides

## Context
What exists now, verified against the code, and the problem.

## Decision drivers
What must be true; what may not change.

## Options considered
1. Doing nothing.
2. Option A, with its trade-offs.
3. Option B, with its trade-offs.

## Decision
The chosen option and why it beats the others on the drivers.

## Consequences
What gets better, what gets worse, and what follow-up work this creates.

## How we will know
Success criteria a command, a test or a metric can check, and when to check them.

## Links
Issues, pull requests, sources and related ADRs.
```

## Weighing the options

For each option, consider reliability, security, cost, operational load and performance. State
the trade-off rather than declaring a winner on every axis. Ground it in what runs here:

- The evaluator API is a container on Azure Container Apps, built and deployed by
  `.github/workflows/deploy-evaluator-api.yml`.
- Production model calls go through the Azure AI Foundry model-router.
- The website is a static export on GitHub Pages.
- Agents run in GitHub Actions sandboxes configured by
  `.github/workflows/copilot-setup-steps.yml`.

Check each fact against the code before relying on it. The ones that have been wrong before are
listed in `.github/instructions/documentation.instructions.md`.
