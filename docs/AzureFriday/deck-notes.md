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
| **~38s per evaluation** | correct | 10 calls, 2026-08-24, median 38.2s, max 46.4s |
| **116 tests passing** | correct | `pytest -q` |

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
