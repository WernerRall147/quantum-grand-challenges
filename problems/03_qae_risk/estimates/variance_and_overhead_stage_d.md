# Stage D Variance Reduction And Overhead Review - 03_qae_risk

Monte Carlo seed: 314159
Monte Carlo samples per instance: 200000

## Variance-Reduction Fairness

| Instance | Threshold | Quantum Std Error | Naive MC Std Error | Antithetic Std Error | Control-Variate Std Error |
|---|---:|---:|---:|---:|---:|
| small | 2.500 | 0.018186 | 0.000857 | 0.000759 | 0.000608 |
| medium | 5.000 | 0.011180 | 0.000502 | 0.000486 | 0.000339 |
| large | 7.000 | 0.006250 | 0.000498 | 0.000480 | 0.000357 |

## Oracle/State-Preparation Overhead Accounting

Effective query-equivalent is modeled as QAE query rounds multiplied by an overhead factor.

| Instance | QAE Query Rounds | Classical Samples @1e-3 | Overhead Factor | Effective Quantum Query-Equivalent | Effective Speedup |
|---|---:|---:|---:|---:|---:|
| small | 384 | 47500 | 1 | 384 | 123.70x |
| small | 384 | 47500 | 10 | 3840 | 12.37x |
| small | 384 | 47500 | 100 | 38400 | 1.24x |
| medium | 384 | 47500 | 1 | 384 | 123.70x |
| medium | 384 | 47500 | 10 | 3840 | 12.37x |
| medium | 384 | 47500 | 100 | 38400 | 1.24x |
| large | 384 | 47500 | 1 | 384 | 123.70x |
| large | 384 | 47500 | 10 | 3840 | 12.37x |
| large | 384 | 47500 | 100 | 38400 | 1.24x |

## Notes

- Variance-reduction comparators now include antithetic and control-variate Monte Carlo estimators.
- Overhead accounting is model-based and should be replaced with backend measured timing when available.
- This artifact supports Stage D fairness and overhead checklist closure for projected-claim hardening.
