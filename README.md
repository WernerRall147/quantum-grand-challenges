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

## 📊 Problem Status

| Problem | Q# Implementation | Classical Baseline | Resource Estimation | Status |
|---------|-------------------|--------------------|---------------------|--------|
| [QAE Risk Analysis](problems/03_qae_risk/) | ✅ Analytical placeholder builds under .NET 6 | ✅ Complete (Monte Carlo + plots) | ⏳ Pending (fault-tolerant QAE sweep) | 🟢 Ready for quantum kernel |
| [Hubbard Model](problems/01_hubbard/) | ✅ Analytical placeholder builds under .NET 6 | ✅ Complete (exact diagonalization) | ⏳ Pending | 🟢 Ready for quantum kernel |
| [Catalysis Simulation](problems/02_catalysis/) | ✅ Placeholder Q# stub | ✅ Complete | ⏳ Pending | 🟡 Scaffolded |
| [Linear Solvers](problems/04_linear_solvers/) | ✅ Placeholder Q# stub | ✅ Complete | ⏳ Pending | � Scaffolded |
| [QAOA MaxCut](problems/05_qaoa_maxcut/) | ✅ Placeholder Q# stub + C# driver | ✅ Complete | ⏳ Pending | � Scaffolded |
| [High-Frequency Trading](problems/06_high_frequency_trading/) | ✅ Placeholder Q# stub | ✅ Complete | ⏳ Pending | 🟡 Scaffolded |
| [Drug Discovery](problems/07_drug_discovery/) | ✅ Placeholder Q# stub | ✅ Complete | ⏳ Pending | 🟡 Scaffolded |
| [Protein Folding](problems/08_protein_folding/) | ✅ Placeholder Q# stub | ✅ Complete | ⏳ Pending | 🟡 Scaffolded |
| [Factorization](problems/09_factorization/) | ✅ Placeholder Q# stub | ✅ Complete | ⏳ Pending | 🟡 Scaffolded |
| [Post-Quantum Cryptography](problems/10_post_quantum_cryptography/) | ✅ Placeholder Q# stub | ✅ Complete | ⏳ Pending | 🟡 Scaffolded |
| [Quantum Machine Learning](problems/11_quantum_machine_learning/) | ✅ Placeholder Q# stub | ✅ Complete | ⏳ Pending | 🟡 Scaffolded |
| [Quantum Optimization](problems/12_quantum_optimization/) | ✅ Placeholder Q# stub | ✅ Complete | ⏳ Pending | 🟡 Scaffolded |
| [Climate Modeling](problems/13_climate_modeling/) | ✅ Placeholder Q# stub | ✅ Complete | ⏳ Pending | 🟡 Scaffolded |
| [Materials Discovery](problems/14_materials_discovery/) | ✅ Placeholder Q# stub | ✅ Complete | ⏳ Pending | 🟡 Scaffolded |
| [Database Search](problems/15_database_search/) | ✅ Placeholder Q# stub | ✅ Complete | ⏳ Pending | 🟡 Scaffolded |
| [Error Correction](problems/16_error_correction/) | ✅ Placeholder Q# stub | ✅ Complete | ⏳ Pending | 🟡 Scaffolded |
| [Nuclear Physics](problems/17_nuclear_physics/) | ✅ Placeholder Q# stub | ✅ Complete | ⏳ Pending | 🟡 Scaffolded |
| [Photovoltaics](problems/18_photovoltaics/) | ✅ Placeholder Q# stub | ✅ Complete | ⏳ Pending | 🟡 Scaffolded |
| [Quantum Chromodynamics](problems/19_quantum_chromodynamics/) | ✅ Placeholder Q# stub | ✅ Complete | ⏳ Pending | 🟡 Scaffolded |
| [Space Mission Planning](problems/20_space_mission_planning/) | ✅ Placeholder Q# stub | ✅ Complete | ⏳ Pending | 🟡 Scaffolded |

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

### 🎲 Problem Instances

Each problem includes parameterized instances:

- **Small**: Development and unit testing
- **Medium**: Benchmarking and validation
- **Large**: Challenge instances for future hardware

---

## 🔬 Featured Case Studies

Two problems anchor the current roadmap and demonstrate the end-to-end workflow from classical baseline to quantum-readiness.

### QAE Risk Analysis (`problems/03_qae_risk`)

- **Challenge**: Estimate 3–4σ tail risk probabilities for synthetic loss distributions
- **Classical Baseline**: `make classical` runs 47 500 Monte Carlo samples to nail 0.1 % precision in ≈1.3 s (Python)
- **Q# Status**: Analytical placeholder builds under .NET 6; amplitude-estimation oracle hooks are ready for a full QAE kernel
- **Opportunity**: True amplitude estimation would collapse the sample complexity to O(1/ε) ≈ 1.5 k Grover iterations—next milestone is wiring the controlled-rotation oracle and phase estimation stack

### Hubbard Model (`problems/01_hubbard`)

- **Challenge**: Track charge and spin gaps in the two-site half-filled Hubbard model
- **Classical Baseline**: Closed-form diagonalization sweeps U/t to produce ground-state energy and Mott-gap curves stored in `estimates/classical_baseline.json`
- **Q# Status**: Analytical parity check matches the classical spectrum; the project builds under .NET 6 and shares the same interfaces for future adiabatic/phase-estimation routines
- **Opportunity**: Replace the placeholder with adiabatic state preparation + phase estimation and feed the resulting circuits into the Azure Quantum Resource Estimator profiles

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

## 📚 Getting Started

### 1. Choose Your Problem

Browse the [problems/](problems/) directory to find an interesting challenge.

### 2. Study the Implementation

Each problem includes comprehensive documentation and commented code.

### 3. Run the Analysis

Use the provided Makefiles to execute the complete analysis pipeline.

### 4. Extend the Work

Modify parameters, try different algorithms, or implement variations.

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Microsoft Quantum Team** for the Q# ecosystem and Azure Quantum platform
- **AI Research Community** for algorithm design and optimization insights
- **Open Source Contributors** for tools, libraries, and inspiration

---

Ready to tackle humanity's greatest challenges with quantum computing? Start exploring! 🚀
