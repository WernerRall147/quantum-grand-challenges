# Problem 10 · Post-Quantum Cryptography Security Analysis

## Overview

Post-quantum cryptography (PQC) must withstand both classical and quantum attacks. Modern lattice schemes trade performance against resistance to advanced BKZ reduction and Grover-amplified sieving. This directory holds two pieces that answer different questions:

- **Classical script** (`python/classical_baseline.py`): a toy cost formula for BKZ lattice attacks on NIST-style parameter sets. Its quadratic cost in the block size and its Grover adjustment are illustrative; they are not the core-SVP estimates of the lattice estimator, so its margins are not security estimates.
- **Q# kernel** (`qsharp/src/Main.qs`): Grover search for one marked key among 2^n (3 to 5 qubits). With 3 qubits one iteration finds the key with probability 0.78125, checked against exact simulation. Its classical comparator is exhaustive search, (N + 1)/2 queries on average; it does not model sieving or a cipher.

## Directory Layout

```text
10_post_quantum_cryptography/
├── estimates/                      # JSON artifacts from classical / quantum workflows
├── instances/                      # Representative NIST parameter sets
├── plots/                          # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py       # Toy BKZ attack-cost formula
│   └── analyze.py                  # Visualization of security margins
└── qsharp/
    ├── qsharp.json                 # Modern QDK project file
    ├── src/Main.qs                 # Grover key search on 3-5 qubits
    └── HardwareKernel.qs           # QIR kernel for Azure Quantum
```

## Quick Start

```bash
cd problems/archived/10_post_quantum_cryptography

# Toy attack-cost formula (writes estimates/classical_baseline.json)
python python/classical_baseline.py

# Visualize cost curves and margins
python python/analyze.py

# Grover key search demo
python -c "from qdk import qsharp; qsharp.init(project_root='qsharp'); qsharp.run('Main.RunPostQuantumAnalysis()', 1)"
```

## Next Quantum Milestones

1. **Amplitude Amplification Kernel** – Prototype Grover-style boosts for nearest vector search cost models.
2. **Hybrid BKZ Simulation** – Integrate amplitude amplification with classical pruning heuristics in Q#.
3. **Adaptive Parameter Study** – Sweep lattice dimensions / modulus sizes to locate safe PQC parameters.
4. **Resource Estimation** – Quantify logical qubits and T-count for practical quantum sieving on targeted dimensions.

This scaffold keeps classical estimators reproducible while we prototype quantum-enhanced attack analyses. 🔐⚛️

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

- **Claim category (current)**: `projected`.
- **Problem class and regime**: Problem-specific challenge instances defined in this directory.
- **Fair baseline**: Exhaustive key search, (N + 1)/2 queries on average for one marked key among N. `python/classical_baseline.py` is a toy lattice-attack cost formula for a different question.
- **Quantum resource scaling claim**: Expected asymptotic advantage depends on algorithm family and implementation assumptions; no hardware-demonstrated speedup claim yet.
- **Data-loading and I/O assumptions**: Must be documented alongside future advantage claims.
- **Noise/error model assumptions**: Backend-specific model and calibration assumptions to be added at Stage C.
- **Confidence/uncertainty method**: To be reported using shot-based confidence intervals or equivalent statistical bounds.
- **Residual risks**: Oracle/state-preparation/transpilation overhead may dominate for near-term instance sizes.
