# Deck notes - Quantum Advantage Evaluator

Two decks live here, because two different rooms need different things.

- **Section A** is the Azure Friday cut. Three slides. Chris caps *all* slide time at
  60-90 seconds and says the recording gets stopped and restarted if it runs over.
- **Section B** is speaker notes for the full 19-slide deck
  (`Azure Friday - Quantum Advantage Evaluator.pdf`), which is a good 30-45 minute
  session for a user group, internal brown-bag or conference breakout.

Every number below was verified on 2026-08-24. Where a number could not be verified it
says so, rather than being rounded up.

---

## Verified numbers - use these, not the ones in the current deck

| Claim | Status | Source |
|---|---|---|
| **47 algorithms indexed** | correct | `knowledge/data/algorithm_zoo_index.json`, `total_algorithms: 47`, array length 47 |
| **80 resource estimates** | corrected, deck says 160 | `iter_model_configs()` yields 4 configs x 20 problems |
| **20 problems, 9 active / 11 archived** | correct | `problems/`, `problems/archived/` |
| **Stage B 8, C 9, D 3** | correct | `docs/objective-kpis.json` |
| **100 Azure Quantum jobs, 70 succeeded** | **deck says "130+", unconfirmed** | `az quantum job list` returns exactly 100, which looks like a page cap |
| **~38s per evaluation** | correct, verdict only | 15 calls, 2026-08-24, median 38.0s, max 58.9s. Code generation is a separate, slower path |
| **214 tests passing** | correct | `pytest -q`, 2026-08-26 |

Two things to fix in the deck itself:

- Slide 2 says **160 resource estimates**. It is 80. The Majorana profiles and
  `floquet_code` were retired because QRE v3 does not realise them, which halved the count.
- Slide 17 says the repo is **"All Rights Reserved"**. `LICENSE` is **GNU AGPL v3**.

On **"130+ Azure Quantum runs"**: the CLI shows 100 jobs, 70 succeeded, 30 failed, spanning
2026-04-12 to 2026-06-10 with nothing since. 100 is suspiciously round so the real figure
may be higher, but two caveats matter on air. Roughly a third failed, and none are recent.
Safer phrasing: *"about a hundred jobs against Quantinuum and Rigetti simulators."* It is
true, checkable, and does not invite a follow-up you cannot answer.

---

# Section A - the Azure Friday cut (3 slides)

Chris's constraints, verbatim: 60-90 seconds of slide time total; not a feature parade;
a technical conversation between two engineers, not a Build or Ignite talk; do not plan
to talk nonstop for several minutes.

The storyboard already reached the right answer independently - *"One slide, used in
beat 4: the architecture diagram. Nothing else."* These three exist because slide 1
carries the title card and slide 3 is the closing background Chris asks for, so neither
costs narration time.

### Slide 1 - Title (on screen ~10s, while Scott introduces you)

> **Quantum Advantage Evaluator**
> An honest advisor: quantum, AI/ML, or HPC
>
> 20 problems - 9 still standing, 11 honestly downgraded
> 47 algorithms indexed - 80 resource estimates

Drop "130+ Azure Quantum runs" from the title card. It is the one number you cannot
defend if asked, and the 11-downgraded figure is a stronger opening anyway because it is
the whole point of the project.

### Slide 2 - Architecture (beat 4, 60-90s - this is your only real slide)

Use the diagram from `docs/architecture.md`, which was corrected in #196. Say four things
and stop:

1. The **verdict is deterministic**. Troyer's filters run in Python, not in the model.
   Same question, same answer, every time.
2. The **model explains and stress-tests** the verdict. If it disagrees, that is recorded
   as `model_dissent` and never applied.
3. **Retrieval needed a relevance gate.** Vector search returns a top hit for *every*
   query, so it was recommending quantum for image classification.
4. **Managed identity end to end.** No keys anywhere in the path.

### Slide 3 - Resources (last tab, becomes the closing background)

Chris explicitly asks for the last browser tab to be a call-to-action or resources page.
Make this a page, not a slide, and leave it open.

- Live: `wernerrall147.github.io/quantum-grand-challenges`
- Repo: `github.com/WernerRall147/quantum-grand-challenges` (AGPL-3.0)
- Paper: DOI `10.5281/zenodo.19222021`
- Troyer utility-scale criteria - `arXiv:2409.08910`
- `errorcorrectionzoo.org`

### What moves from slides into conversation

Everything else. Scott's questions are the format, and this material answers them well:

| If Scott asks | You have |
|---|---|
| "How do you stop it over-claiming?" | Deterministic router, `model_dissent`, the relevance gate story |
| "What are Troyer's filters?" | Slide 10's content, spoken over beat 1's wait |
| "Which problems did you drop?" | 11 archived with recorded reasons |
| "Has this run on real hardware?" | Simulators via Azure Quantum; be straight that hardware is blocked |
| "How did this start?" | One ChatGPT question, August 2025 |

---

# Section B - speaker notes for the full 19-slide deck

For a 30-45 minute session. Timings assume 40 minutes with 5 for questions.

### 1. Azure Friday programme cover (~15s)
Skip in any non-Azure-Friday setting.

### 2. Title + numbers (1 min)
Open with the honest framing: this is an advisor that tells you *not* to use quantum most
of the time. Use the verified numbers above. Say 20 problems, 9 still standing.

### 3. Origin - the ChatGPT conversation (2 min)
14 August 2025, one question: *what are the 20 hardest problems in science, and could Q#
help?* The useful admission is that the answer was optimistic about all 20, and the
project since has largely been finding out which of those were wrong.

### 4. Top 20 problems with Q# plans (3 min)
**Do not read this slide.** It is a reference artefact. Pick three: one that survived
(FeMoco, #2), one that did not (portfolio optimisation, #11), and one that surprised you.
Say plainly that this slide is the *original* optimism and that 11 have since been
downgraded - the slide is a before picture.

### 5. The people (1 min)
Troyer's utility-scale framework is the backbone of the filters; the 2024 F6 addition
(`arXiv:2409.08910`) separates class-1 electronic structure, where coupled cluster already
wins, from class-2 where it does not. FeMoco is the prototypical class-2 case. Keep this
about the *work*, not the org chart.

### 6-9. Qubits, gates, and solving with gates (6 min)
Know your room. Skip entirely for a quantum-literate audience. For a general developer
audience this is the most valuable part of the deck - superposition, entanglement,
measurement collapse, why a gate is a unitary. Bloch sphere first, then single-qubit
gates, then two-qubit.

### 10. DiVincenzo criteria (3 min)
Five criteria, used as a hardware-realism overlay: scalable qubits, initialisation,
coherence vs gate time, universal gate set, qubit-specific measurement. The point to land:
an algorithm passing Troyer's filters still fails if the hardware criteria are not met,
which is why "theoretically advantaged" and "runnable" are different claims.

### 11. The problems (3 min)
9 active, 11 archived with recorded reasons. The archive is the honest part - most
downgrades were quadratic speedups that do not survive error-correction overhead.

### 12. Solving problems (3 min)
The four-stage maturity gate model, A to D. Each stage has explicit evidence requirements
and CI rejects merges that claim a stage without the artefacts. Current spread: B 8, C 9,
D 3, and nothing sitting at A.

### 13. Compiling for Azure (3 min)
Q# to QIR via modern QDK (`qsharp 1.31.0`, no .NET dependency). 20 circuits validated on the
Quantinuum H2-1SC syntax checker.

### 14. Runs in Azure (3 min)
About a hundred jobs against Quantinuum H2-1E, H2-1SC and Rigetti QVM. Be straight that
roughly a third failed and that submission is currently blocked by a storage-account
network policy - it is a better story than a clean number, and it is true.

### 15. Architecture (4 min)
As Section A slide 2, with more room. Add the two-index point from the analysis below if
the audience is technical - it is a good honest-engineering story.

### 16. Stream this (1 min)
Light relief. Keep it short.

### 17. Like this (1 min)
Repo link. **Fix the licence line** - it is AGPL-3.0, not All Rights Reserved.

### 18-19. Study this / close (1 min)
QDK docs, Azure Quantum workspace setup, `errorcorrectionzoo.org`, the paper DOI.

---

# Why there are only 47 algorithms, and whether we have enough data

Short answer: **we have far more data than we use. The daily arXiv feed is not connected
to anything.**

There are two Azure AI Search indexes:

| Index | Written by | Read by |
|---|---|---|
| `quantum-algorithms` | `seed_knowledge_base.py`, from `algorithm_zoo_index.json` | `kb_client.search_algorithms()` -> the router -> **the verdict** |
| `quantum-papers` | `arxiv_ingester.py` daily, `mit_xpro_ingester.py` | **nothing** |

`QuantumKnowledgeBase` is constructed with `index_name="quantum-algorithms"` and never
queries `quantum-papers`. A grep for `quantum-papers` across the repo returns only the two
ingesters that write to it, the seeder that creates it, and a variable in `.env.template`.
`docs/architecture.md` line 173 documents a `search_papers(query, filters)` tool. That
function does not exist.

So:

1. **Verdicts come from 47 static entries.** `algorithm_zoo_index.json` was generated on
   2026-04-18 and has not been regenerated since. `tooling/expand_algorithm_zoo.py` is in
   no workflow - it is a manual tool nobody has run in four months.
2. **The daily arXiv job feeds an index nothing reads.** Over the last six days it has
   ingested between 11 and 79 relevant papers a day. We fixed it three times this month -
   #193 stale image, #194 pagination and the dead `cs.QC` source, #195 rate limiting - and
   every one of those fixes improved the throughput of a pipe that is not attached at the
   far end.
3. **Citations are not retrieved from our corpus.** They are model-generated and then
   link-checked (#188 stopped publishing ones that do not resolve). That is a real
   guarantee, but it is *resolvability*, not grounding in the indexed papers.

### What this means for the demo

Do not say the agent is grounded in a daily-updated corpus of arXiv papers. It is not.
What is true and still impressive:

- the verdict is deterministic and reproducible
- it is grounded in a curated, speedup-classified algorithm index
- citations are validated to resolve before publication

If Scott asks what is next, this is a genuinely good answer: *"the retrieval corpus and
the decision corpus are separate right now, and only one of them is wired in."*

### Fixing it - in rough order of value

1. **Wire `quantum-papers` into retrieval**, or stop the ingest job. Right now it is cost
   and complexity with no output. Wiring it in needs the same relevance gate the algorithm
   index needed in #159, because a paper index will also return a top hit for every query.
2. **Regenerate the algorithm zoo.** `quantumalgorithmzoo.org` lists several hundred; we
   index 47. That is where the erroneous "400+" in the architecture diagram came from - it
   was the size of the *source*, not of our index. Adding entries directly widens the set
   of problems that can get a confident verdict.
3. **Put the zoo regeneration in a workflow** so it cannot silently go four months stale
   again.
4. **Index more than abstracts.** Only the abstract is indexed (`abstract[:2000]`, in both
   the embedding and the stored document). Most abstracts fit well inside that cap, so the
   cap is not really the constraint - abstract-only is. The resource-estimate tables and
   methodology sections that would actually sharpen a verdict are never ingested at all.

None of this is needed before 3 September. The demo works and the verdicts are correct.
It is the honest answer to "what would you do next", which is a question Scott asks.

---

# Section C - the engineer track

Written after the prep call, where the failure mode was going broad on the problem domain
instead of the engineering. This is the material to pull from when Scott asks a question,
and the source for the beat narration. **Pick two or three. Do not recite it.**

The test for whether something belongs on air: *does it change a decision an engineer
would make, or is it background?* Quantum background is background.

## C1. The components, and what each one is actually doing

| Component | Doing what | The bit worth saying |
|---|---|---|
| **Container Apps** `qgc-eval-api` | Hosts the FastAPI evaluator | `minReplicas: 1`, so it never scales to zero. The ~38s is model inference, not a cold start - pre-warming would not help, which is why one beat is pre-loaded. |
| **AI Foundry model router** | Picks a model per request | Convenience with a sharp edge: it selects reasoning models, whose thinking counts against `max_completion_tokens`. That is a real, Azure-specific gotcha - see C3. |
| **AI Search** `qgcsearcheval` | Hybrid keyword + vector retrieval | Two indexes. `quantum-algorithms` (47 entries) feeds the router and decides verdicts. `quantum-papers` (2,239) is read by nothing that decides - deliberately, see C3. |
| **Managed identity** | Every Azure call | No keys anywhere in the app. Also the main operational risk: a governance job stripped the data-plane role once, silently. |
| **ACR** | Builds the image | Build context is not the repo. `.dockerignore` is a whitelist here, which bit us - C3. |
| **Container Apps Job** | Daily arXiv ingest | Runs, succeeds, and feeds an index nothing reads. Honest answer to "what would you cut". |
| **GitHub Actions** | Build, deploy, nightly checks, uptime probe | Deploy now includes a behavioural smoke test, not just a schema one. |
| **GitHub Pages** | The static front end | Next.js static export. Calls the Container App directly; falls back to DEMO MODE if that fails. |
| **Azure Quantum** | Resource estimation | The estimator runs in-process via `qdk.qre`. Hardware submission is currently blocked - C5. |

## C2. Good practices, with the evidence rather than the claim

- **The verdict is deterministic and the model cannot override it.** `route_platform()`
  runs before the model and never sees its output. Disagreement lands in `model_dissent`.
  A test pins the router's signature so papers cannot be passed into it by accident.
- **Pure functions for anything that decides.** `find_drift`, `reconcile`, `validate`,
  `classify_paper`, `sweep_is_pure_dilution` all take plain data and return plain data, so
  the tests drive them with synthetic cases instead of writing bad records into production.
- **Guards are verified by breaking something.** Every check added this month was watched
  failing first: the ledger with a disposition deleted, the index with HHL relabelled, the
  prompt-verifier pointed at LICENSE. A guard nobody has seen fail is not a guard.
- **Rules derived from the data, not invented.** The index validator's rules were tested
  against all 47 entries and only the ones that held were kept. One obvious candidate -
  `QUANTUM_ADVANTAGE` implies naturally quantum - is violated by 11 entries *correctly*,
  because Shor and friends are structural speedups. It is now pinned by a test so nobody
  adds it later.
- **Measure before adopting.** The Foundry agent path was dropped on latency (52s vs 38s
  median, n=22). The papers corpus was kept out of the decision path on a measurement, not
  a hunch. Numbers in the docs carry their sample size.
- **Reconciliation over inventory.** Every one of the Zoo's 74 algorithms must be matched,
  excluded with a reason, or counted as a gap. Anything undispositioned fails the build.
- **Citations resolved before they are shown.** The model proposes references; they are
  link-checked at the source. A fabricated source is worse than a slow answer.

## C3. Bad practices, and the debt still on the board

This is the half that makes the other half credible. Scott will respect it more than a
feature list.

- **Swallowing exceptions into empty strings.** `/api/evaluate` caught the code generator's
  failure and returned `qsharp_code: ""`. The site renders that field only when it is
  non-empty. So a dead feature and an unticked checkbox produced an identical page, with
  HTTP 200 throughout. **Q# generation was broken in production and nothing said so.**
- **Three faults stacked, each hiding the next.** `tooling/` was not in the image; then
  `.dockerignore` excluded the files added to fix it; then `max_completion_tokens=1500`
  let reasoning tokens eat the whole budget so the model returned nothing at all. Fixing
  one only revealed the next.
- **A guard that measured the wrong layer.** The test for the missing files read the
  Dockerfile, found the `COPY`, and passed - while the build could never succeed, because
  `.dockerignore` dropped those paths. Green check, impossible build.
- **Schema tests mistaken for behaviour tests.** The deploy checked that
  `/api/generate-bicep` was in the OpenAPI spec and that `bicep_template` was declared.
  Both true, both useless: they cannot notice that generation returns nothing.
- **The same bug fixed in one place and not the other.** The token-budget failure was
  already documented in `evaluate.py` and raised to 4000 there. `generate.py` sat at 1500
  and failed the same way, in the same repo.
- **A hand-edited file that every verdict rests on.** `algorithm_zoo_index.json` was last
  generated 2026-04-18 and its regeneration script is in no workflow.
- **An upserting seeder.** It writes by id without reconciling, so an id-scheme change
  orphaned a duplicate that then took ranks 1 *and* 2 of a top-3.
- **A pipeline attached at one end only.** ~100 papers a day into an index nothing reads,
  and only 2.3% of that sweep carries a claim the filters could use.

## C4. PRs and the GitHub side

370 commits, 173 merged PRs. Worth showing only if Scott asks how it is actually built.

- **Every change is a PR with five required checks**: build-and-test, quick-estimation,
  dependency-graph drift, secret hygiene, GitGuardian. Squash merge, delete branch.
- **The dependency graph is committed and drift-checked.** `docs/depgraph/` is regenerated
  from the tree; CI fails if it is stale. It exists so that deleting code is evidence-based
  rather than brave - it knows what is reachable from an entry point and what is not.
- **Nightly jobs check the things a PR cannot see**: the deployed search index against the
  committed file, and the live Quantum Algorithm Zoo against our reconciliation ledger, so
  an upstream addition becomes a build failure instead of a note in someone's head.
- **The commit message carries the measurement.** Over-claim rates, latency samples,
  confusion matrices go in the message, so `git log` is the record of what was true when.
- **The uptime probe opens a GitHub issue** labelled `uptime` when the live API fails a
  real evaluation, every 30 minutes.

## C5. The quantum piece, kept to what an engineer can use

- **Modern QDK, no .NET.** `qsharp.json` projects, `pip install qdk`, run from Python. The
  legacy `Microsoft.Quantum.Sdk` toolchain is gone.
- **Generated Q# is compiled and estimated in the request path.** Not emitted and hoped
  over - `qdk.qre` gives physical qubits and runtime across qubit models. That number is
  what makes "quantum advantage" falsifiable: RSA-2048 needs roughly 4,000 logical qubits.
- **80 resource estimates**, four qubit models against the surface code across 20 problems.
  Majorana and floquet codes were dropped because the current estimator does not realise
  them - worth saying if the deck's old "160" comes up.
- **11 of the 20 problems were honestly downgraded** on I/O, quadratic-only speedups or
  QEC overhead. That is the project's actual result and it is a negative one.
- **Hardware submission is currently blocked.** Azure Quantum job containers live in the
  managed storage account, which subscription policy holds disabled; every workaround was
  tested and none survived. Around a hundred jobs ran against Quantinuum and Rigetti
  simulators before that. Say it plainly if it comes up - it is a better story than a
  vague claim about hardware runs.

## C6. Likely questions, with the engineer answer

| Question | Answer to reach for |
|---|---|
| How do you stop it over-claiming? | Deterministic router, the relevance gate from C2, `model_dissent`, and the over-claim rate is measured: 1.7% on 358 labelled papers. |
| Why not just let the model decide? | It reaches different conclusions and we record them. Also the corpus it would read is one-sided - retrieval scores portfolio optimisation *above* FeMoco, so score runs against correctness. |
| What is the hardest bug you hit? | The empty string. Three stacked faults, HTTP 200 throughout, months undetected, and the smoke test that was supposed to catch it was asking a schema question. |
| Is this production-grade? | The verdict path is. The knowledge pipeline has real debt - C3 - and it is written down rather than papered over. |
| What would you do next? | Make the algorithm index a build artefact, and either wire the papers index into retrieval behind a relevance gate or stop paying for the job. |
| When does quantum actually arrive? | Not a date. The filters answer it per problem: strong speedup, I/O survives, QEC survives, naturally quantum, crossover feasible. Most things fail one of them. |
