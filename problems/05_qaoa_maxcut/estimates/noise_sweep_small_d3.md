# QAOA Noise Sweep (small, depth=3)

Readout-noise proxy: each bit in each trial's best assignment is flipped independently with probability `p`.
Source quantum report: `quantum_baseline_small_d3.json`

| Noise p | Noisy Mean +/- 95% CI | Mean Gap To Optimum | Retention vs Optimum |
|---:|---:|---:|---:|
| 0.000 | 2.2000 +/- 0.0000 | 0.0000 | 100.0% |
| 0.010 | 2.1760 +/- 0.0051 | 0.0240 | 98.9% |
| 0.020 | 2.1411 +/- 0.0122 | 0.0589 | 97.3% |
| 0.050 | 2.0747 +/- 0.0230 | 0.1253 | 94.3% |
| 0.100 | 1.9521 +/- 0.0222 | 0.2479 | 88.7% |
