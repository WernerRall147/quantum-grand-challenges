# Stage D Fairness Benchmark - 05_qaoa_maxcut

Classical comparator families used: exhaustive optimum, greedy local search, and random sampling baseline.

| Instance | Quantum Mean +/- CI95 | Classical Optimum | Greedy | Random Best | Gap To Optimum |
|---|---:|---:|---:|---:|---:|
| large | 4.1578 +/- 0.2270 | 7.3000 | 7.3000 | 7.3000 | 3.1422 |
| medium | 2.8316 +/- 0.2005 | 4.0000 | 2.5000 | 4.0000 | 1.1684 |
| small | 1.9247 +/- 0.0220 | 2.2000 | 2.2000 | 2.2000 | 0.2753 |

Notes:
- Quantum values are taken from highest-depth available baseline artifacts per instance.
- Greedy/random comparators are deterministic through fixed seeds in this script.

