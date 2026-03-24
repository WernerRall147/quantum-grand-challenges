# Backend Assumptions - 18_photovoltaics

## Target Architecture
- Primary: surface_code_generic_v1 (topological surface codes)
- Secondary: qubit_gate_ns_e3 (gate-based, 1us gate time, 10^-3 error rate)

## Circuit Characteristics
- **Algorithm**: Quantum Walk
- **Qubits**: 3 (coin + 2 position)
- **Gate set**: Ry, X, Controlled-SWAP, M

## Noise Model
- Walk fidelity degrades with steps
- Simulator validation only; hardware noise characterization pending

## Transpilation Notes
- Gate decomposition targets native sets: {Rz, SX, CNOT} (IBM) or {Rz, Ry, ZZ} (Quantinuum)
- Resource estimates generated via mock estimator on 2026-03-24
