# Backend Assumptions - 09_factorization

## Target Architecture
- Primary: surface_code_generic_v1 (topological surface codes)
- Secondary: qubit_gate_ns_e3 (gate-based, 1us gate time, 10^-3 error rate)

## Circuit Characteristics
- **Algorithm**: Shor Period-Finding
- **Qubits**: 8 (4 counting + 4 work)
- **Gate set**: H, SWAP, Controlled-SWAP, R1, X, M

## Noise Model
- Deep QPE circuit; sensitive to phase errors
- Simulator validation only; hardware noise characterization pending

## Transpilation Notes
- Gate decomposition targets native sets: {Rz, SX, CNOT} (IBM) or {Rz, Ry, ZZ} (Quantinuum)
- Resource estimates generated via mock estimator on 2026-03-24
