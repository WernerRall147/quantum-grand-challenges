# Makefile for QAE Risk Analysis Problem

PROBLEM_DIR := $(CURDIR)
TOOLING_DIR := $(PROBLEM_DIR)/../../tooling
PYTHON ?= python3
ifeq ($(OS),Windows_NT)
override PYTHON = python
endif
ESTIMATOR := $(PYTHON) $(TOOLING_DIR)/estimator/run_estimation.py
AZQ := $(PYTHON) $(TOOLING_DIR)/azq/job_manager.py

# Default target for resource estimation
TARGET ?= surface_code_generic_v1
INSTANCE ?= small

# Python environment
VENV_DIR := venv

.PHONY: help build test estimate sweep analyze calibrate compare clean setup-python install-deps

help:
	@echo "QAE Risk Analysis - Available targets:"
	@echo ""
	@echo "  setup-python  - Create Python virtual environment"
	@echo "  install-deps  - Install Python dependencies"
	@echo "  build         - Build Q# project"
	@echo "  test          - Run Q# unit tests"
	@echo "  run           - Run Q# program locally"
	@echo "  estimate      - Run resource estimation (TARGET=$(TARGET))"
	@echo "  sweep         - Run parameter sweep across multiple targets"
	@echo "  analyze       - Generate analysis and plots"
	@echo "  calibrate     - Run repeated quantum calibration ensemble and plots"
	@echo "  compare       - Compare with classical baseline"
	@echo "  classical     - Run classical Monte Carlo baseline"
	@echo "  clean         - Clean build artifacts"
	@echo ""
	@echo "Instance options: small, medium, large"
	@echo "Target options: surface_code_generic_v1, qubit_gate_ns_e3, qubit_gate_ns_e4"

# Python setup
setup-python:
	@echo "Setting up Python virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created in $(VENV_DIR)/"
	@echo "Activate with: source $(VENV_DIR)/bin/activate (Linux/Mac) or $(VENV_DIR)\\Scripts\\activate (Windows)"

install-deps: 
	@echo "Installing Python dependencies..."
	pip install numpy scipy matplotlib pandas seaborn plotly jupyter pyyaml jsonschema pytest

# Q# build and test
build:
	@echo "Building Q# project..."
	cd qsharp && dotnet build --configuration Release

test: build
	@echo "Running Q# tests..."
	cd qsharp && dotnet test --verbosity normal

run: build
	@echo "Running Q# QAE risk analysis..."
	cd qsharp && dotnet run

# Resource estimation
estimate: build
	@echo "Running resource estimation with target: $(TARGET) and instance: $(INSTANCE)"
	$(ESTIMATOR) $(PROBLEM_DIR) --target $(TARGET) --params instances/$(INSTANCE).yaml

sweep: build
	@echo "Running resource estimation parameter sweep..."
	$(ESTIMATOR) $(PROBLEM_DIR) --sweep

# Analysis and visualization
classical:
	@echo "Running classical Monte Carlo baseline..."
	cd python && $(PYTHON) classical_baseline.py

analyze: 
	@echo "Generating analysis and plots..."
	cd python && $(PYTHON) analyze.py

CALIBRATION_RUNS ?= 20

calibrate:
	@echo "Running QAE calibration ensemble with $(CALIBRATION_RUNS) runs..."
	cd python && $(PYTHON) analyze.py --ensemble-runs $(CALIBRATION_RUNS)

compare: classical analyze
	@echo "Complete comparison analysis finished"
	@echo "Check plots/ directory for visualizations"

# Azure Quantum (optional)
list-targets:
	@echo "Available Azure Quantum targets:"
	@if [ -n "$(AZQ_WORKSPACE)" ] && [ -n "$(AZQ_RESOURCE_GROUP)" ]; then \
		$(AZQ) list-targets --workspace $(AZQ_WORKSPACE) --resource-group $(AZQ_RESOURCE_GROUP); \
	else \
		echo "Set AZQ_WORKSPACE and AZQ_RESOURCE_GROUP environment variables"; \
	fi

submit-job:
	@echo "Submitting job to Azure Quantum..."
	@if [ -n "$(AZQ_WORKSPACE)" ] && [ -n "$(AZQ_RESOURCE_GROUP)" ] && [ -n "$(AZQ_TARGET)" ]; then \
		mkdir -p runs; \
		$(AZQ) run qsharp/Program.qs --target $(AZQ_TARGET) --output-dir runs/ \
			--workspace $(AZQ_WORKSPACE) --resource-group $(AZQ_RESOURCE_GROUP); \
	else \
		echo "Set AZQ_WORKSPACE, AZQ_RESOURCE_GROUP, and AZQ_TARGET environment variables"; \
	fi

# Validation and testing
validate-instances:
	@echo "Validating instance files..."
	@for instance in instances/*.yaml; do \
		echo "Validating $$instance..."; \
		$(PYTHON) -c "import yaml; yaml.safe_load(open('$$instance'))" || exit 1; \
	done
	@echo "✅ All instance files are valid YAML"

validate-results:
	@echo "Validating result files against schema..."
	@for result in estimates/*.json; do \
		if [ -f "$$result" ]; then \
			echo "Validating $$result..."; \
			$(PYTHON) -c "\
				import json, jsonschema; \
				schema = json.load(open('$(TOOLING_DIR)/schema/result.json')); \
				result = json.load(open('$$result')); \
				jsonschema.validate(result, schema); \
				print('✅ $$result is valid')" || exit 1; \
		fi \
	done

# Clean up
clean:
	@echo "Cleaning build artifacts..."
	cd qsharp && dotnet clean
	rm -rf qsharp/bin qsharp/obj
	rm -rf python/__pycache__
	rm -rf estimates/temp_*
	rm -rf plots/*.png
	@echo "Clean complete"

# Full workflow targets
quick-demo: build run classical
	@echo "🎉 Quick demo complete!"
	@echo "   - Built and ran Q# program"  
	@echo "   - Generated classical baseline"
	@echo "   - Ready for analysis with 'make analyze'"

full-analysis: build test estimate classical analyze
	@echo "🎉 Full analysis complete!"
	@echo "   - Q# implementation tested"
	@echo "   - Resource estimation complete" 
	@echo "   - Classical baseline computed"
	@echo "   - Analysis plots generated"
	@echo ""
	@echo "📊 Check these directories:"
	@echo "   - estimates/ for resource estimates"
	@echo "   - plots/ for visualizations"

# Development helpers
check-env:
	@echo "Development environment check:"
	@echo "  Python: $$(python3 --version 2>/dev/null || echo 'Not found')"
	@echo "  .NET: $$(dotnet --version 2>/dev/null || echo 'Not found')"
	@echo "  Q# compiler: $$(cd qsharp && dotnet build --verbosity quiet > /dev/null 2>&1 && echo 'Available' || echo 'Not available')"
	@echo "  Azure CLI: $$(az --version 2>/dev/null | head -1 || echo 'Not found')"
	@echo "  Quantum extension: $$(az extension list --output table 2>/dev/null | grep quantum || echo 'Not installed')"

status:
	@echo "QAE Risk Analysis - Status:"
	@echo ""
	@echo "📁 Files:"
	@echo "  Q# sources: $$(find qsharp -name '*.qs' | wc -l) files"
	@echo "  Python scripts: $$(find python -name '*.py' | wc -l) files"  
	@echo "  Instance files: $$(find instances -name '*.yaml' | wc -l) files"
	@echo "  Results: $$(find estimates -name '*.json' 2>/dev/null | wc -l) files"
	@echo ""
	@echo "🔧 Last build: $$(stat qsharp/bin/Release/net6.0/QAERisk.dll 2>/dev/null | grep Modify || echo 'Never built')"
	@echo "📊 Last analysis: $$(stat plots/analysis_report.md 2>/dev/null | grep Modify || echo 'Never run')"

# Documentation
docs:
	@echo "Generating documentation..."
	@echo "# QAE Risk Analysis - Auto-generated Documentation" > docs.md
	@echo "" >> docs.md
	@echo "## Q# Implementation" >> docs.md
	@echo "\`\`\`qsharp" >> docs.md
	@head -50 qsharp/Program.qs >> docs.md
	@echo "\`\`\`" >> docs.md
	@echo "" >> docs.md
	@echo "## Available Instances" >> docs.md
	@for instance in instances/*.yaml; do \
		echo "### $$(basename $$instance .yaml)" >> docs.md; \
		echo "\`\`\`yaml" >> docs.md; \
		head -20 $$instance >> docs.md; \
		echo "\`\`\`" >> docs.md; \
		echo "" >> docs.md; \
	done
	@echo "Documentation generated: docs.md"
