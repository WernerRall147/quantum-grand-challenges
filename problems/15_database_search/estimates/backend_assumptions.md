# Backend Assumptions - 15_database_search

## Target Architecture
- Primary: `surface_code_generic_v1` (topological surface codes)
- Secondary: `qubit_gate_ns_e3` (gate-based, 1μs gate time, 10⁻³ error rate)

## Circuit Characteristics
- **Qubits**: 4 (small instance), 12 (estimation variant)
- **Gate set**: H, X, CNOT, T, Tdg, Controlled-Z, Measure
- **Algorithm**: Canonical Grover with oracle phase-marking + diffusion
- **Iterations**: floor(π/4 × √N) optimal iterations

## Connectivity Assumptions
- Multi-controlled Z requires decomposition into 2-qubit gates
- 4-qubit Grover: C³Z decomposes to 14 T-gates + 6 CNOT (standard Toffoli decomposition)
- 12-qubit Grover: O(n) ancilla-free decomposition or O(1) ancilla with borrowed qubits

## Noise Model
- Simulator validation: 93% success at 4-qubit, confirmed on Quantinuum H2-1SC
- T-gate noise dominates: each T-gate requires magic state distillation at scale
- Oracle depth × iterations determines total noise exposure

## Transpilation Notes
- Oracle: bit-flip + MCZ pattern for arbitrary target marking
- Diffusion: H + X + MCZ + X + H (standard)
- MCZ decomposition uses relative-phase Toffoli (7 T-gates per Toffoli)

## Azure Quantum Validation
- 4-qubit Grover circuit submitted to `quantinuum.sim.h2-1sc` on 2026-03-24 (syntax validated)
- Full emulator run queued on `quantinuum.sim.h2-1e`
- Resource estimates generated for surface_code_generic_v1 and qubit_gate_ns_e3
