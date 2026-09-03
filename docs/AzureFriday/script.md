# Azure Friday - recording script

Step-by-step for **Thu 3 Sept 2026, 12:00 PM PT**. Read [README.md](README.md) for the
operational runbook and [deck-notes.md](deck-notes.md) Section C for Scott's likely
questions. This file is what you actually follow on the day.

**The storyboard was submitted on 2026-08-26** ([storyboard.md](storyboard.md) section 0
is the record). The producers build the episode around it, so every beat below traces to
something that was promised:

| Submitted | Delivered by |
|---|---|
| Prologue: premise, then the confession about being confidently wrong | Prologue, 0:45-1:30 - **confession cut, see below** |
| Slides: architecture in the prologue, CTA at the end, none mid-demo | Unchanged |
| Demo: portfolio **live**, FeMoco + Q# + estimate **pre-executed** | **Replaced.** One problem, all live |
| Demo: raw JSON, `evaluate()` in the editor, deploy log, no portal | **Replaced.** Trace, local run, estimator, Azure Quantum jobs. Still no portal |
| Wrap: deterministic core generalises, then CTA | Unchanged |

> ## This is a different demo from the one on the form. Tell Chris before the recording.
>
> Not a tweak - the storyboard promised two problems and code generation, and this is one
> problem with neither. It was rewritten after the Azure Friday team's run-through, whose
> feedback is quoted in full in the next section. In their words it was *"way too long"*,
> *"less dialogue and more lecture"*, and the two worked examples were *"way over regular
> folks heads"*.
>
> **What is gone:** FeMoco, portfolio optimisation, Q# generation, Bicep, the RAG confession
> in the prologue, and about a minute of runtime.
>
> **What replaces it:** one problem - unsorted search - carried end to end, with far more
> Azure Quantum on screen: the Resource Estimator, real submitted jobs, and the provider
> and queue-time list.
>
> **The through-line still holds.** The episode is still the tool talking you out of quantum;
> it now does it with a working algorithm and a number from an Azure service instead of two
> problems nobody in the audience recognises.

If you improvise past this on the day, you are improvising past what Chris and Scott
prepared against.

---

## Everything you open, in order

One place to click from, so you are not hunting for a path on camera. Tabs are in the
order Chris asked for: the **last** one becomes the closing background.

### Browser tabs, left to right

| # | Tab | Used in |
|---|---|---|
| 1 | [The evaluator](https://wernerrall147.github.io/quantum-grand-challenges/evaluate/) - **type here** | Beat 1, live |
| 2 | Fallback recording of beat 1 - **open before you start**, do not use unless it stalls | Beat 1 insurance |
| 3 | [The repo](https://github.com/WernerRall147/quantum-grand-challenges) - **last tab, closing background** | Wrap |

Beats 2, 3 and 4 are **all terminal**. That is deliberate: it is one window, no tab
hunting, and it is where the Azure Quantum content lives.

Have a terminal open and sized so twelve lines are legible at 1080p - beat 3's output is
twenty lines and beat 4's job table is wide.

**Not committed, deliberately:** the StreamYard studio link. This repo is public; it is in
Chris's prep mail.

### Terminal, in beat order

```powershell
# Beat 2 - who decided the verdict, and when
python tooling/show_trace.py --demo "Search an unsorted database of 10 million records for a matching entry"

# Beat 3 - the algorithm actually working, ~10s
python -c "from qdk import qsharp; qsharp.init(project_root='problems/archived/15_database_search/qsharp'); qsharp.run('Main.RunGroverDemonstration()', shots=1)"

# Beat 3 - and what it costs fault-tolerantly
type problems\archived\15_database_search\circuits\estimate.json

# Beat 4 - real Azure Quantum. No -l: it is deprecated and pins a retiring API version.
az quantum job list -g Quantum-Grand-Challenges -w Quantum-Grand-Challenges -o table `
  --query "[?contains(name,'database_search')].{Job:name, Status:status, Target:target}"
az quantum target list -g Quantum-Grand-Challenges -w Quantum-Grand-Challenges -o table

# Beat 4 - the job I ran yesterday: Grover on Quantinuum's H2 emulator, rendered
az quantum job output -g qgc-af-demo-rg -w qgc-af-demo `
  -j ad36284c-a707-11f1-8583-f068e3583cd5 -o table

# Beat 4 fallback, if the preview CLI errors. Do not retry live.
type docs\AzureFriday\azure-quantum-snapshot.txt

# ~15 min before: six prompts + code generation, against production
python tooling/verify_demo_prompts.py

# Day-of machine + demo readiness, one command
.\docs\AzureFriday\Prep-DemoMachine.ps1 -PreFlight
```

**Set the workspace once before you go live** so the two Azure commands do not prompt:

```powershell
az quantum workspace set -g Quantum-Grand-Challenges -w Quantum-Grand-Challenges
```

### Files, if a question takes you into the code

Only open these if Scott asks. The trace in beat 2 replaced scrolling source, and going
back to it unprompted spends time you do not have.

| File | The question it answers |
|---|---|
| [agents/orchestrator/evaluate.py](../../agents/orchestrator/evaluate.py) | "show me the call order" - steps 1, 1b, 2, 3, 4 are labelled |
| [agents/classifier/platform_router.py](../../agents/classifier/platform_router.py) | "what is the relevance gate?" - the beat 1 fix |
| [agents/tests/test_trace_ordering.py](../../agents/tests/test_trace_ordering.py) | "what stops the ordering regressing?" |
| [tooling/show_trace.py](../../tooling/show_trace.py) | "how are you drawing that?" |
| [.github/workflows/deploy-evaluator-api.yml](../../.github/workflows/deploy-evaluator-api.yml) | "how do you know a deploy works?" - the behavioural smoke test |

### The other documents

| File | What it owns |
|---|---|
| [README.md](README.md) | Runbook, the six prompts, what to do when it breaks |
| [deck-notes.md](deck-notes.md) | Verified numbers, and Section C - Scott's likely questions |
| [storyboard.md](storyboard.md) | What was actually submitted to the producers |
| [../tracing.md](../tracing.md) | How the trace works, and the KQL behind it |
| [Set-AzureDemoAccess.ps1](Set-AzureDemoAccess.ps1) | Opens the Azure Quantum storage exclusion so the workspace does not read *Failed*. **`-Revert` after the recording** |
| [../../problems/archived/15_database_search/azure_runs/2026-09-02-grover-h2-1e/](../../problems/archived/15_database_search/azure_runs/2026-09-02-grover-h2-1e/README.md) | The Quantinuum run: submitted QIR, raw result, and what the numbers mean |

### If it breaks

Fallback recording open **before** you start. [README.md](README.md) section 6 has the
failure modes and the fix for each; the one that has actually happened is the managed
identity losing its data-plane role, which shows as **DEMO MODE** on the site.

---

## The decision: one problem, and why this one

**Grover's algorithm on an unsorted search. Nothing else.**

This replaces the two-problem demo (portfolio optimisation *and* FeMoco) after the run-
through with the Azure Friday team. Their feedback, verbatim:

> you basically spoke for 10 straight minutes - that's way too long. Even though Scott
> isn't a Quantum expert, this was less dialogue and more lecture
>
> spend more time on the Quantum Azure stuff - I'm guessing 99% of the people have never
> done this, and it's all going over their head
>
> Spend less time talking about the math problems - you cut it down but it really needs to
> be less - those two different math problems are way over regular folks heads most likely
>
> Is this tool something regular folks have access to? If not, it kinda isn't as
> interesting because you don't show enough of how the app actually interfaces with the
> quantum stuff behind it

Four separate instructions, and one problem fixes all four.

**Why unsorted search.** "Find one record in ten million" needs no explanation and no
mathematics. Nobody has to be told what a nitrogenase cofactor is, or what mean-variance
optimisation is. That was the complaint, and this is the fix.

**Why this one specifically - it is the only candidate where every piece is real:**

| Piece | Grover / `15_database_search` | Measured |
|---|---|---|
| The app declines it | `HPC_PREFERRED`, 0.7 confidence | 2026-09-01 |
| The algorithm actually works | 4 targets in 4,096 items, **50/50 successes** against 99.8% predicted | 2026-09-01, 9.9s |
| A real Azure Quantum resource estimate | **61,122 physical qubits**, 18 logical, 63% T-factories | committed `circuits/estimate.json` |
| Real Azure Quantum jobs | **6 succeeded** on Quantinuum H2 + Rigetti QVM | `azureRunHistory.json` |
| Anyone can run it | two commands, no Azure account | README "Try it, no setup" |

**Shor was the obvious alternative and it fails on evidence.** Factoring is the more famous
story, and the app does return `QUANTUM_ADVANTAGE` for RSA-2048 with Q# that compiled 3
times out of 3. But the local demo does not actually factor 15 - quantum period finding
returns r=8 where the classical period is 4, and the GCDs come back 15 and 1 rather than 3
and 5. And the generated circuit's estimate swung **60,665 → 17 → 17** physical qubits
across three runs on 2026-09-01. Saying "this is what breaking RSA costs" over the number
17 is a credibility failure with a live audience. Grover is the one that survives contact.

**The spine of the episode, in one number:**

> It takes **61,122 physical qubits** to reliably search **sixteen items**. Classically
> that is four comparisons.

That is the whole thesis, it comes from an Azure service rather than from an opinion, and
it needs no mathematics to land.

**What gets cut, and it is a lot.** Code generation, Bicep, FeMoco, portfolio
optimisation, Troyer's six filters as a walkthrough, and the origin story beyond one line.
Chris: *"not a feature parade"*. The Azure Friday team: *"way too long"*. The Q# on screen
is the repository's own - the code that actually ran on Azure Quantum - not something the
model wrote during the recording.

**Timings.** Chris's prep mail: 11-13 min total, 6-9 min demo, slides 60-90s. This demo
targets **5m30s**, deliberately under the floor, because the note that mattered most was
that it played as a lecture. The recovered time goes to Scott.

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

**Since #238 this is no longer a claim you have to take on trust.** Every response carries
a `trace` of those steps with what each one decided, so the ordering is visible on screen
in beat 2, and `agents/tests/test_trace_ordering.py` fails the build if a routing decision
ever moves after the model call. See [../tracing.md](../tracing.md).

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
| 0:45-1:30 | Prologue + architecture slide | **45s on the slide, not 60** |
| 1:30-7:00 | **Demo**, four beats | 5m30s |
| 7:00-11:30 | Conversation with Scott | [deck-notes.md](deck-notes.md) Section C |
| 11:30-12:30 | Takeaway + CTA slide | |

**The demo lost a full minute and the conversation gained 90 seconds.** That is the point
of this revision. Chris: *"Do not plan to talk nonstop for several minutes."* Azure
Friday: *"less dialogue and more lecture."*

The **>>** marks below are deliberate hand-offs. There are now **five** of them in five and
a half minutes, and none is optional. If Scott does not take one, ask him a direct
question - the suggested ones are written in.

**No block below is longer than four sentences.** That is the rule that fixes the note.

---

## Prologue (0:45-1:30)

**Screen: architecture slide. Forty-five seconds.**

The premise, about twenty seconds:

> Everyone has someone asking whether their workload should run on a quantum computer, and
> almost every answer out there is marketing. The useful answer is usually no. Being able
> to say no, with a number behind it, is the whole product.

One line of origin - **one line**:

> This started as a ChatGPT question about the twenty hardest problems in science, and
> whether Q# could touch any of them. The app is what is left after finding out.

**>> Hand off.** *"Have you had people ask you whether they should be doing quantum yet?"*

Then the slide, twenty seconds. Do not read the boxes out:

> Container Apps, AI Search over a curated corpus, the Foundry model-router, and Azure
> Quantum for the estimates. The only part that matters today: the verdict is decided in
> code, before the model is ever called.

---

## Beat 1 - ask it (1:30-2:45) **LIVE**

**Screen: [the live site](https://wernerrall147.github.io/quantum-grand-challenges/evaluate/) - tab 1.**

Type, exactly:

```
Search an unsorted database of 10 million records for a matching entry
```

Leave **Generate code unticked**. Hit Evaluate.

Set it up in two sentences while it thinks - **no mathematics, and do not teach Grover**:

> There is a famous quantum algorithm for exactly this, from 1996, and it is one of the very
> few where the speedup is actually proven rather than conjectured. It has been the poster
> child for quantum search ever since.

**Precision matters on that line.** Grover is provably *optimal* for unstructured search -
there is a matching lower bound, which is genuinely rare. Do not say "the only thing
quantum is provably better at", and do not say "exponential": it is quadratic, and the
whole point of the episode is that quadratic is not enough.

**>> Hand off.** *"If I told you quantum could search ten million records faster, would you
buy it?"* Let him answer. **The call takes twenty to sixty seconds - do not fill it.**

Lands on **HPC_PREFERRED**, confidence 0.7.

> So it says no. Use a classical machine.

**>> Hand off.** *"That surprise you?"*

*If it runs past 60s:* switch to the fallback tab and say plainly that you are switching.
Do not narrate a spinner.

---

## Beat 2 - who decided that, and when (2:45-3:30)

**Screen: the terminal.**

```powershell
python tooling/show_trace.py --demo "Search an unsorted database of 10 million records for a matching entry"
```

Every response carries a trace of what each step decided. Three sentences, pointing at it:

> The verdict is decided at step 1b, in code, in a fraction of a millisecond. The model is
> not called until step 4, and by then the answer is already an input it is being asked to
> explain. It is allowed to disagree, and when it does that gets recorded and thrown away.

> That is not a policy or a prompt. It is call order, and there is a test that fails the
> build if it ever changes.

**>> Hand off.** *"That is the bit I would steal for any agent - has that bitten you?"*

*Do not quote the millisecond figure.* Read what is on screen. The ratio is what matters:
the deciding is free, the writing is twenty-odd seconds.

---

## Beat 3 - but the algorithm works (3:30-5:15) **LIVE**

**Screen: the terminal. This is the heart of the episode.**

> Here is the awkward part. The algorithm is not broken. Watch it run.

```powershell
python -c "from qdk import qsharp; qsharp.init(project_root='problems/archived/15_database_search/qsharp'); qsharp.run('Main.RunGroverDemonstration()', shots=1)"
```

**Ten to fifteen seconds.** Measured 9.0s, 9.9s and 13.8s on 2026-09-01 - it varies, so do
not promise a number. Let it finish, then point at the two things that matter - the success
rate, and the summary line it ends on:

```
Demo 3: Large search space (12 qubits, 4096 items)
  Target indices: [42, 137, 999, 2048]
  Optimal iterations: 24
  Predicted success probability: 0.9984
  Empirical success rate: 1.0 (50/50)

Demo 3 (4096 items): Classical~1024, Quantum=24, Speedup~42.7x
```

> Four needles in four thousand haystacks. Twenty-four quantum steps instead of about a
> thousand classical checks - forty times fewer. Fifty runs, fifty successes, and the
> theory predicted 99.8%, so it works exactly as much as the mathematics says it should.

**>> Hand off.** *"So why did the tool tell me not to use it?"* - if Scott does not ask
this, ask it yourself out loud. It is the pivot of the whole episode.

Then the answer, and **this is the most important thing on screen all episode**:

```powershell
type problems\archived\15_database_search\circuits\estimate.json
```

> That run was on a simulator, and a simulator does not make mistakes. A real quantum
> computer does, constantly, so you wrap the whole thing in error correction. The Azure
> Quantum Resource Estimator tells you what that costs.

> **Sixty-one thousand physical qubits. To reliably search sixteen items.** Eighteen useful
> qubits, and sixty-three percent of the machine doing nothing but manufacturing the special
> states the algorithm needs.

> Classically, searching sixteen items is four comparisons. That is the answer, and it is a
> number from an Azure service rather than an opinion from me.

**>> Hand off.** *"That gap is the whole industry right now."*

**Read the numbers off the screen, not off this page.** They are stable - the file is
committed - but read them anyway.

---

## Beat 4 - it is real, and you can run it tonight (5:15-7:00)

**Screen: the terminal, Azure Quantum.**

> That estimate is not a simulation of a simulation. The same circuit has been submitted to
> Azure Quantum for real.

```powershell
az quantum job list -g Quantum-Grand-Challenges -w Quantum-Grand-Challenges -o table `
  --query "[?contains(name,'database_search')].{Job:name, Status:status, Target:target}"
```

> **No `-l`.** The `--location` flag is deprecated, and it pins the request to API version
> `2023-11-13-preview` which the service is in the middle of retiring. On 2026-09-01 that
> combination returned `NoRegisteredProviderFound` on one machine and worked on another
> minutes later. Without the flag the CLI resolves the location itself. Six runs each way
> succeeded afterwards, so this is **intermittent, not fixed** - see the fallback below.

Five rows, and they tell the whole story on their own:

```
Job                               Status     Target
--------------------------------  ---------  ---------------------
qgc-15_database_search-1000shots  Succeeded  quantinuum.sim.h2-1e
qgc-rigetti-15_database_search    Succeeded  rigetti.sim.qvm
qgc-15_database_search            Failed     quantinuum.sim.h2-1sc
qgc-15_database_search            Succeeded  quantinuum.sim.h2-1e
qgc-15_database_search            Succeeded  quantinuum.sim.h2-1sc
```

> Same circuit, two different vendors' machines, submitted from one workspace. One of them
> failed. That is what this actually looks like.

**The `--query` is not decoration.** The full table is seven columns wide and wraps at
1080p; this is three. Do not drop it on the day.

> ### If either command errors, do not retry on camera
>
> `az quantum` is a **preview extension** talking to an API that is mid-migration. It threw
> `NoRegisteredProviderFound` once already. Say "let me show you the capture from earlier"
> and run:
>
> ```powershell
> type docs\AzureFriday\azure-quantum-snapshot.txt
> ```
>
> Same content, captured from the same commands, regenerated by `-PreFlight` on the day.
> Retrying a preview CLI live is how thirty seconds becomes ninety.

Then the part almost nobody watching has seen:

```powershell
az quantum target list -g Quantum-Grand-Challenges -w Quantum-Grand-Challenges -o table
```

> Quantinuum, Rigetti, IonQ, Pasqal - the machines and emulators you can submit to from one
> Azure workspace. Note the queue times, and note that some of them say Unavailable right
> now. That is what the quantum industry looks like from a terminal.

**The queue column is the best unscripted moment available.** It swings hard: `h2-1e` read
about **five hours** on 2026-09-01 and **three minutes** on 2026-09-02. **Read whatever is
on your screen** - do not quote either number from memory. Whatever it says, the point
lands: "there is a queue for the quantum computer" tells the audience more about the state
of the field than any slide.

> ### If Scott asks whether you can submit one right now - you can, and you did
>
> Show the result you already have rather than submitting live; the emulator queue moves and
> quota is finite. Azure renders it as a histogram, which reads better on camera than JSON:
>
> ```powershell
> az quantum job output -g qgc-af-demo-rg -w qgc-af-demo `
>   -j ad36284c-a707-11f1-8583-f068e3583cd5 -o table
> ```
>
> > *"I ran this one yesterday. Same Grover circuit you just watched, on Quantinuum's H2
> > emulator. It found the marked item in 80 shots out of 100. With no noise at all that
> > circuit is about 96% - so that gap is the noise, and that's the honest state of the
> > hardware right now."*
>
> **Say "80 out of 100" against "about 96%".** The 80 is an exact count. The 96% is analytic,
> not a simulator run - repeat simulator runs gave 92.5%, 93.5%, 96.0%, and a single earlier
> run gave 97%. Do not quote a sampled number as a constant. The other 20 shots are spread
> across twelve outcomes at 1-3 shots each - noise, not a competing answer.
>
> The full record - the exact QIR submitted, the raw payload returned, and the explanation -
> is committed at
> [`problems/archived/15_database_search/azure_runs/2026-09-02-grover-h2-1e/`](../../problems/archived/15_database_search/azure_runs/2026-09-02-grover-h2-1e/README.md).
>
> **Do not submit live on camera.** Quota is shared across the subscription and metered in
> eHQC: 200 shots of this kernel was rejected as `NotEnoughQuota`, 100 shots went through and
> consumed 40.18. And do not quote the `h2-1sc` histogram if you ever run it - that target is a
> syntax checker, returns all zeros, and proves nothing about the algorithm.
>
> One caveat worth having ready, because it is a good story rather than a bad one: this job ran
> in a **second workspace**, created that afternoon. The original one cannot accept new jobs -
> its storage sits in a Microsoft-managed resource group that tenant policy locked down and a
> deny assignment protects, so not even the subscription Owner can open it. Full diagnosis, and
> the ten things ruled out getting there, in [deck-notes.md](deck-notes.md) C7.
>
> **The original workspace can list jobs but not open them.** `az quantum job show` and
> `job output` fail on every job there, because those older payloads live in that same locked
> account. If you need to open a job on camera, use `qgc-af-demo` as above.

**>> Hand off.** *"Have you ever seen a queue time on a quantum computer before?"*

Then close the loop - **this is the answer to "can regular folks use this?", and it is the
line the episode is for**:

> Everything you have just watched, apart from the Azure jobs, runs on a laptop with no
> Azure account. Two commands: `pip install qdk`, then run the problem. The evaluator itself
> is a public web page - no login, no subscription, no waitlist.

> Twenty problems in the repository, nine of them still standing, eleven honestly downgraded
> exactly like this one. All of it is open, and the downgrades are the interesting part.

**Do not open the portal.** The storyboard said no portal and the terminal is better on
camera anyway.

---

## Wrap (11:30-12:30)

Two takeaways, and the second one is the one the episode is for.

> The engineering pattern generalises past quantum. If you are building any grounded agent,
> put the decision in a deterministic core and let the model explain it rather than make it.
> You get reproducibility, an audit trail, and somewhere to record when the model disagrees.

> And the quantum one: the interesting work right now is not finding the next algorithm. It
> is being honest about which of the ones we already have are worth the machine. Eleven of
> my twenty are downgraded. That is not a failure, it is the actual state of the field, and
> anyone can go and check my reasoning because all of it is in the open.

**>> Hand off.** Leave him the last word.

**Screen: CTA tab** - [the repo](https://github.com/WernerRall147/quantum-grand-challenges),
the last tab, which becomes the closing background.

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

Every one of these is a prop in the new demo. Run them in beat order - that also rehearses
the sequence.

- [ ] `python tooling/verify_demo_prompts.py` ~15 min before - all six verdicts
- [ ] **Beat 1** - the site returns `HPC_PREFERRED` for the search prompt, and is not in
      DEMO MODE
- [ ] **Beat 2** - `show_trace.py --demo` renders and exits 0
- [ ] **Beat 3** - the Grover run finishes in about ten seconds and Demo 3 reads 50/50
- [ ] **Beat 3** - `estimate.json` opens and 61,122 is legible at 1080p
- [ ] **Azure access open** - `.\docs\AzureFriday\Set-AzureDemoAccess.ps1 -Check` shows
      `publicNetworkAccess: Enabled` and `provisioningState: Succeeded`. If the workspace
      reads **Failed**, run `-Apply`. **Run `-Revert` after the recording.**
- [ ] **Beat 4** - `az quantum job list` and `target list` both return a table, **without
      `-l`**. These need network and a valid login, and the extension is preview - check
      them, not just the app
- [ ] **Beat 4** - the rendered histogram shows `[0, 1, 1, 1]` at `0.80` and is legible at
      1080p: `az quantum job output -g qgc-af-demo-rg -w qgc-af-demo -j ad36284c-a707-11f1-8583-f068e3583cd5 -o table`
- [ ] **Beat 4 fallback** - `docs\AzureFriday\azure-quantum-snapshot.txt` regenerated today
      and legible. If the live command failed above, this is the beat
- [ ] No open GitHub issue labelled `uptime`
- [ ] **Three** tabs - live site, fallback recording, CTA last. Beats 2-4 are all terminal
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
