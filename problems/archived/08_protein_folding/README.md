# Problem 08 · Toy Ising/QUBO Energy Search

## Overview

This archived Q# program is not a protein-folding implementation. It runs a depth-1 QAOA circuit for a four-variable toy Ising/QUBO energy with pair weights that are stored in a matrix named `contacts`. The code has no protein sequence, lattice walk, or contact-map geometry. It also has no self-avoidance constraint. The protein-folding framing in earlier documentation was therefore false.

**Correction (2026-09-26)**: Earlier text described a protein-folding contact model and future quantum Boltzmann sampling. The verified Q# path builds only a toy Ising/QUBO same-side energy. The hardware kernel now uses the same four-variable toy model and optimized p=1 angles as the estimator entry. Existing website emulator notes predate this alignment.

## Verified toy model

- Q# source: `qsharp/src/Main.qs`.
- Hardware kernel: `qsharp/HardwareKernel.qs`.
- Cost function: sum `w_ij` when two bits are equal, with weights `-1.2`, `-0.3`, `-0.8`, `-0.5`, and `-1.0` on five pairs.
- QAOA convention: the same-side penalty layer uses `Rz(2 gamma w_ij)`, so `gamma_standard = 2 gamma` for `exp(-i gamma_standard C)`, up to a global phase.
- Exact brute-force optimum of the toy QUBO: `-3.8`.
- Exact state-vector expectation at the optimized p=1 angles `gamma=0.47123889803846897`, `beta=1.119192382841364`: `-3.1250872910581253`.
- Approximation ratio for this minimization toy objective: `0.8224` relative to the optimum energy magnitude.
- There is no proven QAOA speedup claimed for this problem.

## Classical baseline

`python/classical_baseline.py` is a heuristic knowledge-based scoring script over YAML sequence/contact records. It is useful as a reproducible data-analysis scaffold, but it is not the same objective as the Q# toy QUBO and is not a standard protein-folding solver.

## Directory Layout

```text
08_protein_folding/
├── ARCHIVED.md
├── README.md
├── estimates/
├── instances/
├── plots/
├── python/
│   ├── analyze.py
│   ├── classical_baseline.py
│   └── test_baseline.py
└── qsharp/
    ├── HardwareKernel.qs
    ├── qsharp.json
    └── src/
        └── Main.qs
```

## Quick Start

```powershell
cd problems\archived\08_protein_folding
python python\classical_baseline.py
python python\analyze.py
python -c "from qdk import qsharp; qsharp.init(project_root='qsharp'); print(qsharp.run('Main.RunProteinFolding()', 1))"
```

## Objective Maturity Gate

- **Current gate**: **Stage B complete** for a toy QUBO scaffold only.
- **Next gate target**: none scheduled. Any future protein-folding claim must implement and test an actual protein model before promotion.

## DiVincenzo Readiness (Stage C/D Overlay)

| Criterion | Status | Evidence / Notes |
|---|---|---|
| Scalable qubit system | partial | Four toy QUBO variables are implemented; no protein-scale encoding exists. |
| Initialization | partial | Uniform-superposition QAOA initialization is implemented for the toy model. |
| Coherence vs gate time | not-yet | Backend-calibrated coherence-vs-depth evidence is not current after kernel alignment. |
| Universal gate set | partial | The Q# and QASM circuits use standard one- and two-qubit gates. |
| Qubit-specific measurement | partial | Computational-basis measurement is implemented; hardware readout characterization is stale. |

## Advantage Claim Contract

- **Claim category (current)**: `theoretical`.
- **Fair baseline**: no fair protein-folding quantum comparison exists in this folder.
- **Residual risks**: the Q# toy objective, classical scoring script, and earlier website emulator records describe different things unless explicitly regenerated from the current kernel.
