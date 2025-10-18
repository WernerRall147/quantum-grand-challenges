# 🌌 Quantum Grand Challenges

*Systematic exploration of 20 of the world's most challenging scientific problems using quantum computing and AI-assisted development.*

[![CI/CD](https://github.com/WernerRall147/quantum-grand-challenges/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/WernerRall147/quantum-grand-challenges/actions/workflows/ci-cd.yml)
[![Website](https://img.shields.io/badge/website-live-blue)](https://wernerall147.github.io/quantum-grand-challenges/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

This repository systematically tackles 20 of the world's most challenging scientific problems using **Microsoft Q# quantum computing** and **AI-assisted development**. Each problem follows a standardized structure for reproducible research, automated resource estimation, and comparative analysis with classical methods.

## 🚀 Quick Start

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

| Problem | Q# Implementation | Resource Estimation | Classical Baseline | Status |
|---------|------------------|--------------------|--------------------|---------||
| [QAE Risk Analysis](problems/03_qae_risk/) | ✅ Building (analytical baseline) | ⏳ Pending (needs fault-tolerant QAE) | ✅ Complete | 🟢 **Ready for development** |
| [Hubbard Model](problems/01_hubbard/) | 🔄 In Progress | ⏳ Pending | ⏳ Pending | 🟡 Working |
| [Catalysis Simulation](problems/02_catalysis/) | ⏳ Pending | ⏳ Pending | ⏳ Pending | 🔴 Planned |
| [Linear Solvers](problems/04_linear_solvers/) | ⏳ Pending | ⏳ Pending | ⏳ Pending | 🔴 Planned |
| [QAOA MaxCut](problems/05_qaoa_maxcut/) | ⏳ Pending | ⏳ Pending | ⏳ Pending | 🔴 Planned |
| *...15 more problems* | ⏳ Pending | ⏳ Pending | ⏳ Pending | 🔴 Planned |

## 🏗️ Repository Structure

```
quantum-grand-challenges/
├── 📁 problems/              # Individual quantum challenges
│   ├── 01_hubbard/          # Strongly correlated systems
│   ├── 02_catalysis/        # Chemical reaction catalysis
│   ├── 03_qae_risk/         # ✅ Quantum amplitude estimation
│   ├── 04_linear_solvers/   # HHL algorithm applications
│   ├── 05_qaoa_maxcut/      # Quantum approximate optimization
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

```
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

- **Automated CI/CD**: GitHub Actions smoke-tests Python tooling and attempts Q# builds (currently fails for `03_qae_risk` because amplitude estimation is a stub)
- **Resource Estimation**: Scripts and CI harness prepared for Azure Quantum Resource Estimator once Q# builds succeed
- **Standardized Schema**: JSON validation for cross-problem comparison
- **Codespaces Ready**: Devcontainer supplies .NET 6, Python 3.11, Node 18 (website skeleton is still a placeholder)

### 📈 Analysis Pipeline

Each problem follows this workflow:

1. **Q# Implementation**: Quantum algorithm with unit tests
2. **Classical Baseline**: Equivalent classical algorithm for comparison
3. **Resource Estimation**: Azure Quantum resource analysis
4. **Performance Analysis**: Quantum advantage quantification
5. **Visualization**: Interactive plots and dashboards

### 🎲 Problem Instances

Each problem includes parameterized instances:

- **Small**: Development and unit testing
- **Medium**: Benchmarking and validation
- **Large**: Challenge instances for future hardware

---

## 🔬 Featured Implementation: QAE Risk Analysis

Our **Quantum Amplitude Estimation (QAE) for Financial Risk** is the most advanced problem so far. The classical pipeline is production-ready; the quantum code still needs a working amplitude estimation kernel.

### 🎯 Problem Overview

- **Challenge**: Estimate tail risk probabilities in financial portfolios
- **Quantum Advantage**: Quadratic speedup in sampling complexity (target outcome)
- **Implementation Status**: Classical Monte Carlo + analysis ✅, Q# analytical baseline ✅ (builds and runs)

### 💻 Key Components

- **Q# Algorithm**: Analytical tail probability computation (serves as classical-quantum bridge) ✅
- **Classical Baseline**: Monte Carlo simulation with variance reduction ✅
- **Resource Analysis**: Schema + tooling ready for fault-tolerant QAE implementation
- **Visualization**: Performance comparison plots generated from classical + quantum-inspired results

### 📊 Results Preview

- **Classical**: 10⁶ samples → 0.1% accuracy (validated in `classical_baseline.py`)
- **Q# Analytical**: Direct probability computation from log-normal PDF ✅
- **Next Step**: Implement full quantum amplitude estimation circuit with phase estimation

---

## 🧮 The 20 Grand Challenges

*Quantum computing applications to humanity's most complex scientific problems*

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

- **Compilation Attempts**: GitHub Actions tries to build every Q# project (currently flags failures for `03_qae_risk` so we remember to fix it)
- **Python Tooling**: Pip installs and module byte-compilation run on each commit
- **Resource Estimation**: Nightly workflow produces mock results until real estimates are available
- **Website**: Placeholder static export keeps deployment pipeline warm for future Next.js work

### 🤖 Agent Workflow (GPT-5 Codex)

1. **Read `.github/copilot-instructions.md` first** – it captures environment constraints (.NET 6 only) and validated commands.
2. **Start with Python tooling** – `make classical` and `make analyze` are reliable smoke tests that populate `estimates/` and `plots/`.
3. **Triage Q# build failures** – current blockers are inside `libs/common/Utils.qs` (placeholder `AmplitudeEstimation`) and `problems/03_qae_risk/qsharp/Program.qs` (non-compiling math operations).
4. **Update documentation as you go** – keep this README and per-problem READMEs in sync with actual capabilities.
5. **Lean on CI** – use the `ci-cd.yml` workflow as a guide; replicate its steps locally before opening a PR.

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

- [Microsoft Q# Documentation](https://docs.microsoft.com/en-us/quantum/)
- [Azure Quantum Resource Estimator](https://docs.microsoft.com/en-us/azure/quantum/overview-resources-estimator)
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

*Ready to tackle humanity's greatest challenges with quantum computing? Start exploring! 🚀*
