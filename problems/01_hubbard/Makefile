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

estimate:
	@echo "Resource estimation workflow not yet implemented for 01_hubbard"

clean:
	dotnet clean qsharp/Hubbard.csproj --configuration Release || true
	rm -f estimates/*.json
	rm -f plots/*.png
