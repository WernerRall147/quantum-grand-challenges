# 04. Quantum Linear Solvers

This archived challenge now contains a checked textbook HHL circuit for the 2x2 symmetric system

```text
A = [[4, -1], [-1, 3]]
b = [15, 10]
```

The classical solution is x = [5, 5], so the normalized solution distribution is [0.5, 0.5]. The Q# circuit keeps the existing `Main.HHLSolve2x2([[4.0, -1.0], [-1.0, 3.0]], [15.0, 10.0], bits)` entry shape. It returns one system-qubit sample after post-selecting the ancilla on `One`. `Main.HHLJointSample2x2` and `HHLKernel()` return `[ancilla, system]` so callers can post-select directly.

## Correction (2026-09-26)

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
| Ancilla success probability | 0.1507474826 |
| Post-selected system distribution | [0.50403167, 0.49596833] |
| Fidelity with normalized classical solution [0.5, 0.5] | 0.9999837453 |

The fidelity is below one because the eigenvalues `(7 +/- sqrt(5)) / 2` fall between clock values. Each controlled-evolution step is `exp(i A 2 pi/8)` whatever the clock size, so every added clock bit halves the eigenvalue resolution and the output converges on the solution (fidelity 0.99957, 0.99998 and 0.99999 with 3, 4 and 5 bits). A step that shrank as `2 pi / 2^m` would fix the resolution at 1, and extra bits would then move the output slightly away from the solution.

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
- Next gate target: Stage C, which needs calibration and noise evidence for the corrected circuit; its resource estimate was regenerated on 2026-09-26.

Stage C exit criteria remain:

- Execute a non-placeholder quantum workflow tied to the problem objective.
- Report uncertainty-bounded comparisons between classical and quantum outputs on `small` and `medium` instances.
- Document transpilation, connectivity and backend assumptions for reported quantum runs.
- Add calibration and noise-sensitivity evidence for reported quantum metrics.

## DiVincenzo Readiness (Stage C/D Overlay)

| Criterion | Status | Evidence / Notes |
|---|---|---|
| Scalable qubit system | partial | The 2x2 instance is estimated at 86,567 physical qubits and 23 logical qubits (`circuits/estimate.json`); larger systems are not implemented. |
| Initialization | partial | The right-hand side is loaded with one Ry rotation; loading an N-dimensional classical vector costs O(N) gates in general. |
| Coherence vs gate time | not-yet | No backend-calibrated coherence evidence exists for the corrected circuit. |
| Universal gate set | met | Exact controlled exp(iAt), phase estimation, the controlled Ry inversion and inverse phase estimation are implemented and checked against exact simulation (`tooling/test_hhl_kernel.py`). |
| Qubit-specific measurement | partial | The hardware kernel returns the ancilla and the system qubit so shots can be post-selected; hardware readout characterization is pending. |

## Advantage Claim Contract

- **Claim category (current)**: `theoretical`.
- **Problem class and regime**: A 2x2 symmetric positive-definite system solved by textbook HHL with a 3-bit clock (4-bit in calibration).
- **Fair baseline**: The direct solution in `python/`, exact and instantaneous at this size; conjugate gradient is the scalable classical comparator for sparse systems.
- **Quantum resource scaling claim**: HHL runs in time polylogarithmic in N for sparse, well-conditioned A, given efficient state preparation and when only expectation values of x are needed (Harrow, Hassidim and Lloyd, arXiv:0811.3171). None of these conditions is demonstrated here.
- **Data-loading and I/O assumptions**: Loading b and reading out x each cost O(N) for classical data (Aaronson, Nature Physics 11, 291, 2015), which removes the advantage for generic classical inputs; low-rank inputs are dequantized (Tang, arXiv:1807.04271).
- **Noise/error model assumptions**: Noiseless simulation; the resource estimate assumes a surface code at a 10^-3 physical error rate.
- **Confidence/uncertainty method**: State-vector comparison with an independent model of the circuit to 1e-9, and sampled outputs within five standard errors or a total-variation tolerance.
- **Residual risks**: State preparation, readout and the condition number dominate at any useful size.
