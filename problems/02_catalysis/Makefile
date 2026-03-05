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
	cd qsharp && dotnet build --configuration Release

run:
	cd qsharp && dotnet run

estimate:
	@echo "Resource estimation not yet implemented for catalysis."

clean:
	rm -rf estimates/*.json plots/*.png qsharp/bin/ qsharp/obj/
