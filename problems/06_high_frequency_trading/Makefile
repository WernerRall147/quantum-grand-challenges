# High-Frequency Trading (Problem 06) Makefile

PROBLEM_DIR := $(CURDIR)
PYTHON ?= python3
ifeq ($(OS),Windows_NT)
override PYTHON = python
endif

INSTANCE ?= small

.PHONY: help build run classical analyze estimate sweep check-env clean

help:
	@echo "HFT Quantum Challenge - Available targets:"
	@echo "  make build       Build the Q# prototype"
	@echo "  make run         Execute the Q# placeholder entry point"
	@echo "  make classical   Run the moving-average classical baseline"
	@echo "  make analyze     Generate price/equity plots"
	@echo "  make estimate    Placeholder for resource estimation"
	@echo "  make clean       Remove generated artifacts"

build:
	@echo "Building Q# project..."
	dotnet build qsharp/HighFrequencyTrading.csproj --configuration Release

run: build
	@echo "Running Q# prototype..."
	dotnet run --project qsharp/HighFrequencyTrading.csproj

classical:
	@echo "Running classical trading baseline..."
	$(PYTHON) python/classical_baseline.py

analyze:
	@echo "Generating plots from classical baseline..."
	$(PYTHON) python/analyze.py

estimate:
	@echo "Resource estimation pending quantum model implementation."

sweep:
	@echo "Parameter sweep tooling not yet implemented."

check-env:
	@echo "Development environment check:"
	@echo "  Python: $$(python --version 2>/dev/null || echo 'Not found')"
	@echo "  .NET: $$(dotnet --version 2>/dev/null || echo 'Not found')"
	@echo "  Q# build: $$(dotnet build qsharp/HighFrequencyTrading.csproj --verbosity quiet >/dev/null 2>&1 && echo 'Available' || echo 'Unavailable')"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf qsharp/bin qsharp/obj
	rm -rf python/__pycache__
	rm -f estimates/*.json
	rm -f plots/*.png
	@echo "Clean complete."
