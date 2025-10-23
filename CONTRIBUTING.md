# Contributing to Quantum Grand Challenges

Thank you for your interest in contributing to the Quantum Grand Challenges project! This document provides guidelines for contributing to this repository.

## 🎯 Project Vision

This project aims to systematically explore 20 of the world's most challenging scientific problems using quantum computing and AI-assisted development. We welcome contributions that:

- Implement new quantum algorithms for the grand challenges
- Improve existing Q# implementations
- Enhance classical baselines and performance analysis
- Expand visualization and analysis tools
- Improve documentation and educational materials

## 🛠️ Development Setup

### Prerequisites

1. **.NET 6.0.x runtime/SDK** (strictly 6.0; the Microsoft.Quantum.Sdk version in this repo does *not* support .NET 7/8)
2. **Python 3.11+** with the scientific computing stack (NumPy, SciPy, matplotlib, pandas, PyYAML, jsonschema)
3. **Azure CLI** with the optional `quantum` extension for running the Resource Estimator or submitting Azure Quantum jobs
4. **Git** for version control (and optionally GitHub CLI for Codespaces)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/WernerRall147/quantum-grand-challenges.git
cd quantum-grand-challenges

# Install Q# tools (optional for Jupyter integration)
dotnet tool install -g Microsoft.Quantum.IQSharp

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install baseline Python dependencies
pip install numpy scipy matplotlib pandas seaborn plotly jsonschema pyyaml pytest

# Validate the canonical workflow
cd problems/03_qae_risk
make classical
make analyze
```

### Using GitHub Codespaces (Recommended)

Click the "Open in Codespaces" button for an instant development environment with all dependencies pre-installed.

## 📋 Contribution Guidelines

### Types of Contributions

#### 🔬 New Problem Implementations

- Choose an unimplemented problem from the list of 20 grand challenges
- Follow the standard problem structure (see below)
- Include Q# quantum implementation, classical baseline, and analysis

#### 🚀 Algorithm Improvements

- Optimize existing Q# code for better performance
- Implement additional quantum algorithms for existing problems
- Add more sophisticated classical baselines

#### 📊 Analysis & Visualization

- Enhance performance comparison scripts
- Create better visualizations and plots
- Improve resource estimation analysis

#### 📚 Documentation

- Improve README files for individual problems
- Add tutorials and educational content
- Document quantum algorithms and their advantages

### Standard Problem Structure

When implementing a new problem, follow this structure:

```text
problems/XX_problem_name/
├── README.md                      # Problem description, acceptance criteria, current status
├── Makefile                       # `make classical`, `make analyze`, `make build`, `make estimate`
├── instances/
│   ├── small.yaml                 # Development-sized instance
│   ├── medium.yaml                # Benchmark instance
│   └── large.yaml                 # Stretch goal / challenge instance
├── estimates/
│   ├── classical_baseline.json    # Deterministic output from classical pipeline
│   └── ci_latest.json             # (Optional) CI-generated mock or estimator results
├── plots/                         # Generated figures from `make analyze`
├── python/
│   ├── classical_baseline.py      # Primary classical algorithm implementation
│   ├── analyze.py                 # Visualization and report script
│   └── __init__.py (optional)
└── qsharp/
	├── Program.qs                 # Entry-point operation / placeholder circuit
	├── *.csproj                   # Q# project configuration
	└── Tests.qs (optional)        # Quantum unit tests when available
```

### Code Quality Standards

#### Q# Code

- Use meaningful operation and variable names
- Include comprehensive documentation comments
- Follow Q# naming conventions (PascalCase for operations)
- Include unit tests for all quantum operations
- Use the shared utilities from `libs/common/Utils.qs` when appropriate

#### Python Code

- Follow PEP 8 style guidelines
- Include type hints where appropriate
- Use docstrings for functions and classes
- Create clear, well-labeled plots
- Include error handling for edge cases

#### General

- Write clear commit messages
- Include tests for new functionality
- Update documentation for any changes
- Ensure all code compiles and tests pass

### Resource Estimation

All quantum implementations should include:

1. **Logical Resource Analysis**: Use Azure Quantum Resource Estimator
2. **Physical Resource Projections**: Estimate requirements for fault-tolerant hardware
3. **Classical Comparison**: Compare quantum vs. classical resource requirements
4. **Error Budget Analysis**: Understand error correction overhead

Example resource estimation call:

```bash
cd problems/XX_problem_name
make estimate  # Runs resource estimation pipeline
```

## 🔄 Development Workflow

### 1. Choose an Issue or Problem

- Browse [open issues](https://github.com/WernerRall147/quantum-grand-challenges/issues)
- Check the [project board](https://github.com/WernerRall147/quantum-grand-challenges/projects) for planned work
- Propose new problems or improvements via issues

### 2. Create a Branch

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

### 3. Implement Your Changes

Follow the guidelines above for code quality and structure.

### 4. Test Your Implementation

```bash
# Classical + analysis pipeline
cd problems/XX_problem_name
make classical
make analyze

# Q# build (requires local .NET 6.0 runtime)
make build

# (Optional) Run resource estimation wrappers
make estimate
```

### 5. Submit a Pull Request

- Ensure all tests pass
- Update relevant documentation
- Include clear description of changes
- Reference related issues

## 📝 Pull Request Template

When submitting a pull request, please include:

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] New problem implementation
- [ ] Algorithm improvement
- [ ] Bug fix
- [ ] Documentation update
- [ ] Performance optimization

## Problem Details (for new implementations)
- **Problem**: Which grand challenge does this address?
- **Algorithm**: What quantum algorithm is implemented?
- **Quantum Advantage**: What speedup/advantage does this provide?
- **Resources**: What are the estimated resource requirements?

## Testing
- [ ] Q# code compiles without errors
- [ ] Unit tests pass
- [ ] Classical baseline implemented and tested
- [ ] Resource estimation completed
- [ ] Documentation updated

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or clearly documented)
```

## 🚨 Issue Templates

### Bug Report

Use this template for reporting bugs:

```markdown
**Problem Description**
Clear description of the issue

**Steps to Reproduce**
1. Navigate to...
2. Run command...
3. Error occurs...

**Expected Behavior**
What should happen

**Environment**
- OS: [e.g., Windows 11, Ubuntu 20.04]
- .NET Version: [e.g., 6.0.1]
- Q# Version: [e.g., 0.28.1]
- Python Version: [e.g., 3.9.7]
```

### Feature Request

Use this template for suggesting new features:

```markdown
**Problem/Challenge**
Which of the 20 grand challenges does this relate to?

**Proposed Solution**
Describe your idea

**Quantum Algorithm**
What quantum algorithm would be used?

**Expected Impact**
What advantage would this provide?

**Additional Context**
Any other relevant information
```

## 🏆 Recognition

Contributors will be recognized in:

- Repository contributor list
- Individual problem README files
- Project documentation
- Conference presentations (with permission)

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please:

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Assume good intentions

### Communication

- Use GitHub issues for bug reports and feature requests
- Use GitHub discussions for general questions and ideas
- Join our community channels for real-time collaboration

## 📖 Resources for Contributors

### Learning Materials

- [Microsoft Q# Documentation](https://docs.microsoft.com/quantum/)
- [Azure Quantum Resource Estimator Guide](https://docs.microsoft.com/azure/quantum/)
- [Quantum Computing: An Applied Approach](https://link.springer.com/book/10.1007/978-3-030-23922-0)

### Research References

- [Quantum Algorithm Zoo](https://quantumalgorithmzoo.org/)
- [arXiv Quantum Physics](https://arxiv.org/list/quant-ph/recent)
- Problem-specific references in individual README files

### Tools and Libraries

- [Q# Standard Library](https://docs.microsoft.com/qsharp/api/)
- [NumPy](https://numpy.org/) for classical implementations
- [Matplotlib](https://matplotlib.org/) for visualization
- [Azure Quantum](https://azure.microsoft.com/products/quantum/) for resource estimation

## ❓ Getting Help

If you need help:

1. Check existing documentation and README files
2. Search through [existing issues](https://github.com/WernerRall147/quantum-grand-challenges/issues)
3. Create a new issue with detailed information
4. Join our community discussions

Thank you for contributing to advancing quantum computing research! 🚀
