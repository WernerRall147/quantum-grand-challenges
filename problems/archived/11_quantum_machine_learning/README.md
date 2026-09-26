# Problem 11 · Quantum Machine Learning Kernel Benchmark

## Overview

Quantum kernel methods map classical data into high-dimensional Hilbert spaces using parameterized feature maps. This directory holds two pieces that measure different things:

- **Q# swap test** (`qsharp/src/Main.qs`): amplitude-encodes 4-feature vectors on two qubits each and estimates |⟨a|b⟩|² from P(ancilla = 0) = (1 + |⟨a|b⟩|²)/2. The error falls as 1/√shots, so additive error ε costs O(1/ε²) repetitions, and loading a d-dimensional classical vector costs O(d) gates in general: for classical data the same kernel is computable classically in O(d) time, and this example demonstrates no speedup.
- **Classical baseline** (`python/classical_baseline.py`): kernel ridge classification with a radial-basis-function kernel on synthetic datasets. It reports classification accuracy, a different task from the Q# overlap estimate.

### Correction (2026-09-26)

The encoding applied an absolute value to every amplitude, so vectors with negative entries were encoded as their absolute values while the classical reference kept the signs (for [0.5, −0.5, 0.5, 0.5] against [0.5, 0.5, 0.5, 0.5] the swap test returned P(0) = 1 instead of 0.625). The hardware kernel swapped two product states unrelated to any feature vector; it now encodes the estimator's vectors, with exact P(0) = 0.9175. The demo claimed the swap test needs O(1) measurements and gives an exponential speedup; both claims are removed. `tooling/test_swap_test_kernel.py` pins the encoding, the program and the hardware kernel to exact values.

## Directory Layout

```text
11_quantum_machine_learning/
├── estimates/                      # JSON artifacts from classical / quantum workflows
├── instances/                      # Dataset parameter sets (small/medium/large)
├── plots/                          # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py       # Kernel ridge classification baseline
│   └── analyze.py                  # Visualization of accuracy and alignment metrics
└── qsharp/
    ├── qsharp.json                 # Modern QDK project file
    ├── src/Main.qs                 # Swap-test kernel estimation
    └── HardwareKernel.qs           # QIR kernel for Azure Quantum
```

## Quick Start

```bash
cd problems/archived/11_quantum_machine_learning

# Classical baseline (writes estimates/classical_baseline.json)
python python/classical_baseline.py

# Visualize accuracy and kernel statistics
python python/analyze.py

# Swap-test kernel demo
python -c "from qdk import qsharp; qsharp.init(project_root='qsharp'); qsharp.run('Main.RunQuantumKernelEstimation()', 1)"
```

## Next Quantum Milestones

1. **Feature Map Implementation** – Encode classical feature vectors into amplitude or Hamiltonian embeddings within Q#.
2. **Quantum Kernel Evaluation** – Use swap-test style overlaps to assemble Gram matrices for downstream classifiers.
3. **Hybrid Training Loop** – Combine quantum kernel evaluations with classical optimizers for model selection.
4. **Resource Estimation** – Evaluate qubit counts and circuit depth for realistic dataset sizes and compare against classical baselines.

This scaffold keeps the classical kernel baseline reproducible while we iterate toward genuine quantum machine learning experiments. 🤖⚛️

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
- **Quantum resource scaling claim**: None for this kernel on classical data (O(d) loading, O(1/ε²) shots per kernel entry); no hardware-demonstrated speedup claim.
- **Data-loading and I/O assumptions**: Must be documented alongside future advantage claims.
- **Noise/error model assumptions**: Backend-specific model and calibration assumptions to be added at Stage C.
- **Confidence/uncertainty method**: To be reported using shot-based confidence intervals or equivalent statistical bounds.
- **Residual risks**: Oracle/state-preparation/transpilation overhead may dominate for near-term instance sizes.
