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
	$(PYTHON) -c "import qsharp; qsharp.init(project_root='qsharp'); print('Q# compilation OK')"

run: build
	$(PYTHON) -c "import qsharp; qsharp.init(project_root='qsharp'); qsharp.run('Main.RunTwoSiteHubbardAnalysis()', shots=1)"

estimate: build
	@echo "Running resource estimation for 01_hubbard..."
	$(PYTHON) ../../tooling/estimator/run_estimation.py --all --problem 01_hubbard --targets surface_code_generic_v1,qubit_gate_ns_e3 --mock

clean:
	rm -rf qsharp/bin qsharp/obj
	rm -f estimates/*.json
	rm -f plots/*.png
