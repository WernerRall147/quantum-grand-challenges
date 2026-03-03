# QAOA Max-Cut Makefile

PROBLEM_DIR := $(CURDIR)
PYTHON ?= python3
ifeq ($(OS),Windows_NT)
override PYTHON = python
endif

INSTANCE ?= small
DEPTH ?= 1
COARSE_SHOTS ?= 64
REFINED_SHOTS ?= 256
TRIALS ?= 16
DEPTHS ?= 1,2,3
NOISE_LEVELS ?= 0.00,0.01,0.02,0.05,0.10
NOISE_SAMPLES ?= 256
ESTIMATE_MOCK ?= 1

ifeq ($(ESTIMATE_MOCK),1)
ESTIMATE_FLAGS := --mock
else
ESTIMATE_FLAGS :=
endif

.PHONY: help build run run-all depth-sweep noise-sweep validate-assumptions validate-quality evidence test classical analyze estimate estimate-all sweep check-env clean

help:
	@echo "QAOA Max-Cut - Available targets:"
	@echo "  make build       Build the Q# project"
	@echo "  make run         Execute the Q# driver (INSTANCE/DEPTH/COARSE_SHOTS/REFINED_SHOTS configurable)"
	@echo "  make run-all     Run QAOA for small/medium/large instances"
	@echo "  make depth-sweep Run depth sweep for an instance (DEPTHS=1,2,3 by default)"
	@echo "  make noise-sweep Run readout-noise sensitivity sweep for a selected instance/depth"
	@echo "  make validate-assumptions Validate backend/transpilation assumptions artifact"
	@echo "  make validate-quality Validate depth/noise evidence quality thresholds"
	@echo "  make evidence    Rebuild quantum artifacts and regenerate plots/summary"
	@echo "  make classical   Run exhaustive Max-Cut baseline for all instances"
	@echo "  make analyze     Generate diagnostic plots"
	@echo "  make estimate    Generate estimator params and run estimator automation (ESTIMATE_MOCK=1 by default)"
	@echo "  make estimate-all Generate estimator params and estimates for small/medium/large"
	@echo "  make clean       Remove generated artifacts"

build:
	@echo "Building Q# library and host driver..."
	dotnet build host/QaoaMaxCut.Driver.csproj --configuration Release

run: build
	@echo "Running QAOA depth $(DEPTH) for instance '$(INSTANCE)'..."
	dotnet run --project host/QaoaMaxCut.Driver.csproj -- --instance $(INSTANCE) --depth $(DEPTH) --coarse-shots $(COARSE_SHOTS) --refined-shots $(REFINED_SHOTS) --trials $(TRIALS)

run-all: build
	@echo "Running QAOA depth $(DEPTH) for instances: small, medium, large..."
	dotnet run --project host/QaoaMaxCut.Driver.csproj -- --instance small --depth $(DEPTH) --coarse-shots $(COARSE_SHOTS) --refined-shots $(REFINED_SHOTS) --trials $(TRIALS)
	dotnet run --project host/QaoaMaxCut.Driver.csproj -- --instance medium --depth $(DEPTH) --coarse-shots $(COARSE_SHOTS) --refined-shots $(REFINED_SHOTS) --trials $(TRIALS)
	dotnet run --project host/QaoaMaxCut.Driver.csproj -- --instance large --depth $(DEPTH) --coarse-shots $(COARSE_SHOTS) --refined-shots $(REFINED_SHOTS) --trials $(TRIALS)

depth-sweep: build
	@echo "Running QAOA depth sweep for instance '$(INSTANCE)' with depths $(DEPTHS)..."
	$(PYTHON) python/depth_sweep.py --instance $(INSTANCE) --depths $(DEPTHS) --coarse-shots $(COARSE_SHOTS) --refined-shots $(REFINED_SHOTS) --trials $(TRIALS)

noise-sweep:
	@echo "Running QAOA noise sweep for instance '$(INSTANCE)' at depth $(DEPTH)..."
	$(PYTHON) python/noise_sweep.py --instance $(INSTANCE) --depth $(DEPTH) --noise-levels $(NOISE_LEVELS) --samples-per-trial $(NOISE_SAMPLES)

validate-assumptions:
	@echo "Validating backend/transpilation assumptions evidence..."
	$(PYTHON) python/validate_backend_assumptions.py

validate-quality:
	@echo "Validating depth/noise evidence quality thresholds..."
	$(PYTHON) python/validate_evidence_quality.py

evidence: classical run-all analyze estimate-all validate-assumptions validate-quality
	@echo "QAOA evidence bundle refreshed in estimates/ and plots/."

test:
	@echo "No dedicated Q# tests yet; build covers compilation."

classical:
	@echo "Running brute-force Max-Cut baselines..."
	$(PYTHON) python/classical_baseline.py

analyze:
	@echo "Generating Max-Cut diagnostic plots..."
	$(PYTHON) python/analyze.py
	@echo "Generating quantum/classical markdown summary..."
	$(PYTHON) python/compare.py

estimate:
	@echo "Preparing estimator parameter payload from latest QAOA artifact..."
	$(PYTHON) python/prepare_estimator_params.py --instance $(INSTANCE) --depth $(DEPTH)
	@echo "Running estimator automation for QAOA Max-Cut (mock mode by default)..."
	$(PYTHON) ../../tooling/estimator/run_estimation.py --all --problem 05_qaoa_maxcut --params-file estimates/estimator_params_$(INSTANCE)_d$(DEPTH).json --targets surface_code_generic_v1,qubit_gate_ns_e3 $(ESTIMATE_FLAGS) --summary-path ../../tooling/estimator/output/qaoa_summary_$(INSTANCE).json

estimate-all:
	@echo "Preparing estimator parameter payloads for small/medium/large..."
	$(PYTHON) python/prepare_estimator_params.py --instance small --depth $(DEPTH)
	$(PYTHON) python/prepare_estimator_params.py --instance medium --depth $(DEPTH)
	$(PYTHON) python/prepare_estimator_params.py --instance large --depth $(DEPTH)
	@echo "Running estimator automation for all QAOA benchmark instances..."
	$(PYTHON) ../../tooling/estimator/run_estimation.py --all --problem 05_qaoa_maxcut --params-file estimates/estimator_params_small_d$(DEPTH).json --targets surface_code_generic_v1,qubit_gate_ns_e3 $(ESTIMATE_FLAGS) --summary-path ../../tooling/estimator/output/qaoa_summary_small.json
	$(PYTHON) ../../tooling/estimator/run_estimation.py --all --problem 05_qaoa_maxcut --params-file estimates/estimator_params_medium_d$(DEPTH).json --targets surface_code_generic_v1,qubit_gate_ns_e3 $(ESTIMATE_FLAGS) --summary-path ../../tooling/estimator/output/qaoa_summary_medium.json
	$(PYTHON) ../../tooling/estimator/run_estimation.py --all --problem 05_qaoa_maxcut --params-file estimates/estimator_params_large_d$(DEPTH).json --targets surface_code_generic_v1,qubit_gate_ns_e3 $(ESTIMATE_FLAGS) --summary-path ../../tooling/estimator/output/qaoa_summary_large.json
	$(PYTHON) python/prune_estimator_artifacts.py --keep-per-target 3
	$(PYTHON) python/summarize_estimator.py

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
