# Problem 20 · Quantum Space Mission Planning

## Overview

Designing efficient interplanetary trajectories involves balancing launch windows, gravity assists, and propulsive maneuvers under tight mission constraints. This scaffold couples a reproducible classical baseline based on patched-conic transfer approximations with a Q# project prepared for future quantum annealing and amplitude amplification studies. The objective is to benchmark classical delta-v budgets and schedule feasibility against quantum-inspired search strategies for complex mission profiles.

## Directory Layout

```text
20_space_mission_planning/
├── estimates/                        # JSON artifacts from classical and quantum workflows
├── instances/                        # Mission geometries, gravity assist sequences, and time budgets
├── plots/                            # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py         # Patched-conic delta-v estimator and window feasibility scoring
│   └── analyze.py                    # Visualization of delta-v breakdowns and schedule slack
└── qsharp/
    ├── QuantumMission.csproj         # Q# project placeholder for annealing style routines
    └── Program.qs                    # Stubbed quantum workflow
```

## Quick Start

```bash
cd problems/20_space_mission_planning

# Classical mission baseline
python python/classical_baseline.py

# Plot delta-v budgets and schedule slack
python python/analyze.py

# Quantum placeholder (requires .NET 6)
dotnet build qsharp/QuantumMission.csproj
 dotnet run --project qsharp/QuantumMission.csproj
```

## Next Quantum Milestones

1. **Trajectory Encoding** – Map transfer legs into qubit registers for annealing or amplitude amplification.
2. **Constraint Encoding** – Incorporate launch windows, gravity assists, and vehicle limits via penalty functions.
3. **Hybrid Heuristics** – Combine classical patched-conic seeding with quantum search refinement.
4. **Resource Estimation** – Evaluate qubit counts and circuit depth for realistic mission complexity.

This scaffold keeps the classical planning baseline reproducible while preparing for quantum-enhanced mission optimization.
