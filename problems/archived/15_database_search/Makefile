# Database Search (Problem 15) Makefile

PROBLEM_DIR := $(CURDIR)
PYTHON ?= python3
ifeq ($(OS),Windows_NT)
PYTHON := $(CURDIR)/../../.venv/Scripts/python.exe
endif

.PHONY: help build run classical analyze stage-d test estimate sweep check-env clean

help:
	@echo "Database Search - Available targets:"
	@echo "  make build       Build the Q# prototype"
	@echo "  make run         Execute the Q# placeholder entry point"
	@echo "  make classical   Run the exhaustive search baseline"
	@echo "  make analyze     Generate query complexity plots"
	@echo "  make stage-d     Generate Stage D uncertainty/overhead/sensitivity artifacts"
	@echo "  make test        Run deterministic baseline checks"
	@echo "  make estimate    Placeholder for resource estimation"
	@echo "  make clean       Remove generated artifacts"

build:
	@echo "Building Q# project..."
	$(PYTHON) -c "import qsharp; qsharp.init(project_root='qsharp'); print('Q# compilation OK')"

run: build
	@echo "Running quantum placeholder..."
	$(PYTHON) -c "import qsharp; qsharp.init(project_root='qsharp'); qsharp.run('Main.RunGroverDemonstration()', shots=1)"

classical:
	@echo "Evaluating classical search baseline..."
	$(PYTHON) python/classical_baseline.py

analyze:
	@echo "Generating database search plots..."
	$(PYTHON) python/analyze.py

stage-d: classical
	@echo "Generating Stage D reports..."
	$(PYTHON) python/stage_d_reports.py

test: classical
	@echo "Running deterministic baseline checks..."
	$(PYTHON) python/test_baseline.py

ESTIMATOR := $(PYTHON) ../../tooling/estimator/run_estimation.py

estimate: build
	@echo "Running resource estimation for 15_database_search..."
	$(ESTIMATOR) --all --problem 15_database_search --targets surface_code_generic_v1,qubit_gate_ns_e3 --mock

sweep:
	@echo "Parameter sweep tooling not yet implemented."

check-env:
	@echo "Development environment check:"
	@echo "  Python: $$(python --version 2>/dev/null || echo 'Not found')"
	@echo "  Q# build: $$($(PYTHON) -c 'import qsharp; qsharp.init(project_root=\"qsharp\"); print(\"Available\")' 2>/dev/null || echo 'Unavailable')"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf qsharp/bin qsharp/obj
	rm -rf python/__pycache__
	rm -f estimates/*.json
	rm -f plots/*.png
	@echo "Clean complete."
