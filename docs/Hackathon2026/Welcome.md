# Hackathon 2026 - welcome message to joiners

A record of the message sent to the four hack-week joiners on **8 September 2026**,
reproduced below with dashes normalised to ASCII to match the rest of this folder.
It is a snapshot, not a living document.

Live scope lives in the tracking issues, not here - if the plan changes, change those:

| | Workstream | Issue |
| --- | --- | --- |
| A | Retire the mock estimator (headline) | [#255](https://github.com/WernerRall147/quantum-grand-challenges/issues/255) |
| B | Blender visualisation | [#254](https://github.com/WernerRall147/quantum-grand-challenges/issues/254) |
| C | Prove the agent is grounded | [#256](https://github.com/WernerRall147/quantum-grand-challenges/issues/256) |
| D | Demo surface | [#257](https://github.com/WernerRall147/quantum-grand-challenges/issues/257) |

Milestone: [Hackathon 2026](https://github.com/WernerRall147/quantum-grand-challenges/milestone/1),
due Friday 18 September 2026.

Two deliberate choices worth keeping if this is reused:

- It asks for a **GitHub username**, never credentials. A collaborator invite needs only
  the handle, and a joining instruction that normalises pasting secrets into Teams is the
  wrong first impression for a project whose pitch is trustworthiness.
- The `viz/` entry in the directory tree is marked *"new, you'll create it"* because it
  did not exist when this was sent. A file tree is a claim; an unbuilt path has to say so.

---

**Welcome to Quantum Grand Challenges - Hackathon 2026** 🚀

Hi all - glad to have you on this one. Short version of what we're building, what I need from you before Wednesday, and how we'll run the week.

---

**1. What I need from you first**

Reply with your **GitHub username** (just the handle, e.g. `@octocat`) and I'll send you a collaborator invite.

That's genuinely all I need - please **don't send passwords, PATs or any credentials**. GitHub invites work off the username alone, and anything else is a secret you shouldn't be pasting into Teams.

---

**2. What the project is**

An **AI agent that tells you which compute substrate a workload actually belongs on** - quantum, AI/ML, or HPC - and shows its working.

You describe a problem in plain language. It scores it against Troyer's utility-scale filters, grounds every claim in peer-reviewed papers, returns a verdict *with citations and real qubit-level resource estimates*, then generates Q# or Bicep to run it.

The whole thesis is **honest claims**. It's designed to talk you *out* of quantum when the evidence says so - ask it to optimise a portfolio and it returns `HPC_PREFERRED`. Of our 20 problem domains, **11 were honestly downgraded and archived** with the reason recorded. Publishing the negative results is the point, not a caveat.

It's live and deployed, not a prototype: https://wernerrall147.github.io/quantum-grand-challenges/

---

**3. What we're getting ready during the hack**

Four workstreams. Each has a GitHub issue with full scope - come to Wednesday's check-in with a preference and we'll divide up.

| | Workstream | The short version |
|---|---|---|
| **A** | Retire the mock estimator *(headline)* | We found a **fake estimate pipeline shadowing a real one**. All 9 active problems currently report identical qubit budgets. Fix it, and make the fallback fail loudly instead of inventing numbers. |
| **B** | Blender visualisation | Render what a quantum run actually looks like, for 3-4 flagship problems. |
| **C** | Prove the agent is grounded | Foundry evals + tracing, so a judge can watch a verdict being formed from its sources. |
| **D** | Demo surface | The website, and owning the 3-minute demo end to end. |

A is the headline - our executive challenge is *Cloud Hardware Infra in the Era of AI*, and honest hardware requirement modelling is what answers it.

---

**4. Where you'll be working**

Python + Q# backend, Next.js front end, all on Azure. You do **not** need .NET - Q# runs through the `qdk` Python package.

```
agents/       the evaluator: API, orchestrator, evals   (C)
problems/     20 domains, Q# + classical baselines       (A)
tooling/      estimation, validation, guard tests        (A)
website/      Next.js dashboard                          (D)
viz/          Blender pipeline - new, you'll create it   (B)
```

Roughly: **FastAPI on Azure Container Apps**, managed identity end to end (no keys), Azure AI Search for retrieval, the **Azure AI Foundry model-router** picking the cheapest capable model per query, and a nightly job ingesting new arXiv papers.

The workstreams own separate directories on purpose - so four of us can move at once without fighting over the same files.

---

**5. How we work**

- **Branch + PR.** `main` is protected, nobody pushes to it directly (me included).
- **Approvals required is 0** - CI is the gate. Once it's green, merge your own PR. Don't sit waiting on a reviewer.
- Branch prefixes: `feat/`, `fix/`, `docs/`, `test/`, `chore/`.
- There's a PR template that'll walk you through the rest.

One habit that matters here more than most repos: **a green check is not evidence.** We've had four checks pass for months while the thing they guarded was broken. So if you add a check, break the thing deliberately first and watch it go red. The template asks you to confirm you did.

---

**6. Check-ins & deadline**

**Mon / Wed / Fri at 13:00 SAST on Teams** - Wed 9, Fri 11, Mon 14, Wed 16, Fri 18.

**Deadline: Friday 18 September.** That's 8 working days, so:

- **Wed 9** - kickoff, pick workstreams, get everyone building locally
- **Thu 17** - feature freeze + full demo rehearsal
- **Fri 18** - submission

The Wednesday 16th check-in is our last one before freeze. Anything not landed by then doesn't go in the demo.

---

Send me those GitHub handles and I'll get you access today. Any questions, just shout. 👋
