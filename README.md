# 🌌 Quantum Grand Challenges

*Systematic exploration of 20 of the world's most challenging scientific problems using quantum computing and AI-assisted development.*

[![CI/CD](https://github.com/WernerRall147/quantum-grand-challenges/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/WernerRall147/quantum-grand-challenges/actions/workflows/ci-cd.yml)
[![Website](https://img.shields.io/badge/website-live-blue)](https://wernerrall147.github.io/quantum-grand-challenges/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

This repository systematically tackles 20 of the world's most challenging scientific problems using **Microsoft Q# quantum computing** and **AI-assisted development**. Each problem follows a standardized structure for reproducible research, automated resource estimation, and comparative analysis with classical methods.

## 🌐 Live Dashboard

Website: <https://wernerrall147.github.io/quantum-grand-challenges/>

## 🎯 Quick Start

### Prerequisites

- **.NET 6.0 runtime/SDK** (*6.0.x only* – the QDK version we use does **not** support .NET 7/8)
- **Python 3.11+** with scientific computing stack
- **Azure CLI** (optional) with the Quantum extension for resource estimation experiments

### Development Environment

```bash
# Option 1: GitHub Codespaces (Recommended)
# Click "Open in Codespaces" for instant setup (installs .NET 6, Python 3.11, Node 18)

# Option 2: Local Development
git clone https://github.com/WernerRall147/quantum-grand-challenges.git
cd quantum-grand-challenges

# Verify .NET 6.0 is available (required for any Q# work)
dotnet --list-runtimes | findstr 6.0

# Optional: install IQ# tooling if you prefer Jupyter integration
dotnet tool install -g Microsoft.Quantum.IQSharp
```

### Run a Problem

```bash
# Navigate to the currently implemented problem
cd problems/03_qae_risk

# Run the validated classical workflow
make classical        # Monte Carlo baseline + writes estimates/classical_baseline.json
make analyze          # Generates plots/ and a markdown summary

# Q# workflow (requires local .NET 6)
make build           # dotnet build --configuration Release
make run             # Runs Program.qs entry point - produces analytical tail probability
make estimate        # Resource estimator harness (requires successful build)
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

Status labels are being migrated to a maturity-gate model so readiness claims stay aligned with validation depth.

**Maturity Gate Legend**

- **Stage A**: Classical baseline validated on defined instances.
- **Stage B**: Quantum scaffold or canonical algorithm implemented and building.
- **Stage C**: Hardware-aware validation complete (transpilation/mapping + uncertainty-bounded results + calibration evidence).
- **Stage D**: Advantage evidence package complete (assumptions, fair classical baseline, and claim category).

See `docs/objective-gates.md` for gate criteria and the required advantage-claim template.

| Problem | Q# Implementation | Classical Baseline | Resource Estimation | Status |
|---------|-------------------|--------------------|---------------------|--------|
| [QAE Risk Analysis](problems/03_qae_risk/) | ✅ **Canonical QAE with Grover + QPE** | ✅ Complete (Monte Carlo + plots) | ✅ **Complete** (594k qubits, 6.4s, 965k T-states) | 🟢 **Stage C complete; Stage D evidence hardening next** |
| [Hubbard Model](problems/01_hubbard/) | ✅ Analytical placeholder builds under .NET 6 | ✅ Complete (exact diagonalization) | ⏳ Pending | 🟡 **Stage B complete; Stage C not started** |
| [Catalysis Simulation](problems/02_catalysis/) | ✅ Analytical baseline builds under .NET 6 | ✅ Complete (Arrhenius rates + plots) | ⏳ Pending | 🟡 **Stage B complete; Stage C not started** |
| [Linear Solvers](problems/04_linear_solvers/) | ✅ Analytical baseline builds under .NET 6 | ✅ Complete (condition analysis + plots) | ⏳ Pending | 🟡 **Stage B complete; Stage C not started** |
| [QAOA MaxCut](problems/05_qaoa_maxcut/) | ✅ Analytical baseline builds under .NET 6 | ✅ Complete (graph cuts + plots) | ⏳ Pending | 🟢 **Stage C complete; Stage D evidence hardening next** |
| [High-Frequency Trading](problems/06_high_frequency_trading/) | ✅ Analytical baseline builds under .NET 6 | ✅ Complete (portfolio optimization) | ⏳ Pending | 🟡 **Stage B complete; Stage C not started** |
| [Drug Discovery](problems/07_drug_discovery/) | ✅ Analytical baseline builds under .NET 6 | ✅ Complete (molecular docking + plots) | ⏳ Pending | 🟡 **Stage B complete; Stage C not started** |
| [Protein Folding](problems/08_protein_folding/) | ✅ Analytical baseline builds under .NET 6 | ✅ Complete (contact maps + plots) | ⏳ Pending | 🟡 **Stage B complete; Stage C not started** |
| [Factorization](problems/09_factorization/) | ✅ Analytical baseline builds under .NET 6 | ✅ Complete (Pollard's rho + plots) | ⏳ Pending | 🟡 **Stage B complete; Stage C not started** |
| [Post-Quantum Cryptography](problems/10_post_quantum_cryptography/) | ✅ Analytical baseline builds under .NET 6 | ✅ Complete (attack cost analysis) | ⏳ Pending | 🟡 **Stage B complete; Stage C not started** |
| [Quantum Machine Learning](problems/11_quantum_machine_learning/) | ✅ Analytical baseline builds under .NET 6 | ✅ Complete (kernel methods + plots) | ⏳ Pending | 🟡 **Stage B complete; Stage C not started** |
| [Quantum Optimization](problems/12_quantum_optimization/) | ✅ Analytical baseline builds under .NET 6 | ✅ Complete (scheduling + plots) | ⏳ Pending | 🟡 **Stage B complete; Stage C not started** |
| [Climate Modeling](problems/13_climate_modeling/) | ✅ Analytical baseline builds under .NET 6 | ✅ Complete (energy balance + plots) | ⏳ Pending | 🟡 **Stage B complete; Stage C not started** |
| [Materials Discovery](problems/14_materials_discovery/) | ✅ Analytical baseline builds under .NET 6 | ✅ Complete (cluster expansion + plots) | ⏳ Pending | 🟡 **Stage B complete; Stage C not started** |
| [Database Search](problems/15_database_search/) | ✅ Canonical Grover implementation builds under .NET 6 | ✅ Complete (query complexity + plots) | ⏳ Pending | 🟢 **Stage C complete; Stage D evidence hardening next** |
| [Error Correction](problems/16_error_correction/) | ✅ Analytical baseline builds under .NET 6 | ✅ Complete (repetition codes + plots) | ⏳ Pending | 🟡 **Stage B complete; Stage C not started** |
| [Nuclear Physics](problems/17_nuclear_physics/) | ✅ Analytical baseline builds under .NET 6 | ✅ Complete (EFT diagonalization + plots) | ⏳ Pending | 🟡 **Stage B complete; Stage C not started** |
| [Photovoltaics](problems/18_photovoltaics/) | ✅ Analytical baseline builds under .NET 6 | ✅ Complete (Shockley-Queisser + plots) | ⏳ Pending | 🟡 **Stage B complete; Stage C not started** |
| [Quantum Chromodynamics](problems/19_quantum_chromodynamics/) | ✅ Analytical baseline builds under .NET 6 | ✅ Complete (lattice gauge + plots) | ⏳ Pending | 🟡 **Stage B complete; Stage C not started** |
| [Space Mission Planning](problems/20_space_mission_planning/) | ✅ Analytical baseline builds under .NET 6 | ✅ Complete (orbital mechanics + plots) | ⏳ Pending | 🟡 **Stage B complete; Stage C not started** |

## 🏗️ Repository Structure

```text
quantum-grand-challenges/
├── 📁 problems/              # Individual quantum challenges
│   ├── 01_hubbard/          # Strongly correlated systems
│   ├── 02_catalysis/        # Chemical reaction catalysis
│   ├── 03_qae_risk/         # ✅ Quantum amplitude estimation
│   ├── 04_linear_solvers/   # HHL algorithm applications
│   ├── 05_qaoa_maxcut/      # Quantum approximate optimization
│   ├── 06_high_frequency_trading/ # Quantum-enhanced market simulation
│   ├── 07_drug_discovery/   # Quantum chemistry for docking refinement
│   ├── 08_protein_folding/  # Quantum-assisted folding and conformational search
│   ├── 09_factorization/    # Shor's algorithm scaffold for RSA-style moduli
│   ├── 10_post_quantum_cryptography/ # PQC attack surface evaluation
│   ├── 11_quantum_machine_learning/ # Quantum kernel and hybrid ML benchmarking
│   └── ...                  # 15 additional challenges
├── 📁 libs/                 # Shared quantum algorithms
│   └── common/Utils.qs      # QFT, Grover, state preparation
├── 📁 tooling/              # Development infrastructure
│   ├── estimator/           # Azure Quantum resource estimation
│   ├── schema/              # Standardized result formats
│   └── ci/                  # Continuous integration scripts
├── 📁 website/              # Next.js visualization dashboard
└── 📁 .devcontainer/        # Codespaces development environment
```

### Standard Problem Structure

Each problem follows this consistent layout:

```text
problems/XX_problem_name/
├── 📄 README.md             # Problem description & results
├── 📁 qsharp/               # Q# quantum implementation
│   ├── Program.qs           # Main quantum algorithm
│   ├── *.csproj             # Project configuration
│   └── bin/                 # Compiled executables
├── 📁 python/               # Classical analysis & visualization
│   ├── analysis.py          # Performance comparison
│   ├── baseline.py          # Classical algorithm baseline
│   └── requirements.txt     # Python dependencies
├── 📁 instances/            # Problem parameter sets
│   ├── small.yaml           # Development/testing
│   ├── medium.yaml          # Benchmark instances
│   └── large.yaml           # Challenge instances
├── 📁 estimates/            # Resource estimation results
│   ├── logical_resources.json
│   ├── physical_resources.json
│   └── error_budget.json
└── 📄 Makefile             # Automated build & analysis
```

## 🌟 Key Features

### 🔧 Development Infrastructure

- **Automated CI/CD**: GitHub Actions validates Python baselines, attempts Q# builds under .NET 6, runs JSON schema checks, and publishes the dashboard
- **Resource Estimation Ready**: Tooling and nightly workflows are wired for Azure Quantum Resource Estimator profiles once real kernels land
- **Standardized Schema**: Shared JSON contract enables apples-to-apples comparison across all 20 challenges
- **Codespaces Ready**: Devcontainer provisions .NET 6, Python 3.11, Node 18, Azure CLI + quantum extension, and Next.js tooling out of the box
- **Case-Study Dashboard**: The GitHub Pages site now surfaces live highlights, reproducibility commands, and roadmap context

### 📈 Analysis Pipeline

Each problem follows this workflow:

1. **Classical Baseline**: Deterministic Python pipeline (`make classical`) produces JSON metrics
2. **Visualization & Reporting**: `make analyze` emits plots and summaries for the dashboard
3. **Q# Placeholder / Kernel**: Matching Q# project (`make build`) keeps the quantum interface ready for upgrades
4. **Resource Estimation**: Azure Quantum profiles (manual today, automated via nightly sweeps tomorrow)
5. **Website Publication**: CI packages outputs into the Next.js dashboard for reproducibility and storytelling

### 🎯 Objective Maturity Gates

To level up from implementation to evidence-backed outcomes, each problem should pass these gates in order:

1. **Stage A (Classical baseline)**: deterministic baseline, instance coverage, and reproducible metrics.
2. **Stage B (Quantum implementation)**: compiling Q# kernel/scaffold with documented algorithm assumptions.
3. **Stage C (Hardware-aware validation)**: topology-aware mapping impact, error/calibration trends, and uncertainty-bounded comparisons.
4. **Stage D (Advantage evidence)**: explicit claim contract (`theoretical`, `projected`, or `demonstrated`) with fair classical comparator and assumption log.

This gate model keeps roadmap claims honest as we scale from placeholders to production-grade quantum studies.

### 🎲 Problem Instances

Each problem includes parameterized instances:

- **Small**: Development and unit testing
- **Medium**: Benchmarking and validation
- **Large**: Challenge instances for future hardware

---

## 🔬 Featured Case Studies

Two problems anchor the current roadmap and demonstrate the end-to-end workflow from classical baseline to quantum-readiness.

### QAE Risk Analysis (`problems/03_qae_risk`)

- **Challenge**: Estimate tail risk probabilities P(Loss > threshold) for log-normal loss distributions using quantum amplitude estimation
- **Classical Baseline**: `make classical` runs 10,000 Monte Carlo samples achieving 18.98% ± 0.39% (theoretical: 18.98%)
- **Q# Status**: ✅ **Full canonical implementation complete** with:
  - Grover operator (oracle + diffusion) using phase kickback
  - Quantum phase estimation with controlled Grover^(2^k) powers
  - Amplitude encoding state preparation with multiplex rotations
  - Statistical averaging over 20 repetitions
- **Resource Requirements**: 
  - **Optimal**: 594k qubits, 6.4s runtime, 965k T-states (gate_ns_e3)
  - **Alternatives**: 561k qubits/6.7s (gate_ns_e4), 400k qubits/28.5s (Majorana)
  - **T-State Breakdown**: 738k from 36.9k rotations (76%), 227k from 56.8k CCZ gates (24%)
- **Quantum Advantage**: O(1/ε) vs O(1/ε²) complexity—quadratic speedup for precision ε
- **Comparison**: 31.8× more qubits than HHL, 5.4-12.2× more than VQE (highest T-state count of all three algorithms)
- **Next Steps**: Algorithm calibration for phase-to-amplitude mapping (current: 74% vs theoretical 18.98%)

### Hubbard Model (`problems/01_hubbard`)

- **Challenge**: Track charge and spin gaps in the two-site half-filled Hubbard model
- **Classical Baseline**: Closed-form diagonalization sweeps U/t to produce ground-state energy and Mott-gap curves stored in `estimates/classical_baseline.json`
- **Q# Status**: ✅ **VQE + HHL implementations complete** with comprehensive resource estimates:
  - **VQE**: 48.5k-110k qubits, 47-182μs runtime, 18 T-gates (8/8 convergence)
  - **HHL**: 18.7k qubits, 52ms runtime, 903 T-gates, 6 logical qubits
  - Full documentation in `VQE_IMPLEMENTATION_SUMMARY.md` and `HHL_IMPLEMENTATION_SUMMARY.md`
- **Next Steps**: Implement quantum phase estimation for energy spectrum and compare with VQE/HHL approaches

---

## 🧮 The 20 Grand Challenges

### Quantum computing applications to humanity's most complex scientific problems

### 🔬 **Physics & Materials Science**

**1. Hubbard Model** - Strongly-correlated electron systems  
*Status: Foundation laid*  
Q# angle: Hamiltonian simulation + Phase Estimation / qubitization

**2. High-Temperature Superconductivity** - Cooper pair mechanisms  
*Status: Foundation laid*  
Q# angle: Multi-orbital models with adiabatic state preparation

**3. Catalysis Simulation** - Chemical reaction pathways  
*Status: Foundation laid*  
Q# angle: Electronic structure with VQE → PEA refinement

**4. Topological Quantum Matter** - Non-Abelian anyons  
*Status: Foundation laid*  
Q# angle: Tight-binding Hamiltonians with Trotter/qubitization

### 💰 **Finance & Economics**

**5. Financial Risk Modeling** - Portfolio optimization  
*Status: ✅ Complete implementation*  
Q# angle: Quantum amplitude estimation for tail risk

**6. High-Frequency Trading** - Market prediction algorithms  
*Status: Foundation laid*  
Q# angle: Quantum machine learning for pattern recognition

### 🧬 **Biology & Medicine**

**7. Drug Discovery** - Molecular docking and binding  
*Status: Foundation laid*  
Q# angle: Active-space chemistry + VQE/PEA

**8. Protein Folding** - Ab initio structure prediction  
*Status: Foundation laid*  
Q# angle: Biomolecular quantum dynamics simulation

### 🔐 **Cryptography & Security**

**9. Factorization** - Shor's algorithm applications  
*Status: Foundation laid*  
Q# angle: Resource estimation for cryptographic security

**10. Post-Quantum Cryptography** - Security analysis  
*Status: Foundation laid*  
Q# angle: Grover oracle for cipher analysis

### 🧠 **Artificial Intelligence**

**11. Quantum Machine Learning** - Variational algorithms  
*Status: Foundation laid*  
Q# angle: Quantum kernel methods and feature maps

**12. Optimization** - NP-hard scheduling problems  
*Status: Foundation laid*  
Q# angle: QAOA for constrained optimization

### 🌍 **Climate & Environment**

**13. Climate Modeling** - Large-scale simulations  
*Status: Foundation laid*  
Q# angle: HHL algorithm for sparse linear systems

**14. Materials Discovery** - Next-generation batteries  
*Status: Foundation laid*  
Q# angle: Band-gap and defect energetics

### 🚀 **Advanced Applications**

**15. Database Search** - Grover's algorithm  
*Status: Foundation laid*  
Q# angle: Unstructured search with oracle optimization

**16. Error Correction** - Fault-tolerant computing  
*Status: Foundation laid*  
Q# angle: Surface codes with parameter optimization

**17. Nuclear Physics** - Few-nucleon systems  
*Status: Foundation laid*  
Q# angle: Lattice gauge theory toy models

**18. Photovoltaic Efficiency** - Light harvesting  
*Status: Foundation laid*  
Q# angle: Exciton transport in organic semiconductors

**19. Quantum Chromodynamics** - Strong interactions  
*Status: Foundation laid*  
Q# angle: Lattice gauge theory simulations

**20. Space Exploration** - Mission optimization  
*Status: Foundation laid*  
Q# angle: Trajectory optimization with quantum annealing

---

## 🔬 Research Methodology

### Quantum Advantage Analysis

Each problem includes:

- **Complexity Analysis**: Classical vs. quantum algorithmic complexity
- **Resource Requirements**: Logical qubits, gate counts, error rates
- **Practical Thresholds**: When quantum advantage becomes achievable

### Benchmarking Protocol

1. **Small Instances**: Verify correctness against classical solutions
2. **Medium Instances**: Validate quantum algorithms on simulators
3. **Large Instances**: Project performance on fault-tolerant hardware

---

## 🛠️ Development Workflow

### AI-Assisted Development

This repository leverages AI tools for:

- **Algorithm Design**: Quantum circuit optimization
- **Code Generation**: Q# implementation patterns
- **Testing**: Automated unit test creation
- **Documentation**: Problem analysis and results

### Continuous Integration

- **Q# Compilation Attempts**: GitHub Actions restores .NET 6 and attempts to build every placeholder project, surfacing regressions while tolerating known runtime gaps
- **Python Tooling**: Pip installs, smoke tests, and JSON schema validation run on each commit
- **Resource Estimation**: Nightly workflow stubs out estimator artifacts so the pipeline is ready for real hardware profiles
- **Website**: Next.js static export rebuilds automatically and publishes case studies to GitHub Pages

### 🤖 Agent Workflow (GPT-5 Codex)

1. **Read `.github/copilot-instructions.md` first** – it captures validated commands, timing expectations, and environment constraints (notably the .NET 6 requirement).
2. **Start with the classical pipeline** – `make classical` then `make analyze` confirm the problem scaffold before touching Q#.
3. **Keep Q# placeholders building** – run `make build` under .NET 6 to ensure the stub stays healthy while quantum kernels evolve.
4. **Document every change** – sync per-problem READMEs, the dashboard, and this README whenever capabilities shift.
5. **Lean on CI** – the `ci-cd.yml` workflow provides immediate feedback on Python, Q#, estimator artifacts, and the website export.

---

## 📊 Algorithm Comparison Dashboard

**NEW**: Comprehensive visual comparison of VQE, HHL, and QAE implementations!

📁 **Location**: [`tooling/visualization/`](tooling/visualization/)

**Visualizations Available**:
- **Physical Qubit Requirements**: HHL (18.7k) vs VQE (79k) vs QAE (594k)
- **Runtime Comparison**: VQE (114μs) vs HHL (52ms) vs QAE (6.4s)
- **T-State Breakdown**: Rotation gates dominate all algorithms (76-99%)
- **Scaling Analysis**: Predictions for larger problem instances
- **Quantum Advantage Map**: When each algorithm wins over classical
- **Technology Timeline**: 2027 (HHL) → 2030 (VQE) → 2035 (QAE)

**Generate Plots**:
```bash
cd tooling/visualization
python generate_comparison_plots.py
```

**Full Analysis**: See [`docs/algorithm-comparison.md`](docs/algorithm-comparison.md) for detailed comparison across 11 dimensions.

---

## 📚 Getting Started

### 1. Choose Your Problem

Browse the [problems/](problems/) directory to find an interesting challenge.

### 2. Study the Implementation

Each problem includes comprehensive documentation and commented code.

### 3. Run the Analysis

Use the provided Makefiles to execute the complete analysis pipeline.

### 4. Extend the Work

Modify parameters, try different algorithms, or implement variations.

### 5. Compare Algorithms

Use the [visualization dashboard](tooling/visualization/) to understand resource tradeoffs.

---

## 🤝 Contributing

We welcome contributions to expand and improve the quantum grand challenges:

- **New Problems**: Implement additional quantum algorithms
- **Optimizations**: Improve existing Q# implementations
- **Analysis**: Enhanced classical baselines and visualizations
- **Documentation**: Clearer explanations and tutorials

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📖 Resources

### Learning Materials

- [Microsoft Q# Documentation](https://learn.microsoft.com/quantum/)
- [Azure Quantum Resource Estimator](https://learn.microsoft.com/azure/quantum/overview-resources-estimator)
- [Quantum Algorithm Zoo](https://quantumalgorithmzoo.org/)

### Research Papers

- Nielsen & Chuang: "Quantum Computation and Quantum Information"
- Preskill: "Quantum Computing in the NISQ era and beyond"
- Problem-specific references in each implementation

---

## 📄 License

“All Rights Reserved”

---

## 🙏 Acknowledgments

- **Microsoft Quantum Team** for the Q# ecosystem and Azure Quantum platform
- **AI Research Community** for algorithm design and optimization insights
- **Open Source Contributors** for tools, libraries, and inspiration

---

Ready to tackle humanity's greatest challenges with quantum computing? Start exploring! 🚀
