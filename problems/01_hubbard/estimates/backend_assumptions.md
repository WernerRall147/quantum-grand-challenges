# Backend Assumptions - 01_hubbard

## Target Architecture
- Primary: `surface_code_generic_v1` (topological surface codes)
- Secondary: `qubit_gate_ns_e3` (gate-based, 1μs gate time, 10⁻³ error rate)

## Circuit Characteristics
- **Qubits**: 2 (two-site Hubbard model)
- **Gate set**: X, Ry, Rz, CNOT, H, S, Measure
- **Circuit depth**: O(shots × Pauli terms) — 4 Pauli measurement bases per energy evaluation
- **Measurement**: Shot-based Pauli expectation values (XX, YY, ZI, IZ)

## Connectivity Assumptions
- All-to-all connectivity assumed (2 qubits require no routing overhead)
- No SWAP insertion needed for the current problem size

## Noise Model
- Simulator validation only (no hardware noise characterization yet)
- VQE is inherently noise-resilient due to variational optimization
- Expected depolarizing noise tolerance: moderate (short circuit depth)

## Transpilation Notes
- Native gate set: {Rz, SX, CNOT} on IBM-style backends; {Rz, Ry, ZZ} on Quantinuum
- Ry gates decompose directly; CNOT is native on both platforms
- No non-Clifford overhead beyond Rz/Ry rotations

## Azure Quantum Validation
- VQE ansatz (ZZ and XX basis) submitted to `quantinuum.sim.h2-1sc` on 2026-03-24
- Full emulator runs queued on `quantinuum.sim.h2-1e`
