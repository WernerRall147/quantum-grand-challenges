# Climate Modeling (Problem 13) Makefile

PROBLEM_DIR := $(CURDIR)
PYTHON ?= python3
ifeq ($(OS),Windows_NT)
override PYTHON = python
endif

.PHONY: help build run classical analyze estimate sweep check-env clean

help:
	@echo "Climate Modeling - Available targets:"
	@echo "  make build       Build the Q# prototype"
	@echo "  make run         Execute the Q# placeholder entry point"
	@echo "  make classical   Run the diffusion baseline"
	@echo "  make analyze     Generate profile and convergence plots"
	@echo "  make estimate    Placeholder for resource estimation"
	@echo "  make clean       Remove generated artifacts"

build:
	@echo "Building Q# project..."
	dotnet build qsharp/QuantumClimate.csproj --configuration Release

run: build
	@echo "Running quantum placeholder..."
	dotnet run --project qsharp/QuantumClimate.csproj

classical:
	@echo "Simulating finite-difference diffusion baseline..."
	$(PYTHON) python/classical_baseline.py

analyze:
	@echo "Generating climate modeling plots..."
	$(PYTHON) python/analyze.py

estimate:
	@echo "Resource estimation pending HHL implementation."

sweep:
	@echo "Parameter sweep tooling not yet implemented."

check-env:
	@echo "Development environment check:"
	@echo "  Python: $$(python --version 2>/dev/null || echo 'Not found')"
	@echo "  .NET: $$(dotnet --version 2>/dev/null || echo 'Not found')"
	@echo "  Q# build: $$(dotnet build qsharp/QuantumClimate.csproj --verbosity quiet >/dev/null 2>&1 && echo 'Available' || echo 'Unavailable')"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf qsharp/bin qsharp/obj
	rm -rf python/__pycache__
	rm -f estimates/*.json
	rm -f plots/*.png
	@echo "Clean complete."
