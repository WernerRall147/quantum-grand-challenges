#!/bin/bash
# Quantum Grand Challenges - DevContainer Setup Script
# This script runs after the container is created to install additional tools

set -e

echo "🚀 Setting up Quantum Grand Challenges development environment..."

# Update package lists
sudo apt-get update

# Install Azure CLI quantum extension
echo "📦 Installing Azure CLI Quantum extension..."
az extension add --name quantum --only-show-errors || echo "Quantum extension already installed"

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip
pip install \
    numpy \
    scipy \
    matplotlib \
    pandas \
    jupyter \
    qiskit \
    cirq \
    pytest \
    black \
    pylint \
    notebook \
    plotly \
    seaborn \
    pyyaml \
    jsonschema

# Install Node.js dependencies for website
echo "📦 Installing Node.js dependencies..."
npm install -g \
    @azure/quantum-chemistry \
    typescript \
    ts-node \
    prettier \
    eslint

# Create symbolic links for tooling scripts
echo "🔗 Setting up tooling scripts..."
sudo ln -sf /workspaces/quantum-grand-challenges/tooling/estimator/run_estimation.py /usr/local/bin/qgc-estimate
sudo ln -sf /workspaces/quantum-grand-challenges/tooling/azq/job_manager.py /usr/local/bin/qgc-azq
sudo chmod +x /usr/local/bin/qgc-estimate /usr/local/bin/qgc-azq

# Set up Git configuration (if not already configured)
echo "🔧 Configuring Git..."
if [ -z "$(git config --global user.name)" ]; then
    echo "Please configure Git with your name and email:"
    echo "git config --global user.name 'Your Name'"
    echo "git config --global user.email 'your.email@example.com'"
fi

# Create shared libraries directory structure
echo "📚 Setting up shared libraries..."
mkdir -p /workspaces/quantum-grand-challenges/libs/{common,algorithms,oracles}

# Set up pre-commit hooks (if .pre-commit-config.yaml exists)
if [ -f "/workspaces/quantum-grand-challenges/.pre-commit-config.yaml" ]; then
    echo "🪝 Installing pre-commit hooks..."
    pip install pre-commit
    cd /workspaces/quantum-grand-challenges
    pre-commit install
fi

# Verify Q# installation
echo "✅ Verifying Q# installation..."
if command -v dotnet &> /dev/null; then
    dotnet --list-sdks | grep -E "(5\.|6\.|7\.|8\.)" || echo "⚠️  Warning: .NET SDK 5.0+ recommended for Q# development"
else
    echo "❌ .NET SDK not found. Q# development may not work properly."
fi

# Check Azure CLI authentication status
echo "🔐 Checking Azure CLI authentication..."
if az account show &> /dev/null; then
    echo "✅ Azure CLI is authenticated"
    SUBSCRIPTION=$(az account show --query name -o tsv)
    echo "📋 Current subscription: $SUBSCRIPTION"
else
    echo "⚠️  Azure CLI not authenticated. Run 'az login' to authenticate."
fi

# Create default problem structure template
echo "📁 Creating problem template..."
mkdir -p /tmp/problem_template/{qsharp,python,instances,estimates}

cat > /tmp/problem_template/README.md << 'EOF'
# Problem: [Problem Name]

## Overview
Brief description of the quantum computing problem being addressed.

## Algorithm
Primary quantum algorithm(s) used and theoretical approach.

## Implementation
- **Q# Code**: `qsharp/` directory contains quantum implementations
- **Analysis**: `python/` directory contains classical analysis and plotting
- **Instances**: `instances/` directory contains test problem instances
- **Results**: `estimates/` directory contains resource estimation outputs

## Usage

### Build and Test
```bash
make build
make test
```

### Resource Estimation
```bash
make estimate                    # Default target
make estimate TARGET=<target>    # Specific target
make sweep                       # Parameter sweep
```

### Analysis and Plotting
```bash
make analyze                     # Generate analysis plots
make compare                     # Compare with classical baseline
```

## Status
- [ ] Q# implementation complete
- [ ] Unit tests passing
- [ ] Resource estimation complete
- [ ] Classical baseline implemented
- [ ] Analysis and visualization complete
- [ ] Documentation complete

## Results Summary
Latest resource estimates:
- **Logical Qubits**: TBD
- **Physical Qubits**: TBD  
- **T-count**: TBD
- **Runtime**: TBD

## References
- Paper/source references
- Related work
EOF

cat > /tmp/problem_template/Makefile << 'EOF'
# Makefile for Quantum Grand Challenge Problem

PROBLEM_DIR := $(shell pwd)
TOOLING_DIR := $(PROBLEM_DIR)/../../tooling
ESTIMATOR := python $(TOOLING_DIR)/estimator/run_estimation.py
AZQ := python $(TOOLING_DIR)/azq/job_manager.py

# Default target for resource estimation
TARGET ?= surface_code_generic_v1

.PHONY: build test estimate sweep analyze compare clean help

help:
	@echo "Available targets:"
	@echo "  build     - Build Q# project"
	@echo "  test      - Run unit tests"
	@echo "  estimate  - Run resource estimation (TARGET=$(TARGET))"
	@echo "  sweep     - Run parameter sweep across multiple targets"
	@echo "  analyze   - Generate analysis and plots"
	@echo "  compare   - Compare with classical baseline"
	@echo "  clean     - Clean build artifacts"

build:
	@echo "Building Q# project..."
	cd qsharp && dotnet build

test: build
	@echo "Running tests..."
	cd qsharp && dotnet test

estimate: build
	@echo "Running resource estimation with target: $(TARGET)"
	$(ESTIMATOR) $(PROBLEM_DIR) --target $(TARGET)

sweep: build
	@echo "Running parameter sweep..."
	$(ESTIMATOR) $(PROBLEM_DIR) --sweep

analyze:
	@echo "Generating analysis..."
	cd python && python analyze.py

compare:
	@echo "Comparing with classical baseline..."
	cd python && python classical_baseline.py

clean:
	@echo "Cleaning build artifacts..."
	cd qsharp && dotnet clean
	rm -rf estimates/temp_*
	rm -rf python/__pycache__

# Azure Quantum job management
list-targets:
	@echo "Available Azure Quantum targets:"
	$(AZQ) list-targets --workspace $(AZQ_WORKSPACE) --resource-group $(AZQ_RESOURCE_GROUP)

submit-job:
	@echo "Submitting job to Azure Quantum..."
	$(AZQ) run qsharp/Program.qs --target $(AZQ_TARGET) --output-dir runs/

EOF

echo "✅ Problem template created in /tmp/problem_template"
echo "   Copy this template when creating new problems"

# Print setup summary
echo ""
echo "🎉 Quantum Grand Challenges setup complete!"
echo ""
echo "Available commands:"
echo "  qgc-estimate <problem_dir> [--target <target>] - Run resource estimation"
echo "  qgc-azq <command> - Azure Quantum job management"
echo ""
echo "Next steps:"
echo "1. Authenticate with Azure: az login"
echo "2. Set up Azure Quantum workspace (if using hardware)"
echo "3. Choose a problem to work on in problems/ directory"
echo "4. Follow the standard problem template structure"
echo ""
echo "Happy quantum computing! 🌌"
