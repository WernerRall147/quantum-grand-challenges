# Backend Assumptions - 04_linear_solvers

## Target Architecture
- Primary: `surface_code_generic_v1` (topological surface codes)
- Secondary: `qubit_gate_ns_e3` (gate-based, 1μs gate time, 10⁻³ error rate)

## Circuit Characteristics
- **Qubits**: 6 (1 system + 4 precision + 1 ancilla)
- **Gate set**: Ry, Rz, Rx, H, CNOT, Controlled-R1, SWAP, Measure
- **Algorithm**: HHL with QPE for 2×2 symmetric Poisson system
- **Circuit depth**: O(n² × precision_qubits) for QFT + Hamiltonian simulation

## Connectivity Assumptions
- Linear/nearest-neighbor connectivity sufficient with SWAP routing
- QPE register requires controlled rotations across precision qubits
- Ancilla qubit needs controlled-Ry access from precision register

## Noise Model
- Simulator validation only (no hardware noise characterization yet)
- HHL sensitivity: condition number κ(A) = 1.94 (well-conditioned; noise-tolerant)
- Phase estimation precision limited by 4 precision qubits (16 phase bins)

## Transpilation Notes
- Controlled-R1 gates decompose to CNOT + Rz
- QFT block is standard: H + controlled-phase + SWAP reversal
- Hamiltonian simulation via first-order Trotter (Rz + Rx per time step)

## Azure Quantum Validation
- Resource estimates generated via mock estimator on 2026-03-24
- QASM circuit generation and emulator submission planned as next step
