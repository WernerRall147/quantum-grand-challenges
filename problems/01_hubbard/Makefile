.PHONY: classical analyze build run estimate clean

PYTHON := python
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

classical:
	cd python && $(PYTHON) classical_baseline.py

analyze: classical
	cd python && $(PYTHON) analyze.py

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
