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

- **Q# code**: `qsharp/Program.qs` implements the **canonical QAE algorithm** with Grover operators and quantum phase estimation. ✅ **COMPLETE**
- **Python tooling**: `python/` contains the Monte Carlo baseline and visualization scripts.
- **Instances**: `instances/` provides YAML files that parameterize the loss distribution and thresholds.
- **Estimates**: `estimates/` captures resource estimation outputs produced by Azure Quantum tooling.
- **Documentation**: See [QAE_IMPLEMENTATION_SUMMARY.md](QAE_IMPLEMENTATION_SUMMARY.md) for comprehensive technical details.

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
- [x] **Canonical QAE implementation** with Grover operators and QPE
- [x] Azure Quantum resource estimation
- [x] Classical Monte Carlo baseline
- [x] Analysis and visualization
- [x] Comprehensive technical documentation
- [x] Calibrated baseline instance (phase/oracle alignment and entrypoint fix)
- [ ] Broader calibration hardening across more instances and seeds

## Results Summary

**Test Case**: 4 loss qubits (16 levels), 6 precision qubits, log-normal(0,1), threshold=2.5, theoretical tail probability 18.98%

Latest Azure Quantum Resource Estimates:

| Architecture | Physical Qubits | Runtime | T-States | Logical Qubits |
|--------------|-----------------|---------|----------|----------------|
| gate_ns_e3 (optimal) | **594k** | **6.4s** | **965k** | 13 (38 layout) |
| gate_ns_e4 | 561k | 6.7s | 965k | 13 (38 layout) |
| maj_ns_e4 (Majorana) | 400k | 28.5s | 965k | 13 (38 layout) |

**T-State Breakdown** (gate_ns_e3):
- Rotation gates: 36.9k × 20 = **738k** (76%)
- CCZ gates: 56.8k × 4 = **227k** (24%)
- Direct T gates: 240 (<1%)

**Comparison with Other Quantum Algorithms**:
- **QAE**: 594k qubits, 6.4s, 965k T-states
- **HHL** (Problem 01): 18.7k qubits, 52ms, 903 T-states (31.8× less qubits)
- **VQE** (Problem 01): 48.5k-110k qubits, 47-182μs, 18 T-gates (5.4-12.2× less qubits)

## Classical Comparison

**Current Test Results**:
- **Classical Monte Carlo** (10k samples): 18.98% ± 0.39% (0% relative error)
- **QAE Current** (120 repetitions): 19.17% ± 3.59% (about 1.0% relative error)
- **Theoretical**: 18.98%

**Complexity Analysis**:
- **Classical Monte Carlo**: O(1/ε²) samples
  - For ε = 0.01: ~10,000 samples
- **Quantum Amplitude Estimation**: O(1/ε) oracle calls
  - For ε = 0.01: ~100 queries
  - **Quadratic speedup** for high precision

**Implementation Status**: Calibrated baseline instance is accurate with proper Grover operators and QPE; next work is robustness hardening across additional instances and ensemble seeds.

### Calibration Workflow

```bash
make calibrate CALIBRATION_RUNS=20
```

This command runs repeated Q# executions through `python/analyze.py --ensemble-runs ...`, stores per-run outputs in `estimates/quantum_estimate_run*.json`, and writes aggregate metrics to `estimates/quantum_estimate_ensemble.json`.

Quantum advantage becomes compelling when:

- Sub-percent tail probabilities are required for regulatory reporting.
- Loss distributions are expensive to sample due to complex correlations.
- Multiple related risk metrics must be estimated simultaneously.
- Precision requirements are high (ε < 0.01).

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
