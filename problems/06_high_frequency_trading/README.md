# Problem 06 · Quantum-Enhanced High-Frequency Trading

## Overview

High-frequency trading (HFT) strategies react to market micro-structure signals within milliseconds. Classical approaches rely on hand-crafted signals and predictive models that must balance latency, accuracy, and transaction costs. The goal of this challenge is to explore how quantum machine learning can accelerate signal discovery and execution for intraday trading.

This directory contains the first scaffold toward that objective:

- **Classical baseline** – A synthetic limit-order-book price generator paired with a moving-average crossover strategy that trades subject to transaction costs. The baseline produces reproducible metrics (Sharpe ratio, turnover, drawdown) for each benchmark instance.
- **Quantum plan** – A Q# project stub prepared to host amplitude-encoded feature maps and variational classifiers (e.g., quantum kernel methods or QAOA-style policy search). The current entry point simply validates project wiring while we develop the quantum pipeline.
- **Analysis tooling** – Plot generation for price trajectories and strategy equity curves to gauge the quality of classical baselines before quantum enhancements are implemented.

## Repository Layout

```text
06_high_frequency_trading/
├── estimates/                # JSON outputs (classical & quantum once available)
├── instances/                # Synthetic market scenarios (small/medium/large)
├── plots/                    # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py # Deterministic Monte Carlo + trading metrics
│   └── analyze.py            # Visualization helpers
└── qsharp/
    ├── HighFrequencyTrading.csproj # Q# project stub
    └── Program.qs                  # Placeholder quantum workflow
```

## Getting Started

```bash
cd problems/06_high_frequency_trading

# Classical baseline (writes estimates/classical_baseline.json)
python python/classical_baseline.py

# Plot price + equity curves
python python/analyze.py

# Quantum entry point placeholder
dotnet build qsharp/HighFrequencyTrading.csproj
dotnet run --project qsharp/HighFrequencyTrading.csproj
```

## Next Quantum Milestones

1. **Data Encoding** – Implement efficient amplitude/state preparation routines that embed recent order-book states into qubit registers.
2. **Quantum Model** – Prototype a variational classifier (e.g., quantum kernel SVM or variational quantum perceptron) that predicts short-term delta sign.
3. **Execution Policy** – Combine quantum predictions with classical risk management to minimize turnover and cost drag.
4. **Resource Estimation** – Evaluate qubit and gate requirements for realistic market depths, then benchmark against classical baselines.

Stay tuned as we iterate toward quantum-native trading signals! 🧠⚡️

## Objective Maturity Gate

- **Current gate**: **Stage B complete** (classical baseline and Q# scaffold/build path are in place).
- **Next gate target**: **Stage C** (hardware-aware validation with uncertainty-bounded comparisons).

Stage C exit criteria for this problem:

- Execute at least one non-placeholder quantum workflow path tied to the problem objective.
- Report uncertainty-bounded comparisons between classical and quantum outputs on `small` and `medium` instances.
- Document transpilation/connectivity and backend assumptions used for reported quantum runs.
- Add calibration/noise-sensitivity evidence for the reported quantum metrics.

## DiVincenzo Readiness (Stage C/D Overlay)

| Criterion | Status | Evidence / Notes |
|---|---|---|
| Scalable qubit system | partial | Problem-scoped instance baselines are in place; full hardware-scale projections are tracked as Stage C work. |
| Initialization | partial | Input/state initialization path is defined for current workflows, with backend-ready loading fidelity still to be hardened. |
| Coherence vs gate time | not-yet | Backend-calibrated coherence-vs-depth evidence is pending and required for Stage C/D promotion. |
| Universal gate set | partial | Q# scaffold/build path exists; gate-basis decomposition and transpilation evidence remain Stage C tasks. |
| Qubit-specific measurement | partial | Measurement outputs are defined for current validation flows; hardware readout characterization is pending. |
## Advantage Claim Contract

- **Claim category (current)**: `theoretical`.
- **Problem class and regime**: Problem-specific challenge instances defined in this directory.
- **Fair baseline**: Problem-local classical baseline in `python/` outputs.
- **Quantum resource scaling claim**: Expected asymptotic advantage depends on algorithm family and implementation assumptions; no hardware-demonstrated speedup claim yet.
- **Data-loading and I/O assumptions**: Must be documented alongside future advantage claims.
- **Noise/error model assumptions**: Backend-specific model and calibration assumptions to be added at Stage C.
- **Confidence/uncertainty method**: To be reported using shot-based confidence intervals or equivalent statistical bounds.
- **Residual risks**: Oracle/state-preparation/transpilation overhead may dominate for near-term instance sizes.
