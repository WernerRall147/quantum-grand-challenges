# QAOA Noise Sweep (large, depth=2)

Readout-noise proxy: each bit in each trial's best assignment is flipped independently with probability `p`.
Source quantum report: `quantum_baseline_large_d2.json`

| Noise p | Noisy Mean +/- 95% CI | Mean Gap To Optimum | Retention vs Optimum |
|---:|---:|---:|---:|
| 0.000 | 7.3000 +/- 0.0000 | 0.0000 | 100.0% |
| 0.010 | 7.1690 +/- 0.0293 | 0.1310 | 98.2% |
| 0.020 | 7.0158 +/- 0.0391 | 0.2842 | 96.1% |
| 0.050 | 6.5715 +/- 0.0259 | 0.7285 | 90.0% |
| 0.100 | 5.9883 +/- 0.0818 | 1.3117 | 82.0% |
