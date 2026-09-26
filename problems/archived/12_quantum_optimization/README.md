# Problem 12 · Toy QAOA Scheduling Penalty

## Overview

This archived problem contains two separate artifacts: a classical greedy weighted tardiness scheduler and a Q# depth-1 QAOA toy QUBO. The Q# model is a four-job, two-machine same-side penalty Hamiltonian. It is not a full scheduling solver and it does not encode due dates, processing times, or weighted tardiness.

**Correction (2026-09-26)**: Earlier text implied a broad quantum-assisted combinatorial optimization scaffold and described the Q# path as future work. The verified Q# path is already executable, but it is only the toy same-machine penalty QUBO in `qsharp/src/Main.qs`. The hardware kernel now uses the same four-variable toy model and optimized p=1 angles as the estimator entry.

## Verified toy model

- Q# source: `qsharp/src/Main.qs`.
- Hardware kernel: `qsharp/HardwareKernel.qs`.
- Cost function: sum `w_ij` when two jobs are assigned to the same machine.
- Weights: `1.0`, `0.5`, `0.2`, `1.2`, `0.8`, and `0.6` across all six job pairs.
- QAOA convention: the same-side penalty layer uses `Rz(2 gamma w_ij)`, so `gamma_standard = 2 gamma` for `exp(-i gamma_standard C)`, up to a global phase.
- Exact brute-force optimum of the toy QUBO: `1.3`.
- Exact state-vector expectation at the optimized p=1 angles `gamma=0.3141592653589793`, `beta=1.2566370614359172`: `1.546699034716197`.
- Approximation ratio for this minimization toy objective: `1.1898`.
- There is no proven QAOA speedup claimed for this problem.

## Classical baseline

`python/classical_baseline.py` implements greedy weighted tardiness. That is an honest heuristic scheduling baseline for the YAML instances, but it is not the same objective as the Q# toy QUBO.

## Directory Layout

```text
12_quantum_optimization/
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
cd problems\archived\12_quantum_optimization
python python\classical_baseline.py
python python\analyze.py
python -c "from qdk import qsharp; qsharp.init(project_root='qsharp'); print(qsharp.run('Main.RunSchedulingOptimization()', 1))"
```

## Objective Maturity Gate

- **Current gate**: **Stage B complete** for a toy QUBO scaffold only.
- **Next gate target**: none scheduled. Any future scheduling claim must compare the same objective on both classical and quantum sides.

## DiVincenzo Readiness (Stage C/D Overlay)

| Criterion | Status | Evidence / Notes |
|---|---|---|
| Scalable qubit system | partial | Four toy QUBO variables are implemented; no realistic scheduling encoding exists. |
| Initialization | partial | Uniform-superposition QAOA initialization is implemented for the toy model. |
| Coherence vs gate time | not-yet | Backend-calibrated coherence-vs-depth evidence is not current after kernel alignment. |
| Universal gate set | partial | The Q# and QASM circuits use standard one- and two-qubit gates. |
| Qubit-specific measurement | partial | Computational-basis measurement is implemented; hardware readout characterization is stale. |

## Advantage Claim Contract

- **Claim category (current)**: `theoretical`.
- **Fair baseline**: greedy weighted tardiness for YAML instances, plus exact enumeration for the four-bit Q# toy model in tests.
- **Residual risks**: the classical heuristic and Q# toy objective are different models.
