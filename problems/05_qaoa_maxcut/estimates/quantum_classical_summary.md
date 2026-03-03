# QAOA Quantum vs Classical Summary

This summary is auto-generated from `estimates/classical_baseline.json` and `estimates/quantum_baseline_*_d*.json`.

| Instance | Classical Optimum | Quantum Refined Mean +/- 95% CI | Mean Gap | Depth | Trials | Source |
|---|---:|---:|---:|---:|---:|---|
| large | 7.3000 | 4.1034 +/- 0.3249 | 3.1966 | 2 | 4 | `quantum_baseline_large_d2.json` |
| medium | 4.0000 | 2.8893 +/- 0.2890 | 1.1107 | 2 | 4 | `quantum_baseline_medium_d2.json` |
| small | 2.2000 | 1.9182 +/- 0.0323 | 0.2818 | 3 | 4 | `quantum_baseline_small_d3.json` |

## Depth Sweep Dashboard

| Instance | Depths | Trend | Best Refined Mean | Best Depth | Best Mean Gap |
|---|---|---|---:|---:|---:|
| large | 1, 2 | improving | 4.1034 | 2 | 3.1966 |
| medium | 1, 2 | improving | 2.8893 | 2 | 1.1107 |
| small | 1, 2, 3 | improving | 1.9182 | 3 | 0.2818 |

## Noise Sweep Dashboard

| Instance/Depth | Noise Levels | Low-Noise Mean (p=min) | High-Noise Mean (p=max) | Degradation |
|---|---|---:|---:|---:|
| large::d2 | 0.000, 0.010, 0.020, 0.050, 0.100 | 7.3000 | 5.8714 | 1.4286 |
| medium::d2 | 0.000, 0.010, 0.020, 0.050, 0.100 | 4.0000 | 3.3325 | 0.6675 |
| small::d3 | 0.000, 0.010, 0.020, 0.050, 0.100 | 2.2000 | 1.9646 | 0.2354 |
