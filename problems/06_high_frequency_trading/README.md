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
