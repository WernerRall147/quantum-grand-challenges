# QAOA Max-Cut Makefile

PROBLEM_DIR := $(shell pwd)
PYTHON := python

INSTANCE ?= small
DEPTH ?= 1
COARSE_SHOTS ?= 64
REFINED_SHOTS ?= 256

.PHONY: help build run test classical analyze estimate sweep check-env clean

help:
	@echo "QAOA Max-Cut - Available targets:"
	@echo "  make build       Build the Q# project"
	@echo "  make run         Execute the Q# driver (INSTANCE/DEPTH/COARSE_SHOTS/REFINED_SHOTS configurable)"
	@echo "  make classical   Run exhaustive Max-Cut baseline for all instances"
	@echo "  make analyze     Generate diagnostic plots"
	@echo "  make estimate    Placeholder for resource estimation"
	@echo "  make clean       Remove generated artifacts"

build:
	@echo "Building Q# library and host driver..."
	dotnet build host/QaoaMaxCut.Driver.csproj --configuration Release

run: build
	@echo "Running QAOA depth $(DEPTH) for instance '$(INSTANCE)'..."
	dotnet run --project host/QaoaMaxCut.Driver.csproj -- --instance $(INSTANCE) --depth $(DEPTH) --coarse-shots $(COARSE_SHOTS) --refined-shots $(REFINED_SHOTS)

test:
	@echo "No dedicated Q# tests yet; build covers compilation."

classical:
	@echo "Running brute-force Max-Cut baselines..."
	$(PYTHON) python/classical_baseline.py

analyze:
	@echo "Generating Max-Cut diagnostic plots..."
	$(PYTHON) python/analyze.py

estimate:
	@echo "Resource estimation will be wired once QAOA circuits land."

sweep:
	@echo "Parameter sweep not yet implemented for QAOA Max-Cut."

check-env:
	@echo "Development environment check:"
	@echo "  Python: $$(python --version 2>/dev/null || echo 'Not found')"
	@echo "  .NET: $$(dotnet --version 2>/dev/null || echo 'Not found')"
	@echo "  Q# build: $$(cd qsharp && dotnet build --verbosity quiet >/dev/null 2>&1 && echo 'Available' || echo 'Unavailable')"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf qsharp/bin qsharp/obj
	rm -rf host/bin host/obj
	rm -rf python/__pycache__
	rm -f estimates/*.json
	rm -f plots/*.png
	@echo "Clean complete."
