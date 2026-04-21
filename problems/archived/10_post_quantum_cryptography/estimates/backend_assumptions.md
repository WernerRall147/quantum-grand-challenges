# Backend Assumptions - 10_post_quantum_cryptography

## Target Architecture
- Primary: surface_code_generic_v1 (topological surface codes)
- Secondary: qubit_gate_ns_e3 (gate-based, 1us gate time, 10^-3 error rate)

## Circuit Characteristics
- **Algorithm**: Grover Key Search
- **Qubits**: 3-5 (keyspace)
- **Gate set**: H, X, Controlled-Z, M

## Noise Model
- Oracle depth x iterations; T-gate noise dominates
- Simulator validation only; hardware noise characterization pending

## Transpilation Notes
- Gate decomposition targets native sets: {Rz, SX, CNOT} (IBM) or {Rz, Ry, ZZ} (Quantinuum)
- Resource estimates generated via mock estimator on 2026-03-24
