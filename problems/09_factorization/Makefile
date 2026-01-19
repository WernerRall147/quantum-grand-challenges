# Quantum-Accelerated Factorization (Problem 09) Makefile

PROBLEM_DIR := $(CURDIR)
PYTHON ?= python3
ifeq ($(OS),Windows_NT)
override PYTHON = python
endif

.PHONY: help build run classical analyze estimate sweep check-env clean

help:
	@echo "Factorization - Available targets:"
	@echo "  make build       Build the Q# prototype"
	@echo "  make run         Execute the Q# placeholder entry point"
	@echo "  make classical   Run the Pollard Rho baseline"
	@echo "  make analyze     Generate iteration and runtime plots"
	@echo "  make estimate    Placeholder for resource estimation"
	@echo "  make clean       Remove generated artifacts"

build:
	@echo "Building Q# project..."
	dotnet build qsharp/Factorization.csproj --configuration Release

run: build
	@echo "Running quantum placeholder..."
	dotnet run --project qsharp/Factorization.csproj

classical:
	@echo "Factoring instances with Pollard Rho baseline..."
	$(PYTHON) python/classical_baseline.py

analyze:
	@echo "Generating plots from baseline metrics..."
	$(PYTHON) python/analyze.py

estimate:
	@echo "Resource estimation pending Shor implementation."

sweep:
	@echo "Parameter sweep tooling not yet implemented."

check-env:
	@echo "Development environment check:"
	@echo "  Python: $$(python --version 2>/dev/null || echo 'Not found')"
	@echo "  .NET: $$(dotnet --version 2>/dev/null || echo 'Not found')"
	@echo "  Q# build: $$(dotnet build qsharp/Factorization.csproj --verbosity quiet >/dev/null 2>&1 && echo 'Available' || echo 'Unavailable')"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf qsharp/bin qsharp/obj
	rm -rf python/__pycache__
	rm -f estimates/*.json
	rm -f plots/*.png
	@echo "Clean complete."
