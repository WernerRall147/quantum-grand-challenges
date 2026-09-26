# Backend Assumptions - 13_climate_modeling

## Correction note

Updated 2026-09-26. The Q# circuit now implements exact 2x2 HHL for the diffusion matrix `[[2,-1],[-1,2]]`. Earlier notes that described a generic HHL diffusion kernel are superseded.

## Circuit characteristics

- Algorithm: textbook HHL for a two-point diffusion/Laplacian matrix.
- Clock: 3 bits, big-endian.
- Evolution convention: `U = exp(i A t)` with `t = 2 pi / 8`.
- Hardware kernel output: `[ancilla, system]`, so callers can post-select on `ancilla = One`.
- Gate families: `H`, `Ry`, `Rz`, `R1`, controlled rotations, `SWAP` and measurement.

## Validation boundary

- Simulator validation is pinned by `tooling/test_hhl_kernel.py`.
- The Python climate baseline models a different finite-difference energy-balance system.
- The existing `latest_*.json` files are mock estimator outputs from the previous pipeline. They are not estimates of the corrected circuit.
- Hardware noise characterization is pending.
