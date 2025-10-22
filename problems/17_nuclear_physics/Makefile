# Quantum Nuclear Physics (Problem 17) Makefile

PROBLEM_DIR := $(shell pwd)
PYTHON := python

.PHONY: help build run classical analyze estimate sweep check-env clean

help:
	@echo "Quantum Nuclear Physics - Available targets:"
	@echo "  make build       Build the Q# prototype"
	@echo "  make run         Execute the Q# placeholder entry point"
	@echo "  make classical   Run the pionless EFT baseline"
	@echo "  make analyze     Generate binding and scattering plots"
	@echo "  make estimate    Placeholder for resource estimation"
	@echo "  make clean       Remove generated artifacts"

build:
	@echo "Building Q# project..."
	dotnet build qsharp/QuantumNuclear.csproj --configuration Release

run: build
	@echo "Running quantum placeholder..."
	dotnet run --project qsharp/QuantumNuclear.csproj

classical:
	@echo "Evaluating pionless EFT baseline..."
	$(PYTHON) python/classical_baseline.py

analyze:
	@echo "Generating EFT plots..."
	$(PYTHON) python/analyze.py

estimate:
	@echo "Resource estimation pending Hamiltonian encoding."

sweep:
	@echo "Parameter sweep tooling not yet implemented."

check-env:
	@echo "Development environment check:"
	@echo "  Python: $$(python --version 2>/dev/null || echo 'Not found')"
	@echo "  .NET: $$(dotnet --version 2>/dev/null || echo 'Not found')"
	@echo "  Q# build: $$(dotnet build qsharp/QuantumNuclear.csproj --verbosity quiet >/dev/null 2>&1 && echo 'Available' || echo 'Unavailable')"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf qsharp/bin qsharp/obj
	rm -rf python/__pycache__
	rm -f estimates/*.json
	rm -f plots/*.png
	@echo "Clean complete."
