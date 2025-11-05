# Quantum Algorithm Visualization Dashboard

This directory contains comprehensive visualizations comparing the three major quantum algorithms implemented in the Quantum Grand Challenges repository: **VQE**, **HHL**, and **QAE**.

## Quick Start

```bash
# Generate all visualizations
python generate_comparison_plots.py

# View plots in plots/ directory
```

## Prerequisites

```bash
pip install matplotlib numpy seaborn
```

## Generated Visualizations

### 1. Physical Qubit Comparison (`qubit_comparison.png`)
- **Left Panel**: Bar chart showing physical qubit requirements for each algorithm
  - VQE: 48.5k-110k qubits (mean: 79.3k)
  - HHL: 18.7k qubits (baseline, most efficient)
  - QAE: 594k qubits (31.8× more than HHL)
- **Right Panel**: Pie chart showing qubit allocation breakdown
  - Demonstrates that 93-97% of qubits are dedicated to T-state factories
  - Only 3-7% used for algorithm execution

**Key Insight**: T-state distillation dominates hardware requirements for all algorithms.

### 2. Runtime Comparison (`runtime_comparison.png`)
- Log-scale bar chart comparing algorithm execution times
  - VQE: 47-182 microseconds (fastest)
  - HHL: 52 milliseconds (454× slower than VQE)
  - QAE: 6.4 seconds (123× slower than HHL)
- Includes speedup annotations showing relative performance
- Demonstrates 3 orders of magnitude range across algorithms

**Key Insight**: VQE's shallow circuits enable microsecond execution, while QAE's deep circuits (838k logical cycles) require seconds.

### 3. T-State Comparison (`tstate_comparison.png`)
- **Left Panel**: Total T-state requirements on log scale
  - VQE: 1,596 T-states (minimal)
  - HHL: 185k T-states (116× more than VQE)
  - QAE: 965k T-states (5.2× more than HHL)
- **Right Panel**: Stacked bar chart showing T-state breakdown by source
  - Direct T-gates: <1% for all algorithms
  - Rotation gates: 76-99% (dominant cost)
  - CCZ gates: 0-24% (QAE only)

**Key Insight**: Rotation gate synthesis dominates T-state consumption (20 T-states per rotation).

### 4. Scaling Analysis (`scaling_analysis.png`)
Four subplots showing how each algorithm scales with problem size:

- **Top Left**: VQE scaling with number of Hubbard model sites
  - Linear scaling: ~5k qubits per site
  - 50 sites → 250k qubits
  
- **Top Right**: HHL scaling with system size N
  - Logarithmic scaling: ~5k × log₂(N) qubits
  - N=1024 → 50k qubits
  
- **Bottom Left**: QAE scaling with loss qubits
  - Exponential scaling: ~20k × 2^(n/4) qubits
  - 16 loss qubits → 40M qubits (exponential barrier)
  
- **Bottom Right**: Combined runtime comparison
  - Shows all three algorithms on same log-scale plot
  - Demonstrates different scaling behaviors

**Key Insight**: QAE's exponential scaling in physical qubits limits practical problem sizes to 8-12 loss qubits.

### 5. Quantum Advantage Assessment (`quantum_advantage_map.png`)
Heatmap evaluating each algorithm across six criteria:

| Criterion | VQE | HHL | QAE |
|-----------|-----|-----|-----|
| Qubit Efficiency | Good | Excellent | Poor |
| Runtime Speed | Excellent | Good | Poor |
| Error Tolerance | Excellent | Fair | Fair |
| Near-term Viability (2027-2029) | Fair | Excellent | Poor |
| Scalability | Good | Very Good | Fair |
| Classical Advantage Threshold | Good | Very Good | Excellent |

**Key Insights**:
- **HHL** wins on near-term viability (ready by 2027-2029)
- **VQE** wins on runtime and error tolerance
- **QAE** wins on quantum advantage potential (quadratic speedup)

### 6. Technology Timeline (`technology_timeline.png`)
Roadmap showing when each algorithm becomes practical:

```
2025 ──────► 2027 ──────► 2030 ──────► 2033 ──────► 2035+
  │            │            │            │            │
NISQ Era    HHL Ready   VQE Ready   QAE Ready    Full FT-QC
~1k qubits  ~50k qubits ~100k qubits ~1M qubits  ~10M qubits
```

- **2027-2029**: HHL becomes practical (18.7k qubits)
- **2028-2030**: VQE becomes practical (100k qubits)
- **2033-2035**: QAE becomes practical (594k qubits)

**Key Insight**: 6-8 year wait before QAE reaches practical deployment, vs. 2-3 years for HHL.

## Interpretation Guide

### Physical Qubit Requirements
- **HHL is the most efficient** at 18.7k qubits
- **QAE requires 31.8× more qubits** than HHL due to:
  - 36.9k rotation gates (vs. 12.2k for HHL)
  - 56.8k CCZ gates (vs. 0 for HHL)
  - Deep circuit depth (838k vs. 17k logical cycles)

### Runtime Analysis
- **VQE is fastest** (microseconds) due to shallow circuits
- **QAE is slowest** (seconds) due to:
  - Quantum phase estimation with controlled Grover^(2^k) powers
  - 838k logical cycles vs. 17k for HHL
  - Statistical averaging over 20 repetitions

### T-State Economy
- **Rotation synthesis dominates** (20 T-states per rotation)
- **QAE's 36.9k rotations** require 738k T-states (76% of total)
- **CCZ gates** add 227k T-states (24% of total) for QAE only
- **Direct T-gates** are negligible (<1%) for all algorithms

### Quantum Advantage
Each algorithm has distinct advantage regimes:

**VQE**:
- ✅ Advantage for 20+ site systems (classical: infeasible)
- ✅ Error-resilient (variational optimization)
- ❌ Needs many iterations (reduces practical speedup)

**HHL**:
- ✅ Advantage for N > 10^4, κ < 100, ε < 0.01
- ✅ Exponential speedup over Gaussian elimination
- ❌ Requires well-conditioned systems (κ constraint)

**QAE**:
- ✅ Quadratic speedup over Monte Carlo (O(1/ε) vs O(1/ε²))
- ✅ Best for rare events (P < 1%)
- ❌ Requires massive hardware (594k qubits)
- ❌ State preparation bottleneck (exponential in qubits)

## Algorithm Selection Decision Tree

```
Need energy minimization?
├─ Yes → VQE (2028-2030, 100k qubits)
└─ No
    └─ Need to solve linear systems?
        ├─ Yes → HHL (2027-2029, 18.7k qubits)
        └─ No
            └─ Need probability estimation?
                ├─ Yes → QAE (2033-2035, 594k qubits)
                └─ No → Consider other quantum algorithms
```

## Cross-Algorithm Insights

### 1. T-State Factories are the Bottleneck
- **93-97% of qubits** dedicated to T-state production
- **Hardware optimization** should focus on:
  - Faster T-state distillation (currently 95-111μs per T-state)
  - Higher fidelity T-gates (reduce distillation rounds)
  - Parallel factory architectures (already 2-17 factories)

### 2. Rotation Gates Dominate Costs
- **Synthesis cost**: 20 T-states per arbitrary rotation
- **Optimization opportunities**:
  - Circuit compilation to reduce rotation count
  - Approximate rotation synthesis (trade accuracy for cost)
  - Gate teleportation patterns

### 3. Error Correction Overhead
- **Code distances**: 9 (VQE) to 19 (QAE)
- **Logical error rates**: 3e-10 (VQE) to 3e-12 (HHL/QAE)
- **Implication**: High-precision algorithms pay 2-4× overhead in code distance

### 4. Circuit Depth vs. Qubit Count Tradeoff
- **VQE**: Shallow circuits (low T-states) but many iterations → medium qubits
- **HHL**: Medium depth (moderate T-states) → low qubits (most efficient)
- **QAE**: Deep circuits (high T-states) → high qubits (least efficient)

## Data Sources

All visualizations are based on Azure Quantum Resource Estimator results:
- **VQE**: `problems/01_hubbard/VQE_IMPLEMENTATION_SUMMARY.md`
- **HHL**: `problems/01_hubbard/HHL_IMPLEMENTATION_SUMMARY.md`
- **QAE**: `problems/03_qae_risk/QAE_IMPLEMENTATION_SUMMARY.md`

Resource estimation parameters:
- **Error budget**: 0.001 for all algorithms
- **Architecture**: gate_ns_e3 (superconducting qubits, 1e-3 error rate)
- **Error correction**: Surface code with distance optimization
- **Estimation date**: November 2025

## Updating Visualizations

To regenerate plots with updated data:

1. Edit resource values in `generate_comparison_plots.py`:
   ```python
   physical_qubits = [79_250, 18_700, 594_000]
   runtime_us = [114.5, 52_000, 6_400_000]
   t_states = [1_596, 185_000, 965_000]
   ```

2. Run the script:
   ```bash
   python generate_comparison_plots.py
   ```

3. Plots are saved to `plots/` directory

## Integration with Repository

These visualizations support the repository's goals:
- **Documentation**: Visual summary for README and presentations
- **Analysis**: Resource requirement comparisons for hardware planning
- **Education**: Clear visualization of quantum algorithm tradeoffs
- **Research**: Scaling predictions for future problem instances

## Future Enhancements

Potential additions to the dashboard:
- [ ] Interactive plots (Plotly/Bokeh)
- [ ] 3D surface plots for multi-parameter scaling
- [ ] Animated timeline showing hardware evolution
- [ ] Cost-benefit analysis charts ($/qubit × runtime)
- [ ] Error rate sensitivity analysis
- [ ] Comparison with classical algorithms (runtime, energy)

## References

- Azure Quantum Resource Estimator: https://learn.microsoft.com/azure/quantum/
- Surface Code Error Correction: Nielsen & Chuang, Chapter 10
- T-State Distillation: arXiv:1209.2426
- Quantum Algorithm Zoo: https://quantumalgorithmzoo.org/

---

*Dashboard created: November 2025*  
*Last updated: November 6, 2025*  
*Tools: Python 3.11, Matplotlib 3.8, Seaborn 0.13*
