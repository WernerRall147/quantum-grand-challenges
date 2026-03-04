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
TARGET_ID ?= microsoft.estimator
NOISE_LEVELS ?= 0.00,0.01,0.02,0.05,0.10
NOISE_SAMPLES ?= 256
AZURE_ENV_FILE ?= .env.azure.local
AZURE_MANUAL_JOB_ID ?=
AZURE_RESULT_STATUS ?=
ESTIMATE_MOCK ?= 1

ifeq ($(ESTIMATE_MOCK),1)
ESTIMATE_FLAGS := --mock
else
ESTIMATE_FLAGS :=
endif

.PHONY: help build run run-all depth-sweep noise-sweep azure-manifest azure-runbook validate-azure-env validate-azure-cli validate-azure-manifest azure-submit azure-collect azure-collect-auto validate-assumptions validate-quality evidence test classical analyze estimate estimate-all sweep check-env clean

help:
	@echo "QAOA Max-Cut - Available targets:"
	@echo "  make build       Build the Q# project"
	@echo "  make run         Execute the Q# driver (INSTANCE/DEPTH/COARSE_SHOTS/REFINED_SHOTS configurable)"
	@echo "  make run-all     Run QAOA for small/medium/large instances"
	@echo "  make depth-sweep Run depth sweep for an instance (DEPTHS=1,2,3 by default)"
	@echo "  make noise-sweep Run readout-noise sensitivity sweep for a selected instance/depth"
	@echo "  make azure-manifest Build Azure Quantum job manifest contract for selected instance/depth"
	@echo "  make azure-runbook Print Azure auth + run checklist with current variables"
	@echo "  make validate-azure-env Validate manual Azure auth/config env file before cloud operations"
	@echo "  make validate-azure-cli Validate Azure CLI login/extension/workspace readiness"
	@echo "  make validate-azure-manifest Validate Azure Quantum job manifest and referenced evidence"
	@echo "  make azure-submit Record manual Azure submission metadata in manifest (requires AZURE_MANUAL_JOB_ID)"
	@echo "  make azure-collect Record manual Azure result status in manifest (requires AZURE_RESULT_STATUS)"
	@echo "  make azure-collect-auto Fetch Azure result status via az CLI and update manifest"
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

azure-manifest:
	@echo "Preparing Azure Quantum job manifest for instance '$(INSTANCE)' at depth $(DEPTH)..."
	$(PYTHON) python/prepare_azure_job_manifest.py --instance $(INSTANCE) --depth $(DEPTH) --coarse-shots $(COARSE_SHOTS) --refined-shots $(REFINED_SHOTS) --trials $(TRIALS) --target-id $(TARGET_ID)

azure-runbook:
	@echo "Azure Quantum Runbook (QAOA MaxCut)"
	@echo "==================================="
	@echo "Current defaults: INSTANCE=$(INSTANCE) DEPTH=$(DEPTH) TARGET_ID=$(TARGET_ID)"
	@echo ""
	@echo "1) Create local auth/workspace file (manual):"
	@echo "   cp .env.azure.example .env.azure.local"
	@echo "   Then edit .env.azure.local and replace all CHANGE_ME values."
	@echo ""
	@echo "2) Validate env gate:"
	@echo "   make validate-azure-env AZURE_ENV_FILE=$(AZURE_ENV_FILE)"
	@echo ""
	@echo "3) Build/validate manifest:"
	@echo "   make azure-manifest INSTANCE=$(INSTANCE) DEPTH=$(DEPTH) TARGET_ID=$(TARGET_ID)"
	@echo "   make validate-azure-manifest INSTANCE=$(INSTANCE) DEPTH=$(DEPTH)"
	@echo ""
	@echo "4) After real Azure submission, stamp job metadata:"
	@echo "   make azure-submit INSTANCE=$(INSTANCE) DEPTH=$(DEPTH) AZURE_MANUAL_JOB_ID=<azure_job_id>"
	@echo ""
	@echo "5) After completion, stamp result status:"
	@echo "   make azure-collect INSTANCE=$(INSTANCE) DEPTH=$(DEPTH) AZURE_RESULT_STATUS=succeeded"
	@echo "   or fetch status directly from Azure CLI:"
	@echo "   make azure-collect-auto INSTANCE=$(INSTANCE) DEPTH=$(DEPTH)"
	@echo ""
	@echo "Manual gate reminder: Azure operations are blocked until .env.azure.local is valid."

validate-azure-env:
	@echo "Validating Azure env file $(AZURE_ENV_FILE)..."
	$(PYTHON) python/validate_azure_env.py --env-file $(AZURE_ENV_FILE)

validate-azure-cli: validate-azure-env
	@echo "Validating Azure CLI preflight for env file $(AZURE_ENV_FILE)..."
	$(PYTHON) python/validate_azure_cli.py --env-file $(AZURE_ENV_FILE)

validate-azure-manifest: validate-azure-env
	@echo "Validating Azure Quantum job manifest for instance '$(INSTANCE)' at depth $(DEPTH)..."
	$(PYTHON) python/validate_azure_job_manifest.py --manifest estimates/azure_job_manifest_$(INSTANCE)_d$(DEPTH).json

azure-submit: validate-azure-env
	@echo "Recording Azure submission metadata for instance '$(INSTANCE)' at depth $(DEPTH)..."
	$(PYTHON) python/submit_azure_job.py --manifest estimates/azure_job_manifest_$(INSTANCE)_d$(DEPTH).json --env-file $(AZURE_ENV_FILE) --manual-job-id $(AZURE_MANUAL_JOB_ID)

azure-collect: validate-azure-env
	@echo "Recording Azure result metadata for instance '$(INSTANCE)' at depth $(DEPTH)..."
	$(PYTHON) python/collect_azure_job.py --manifest estimates/azure_job_manifest_$(INSTANCE)_d$(DEPTH).json --env-file $(AZURE_ENV_FILE) --result-status $(AZURE_RESULT_STATUS)

azure-collect-auto: validate-azure-cli
	@echo "Fetching Azure result metadata from az CLI for instance '$(INSTANCE)' at depth $(DEPTH)..."
	$(PYTHON) python/collect_azure_job.py --manifest estimates/azure_job_manifest_$(INSTANCE)_d$(DEPTH).json --env-file $(AZURE_ENV_FILE) --fetch-from-azure

validate-assumptions:
	@echo "Validating backend/transpilation assumptions evidence..."
	$(PYTHON) python/validate_backend_assumptions.py

validate-quality:
	@echo "Validating depth/noise evidence quality thresholds and writing evidence_quality_report.* ..."
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
