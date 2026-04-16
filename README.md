# 🌌 Quantum Grand Challenges — Quantum Advantage Evaluator

*An AI-powered platform that evaluates whether your scientific problem is better solved on a quantum computer or Azure HPC — backed by peer-reviewed science, real resource estimation, and honest assessment.*

[![CI/CD](https://github.com/WernerRall147/quantum-grand-challenges/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/WernerRall147/quantum-grand-challenges/actions/workflows/ci-cd.yml)
[![Website](https://img.shields.io/badge/website-live-blue)](https://wernerrall147.github.io/quantum-grand-challenges/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19222021.svg)](https://doi.org/10.5281/zenodo.19222021)

## 🎯 What This Does

**Input**: Describe your quantum computing problem in natural language.

**Output**: An honest, science-backed evaluation:
- ✅ **Verdict**: Quantum advantage / HPC preferred / Inconclusive
- 📊 **Classification**: Exponential / superpolynomial / quadratic / no proven speedup
- 🔬 **Fact-check**: Troyer's 5 utility-scale filters applied (I/O, QEC, oracle costs)
- 💻 **HPC comparison**: What Azure HPC can do today vs. quantum requirements
- 🔧 **Q# code**: Generated implementation with resource estimates (optional)
- 📚 **References**: Peer-reviewed arxiv papers backing every claim

## 🏗️ Architecture

```
Scientist → Chat Interface → Orchestrator Agent
                                ├── Classifier (speedup class + Troyer filters)
                                ├── Fact-Checker (peer-reviewed validation)
                                ├── HPC Comparator (Azure HPC vs quantum)
                                └── Code Generator (Q# + resource estimation)
                                        ↓
                              Knowledge Layer (Cosmos DB + AI Search)
                                ├── arxiv papers (daily ingestion)
                                ├── Quantum Algorithm Zoo (400+ algorithms)
                                ├── GitHub Q# samples (MCP)
                                └── 9 reference implementations
```

See [docs/architecture.md](docs/architecture.md) for full architecture details.

## 🔬 Design Principles (from Dr. Matthias Troyer's Architecture Series)

Every evaluation applies **5 utility-scale filters**:

| Filter | Question | What kills advantage |
|--------|----------|---------------------|
| **F1** | Proven speedup? | VQE/QAOA: no proven advantage |
| **F2** | I/O survives? | Data loading O(N) erases speedup |
| **F3** | QEC survives? | Error correction overhead negates quadratic gains |
| **F4** | Naturally quantum? | Feynman criterion: is the problem inherently quantum? |
| **F5** | Crossover feasible? | Realistic problem size where quantum wins? |

## 📊 Reference Implementations

**9 active problems** that pass all Troyer filters:

| Problem | Algorithm | Speedup | Why It Survives |
|---------|-----------|---------|-----------------|
| Hubbard Model | **QPE** | Exponential | Naturally quantum Hamiltonian |
| Catalysis (H₂) | **QPE** | Exponential | Quantum chemistry — Troyer's #1 |
| Drug Discovery | **QPE** | Exponential | Pharmaceutical Hamiltonians |
| Factorization | **Shor** | Superpolynomial | Clean utility path (RSA-2048) |
| Materials | **QPE** | Exponential | Correlated materials beyond DFT |
| Error Correction | **QEC** | Infrastructure | Enables fault-tolerant computation |
| Nuclear Physics | **QPE** | Exponential | Many-body nuclear Hamiltonians |
| Photovoltaics | **Quantum Walk** | Exponential | Naturally quantum transport |
| QCD Lattice | **Trotter** | Exponential | Sign problem — genuinely hard |

**11 archived problems** with honest archival reasons (quadratic speedup negated by I/O, oracle cost, or QEC overhead).

## 🌐 Live Dashboard

Website: <https://wernerrall147.github.io/quantum-grand-challenges/>

## 🏁 Latest Milestone (April 2026)

- **9 active problems** after applying Dr. Matthias Troyer's utility-scale filters. 11 problems archived (quadratic speedup negated by I/O, oracle cost, or QEC overhead).
- **5 VQE→QPE upgrades** (Hubbard, Catalysis, Drug Discovery, Materials, Nuclear) — QPE provides exponential speedup for naturally quantum Hamiltonians.
- **4 kept as-is**: Shor (superpolynomial, clean utility path), QEC (infrastructure), Photovoltaics (naturally quantum), QCD (sign problem — exponential advantage).
- **Cross-platform emulator validation**: 20 problems on H2-1E (100 shots) + 19 on Rigetti QVM. 17/19 agree on dominant outcome.
- **120+ Azure Quantum runs** across 3 systems (Quantinuum H2-1SC, H2-1E, Rigetti QVM).
- **Multi-model resource estimation**: 160 estimates across 6 qubit technologies × 2 QEC schemes.
- **Noisy simulation study** across all 20 problems at 3 depolarizing error rates (0.001, 0.01, 0.05).
- Website live with Troyer utility-scale classification, multi-model charts, and archived problem badges.

Milestone notes: `docs/MILESTONE_2026_03_CLOSEOUT.md`.

## Completeness Gate Before Website Updates

Before updating website-facing data, run the full completeness gate:

```bash
python tooling/reporting/stage_kpis.py --out-md docs/objective-kpis.md --out-json docs/objective-kpis.json
python tooling/reporting/problem_runnable_correctness_audit.py --output tooling/reporting/problem_runnable_correctness_report.json
python tooling/reporting/audit_azure_run_history_metrics.py --min-resolved-coverage 0.85 --enforce-threshold
python tooling/reporting/validate_website_data_schema.py
cd website && npm run build
```

Execution plan: `docs/planning/completeness-execution-plan-2026-03-10.md`.

## 🎯 Quick Start

### Prerequisites

- **Python 3.11+** with `qsharp` package (`pip install qsharp`) — no .NET dependency
- **Azure CLI** (optional) with the Quantum extension for cloud submissions

### Development Environment

```bash
# Option 1: GitHub Codespaces (Recommended)
# Click "Open in Codespaces" for instant setup (installs Python 3.11, Node 18)

# Option 2: Local Development
git clone https://github.com/WernerRall147/quantum-grand-challenges.git
cd quantum-grand-challenges

# Install the modern QDK (Q# via Python — no .NET needed)
pip install qsharp numpy scipy matplotlib pandas
```

### Run a Problem

```bash
# Navigate to the currently implemented problem
cd problems/03_qae_risk

# Run the validated classical workflow
make classical        # Monte Carlo baseline + writes estimates/classical_baseline.json
make analyze          # Generates plots/ and a markdown summary

# Q# workflow (modern QDK — no .NET required)
make build           # Validates Q# compilation via qsharp Python package
make run             # Runs Q# entry point on local sparse-state simulator
make estimate        # Resource estimator harness
```

### Azure Auth + Run (QAOA, Microsoft Priority)

For Azure-backed QAOA workflows, auth is intentionally manual-gated to avoid accidental cloud submissions.

```bash
cd problems/05_qaoa_maxcut

# 1) Prepare env file (manual step)
cp .env.azure.example .env.azure.local
# Edit .env.azure.local and replace all CHANGE_ME values.

# 2) Validate local auth/workspace config
make validate-azure-env
make validate-azure-cli

# 3) Generate and validate Azure job manifest
make azure-manifest INSTANCE=small DEPTH=3 TARGET_ID=microsoft.estimator
make validate-azure-manifest INSTANCE=small DEPTH=3

# 4) After real Azure submission, stamp job id/status into the manifest
make azure-submit INSTANCE=small DEPTH=3 AZURE_MANUAL_JOB_ID=<azure_job_id>

# 4b) Or submit via Azure CLI using the manifest context (dry-run by default)
make azure-submit-auto INSTANCE=small DEPTH=3 TARGET_ID=microsoft.estimator AZURE_JOB_INPUT_FILE=<path/to/program.qir>
make azure-submit-auto INSTANCE=small DEPTH=3 TARGET_ID=microsoft.estimator AZURE_JOB_INPUT_FILE=<path/to/program.qir> AZURE_SUBMIT_EXECUTE=1

# 4c) One-command smoke path (preflight + manifest + submit; dry-run default)
make azure-smoke INSTANCE=small DEPTH=3 TARGET_ID=microsoft.estimator AZURE_JOB_INPUT_FILE=<path/to/program.qir>
make azure-smoke INSTANCE=small DEPTH=3 TARGET_ID=microsoft.estimator AZURE_JOB_INPUT_FILE=<path/to/program.qir> AZURE_SUBMIT_EXECUTE=1 AZURE_SMOKE_COLLECT=1

# 4d) Optional: regenerate smoke audit artifacts from current manifest
make azure-smoke-report INSTANCE=small DEPTH=3

# 5) After completion, stamp final result status
make azure-collect INSTANCE=small DEPTH=3 AZURE_RESULT_STATUS=succeeded

# Optional: fetch result status directly from Azure CLI
make azure-collect-auto INSTANCE=small DEPTH=3
```

Notes:

- `.env.azure.local` is intentionally ignored by git and must be created manually.
- Placeholder values are rejected by `make validate-azure-env`.
- Problem-specific details are documented in `problems/05_qaoa_maxcut/README.md`.

### Shared Azure Workflow (All Problems)

QAOA keeps its dedicated runbook, and a shared mechanism now exists for every `problems/XX_*` folder:

```bash
# Copy template into any problem-local env file
cp tooling/azure/.env.azure.example problems/03_qae_risk/.env.azure.local

# Run shared dry-run smoke (env + CLI + manifest + submit-preview + report)
python tooling/azure/smoke_problem.py \
  --problem 03_qae_risk \
  --instance small \
  --depth 1 \
  --env-file problems/03_qae_risk/.env.azure.local

# Works the same for other problems
python tooling/azure/smoke_problem.py \
  --problem 15_database_search \
  --instance small \
  --depth 1 \
  --env-file problems/15_database_search/.env.azure.local
```

Shared workflow docs: `tooling/azure/README.md`.

### Azure Secret Hygiene (Repo-Wide)

To prevent accidental secret commits across all problems:

- Every problem now has `problems/<problem>/.env.azure.example`.
- Local secret files must use `problems/<problem>/.env.azure.local` (ignored by git).
- CI enforces this with `.github/workflows/azure-secret-hygiene.yml`.

Run the same checks locally:

```bash
python tooling/azure/check_secret_hygiene.py
```

### Windows tips

- `make` works from PowerShell/CMD; we auto-detect `PYTHON=python` on Windows.
- If `python` is not found, install Python 3.11+ and ensure `python` is on PATH (disable Store alias if needed).
- Some helper targets (e.g., `make check-env`) use POSIX utilities; run from Git Bash/WSL if needed.
- For reliable local runs, bootstrap the shell first (sets UTF-8 output and optional headless plotting):

```powershell
. .\tooling\windows\bootstrap-env.ps1 -HeadlessPlots
```

- Run a full Windows validation sweep (all `classical`, `analyze`, and `build` targets):

```powershell
.\tooling\windows\validate-all.ps1
```

- Run QAE-specific helper actions without `make`:

```powershell
.\tooling\windows\qae-risk.ps1 -Action run -Instance small
.\tooling\windows\qae-risk.ps1 -Action analyze -Instance small
.\tooling\windows\qae-risk.ps1 -Action calibrate -Instance medium -CalibrationRuns 10
.\tooling\windows\qae-risk.ps1 -Action run -Instance small -Quick
.\tooling\windows\qae-risk.ps1 -Action analyze -Instance small -Quick
.\tooling\windows\qae-risk.ps1 -Action calibrate -Instance small -CalibrationRuns 3 -Quick
.\tooling\windows\qae-risk.ps1 -Action run -Instance small -Quick -NoBuild
```

- Run QAOA Max-Cut helper actions without `make`:

```powershell
.\tooling\windows\qaoa-maxcut.ps1 -Action run -Instance small
.\tooling\windows\qaoa-maxcut.ps1 -Action run-all
.\tooling\windows\qaoa-maxcut.ps1 -Action azure-runbook -Instance small -Depth 3
.\tooling\windows\qaoa-maxcut.ps1 -Action validate-azure-env -AzureEnvFile .env.azure.local
.\tooling\windows\qaoa-maxcut.ps1 -Action validate-azure-cli -AzureEnvFile .env.azure.local
.\tooling\windows\qaoa-maxcut.ps1 -Action azure-manifest -Instance small -Depth 3 -TargetId microsoft.estimator
.\tooling\windows\qaoa-maxcut.ps1 -Action azure-submit -Instance small -Depth 3 -AzureEnvFile .env.azure.local -AzureManualJobId <azure_job_id>
.\tooling\windows\qaoa-maxcut.ps1 -Action azure-submit-auto -Instance small -Depth 3 -TargetId microsoft.estimator -AzureEnvFile .env.azure.local -AzureJobInputFile <path\to\program.qir>
.\tooling\windows\qaoa-maxcut.ps1 -Action azure-submit-auto -Instance small -Depth 3 -TargetId microsoft.estimator -AzureEnvFile .env.azure.local -AzureJobInputFile <path\to\program.qir> -AzureSubmitExecute
.\tooling\windows\qaoa-maxcut.ps1 -Action azure-smoke -Instance small -Depth 3 -TargetId microsoft.estimator -AzureEnvFile .env.azure.local -AzureJobInputFile <path\to\program.qir>
.\tooling\windows\qaoa-maxcut.ps1 -Action azure-smoke -Instance small -Depth 3 -TargetId microsoft.estimator -AzureEnvFile .env.azure.local -AzureJobInputFile <path\to\program.qir> -AzureSubmitExecute -AzureSmokeCollect
.\tooling\windows\qaoa-maxcut.ps1 -Action azure-smoke-report -Instance small -Depth 3
.\tooling\windows\qaoa-maxcut.ps1 -Action azure-collect -Instance small -Depth 3 -AzureEnvFile .env.azure.local -AzureResultStatus succeeded
.\tooling\windows\qaoa-maxcut.ps1 -Action azure-collect-auto -Instance small -Depth 3 -AzureEnvFile .env.azure.local
.\tooling\windows\qaoa-maxcut.ps1 -Action evidence
.\tooling\windows\qaoa-maxcut.ps1 -Action evidence -Quick
```

- Run shared Azure workflow for any problem (single mechanism):

```powershell
.\tooling\windows\problem-azure.ps1 -Action smoke -Problem 03_qae_risk -Instance small -Depth 1 -EnvFile problems/03_qae_risk/.env.azure.local
.\tooling\windows\problem-azure.ps1 -Action smoke -Problem 15_database_search -Instance small -Depth 1 -EnvFile problems/15_database_search/.env.azure.local
```

`-Quick` lowers default `precision_bits` to `4` and `repetitions` to `24` for faster smoke tests.
Use `-NoBuild` with `-Action run` only when artifacts were already built.
For `qaoa-maxcut.ps1`, `-Quick` lowers defaults to `coarse_shots=12`, `refined_shots=48`, and `trials=3`.

- Run the complete local Windows pipeline (validation + mock estimator + website build):

```powershell
.\tooling\windows\run-all.ps1
```

- CMD wrappers are available too:

```bat
tooling\windows\validate-all.cmd
tooling\windows\run-all.cmd -SkipNpmInstall
tooling\windows\qaoa-maxcut.cmd -Action evidence -Quick
tooling\windows\qaoa-maxcut-quick.cmd
```

## 📊 Problem Status

**9 active** | **11 archived** (per Troyer utility-scale filters)

### Active Problems (pass all 5 Troyer filters)

| Problem | Algorithm | Speedup | Physical Qubits | Status |
|---------|-----------|---------|-----------------|--------|
| [Hubbard Model](problems/01_hubbard/) | **QPE** | Exponential | 132k | 🟢 Active (QPE) |
| [Catalysis (H₂)](problems/02_catalysis/) | **QPE** | Exponential | 132k | 🟢 Active (QPE) |
| [Drug Discovery](problems/07_drug_discovery/) | **QPE** | Exponential | 130k | 🟢 Active (QPE) |
| [Factorization](problems/09_factorization/) | **Shor** | Superpolynomial | 77k | 🟢 Active |
| [Materials Discovery](problems/14_materials_discovery/) | **QPE** | Exponential | 132k | 🟢 Active (QPE) |
| [Error Correction](problems/16_error_correction/) | **QEC** | Infrastructure | 1.8k | 🟢 Active |
| [Nuclear Physics](problems/17_nuclear_physics/) | **QPE** | Exponential | 132k | 🟢 Active (QPE) |
| [Photovoltaics](problems/18_photovoltaics/) | **Quantum Walk** | Exponential | 138k | 🟢 Active |
| [QCD Lattice](problems/19_quantum_chromodynamics/) | **Trotter** | Exponential | 131k | 🟢 Active |

### Archived Problems (Troyer filter failures)

| Problem | Original Algorithm | Archival Reason |
|---------|--------------------|-----------------|
| [QAE Risk](problems/03_qae_risk/) | QAE | Quadratic + I/O cost |
| [Linear Solvers](problems/04_linear_solvers/) | HHL | I/O bottleneck (state prep + readout) |
| [QAOA MaxCut](problems/05_qaoa_maxcut/) | QAOA | At most quadratic, no proven advantage |
| [HFT VaR](problems/06_high_frequency_trading/) | QAE | Quadratic + I/O |
| [Protein Folding](problems/08_protein_folding/) | QAOA | At most quadratic; AlphaFold dominates |
| [PQC Grover](problems/10_post_quantum_cryptography/) | Grover | Quadratic + oracle cost dominates |
| [QML Swap Test](problems/11_quantum_machine_learning/) | Swap Test | I/O bottleneck (data loading) |
| [Optimization](problems/12_quantum_optimization/) | QAOA | At most quadratic |
| [Climate HHL](problems/13_climate_modeling/) | HHL | I/O bottleneck |
| [DB Search](problems/15_database_search/) | Grover | Quadratic + QRAM cost |
| [Space Mission](problems/20_space_mission_planning/) | QAOA | At most quadratic |

## 🏗️ Repository Structure

```text
quantum-grand-challenges/
├── 📁 agents/                # AI agent definitions (GenAIOps)
│   ├── orchestrator/         # Main evaluator agent + prompts
│   ├── classifier/           # Troyer filter classifier
│   ├── fact_checker/         # Peer-review validation
│   ├── hpc_comparator/       # Azure HPC comparison
│   └── code_generator/       # Q# code generation
├── 📁 knowledge/             # Knowledge base management
│   ├── ingest/               # arxiv + algorithm zoo ingestion
│   ├── search/               # KB query client (Cosmos + AI Search)
│   └── data/                 # Algorithm zoo index
├── 📁 infrastructure/        # Azure resource definitions
│   ├── main.bicep            # Cosmos DB, AI Search, Functions
│   └── .env.template         # Endpoint configuration
├── 📁 problems/              # 9 active + 11 archived quantum problems
│   ├── 01_hubbard/ (QPE)     # Active: strongly-correlated systems
│   ├── 09_factorization/     # Active: Shor's algorithm
│   ├── 03_qae_risk/          # Archived: quadratic + I/O
│   └── reference_index.json  # Algorithm class mappings
├── 📁 website/               # Next.js dashboard + evaluator chat
│   └── pages/evaluate.tsx    # Quantum advantage evaluator UI
├── 📁 tooling/               # Resource estimation + reporting
└── 📁 docs/                  # Architecture + methodology paper
```

## 🚀 Try the Evaluator

### CLI (requires Azure credentials)

```bash
az login --tenant dc692f3e-104b-4247-b52c-23692694684a
export SEARCH_ADMIN_KEY=$(az search admin-key show --service-name qgcsearcheval --resource-group qgc-evaluator --query primaryKey -o tsv)

python agents/orchestrator/evaluate.py "Simulate the ground state energy of a 50-atom catalyst"
```

### Website

Visit the [Evaluate page](https://wernerrall147.github.io/quantum-grand-challenges/evaluate/) on the live dashboard.

## 🔧 Azure Resources

| Resource | Name | Purpose |
|----------|------|---------|
| Azure OpenAI | qgc-openai | GPT-5.4-mini + model-router + text-embedding-3-large |
| Cosmos DB | qgccosmoseval | Knowledge store (papers, algorithms, history) |
| AI Search | qgcsearcheval | Hybrid vector + keyword search |
| Azure Quantum | Quantum-Grand-Challenges | Q# resource estimation + emulators |

## 📖 Resources

- [Architecture Design](docs/architecture.md) — Full system design document
- [Methodology Paper](docs/paper/methodology-paper.md) (CC BY-NC-SA 4.0)
- [Troyer Architecture Series](https://quantum.microsoft.com/en-us/insights/industry-insights/quantum-architecture-series)
- [Q# Documentation](https://learn.microsoft.com/quantum/)
- [Quantum Algorithm Zoo](https://quantumalgorithmzoo.org/)

## 📄 License

**AGPL-3.0** — See [LICENSE](LICENSE). Methodology paper under CC BY-NC-SA 4.0.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
