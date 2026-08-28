# Azure Friday - recording script

Step-by-step for **Thu 3 Sept 2026, 12:00 PM PT**. Read [README.md](README.md) for the
operational runbook and [deck-notes.md](deck-notes.md) Section C for Scott's likely
questions. This file is what you actually follow on the day.

**The storyboard was submitted on 2026-08-26** ([storyboard.md](storyboard.md) section 0
is the record). The producers build the episode around it, so every beat below traces to
something that was promised:

| Submitted | Delivered by |
|---|---|
| Prologue: premise, then the confession about being confidently wrong | Prologue, 0:45-1:45 |
| Slides: architecture in the prologue, CTA at the end, none mid-demo | Prologue slide; beat 4 refers back rather than showing a second |
| Demo: portfolio **live**, FeMoco + Q# + estimate **pre-executed** | Beats 1 and 3 |
| Demo: raw JSON, `evaluate()` in the editor, deploy log, no portal | Beats 2 and 4 |
| Wrap: deterministic core generalises, then CTA | Wrap, 11:30-12:30 |

If you improvise past this on the day, you are improvising past what Chris and Scott
prepared against.

---

## The decision: which demo

**Lead live with the "no" - portfolio optimisation. Pre-record the "yes".**

[README.md](README.md) and [storyboard.md](storyboard.md) disagreed on this. The README
beat sheet opens live with FeMoco (the yes) and fills the wait by walking Troyer's six
filters. That is the older plan and it loses, for three reasons:

1. **The episode is titled "the agent that talks you *out* of quantum computing".** The
   "no" is the promise. Deliver it in the first ninety seconds, not at 2:00.
2. **Filling a wait by teaching Troyer's filters is the exact failure the prep call
   flagged** - going broad on the domain. Chris: *"not a Build or Ignite marketing talk"*.
3. **Portfolio is the fastest call.** Verdict-only lands in 20-60s; the code-generation
   path is 58-79s. Put the short one on camera.

The README itself already concedes it: *"The portfolio and AI prompts are the money shot:
the agent talks you out of quantum."*

**What gets cut.** Bicep generation. Chris: *"This is not a feature parade. Do not show
every option, screen, or workflow possible."* Q# plus a resource estimate plus Bicep is a
parade. The estimator is the quantum content; Bicep is a second code block that makes the
same point.

**Timings.** Chris's prep mail is authoritative and the most recent: **11-13 min total,
6-9 min demo, slides 60-90s**. The README's 10-12/6-8 predates it. The storyboard form's
"5-8" is generic boilerplate; 6m30s satisfies both.

---

## What the app actually does, end to end

Show this once, on one slide, in the prologue. Do not re-explain it later.

The whole argument rests on **the order of operations in `evaluate()`**, which is worth
stating precisely because it is checkable:

```
POST /api/evaluate
  |
  1.  kb.classify_problem()      AI Search over the curated corpus. No model.
  1b. route_platform()           <-- VERDICT, PLATFORM AND CONFIDENCE DECIDED HERE
  2.  find_similar_problems()    reference problems from the 20
  3.  build context JSON         the already-decided routing goes IN as input
  4.  model call                 writes the prose, may disagree -> model_dissent
  |
  response
```

**The model is called at step 4. The verdict was decided at step 1b.** That is not a
policy or a prompt instruction - it is call order, and it is why the same question gives
the same answer twice. If Scott pushes on "how do you stop the model overriding it", the
honest answer is "it is never asked".

Two details worth having ready:

- **The arXiv corpus is switched off by default** (`USE_PAPERS`). It is a quant-ph sweep,
  so it argues for quantum on every question - and when measured, its most confident hits
  were for the two prompts that must be declined. When it is on, it goes to the model in
  its own labelled block and never reaches `route_platform()`.
- **Production runs chat-completions on the Azure AI Foundry model-router**, not a Foundry
  Agent. The agent `quantum-advantage-orchestrator` is provisioned on `qgc-eval-proj` but
  `QGC_USE_AGENT=0`, because measured on 2026-08-19 it was 51.9s median against 28.3s -
  1.8x slower, for one formatting improvement in 22 cases. **Do not call it an agent
  running in Foundry on air.** If asked: "we built it, measured it, and left it off."

---

## Run of show

| Time | Segment | |
|---|---|---|
| 0:00-0:45 | Scott's intro + premise | conversational |
| 0:45-1:45 | Prologue + architecture slide | **60s max on the slide** |
| 1:45-8:15 | **Demo**, four beats | 6m30s |
| 8:15-11:30 | Conversation with Scott | [deck-notes.md](deck-notes.md) Section C |
| 11:30-12:30 | Takeaway + CTA slide | |

Chris: *"Do not plan to talk nonstop for several minutes."* The **>>** marks below are
deliberate hand-offs - stop talking there and let Scott in.

---

## Prologue (0:45-1:45)

**Screen: architecture slide. One minute. Chris will stop the recording if it runs.**

The premise, roughly thirty seconds:

> Every team now has someone asking whether their workload belongs on a quantum computer,
> and almost every answer is marketing. The useful answer is usually no. Being able to say
> no, with a reason you can audit, is the whole product.

One line of where it came from - **one line, not the chronology**:

> I started this because I thought AI plus quantum was going to let me solve one of the
> hardest problems in science. I was wrong in an interesting way, and the app is what is
> left after finding out.

Then the confession, which is what earns the demo:

> This thing used to be confidently wrong. Ask it about portfolio optimisation and it came
> back QUANTUM_ADVANTAGE, 0.9 confidence, with citations. That was not a hallucination -
> vector search did its job and returned its best match, because there is no "no match".

**>> Hand off here.** That line lands with anyone who has shipped RAG. Let Scott react.

Then the slide, thirty seconds, pointing at the request path above:

> Container Apps, managed identity end to end, AI Search over a curated corpus, the Foundry
> model-router. The one thing that matters: the verdict is decided in code, before the
> model is called.

---

## Beat 1 - the bug you also have (1:45-3:15) **LIVE**

**Screen: the live site.**

Type, exactly - the router reads the problem text and paraphrasing can change the answer:

```
Optimize a portfolio of 500 assets using mean-variance optimisation
```

Leave **Generate code unticked**. Hit Evaluate.

**The wait is 20-60s.** Do not fill it with quantum theory. Fill it with the bug:

> Grover gives you a quadratic speedup on search. Sounds great. It does not survive
> error-correction overhead - you spend more on the correction than you win on the
> search. So the honest answer here is classical. The old version could not tell you
> that, because it matched an index entry called "Probabilistic Sampling, Quantum
> Supremacy" and took the match as evidence.

**>> Hand off.** Ask Scott whether he has seen a retrieval hit treated as proof.

Lands on **HPC_PREFERRED**. Then the fix, in one sentence:

> The fix is a relevance gate. The problem text itself has to corroborate before a
> retrieved hit is allowed to carry a verdict.

*If it runs long past 60s:* keep talking, switch to the fallback tab, say plainly that you
are switching. Do not narrate a spinner.

---

## Beat 2 - the model does not get a vote (3:15-4:45)

**Screen: raw JSON, then `evaluate()` in the editor.**

Show `model_dissent` in the response. Then show the function, and scroll to the step
comments - this is the strongest thirty seconds in the episode because it is checkable:

> `route_platform` is step 1b. The model call is step 4. The verdict is already decided
> and gets passed in as *input*. The model writes the explanation and is allowed to
> disagree - when it does, that goes in `model_dissent` and is never applied.

Run the same prompt again. Same verdict.

**>> Hand off.** This is the reusable pattern; Scott will have a question about it.

---

## Beat 3 - the quantum part (4:45-6:45) **PRE-EXECUTED**

**Screen: second tab, already loaded.** Say plainly that you ran it earlier.

```
I need to find the ground state energy of the FeMoco nitrogenase cofactor for catalyst design
```

Verdict **QUANTUM_ADVANTAGE**. Scroll the generated Q#, then the resource estimate.

> The Q# is not just emitted. It is compiled inside the request, and if it does not
> compile the compiler error goes back to the model and it tries again. What you are
> looking at provably built. Then the Azure Quantum Resource Estimator gives physical
> qubits and runtime - and that number is the point. "Quantum advantage" means nothing
> until you know it needs a machine nobody has yet.

If there is room, the line that makes the estimate land - Troyer's constraint, and the
best piece of domain content available because it changes a decision rather than teaching
physics:

> The naive plan is: run the quantum job, get the state back, analyse it classically. Try
> that with a thousand qubits. The state you would be copying is larger than anything you
> can move over a network or put on disk - you would still be transferring it long after
> the machine was scrapped. So the quantum part cannot hand you raw state. It has to hand
> you an answer. That constraint is why the estimator matters more than the circuit.

**Do not attach a specific figure to that.** The point is the order of magnitude, and an
exact byte count invites a correction you do not need on camera.

**Do not script a specific qubit count.** It varies run to run because the generated
circuit varies - two runs on 2026-08-26 gave 98,705 and 137,265. Read whatever is on
screen.

**Pre-executed because this path is 58-79s**, and the retry loop can push it further.

---

## Beat 4 - how we know it works (6:45-8:15)

**Screen: the deploy log line. No slide** - the architecture already ran in the prologue.

> Q# generation was dead in production for weeks and every check stayed green. The API
> caught the generator's exception and returned an empty string, and the deploy check only
> asked whether the field was *declared* in the OpenAPI schema. Schema tests answer schema
> questions. The deploy now posts a real prompt and fails if no Q# comes back.

**>> Hand off into the conversation.**

---

## Wrap (11:30-12:30)

> The pattern generalises past quantum. If you are building any grounded agent, put the
> decision in a deterministic core and let the model explain it rather than make it. You
> get reproducibility, an audit trail, and somewhere to record when the model disagrees.

**Screen: CTA tab** - this is the last tab, and becomes the closing background.

---

## The journey - answers, not narration

This is the strongest material available and the easiest way to lose the episode. Told as
a chronology it is ten topics and about three minutes, which is the keynote Chris asked
you not to give: *"not a Build or Ignite marketing talk"*, *"not a feature parade"*, *"do
not plan to talk nonstop for several minutes"*.

So none of it is narrated. It is held here as answers, and Scott decides which get used.
One line of the arc is already in the prologue; that is the whole budget for autobiography.

**"How did this start?"**
> A ChatGPT question in August 2025 - what are the twenty hardest problems in science, and
> could Q# help. I was in full shiny-object mode, half convinced AI plus quantum was going
> to hand me something Nobel-shaped. I wrote the Q# with AI, structured it like any other
> architecture job, and ran around a hundred jobs on Azure Quantum hoping for a light at
> the end of the tunnel.

**"What changed your mind?"** - the best answer you have, so leave room for it:
> I met Dr Matthias Troyer, and he nullified several of my problems in about an hour. Not
> the physics - the plumbing. The naive plan is to run the quantum job and analyse the
> state classically. At a thousand qubits that state is bigger than anything you can move
> over a network or store, so you would still be copying it long after the machine was
> scrapped. The quantum part cannot hand you raw state; it has to hand you an answer. Half
> of what I had assumed died on that constraint alone.

**"What did you throw away?"**
> A Cosmos graph database linking the sources - built it, then removed it, the knowledge
> base is committed JSON with AI Search over it. Two agents, a fact-checker and an HPC
> comparator - they were YAML that nothing ever loaded. And the Foundry agent itself is
> still provisioned but switched off, because I measured it at 1.8x the latency of plain
> chat-completions for one formatting improvement in twenty-two cases.

**"Why the grounding work?"**
> I wanted the model standing on something. arXiv for current work, and the Quantum
> Algorithm Zoo - which I only found because someone on my MITx course pointed me at it -
> for the algorithms. Both go into a search index. The zoo is the part that carries
> verdicts, because it is curated; the arXiv sweep turned out to be decidable about 2% of
> the time against 13.5% for the curated references.

**"What does the evaluator actually decide?"**
> Quantum, AI/ML or HPC. Sometimes classical wins outright on sheer available compute, and
> that is a real answer, not a cop-out. Then I wanted three things the verdict alone does
> not give you: what the code would look like, what it would cost, and whether you could
> run it today at all.

## Say it this way

Eight things in the draft narrative would misfire on camera. These are checkable, and
Azure Friday is exactly where someone checks.

| Do not say | Say | Why |
|---|---|---|
| "container instance" | **Azure Container Apps** | ACI and ACA are different products; wrong one on Azure Friday is a bad look |
| "I created an MCP server" | "I attached Microsoft's public **Learn MCP** server to a Foundry agent" | there is no MCP server in this repo - `*mcp*.py` returns nothing. You consumed one |
| "we use Cosmos as a graph db" | "I built it on Cosmos, then took it out" | retired in #156; past tense is honest and a better story |
| "300 commits" | **380 commits, 181 merged PRs** | measured 2026-08-26 |
| "over a hundred simulations" | "around a hundred" | `az quantum job list` returns exactly 100, which looks like a page cap rather than a count |
| "Divencenzo" | **DiVincenzo** | spelling, and the audience will include people who know the name |
| "the agents had to pass the DiVincenzo criteria" | "each **problem** is scored against DiVincenzo hardware-readiness criteria" | agents do not pass criteria; problems are evaluated against them |
| "an AI agent running in AI Foundry" | "the Azure AI Foundry **model-router**" | `QGC_USE_AGENT=0` - the agent is not in the request path |

> The MCP one is the dangerous one, and it is not your fault: `docs/architecture.md` ticked
> "Scientific Papers MCP server" and "Algorithm Zoo MCP server" as complete while the same
> file said "Not built" a hundred and fifty lines above. The doc has been corrected.

---

## Pre-flight, day of

- [ ] `python tooling/verify_demo_prompts.py` ~15 min before - covers all five verdicts
      **and** code generation
- [ ] No open GitHub issue labelled `uptime`
- [ ] Site does not show DEMO MODE
- [ ] Tab order: **1** live site (empty) - **2** beat 3 pre-loaded - **3** raw JSON -
      **4** `evaluate.py` - **5** deploy log - **6** CTA
- [ ] Fallback recording open behind tab 1
- [ ] `QGC_USE_AGENT` still `0`:
      `az containerapp show -n qgc-eval-api -g qgc-evaluator -o json`

## Do not say

- "An AI agent running in AI Foundry" - it is the model-router; the agent is off.
- "I created an MCP server" - there is none in this repo; the Learn MCP is consumed.
- "Azure Container Instances" - it is Container Apps.
- Cosmos DB in the present tense - retired in #156.
- Any specific physical-qubit count - it varies per run.
- Any specific byte figure for the thousand-qubit state - the order of magnitude is the point.
- "By the time you see this" - record as though it publishes that day.
- All 20 problems are at Stage C - it is 9 at C, 8 at B, 3 at D. <!-- not-a-claim -->
