# Backend Assumptions - 06_high_frequency_trading

## Target Architecture
- Primary: surface_code_generic_v1 (topological surface codes)
- Secondary: qubit_gate_ns_e3 (gate-based, 1us gate time, 10^-3 error rate)

## Circuit Characteristics
- **Algorithm**: Quantum VaR
- **Qubits**: 3 (market + marker)
- **Gate set**: Ry, X, Controlled-Ry, Controlled-X, M

## Noise Model
- Amplitude encoding sensitive to state prep fidelity
- Simulator validation only; hardware noise characterization pending

## Transpilation Notes
- Gate decomposition targets native sets: {Rz, SX, CNOT} (IBM) or {Rz, Ry, ZZ} (Quantinuum)
- Resource estimates generated via mock estimator on 2026-03-24
