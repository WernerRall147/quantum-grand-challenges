.PHONY: classical analyze test build run estimate clean

PYTHON ?= python3
ifeq ($(OS),Windows_NT)
PYTHON := $(CURDIR)/../../.venv/Scripts/python.exe
endif
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

classical:
	cd python && $(PYTHON) classical_baseline.py

analyze: classical
	cd python && $(PYTHON) analyze.py

test: classical
	cd python && $(PYTHON) test_baseline.py

build:
	dotnet build qsharp/Hubbard.csproj --configuration Release

run: build
	dotnet run --project qsharp/Hubbard.csproj --configuration Release

estimate: build
	@echo "Running resource estimation for 01_hubbard..."
	$(PYTHON) ../../tooling/estimator/run_estimation.py --all --problem 01_hubbard --targets surface_code_generic_v1,qubit_gate_ns_e3 --mock

clean:
	dotnet clean qsharp/Hubbard.csproj --configuration Release || true
	rm -f estimates/*.json
	rm -f plots/*.png
