# Azure Friday storyboard - Quantum Advantage Evaluator

Submission draft. Paste into the storyboard form when the link arrives.

| | |
|---|---|
| **Working title** | The AI agent that talks you *out* of quantum computing |
| **Presenter** | Werner Rall |
| **Host** | Scott Hanselman |
| **Recording** | *(fill in the booked slot)* - virtual, via StreamYard |
| **Storyboard due** | One week before the recording. 2 Sept slot -> **26 Aug**. 3 Sept slot -> **27 Aug**. |
| **Show notes due** | 1-2 business days after recording |
| **Target length** | 10-12 min total, of which 6-8 min demo |

> The invitation email says 12-16 minutes; the production deck says 10-12. Build to
> **10-12** and the shorter number will not hurt you.

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
in science, and could Q# help?* A year and ~300 commits later it is running on Azure, and
11 of those 20 problems have been honestly downgraded.

## 2. Key takeaways

1. **An honest AI advisor needs a deterministic core.** The verdict comes from a rules
   engine over a curated algorithm database, not from the model. The model explains and
   stress-tests the decision; if it disagrees, that is recorded as `model_dissent` rather
   than allowed to change the answer. Same question, same answer, every time.
2. **Retrieval is not evidence.** Vector search returns a top hit for every query. Ours
   was confidently recommending quantum for image classification because the index
   returned a quantum algorithm, as it always will. Grounding needs a relevance gate.
3. **This is a pattern you can reuse** for any grounded, tool-using agent on Azure:
   AI Foundry agent + model router, AI Search for retrieval, Container Apps with managed
   identity, GitHub Actions to deploy.

## 3. Run of show

| Time | Segment | Content |
|---|---|---|
| 0:00-1:30 | Setup with Scott | The premise: should this be quantum? Why most answers are hype. Origin story in one line. |
| 1:30-8:00 | **Demo** (see below) | |
| 8:00-11:00 | Conversation | Ad hoc questions from Scott. Likely: how do you stop it over-claiming, what is Troyer's filter set, what would change the verdict, when does quantum actually arrive. |
| 11:00-12:00 | Takeaway | "This is how you build any grounded, tool-using Azure agent." |

## 4. Demo beat sheet

**A call takes ~51s and has been measured at 78s.** Azure Friday's own guidance is to
have a completed item to transition to rather than watch a spinner. So:

| Beat | Time | On screen | Notes |
|---|---|---|---|
| 1. The yes | 1:30-3:30 | Type the FeMoco prompt on the live site, submit | **Run this one live** so it is visibly real. Fill the wait by walking Troyer's six filters, which are the thing the audience needs to understand anyway. F6 is the 2024 addition and FeMoco is the paper's own prototype, which is a good line to land. Lands on `QUANTUM_ADVANTAGE`, 0.9 confidence, QPE, with citations. |
| 2. The no | 3:30-5:00 | Portfolio optimisation, 500 assets | **Pre-loaded in a second tab.** Say plainly that you ran it earlier. Explain why a quadratic speedup dies under QEC overhead. Lands on `HPC_PREFERRED`. This is the memorable beat. |
| 3. The payoff | 5:00-6:30 | Generated Q# and a Bicep template | It does not just judge, it hands you the workspace. |
| 4. The platform | 6:30-8:00 | Architecture, 1 slide | Foundry agent + model router, AI Search, Container Apps, managed identity, GitHub Actions. |

**If you are running long, cut beat 3 before beat 2.** The agent declining quantum is the
differentiator; code generation is table stakes.

**Fallback:** if beat 1 fails live, switch to a pre-recorded run of the same prompt and
keep talking. Have it open before you start.

## 5. Slides

One slide, used in beat 4: the architecture diagram. Nothing else.

## 6. Resources for show notes

- Live site: https://wernerrall147.github.io/quantum-grand-challenges/
- Repo: https://github.com/WernerRall147/quantum-grand-challenges
- Methodology paper: DOI `10.5281/zenodo.19222021`
- Troyer et al., utility-scale quantum advantage criteria
- errorcorrectionzoo.org

## 7. Machine setup

From the production prep doc. Do this the day before, not on the day.

- [ ] Display 1920x1080, solid colour background
- [ ] Default browser opens to `about:blank`
- [ ] Hide the date in the taskbar
- [ ] Quiet Hours on
- [ ] Sign out of Outlook, Teams, and any messaging client
- [ ] Nothing confidential on the desktop or in open tabs
- [ ] Browser zoom set so the verdict and filters are legible at 1080p
- [ ] Second tab pre-loaded with the beat 2 result
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
