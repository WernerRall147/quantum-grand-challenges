# Backend Assumptions - 17_nuclear_physics

## Target Architecture
- Primary: surface_code_generic_v1 (topological surface codes)
- Secondary: qubit_gate_ns_e3 (gate-based, 1us gate time, 10^-3 error rate)

## Circuit Characteristics
- **Algorithm**: VQE Deuteron
- **Qubits**: 2 (nucleon model)
- **Gate set**: X, Ry, Rz, CNOT, Measure

## Noise Model
- VQE is noise-resilient; short circuit depth
- Simulator validation only; hardware noise characterization pending

## Transpilation Notes
- Gate decomposition targets native sets: {Rz, SX, CNOT} (IBM) or {Rz, Ry, ZZ} (Quantinuum)
- Resource estimates generated via mock estimator on 2026-03-24
