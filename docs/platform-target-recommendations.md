# Platform Target Recommendations

Generated: 2026-03-10T12:35:20Z

Preference mode: `balanced`

Scoring: `5*run_history_successes + 3*smoke_successes - failures + strategy bonus - optional cost/runtime/queue penalties`

## Global Target Summary

| Target | Succeeded Runs |
|---|---:|
| quantinuum.sim.h2-1sc | 21 |
| rigetti.sim.qvm | 2 |

## Per-Problem Recommendation

| Problem | Recommended Target | Confidence |
|---|---|---|
| 01_hubbard | quantinuum.sim.h2-1sc | low |
| 02_catalysis | quantinuum.sim.h2-1sc | low |
| 03_qae_risk | rigetti.sim.qvm | medium |
| 04_linear_solvers | quantinuum.sim.h2-1sc | low |
| 05_qaoa_maxcut | rigetti.sim.qvm | medium |
| 06_high_frequency_trading | quantinuum.sim.h2-1sc | low |
| 07_drug_discovery | quantinuum.sim.h2-1sc | low |
| 08_protein_folding | quantinuum.sim.h2-1sc | low |
| 09_factorization | quantinuum.sim.h2-1sc | low |
| 10_post_quantum_cryptography | quantinuum.sim.h2-1sc | low |
| 11_quantum_machine_learning | quantinuum.sim.h2-1sc | low |
| 12_quantum_optimization | quantinuum.sim.h2-1sc | low |
| 13_climate_modeling | quantinuum.sim.h2-1sc | low |
| 14_materials_discovery | quantinuum.sim.h2-1sc | low |
| 15_database_search | quantinuum.sim.h2-1sc | high |
| 16_error_correction | quantinuum.sim.h2-1sc | low |
| 17_nuclear_physics | quantinuum.sim.h2-1sc | low |
| 18_photovoltaics | quantinuum.sim.h2-1sc | low |
| 19_quantum_chromodynamics | quantinuum.sim.h2-1sc | low |
| 20_space_mission_planning | quantinuum.sim.h2-1sc | low |

## Top Candidate Details

### 01_hubbard

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: low
- Rationale: Highest weighted score (4.98) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (balanced).
- Evidence: score=4.9845, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 9.32
- Avg cost usd: 0.0000

### 02_catalysis

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: low
- Rationale: Highest weighted score (5.00) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (balanced).
- Evidence: score=4.9952, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 2.90
- Avg cost usd: 0.0000

### 03_qae_risk

- Recommended target: rigetti.sim.qvm
- Confidence: medium
- Rationale: Highest weighted score (7.99) from run-history successes (1), smoke successes (1), failures (0), and strategy mode (balanced).
- Evidence: score=7.9914, run_history=1, smoke=1, failures=0, global=2
- Simulator target: True
- Avg runtime seconds: 1.31
- Avg queue seconds: 3.82
- Avg cost usd: 0.0000
- Input formats: rigetti.quil.v1
- Output formats: rigetti.quil-results.v1

### 04_linear_solvers

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: low
- Rationale: Highest weighted score (4.99) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (balanced).
- Evidence: score=4.9948, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 3.11
- Avg cost usd: 0.0000

### 05_qaoa_maxcut

- Recommended target: rigetti.sim.qvm
- Confidence: medium
- Rationale: Highest weighted score (8.00) from run-history successes (1), smoke successes (1), failures (0), and strategy mode (balanced).
- Evidence: score=8.0, run_history=1, smoke=1, failures=0, global=2
- Simulator target: True
- Input formats: rigetti.quil.v1
- Output formats: rigetti.quil-results.v1

### 06_high_frequency_trading

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: low
- Rationale: Highest weighted score (4.99) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (balanced).
- Evidence: score=4.9949, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 3.06
- Avg cost usd: 0.0000

### 07_drug_discovery

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: low
- Rationale: Highest weighted score (4.99) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (balanced).
- Evidence: score=4.9944, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 3.38
- Avg cost usd: 0.0000

### 08_protein_folding

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: low
- Rationale: Highest weighted score (5.00) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (balanced).
- Evidence: score=4.9951, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 2.95
- Avg cost usd: 0.0000

### 09_factorization

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: low
- Rationale: Highest weighted score (5.00) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (balanced).
- Evidence: score=4.9951, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 2.95
- Avg cost usd: 0.0000

### 10_post_quantum_cryptography

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: low
- Rationale: Highest weighted score (5.00) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (balanced).
- Evidence: score=4.9951, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 2.95
- Avg cost usd: 0.0000

### 11_quantum_machine_learning

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: low
- Rationale: Highest weighted score (4.99) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (balanced).
- Evidence: score=4.995, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 3.01
- Avg cost usd: 0.0000

### 12_quantum_optimization

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: low
- Rationale: Highest weighted score (5.00) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (balanced).
- Evidence: score=4.9951, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 2.97
- Avg cost usd: 0.0000

### 13_climate_modeling

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: low
- Rationale: Highest weighted score (4.99) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (balanced).
- Evidence: score=4.9947, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 3.17
- Avg cost usd: 0.0000

### 14_materials_discovery

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: low
- Rationale: Highest weighted score (4.99) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (balanced).
- Evidence: score=4.9936, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 3.82
- Avg cost usd: 0.0000

### 15_database_search

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: high
- Rationale: Highest weighted score (12.99) from run-history successes (2), smoke successes (1), failures (0), and strategy mode (balanced).
- Evidence: score=12.9859, run_history=2, smoke=1, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 8.48
- Avg cost usd: 0.0000
- Input formats: honeywell.openqasm.v1
- Output formats: honeywell.quantum-results.v1

### 16_error_correction

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: low
- Rationale: Highest weighted score (4.99) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (balanced).
- Evidence: score=4.9949, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 3.05
- Avg cost usd: 0.0000

### 17_nuclear_physics

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: low
- Rationale: Highest weighted score (5.00) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (balanced).
- Evidence: score=4.9951, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 2.97
- Avg cost usd: 0.0000

### 18_photovoltaics

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: low
- Rationale: Highest weighted score (4.99) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (balanced).
- Evidence: score=4.9949, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 3.04
- Avg cost usd: 0.0000

### 19_quantum_chromodynamics

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: low
- Rationale: Highest weighted score (5.00) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (balanced).
- Evidence: score=4.9951, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 2.91
- Avg cost usd: 0.0000

### 20_space_mission_planning

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: low
- Rationale: Highest weighted score (5.00) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (balanced).
- Evidence: score=5.0, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True

