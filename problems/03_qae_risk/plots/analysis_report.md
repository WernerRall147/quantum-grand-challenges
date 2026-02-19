# QAE Risk Analysis Summary Report
Generated: 2026-02-19 21:42:11.128034

## Quantum Amplitude Estimation Results
### Result 1: TailRisk > 3.0
- Algorithm: QPEAmplitudeEstimation
- Logical Qubits: 8
- Physical Qubits: 8
- T-count: 2,688
- Circular amplitude (phase-averaged): 0.161918
- Circular phase estimate: 0.131820
- Runtime: 0 days

### Result 2: TailRisk > 3.0
- Algorithm: QPEAmplitudeEstimation
- Logical Qubits: 8
- Physical Qubits: 8
- T-count: 2,688
- Circular amplitude (phase-averaged): 0.161271
- Circular phase estimate: 0.131541
- Runtime: 0 days

### Result 3: TailRisk > 3.0
- Algorithm: QPEAmplitudeEstimation
- Logical Qubits: 8
- Physical Qubits: 8
- T-count: 2,688
- Circular amplitude (phase-averaged): 0.161918
- Circular phase estimate: 0.131820
- Runtime: 0 days

## Quantum Ensemble Aggregations
### Ensemble 1: TailRisk > 3.0
- Completed runs: 2 (requested 2)
- Ensemble mean amplitude: 0.162920
- Ensemble standard deviation: 0.000938
- Ensemble standard error: 0.000663
- Mean per-run reported std. error: 0.018254
- Mean deviation from analytic: 0.003895
- Circular amplitude (aggregated): 0.161594
- Circular phase (aggregated): 0.131681
- Most frequent outcome across ensemble: 111/128
- Run artifacts: quantum_estimate_run1.json, quantum_estimate_run2.json

## Classical Monte Carlo Results
### Threshold = 2.0
| Precision | Samples Needed | Runtime |
|-----------|----------------|---------|
| 0.1 | 1,000 | 0.000s |
| 0.05 | 1,000 | 0.000s |
| 0.01 | 1,000 | 0.000s |
| 0.005 | 1,900 | 0.000s |
| 0.001 | 47,500 | 0.000s |

### Threshold = 3.0
| Precision | Samples Needed | Runtime |
|-----------|----------------|---------|
| 0.1 | 1,000 | 0.000s |
| 0.05 | 1,000 | 0.000s |
| 0.01 | 1,000 | 0.000s |
| 0.005 | 1,900 | 0.000s |
| 0.001 | 47,500 | 0.000s |

### Threshold = 4.0
| Precision | Samples Needed | Runtime |
|-----------|----------------|---------|
| 0.1 | 1,000 | 0.000s |
| 0.05 | 1,000 | 0.000s |
| 0.01 | 1,000 | 0.000s |
| 0.005 | 1,900 | 0.000s |
| 0.001 | 47,500 | 0.001s |

## Analysis Conclusions
### Quantum Advantage
- **Theoretical**: Quadratic speedup for high-precision estimates
- **Practical**: Advantage emerges at ε < 0.001 precision levels
- **Current Status**: Requires fault-tolerant quantum computers

### Key Insights
1. QAE provides quadratic speedup in precision requirements
2. Resource overhead is significant for near-term quantum devices
3. Classical methods remain competitive for moderate precision
4. Quantum advantage most pronounced for tail risk analysis

### Next Steps
- Implement noise-aware QAE variants
- Optimize state preparation circuits
- Analyze real financial datasets
- Compare with advanced classical methods