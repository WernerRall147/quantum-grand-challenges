---
name: code-review
description: Procedure for reviewing a pull request or diff in this repository as an independent reviewer - reproduce the evidence, exercise the behaviour, apply REVIEW.md and the security, reliability, operations, accessibility and responsible-AI lenses, and report concrete findings. Use for pull request review and for the Verifier agent.
---

# Review a change

You are checking whether the change does what it claims and breaks nothing else. A review that
only restates the diff has not started. The checklist of what to look for is `REVIEW.md`; this
skill is how to work through it.

## 1. Context

- The pull request description and the linked issue's acceptance criteria.
- The diff: `gh pr diff <n>` locally, or the GitHub MCP pull-request tools.
- For each changed file, what depends on it: `docs/depgraph/reverse-index.json`.

## 2. Reproduce, then exercise

- Re-run the commands the description reports, and compare the results.
- For each acceptance criterion, make the observation that proves it.
- For a new test, confirm it fails without the change. Use a separate worktree of the base branch
  rather than editing the branch under review.

## 3. Lenses

Adapted from the specialist reviewers in
[niksacdev/engineering-team-agents](https://github.com/niksacdev/engineering-team-agents) (MIT
licence), cut down to what this repository runs.

- **Security:** secrets in code, logs or fixtures. Workflow injection through `${{ github.event.* }}`
  in `run:`. New `pull_request_target` triggers or broader `permissions:`. Input to the evaluator
  API reaching a shell, a file path or a prompt without validation. Dependencies added without a
  pinned version.
- **Reliability:** errors that are caught and turned into an empty success. The evaluator once
  answered HTTP 200 with empty Q# while generation was broken, because an exception became `""`.
  Also timeouts and retries on network calls, and behaviour when Azure or a model is unavailable.
- **Operations:** files the API image needs or ships (`agents/tests/test_container_contents.py`),
  deploy triggers, cost of new Azure calls, scheduled workflows that can fail silently.
- **Accessibility, for `website/`:** headings in order, text alternatives for images and charts,
  keyboard reachability, colour that is not the only carrier of meaning.
- **Responsible AI, for `agents/`:** verdicts worded with the confidence the evidence supports,
  model output labelled as such, no route by which a prompt turns into an advantage claim.
- **Science:** any number or comparison goes through the
  [scientific-claims](../scientific-claims/SKILL.md) skill.

## 4. Report

- **Verdict:** ready, changes needed, or blocked.
- **Findings,** most serious first. Give the file and line, what is wrong, the evidence, and the
  smallest fix. Leave out anything you cannot tie to a concrete failure.
- **What you ran:** each command and what it returned.
