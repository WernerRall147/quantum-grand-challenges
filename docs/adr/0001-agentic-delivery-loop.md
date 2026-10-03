# ADR-0001: Issue-driven agentic delivery with a small specialist team

Date: 2026-10-03
Status: Proposed. Accepted when merged.
Deciders: Werner Rall (repository owner)

## Context

Until now, work here was done by a person and one agent in a local session. The owner wants to
start, follow and review work from GitHub Mobile, VS Code or a terminal, with Copilot's cloud and
local agents doing the implementation.

The repository already had strong guards: CI that runs the claim and kernel tests, a dependency
map with a drift check, a pull request template that asks for evidence, and the rule that a
green check is not evidence. It had no agent infrastructure: no `AGENTS.md`, custom agents,
skills, hooks or issue forms, and no `copilot-setup-steps.yml`. Copilot cloud agent had opened
pull requests here, but each time it had to work out on its own how to install and test the
project. The one instruction file, `.github/copilot-instructions.md`, was long, and parts of it
had gone stale, such as a status section that singled out problems which have since been
archived.

Two methodologies were on the table:

- **A trends review the owner commissioned in October 2026** of agentic delivery practice:
  Anthropic's long-running harnesses and planner, builder and evaluator loop; the Ralph loop;
  OpenAI's harness engineering and Symphony; SWE-agent's agent-computer interface; and GitHub's
  and VS Code's customization features. It recommends an issue-driven loop. GitHub holds the
  state, there are a few roles, skills hold the procedures, hooks enforce rules
  deterministically, CI is the objective function, an independent reviewer works in a fresh
  context, failures escalate instead of looping, and a human merges.
- **[niksacdev/engineering-team-agents](https://github.com/niksacdev/engineering-team-agents)**
  (MIT licence, copyright 2025 Nik Sachdeva), which the owner had used on another project. It
  provides specialist role agents: product manager, UX designer, architect, security reviewer,
  responsible-AI reviewer, DevOps specialist, technical writer and a sync coordinator. It adds a
  question-first workflow and persistent documentation, such as ADRs and review reports, under
  `docs/`.

## Decision drivers

- The same rules on every surface, so an agent on a phone-started session behaves like one in
  VS Code.
- Scientific accuracy is the product. Correctness has to be checked by something other than the
  agent that wrote the change.
- The repository is public. Copilot automations are only available to private and internal
  repositories, and workflows on an agent's pull request wait for human approval.
- Few moving parts, and nothing that can stop working without anyone noticing.

## Options considered

1. **Do nothing.** The default cloud agent with the existing instructions. It works, but every
   session rediscovers the environment, and nothing checks its work before CI.
2. **Adopt engineering-team-agents as it is.** It brings strong specialist lenses and an ADR
   habit. But the agents are generic, written for enterprise web applications. Their handoffs are
   conversational, and the cloud agent ignores those. Their review reports would duplicate
   pull-request reviews and drift from them. And it has no environment or verification loop.
3. **Adopt the review's loop alone.** It works from a phone and puts deterministic pressure on
   the agent, but it has no domain specialist. Here the main risk is scientific, not code
   quality.
4. **A hybrid (chosen).** The review's loop is the backbone. From engineering-team-agents come
   the specialists this repository needs as agents: a Science Reviewer for its main risk and an
   Architect for cross-cutting design, with ADRs in `docs/adr/`. Its other lenses (security,
   reliability, operations, accessibility, responsible AI) go into the `code-review` and
   `browser-verify` skills and `REVIEW.md`. Its question-first intake becomes the Agent Task
   issue form.
5. **A custom orchestrator service**, a supervisor in the style of Symphony. Rejected for now:
   GitHub already provides the state, the sandbox, CI and review. Revisit it if many agents need
   scheduling.

## Decision

Option 4:

- `AGENTS.md` is the canonical guide. `.github/copilot-instructions.md`, `CLAUDE.md` and
  `REVIEW.md` stay thin.
- Six custom agents in `.github/agents/`: Planner, Builder, Verifier, Maintainer, Science
  Reviewer and Architect.
- Nine skills in `.github/skills/`.
- Hooks in `.github/hooks/agent-gates.json`: deny destructive commands, check that an edited file
  still parses, and run the cheap CI checks before the agent stops.
- `.github/workflows/copilot-setup-steps.yml` installs exactly what CI installs. The dev container
  does the same for Codespaces.
- The Agent Task issue form is the specification.
- Copilot code review runs automatically on pull requests into `main`. A person merges.

## Consequences

Better:

- Every surface reads the same rules.
- The most common red builds (dependency-map drift, a stale test count, a broken workflow file)
  are caught inside the agent's session, before anyone has to approve a CI run from a phone.
- Review happens in a fresh context, from CI and from Copilot code review.
- Design decisions leave a trail.

Worse:

- More files to keep consistent. `tooling/test_agent_harness.py` guards their structure, links
  and paths, and `tooling/test_agent_hooks.py` guards the hooks' decisions.
- Hooks run on every shell command and edit. They fail open by design, so a broken hook means a
  missing check, not a blocked agent.
- Automatic reviews use Copilot requests.
- Assigning an issue from the phone runs the default agent. Choosing a specialist means starting
  a New Session.

Follow-up: decide whether an agent should start automatically when an issue is labelled. That
needs a personal access token stored as a secret.

## How we will know

- The Copilot Setup Steps workflow passes on `main`.
- A cloud session started with a custom agent opens a pull request that names the agent and
  carries verification evidence.
- `tooling/test_agent_harness.py` and `tooling/test_agent_hooks.py` pass in CI. Each was seen
  failing on a deliberately broken case before it was trusted.
- Over the following weeks, look at how many agent pull requests needed a second CI run, and how
  many Copilot review comments led to a change. If the hooks or the review add noise rather than
  catching problems, revisit this ADR.

## Links

- Playbook: `docs/agentic-delivery.md`
- GitHub documentation: custom agents configuration, hooks reference, agent skills, configuring
  the cloud agent's environment, Copilot code review.
- Sources cited by the trends review: Anthropic, "Effective harnesses for long-running agents"
  and "Harness design for long-running application development"; OpenAI, "Harness engineering"
  and Symphony; the SWE-agent documentation on the agent-computer interface.
