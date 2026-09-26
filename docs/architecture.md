# Quantum Advantage Evaluator  Architecture & Project Plan

## Vision

Transform the Quantum Grand Challenges project into a **live AI-powered platform** that helps scientists and engineers determine the optimal compute path for their problem  **Quantum, AI/ML, or HPC**  on Azure. The evaluator applies Troyer's utility-scale filters, DiVincenzo's hardware-readiness criteria, and honest resource estimation to guide users toward building the right Azure workspace.

## Strategic Focus (April 2026)

The primary mission is now **optimizing the Evaluation Agent** to help users:
1. **Evaluate** their problem using the 6 utility-scale filters and the Troyer cost model
2. **Estimate** quantum resource requirements via Q# resource estimation
3. **Compare** against Azure HPC and AI/ML alternatives with real pricing and benchmarks
4. **Build** the right Azure workspace  Quantum (Azure Quantum), AI/ML (Azure AI Foundry), or HPC (Azure CycleCloud / NDv6 GPU clusters)

### Key Frameworks Applied
- **Troyer Utility-Scale Classification** (lecture series, nine parts published 2025-2026): the filters F1-F5 for honest quantum advantage assessment, with F6 from Moerchen et al., and the Part 6 cost model (published 2026-04-28, not yet applied by the evaluator)
- **DiVincenzo Criteria** (5+2): Hardware-realism overlay for quantum readiness  scalable qubits, initialization, coherence, universal gates, measurement
- **Error Correction Zoo** (errorcorrectionzoo.org): Comprehensive code taxonomy for QEC strategy selection (surface, color, QLDPC, bosonic codes)

### Industry Context
- Google Quantum AI expanding to dual-modality (superconducting + neutral atoms, Mar 2026)
- Google sets 2029 as its own PQC migration deadline (Mar 2026); Microsoft aims for quantum-safe capabilities by 2029 and a completed transition by 2033 (Aug 2025). Neither is a forecast of when a cryptographically relevant quantum computer will exist
- MIT efficient trapped-ion cooling advances chip-based QC scalability (Jan 2026)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        WEBSITE (Next.js)                           │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  Chat Interface  "Describe your quantum problem"             │ │
│  │  → Quantum vs HPC recommendation with confidence rating      │ │
│  │  → Generated Q# code + resource estimate + HPC comparison    │ │
│  └───────────────────────────┬───────────────────────────────────┘ │
└──────────────────────────────┼───────────────────────────────────────┘
                               │ API
┌──────────────────────────────▼───────────────────────────────────────┐
│                    EVALUATOR (Azure Container Apps)                  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ DETERMINISTIC ROUTER   agents/classifier/platform_router.py     │ │
│  │ Owns the verdict and the platform. Troyer filters F1-F6 are     │ │
│  │ evaluated in code, so identical input returns identical output. │ │
│  │ The model cannot overrule it.                                   │ │
│  └────────────────────────────┬───────────────────────────────────┘ │
│                               │ routing decision + KB context        │
│  ┌────────────────────────────▼───────────────────────────────────┐ │
│  │ LANGUAGE MODEL   model-router (per-request model selection)     │ │
│  │ Writes explanation, red flags, alternatives and references.     │ │
│  │ Disagreement with the router is recorded as model_dissent,      │ │
│  │ never applied. Citations must resolve before they are published.│ │
│  │                                                                 │ │
│  │ Two interchangeable paths, selected by QGC_USE_AGENT:           │ │
│  │   0  chat-completions       ~28s model time    << LIVE          │ │
│  │   1  Foundry prompt agent   ~52s model time                     │ │
│  │      quantum-advantage-orchestrator, adds Code Interpreter      │ │
│  │      and the Microsoft Learn MCP tool                           │ │
│  │                                                                 │ │
│  │ Model time, not end to end. Production requests took 23s median │ │
│  │ (286, 1-25 Sep 2026), and 36s (29) with code generation on.     │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  GENERATORS  agents/code_generator/ - invoked after the verdict,     │
│  ordinary Python modules, not agents.                                │
│    Q#    generated, then compiled and costed through the Azure       │
│          Quantum Resource Estimator (qdk.qre) in the request path    │
│          A failed compile is fed back to the model and retried, up   │
│          to 3 attempts. Code that never compiles is reported as a    │
│          failure, not rendered as output.                            │
│    Bicep generated, then validated with `az bicep build`             │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ MCP / Tools
┌──────────────────────────────▼───────────────────────────────────────┐
│                      KNOWLEDGE LAYER                                 │
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ SCIENTIFIC KB    │  │ ALGORITHM ZOO   │  │ REFERENCE CODE  │     │
│  │ (repo files +    │  │ (Indexed from   │  │ (GitHub MCP +   │     │
│  │  AI Search)      │  │  quantumalgo-   │  │  Q# samples)    │     │
│  │                 │  │  rithmzoo.org)  │  │                 │     │
│  │ • arxiv papers  │  │ • 47 algorithms │  │ • microsoft/qsharp│    │
│  │ • Daily ingest  │  │ • Speedup class │  │ • Proven patterns│     │
│  │ • Preprints     │  │ • Gate counts   │  │ • Azure samples  │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐                          │
│  │ MS DOCS MCP     │  │ ARXIV INGEST    │                          │
│  │ (Azure HPC      │  │ (Container Apps │                          │
│  │  specs, pricing) │  │  Job, daily)    │                          │
│  │ • VM specs      │  │ • quant-ph,cs.ET│                          │
│  │ • HPC clusters  │  │ • +4 abs terms  │                          │
│  │ • GPU benchmarks│  │ • Relevance gate│                          │
│  └─────────────────┘  └─────────────────┘                          │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ OUR 9 ACTIVE PROBLEMS  Reference implementations           │    │
│  │ QPE: Hubbard, Catalysis, Drug, Materials, Nuclear           │    │
│  │ Kept: Shor, QEC, Photovoltaics, QCD                        │    │
│  │ + 11 Archived in problems/archived/ with Troyer reasons     │    │
│  ├─────────────────────────────────────────────────────────────┤    │
│  │ ADDITIONAL KNOWLEDGE SOURCES                                │    │
│  │ • Error Correction Zoo (errorcorrectionzoo.org)             │    │
│  │ • Troyer Lecture Series (6 parts, quantum.microsoft.com)    │    │
│  │ • DiVincenzo Criteria (hardware-readiness overlay)          │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

## Component design

This is deliberately **not** a multi-agent system. Classification, fact-checking and
HPC comparison are roles, not security or team boundaries, and CAF guidance is to
reach for multiple agents only when such a boundary mandates separation. The verdict
is owned by a deterministic function, so splitting it across agents would hand a
scientific claim back to a stochastic model.

An earlier draft of this document described five collaborating Foundry agents. Only
one was ever deployed; the rest existed as YAML that nothing loaded. They were removed
rather than left to imply a system that did not exist.

### Deterministic router - `agents/classifier/platform_router.py`
- **Owns**: the verdict and the recommended platform. These are the claims the tool stands behind.
- **Method**: Troyer filters F1-F6 plus electronic-structure classification, evaluated in code.
- **Why in code**: a stochastic verdict made identical inputs return different answers.
- **Output**: platform, verdict, confidence, and the filter evidence behind them.

### Language model - `agents/orchestrator/evaluate.py`
- **Owns**: explanation, red flags, HPC/AI alternatives, references, similar problems,
  and a quadratic or no-advantage class. A strong class (exponential or superpolynomial)
  is a claim of advantage, so it is published only beside the router's QUANTUM_ADVANTAGE
  verdict and is taken from the match the router accepted
  (`published_advantage_class` in `agents/classifier/platform_router.py`).
- **Model**: Foundry `model-router`, which selects a model per request.
- **Contract**: `agents/orchestrator/output_schema.py` is the single definition of the
  response shape. `agents/tests/test_evaluator_smoke.py` fails the build if the prompt
  and the schema drift apart, which has happened twice.
- **Dissent**: if the model disagrees with the router it is recorded in `model_dissent`
  and reviewed. It never changes the result.
- **Citations**: `agents/orchestrator/citations.py` resolves every reference before
  publication. Both paths fabricate a source roughly 1 time in 22, and the agent path's
  Learn MCP tool did not prevent it, so verification happens at the source rather than
  being delegated to a tool.
- **Latency**: `model_seconds` is recorded on every evaluation.

### Q# generator and estimator - `agents/code_generator/`
- **Role**: generates Q#, compiles it, runs resource estimation.
- **Tools**: `qsharp` Python package, Azure Quantum Resource Estimator.
- **Pipeline**: pick the exemplar for the algorithm family → generate → compile → repair
  (up to three attempts) → estimate on four hardware profiles.
- **Exemplars**: `agents/code_generator/exemplars/` holds complete QPE and Shor programs,
  checked against exact results by `agents/tests/test_codegen_exemplars.py`. The evaluator
  names algorithms in prose, so the family is read from the text; an exact-key lookup had
  given every production request the same VQE code.
- **Repair**: gets the full compiler message, hints naming the correct form for the type
  errors that used to fail every attempt (`compiler_hints.py`), a check of called names
  against the standard library (`stdlib_index.py`), and the exemplar again.
- **Quantum work**: a program that compiles but uses fewer qubits than the algorithm needs
  is a classical placeholder. It is repaired like a compile error and, if it stays one, is
  reported with `quantum_work: false` and no estimate.
- **Threading**: the qsharp interpreter is thread-bound, so every compile and estimate runs
  on one dedicated thread (`agents/tests/test_codegen_threads.py`).
- **Measured**: `agents/evaluations/run_codegen_eval.py` runs the real pipeline on the
  production algorithm mix. On 2026-09-25 the deployed generator compiled 19 of 24 runs and
  produced 17 usable programs; this version compiled and produced usable programs in 24 of 24.

### Bicep generator - `agents/code_generator/`
- **Role**: for HPC and AI/ML verdicts, emits the Azure workspace template to provision instead.

### Foundry agent - `quantum-advantage-orchestrator`
- **Status**: provisioned and schema-bound, **not in the live request path**.
- **Tools**: Code Interpreter, Microsoft Learn MCP.
- **Why off**: measured at ~52s median against ~28s for chat-completions, and its only
  quality advantage disappeared once citations were verified at the source. It stays
  provisioned as the migration path for when a tool genuinely needs to be in the loop.
- **Switch**: `QGC_USE_AGENT` on the Container App, not a code change.

## Knowledge Base Design

### Committed data files (source of truth)
1. **knowledge/data/algorithm_zoo_index.json**  Quantum Algorithm Zoo entries with speedup classifications
2. **problems/reference_index.json**  our 9 active + 11 archived problems as reference examples

These are read directly by the knowledge base client. They were previously mirrored
into Cosmos DB, which has been retired: the mirror held nothing the files did not,
and could fail silently while the ingestion job still reported success.

### Azure AI Search - two indexes, only one decides

**`quantum-algorithms`** - 47 entries built from `algorithm_zoo_index.json`. Queried by
`kb_client.search_algorithms()` via hybrid keyword+vector search. This is the corpus every
verdict rests on. Regenerated by hand; `tooling/expand_algorithm_zoo.py` is in no workflow,
and the file was last generated 2026-04-18.

> How far behind that leaves it is now counted rather than guessed.
> `tooling/reconcile_algorithm_zoo.py` gives every one of the Zoo's 74 algorithms a
> disposition in `knowledge/data/zoo_reconciliation.json`: **31 matched**, **22 excluded**
> because a polynomial or constant-factor speedup fails F3 regardless, and **21 candidates**
> - of which **17 carry a superpolynomial or exponential claim**. Those 17 are problems the
> router structurally cannot answer QUANTUM for, however well the model reasons around it.
>
> The mapping had to be made by hand because no string match survives it: the Zoo names the
> problem, we name the algorithm or its author, so "Factoring" is our Shor's Algorithm and
> "Linear Systems" is our HHL. Only judgement calls are recorded; exact matches need no
> entry. From then on it is mechanical - an algorithm with no disposition fails the test
> suite, and a nightly job re-fetches the live Zoo so an upstream addition fails too. An
> index rename that orphans an alias fails as well, which is what stops a reconciled match
> quietly reverting to an untracked gap.

**`quantum-papers`** - 2,239 abstracts: 1,788 from the daily arXiv sweep and 451 curated
references pulled from the Quantum Algorithm Zoo's own bibliography. Read by
`kb_client.search_papers()`, which feeds the model a clearly-labelled block of recent work
and **never reaches the router**. Off by default behind `QGC_USE_PAPERS`.

> Two separate problems, both measured, neither fixed by adding more papers.
>
> **It leans quantum.** Re-measured 2026-08-24 across the five demo prompts: the strongest
> hits are portfolio optimisation (0.0323) and image classification (0.0323), the two that
> must be declined, while FeMoco, which must be accepted, scores 0.0290. Retrieval score
> runs against correctness, so no threshold separates them and the separation has to be
> structural. Adding 451 curated references did not shift this.
>
> **Most of it cannot state a speedup.** `tooling/measure_corpus_decidability.py` classifies
> every document: only 4.6% carry a claim the Troyer filters could read - 13.5% of the
> curated references against 2.3% of the daily sweep. The curated set wins despite shorter
> abstracts (966 chars against 1,386), so this is population, not length. References cited
> by an algorithm state that algorithm's scaling; the sweep returns application and NISQ
> work that makes no scaling claim. Over the five demo prompts retrieval returned 25 papers
> and none were decidable, which is exactly what 2.3% predicts.
>
> Coverage itself is fine now - Reiher arXiv:1605.03590 and Shor quant-ph/9508027 are both
> present since the Zoo ingest.

### Daily Ingestion Pipeline
- **arxiv**: `cat:quant-ph` and `cat:cs.ET` plus four abstract-term sweeps, paged, with
  inter-source delays to stay inside arXiv's rate limit
- **Filter**: keyword relevance only. There is no peer-review or citation-count filter;
  everything indexed is a preprint
- **Embed**: `text-embedding-3-large` over `abstract[:2000]`
- **Index**: upsert into `quantum-papers`; a partial write fails the run
- **Watch**: the sweep adds ~100 documents a day at 2.3% decidability, so it dilutes the
  corpus faster than it informs it. `tooling/measure_corpus_decidability.py` fails below a
  1% floor, which catches the sweep going to pure noise but not the slow dilution

## MCP Servers

### 1. Scientific Papers MCP (Custom)
Not built. The knowledge base client exposes `search_papers(query, top)` in-process; there
is no MCP server in front of it, and `get_paper`, `get_related_algorithms` and
`check_claims` do not exist in any form.

### 2. Algorithm Zoo MCP (Custom)
Not built either. The zoo is read from committed JSON through the knowledge base client;
`search_algorithms`, `get_algorithm` and `compare_classical` do not exist as MCP tools.
The only MCP in this system is Microsoft's public Learn server, which the Foundry agent
consumes - we did not author an MCP server.

### 3. GitHub MCP (Existing)
- Search `microsoft/qsharp` samples for reference implementations
- Ingest well-architected Q# patterns for code generation

### 4. Microsoft Docs MCP (Existing)
- Azure HPC VM specs, pricing, benchmarks
- Azure Quantum documentation
- Resource estimator parameters and qubit models

## Output Format

For each user-submitted problem, the system produces:

```json
{
  "problem_summary": "...",
  "verdict": "QUANTUM_ADVANTAGE" | "HPC_PREFERRED" | "AI_ML_PREFERRED" | "INCONCLUSIVE",
  "confidence": 0.0-1.0,
  "advantage_class": "exponential" | "superpolynomial" | "quadratic" | "none",
  "troyer_filters": {
    "F1_proven_speedup": true/false,
    "F2_io_survives": true/false,
    "F3_qec_survives": true/false,
    "F4_naturally_quantum": true/false,
    "F5_crossover_feasible": true/false,
    "F6_state_preparation": true/false
  },
  "red_flags": ["..."],
  "quantum_estimate": {
    "algorithm": "QPE / Shor / Grover / ...",
    "logical_qubits": N,
    "physical_qubits": N,
    "t_gates": N,
    "runtime_estimate": "..."
  },
  "hpc_comparison": {
    "best_azure_option": "ND96amsr_A100_v4",
    "estimated_runtime": "...",
    "estimated_cost": "$X",
    "classical_algorithm": "..."
  },
  "generated_qsharp": "// Q# code...",
  "references": ["arxiv:2301.12345", "..."],
  "similar_problems": ["09_factorization", "..."]
}
```

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Agent Framework | Azure AI Foundry + Agent Framework SDK | GenAIOps, hot-swappable agents |
| Knowledge Store | Repo files + Azure AI Search | Cosmos DB was retired in #156 - see below |
| Search | Azure AI Search | Vector + keyword hybrid search |
| Embeddings | Azure OpenAI (text-embedding-3-large) | Best-in-class for scientific text |
| Agent Model | GPT-4.1 / latest in Foundry | Reasoning over scientific content |
| Q# Runtime | qsharp Python package (pinned 1.31.0) | Resource estimation + compilation |
| Website | Next.js (existing) | Add chat component |
| MCP Servers | Python (FastAPI + MCP protocol) | Custom scientific + algo zoo servers |
| Daily Ingest | Azure Functions (timer trigger) | arxiv paper ingestion pipeline |
| CI/CD | GitHub Actions (later) | Not priority for now |

## Azure Resources Needed

| Resource | Purpose | Estimated Cost |
|----------|---------|----------------|
| Azure AI Foundry project | Agent hosting | Included in subscription |
| Azure OpenAI (GPT-4.1) | Agent model | ~$0.01/1k tokens |
| Azure OpenAI (embeddings) | Vector embeddings | ~$0.00002/1k tokens |
| Azure AI Search (Basic) | Hybrid search index | ~$75/month |
| Azure Functions | Daily ingestion | ~$0/month (consumption) |
| Application Insights | Request tracing (`qgc-eval-insights`) | ~$0/month (inside the 5 GB free grant) |
| Existing: Azure Quantum | Q# resource estimation | Already provisioned |

> **Cosmos DB is retired in code but still provisioned.** #156 removed every read and
> write, and this document said so in one place while two tables below still listed it as
> the knowledge store. The account `qgccosmoseval` in `qgc-evaluator` is nevertheless
> still deployed, `infrastructure/main.bicep` still creates one, and
> `agents/api/requirements.txt` still pins `azure-cosmos` because
> `knowledge/seed_knowledge_base.py` imports `CosmosClient` at module level and ships in
> the same image. Retiring the code is not the same as de-provisioning the resource, and
> until the account is removed the honest statement is that it exists and is unused.

## Observability

Every `POST /api/evaluate` returns a `trace`: each pipeline step, in order, with
what it decided. It needs no configuration and no portal round-trip, and it exists
to make the ordering claim above checkable rather than asserted - `route_platform()`
closes before the model span opens, or the trace says otherwise.

`agents/tests/test_trace_ordering.py` fails if any routing span starts after the
model call. `tooling/show_trace.py` draws the timeline and makes the same assertion
against a live API. When `APPLICATIONINSIGHTS_CONNECTION_STRING` is set the same
spans go to Application Insights under one `operation_Id` per request, which the
response returns so a call can be found in the portal.

Full detail, including the KQL: [tracing.md](tracing.md).

## Directory Structure

Kept honest by `tooling/test_architecture_claims.py`: every file named below must exist.
This tree previously listed seven files that were never written.

```
quantum-grand-challenges/
├── agents/
│   ├── orchestrator/
│   │   ├── agent.yaml               # GenAIOps agent definition (provisioned, off)
│   │   ├── instructions.py          # Deployed system prompt (single source)
│   │   └── evaluate.py              # The pipeline; route_platform runs before the model
│   ├── classifier/                  # Deterministic router, filters, cost model
│   ├── evaluations/                 # Router, narrative and Q# generation eval harnesses
│   ├── observability/
│   │   └── trace.py                 # Per-request spans; proves the router runs first
│   ├── api/                         # FastAPI app deployed to Container Apps
│   └── code_generator/
├── knowledge/
│   ├── data/
│   │   ├── algorithm_zoo_index.json # The 47 indexed algorithms
│   │   ├── zoo_references.json      # Curated citations behind the verdicts
│   │   └── zoo_reconciliation.json  # Aliases, exclusions, candidates for the Zoo's 74
│   ├── ingest/
│   │   ├── arxiv_ingester.py        # Daily arxiv paper fetcher
│   │   ├── algorithm_zoo_parser.py  # Hand-curated zoo entries, not a scraper
│   │   └── mit_xpro_ingester.py
│   ├── search/
│   │   └── kb_client.py             # Hybrid search wrapper
│   └── seed_knowledge_base.py       # Still imports CosmosClient at module level
├── infrastructure/
│   ├── main.bicep                   # All Azure resources, still creates Cosmos
│   ├── cosmos-deploy.json
│   └── openai-create.json
├── problems/                        # Reference implementations
│   ├── 01_hubbard/                  # 9 active, 11 archived
│   └── reference_index.json         # Maps problems to algorithm classes
├── website/
│   ├── pages/
│   │   ├── evaluate.tsx             # Problem evaluation page
│   │   ├── architecture.tsx
│   │   └── compare.tsx
│   └── components/
│       ├── CostReference.tsx
│       └── MermaidDiagram.tsx
├── tooling/                         # Estimation, validation and claim tests
└── docs/
    ├── architecture.md              # This file
    └── paper/                       # Methodology paper
```

## Implementation Phases

### Phase 1: Foundation (Completed)
- [x] Create project structure (agents/, knowledge/, infrastructure/)
- [x] Set up Cosmos DB (serverless) + AI Search (basic)
- [x] Build arxiv ingestion pipeline (Azure Function, daily timer)
- [x] Parse and index Quantum Algorithm Zoo
- [x] Create reference_index.json from our 9 active problems
- [x] Move 11 archived problems to problems/archived/ with Troyer reasons

### Phase 2: Agent Framework (Completed)
- [x] Deploy Azure AI Foundry project
- [x] Build the orchestrator as a Foundry prompt agent (provisioned; off by default)
- [x] Build the deterministic platform router (Troyer filters in code, owns the verdict)
- [x] Build Code Generator (Q# generation + qsharp.estimate())
- [x] Bind the agent to a single output schema and guard prompt/schema drift in CI
- [x] Verify citations resolve before publishing them
- [ ] Fact-Checker and HPC Comparator as separate agents - **dropped**, not built.
      Both were YAML that nothing loaded. Their function lives in the router, the
      citation verifier and the cost model.

### Phase 3: Knowledge Integration (Partially completed)
- [ ] Scientific Papers MCP server - **not built**, see above. `search_papers()` is called
      in-process; nothing sits in front of it.
- [ ] Algorithm Zoo MCP server - **not built**. No MCP server exists in this repo; a
      search for `*mcp*.py` returns nothing.
- [ ] GitHub MCP integration for Q# samples - **not attached**. `agent.yaml` attaches
      `code_interpreter` and `mcp:microsoft_learn`, and nothing else.
- [x] MS Docs MCP for Azure HPC specs - the public Learn MCP server is attached to the
      Foundry agent, which is **consumed, not authored**, and is off in production
      (`QGC_USE_AGENT=0`).
- [x] Daily ingestion pipeline live

### Phase 4: Website Integration (Completed)
- [x] Chat interface component (evaluate.tsx)
- [x] Agent API endpoint
- [x] Problem history display
- [x] Result visualization (quantum vs HPC comparison charts)

### Phase 5: Evaluator Optimization (Current  April 2026)
**Focus: Optimize the agent to guide users to the right Azure workspace**
- [ ] Integrate Troyer cost model (Part 6, published 2026-04-28: runtime times an amortized cost per module-hour) into evaluation pipeline
- [ ] Add Error Correction Zoo references for QEC strategy recommendations
- [ ] Add DiVincenzo criteria assessment to quantum recommendations
- [ ] Enhance workspace recommendation engine:
  - Quantum → Azure Quantum workspace setup guidance + resource estimates
  - AI/ML → Azure AI Foundry project setup + model selection guidance
  - HPC → Azure CycleCloud / NDv6 cluster sizing + SLURM configuration
- [ ] Add Google neutral atom / PQC timeline context to factorization assessments
- [ ] Integrate MIT trapped-ion advances into hardware roadmap projections
- [ ] Evaluation pipeline for agent quality (precision, recall, honesty metrics)
- [ ] Prompt versioning and A/B testing
- [ ] User feedback loop → knowledge base improvements

### Phase 6: Production Hardening
- [ ] Stage D promotions for 3 ready candidates (QAE, QAOA, DB Search)
- [ ] Stage B→C promotions for 9 active problems
- [ ] CI required status checks for reporting integrity
- [ ] Agent smoke tests with mocked backends in CI
- [ ] Cost-optimized model routing via model-router deployment
