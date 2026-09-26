# Problem 20 · Toy QAOA Mission-Planning QUBO

## Overview

This archived problem contains a heuristic mission-scoring script and a separate Q# depth-1 QAOA toy QUBO. The Q# model chooses one of two options for each of four mission legs and adds a pairwise penalty when two legs choose the same option. It is not a patched-conic trajectory optimizer.

**Correction (2026-09-27)**: Earlier text blurred the classical patched-conic scoring script with the Q# model, and the hardware kernel used a different three-qubit chain with different biases. The hardware kernel now matches the four-leg model in `Main.RunMissionOptimization` and uses optimized p=1 angles. Existing website emulator results predate this alignment and should be labelled as stale until regenerated.

## Verified toy model

- Q# source: `qsharp/src/Main.qs`.
- Hardware kernel: `qsharp/HardwareKernel.qs`.
- Cost function: four option costs `[[2.5, 1.8], [1.2, 0.8], [3.1, 2.4], [1.5, 1.0]]` plus `0.5` for each equal-option pair.
- Exact brute-force optimum of the toy QUBO: `7.9`.
- Exact state-vector expectation at the optimized p=1 angles `gamma=0.667588438887831`, `beta=1.3940817400304706`: `8.567469059209166`.
- Approximation ratio for this minimization toy objective: `1.0845`.
- There is no proven QAOA speedup claimed for this problem.

## Classical baseline

`python/classical_baseline.py` implements heuristic patched-conic scoring for YAML mission records. It estimates aggregate delta-v, slack, feasibility, and a mission score. It is not the same objective as the Q# toy QUBO.

## Directory Layout

```text
20_space_mission_planning/
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
cd problems\archived\20_space_mission_planning
python python\classical_baseline.py
python python\analyze.py
python -c "from qdk import qsharp; qsharp.init(project_root='qsharp'); print(qsharp.run('Main.RunMissionOptimization()', 1))"
```

## Objective Maturity Gate

- **Current gate**: **Stage B complete** for a toy QUBO scaffold only.
- **Next gate target**: none scheduled. Any future mission-planning claim must compare the same objective on both classical and quantum sides.

## DiVincenzo Readiness (Stage C/D Overlay)

| Criterion | Status | Evidence / Notes |
|---|---|---|
| Scalable qubit system | partial | Four toy QUBO variables are implemented; no realistic trajectory encoding exists. |
| Initialization | partial | Uniform-superposition QAOA initialization is implemented for the toy model. |
| Coherence vs gate time | not-yet | Backend-calibrated coherence-vs-depth evidence is not current after kernel alignment. |
| Universal gate set | partial | The Q# and QASM circuits use standard one- and two-qubit gates. |
| Qubit-specific measurement | partial | Computational-basis measurement is implemented; hardware readout characterization is stale. |

## Advantage Claim Contract

- **Claim category (current)**: `theoretical`.
- **Fair baseline**: heuristic patched-conic scoring for YAML records, plus exact enumeration for the four-bit Q# toy model in tests.
- **Residual risks**: the classical heuristic and Q# toy objective are different models, and shared website emulator records are stale until regenerated.
