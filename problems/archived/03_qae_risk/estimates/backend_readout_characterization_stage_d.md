# Backend Readout Characterization - Stage D (03_qae_risk)

Generated: 2026-06-10T10:02:22Z

## Summary

- Success rate: 1.000 (95% CI [0.342, 1.000])
- Metrics-availability rate: 0.500 (95% CI [0.095, 0.905])
- Total runs: 2

## Per-Target Reliability

| Target | Runs | Success Rate | Success CI95 | Metrics Availability | Metrics CI95 | Avg Runtime (s) | Avg Queue (s) | Avg Duration (s) |
|---|---:|---:|---|---:|---|---:|---:|---:|
| quantinuum.sim.h2-1sc | 1 | 1.000 | [0.207, 1.000] | 0.000 | [0.000, 0.793] | 0.000000 | 0.000000 | 0.000000 |
| rigetti.sim.qvm | 1 | 1.000 | [0.207, 1.000] | 1.000 | [0.207, 1.000] | 1.305996 | 3.824282 | 5.130278 |

## Notes

- This artifact is derived from measured Azure run history entries for this problem.
- Characterization is execution/readout proxy evidence, not full hardware tomography.
- Use this to bound backend reliability assumptions in Stage D claim confidence mapping.
