# ARCHIVED  QAOA MaxCut

**Status**: Archived (April 2026)

## Archival Reason

QAOA has no proven speedup, and no constant-depth QAOA is known to beat the Goemans-Williamson 0.878 approximation; on certain MaxCut instances Goemans-Williamson outperforms QAOA at any constant depth (Bravyi et al., arXiv:1910.08980). For bounded-degree graphs its constant-depth MaxCut expectation values can be computed classically (each edge depends only on a bounded neighbourhood), although sampling its output distribution can be classically hard even at depth one (Farhi and Harrow, arXiv:1602.07674).

> Code in this directory remains for **pedagogical reference**.

## Reference

Analysis follows Dr. Matthias Troyer’s “Building the Modern Quantum Architecture” framework (2025–2026).
