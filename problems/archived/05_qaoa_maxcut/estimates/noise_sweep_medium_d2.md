# QAOA Noise Sweep (medium, depth=2)

Readout-noise proxy: each bit in each trial's best assignment is flipped independently with probability `p`.
Source quantum report: `quantum_baseline_medium_d2.json`

| Noise p | Noisy Mean +/- 95% CI | Mean Gap To Optimum | Retention vs Optimum |
|---:|---:|---:|---:|
| 0.000 | 4.0000 +/- 0.0000 | 0.0000 | 100.0% |
| 0.010 | 3.9473 +/- 0.0143 | 0.0527 | 98.7% |
| 0.020 | 3.8590 +/- 0.0219 | 0.1410 | 96.5% |
| 0.050 | 3.6494 +/- 0.0305 | 0.3506 | 91.2% |
| 0.100 | 3.3164 +/- 0.0411 | 0.6836 | 82.9% |
