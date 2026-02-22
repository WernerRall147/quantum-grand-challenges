# Quantum Grand Challenges: AI Agent Setup Guide

*Last Updated: October 19, 2025*  
*For: GPT-5 Codex (Preview), Claude Sonnet 4, and other AI coding agents*

## 🎯 Project Overview

This repository systematically tackles 20 of the world's most challenging scientific problems using Q# quantum computing and AI-assisted development. Each problem has a standardized structure for reproducible research and automated tooling. **Today `problems/01_hubbard` and `problems/03_qae_risk` ship working classical pipelines with matching analytical Q# baselines in place.**

## 📁 Repository Structure

```
quantum-grand-challenges/
├── docs/                        # Documentation and planning
│   ├── planning/               # Original conversations and blueprints
│   ├── guides/                 # Setup and usage guides
│   └── ai-agents/             # Instructions for AI agents
├── libs/                       # Shared Q# libraries and utilities
├── problems/                   # Individual problem implementations
│   ├── 01_hubbard/            # Superconductivity (Hubbard model)
│   ├── 02_catalysis/          # Industrial catalysis design
│   ├── 03_qae_risk/           # Climate risk (QAE)
│   ├── 04_linear_solvers/     # HHL algorithms
│   ├── 05_qaoa_maxcut/        # Combinatorial optimization
│   ├── 06_shor_resources/     # Cryptanalysis resource estimation
│   └── [... 14 more problems]
├── tooling/                   # Development and automation tools
│   ├── estimator/            # Resource Estimator scripts
│   ├── azq/                  # Azure Quantum CLI helpers
│   └── schema/               # JSON schemas for results
├── .devcontainer/            # Codespaces development environment
├── .github/workflows/        # CI/CD automation
└── website/                  # Results presentation website
```

## 🤖 AI Agent Instructions

### When Working on This Project:

1. **Always read this file first** to understand the project structure
2. **Follow the standard problem template** (see section below)
3. **Document all changes** in appropriate README files
4. **Use the standard JSON schema** for results
5. **Test with Resource Estimator** before committing

### Standard Problem Template

Each problem follows this exact structure:

```
problems/XX_problem_name/
├── qsharp/                    # Q# implementation
│   ├── Program.qs            # Main Q# program
│   ├── Oracles.qs           # Problem-specific oracles
│   └── Tests.qs             # Unit tests
├── python/                   # Analysis and plotting
│   ├── analyze.py           # Results analysis
│   ├── plot.py              # Visualization
│   └── classical_baseline.py # Classical comparison
├── instances/                # Input data
│   ├── small.yaml           # Toy problem instances
│   ├── medium.yaml          # Moderate instances
│   └── large.yaml           # Challenge instances
├── estimates/                # Resource estimation results
│   ├── latest.json          # Most recent estimates
│   └── archive/             # Historical results
├── README.md                 # Problem description and status
└── Makefile                 # Build and run automation
```

### Standard JSON Result Schema

All results must follow this schema (defined in `tooling/schema/result.json`):

```json
{
  "problem_id": "string (e.g., '03_qae_risk')",
  "algorithm": "string (e.g., 'QAE', 'Shor', 'QAOA')",
  "instance": {
    "description": "string",
    "parameters": "object (problem-specific)"
  },
  "estimator_target": "string (e.g., 'surface_code_generic_v1')",
  "metrics": {
    "logical_qubits": "integer",
    "physical_qubits": "integer", 
    "t_count": "integer",
    "runtime_days": "float"
  },
  "build": {
    "commit": "string (git commit hash)",
    "qdk_version": "string",
    "date_utc": "string (ISO 8601)"
  },
  "notes": "string (methodology, comparisons, etc.)"
}
```

## 🛠️ Development Environment

### Required Tools (via Codespaces/DevContainer):

1. **Azure Quantum Development Kit (QDK)**
   - Q# compiler and simulator
   - VS Code extension
   - Jupyter integration

2. **Azure CLI with Quantum Extension**
   ```bash
   az extension add -n quantum
   ```

3. **Resource Estimator (Local)**
   - Open-source, no Azure account needed
   - Customizable hardware targets

4. **Chemistry Support (Optional)**
   - Broombridge YAML parser
   - For electronic structure problems

### Quick Start Commands:

```bash
# Navigate to the working problem
cd problems/03_qae_risk

# Classical workflow (stable)
make classical
make analyze

# Quantum workflow (builds successfully; amplitude calibration still in progress)
make build
make run
make estimate
```

## 🎯 Priority Implementation Order

Based on the original planning conversation, tackle problems in this order:

1. **QAE for tail risk** (`problems/03_qae_risk/`)
   - Clean quantum vs classical comparison
   - Good learning example for QAE

2. **Shor resource study** (`problems/06_shor_resources/`)
   - Practical crypto-agility importance
   - Well-defined resource targets

3. **HHL toy linear solver** (`problems/04_linear_solvers/`)
   - Fundamental algorithm building block
   - Teaching exemplar

4. **Chemistry/Broombridge demo** (`problems/02_catalysis/`)
   - Establishes chemistry pipeline
   - Real-world impact

## 📊 Results and Presentation

### Automation Pipeline:
1. **CI/CD**: GitHub Actions build, test, and estimate on every PR
2. **Nightly Sweeps**: Full parameter grids across all problems
3. **Website**: Auto-generated from JSON results with interactive charts
4. **Notebooks**: Executable walkthroughs for each result

### Success Metrics:
- **Resource estimates** for fault-tolerant quantum computers
- **Classical baselines** for comparison
- **Scaling analysis** (precision vs. resources)
- **Hardware comparisons** across different quantum platforms

## 🤝 Collaboration Guidelines

### For AI Agents:
- **Read existing documentation** before making changes
- **Follow naming conventions** strictly
- **Add comprehensive comments** to Q# code
- **Include test cases** for all implementations
- **Update README files** with your changes

### Pull Request Requirements:
- Problem background and approach
- Resource estimation results
- Comparison to classical methods
- Test coverage report
- Documentation updates

## 🔄 Reproducibility Standards

Every result must be:
1. **Reproducible** from source code
2. **Versioned** with git commit hashes
3. **Documented** with clear methodology
4. **Tested** with unit tests
5. **Estimated** with resource requirements

## 📚 Key References

- [Azure Quantum Documentation](https://docs.microsoft.com/en-us/azure/quantum/)
- [Q# Language Guide](https://docs.microsoft.com/en-us/quantum/language/)
- [Quantum Katas](https://github.com/microsoft/QuantumKatas)
- [Resource Estimator](https://docs.microsoft.com/en-us/azure/quantum/how-to-work-with-re)

---

## 🚨 Important Notes for AI Agents

1. **Never modify** the project structure without updating this documentation
2. **Always validate** Q# code with the compiler before committing
3. **Include resource estimates** for any new quantum algorithms
4. **Document assumptions** clearly in your implementations
5. **Test on small instances** before scaling up

*This guide ensures consistent, high-quality contributions from AI agents working on quantum grand challenges.*
