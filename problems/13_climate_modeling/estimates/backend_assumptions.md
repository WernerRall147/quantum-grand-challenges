# Backend Assumptions - 13_climate_modeling

## Target Architecture
- Primary: surface_code_generic_v1 (topological surface codes)
- Secondary: qubit_gate_ns_e3 (gate-based, 1us gate time, 10^-3 error rate)

## Circuit Characteristics
- **Algorithm**: HHL Diffusion
- **Qubits**: 6 (precision + system + ancilla)
- **Gate set**: H, Ry, Rz, Rx, Controlled-Rz, R1, SWAP, M

## Noise Model
- Phase estimation sensitive to coherence
- Simulator validation only; hardware noise characterization pending

## Transpilation Notes
- Gate decomposition targets native sets: {Rz, SX, CNOT} (IBM) or {Rz, Ry, ZZ} (Quantinuum)
- Resource estimates generated via mock estimator on 2026-03-24
