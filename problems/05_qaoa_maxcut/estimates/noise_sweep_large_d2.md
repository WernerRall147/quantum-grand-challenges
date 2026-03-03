# QAOA Noise Sweep (large, depth=2)

Readout-noise proxy: each bit in each trial's best assignment is flipped independently with probability `p`.
Source quantum report: `quantum_baseline_large_d2.json`

| Noise p | Noisy Mean +/- 95% CI | Mean Gap To Optimum | Retention vs Optimum |
|---:|---:|---:|---:|
| 0.000 | 7.3000 +/- 0.0000 | 0.0000 | 100.0% |
| 0.010 | 7.1882 +/- 0.0160 | 0.1118 | 98.5% |
| 0.020 | 7.0017 +/- 0.0303 | 0.2983 | 95.9% |
| 0.050 | 6.5652 +/- 0.0730 | 0.7348 | 89.9% |
| 0.100 | 5.8714 +/- 0.0312 | 1.4286 | 80.4% |
