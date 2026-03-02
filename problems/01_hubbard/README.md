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

# Dedicated CLI modes
dotnet run --project qsharp/Hubbard.csproj -- analysis            # original report
dotnet run --project qsharp/Hubbard.csproj -- energy 1.0 4.0 0.785398 1.570796 0.392699 1024  # energy estimate
```

## 📈 Current Results

The analytical baseline computes the singlet and triplet energies of the two-site
Hubbard model across a small parameter sweep. The classical and Q# implementations
share the same closed-form expressions, ensuring parity between the two workflows.

Generated artefacts:

- `estimates/classical_baseline.json`: Numerical data for ground and excited states.
- `plots/gaps.png`: Charge and spin gap trends vs interaction strength.

## Objective Maturity Gate

- **Current gate**: **Stage B complete** (classical baseline validated and Q# analytical scaffold builds/runs under .NET 6).
- **Next gate target**: **Stage C** (hardware-aware validation with uncertainty-bounded comparisons for quantum kernels).

Stage C exit criteria for this problem:

- Replace analytical Q# placeholder with at least one executable quantum kernel path (for example VQE or phase-estimation component).
- Report uncertainty-bounded comparisons between classical and quantum outputs on `small` and `medium` instances.
- Document transpilation and connectivity assumptions used for hardware-aware or estimator-backed runs.
- Include calibration or validation artifacts that quantify drift/sensitivity of reported quantum metrics.

## Advantage Claim Contract

- **Claim category (current)**: `theoretical`.
- **Problem class and regime**: Two-site half-filled Hubbard baseline with parameter sweeps in `instances/`.
- **Fair baseline**: Closed-form exact diagonalization style reference in `python/classical_baseline.py`.
- **Quantum resource scaling claim**: No demonstrated speedup claim yet; current Q# path is analytical parity scaffolding.
- **Data-loading and I/O assumptions**: Small fixed-size Hamiltonian instances; no large-scale state-preparation pipeline yet.
- **Noise/error model assumptions**: Not yet characterized for a physical backend because quantum kernel is pending.
- **Confidence/uncertainty method**: Classical outputs deterministic; quantum uncertainty reporting to be added at Stage C.
- **Residual risks**: Placeholder algorithm may not preserve performance once variational or phase-estimation circuits are introduced.

## 🧭 Roadmap

- [ ] Replace analytical expressions with variational or phase-estimation circuits.
- [ ] Expand classical baselines to include finite-temperature observables.
- [ ] Integrate Azure Quantum Resource Estimator once quantum kernels are implemented.

Contributions and experiments welcome!
