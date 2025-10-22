# Quantum Grand Challenges Development Instructions

Always follow these instructions first and fallback to additional search and context gathering only when the information here is incomplete or found to be in error.

## Repository Overview

Quantum Grand Challenges is a systematic exploration of 20 of the world's most challenging scientific problems using quantum computing and AI-assisted development. The repository uses Microsoft Q# for quantum implementations, Python for classical analysis, and Next.js for visualization.

## Critical Dependencies & Compatibility

### .NET Requirements
- **CRITICAL**: Q# compilation requires **.NET 6.0 runtime** specifically, not .NET 8.0
- The Microsoft.Quantum.Sdk version 0.28.302812 used in this project only works with .NET 6.0
- Install .NET 6.0 runtime before attempting any Q# builds:
  ```bash
  # Install .NET 6.0 runtime (platform-specific)
  # Ubuntu 22.04: apt install dotnet-runtime-6.0
  # Other platforms: download from https://dotnet.microsoft.com/download/dotnet/6.0
  ```

### Environment Setup
- **Python 3.11+** with scientific computing stack
- **Node.js 18+** for website development
- **Azure CLI** for quantum resource estimation (optional)

## Working Development Commands

Always reference these validated commands. Build times measured on standard development machines.

### Python Development (✅ VALIDATED)
```bash
# Install Python dependencies - takes 60 seconds. NEVER CANCEL. Set timeout to 90+ seconds.
pip install numpy scipy matplotlib pandas seaborn plotly jupyter pyyaml jsonschema pytest

# Run classical analysis - takes 8 seconds
cd problems/03_qae_risk
make classical

# Generate analysis plots - takes 8 seconds  
make analyze
```

### Q# Development (⚠️ REQUIRES .NET 6.0)
```bash
# CRITICAL: Verify .NET 6.0 is available first
dotnet --list-runtimes | grep "6.0"

# If .NET 6.0 is available:
cd problems/03_qae_risk/qsharp
dotnet build --configuration Release  # Takes 25 seconds. NEVER CANCEL. Set timeout to 60+ seconds.
dotnet test                          # Takes 15 seconds if tests exist
dotnet run                          # Run quantum simulation
```

### Website Development (✅ VALIDATED)
```bash
cd website
npm install  # Takes 75 seconds. NEVER CANCEL. Set timeout to 120+ seconds.

# Note: Website build currently fails - missing pages/app directory
# npm run build  # Currently broken - needs implementation
```

### Complete Problem Analysis
```bash
cd problems/03_qae_risk

# Quick working demo (no Q# required) - takes 15 seconds total
make classical     # Classical Monte Carlo analysis
make analyze      # Generate comparison plots (will show warnings but complete)

# Full analysis (requires .NET 6.0 for Q# parts) - takes 45 seconds total  
make build        # Build Q# project
make test         # Run Q# tests
make estimate     # Resource estimation
make classical    # Classical baseline
make analyze      # Generate complete analysis
```

## Timing Expectations & Timeouts

### Short Operations (< 30 seconds)
- `make classical`: 8 seconds
- `make analyze`: 8 seconds  
- `dotnet build`: 25 seconds
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
cd problems/03_qae_risk
make classical
# Verify: ../estimates/classical_baseline.json created
# Verify: ../plots/*.png files generated

# 3. Test Q# compilation (if .NET 6.0 available)
cd problems/03_qae_risk/qsharp  
dotnet build
# Verify: Build succeeds without errors
```

### End-to-End Scenario Testing
```bash
# Complete working workflow without Q# dependencies
cd problems/03_qae_risk
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
│   ├── Program.qs        # Main quantum algorithm
│   ├── *.csproj          # Project configuration
│   └── bin/              # Compiled executables
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
- **03_qae_risk**: ✅ Classical analysis + analytical Q# baseline both build. Next milestone is implementing the genuine amplitude estimation circuit.
- **01_hubbard**: ✅ Classical analytical baseline + matching Q# program scaffolded. Ready for variational/phase-estimation upgrades.
- **02_catalysis**: ⏳ Planned
- **04_linear_solvers**: ⏳ Planned
- **05_qaoa_maxcut**: ⏳ Planned

## Frequently Used Commands

### Environment Check
```bash
# Verify development environment
python3 --version        # Should be 3.11+
dotnet --version         # Should show available versions
dotnet --list-runtimes   # Check for .NET 6.0 specifically
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

# 4. Classical development (validated for 01_hubbard and 03_qae_risk)
make classical
make analyze

# 5. Q# development (requires .NET 6.0)
make build
make test
make run
```

### Troubleshooting Common Issues

#### Q# Build Fails
```bash
# Check .NET runtime availability
dotnet --list-runtimes | grep "6.0"
# If missing: Install .NET 6.0 runtime for your platform
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
3. **Build validation**: `make build` to verify Q# compilation (if .NET 6.0 available)
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
- **Q# compilation requires .NET 6.0**: Main blocker for quantum development
- **03_qae_risk Q# project currently fails to build**: Placeholder amplitude estimation in `libs/common/Utils.qs` and `problems/03_qae_risk/qsharp/Program.qs` needs a real implementation.
- **Azure Quantum extension**: May not install in restricted network environments
- **Website incomplete**: Missing pages/app directory, build will fail
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
- `bin/`: Compiled Q# executables
- `__pycache__/`: Python bytecode (excluded from git)

Always check these locations after running analysis to verify outputs were generated correctly.