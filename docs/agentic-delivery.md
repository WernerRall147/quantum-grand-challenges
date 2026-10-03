# Agentic delivery

How to run this repository's software delivery with Copilot agents, from a phone, a laptop or a
browser. The rules every agent follows are in [AGENTS.md](../AGENTS.md); why the process looks
like this is in [ADR-0001](adr/0001-agentic-delivery-loop.md).

## The loop

```text
idea -> Agent Task issue -> agent: plan -> change -> verify --> draft pull request
                                            ^            |
                                            +-- fails ---+   (stop hook, local checks)

draft pull request -> you approve the workflow runs -> CI + Copilot code review (REVIEW.md)
                   -> findings? -> "@copilot <fix this>" -> back into the loop
                   -> you merge -> deploy workflows -> production checks (deploy-verify skill)
```

GitHub holds the state: the issue is the specification, the branch and pull request are the
work, CI and the review are the judgement. Agents are disposable. If a session goes wrong, close
it and start another from the same issue; nothing is lost.

## From your phone (GitHub Mobile)

1. **Write the task.** In the repository, open a new issue with the **Agent task** form. Fill in
   the objective and acceptance criteria; the agent stops when those hold.
2. **Start an agent.** Two ways:
   - **To pick the team member and model:** tap the Copilot icon, then **Agents**, then
     **New Session**. Choose this repository, write a prompt such as `Implement #123`, pick a
     custom agent (Builder for most work), pick the model and reasoning level, and submit.
   - **Quickest:** on the issue, use **Assign an Agent**, or add Copilot under Assignees. This
     runs the default Copilot agent, which follows the same `AGENTS.md`, skills, hooks and
     environment, but not a specialist's instructions.
3. **Track it** under **Agent Tasks** in the Agents section of the Home page.
4. **Review.** Workflows on an agent's pull request wait for your approval; approve them, then
   read the first lines of the description and Copilot's review. Comment `@copilot` with what to
   change, or merge. You are the only one who merges.

## From VS Code

- Pick an agent in the Chat view's agent picker. The handoff buttons chain them: Planner "Build
  this plan" goes to the Builder, the Builder's "Verify independently" goes to the Verifier, and
  the Verifier's "Fix the findings" goes back. Each handoff starts the next agent with a prompt you
  can edit first.
- The same agents can run in the cloud: choose **Cloud** in the Chat view's **Session Target**
  control to hand a task to Copilot cloud agent and close the laptop.
- Hooks follow the session target. **Copilot** sessions use the same hook implementation as
  Copilot CLI and read `.github/hooks/`; hook support in the **Local** harness is in preview.

## From a terminal

- **Copilot CLI:** run `copilot` in the repository and pick an agent with `/agent`. The hooks in
  `.github/hooks/` run on your machine.
- **Start a cloud session:** `gh agent-task create "Implement #123" --custom-agent builder --follow`
  (GitHub CLI 2.80 or later), then `gh agent-task list` to see your sessions.

## From a browser (Codespaces)

Open the repository in a codespace. The dev container (`.devcontainer/`) installs what CI and
the cloud agent install, plus the Q# and Python extensions, so the agents, skills and commands in
`AGENTS.md` work the same way there.

## Which agent

| Situation | Agent |
|---|---|
| A clear issue with acceptance criteria | Builder |
| An idea, or a large or risky change | Planner, then Builder |
| Several components, an Azure resource or a contract changes | Architect, then Planner |
| A pull request that matters, beyond what CI and Copilot review check | Verifier, in a fresh session |
| The paper, a README or the website states a result | Science Reviewer |
| Drift, stale claims, failing scheduled checks | Maintainer |

## Models and effort

Choose the model when you start the session. A starting policy:

- **Builder:** Claude Opus 5.5 at medium reasoning. Raise it to high for hard debugging, and only
  after a repeated failure.
- **Planner, Architect, Science Reviewer:** high reasoning; their mistakes are expensive later.
- **Verifier:** a different model family from the one that wrote the change, so the review is
  independent in model as well as context.
- **Mechanical fixes,** such as a stale count or a lint failure: low or medium, or Auto.

## What enforces what

| Rule | Enforced by |
|---|---|
| No force pushes, no pushes to `main`, no `git clean -f`, no whole-tree discards on a developer machine | `.github/hooks/agent-gates.json`, and branch protection on `main` |
| No deleting the danger list's entry points (as `docs/depgraph/entry-points.json` records them) or published artifacts, including through `bash -c`, `eval` or `$(...)` | `.github/hooks/agent-gates.json` |
| An edited file still parses | the post-tool hook, immediately after the edit |
| Dependency map, Python syntax, workflow YAML, Q# compilation, documented test counts | the stop hook, once per stop, then CI |
| The agent's environment matches CI | `.github/workflows/copilot-setup-steps.yml`, checked by `tooling/test_agent_harness.py` |
| A codespace builds and can run the project | `.github/workflows/devcontainer-check.yml`, on every change to `.devcontainer/` |
| Agent, skill, hook and form files are well formed; their links and paths resolve | `tooling/test_agent_harness.py` |
| The hooks deny and allow what they should | `tooling/test_agent_hooks.py` |
| Independent review | Copilot code review with `REVIEW.md`, and CI |
| Merging | a person; `main` requires a pull request with every conversation resolved |

The hooks guard against accidents; they are not a sandbox, and a determined command can get round
them. The boundary is branch protection, review and a person merging.

## Repository settings outside git

- **Copilot cloud agent** is enabled for the repository.
- **Ruleset "Copilot code review"** asks Copilot to review every pull request into `main`, and to
  re-review new pushes. Drafts are not reviewed until they are marked ready.
- **Workflow approval** for agents' pull requests stays on (GitHub's default). Turn it off only
  once no workflow can be changed by an untrusted pull request to reach secrets.
- **Label `agent-task`** is applied by the issue form.
- **Cloud agent firewall:** the default allow list. Production hosts are not reachable from an
  agent session; the [deploy-verify](../.github/skills/deploy-verify/SKILL.md) skill says what
  to do instead.

## Not built yet, on purpose

- **Starting an agent automatically when an issue is created.** Copilot automations are only
  available to private and internal repositories, and this one is public. A workflow could assign
  Copilot through the REST API when a label is added, but it needs a personal access token stored
  as a secret, so it waits for the owner's decision.
- **Several agents on one change at once.** Worth it when tasks split cleanly, such as the
  website and a kernel. Parallel agents on shared code collide.
- **Handoffs on GitHub.** The cloud agent ignores `handoffs`, so on GitHub, CI and review are the
  handoff.
