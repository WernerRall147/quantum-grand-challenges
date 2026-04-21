# Backend Assumptions - 11_quantum_machine_learning

## Target Architecture
- Primary: surface_code_generic_v1 (topological surface codes)
- Secondary: qubit_gate_ns_e3 (gate-based, 1us gate time, 10^-3 error rate)

## Circuit Characteristics
- **Algorithm**: Swap Test Kernel
- **Qubits**: 5 (ancilla + 2x2 registers)
- **Gate set**: H, Ry, Controlled-Ry, Controlled-SWAP, M

## Noise Model
- Swap test robust to moderate noise
- Simulator validation only; hardware noise characterization pending

## Transpilation Notes
- Gate decomposition targets native sets: {Rz, SX, CNOT} (IBM) or {Rz, Ry, ZZ} (Quantinuum)
- Resource estimates generated via mock estimator on 2026-03-24
