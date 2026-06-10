# Quantum Grand Challenges Development Instructions

Always follow these instructions first and fallback to additional search and context gathering only when the information here is incomplete or found to be in error.

## Repository Overview

Quantum Grand Challenges is a systematic exploration of 20 of the world's most challenging scientific problems using quantum computing and AI-assisted development. The repository uses Microsoft Q# for quantum implementations, Python for classical analysis, and Next.js for visualization.

## Critical Dependencies & Compatibility

### QDK (Quantum Development Kit)
- **Modern QDK**: Q# programs use `qsharp.json` project format with the `qsharp` Python package (v1.27+)
- **No .NET dependency**: The legacy Microsoft.Quantum.Sdk / .NET 6.0 toolchain has been fully replaced
- **Install**: `pip install qsharp` (or `pip install "qdk[azure]"` for Azure Quantum submission)

### Environment Setup
- **Python 3.11+** with scientific computing stack + `qsharp` package
- **Node.js 18+** for website development
- **Azure CLI** for quantum job submission (optional)

## Working Development Commands

Always reference these validated commands. Build times measured on standard development machines.

### Python Development (✅ VALIDATED)
```bash
# Install Python dependencies - takes 60 seconds. NEVER CANCEL. Set timeout to 90+ seconds.
pip install numpy scipy matplotlib pandas seaborn plotly jupyter pyyaml jsonschema pytest

# Run classical analysis - takes 8 seconds
cd problems/archived/03_qae_risk
make classical

# Generate analysis plots - takes 8 seconds  
make analyze
```

### Q# Development (✅ VALIDATED  Modern QDK)
```bash
# Install the qsharp Python package (one-time)
pip install qsharp

# Compile and run any problem via Python:
python -c "import qsharp; qsharp.init(project_root='problems/01_hubbard/qsharp'); qsharp.run('Main.RunTwoSiteHubbardAnalysis()', 1)"

# Run all 20 problems (compile + execute):
python tooling/run_all_qsharp.py      # ~15 seconds total

# Generate resource estimates for all:
python tooling/generate_estimates.py   # ~30 seconds total

# Generate circuit diagrams:
python tooling/trace_circuits.py       # ~60 seconds total
```

### Website Development (✅ VALIDATED)
```bash
cd website
npm install  # Takes 75 seconds. NEVER CANCEL. Set timeout to 120+ seconds.
npm run build  # Static export to website/out/. Takes ~15 seconds.
```

### Complete Problem Analysis
```bash
cd problems/archived/03_qae_risk

# Quick working demo - takes 15 seconds total
make classical     # Classical Monte Carlo analysis
make analyze      # Generate comparison plots

# Full quantum analysis via modern QDK - takes ~2 seconds
make run          # Runs Q# via qsharp Python package (no .NET needed)

# IQAE adaptive analysis (problem 03 only):
python python/iqae_driver.py --epsilon 0.05 --alpha 0.05
```

## Timing Expectations & Timeouts

### Short Operations (< 30 seconds)
- `make classical`: 8 seconds
- `make analyze`: 8 seconds  
- Q# compile + run via `qsharp.run()`: 1-12 seconds per problem
- Individual Python scripts: 5-10 seconds

### Medium Operations (30-120 seconds)
- `pip install` (full stack): 60 seconds - **NEVER CANCEL, set timeout to 90+ seconds**
- `npm install`: 75 seconds - **NEVER CANCEL, set timeout to 120+ seconds**

### Long Operations (2+ minutes)
- Complete `make full-analysis`: 45 seconds - **NEVER CANCEL, set timeout to 90+ seconds**
- Resource estimation sweeps: 60+ seconds - **NEVER CANCEL, set timeout to 180+ seconds**

## Validation Scenarios

Always test these scenarios after making changes to ensure functionality:

### Core Functionality Validation
```bash
# 1. Test Python scientific stack
python3 -c "import numpy as np; import matplotlib.pyplot as plt; import scipy; print('All packages working')"

# 2. Run working classical analysis
cd problems/archived/03_qae_risk
make classical
# Verify: ../estimates/classical_baseline.json created
# Verify: ../plots/*.png files generated

# 3. Test Q# compilation
python3 -c "import qsharp; qsharp.init(project_root='problems/archived/03_qae_risk/qsharp'); print('Q# OK')"
# Verify: No errors, prints 'Q# OK'
```

### End-to-End Scenario Testing
```bash
# Complete working workflow
cd problems/archived/03_qae_risk
make classical && make analyze
# Expected: Monte Carlo analysis runs, plots generated in ../plots/
# Expected: classical_baseline.json created in ../estimates/
# Expected: Comparison plots show classical vs quantum projections
```

## Problem Structure & Navigation

### Standard Problem Layout
```
problems/XX_problem_name/
├── README.md              # Problem description and results
├── qsharp/               # Q# quantum implementation  
│   ├── qsharp.json       # Modern QDK project file
│   ├── src/              # Q# source files
│   │   └── Main.qs       # Main quantum algorithm
│   └── HardwareKernel.qs # Azure-submittable QIR kernel
├── circuits/             # Circuit diagrams and resource estimates
│   ├── circuit.txt       # ASCII circuit diagram
│   └── estimate.json     # Resource estimation results
├── python/               # Classical analysis & visualization
│   ├── analysis.py       # Performance comparison  
│   ├── classical_baseline.py  # Classical algorithm baseline
│   └── requirements.txt  # Python dependencies
├── instances/            # Problem parameter sets
│   ├── small.yaml        # Development/testing
│   ├── medium.yaml       # Benchmark instances  
│   └── large.yaml        # Challenge instances
├── estimates/            # Resource estimation results
└── Makefile             # Build automation
```

### Current Implementation Status
- **All 20 problems**: ✅ Migrated to modern QDK (qsharp 1.27), compile, run, Azure syntax-checked
- **03_qae_risk**: ✅ IQAE algorithm (iterative, no QPE register), adaptive Python driver with Clopper-Pearson CI, variance-reduced MC baseline, CVaR/VaR bisection search
- **01_hubbard**: ✅ VQE ansatz with Pauli expectation measurement, analytical baseline
- **02_catalysis**: ✅ VQE for H₂ ground state (STO-3G), Arrhenius rate baseline
- **04_linear_solvers**: ✅ HHL algorithm with QPE + eigenvalue inversion
- **05_qaoa_maxcut**: ✅ QAOA with ZZ cost layer + Rx mixer, coordinate-descent optimizer

## Frequently Used Commands

### Environment Check
```bash
# Verify development environment
python3 --version        # Should be 3.11+
python3 -c "import qsharp; print('qsharp OK')"  # Modern QDK
node --version           # Should be 18+
az --version            # Azure CLI (optional)
```

### Problem Development Workflow
```bash
# 1. Navigate to problem (e.g., 01_hubbard or 03_qae_risk)
cd problems/<problem_directory>

# 2. Check available commands
make help

# 3. Run quick validation
make check-env

# 4. Classical development (validated for all 20 problems)
make classical
make analyze

# 5. Q# development (via modern QDK  no .NET required)
make build
make test
make run
```

### Troubleshooting Common Issues

#### Q# Build Fails
```bash
# Verify qsharp package is installed
pip install qsharp
# Test compilation:
python -c "import qsharp; qsharp.init(project_root='problems/01_hubbard/qsharp'); print('OK')"
```

#### Python Import Errors  
```bash
# Install/reinstall dependencies
pip install --upgrade numpy scipy matplotlib pandas
```

#### Resource Estimation Fails
```bash
# Check Azure CLI quantum extension
az extension list | grep quantum
# If missing and network allows: az extension add --name quantum
```

## Development Best Practices

### Always Run These Validation Steps
1. **Environment check**: `make check-env` in any problem directory
2. **Classical validation**: `make classical` to verify Python stack
3. **Build validation**: `make build` to verify Q# compilation
4. **End-to-end test**: Run complete analysis pipeline on small instance

### Making Changes
- **Always validate working components first** before attempting Q# changes
- **Test classical baselines** to verify mathematical correctness  
- **Run analysis plots** to visualize algorithm performance
- **Check estimates/ directory** for resource estimation outputs
- **Verify plots/ directory** for generated visualizations

### Performance Expectations
- **Classical analysis**: Should complete in under 10 seconds for small instances
- **Q# compilation**: Should complete in under 30 seconds
- **Resource estimation**: May take 60+ seconds - always wait for completion
- **Plot generation**: Should complete in under 10 seconds

## Known Limitations

### Current Issues
- **Azure Quantum extension**: May not install in restricted network environments
- **Analysis formatting**: Minor string formatting issues in summary reports

### Workarounds
- **Use classical analysis** for algorithm validation when Q# unavailable
- **Mock resource estimation** using provided templates when Azure unavailable
- **Focus on Python development** for baseline implementations and analysis

## File Locations

### Important Directories
- `problems/`: Individual quantum challenge implementations
- `libs/common/`: Shared quantum algorithm utilities
- `tooling/`: Resource estimation and automation scripts
- `website/`: Next.js visualization dashboard (incomplete)
- `.github/workflows/`: CI/CD pipeline definitions

### Generated Outputs
- `estimates/*.json`: Resource estimation results
- `plots/*.png`: Analysis visualizations
- `circuits/circuit.txt`: ASCII circuit diagrams
- `circuits/estimate.json`: Resource estimation summaries
- `__pycache__/`: Python bytecode (excluded from git)

Always check these locations after running analysis to verify outputs were generated correctly.