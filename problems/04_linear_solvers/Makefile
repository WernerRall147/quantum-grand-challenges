# Quantum Linear Solvers Makefile

PROBLEM_DIR := $(CURDIR)
TOOLING_DIR := $(PROBLEM_DIR)/../../tooling
PYTHON ?= python3
ifeq ($(OS),Windows_NT)
override PYTHON = python
endif
ESTIMATOR := $(PYTHON) $(TOOLING_DIR)/estimator/run_estimation.py
TARGET ?= surface_code_generic_v1
INSTANCE ?= small

.PHONY: help build run test classical analyze estimate sweep check-env clean

help:
	@echo "Quantum Linear Solvers - Available targets:"
	@echo "  make build       Build the Q# project"
	@echo "  make run         Execute the Q# analytical baseline"
	@echo "  make classical   Run dense classical solves for every YAML instance"
	@echo "  make analyze     Generate diagnostic plots"
	@echo "  make estimate    Run resource estimation scaffold (requires quantum kernel)"
	@echo "  make check-env   Print the toolchain status"
	@echo "  make clean       Remove generated artifacts"

build:
	@echo "Building Q# project..."
	$(PYTHON) -c "import qsharp; qsharp.init(project_root='qsharp'); print('Q# compilation OK')"

run: build
	@echo "Running Q# analytical baseline..."
	$(PYTHON) -c "import qsharp; qsharp.init(project_root='qsharp'); qsharp.run('Main.RunLinearSolverBaseline()', shots=1)"

test:
	@echo "No dedicated Q# tests yet; build covers compilation."

classical:
	@echo "Solving YAML instances with classical dense linear algebra..."
	$(PYTHON) python/classical_baseline.py

analyze:
	@echo "Generating condition-number diagnostics..."
	$(PYTHON) python/analyze.py

estimate: build
	@echo "Running resource estimation for 04_linear_solvers..."
	$(ESTIMATOR) --all --problem 04_linear_solvers --targets surface_code_generic_v1,qubit_gate_ns_e3 --mock

sweep:
	@echo "Parameter sweep not yet wired for the linear solver problem."

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
