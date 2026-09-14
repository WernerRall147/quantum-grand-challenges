# Backend Assumptions - 16_error_correction

## Target Architecture
- Primary: surface_code_generic_v1 (topological surface codes)
- Secondary: qubit_gate_ns_e3 (gate-based, 1us gate time, 10^-3 error rate)

## Circuit Characteristics
- **Algorithm**: Repetition Code
- **Qubits**: 5 (3 code + 2 syndrome)
- **Gate set**: X, CNOT, M

## Noise Model
- Clifford-only; error threshold demonstration
- Simulator validation only; hardware noise characterization pending

## Transpilation Notes
- Gate decomposition targets native sets: {Rz, SX, CNOT} (IBM) or {Rz, Ry, ZZ} (Quantinuum)
- Resource estimates generated with the QDK Resource Estimator (qdk 1.31.0, qubit_gate_ns_e3 + surface_code) on 2026-09-14
