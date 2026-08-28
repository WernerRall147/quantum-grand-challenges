# 🌌 Quantum Grand Challenges — Quantum Advantage Evaluator

*Describe a scientific problem in plain language. Get an honest verdict on whether it belongs on a quantum computer, on AI/ML, or on Azure HPC, with citations, resource estimates, and generated Q# or Bicep to build the right Azure workspace.*

[![CI/CD](https://github.com/WernerRall147/quantum-grand-challenges/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/WernerRall147/quantum-grand-challenges/actions/workflows/ci-cd.yml)
[![Website](https://img.shields.io/badge/website-live-blue)](https://wernerrall147.github.io/quantum-grand-challenges/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19222020.svg)](https://doi.org/10.5281/zenodo.19222020)

The evaluator says **no** more often than yes. That is the point: 11 of our own 20 problems are archived because they fail the filters.

---

## Start here

Pick the row that matches what you want to do.

| I want to... | Do this | Needs |
|---|---|---|
| **Try it, no setup** | Open the [live evaluator](https://wernerrall147.github.io/quantum-grand-challenges/evaluate/) | Nothing |
| **Run a problem locally** | [Run a problem](#run-a-problem) | Python 3.11+ |
| **Evaluate my own problem from the CLI** | [CLI evaluator](#cli-evaluator) | Python + `az login` |
| **Understand the science** | [How it decides](#how-it-decides) | Nothing |
| **Submit to real Azure Quantum** | [Azure runbooks](#azure-runbooks) | Azure subscription |

### Run a problem

```bash
git clone https://github.com/WernerRall147/quantum-grand-challenges.git
cd quantum-grand-challenges

# Modern QDK: Q# runs through Python, no .NET needed
pip install qdk numpy scipy matplotlib pandas

cd problems/01_hubbard
make classical    # Classical baseline
make analyze      # Plots and a markdown summary
make build        # Validate Q# compiles
make run          # Run on the local sparse-state simulator
make estimate     # Resource estimation
```

GitHub Codespaces works too: click **Open in Codespaces** for Python 3.11 and Node 18 preinstalled.

### CLI evaluator

`az login` is enough. AI Search is queried with your Entra identity, so no API key is needed. You need the `Search Index Data Reader` role on `qgcsearcheval`.

```bash
az login --tenant dc692f3e-104b-4247-b52c-23692694684a
python agents/orchestrator/evaluate.py "Simulate the ground state energy of a 50-atom catalyst"
```

> **Phrasing.** The knowledge base uses hybrid keyword plus vector search, so paraphrases of the same problem route the same way. `agents/evaluations/run_eval.py` enforces that. If vector search ever fails, the client logs a warning and reports `keyword-fallback`; treat verdicts from that mode with suspicion, because keyword-only ranking is measurably worse.

---

## What you get back

| | |
|---|---|
| ✅ **Verdict** | Quantum advantage / AI-ML preferred / HPC preferred / Inconclusive |
| 📊 **Classification** | Exponential / superpolynomial / quadratic / no proven speedup |
| 🔬 **Fact-check** | Troyer's six utility-scale filters applied |
| 🧱 **Hardware readiness** | DiVincenzo criteria assessment |
| 💻 **Platform comparison** | What Azure HPC, AI/ML and Quantum can do today |
| 🔧 **Workspace guidance** | Recommended Azure setup (Quantum / AI Foundry / CycleCloud) |
| 🏗️ **Code generation** | Q# for quantum problems, Bicep for HPC and AI/ML workspaces |
| 📚 **References** | Peer-reviewed arXiv papers plus Error Correction Zoo codes behind every claim |

---

## How it decides

### Troyer utility-scale filters

Every evaluation applies **six filters**. Failing any one is usually fatal to the quantum case.

| Filter | Question | What kills advantage |
|--------|----------|---------------------|
| **F1** | Proven speedup? | VQE/QAOA: no proven advantage |
| **F2** | I/O survives? | Data loading O(N) erases the speedup |
| **F3** | QEC survives? | Error-correction overhead negates quadratic gains |
| **F4** | Naturally quantum? | Feynman criterion: is the problem inherently quantum? |
| **F5** | Crossover feasible? | Is there a realistic problem size where quantum wins? |
| **F6** | Guiding state preparable? | Single-reference systems: coupled cluster already wins |

F6 comes from [arXiv:2409.08910](https://arxiv.org/abs/2409.08910) (Mörchen, Low, Weymuth, Liu, Troyer, Reiher). It separates class-1 electronic structure, where classical coupled cluster already resolves the problem, from class-2, where it does not. FeMoco is the prototypical class-2 case.

The verdict is **deterministic**. `agents/classifier/platform_router.py` computes it from the knowledge-base match and the filters. The language model writes the explanation; it does not choose the answer.

### DiVincenzo criteria (hardware readiness)

| Criterion | What it assesses |
|-----------|------------------|
| Scalable qubits | Can the physical system reach utility-relevant qubit counts? |
| Initialization | Can qubits be reliably prepared in a known state? |
| Coherence | Do coherence times exceed gate and measurement times? |
| Universal gates | Is a universal gate set available at acceptable fidelity? |
| Measurement | Can individual qubits be measured without disturbing others? |

### Error correction

QEC recommendations reference the [Error Correction Zoo](https://errorcorrectionzoo.org/), covering stabilizer, CSS, surface, color, QLDPC, bosonic and topological codes.

<details>
<summary><strong>Troyer lecture series</strong> (source material)</summary>

| Part | Topic | Date |
|------|-------|------|
| 1 | Utility-scale quantum applications | Nov 2025 |
| 2 | Utility-scale quantum architecture | Nov 2025 |
| 3 | Quantum Resource Estimation | Dec 2025 |
| 4 | High-performance quantum computing | Dec 2025 |
| 5 | Scalable quantum architecture | Apr 2026 |
| 6 | Balancing the Cost of Utility-Scale QC | Coming soon |

[Troyer Architecture Series](https://quantum.microsoft.com/en-us/insights/industry-insights/quantum-architecture-series)

</details>

---

## Problem status

**9 active, 11 archived**, judged by the filters above.

### Active: pass all six filters

| Problem | Algorithm | Speedup | Physical qubits | Frontier points |
|---------|-----------|---------|-----------------|-----------------|
| [Hubbard Model](problems/01_hubbard/) | **QPE** | Exponential | 54k | 9 |
| [Catalysis (H₂)](problems/02_catalysis/) | **QPE** | Exponential | 58k | 11 |
| [Drug Discovery](problems/07_drug_discovery/) | **QPE** | Exponential | 58k | 11 |
| [Factorization](problems/09_factorization/) | **Shor** | Superpolynomial | 53k | 8 |
| [Materials Discovery](problems/14_materials_discovery/) | **QPE** | Exponential | 163k | 10 |
| [Error Correction](problems/16_error_correction/) | **QEC** | Infrastructure | 2k | 1 |
| [Nuclear Physics](problems/17_nuclear_physics/) | **QPE** | Exponential | 58k | 11 |
| [Photovoltaics](problems/18_photovoltaics/) | **Quantum Walk** | Exponential | 47k | 10 |
| [QCD Lattice](problems/19_quantum_chromodynamics/) | **Trotter** | Exponential | 55k | 9 |

Qubit counts are the fewest-qubit point of each Pareto frontier. See [Reading the numbers](#reading-the-numbers).

### Archived: with the reason

| Problem | Original algorithm | Archival reason |
|---------|--------------------|-----------------|
| [QAE Risk](problems/archived/03_qae_risk/) | QAE | Quadratic plus I/O cost |
| [Linear Solvers](problems/archived/04_linear_solvers/) | HHL | I/O bottleneck (state prep and readout) |
| [QAOA MaxCut](problems/archived/05_qaoa_maxcut/) | QAOA | At most quadratic, no proven advantage |
| [HFT VaR](problems/archived/06_high_frequency_trading/) | QAE | Quadratic plus I/O |
| [Protein Folding](problems/archived/08_protein_folding/) | QAOA | At most quadratic; AlphaFold dominates |
| [PQC Grover](problems/archived/10_post_quantum_cryptography/) | Grover | Quadratic, oracle cost dominates |
| [QML Swap Test](problems/archived/11_quantum_machine_learning/) | Swap Test | I/O bottleneck (data loading) |
| [Optimization](problems/archived/12_quantum_optimization/) | QAOA | At most quadratic |
| [Climate HHL](problems/archived/13_climate_modeling/) | HHL | I/O bottleneck |
| [DB Search](problems/archived/15_database_search/) | Grover | Quadratic plus QRAM cost |
| [Space Mission](problems/archived/20_space_mission_planning/) | QAOA | At most quadratic |

---

## Reading the numbers

Three things are easy to misread. All three are real properties of the data, not caveats that go away with more effort.

**1. The estimate and the hardware run describe different programs.**
Resource estimates are of the `Main.*` expressions, the algorithm at utility scale. Azure Quantum submissions send `HardwareKernel.qs`, a small kernel sized to fit today's devices. A 54k-qubit estimate and a 2-bit run histogram on the same problem page are not two views of one circuit. Each `circuits/estimate.json` records both `entryExpr` and `hardwareKernelEntryPoint` so you can tell them apart.

**2. A resource estimate is a curve, not a number.**
The estimator returns a Pareto frontier of 8 to 11 configurations. The published figure is the fewest-qubit point, which is also the slowest. For Hubbard, 3.6x the qubits buys 2.8x the speed. The full curve is in `paretoFrontier` and plotted on each problem page.

**3. Stored emulator runs are dated.**
The Quantinuum and Rigetti histograms are from April 2026. Five problems (01, 02, 07, 14, 17) were upgraded from VQE to QPE afterwards, so their stored histograms describe kernels that no longer exist. The four unchanged problems agreed with ideal simulation to within a total variation distance of 0.01 to 0.17.

---

## Architecture

```
Scientist → Chat Interface → Evaluator API (Container Apps)
                                ├── Deterministic router — owns the verdict and platform
                                │     Troyer filters F1–F6 evaluated in code, not by the model
                                ├── Language model (Foundry model-router) — explanation,
                                │     red flags, alternatives, references. Disagreement is
                                │     recorded as model_dissent, never applied.
                                ├── Citation verifier — every reference must resolve
                                ├── Q# Code Generator (quantum problems → Q# + resource estimate)
                                └── Bicep Code Generator (HPC/AI/ML → Azure workspace template)
                                        ↓
                              Knowledge Layer (Azure AI Search)
                                ├── arXiv papers (daily ingestion)
                                ├── Quantum Algorithm Zoo (47 algorithms indexed)
                                ├── Error Correction Zoo (QEC code taxonomy)
                                └── 9 reference implementations
```

This is a single agent, not a swarm. Classification and fact-checking are roles rather
than security boundaries, and the verdict is owned by a deterministic function so that
identical input always returns identical output.

Full design: [docs/architecture.md](docs/architecture.md).

### Repository layout

```text
quantum-grand-challenges/
├── agents/                   # AI agent definitions (GenAIOps)
│   ├── orchestrator/         # Main evaluator agent + prompts
│   ├── classifier/           # Troyer filters + deterministic platform router
│   ├── evaluations/          # Router and narrative eval harnesses
│   └── code_generator/       # Q# and Bicep generation
├── knowledge/                # Knowledge base management
│   ├── ingest/               # arXiv + algorithm zoo ingestion
│   ├── search/               # KB query client (AI Search)
│   └── data/                 # Algorithm zoo index
├── infrastructure/           # Azure resource definitions
│   └── main.bicep            # AI Search, Functions (still creates a Cosmos account)
├── problems/                 # 9 active + 11 archived, each self-contained
│   ├── 01_hubbard/           # qsharp/ circuits/ python/ instances/ estimates/
│   └── archived/             # Filter failures, kept with their reasons
├── website/                  # Next.js dashboard + evaluator UI
├── tooling/                  # Estimation, circuits, Azure submission, reporting
└── docs/                     # Architecture + methodology paper
```

### Azure resources

| Resource | Name | Purpose |
|----------|------|---------|
| Azure OpenAI | qgc-openai | GPT-5.4-mini + model-router + text-embedding-3-large |
| Cosmos DB | qgccosmoseval | **Unused.** Retired from the code in #156; the account is still deployed |
| AI Search | qgcsearcheval | Hybrid vector + keyword search |
| Azure Quantum | Quantum-Grand-Challenges | Q# resource estimation + emulators |

---

## Azure runbooks

Azure submission is **manual-gated** throughout, so cloud jobs are never triggered by accident.

<details>
<summary><strong>Simulator and emulator matrix</strong> (all problems, all targets)</summary>

Target compatibility, established by compiling every kernel at both profiles:

| Target | Profile | Accepts | Notes |
|---|---|---|---|
| `quantinuum.sim.h2-1sc` | Adaptive_RI | 9 of 9 | Syntax checker; returns all zeros by design |
| `quantinuum.sim.h2-1e` | Adaptive_RI | 9 of 9 | Consumes eHQC quota |
| `rigetti.sim.qvm` | Base | 8 of 9 | |
| `ionq.simulator` | Base | 8 of 9 | |
| `pasqal.sim.emu-free` | n/a | 0 of 9 | Analog pulse format, cannot accept gate-model QIR |

`16_error_correction` is the one Base-profile targets reject: it branches on a mid-circuit syndrome measurement.

```bash
# Local baseline, no Azure needed
python tooling/run_simulator_matrix.py --local

# Submit to Azure targets
python tooling/run_simulator_matrix.py --targets ionq.simulator rigetti.sim.qvm
```

Job ids are written to the git-ignored `.azure/job-provenance.json`, never into published website data.

</details>

<details>
<summary><strong>Per-problem Azure workflow</strong> (env, manifest, submit, collect)</summary>

```bash
cd problems/archived/05_qaoa_maxcut

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

- `.env.azure.local` is git-ignored and must be created manually.
- Placeholder values are rejected by `make validate-azure-env`.
- Problem-specific details: `problems/archived/05_qaoa_maxcut/README.md`.

</details>

<details>
<summary><strong>Shared Azure workflow</strong> (one mechanism for every problem)</summary>

```bash
# Copy template into any problem-local env file
cp tooling/azure/.env.azure.example problems/archived/03_qae_risk/.env.azure.local

# Run shared dry-run smoke (env + CLI + manifest + submit-preview + report)
python tooling/azure/smoke_problem.py \
  --problem 03_qae_risk \
  --instance small \
  --depth 1 \
  --env-file problems/archived/03_qae_risk/.env.azure.local

# Works the same for other problems
python tooling/azure/smoke_problem.py \
  --problem 15_database_search \
  --instance small \
  --depth 1 \
  --env-file problems/archived/15_database_search/.env.azure.local
```

Docs: `tooling/azure/README.md`.

</details>

<details>
<summary><strong>Secret hygiene</strong> (enforced in CI)</summary>

- Every problem has `problems/<problem>/.env.azure.example`.
- Local secrets go in `problems/<problem>/.env.azure.local`, which is git-ignored.
- CI enforces this via `.github/workflows/azure-secret-hygiene.yml`.
- Published website data is swept for infrastructure identifiers (`job_id`, `subscription_id`, `resource_group`, `workspace_name`, `workspace`, `manifest_path`).

```bash
python tooling/azure/check_secret_hygiene.py
python tooling/reporting/validate_website_data_schema.py
```

</details>

<details>
<summary><strong>Windows helpers</strong> (PowerShell and CMD)</summary>

- `make` works from PowerShell and CMD; `PYTHON=python` is auto-detected on Windows.
- If `python` is not found, install Python 3.11+ and put it on PATH (disable the Store alias if needed).
- Some targets such as `make check-env` use POSIX utilities; run those from Git Bash or WSL.

Bootstrap the shell first (sets UTF-8 output and optional headless plotting):

```powershell
. .\tooling\windows\bootstrap-env.ps1 -HeadlessPlots
```

Full validation sweep (all `classical`, `analyze`, `build` targets):

```powershell
.\tooling\windows\validate-all.ps1
```

QAE-specific helpers without `make`:

```powershell
.\tooling\windows\qae-risk.ps1 -Action run -Instance small
.\tooling\windows\qae-risk.ps1 -Action analyze -Instance small
.\tooling\windows\qae-risk.ps1 -Action calibrate -Instance medium -CalibrationRuns 10
.\tooling\windows\qae-risk.ps1 -Action run -Instance small -Quick
.\tooling\windows\qae-risk.ps1 -Action analyze -Instance small -Quick
.\tooling\windows\qae-risk.ps1 -Action calibrate -Instance small -CalibrationRuns 3 -Quick
.\tooling\windows\qae-risk.ps1 -Action run -Instance small -Quick -NoBuild
```

QAOA Max-Cut helpers without `make`:

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

Shared Azure workflow for any problem:

```powershell
.\tooling\windows\problem-azure.ps1 -Action smoke -Problem 03_qae_risk -Instance small -Depth 1 -EnvFile problems/archived/03_qae_risk/.env.azure.local
.\tooling\windows\problem-azure.ps1 -Action smoke -Problem 15_database_search -Instance small -Depth 1 -EnvFile problems/archived/15_database_search/.env.azure.local
```

`-Quick` lowers default `precision_bits` to 4 and `repetitions` to 24 for faster smoke tests.
Use `-NoBuild` with `-Action run` only when artifacts were already built.
For `qaoa-maxcut.ps1`, `-Quick` lowers defaults to `coarse_shots=12`, `refined_shots=48`, `trials=3`.

Complete local Windows pipeline (validation + mock estimator + website build):

```powershell
.\tooling\windows\run-all.ps1
```

CMD wrappers:

```bat
tooling\windows\validate-all.cmd
tooling\windows\run-all.cmd -SkipNpmInstall
tooling\windows\qaoa-maxcut.cmd -Action evidence -Quick
tooling\windows\qaoa-maxcut-quick.cmd
```

</details>

<details>
<summary><strong>Completeness gate</strong> (run before updating website data)</summary>

```bash
python tooling/reporting/stage_kpis.py --out-md docs/objective-kpis.md --out-json docs/objective-kpis.json
python tooling/reporting/problem_runnable_correctness_audit.py --output tooling/reporting/problem_runnable_correctness_report.json
python tooling/reporting/audit_azure_run_history_metrics.py --min-resolved-coverage 0.85 --enforce-threshold
python tooling/reporting/validate_website_data_schema.py
cd website && npm run build
```

Execution plan: `docs/planning/completeness-execution-plan-2026-03-10.md`.

</details>

---

## Project status

Current as of August 2026.

| | |
|---|---|
| Active problems | 9, passing all six filters |
| Archived problems | 11, each with a stated filter failure |
| Azure Quantum jobs | 191 submitted, 147 succeeded, across H2-1SC, H2-1E and Rigetti QVM |
| Resource estimates | 141 unique, after deduplication |
| Algorithms indexed | 47 |
| Evaluator tests | 92 |

<details>
<summary><strong>Milestone history</strong></summary>

**August 2026**

- Troyer **F6** guiding-state filter added, derived from arXiv:2409.08910, and wired into the deterministic router so it can actually reject a verdict.
- Pareto frontiers retained and published. The estimator explores 8 to 11 configurations per problem where only one was previously kept.
- Circuit diagrams rendered from the kernels Azure Quantum actually receives.
- Five QPE kernels fixed: they measured without resetting, so they could not execute on a simulator at all.
- Estimates now declare which program they estimate, versus which one the hardware runs.

**April 2026**

- **Bicep workspace generation**: `BicepWorkspaceGenerator` produces deployable templates for HPC (CycleCloud + Slurm), AI/ML (Foundry hub + project) and Quantum (workspace + providers).
- **Agent triage**: auto-routes to Q# for quantum-advantage problems, Bicep for HPC and AI/ML.
- **Strategic pivot**: the evaluator guides users to build the right Azure workspace based on the Troyer assessment.
- **11 problems archived** with filter-failure reasons.
- **5 VQE to QPE upgrades** reclassified from heuristic to simulation-native.
- **Troyer assessment reconciled** with current algorithm assignments, 7 industry developments tracked.
- **Error Correction Zoo** integrated as a knowledge source.
- **Industry context**: Google dual-modality QC, Google 2029 PQC timeline, MIT trapped-ion cooling, MIT PQC chip for biomedical devices, World Quantum Day 2026.
- **Cross-platform emulator validation**: 20 problems on H2-1E (100 shots), 19 on Rigetti QVM.
- **Noisy simulation study** across all 20 problems at three depolarizing error rates (0.001, 0.01, 0.05).

Detail: `docs/MILESTONE_2026_03_CLOSEOUT.md`.

</details>

---

## Resources

- [Architecture design](docs/architecture.md), full system design
- [Methodology paper](docs/paper/methodology-paper.md) (CC BY-NC-SA 4.0)
- [Troyer Architecture Series](https://quantum.microsoft.com/en-us/insights/industry-insights/quantum-architecture-series), the six-part utility-scale framework
- [Q# documentation](https://learn.microsoft.com/quantum/)
- [Quantum Algorithm Zoo](https://quantumalgorithmzoo.org/)
- [Error Correction Zoo](https://errorcorrectionzoo.org/)
- [DiVincenzo criteria](https://en.wikipedia.org/wiki/DiVincenzo%27s_criteria)

## License

**AGPL-3.0**, see [LICENSE](LICENSE). Methodology paper under CC BY-NC-SA 4.0.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
