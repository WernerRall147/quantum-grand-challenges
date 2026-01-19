# Space Mission Planning (Problem 20) Makefile

PROBLEM_DIR := $(CURDIR)
PYTHON ?= python3
ifeq ($(OS),Windows_NT)
override PYTHON = python
endif

.PHONY: help build run classical analyze estimate sweep check-env clean

help:
	@echo "Space Mission Planning - Available targets:"
	@echo "  make build       Build the Q# prototype"
	@echo "  make run         Execute the Q# placeholder entry point"
	@echo "  make classical   Run the mission planning baseline"
	@echo "  make analyze     Generate delta-v and score plots"
	@echo "  make estimate    Placeholder for resource estimation"
	@echo "  make clean       Remove generated artifacts"

build:
	@echo "Building Q# project..."
	dotnet build qsharp/QuantumMission.csproj --configuration Release

run: build
	@echo "Running quantum placeholder..."
	dotnet run --project qsharp/QuantumMission.csproj

classical:
	@echo "Evaluating mission planning baseline..."
	$(PYTHON) python/classical_baseline.py

analyze:
	@echo "Generating mission planning plots..."
	$(PYTHON) python/analyze.py

estimate:
	@echo "Resource estimation pending quantum search encoding."

sweep:
	@echo "Parameter sweep tooling not yet implemented."

check-env:
	@echo "Development environment check:"
	@echo "  Python: $$(python --version 2>/dev/null || echo 'Not found')"
	@echo "  .NET: $$(dotnet --version 2>/dev/null || echo 'Not found')"
	@echo "  Q# build: $$(dotnet build qsharp/QuantumMission.csproj --verbosity quiet >/dev/null 2>&1 && echo 'Available' || echo 'Unavailable')"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf qsharp/bin qsharp/obj
	rm -rf python/__pycache__
	rm -f estimates/*.json
	rm -f plots/*.png
	@echo "Clean complete."
