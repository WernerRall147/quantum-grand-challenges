# Backend Assumptions - 04_linear_solvers

## Correction note

Updated 2026-09-27. The Q# circuit now uses exact controlled `exp(i A t 2^k)` for a real symmetric 2x2 matrix. Earlier notes that described first-order Trotter `Rz` and `Rx` simulation are superseded.

## Circuit characteristics

- Algorithm: textbook HHL for `A = [[4,-1],[-1,3]]` and `b = [15,10]`.
- Project entry clock: 3 bits.
- Calibration entry clock: 4 bits.
- Hardware kernel output: `[ancilla, system]`, so callers can post-select on `ancilla = One`.
- Gate families: `H`, `Ry`, `Rz`, `R1`, controlled rotations, `SWAP` and measurement.

## Validation boundary

- Simulator validation is pinned by `tooling/test_hhl_kernel.py`.
- The existing `latest_*.json` files are mock estimator outputs from the previous pipeline. They are not estimates of the corrected circuit.
- Hardware noise characterization is pending.

## Transpilation notes

Controlled rotations and QFT phases must be decomposed for a target backend before any hardware claim. Regenerate resource estimates after decomposition rules are selected.
