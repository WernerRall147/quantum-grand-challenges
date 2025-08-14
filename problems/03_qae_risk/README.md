# Problem 03: Quantum Amplitude Estimation for Risk Analysis

## Overview
This problem demonstrates using Quantum Amplitude Estimation (QAE) to estimate tail probabilities in financial risk models, providing a quadratic speedup over classical Monte Carlo methods.

## Algorithm
**Quantum Amplitude Estimation (QAE)** estimates the amplitude (and thus probability) of marked states in a quantum superposition. For risk analysis, we:

1. Encode a probability distribution as quantum amplitudes
2. Mark "tail risk" states (e.g., losses exceeding a threshold)
3. Use QAE to estimate the probability of these marked states
4. Achieve ε precision with O(1/ε) queries vs. O(1/ε²) for classical Monte Carlo

## Implementation
- **Q# Code**: `qsharp/` directory contains QAE implementation for risk estimation
- **Analysis**: `python/` directory contains classical Monte Carlo baseline and plotting
- **Instances**: `instances/` directory contains risk model parameters (distributions, thresholds)
- **Results**: `estimates/` directory contains resource estimation outputs

## Mathematical Background

### Risk Model
Consider a portfolio with loss distribution L. We want to estimate:
```
P(L > threshold) = P(tail risk event)
```

### Quantum Encoding
1. **State Preparation**: Encode loss distribution L as quantum amplitudes
   ```
   |ψ⟩ = Σᵢ √(p(lᵢ)) |i⟩ ⊗ |lᵢ⟩
   ```

2. **Oracle**: Mark states where loss exceeds threshold
   ```
   O|i⟩|lᵢ⟩|0⟩ = |i⟩|lᵢ⟩|1⟩ if lᵢ > threshold, else |i⟩|lᵢ⟩|0⟩
   ```

3. **QAE**: Estimate amplitude a = √P(L > threshold)

### Quantum Advantage
- **Classical**: O(1/ε²) samples needed for ε precision
- **Quantum**: O(1/ε) queries needed for ε precision
- **Speedup**: Quadratic improvement for high-precision estimates

## Usage

### Build and Test
```bash
make build
make test
```

### Resource Estimation
```bash
make estimate                    # Default surface code target
make estimate TARGET=qubit_gate_ns_e3    # Specific target
make sweep                       # Parameter sweep across precisions
```

### Analysis and Plotting
```bash
make analyze                     # Generate comparison plots
make compare                     # Compare with Monte Carlo baseline
```

## Problem Instances

### Small Instance (`instances/small.yaml`)
- **Distribution**: Log-normal with μ=0, σ=1
- **Threshold**: 95th percentile (VaR 95%)
- **Precision**: ε = 0.1
- **Qubits**: ~8-10 logical qubits

### Medium Instance (`instances/medium.yaml`)
- **Distribution**: Mixture of log-normals (fat tails)
- **Threshold**: 99th percentile (VaR 99%)
- **Precision**: ε = 0.01
- **Qubits**: ~12-15 logical qubits

### Large Instance (`instances/large.yaml`)
- **Distribution**: Complex multi-asset portfolio model
- **Threshold**: 99.9th percentile (extreme tail)
- **Precision**: ε = 0.001
- **Qubits**: ~18-20 logical qubits

## Status
- [x] Problem specification complete
- [x] Q# implementation complete
- [x] Unit tests complete
- [x] Resource estimation complete
- [x] Classical baseline implemented
- [x] Analysis and visualization complete
- [x] Documentation complete

## Results Summary
*Latest resource estimates (Surface Code Generic v1):*

| Instance | Precision | Logical Qubits | Physical Qubits | T-count | Runtime |
|----------|-----------|----------------|-----------------|---------|---------|
| Small    | ε=0.1     | 12            | ~50K            | ~10⁶    | ~1 min  |
| Medium   | ε=0.01    | 18            | ~200K           | ~10⁸    | ~1 hour |
| Large    | ε=0.001   | 24            | ~800K           | ~10¹⁰   | ~1 day  |

## Classical Comparison
For ε=0.01 precision:
- **Classical Monte Carlo**: ~10⁴ samples, ~1 second
- **Quantum Amplitude Estimation**: ~100 queries, requires fault-tolerant quantum computer

**Quantum advantage emerges when:**
- Very high precision needed (ε < 0.001)
- Expensive-to-simulate distributions
- Multiple correlated risk metrics needed

## References
- [Quantum Amplitude Estimation](https://arxiv.org/abs/quant-ph/0005055) - Brassard et al.
- [Quantum Risk Analysis](https://arxiv.org/abs/1906.02573) - Woerner & Egger
- [Financial Applications](https://arxiv.org/abs/1905.02666) - Egger et al.
- [Azure Quantum QAE](https://docs.microsoft.com/en-us/azure/quantum/user-guide/libraries/numerics/amplitude-estimation)

## Notes
This implementation serves as a proof-of-concept for quantum advantage in financial risk analysis. Real-world applications would require:
- More sophisticated distribution encoding
- Noise-aware algorithm design  
- Integration with existing risk management systems
- Cost-benefit analysis vs. classical methods

The quantum advantage is most pronounced for:
1. **High-precision tail risk estimation** (regulatory stress testing)
2. **Complex correlation structures** (difficult to sample classically)
3. **Real-time risk monitoring** (when quantum computers become available)
