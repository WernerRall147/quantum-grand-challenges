# Quantum Catalysis Challenge Makefile

.PHONY: classical analyze build run estimate clean

classical:
	python python/classical_baseline.py

analyze:
	python python/analyze.py

build:
	cd qsharp && dotnet build --configuration Release

run:
	cd qsharp && dotnet run

estimate:
	@echo "Resource estimation not yet implemented for catalysis."

clean:
	rm -rf estimates/*.json plots/*.png qsharp/bin/ qsharp/obj/
