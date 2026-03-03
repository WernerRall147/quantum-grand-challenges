# QAOA Noise Sweep (small, depth=3)

Readout-noise proxy: each bit in each trial's best assignment is flipped independently with probability `p`.
Source quantum report: `quantum_baseline_small_d3.json`

| Noise p | Noisy Mean +/- 95% CI | Mean Gap To Optimum | Retention vs Optimum |
|---:|---:|---:|---:|
| 0.000 | 2.2000 +/- 0.0000 | 0.0000 | 100.0% |
| 0.010 | 2.1766 +/- 0.0073 | 0.0234 | 98.9% |
| 0.020 | 2.1482 +/- 0.0041 | 0.0518 | 97.6% |
| 0.050 | 2.0754 +/- 0.0253 | 0.1246 | 94.3% |
| 0.100 | 1.9646 +/- 0.0229 | 0.2354 | 89.3% |
