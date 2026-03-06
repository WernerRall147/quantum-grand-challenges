# Stage D Fairness Review - 03_qae_risk

This report compares available quantum ensemble estimates with classical Monte Carlo baselines.
Rows marked `provisional_projection` are placeholders and must be replaced by measured ensemble runs.

| Instance | Evidence Mode | Quantum Estimate | Ensemble Std Error | Classical Baseline (threshold 2.0) | Quantum-Classical Delta |
|---|---|---:|---:|---:|---:|
| small | measured | 0.195833 | 0.018186 | 0.242000 | -0.046167 |
| medium | provisional_projection | 0.015000 | 0.002402 | 0.242000 | -0.227000 |
| large | provisional_projection | 0.006000 | 0.001526 | 0.242000 | -0.236000 |

## Fairness Notes

- Baseline source: `python/classical_baseline.py` -> `estimates/classical_baseline.json`.
- Current baseline is plain Monte Carlo and should be extended with variance-reduction comparators.
- Promotion to demonstrated status requires measured ensemble artifacts for all listed instances.

