# 05. QAOA for Max-Cut

This problem prepares the groundwork for implementing the Quantum Approximate Optimization Algorithm on weighted Max-Cut instances. The current milestone provides deterministic classical baselines, representative graph instances, and a working depth-1 QAOA circuit with a coarse parameter sweep.

## Roadmap

- [x] Scaffold directory structure, utilities, and helper scripts
- [x] Provide classical brute-force baseline with summary statistics
- [x] Add parameterized graph instances (small/medium/large)
- [x] Generate diagnostic plots for cut values
- [x] Implement depth-1 QAOA circuit with coarse parameter sweep
- [ ] Generalize QAOA driver to consume YAML instances dynamically
- [ ] Route optimized parameters into the resource estimator profiles

## Quickstart

```bash
cd problems/05_qaoa_maxcut
make classical      # Exhaustive search baseline for each YAML graph instance
make analyze        # Generate plots summarizing best cut values
make build          # Build the Q# project (requires .NET 6.0 runtime)
make run            # Run the depth-1 QAOA grid search on the small triangle graph
```

## Outputs

- `estimates/classical_baseline.json` – Maximum cut assignments and values for every graph instance
- `plots/best_cut_values.png` – Visual comparison of Max-Cut values across instances
- `plots/value_distribution_small.png` – Distribution of cut values for the small instance
- `qsharp/bin/Release/net6.0/QaoaMaxCut.dll` – Compiled Q# QAOA implementation

## Current Baseline

The classical baseline enumerates all bit strings to guarantee optimal Max-Cut values and logs diagnostic metrics that translate directly to QAOA objective functions. The Q# entry point `RunMaxCutBaseline` now performs a depth-1 QAOA grid search for the weighted triangle instance, reports the best sampled cut and expectation value, and highlights the gap to the classical optimum. Future work will expand the pipeline to larger graphs and tighter optimizers.
