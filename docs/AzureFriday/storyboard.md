# Azure Friday storyboard - Quantum Advantage Evaluator

**SUBMITTED 2026-08-26.** This is the record of what the producers have. They build the
episode around it, so the delivery plan in [script.md](script.md) has to match it - if the
two drift, the submitted version wins or you renegotiate on the prep call.

| | |
|---|---|
| **Working title** (locked) | Quantum Advantage Evaluator - the form uses this to link back to the episode submission, do not change it |
| **Go-live title** (candidate) | The AI agent that talks you *out* of quantum computing - can be changed before publish |
| **Presenter** | Werner Rall |
| **Host** | Scott Hanselman |
| **Recording** | **Thu 3 Sept 2026, 12:00 PM PT** - virtual, via StreamYard |
| **Prep call** | Held 26 Aug |
| **Studio link** | In Chris's prep mail - deliberately not committed, this repo is public |
| **Storyboard** | Submitted 26 Aug |
| **Show notes due** | 1-2 business days after recording |
| **Target length** | 11-13 min total, of which **6-9 min max** demo |

> Three different lengths have been quoted. The invitation email said 12-16, the
> production deck said 10-12, and Chris's prep mail - the most recent and the one
> specific to this episode - says **11-13 total with a 6-9 minute demo ceiling**. The
> storyboard form says demos should be 5-8. A 6m30s demo is the only figure that satisfies
> every version, which is why the beat sheet targets it.

---

## 0. What was submitted

Six answers went into the form. Everything below this section is supporting detail; this
is the part the producers actually read.

| Form question | Answer, in short |
|---|---|
| 1. Working title | Quantum Advantage Evaluator (locked) |
| 2. Intro teaser | Honest verdict - quantum, AI/ML or Azure HPC - on Container Apps against the **Azure AI Foundry model-router**. The "no" is the product. |
| 3. Prologue | The premise, then the confession: it used to return `QUANTUM_ADVANTAGE` at 0.9 confidence with citations for portfolio optimisation. Not a hallucination - retrieval has no "no match". |
| 4. Slides | **Yes.** Architecture in the prologue (~60s) and a closing call-to-action. None mid-demo. |
| 5. Demo | Four beats, 6m30s. Portfolio **live**; FeMoco + Q# + resource estimate **pre-executed**; raw JSON and `evaluate()` in the editor; deploy log. No portal. |
| 6. Wrap | The deterministic-core pattern generalises to any grounded agent, then the CTA slide. |

> **Check before the prep call:** the teaser must say model-router, not "an AI agent
> running in AI Foundry". The agent `quantum-advantage-orchestrator` is provisioned but
> `QGC_USE_AGENT=0`, so it is not in the request path. If the earlier wording went in, flag
> it to Chris rather than let Scott ask which agent.

---

## 1. Abstract

Everyone is asking whether their problem should run on a quantum computer, and most
answers are hype. This is a live advisor that gives an honest verdict - quantum, AI/ML,
or Azure HPC - grounded in Troyer's utility-scale filters and DiVincenzo's hardware
criteria, then generates the Q# and the Bicep to actually run it.

The interesting part is what it says *no* to. Ask it about portfolio optimisation and it
tells you to use classical compute, because a quadratic speedup does not survive
error-correction overhead. That "no" is the product.

It started as a single ChatGPT question in August 2025: *what are the 20 hardest problems
in science, and could Q# help?* A year and ~380 commits later it is running on Azure, and
11 of those 20 problems have been honestly downgraded.

## 2. Key takeaways

Pitched at someone who builds this kind of thing, not someone deciding whether quantum
is interesting. The quantum problem is the setting; the engineering is the subject.

1. **Retrieval is not evidence, and this bug is probably in your app too.** Vector search
   returns a top hit for every query - there is no "no match". Ours confidently returned
   `QUANTUM_ADVANTAGE` at 0.9 confidence, with citations, for portfolio optimisation,
   because the index matched "Probabilistic Sampling (Quantum Supremacy)". The fix is a
   relevance gate: the problem text itself has to corroborate before a retrieved hit is
   allowed to carry a verdict.
2. **An honest advisor needs a deterministic core.** The verdict, confidence and platform
   come from a rules engine over a curated database. The model writes the explanation and
   stress-tests the decision; when it disagrees that goes into `model_dissent` and is
   never applied. Same question, same answer, and you can diff it.
3. **A green check is not evidence either.** Q# generation was dead in production while
   every check passed, because the API caught the generator's exception and returned an
   empty string, and the deploy check only asked whether the field was *declared*. Schema
   tests answer schema questions.

## 3. Run of show

| Time | Segment | Content |
|---|---|---|
| 0:00-1:30 | Setup with Scott | Premise in about 30 seconds - "should this run on a quantum computer" is the question, most answers are hype - then straight into the fact that this thing used to be confidently wrong. Origin story is **one line**, not a segment. |
| 1:30-8:00 | **Demo** (see below) | |
| 8:00-11:00 | Conversation | Scott's questions. Prepared answers in [deck-notes.md](deck-notes.md) Section C. |
| 11:00-12:00 | Takeaway | Takeaway 2 - the deterministic-core pattern generalises to any grounded agent. |

> **The failure mode from the prep call was going broad on the problem domain.** Twenty
> hardest problems in science, what a qubit is, why quantum matters - that is a keynote,
> and it eats the clock without telling an engineer anything they can use. Domain detail
> only earns its place when it explains a decision in the code. Troyer's filters are worth
> naming because they *are* the rules engine; they are not worth teaching.

## 4. Demo beat sheet

**A verdict-only call lands in 20-60s**, and the spread matters more than the median: 15
calls on 2026-08-24 gave median 38.0s (min 28.9, max 58.9), 5 calls on 2026-08-26 gave
median 23.4s (min 21.3, max 26.5). Zero mismatches across both. **With code generation it
takes 58-79s** (57.8s local, 79s in CI, both 2026-08-26). Quote the range on camera, not a
number. Beat 3 is pre-loaded for that reason.

| Beat | Time | On screen | The engineering point |
|---|---|---|---|
| 1. The bug you also have | 1:30-3:00 | Portfolio optimisation, 500 assets. **Live.** | Retrieval always returns something. Say what it *used* to answer and why that was worse than useless - confident, cited and wrong. Then the relevance gate. Lands on `HPC_PREFERRED`. |
| 2. The model does not get a vote | 3:00-4:30 | The raw JSON response, `model_dissent` visible | Verdict comes from `route_platform()` in code. Run the same prompt twice, same answer. This is the reusable pattern and the reason the thing can be trusted. |
| 3. The quantum part, and what Azure does | 4:30-6:30 | FeMoco -> `QUANTUM_ADVANTAGE`, generated **Q#**, **resource estimate**. **Pre-loaded.** | The Q# is not just emitted - it is compiled in the request path, and a compile error goes back to the model to try again, so what you are shown provably built. Then the Azure Quantum Resource Estimator. Physical qubits and runtime are what decide whether "advantage" means anything. |
| 4. How it ships, how we know it works | 6:30-8:00 | The deploy log line | Managed identity end to end, Container Apps, ACR, GitHub Actions - referring back to the prologue slide, not showing a second one. Then the honest bit: the deploy now posts a real prompt and fails if no Q# comes back, because the schema check never noticed the feature was dead. |

**Demo runs 6m30s**, inside Chris's 6-9 minute ceiling and the form's 5-8. Exact clock
times live in [script.md](script.md) - it is the only copy, because the last time a beat
sheet existed in two files the two drifted into describing different demos.

**Beat 1 is the live one.** It is the shortest call and the most interesting failure, so if
anything is going to be real on camera, make it that one.

**If you are running long, cut beat 3 to just the resource estimate** and drop the Q#
scroll. The estimator number is the quantum content; the generated source is decoration.

**Fallback:** if beat 1 fails live, switch to the pre-recorded run and keep talking. Have
it open before you start.


## 5. Slides

Two, both outside the demo. **Architecture in the prologue, 60 seconds** - Chris will stop
and restart the recording if slides run past 60-90s, and the form treats slides as part of
the prologue. A call-to-action slide closes the episode and is the last browser tab.

## 6. Resources for show notes

- Live site: https://wernerrall147.github.io/quantum-grand-challenges/
- Repo: https://github.com/WernerRall147/quantum-grand-challenges
- Methodology paper: DOI `10.5281/zenodo.19222021`
- Troyer et al., utility-scale quantum advantage criteria
- errorcorrectionzoo.org

## 7. Machine setup

From the production prep doc. Do this the day before, not on the day.

- [ ] Display card name and title decided (Chris asks for this ahead of the recording)
- [ ] Display 1920x1080, solid colour background
- [ ] Machine is current-gen - Chris warns a five-year-old laptop will struggle
- [ ] **Hardwired ethernet**, not Wi-Fi
- [ ] Headset **wired**, not Bluetooth
- [ ] Desktop widgets off
- [ ] Default browser opens to `about:blank`
- [ ] Hide the date in the taskbar, clock off
- [ ] Quiet Hours on
- [ ] Sign out of Outlook, Teams, and any messaging client
- [ ] Nothing confidential on the desktop or in open tabs
- [ ] Browser zoom set so the verdict and filters are legible at 1080p
- [ ] Second tab pre-loaded with the beat 2 result
- [ ] **Last** tab is the resources/call-to-action page - it becomes the closing background
- [ ] Fallback recording open and ready

## 8. Pre-flight

- [ ] No open GitHub issue labelled `uptime`
- [ ] Section 4 smoke test in `README.md` run ~15 min before
- [ ] All five prompts in `README.md` section 5 re-verified, verdicts match
- [ ] Site loads and does not show DEMO MODE

## 9. Notes on framing

- Engineer-to-engineer, not a pitch. Explain it as you would to a colleague.
- Do not say "by the time you see this". Record as though it publishes that day.
- Avoid date-sensitive claims; the episode airs weeks later.
