# 02. Quantum Catalysis Challenge

This problem explores quantum simulation of catalytic reaction mechanisms, comparing classical and quantum approaches for estimating reaction rates and energy barriers. The goal is to establish analytical baselines and prepare for quantum algorithm implementation.

## Roadmap
- [x] Scaffold directory structure
- [x] Implement classical analytical baseline (Arrhenius model)
- [x] Implement Q# analytical baseline (matching classical results)
- [x] Generate parameter instances (small/medium/large)
- [x] Validate outputs and plots
- [ ] Update documentation and website status

## Quickstart
```bash
cd problems/02_catalysis
make classical      # Run classical baseline analysis
make analyze        # Generate plots
make build          # Build Q# project (requires .NET 6.0)
make run            # Run quantum simulation
```

## Outputs
- `estimates/classical_baseline.json`: Structured Arrhenius rates for each instance
- `plots/rate_vs_temperature.png`: Visualization of reaction rates vs. temperature
- `qsharp/bin/Release/net6.0/Catalysis.dll`: Analytical Q# baseline executable

## Current Results

Running `python python/classical_baseline.py` produces the following reaction rates:

| Instance | Catalyst | Temperature (K) | Rate (s^-1) |
|----------|----------|-----------------|-------------|
| small    | Pt       | 300             | 0.8727      |
| medium   | Fe       | 500             | 5.94×10^2   |
| large    | Cu       | 700             | 2.92×10^5   |

The Q# entry point `RunAnalyticalCatalysisBaseline` reports the same values, confirming parity between classical and quantum-friendly baselines.

## References
- Quantum simulation of chemical catalysis
- Analytical models for reaction rates
- Q# quantum chemistry libraries

## Objective Maturity Gate

- **Current gate**: **Stage B complete** (classical baseline and Q# scaffold/build path are in place).
- **Next gate target**: **Stage C** (hardware-aware validation with uncertainty-bounded comparisons).

Stage C exit criteria for this problem:

- Execute at least one non-placeholder quantum workflow path tied to the problem objective.
- Report uncertainty-bounded comparisons between classical and quantum outputs on `small` and `medium` instances.
- Document transpilation/connectivity and backend assumptions used for reported quantum runs.
- Add calibration/noise-sensitivity evidence for the reported quantum metrics.

## Advantage Claim Contract

- **Claim category (current)**: `theoretical`.
- **Problem class and regime**: Problem-specific challenge instances defined in this directory.
- **Fair baseline**: Problem-local classical baseline in `python/` outputs.
- **Quantum resource scaling claim**: Expected asymptotic advantage depends on algorithm family and implementation assumptions; no hardware-demonstrated speedup claim yet.
- **Data-loading and I/O assumptions**: Must be documented alongside future advantage claims.
- **Noise/error model assumptions**: Backend-specific model and calibration assumptions to be added at Stage C.
- **Confidence/uncertainty method**: To be reported using shot-based confidence intervals or equivalent statistical bounds.
- **Residual risks**: Oracle/state-preparation/transpilation overhead may dominate for near-term instance sizes.
