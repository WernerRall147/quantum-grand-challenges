# Backend Assumptions - 20_space_mission_planning

## Target Architecture
- Primary: surface_code_generic_v1 (topological surface codes)
- Secondary: qubit_gate_ns_e3 (gate-based, 1us gate time, 10^-3 error rate)

## Circuit Characteristics
- **Algorithm**: QAOA Trajectory
- **Qubits**: 4 (mission legs)
- **Gate set**: H, CNOT, Rz, Rx, M

## Noise Model
- QAOA depth-1; moderate noise tolerance
- Simulator validation only; hardware noise characterization pending

## Transpilation Notes
- Gate decomposition targets native sets: {Rz, SX, CNOT} (IBM) or {Rz, Ry, ZZ} (Quantinuum)
- Resource estimates generated via mock estimator on 2026-03-24
