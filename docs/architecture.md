# Quantum Advantage Evaluator  Architecture & Project Plan

## Vision

Transform the Quantum Grand Challenges project into a **live AI-powered platform** that helps scientists and engineers determine the optimal compute path for their problem  **Quantum, AI/ML, or HPC**  on Azure. The evaluator applies Troyer's utility-scale filters, DiVincenzo's hardware-readiness criteria, and honest resource estimation to guide users toward building the right Azure workspace.

## Strategic Focus (April 2026)

The primary mission is now **optimizing the Evaluation Agent** to help users:
1. **Evaluate** their problem using Troyer's 5 utility-scale filters and the Troyer cost model
2. **Estimate** quantum resource requirements via Q# resource estimation
3. **Compare** against Azure HPC and AI/ML alternatives with real pricing and benchmarks
4. **Build** the right Azure workspace  Quantum (Azure Quantum), AI/ML (Azure AI Foundry), or HPC (Azure CycleCloud / NDv6 GPU clusters)

### Key Frameworks Applied
- **Troyer Utility-Scale Classification** (6-part lecture series, 2025-2026): 5 filters (F1-F5) for honest quantum advantage assessment, plus upcoming cost model (Part 6)
- **DiVincenzo Criteria** (5+2): Hardware-realism overlay for quantum readiness  scalable qubits, initialization, coherence, universal gates, measurement
- **Error Correction Zoo** (errorcorrectionzoo.org): Comprehensive code taxonomy for QEC strategy selection (surface, color, QLDPC, bosonic codes)

### Industry Context
- Google Quantum AI expanding to dual-modality (superconducting + neutral atoms, Mar 2026)
- Google sets 2029 PQC migration timeline  CRQC expected end of decade
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
│                   AZURE AI FOUNDRY (Agent Hub)                       │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  ORCHESTRATOR │  │  FACT-CHECKER │  │  CODE-GEN    │              │
│  │  Agent        │→ │  Agent        │→ │  Agent       │              │
│  │              │  │              │  │              │              │
│  │ Routes problem│  │ Theory vs    │  │ Generates Q# │              │
│  │ to specialist │  │ reality check│  │ + runs RE    │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                        │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐              │
│  │  CLASSIFIER   │  │  HPC-COMPARE │  │  ESTIMATOR   │              │
│  │  Agent        │  │  Agent        │  │  Agent       │              │
│  │              │  │              │  │              │              │
│  │ Quantum class │  │ Azure HPC    │  │ qsharp RE    │              │
│  │ of advantage  │  │ benchmarks   │  │ + syntax chk │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                      │
│  GenAIOps: Hot-swappable agents, versioned prompts, eval pipelines  │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ MCP / Tools
┌──────────────────────────────▼───────────────────────────────────────┐
│                      KNOWLEDGE LAYER                                 │
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ SCIENTIFIC KB    │  │ ALGORITHM ZOO   │  │ REFERENCE CODE  │     │
│  │ (Cosmos DB +     │  │ (Indexed from   │  │ (GitHub MCP +   │     │
│  │  AI Search)      │  │  quantumalgo-   │  │  Q# samples)    │     │
│  │                 │  │  rithmzoo.org)  │  │                 │     │
│  │ • arxiv papers  │  │ • 400+ algos    │  │ • microsoft/qsharp│    │
│  │ • Daily ingest  │  │ • Speedup class │  │ • Proven patterns│     │
│  │ • Peer-reviewed │  │ • Gate counts   │  │ • Azure samples  │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ PROBLEM HISTORY  │  │ MS DOCS MCP     │  │ ARXIV MCP       │     │
│  │ (Cosmos DB)      │  │ (Azure HPC      │  │ (Daily paper    │     │
│  │                 │  │  specs, pricing) │  │  ingestion)     │     │
│  │ • User problems │  │ • VM specs      │  │ • cs.QC, quant-ph│    │
│  │ • Past results  │  │ • HPC clusters  │  │ • Filtered by   │     │
│  │ • Algorithm map │  │ • GPU benchmarks│  │   peer review   │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
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

## Agent Design (GenAIOps Pattern)

### Agent 1: Orchestrator
- **Model**: GPT-4.1 or latest available in Foundry
- **Role**: Routes incoming problems, manages conversation flow
- **Tools**: Calls other agents, accesses problem history
- **Swappable**: Yes  new routing logic hot-swapped via prompt versioning

### Agent 2: Quantum Advantage Classifier
- **Role**: Classifies the problem into:
  - **Proven speedup** (exponential, superpolynomial)  with specific algorithm match
  - **Quadratic only**  flags I/O and oracle cost limitations (Troyer filters)
  - **Heuristic/unproven**  warns about VQE/QAOA limitations
  - **No known advantage**  recommends HPC
- **Tools**: Scientific KB search, Algorithm Zoo lookup, Problem History
- **Output**: Classification + confidence + references

### Agent 3: Fact-Checker
- **Role**: Validates claims against peer-reviewed literature
- **Checks**:
  - Does the claimed speedup survive I/O costs? (Troyer filter F2)
  - Does it survive QEC overhead? (Troyer filter F3)
  - Is the oracle polynomial? (oracle cost filter)
  - Is there a better classical algorithm the user didn't consider?
- **Tools**: arxiv MCP, Algorithm Zoo, MS Docs MCP
- **Output**: Red flags, debunked claims, honest assessment

### Agent 4: HPC Comparator
- **Role**: Compares quantum resource estimate against Azure HPC options
- **Tools**: MS Docs MCP (Azure HPC specs, pricing), Azure VM catalog
- **Output**: "Your problem needs 132k physical qubits (not yet available) vs. an ND96amsr A100 cluster that can solve it in 3 hours for $X"

### Agent 5: Q# Code Generator + Estimator
- **Role**: Generates Q# implementation, runs resource estimation, syntax check
- **Tools**: GitHub MCP (Q# samples), qsharp Python package, Azure Quantum RE
- **Pipeline**: Generate → Compile → Estimate → Compare → Optional: Submit to Azure
- **Output**: Q# code, resource estimate, gate counts, qubit requirements

## Knowledge Base Design

### Cosmos DB Collections
1. **scientific_papers**  arxiv papers (cs.QC, quant-ph), daily ingested
2. **algorithm_zoo**  Quantum Algorithm Zoo entries with speedup classifications
3. **problem_history**  User-submitted problems and their evaluations
4. **reference_implementations**  Our 9 active + 11 archived problems as examples

### Azure AI Search Index
- Vector embeddings of papers + algorithm descriptions
- Hybrid search (keyword + semantic) for problem matching
- Faceted by: speedup class, qubit count range, algorithm family, year

### Daily Ingestion Pipeline
- **arxiv**: Fetch new cs.QC + quant-ph papers via arxiv API
- **Filter**: Only peer-reviewed or >10 citations (for preprints)
- **Embed**: Generate vector embeddings via Azure OpenAI
- **Index**: Upsert into AI Search + Cosmos DB

## MCP Servers

### 1. Scientific Papers MCP (Custom)
- `search_papers(query, filters)`  Semantic search over indexed papers
- `get_paper(arxiv_id)`  Fetch specific paper metadata + abstract
- `get_related_algorithms(problem_description)`  Find matching quantum algorithms
- `check_claims(claim_text)`  Validate a quantum advantage claim against literature

### 2. Algorithm Zoo MCP (Custom)
- `search_algorithms(problem_type)`  Find relevant quantum algorithms
- `get_algorithm(name)`  Get speedup class, gate counts, I/O requirements
- `compare_classical(algorithm, problem_size)`  Classical vs quantum complexity

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
  "verdict": "QUANTUM_ADVANTAGE" | "HPC_PREFERRED" | "INCONCLUSIVE",
  "confidence": 0.0-1.0,
  "advantage_class": "exponential" | "superpolynomial" | "quadratic" | "none",
  "troyer_filters": {
    "proven_speedup": true/false,
    "io_survives": true/false,
    "qec_survives": true/false,
    "naturally_quantum": true/false,
    "crossover_feasible": true/false
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
| Knowledge Store | Cosmos DB (NoSQL) | Flexible schema, global distribution |
| Search | Azure AI Search | Vector + keyword hybrid search |
| Embeddings | Azure OpenAI (text-embedding-3-large) | Best-in-class for scientific text |
| Agent Model | GPT-4.1 / latest in Foundry | Reasoning over scientific content |
| Q# Runtime | qsharp Python package (1.27+) | Resource estimation + compilation |
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
| Cosmos DB (serverless) | Knowledge store | ~$0.25/RU + storage |
| Azure AI Search (Basic) | Hybrid search index | ~$75/month |
| Azure Functions | Daily ingestion | ~$0/month (consumption) |
| Existing: Azure Quantum | Q# resource estimation | Already provisioned |

## Directory Structure

```
quantum-grand-challenges/
├── agents/                          # NEW: Agent definitions
│   ├── orchestrator/
│   │   ├── agent.yaml               # GenAIOps agent definition
│   │   ├── prompts/                  # Versioned system prompts
│   │   └── tools.py                  # Tool definitions
│   ├── classifier/
│   ├── fact_checker/
│   ├── hpc_comparator/
│   └── code_generator/
├── knowledge/                        # NEW: Knowledge base management
│   ├── ingest/
│   │   ├── arxiv_ingester.py        # Daily arxiv paper fetcher
│   │   ├── algorithm_zoo_parser.py  # Quantum Algorithm Zoo scraper
│   │   └── cosmos_loader.py         # Cosmos DB uploader
│   ├── search/
│   │   ├── index_schema.json        # AI Search index definition
│   │   └── search_client.py         # Hybrid search wrapper
│   └── mcp/
│       ├── scientific_papers_mcp.py # MCP server for papers
│       └── algorithm_zoo_mcp.py     # MCP server for algorithm zoo
├── infrastructure/                   # NEW: Azure resource definitions
│   ├── main.bicep                   # All Azure resources
│   ├── cosmos.bicep                 # Cosmos DB
│   ├── search.bicep                 # AI Search
│   └── foundry.bicep               # AI Foundry project
├── problems/                         # EXISTING: Reference implementations
│   ├── 01_hubbard/ (QPE)           # 9 active problems as examples
│   ├── ...
│   └── reference_index.json         # Maps problems to algorithm classes
├── website/                          # EXISTING: Add chat interface
│   ├── pages/
│   │   ├── evaluate.tsx             # NEW: Problem evaluation chat page
│   │   └── ...
│   └── components/
│       └── ChatInterface.tsx        # NEW: Embedded agent chat
├── tooling/                          # EXISTING: Keep estimation tools
└── docs/
    ├── architecture.md              # This file
    └── paper/                       # Existing methodology paper
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
- [x] Build Orchestrator agent with GenAIOps pattern
- [x] Build Classifier agent (Troyer filters as tools)
- [x] Build Fact-Checker agent (paper search + claim validation)
- [x] Build HPC Comparator agent (Azure VM specs via MS Docs MCP)
- [x] Build Code Generator agent (Q# generation + qsharp.estimate())

### Phase 3: Knowledge Integration (Completed)
- [x] Scientific Papers MCP server
- [x] Algorithm Zoo MCP server
- [x] GitHub MCP integration for Q# samples
- [x] MS Docs MCP for Azure HPC specs
- [x] Daily ingestion pipeline live

### Phase 4: Website Integration (Completed)
- [x] Chat interface component (evaluate.tsx)
- [x] Agent API endpoint
- [x] Problem history display
- [x] Result visualization (quantum vs HPC comparison charts)

### Phase 5: Evaluator Optimization (Current  April 2026)
**Focus: Optimize the agent to guide users to the right Azure workspace**
- [ ] Integrate Troyer cost model (Part 6, upcoming) into evaluation pipeline
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
