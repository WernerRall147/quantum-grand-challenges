# QAOA Noise Sweep (medium, depth=2)

Readout-noise proxy: each bit in each trial's best assignment is flipped independently with probability `p`.
Source quantum report: `quantum_baseline_medium_d2.json`

| Noise p | Noisy Mean +/- 95% CI | Mean Gap To Optimum | Retention vs Optimum |
|---:|---:|---:|---:|
| 0.000 | 4.0000 +/- 0.0000 | 0.0000 | 100.0% |
| 0.010 | 3.9434 +/- 0.0160 | 0.0566 | 98.6% |
| 0.020 | 3.8594 +/- 0.0266 | 0.1406 | 96.5% |
| 0.050 | 3.6919 +/- 0.0488 | 0.3081 | 92.3% |
| 0.100 | 3.3325 +/- 0.0594 | 0.6675 | 83.3% |
