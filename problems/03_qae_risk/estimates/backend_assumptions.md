# Backend Assumptions - 03_qae_risk

## Target Architecture
- Primary: surface_code_generic_v1 (topological surface codes)
- Secondary: qubit_gate_ns_e3 (gate-based, 1us gate time, 10^-3 error rate)

## Circuit Characteristics
- **Algorithm**: Canonical QAE
- **Qubits**: 11 (loss + precision + marker)
- **Gate set**: H, Ry, X, Controlled-X, Z, R1, SWAP, M

## Noise Model
- Deep circuit; requires error correction at scale
- Simulator validation only; hardware noise characterization pending

## Transpilation Notes
- Gate decomposition targets native sets: {Rz, SX, CNOT} (IBM) or {Rz, Ry, ZZ} (Quantinuum)
- Resource estimates generated via mock estimator on 2026-03-24
