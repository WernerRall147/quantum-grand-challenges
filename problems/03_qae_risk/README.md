# Problem 03: Quantum Amplitude Estimation for Risk Analysis

## Overview

Quantum Amplitude Estimation (QAE) estimates the probability of marked states inside a quantum superposition. Applied to risk analysis, it enables tail probability estimation with quadratically fewer oracle queries than classical Monte Carlo sampling.

## Algorithm

The QAE workflow for risk estimation consists of the following stages:

1. Encode the loss distribution as amplitudes of a quantum state.
2. Mark “tail risk” outcomes (loss exceeding a threshold) with an oracle.
3. Apply amplitude amplification and phase estimation to recover the amplitude of the marked subspace.
4. Achieve ε precision using O(1/ε) calls to the oracle, compared with O(1/ε²) samples for classical Monte Carlo.

## Implementation

- **Q# code**: `qsharp/` implements the analytical QAE baseline used in CI.
- **Python tooling**: `python/` contains the Monte Carlo baseline and visualization scripts.
- **Instances**: `instances/` provides YAML files that parameterize the loss distribution and thresholds.
- **Estimates**: `estimates/` captures resource estimation outputs produced by Azure Quantum tooling.

## Mathematical Background

### Risk Model

Consider a portfolio with loss distribution `L`. The quantity of interest is the tail probability `P(L > threshold)`, the chance that losses exceed a specified VaR boundary.

### Quantum Encoding

1. **State preparation** loads the loss distribution into amplitudes using controlled rotations (final circuit to be published alongside the quantum implementation).
2. **Oracle marking** flips an ancilla qubit whenever the simulated loss breaches the threshold.
3. **Amplitude estimation** extracts the amplitude of the marked subspace, which equals the desired tail probability.

### Quantum Advantage

- **Classical**: O(1/ε²) samples for additive precision ε.
- **Quantum**: O(1/ε) oracle invocations for the same precision.
- **Outcome**: Quadratic speedup becomes meaningful for high confidence levels and expensive payoff calculations.

## Usage

### Build and Test

```bash
make build
make test
```

### Resource Estimation

```bash
make estimate                     # Surface-code defaults
make estimate TARGET=qubit_gate_ns_e3  # Specific hardware target
make sweep                        # Precision sweep for comparison
```

### Analysis and Plotting

```bash
make analyze                      # Generate comparison plots
make compare                      # Compare quantum vs classical
```

## Problem Instances

### Small (`instances/small.yaml`)

- Log-normal loss distribution with μ = 0, σ = 1.
- Tail threshold at the 95th percentile (VaR 95%).
- Precision ε = 0.1 requiring roughly 8–10 logical qubits.

### Medium (`instances/medium.yaml`)

- Mixture of log-normal components producing fat tails.
- Tail threshold at the 99th percentile (VaR 99%).
- Precision ε = 0.01 requiring roughly 12–15 logical qubits.

### Large (`instances/large.yaml`)

- Multi-asset portfolio with correlated factors.
- Tail threshold at the 99.9th percentile (extreme VaR).
- Precision ε = 0.001 requiring roughly 18–20 logical qubits.

## Status Checklist

- [x] Problem specification
- [x] Analytical Q# baseline
- [x] Unit tests
- [x] Resource estimation scripts
- [x] Classical Monte Carlo baseline
- [x] Analysis and visualization
- [x] Documentation

## Results Summary

Latest Azure Quantum estimates (Surface Code Generic v1):

| Instance | Precision | Logical Qubits | Physical Qubits | T-count | Runtime |
|----------|-----------|----------------|-----------------|---------|---------|
| Small    | ε = 0.1   | 12             | ~50K            | ~10⁶    | ~1 min  |
| Medium   | ε = 0.01  | 18             | ~200K           | ~10⁸    | ~1 hour |
| Large    | ε = 0.001 | 24             | ~800K           | ~10¹⁰   | ~1 day  |

## Classical Comparison

For ε = 0.01 precision:

- **Classical Monte Carlo**: ~10⁴ samples (≈1 second on a laptop).
- **Quantum amplitude estimation**: ~10² oracle calls (requires fault-tolerant hardware).

Quantum advantage becomes compelling when:

- Sub-percent tail probabilities are required for regulatory reporting.
- Loss distributions are expensive to sample due to complex correlations.
- Multiple related risk metrics must be estimated simultaneously.

## References

- [Quantum Amplitude Estimation](https://arxiv.org/abs/quant-ph/0005055) — Brassard et al.
- [Quantum Risk Analysis](https://arxiv.org/abs/1906.02573) — Woerner & Egger.
- [Financial Applications](https://arxiv.org/abs/1905.02666) — Egger et al.
- [Azure Quantum QAE](https://learn.microsoft.com/azure/quantum/user-guide/libraries/numerics/amplitude-estimation).

## Notes

This benchmark demonstrates a pathway to quantum advantage in financial risk analytics. Production deployments will require:

- More expressive state preparation that captures real portfolio loss distributions.
- Noise-aware algorithm design and error mitigation techniques.
- Integration with classical risk pipelines and data governance policies.
- Holistic cost/benefit analysis against classical accelerators.

High-impact use cases include regulatory stress testing, extreme tail-risk monitoring, and rapid what-if scenario analysis across large derivative books.
