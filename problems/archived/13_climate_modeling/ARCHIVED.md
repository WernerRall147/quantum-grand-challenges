# ARCHIVED Climate Modeling

**Status**: Archived (April 2026), corrected 2026-09-26.

## Archival reason

The classical climate baseline in `python/` is a finite-difference energy-balance model. The corrected Q# code is a separate 2x2 diffusion-matrix HHL toy. It is useful for checking the HHL linear-solver steps, but it is not a climate model and does not establish climate-simulation advantage.

The old Q# kernel was not HHL. It used fixed rotations, no diffusion matrix in the evolution, no clock uncomputation, and a hard-coded hardware-kernel angle. The current kernel implements exact 2x2 HHL for `[[2,-1],[-1,2]]`.

> Code in this directory remains for pedagogical reference.

## References

- Harrow, Hassidim and Lloyd, arXiv:0811.3171.
- Aaronson, Nature Physics 11, 291 (2015).
- Tang, arXiv:1807.04271.
