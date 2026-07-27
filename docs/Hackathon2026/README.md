# Microsoft Global Hackathon 2026 - Submission Scoping

**SUBMITTED 2026-07-27:**
https://innovation-studio.microsoft.com/events/hackathon2026/submissions/projects/proj-2ca74325-9d36-4557-8f55-9e9f7b5e3a42

- Executive Challenge: `Hack for Cloud Hardware Infra in the Era of AI`
- Topic Challenges: `Hack for Responsible AI`, `Tokenomics: The Zero-Waste AI Challenge`, `The Ambient Agent Challenge`

Working doc for the hackathon entry. Sections 1-5 map 1:1 to the submission form
fields. Section 6 onward is the actual scoping: what to build during hack week,
what is already done, and what is explicitly out of scope.

> Ground rule for this submission: the project's entire thesis is **honest claims**.
> Nothing in the write-up should overstate what has been demonstrated. That honesty
> is the differentiator, not a caveat.

---

## 1. Title  (max 140 chars)

Tuned for the Cloud Hardware Infra lens. Pick one:

- **`Quantum Advantage Evaluator - an AI agent that picks the right compute substrate, and proves it`**  (95)
- `Which hardware should this workload run on? Honest quantum vs AI vs HPC verdicts, with real qubit budgets`  (105)
- `The AI agent that tells you when NOT to use quantum`  (51)

Recommended: the first - it names the infrastructure decision *and* the evidence
angle. Keep the third in your back pocket; it is the line people repeat.

## 2. Tagline  (max 300 chars)

- **Primary (280):**
  `Choosing the wrong compute substrate is expensive. This Azure AI Foundry agent judges any workload against Troyer's utility-scale filters, returns an honest quantum / AI / HPC verdict with citations and real qubit-level resource estimates, then generates the Bicep to provision it.`

- **Alternate (198):**
  `Most "quantum advantage" claims collapse under scrutiny. This agent applies the same filters Microsoft's own quantum leadership uses, cites its sources, and tells you when classical hardware wins.`

## 3. Executive Challenge  (required, single select)

### SELECTED: `Hack for Cloud Hardware Infra in the Era of AI`

There is no quantum challenge in the list, and this is the right home: the project
answers a **compute infrastructure** question, not a physics one.

**The framing to lead with.** AI has made compute substrate choice the expensive
decision of the decade. Teams now choose between GPU fleets, classical HPC, and an
emerging quantum tier - and most "quantum advantage" claims collapse once you account
for error-correction overhead, data-loading cost, or a better classical algorithm.
Picking wrong wastes capital and years.

This agent is **capacity planning for the post-classical era**:

- It routes a workload to the substrate that actually wins - quantum, AI/ML, or HPC.
- It produces **hardware requirement models**: logical qubits, physical qubits,
  T-counts, error-correction overhead and projected runtime, via the Azure Quantum
  Resource Estimator.
- It quantifies the gap between today's hardware and the scale a workload truly needs
  (for example RSA-2048 needing ~4,000 logical qubits) so roadmaps are grounded.
- When the answer is classical, it **generates the Bicep** to provision the right
  Azure compute instead.

So the entry is not "we built a quantum thing" - it is *"we built the thing that stops
you buying the wrong hardware, and it shows its working."*

**Consequence for the build:** hardware requirement modelling is the headline, so the
real-resource-estimation work is the **primary** hack-week deliverable (section 7).

### Considered and rejected

| Option | Why not |
| --- | --- |
| `AI In Action: Agent Evaluations` | Strong fit for the honesty/evidence-gate story - keep as a Topic Challenge |
| `AI in Action: AI-Native Engineering` | Great origin arc, but a crowded category |
| `Hack for Industry - Energy & Resources` | Catalysis and photovoltaics fit, but the project is not industry-specific |
| `Other (will not be judged)` | never - explicitly unjudged |

## 4. Topic Challenges  (optional, up to 5)

The topic list is a different set from the executive challenges. Only three are a
genuine fit - **take those three and stop**. Padding with stretches makes the entry
look unfocused, and these are optional.

### 1. `Hack for Responsible AI`  - strongest fit, take this one

The project's entire thesis is calibrated honesty:

- Every verdict is returned **with peer-reviewed citations**, never bare confidence.
- A four-stage maturity gate model with **CI that fails the build** when a claim is
  not backed by evidence artifacts.
- **11 of 20 problem domains were honestly downgraded** and archived with reasons -
  published negative results.
- The agent's defining behaviour is *declining* to recommend quantum when the
  evidence does not support it.

An AI system engineered to refuse over-claiming is close to a textbook Responsible AI
entry.

### 2. `Tokenomics: The Zero-Waste AI Challenge`  - strong, two angles

- **Token level:** the Azure AI Foundry **model router** selects the cheapest capable
  model per query rather than sending everything to the largest one.
- **Compute level:** the whole product exists to prevent *wasted compute* - stopping
  teams from provisioning quantum or GPU capacity for workloads where cheaper
  classical hardware wins. Zero-waste at the infrastructure tier, which also dovetails
  with the Cloud Hardware Infra executive challenge.

### 3. `The Ambient Agent Challenge`  - legitimate, if slightly quieter

The `qgc-ingest-job` Container Apps Job runs nightly with no human in the loop:
pulling new arXiv papers, filtering for relevance, generating embeddings and
refreshing the knowledge base so the agent's answers stay current. A genuine ambient,
always-on agent rather than a request/response one.

### Skip these

| Option | Why |
| --- | --- |
| `AI-Native Digital Twin: From Device Design to Factory Reality` | You *could* argue quantum simulation is a digital twin of matter itself, but the challenge is aimed at device-to-factory - too much of a stretch |
| `Hack for Supply Chain Predictive Modelling` | Only tangential via optimisation workloads |
| `Hack for Windows Cloud Experience`, `AI for Quality and Reliability at Windows Servicing and Delivery`, `Hack for Families` | No connection |

> If the picker scrolls further than the eight visible options, also look for anything
> named around sustainability, scientific computing or infrastructure.

## 5. Keywords

```
quantum computing, Q#, Azure Quantum, Azure AI Foundry, AI agents, RAG,
resource estimation, responsible AI, Container Apps, Cosmos DB, Azure AI Search,
scientific computing, HPC, Bicep, honest benchmarking
```

---

## 6. Description  (max 30,000 chars - paste as markdown)

### The problem

AI has made **compute substrate choice** the expensive decision of the decade.
Infrastructure teams now weigh GPU fleets against classical HPC against an emerging
quantum tier, and "should we run this on a quantum computer?" has become a
board-level question with mostly hype for an answer.

Claimed quantum speedups repeatedly collapse once someone accounts for the constant
factors of error correction, the cost of loading classical data, or a better classical
algorithm published six months later. Meanwhile the honest comparison - *what hardware
would this actually need, and when will it exist?* - is rarely done, because it
requires resource estimation that most teams never run.

Picking the wrong substrate wastes capital and years.

### What we built

An AI agent that does **capacity planning for the post-classical era**. It gives an
honest verdict - quantum, AI/ML, or Azure HPC - and then generates the code and
infrastructure to actually run it.

Describe a workload in natural language. The agent:

1. Routes it against **Troyer's five utility-scale filters** (proven speedup? does
   I/O survive? does QEC survive? is it naturally quantum? is the crossover
   feasible?) and **DiVincenzo's five hardware-readiness criteria**.
2. Grounds every claim in a knowledge base of peer-reviewed arXiv papers, the
   Quantum Algorithm Zoo and the Error Correction Zoo - refreshed daily.
3. Produces **hardware requirement models** - logical qubits, physical qubits,
   T-counts, error-correction overhead and projected runtime - and quantifies the gap
   between today's machines and the scale the workload truly needs (RSA-2048, for
   instance, needs roughly 4,000 logical qubits).
4. Returns a verdict, a speedup class, red flags and **citations**, then generates
   **Q# code** for genuinely quantum workloads or a **Bicep template** to provision
   the right Azure compute when the answer is HPC or AI/ML.

It is designed to talk you *out* of quantum when the evidence says so. Ask it to
optimise a 500-asset portfolio and it returns `HPC_PREFERRED`. Ask it to train an
image classifier and it returns `AI_ML_PREFERRED`. Ask it to simulate the FeMoco
cofactor for nitrogen fixation and it returns `QUANTUM_ADVANTAGE` - with sources.

This is not "we built a quantum thing". It is the thing that stops you buying the
wrong hardware - and it shows its working.

### How it is built on Azure

| Layer | Service |
| --- | --- |
| Agent | Azure AI Foundry agent + **model router** (auto-selects the model per query), Code Interpreter and an MCP tool |
| API | Azure Container Apps, **managed identity end to end - no keys** |
| Knowledge | Cosmos DB + Azure AI Search (vector + semantic) |
| Ingestion | Container Apps Job on a nightly cron pulling new arXiv papers |
| Quantum | Q# / modern QDK, Azure Quantum resource estimation |
| Delivery | GitHub Actions CI/CD, Next.js dashboard |

### Why it is credible

This is not a weekend prototype dressed up as research.

- **20 problem domains** implemented in Q#, each with a classical baseline,
  parameterised instances and resource-estimation artifacts.
- **11 of the 20 were honestly downgraded** - archived with the reason recorded
  (I/O bottleneck, quadratic-only, QEC overhead). Publishing negative results is
  the point.
- A **four-stage maturity gate model (A -> D)** with **CI that fails the build**
  when an advantage claim is not backed by evidence artifacts. Policy as code, for
  scientific honesty.
- Methodology paper published with a DOI: `10.5281/zenodo.19222021`.

### Origin

It started as a single ChatGPT question in August 2025: *"What are the 20 hardest
problems in science, and could Q# help solve them?"* Roughly 300 commits later it is
a live, deployed Azure application. The whole arc - AI brainstorm to production
Azure agent - is itself the story.

### What we are adding for the hackathon

See section 7.

### Try it

- Live: https://wernerrall147.github.io/quantum-grand-challenges/
- Code: https://github.com/WernerRall147/quantum-grand-challenges

---

## 7. Hack-week scope

The platform already exists, so the entry must show a **crisp, demoable increment**.
Judges reward a sharp delta over a re-tour of existing work.

### Primary deliverable - real hardware requirement models

This is the headline for the Cloud Hardware Infra challenge, and it is the most
honest thing we can fix.

Today **51 estimate artifacts carry `"qdk_version": "mock"`**, and unrelated problems
report identical figures (toy H2 VQE and Shor N=15 both show 16 logical / 35,200
physical qubits). For a project whose thesis is honest resource accounting, this is
the single highest-value thing to fix - and it is very demoable.

- Replace mock artifacts with **real Azure Quantum Resource Estimator** runs for the
  active problems.
- Surface the real numbers in the evaluator's answers and on the website.
- Show a before/after: identical fake numbers -> genuinely different, defensible
  logical-qubit budgets per problem.

### Secondary deliverable - prove the agent is grounded

- Build an **evaluation harness** (Foundry evals) over a fixed set of problems with
  expected verdicts, so verdict quality is measurable, not anecdotal.
- Wire in tracing so a judge can watch a verdict being formed from its sources.

### Stretch

- Failure alerting on the nightly ingestion job.
- A "portfolio mode" that evaluates a list of workloads and ranks them by which are
  actually worth quantum investment.

### Explicitly out of scope

- New quantum algorithms or theory. This is a software-engineering and honest-
  assessment contribution.
- Running on real quantum hardware at utility scale.
- Any claim of demonstrated quantum advantage.

---

## 8. Demo plan (assume ~3 minutes)

1. Type a real problem, get an honest cited verdict. (hook)
2. Ask something the agent **declines** to send to quantum - portfolio optimisation.
   This is the money shot.
3. Show the model router picking a model live, and the daily-refreshed knowledge base.
4. Show the newly-real resource estimates.
5. Generate Q# / Bicep as the payoff.

## 9. Additional information (form section 2)

### Hacking On  (required, keyword field)

Type each and press Enter:

```
Azure Quantum, Azure AI Foundry, AI agents, quantum computing, resource estimation
```

If it only accepts one primary keyword, use **`Azure Quantum`** - it matches the
product field below and the Cloud Hardware Infra framing.

### Problem or opportunity statement  (max 200)

- **Primary (192):**
  `Choosing the wrong compute substrate wastes capital and years. Most quantum advantage claims collapse under scrutiny, and teams rarely run the resource estimates that would tell them the truth.`

- **Alternate (170):**
  `Teams are choosing between quantum, AI and HPC hardware with no honest evidence. Most quantum advantage claims collapse once error correction and data loading are counted.`

### Writing Code

`Yes`.

### Who is this for?  (required, single select)

Options are not visible until the picker opens. Choose in this order of preference:

1. Anything meaning **Customers / external customers** - the evaluator is open source
   and aimed at anyone weighing quantum against AI or HPC before they provision.
2. Otherwise **Everyone / Public**.
3. Avoid an internal-only option - it undersells the reach and weakens the Cloud
   Hardware Infra story.

- Selected: `[CONFIRM]`

### Venue

`I'll find my own place to hack`.

### Feature within an existing Microsoft product or service  (max 200)

`Azure Quantum` alone undersells it. Use (197):

`Azure Quantum - Resource Estimator, plus Azure AI Foundry. Could ship as a workload assessment experience in the Azure portal that routes customers to quantum, AI or HPC before they provision.`

### Briefly describe what you made and how you made it  (max 1000)

Ready to paste (966):

```
An Azure AI Foundry agent that decides which compute substrate a workload belongs on - quantum, AI/ML or HPC - and shows its working.

Describe a problem in plain language. The agent scores it against Troyer's five utility-scale filters and DiVincenzo's hardware criteria, grounds every claim in peer-reviewed arXiv papers plus the Quantum Algorithm and Error Correction Zoos, and returns a verdict with citations, red flags and qubit-level resource estimates. It then generates Q# for genuinely quantum workloads, or Bicep to provision the right Azure compute.

Built with Azure AI Foundry (agent, model router, tools), Container Apps with managed identity end to end, Cosmos DB and AI Search for RAG, a nightly Container Apps Job ingesting new arXiv papers, Q#/QDK with the Azure Quantum Resource Estimator, GitHub Actions and a Next.js dashboard.

20 domains implemented; 11 honestly downgraded and archived. CI fails the build when an advantage claim is not backed by evidence.
```

---

## 10. Pre-submission checklist

- [x] Title and tagline chosen and within limits
- [x] Executive Challenge selected (section 3)
- [x] Topic Challenges selected
- [x] Description pasted and previewed (markdown renders)
- [x] Keywords added
- [x] Additional information completed (section 9) - Hacking On, problem statement, audience, product, summary
- [ ] Live demo smoke-tested - see [../AzureFriday/README.md](../AzureFriday/README.md) section 4
- [ ] Screenshots or short clip attached (the project now exists, so images can be uploaded)
- [ ] Repo link and DOI included
- [ ] Update the submission once the real resource estimates land (section 7)
