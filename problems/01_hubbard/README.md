# 01 · Hubbard Model

> Exploring strongly correlated electrons in a minimal two-site Hubbard model. This
> serves as the starting point for scaling to larger lattices and more realistic
> Hamiltonians.

## 🎯 Objectives

- Establish a reproducible **classical baseline** for the half-filled two-site Hubbard model.
- Provide a compiling **Q# analytical benchmark** that mirrors the classical calculation.
- Prepare the scaffolding for future **variational** and **phase estimation** studies on
  larger Hubbard instances.

## 🧱 Project Structure

```
01_hubbard/
├── README.md                 # This document
├── Makefile                  # Convenience targets for the workflows
├── estimates/                # Generated estimation artifacts
├── instances/                # Parameter grids (small/medium/large)
├── plots/                    # Generated visualisations
├── python/
│   ├── classical_baseline.py # Classical analytical baseline
│   └── analyze.py            # Plot charge/spin gaps
└── qsharp/
    ├── Program.qs            # Analytical Q# baseline
    └── Hubbard.csproj        # Q# project definition
```

## 🚀 Quickstart

From the repository root:

```bash
cd problems/01_hubbard

# Classical workflow
make classical    # writes estimates/classical_baseline.json
make analyze      # produces plots/gaps.png

# Quantum analytical baseline (requires .NET 6)
make build
make run
```

## 📈 Current Results

The analytical baseline computes the singlet and triplet energies of the two-site
Hubbard model across a small parameter sweep. The classical and Q# implementations
share the same closed-form expressions, ensuring parity between the two workflows.

Generated artefacts:

- `estimates/classical_baseline.json`: Numerical data for ground and excited states.
- `plots/gaps.png`: Charge and spin gap trends vs interaction strength.

## 🧭 Roadmap

- [ ] Replace analytical expressions with variational or phase-estimation circuits.
- [ ] Expand classical baselines to include finite-temperature observables.
- [ ] Integrate Azure Quantum Resource Estimator once quantum kernels are implemented.

Contributions and experiments welcome!
