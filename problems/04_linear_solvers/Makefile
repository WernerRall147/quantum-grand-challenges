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
	cd qsharp && dotnet build --configuration Release

run: build
	@echo "Running Q# analytical baseline..."
	cd qsharp && dotnet run

test:
	@echo "No dedicated Q# tests yet; build covers compilation."

classical:
	@echo "Solving YAML instances with classical dense linear algebra..."
	$(PYTHON) python/classical_baseline.py

analyze:
	@echo "Generating condition-number diagnostics..."
	$(PYTHON) python/analyze.py

estimate:
	@echo "Resource estimation pipeline will be enabled once the HHL kernel lands."
	@echo "Use tooling/estimator/run_estimation.py manually against draft qsharp files if needed."

sweep:
	@echo "Parameter sweep not yet wired for the linear solver problem."

check-env:
	@echo "Development environment check:"
	@echo "  Python: $$(python --version 2>/dev/null || echo 'Not found')"
	@echo "  .NET: $$(dotnet --version 2>/dev/null || echo 'Not found')"
	@echo "  Q# build: $$(cd qsharp && dotnet build --verbosity quiet >/dev/null 2>&1 && echo 'Available' || echo 'Unavailable')"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf qsharp/bin qsharp/obj
	rm -rf python/__pycache__
	rm -f estimates/*.json
	rm -f plots/*.png
	@echo "Clean complete."
