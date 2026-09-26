# Backend Assumptions - 06_high_frequency_trading

## Target Architecture
- Primary: surface_code_generic_v1 (topological surface codes)
- Secondary: qubit_gate_ns_e3 (gate-based, 1us gate time, 10^-3 error rate)

## Circuit Characteristics
- **Algorithm**: Loss-probability sampling (direct measurement of a marker; no amplitude estimation)
- **Qubits**: 3 (market + marker)
- **Gate set**: Ry, X, Controlled-Ry, Controlled-X, M

## Noise Model
- Amplitude encoding sensitive to state prep fidelity
- Simulator validation only; hardware noise characterization pending

## Transpilation Notes
- Gate decomposition targets native sets: {Rz, SX, CNOT} (IBM) or {Rz, Ry, ZZ} (Quantinuum)
- The March 2026 `latest_*.json` files came from a mock estimator path; the resource estimate is `circuits/estimate.json`
