# ARCHIVED  High-Frequency Trading

**Status**: Archived (April 2026)

## Archival Reason

The planned approach, amplitude estimation of a loss probability, has the same limitation as QAE (problem 03): at most a quadratic speedup, which error-correction and data-loading costs outweigh. The code never implemented it: `qsharp/src/Main.qs` samples the marked states directly (see the correction in `README.md`).

> Code in this directory remains for **pedagogical reference**.

## Reference

Analysis follows Dr. Matthias Troyer’s “Building the Modern Quantum Architecture” framework (2025–2026).
