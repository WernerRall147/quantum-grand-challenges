# ARCHIVED Quantum Linear Solvers (HHL)

**Status**: Archived (April 2026), corrected 2026-09-26.

## Archival reason

This problem is a pedagogical 2x2 HHL demonstration. HHL can give asymptotic improvements for suitable sparse, well-conditioned linear systems, but only when state preparation and readout do not erase the gain. Full solution-vector readout is a classical-size output.

The corrected Q# code now implements the textbook 2x2 HHL steps for the small matrix in this folder. The archived estimator artifacts are mock data and are not estimates of the corrected circuit.

> Code in this directory remains for pedagogical reference.

## References

- Harrow, Hassidim and Lloyd, arXiv:0811.3171.
- Aaronson, Nature Physics 11, 291 (2015).
- Tang, arXiv:1807.04271.
