# Problem 13 · Quantum-Accelerated Climate Modeling

## Overview

This archived challenge has two separate parts:

1. `python/` contains a classical finite-difference energy-balance climate baseline.
2. `qsharp/` contains a corrected 2x2 HHL toy model for the diffusion matrix `[[2,-1],[-1,2]]` with right-hand side `[1,0]`.

The Q# toy is not the same physical model as the Python energy-balance baseline. It is a minimal two-point diffusion/Laplacian linear system chosen because its eigenvalues 1 and 3 are exactly represented by a 3-bit HHL clock with `t = 2 pi / 8`.

## Correction (2026-09-26)

Earlier text described this problem as an HHL exponential core. The old Q# code did not implement HHL: it applied fixed `Rz(2t)` and `Rx(t)` rotations with no diffusion matrix, used nonstandard inverse-QFT angles, did not uncompute the clock, and the hardware kernel hard-coded `Ry(1.2)`. The replacement implements exact controlled `exp(i A t 2^k)`, big-endian QPE, clock-value controlled inversion with `C = 1`, inverse QPE, and `[ancilla, system]` measurement for post-selection.

## Verified HHL toy numbers

For `A = [[2,-1],[-1,2]]` and `b = [1,0]`:

```text
A^-1 b = [2/3, 1/3]
normalized |A^-1 b|^2 = [0.8, 0.2]
```

The corrected 3-bit circuit is exact for this instance.

| Quantity | Value |
|---|---:|
| Ancilla success probability | 0.5555555556 |
| Post-selected system distribution | [0.8, 0.2] |
| Fidelity with normalized classical solution | 1.0 |
| Joint `[ancilla, system]` distribution | (0,0): 0.2222222222; (0,1): 0.2222222222; (1,0): 0.4444444444; (1,1): 0.1111111111 |

## Directory layout

```text
13_climate_modeling/
├── ARCHIVED.md
├── Makefile
├── README.md
├── circuits/
│   └── circuit.txt
├── estimates/
│   ├── backend_assumptions.md
│   ├── estimator_profile_summary.md
│   └── latest_qubit_gate_ns_e3.json
├── instances/
│   ├── small.yaml
│   ├── medium.yaml
│   └── large.yaml
├── plots/
│   ├── final_profiles.png
│   └── mean_convergence.png
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

The tree lists representative source and report files. Additional archived generated files may exist under `estimates/` and Q# build folders.

## Quick start

```powershell
cd problems\archived\13_climate_modeling
python python\classical_baseline.py
python python\analyze.py
make run
```

A direct QDK smoke test is:

```powershell
$env:PYTHONIOENCODING='utf-8'
python -c "from qdk import qsharp; qsharp.init(project_root='problems/archived/13_climate_modeling/qsharp'); print(qsharp.eval('Main.RunHHLClimate(3, 128)'))"
```

## Estimates and archived artifacts

The `estimates/latest_*.json` files are mock artifacts from the previous pipeline. They are superseded and must not be read as estimates of the corrected HHL circuit, whose estimate (regenerated 2026-09-26) is in `circuits/estimate.json`: 58,903 physical qubits, 23 logical qubits and 40 T gates.

## Scope and caveats

The Q# circuit demonstrates the linear-algebra core on a 2x2 diffusion matrix only. It does not model radiative forcing, nonlinear feedback, multi-layer oceans or the full finite-difference baseline in `python/`. HHL's exponential speedup requires efficient state preparation, sparse well-conditioned matrices, and readout of expectation values rather than a full classical solution vector. See Harrow, Hassidim and Lloyd, arXiv:0811.3171; Aaronson, Nature Physics 11, 291 (2015); and Tang, arXiv:1807.04271.

## Objective maturity gate

- Current gate: Stage B with a corrected toy HHL circuit and a separate classical climate baseline.
- Next gate target: Stage C only after the quantum and classical systems are aligned or the comparison is explicitly scoped as a toy linear-system comparison.

Stage C exit criteria remain:

- Execute a non-placeholder quantum workflow tied to the stated objective.
- Report uncertainty-bounded comparisons between classical and quantum outputs.
- Document transpilation, connectivity and backend assumptions.
- Add calibration and noise-sensitivity evidence for reported quantum metrics.

## DiVincenzo Readiness (Stage C/D Overlay)

| Criterion | Status | Evidence / Notes |
|---|---|---|
| Scalable qubit system | partial | The 2x2 diffusion instance is estimated at 58,903 physical qubits and 23 logical qubits (`circuits/estimate.json`); larger grids are not implemented. |
| Initialization | partial | The right-hand side is loaded with one Ry rotation; a discretized PDE state of N points costs O(N) gates to load in general. |
| Coherence vs gate time | not-yet | No backend-calibrated coherence evidence exists for the corrected circuit. |
| Universal gate set | met | Exact controlled exp(iAt), phase estimation, the controlled Ry inversion and inverse phase estimation are implemented and checked against exact simulation (`tooling/test_hhl_kernel.py`). |
| Qubit-specific measurement | partial | The hardware kernel returns the ancilla and the system qubit so shots can be post-selected; hardware readout characterization is pending. |

## Advantage Claim Contract

- **Claim category (current)**: `theoretical`.
- **Problem class and regime**: The 2x2 discretized diffusion matrix [[2,-1],[-1,2]] solved by textbook HHL with a 3-bit clock; its eigenvalues 1 and 3 are exactly representable, so the post-selected output equals |A^-1 b|^2.
- **Fair baseline**: A direct 2x2 solve, exact and instantaneous; the energy-balance model in `python/` simulates a different system and is not a comparator for the Q# circuit.
- **Quantum resource scaling claim**: HHL runs in time polylogarithmic in N for sparse, well-conditioned A, given efficient state preparation and when only expectation values of x are needed (Harrow, Hassidim and Lloyd, arXiv:0811.3171). None of these conditions is demonstrated here, and discretized diffusion operators have condition numbers that grow with the grid.
- **Data-loading and I/O assumptions**: Loading the initial state and reading out a full solution each cost O(N) for classical data (Aaronson, Nature Physics 11, 291, 2015).
- **Noise/error model assumptions**: Noiseless simulation; the resource estimate assumes a surface code at a 10^-3 physical error rate.
- **Confidence/uncertainty method**: State-vector comparison with an independent model of the circuit to 1e-9, and sampled outputs within a total-variation tolerance.
- **Residual risks**: State preparation, readout, the condition number and the missing climate physics dominate.
