# Quantum Catalysis Challenge Makefile

.PHONY: classical analyze test build run estimate clean

PYTHON ?= python3
ifeq ($(OS),Windows_NT)
PYTHON := $(CURDIR)/../../.venv/Scripts/python.exe
endif

classical:
	$(PYTHON) python/classical_baseline.py

analyze:
	$(PYTHON) python/analyze.py

test: classical
	$(PYTHON) python/test_baseline.py

build:
	$(PYTHON) -c "import qsharp; qsharp.init(project_root='qsharp'); print('Q# compilation OK')"

run:
	$(PYTHON) -c "import qsharp; qsharp.init(project_root='qsharp'); qsharp.run('Main.RunCatalysisAnalysis()', shots=1)"

estimate:
	@echo "Resource estimation not yet implemented for catalysis."

clean:
	rm -rf estimates/*.json plots/*.png qsharp/bin/ qsharp/obj/
