# 04. Quantum Linear Solvers

This challenge sets up the scaffolding needed to explore quantum linear system algorithms such as HHL and modern block-encoding refinements. The immediate goal is to provide deterministic classical baselines, representative instance data, and a Q# entry point that compiles cleanly while we design a genuine quantum kernel.

## Roadmap

- [x] Scaffold directory structure and helper scripts
- [x] Provide classical solver baseline with condition-number diagnostics
- [x] Supply representative Poisson-style benchmark instances (small/medium/large)
- [x] Add analysis notebooks for quick visual checks
- [x] Implement Q# analytical baseline matching the classical small instance
- [ ] Replace analytical baseline with block-encoding + phase estimation routine
- [ ] Connect resource estimator profiles for multiple precision targets

## Quickstart

```bash
cd problems/04_linear_solvers
make classical      # Solve each YAML instance with dense linear algebra
make analyze        # Generate plots of condition numbers and residuals
make build          # Build the Q# project (requires .NET 6.0 runtime)
make run            # Execute the Q# analytical baseline for the small instance
make estimate       # (Placeholder) Run resource estimation once quantum kernel lands
```

## Outputs

- `estimates/classical_baseline.json` – Solutions, condition numbers, and residuals for each YAML instance
- `plots/condition_numbers.png` – Visual comparison of condition numbers across instances
- `plots/residual_vs_precision.png` – Residual norms versus target precision requirements
- `qsharp/bin/Release/net6.0/LinearSolvers.dll` – Compiled Q# analytical baseline

## Current Baseline

The classical baseline uses dense solves via NumPy and reports diagnostics that map directly to HHL parameters (e.g., condition numbers, residual norms). The Q# entry point `RunLinearSolverBaseline` reconstructs the small-instance solution analytically to provide a sanity check while the real quantum linear solver is under construction.

Next milestone: introduce a block-encoding of the tridiagonal Poisson matrix, connect it to iterative phase estimation, and plumb the resulting rotation counts into the Azure Quantum Resource Estimator profiles in `tooling/estimator/targets/`.
