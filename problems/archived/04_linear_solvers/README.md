# 04. Quantum Linear Solvers

This archived challenge now contains a checked textbook HHL circuit for the 2x2 symmetric system

```text
A = [[4, -1], [-1, 3]]
b = [15, 10]
```

The classical solution is x = [5, 5], so the normalized solution distribution is [0.5, 0.5]. The Q# circuit keeps the existing `Main.HHLSolve2x2([[4.0, -1.0], [-1.0, 3.0]], [15.0, 10.0], bits)` entry shape. It returns one system-qubit sample after post-selecting the ancilla on `One`. `Main.HHLJointSample2x2` and `HHLKernel()` return `[ancilla, system]` so callers can post-select directly.

## Correction (2026-09-27)

Earlier text and code said this problem implemented HHL. It did not. The old Hamiltonian simulation used first-order `Rz` and `Rx` steps instead of exact controlled `exp(i A t 2^k)`, the inversion used per-bit angles instead of `2 asin(C/lambda)`, and the hardware kernel returned only the ancilla. For this matrix the old circuit produced about `P(system = 1) = 0.309`, while the true normalized `A^-1 b` distribution is `[0.5, 0.5]`. The replacement implements exact controlled evolution for real 2x2 Hermitian matrices, big-endian QPE, clock-value controlled inversion with `C = 1`, inverse QPE, and explicit ancilla/system measurement.

## Verified numbers

For the 3-bit clock used by `tooling/estimator_config.py` and `HHLKernel()`:

| Quantity | Value |
|---|---:|
| Ancilla success probability | 0.2034890696 |
| Post-selected system distribution | [0.47915502, 0.52084498] |
| Fidelity with normalized classical solution [0.5, 0.5] | 0.9995652979 |
| Joint `[ancilla, system]` distribution | (0,0): 0.5708907296; (0,1): 0.2256202008; (1,0): 0.0975028096; (1,1): 0.1059862600 |

For the 4-bit calibration entry in `tooling/generate_calibration_ensemble.py`:

| Quantity | Value |
|---|---:|
| Ancilla success probability | 0.1977430312 |
| Post-selected system distribution | [0.47467748, 0.52532252] |
| Fidelity with normalized classical solution [0.5, 0.5] | 0.9993583582 |

The fidelity is high, but not exactly one, because the eigenvalues `(7 +/- sqrt(5)) / 2` are not integers and are only approximated by the finite clock.

## How to run

```powershell
cd problems\archived\04_linear_solvers
make classical
make analyze
make run
```

A direct QDK smoke test is:

```powershell
$env:PYTHONIOENCODING='utf-8'
python -c "from qdk import qsharp; qsharp.init(project_root='problems/archived/04_linear_solvers/qsharp'); print(qsharp.run('Main.HHLSolve2x2([[4.0, -1.0], [-1.0, 3.0]], [15.0, 10.0], 3)', shots=10))"
```

## Files

- `qsharp/src/Main.qs`: Q# implementation and demo entry point.
- `qsharp/HardwareKernel.qs`: standalone Azure-style kernel returning `[ancilla, system]`.
- `python/classical_baseline.py`: dense classical baseline for the YAML instances.
- `python/analyze.py`: plots condition numbers and residuals.
- `instances/small.yaml`, `instances/medium.yaml`, `instances/large.yaml`: problem instances for the classical baseline.
- `estimates/latest_*.json`: mock estimator artifacts from the previous pipeline. They are superseded for algorithm correctness and must not be read as estimates of the corrected HHL circuit.

## Scope and caveats

This is a 2x2 pedagogical HHL instance, not evidence of practical advantage. HHL's exponential speedup requires efficient state preparation, sparse well-conditioned matrices, and a task that needs expectation values of `|x>` rather than a full classical readout. See Harrow, Hassidim and Lloyd, arXiv:0811.3171; Aaronson, Nature Physics 11, 291 (2015); and Tang, arXiv:1807.04271 for the data access and dequantization caveats.

## Objective maturity gate

- Current gate: Stage B with a checked toy HHL circuit and classical baseline.
- Next gate target: Stage C only after resource estimates and backend assumptions are regenerated for the corrected circuit.

Stage C exit criteria remain:

- Execute a non-placeholder quantum workflow tied to the problem objective.
- Report uncertainty-bounded comparisons between classical and quantum outputs on `small` and `medium` instances.
- Document transpilation, connectivity and backend assumptions for reported quantum runs.
- Add calibration and noise-sensitivity evidence for reported quantum metrics.
