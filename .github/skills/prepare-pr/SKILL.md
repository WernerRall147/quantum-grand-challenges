---
name: prepare-pr
description: Prepares a pull request in this repository - the bookkeeping CI checks (dependency map, documented test count), the repository's pull request template filled with real evidence, and a description a reviewer can act on from a phone. Use before opening a pull request or marking it ready for review.
---

# Prepare a pull request

## 1. Bookkeeping CI will check

- `git status` lists only files you meant to change. Stage those files by name, never everything.
- The dependency map is current (rule 4 in `AGENTS.md`).
- If you added or removed tests, the count in `docs/AzureFriday/deck-notes.md` matches
  `python -m pytest --collect-only -q`.
- Docs that describe what you changed are updated in the same pull request.

## 2. Commits

One topic per commit. The message says what changed and why, and the why is usually the failure
it prevents or fixes. Do not mix a refactor into a fix.

## 3. The description

Use `.github/pull_request_template.md` as written: keep its headings, comments and checkboxes in
order and replace the placeholders.

- **What changed, and why:** one or two sentences, then `Fixes #<issue>`.
- **Verification:** every command you ran and what it returned, from the
  [verify-change](../verify-change/SKILL.md) skill. A command without its result does not count.
- **Checkboxes:** tick only what is true. An unticked box with a reason is better than a false
  tick.
- **For the phone:** the first three lines say what changed, how risky it is and what the reviewer
  must look at. Put "Noticed, not changed" and open questions at the end.
- **Blocked:** if you stopped without finishing, the description starts with `Blocked:` and the
  pull request stays a draft.

## 4. After it is open

- Watch the runs, not the summary: `gh run list --branch <branch>`, then
  `gh run view <run-id> --json status,conclusion`.
- Answer every Copilot code review comment: fix it, or reply with the evidence for why not.
  `main` requires every conversation to be resolved before merge.
- Agents do not merge. A human merges once CI and review agree.
