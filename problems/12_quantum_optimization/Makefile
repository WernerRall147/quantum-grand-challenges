# Quantum-Assisted Optimization (Problem 12) Makefile

PROBLEM_DIR := $(CURDIR)
PYTHON ?= python3
ifeq ($(OS),Windows_NT)
PYTHON := $(CURDIR)/../../.venv/Scripts/python.exe
endif

.PHONY: help build run classical analyze test estimate sweep check-env clean

help:
	@echo "Quantum Optimization - Available targets:"
	@echo "  make build       Build the Q# prototype"
	@echo "  make run         Execute the Q# placeholder entry point"
	@echo "  make classical   Run the weighted tardiness baseline"
	@echo "  make analyze     Generate tardiness and utilization plots"
	@echo "  make test        Run deterministic baseline checks"
	@echo "  make estimate    Placeholder for resource estimation"
	@echo "  make clean       Remove generated artifacts"

build:
	@echo "Building Q# project..."
	$(PYTHON) -c "import qsharp; qsharp.init(project_root='qsharp'); print('Q# compilation OK')"

run: build
	@echo "Running quantum placeholder..."
	$(PYTHON) -c "import qsharp; qsharp.init(project_root='qsharp'); qsharp.run('Main.RunSchedulingOptimization()', shots=1)"

classical:
	@echo "Evaluating greedy weighted tardiness baseline..."
	$(PYTHON) python/classical_baseline.py

analyze:
	@echo "Generating optimization baseline plots..."
	$(PYTHON) python/analyze.py

test: classical
	@echo "Running deterministic baseline checks..."
	$(PYTHON) python/test_baseline.py

estimate:
	@echo "Resource estimation pending QAOA implementation."

sweep:
	@echo "Parameter sweep tooling not yet implemented."

check-env:
	@echo "Development environment check:"
	@echo "  Python: $$(python --version 2>/dev/null || echo 'Not found')"
	@echo "  .NET: $$(dotnet --version 2>/dev/null || echo 'Not found')"
	@echo "  Q# build: $$($(PYTHON) -c 'import qsharp; qsharp.init(project_root=\"qsharp\"); print(\"Available\")' 2>/dev/null || echo 'Unavailable')"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf qsharp/bin qsharp/obj
	rm -rf python/__pycache__
	rm -f estimates/*.json
	rm -f plots/*.png
	@echo "Clean complete."
