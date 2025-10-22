# Problem 16 · Quantum Error Correction

## Overview

Fault-tolerant quantum computing demands error correction codes that suppress noisy qubit failures faster than they accumulate. This scaffold supplies a reproducible classical baseline for repetition-code style logical error analysis while standing up a Q# project that will ultimately host stabilizer simulations and surface-code primitives. By comparing physical error rates against logical failure probabilities we track where quantum error correction (QEC) begins to pay off.

## Directory Layout

```text
16_error_correction/
├── estimates/                       # JSON artifacts from classical / quantum workflows
├── instances/                       # Code distances and physical error-rate sweeps
├── plots/                           # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py        # Analytical repetition-code logical error model
│   └── analyze.py                   # Visualization of suppression factors and pseudo-thresholds
└── qsharp/
    ├── QuantumQEC.csproj            # Q# project placeholder for stabilizer routines
    └── Program.qs                   # Stubbed quantum workflow
```

## Quick Start

```bash
cd problems/16_error_correction

# Classical logical error analysis
python python/classical_baseline.py

# Plot logical error curves and suppression heatmaps
python python/analyze.py

# Quantum placeholder (requires .NET 6)
dotnet build qsharp/QuantumQEC.csproj
 dotnet run --project qsharp/QuantumQEC.csproj
```

## Next Quantum Milestones

1. **Stabilizer Simulation** – Implement syndrome extraction cycles for repetition or surface codes.
2. **Decoder Integration** – Explore minimum-weight matching or belief propagation within Q#.
3. **Resource Accounting** – Track qubit counts, circuit depth, and ancilla demand per cycle.
4. **Fault-Tolerant Benchmarks** – Compare logical error suppression across physical noise models.

This scaffold keeps the analytical QEC baseline reproducible while we build toward full stabilizer simulations in Q#. 🛡️⚛️
