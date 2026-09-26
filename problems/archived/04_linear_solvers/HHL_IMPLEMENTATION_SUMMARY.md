# HHL Implementation Summary

## Correction status

This file describes the corrected circuit as of 2026-09-27. Earlier versions described a circuit that was not HHL: it used first-order `Rz` and `Rx` evolution, applied per-bit ancilla rotations, and ignored post-selection when reporting the system output.

## Instance

```text
A = [[4, -1], [-1, 3]]
b = [15, 10]
x = A^-1 b = [5, 5]
```

The eigenvalues are `(7 +/- sqrt(5)) / 2`, approximately 4.6180339887 and 2.3819660113. They are not exactly representable with a 3-bit or 4-bit phase clock when the clock value is interpreted as the eigenvalue.

## Circuit convention

- The unitary in QPE is `U = exp(i A t)`.
- For `m` clock bits, `t = 2 pi / 2^m`, so a clock value `y` estimates `lambda` as `y`.
- The clock is big-endian. `clock[0]` is the most significant bit.
- A real symmetric 2x2 matrix is decomposed as `A = c I + z Z + x X`.
- Controlled evolution applies the control phase `exp(i c t)` and the exact axis rotation for `z Z + x X`. No Trotter approximation is used.
- Eigenvalue inversion applies a multi-controlled `Ry(2 asin(C / y))` for each nonzero clock value `y`, with `C = 1`.
- The circuit runs inverse QPE and then measures `[ancilla, system]`. `HHLSolve2x2` repeats until the ancilla is `One` and returns the post-selected system bit.

## Verified behavior

`tooling/test_hhl_kernel.py` checks the Q# state vector against an independent NumPy/SciPy construction of the same HHL circuit and samples both the project entry and `qsharp/HardwareKernel.qs`.

For the 3-bit clock:

| Quantity | Value |
|---|---:|
| Ancilla success probability | 0.2034890696 |
| Post-selected distribution | [0.47915502, 0.52084498] |
| Fidelity with `[0.5, 0.5]` | 0.9995652979 |

For the 4-bit calibration clock:

| Quantity | Value |
|---|---:|
| Ancilla success probability | 0.1977430312 |
| Post-selected distribution | [0.47467748, 0.52532252] |
| Fidelity with `[0.5, 0.5]` | 0.9993583582 |

The corrected hardware kernel returns the joint distribution, not just the ancilla:

```text
(ancilla, system) = (0,0): 0.5708907296
(ancilla, system) = (0,1): 0.2256202008
(ancilla, system) = (1,0): 0.0975028096
(ancilla, system) = (1,1): 0.1059862600
```

## Resource estimates

The `estimates/latest_*.json` files and the estimator summaries in this folder are mock artifacts from the previous pipeline. They are superseded for the corrected circuit. Regenerate estimates before using any qubit, T-count or runtime number in analysis.

## Advantage boundary

The toy problem is smaller than the overhead needed to run HHL. It is useful for testing the algorithmic steps only. A real advantage claim would need efficient state preparation, sparse-access or block-encoding oracles, a well-conditioned matrix family, and a readout task that avoids reconstructing all entries of `x`. These caveats are part of the original HHL setting in arXiv:0811.3171 and are emphasized by Aaronson, Nature Physics 11, 291 (2015). Low-rank recommendation-style inputs also have classical dequantizations, starting with Tang, arXiv:1807.04271.
