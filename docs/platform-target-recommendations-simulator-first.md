# Platform Target Recommendations

Generated: 2026-03-10T12:35:21Z

Preference mode: `simulator-first`

Scoring: `5*run_history_successes + 3*smoke_successes - failures + strategy bonus - optional cost/runtime/queue penalties`

## Global Target Summary

| Target | Succeeded Runs |
|---|---:|
| quantinuum.sim.h2-1sc | 21 |
| rigetti.sim.qvm | 2 |

## Per-Problem Recommendation

| Problem | Recommended Target | Confidence |
|---|---|---|
| 01_hubbard | quantinuum.sim.h2-1sc | medium |
| 02_catalysis | quantinuum.sim.h2-1sc | medium |
| 03_qae_risk | rigetti.sim.qvm | medium |
| 04_linear_solvers | quantinuum.sim.h2-1sc | medium |
| 05_qaoa_maxcut | rigetti.sim.qvm | medium |
| 06_high_frequency_trading | quantinuum.sim.h2-1sc | medium |
| 07_drug_discovery | quantinuum.sim.h2-1sc | medium |
| 08_protein_folding | quantinuum.sim.h2-1sc | medium |
| 09_factorization | quantinuum.sim.h2-1sc | medium |
| 10_post_quantum_cryptography | quantinuum.sim.h2-1sc | medium |
| 11_quantum_machine_learning | quantinuum.sim.h2-1sc | medium |
| 12_quantum_optimization | quantinuum.sim.h2-1sc | medium |
| 13_climate_modeling | quantinuum.sim.h2-1sc | medium |
| 14_materials_discovery | quantinuum.sim.h2-1sc | medium |
| 15_database_search | quantinuum.sim.h2-1sc | high |
| 16_error_correction | quantinuum.sim.h2-1sc | medium |
| 17_nuclear_physics | quantinuum.sim.h2-1sc | medium |
| 18_photovoltaics | quantinuum.sim.h2-1sc | medium |
| 19_quantum_chromodynamics | quantinuum.sim.h2-1sc | medium |
| 20_space_mission_planning | quantinuum.sim.h2-1sc | medium |

## Top Candidate Details

### 01_hubbard

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: medium
- Rationale: Highest weighted score (6.98) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (simulator-first).
- Evidence: score=6.9845, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 9.32
- Avg cost usd: 0.0000

### 02_catalysis

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: medium
- Rationale: Highest weighted score (7.00) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (simulator-first).
- Evidence: score=6.9952, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 2.90
- Avg cost usd: 0.0000

### 03_qae_risk

- Recommended target: rigetti.sim.qvm
- Confidence: medium
- Rationale: Highest weighted score (9.99) from run-history successes (1), smoke successes (1), failures (0), and strategy mode (simulator-first).
- Evidence: score=9.9914, run_history=1, smoke=1, failures=0, global=2
- Simulator target: True
- Avg runtime seconds: 1.31
- Avg queue seconds: 3.82
- Avg cost usd: 0.0000
- Input formats: rigetti.quil.v1
- Output formats: rigetti.quil-results.v1

### 04_linear_solvers

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: medium
- Rationale: Highest weighted score (6.99) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (simulator-first).
- Evidence: score=6.9948, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 3.11
- Avg cost usd: 0.0000

### 05_qaoa_maxcut

- Recommended target: rigetti.sim.qvm
- Confidence: medium
- Rationale: Highest weighted score (10.00) from run-history successes (1), smoke successes (1), failures (0), and strategy mode (simulator-first).
- Evidence: score=10.0, run_history=1, smoke=1, failures=0, global=2
- Simulator target: True
- Input formats: rigetti.quil.v1
- Output formats: rigetti.quil-results.v1

### 06_high_frequency_trading

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: medium
- Rationale: Highest weighted score (6.99) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (simulator-first).
- Evidence: score=6.9949, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 3.06
- Avg cost usd: 0.0000

### 07_drug_discovery

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: medium
- Rationale: Highest weighted score (6.99) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (simulator-first).
- Evidence: score=6.9944, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 3.38
- Avg cost usd: 0.0000

### 08_protein_folding

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: medium
- Rationale: Highest weighted score (7.00) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (simulator-first).
- Evidence: score=6.9951, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 2.95
- Avg cost usd: 0.0000

### 09_factorization

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: medium
- Rationale: Highest weighted score (7.00) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (simulator-first).
- Evidence: score=6.9951, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 2.95
- Avg cost usd: 0.0000

### 10_post_quantum_cryptography

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: medium
- Rationale: Highest weighted score (7.00) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (simulator-first).
- Evidence: score=6.9951, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 2.95
- Avg cost usd: 0.0000

### 11_quantum_machine_learning

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: medium
- Rationale: Highest weighted score (6.99) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (simulator-first).
- Evidence: score=6.995, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 3.01
- Avg cost usd: 0.0000

### 12_quantum_optimization

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: medium
- Rationale: Highest weighted score (7.00) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (simulator-first).
- Evidence: score=6.9951, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 2.97
- Avg cost usd: 0.0000

### 13_climate_modeling

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: medium
- Rationale: Highest weighted score (6.99) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (simulator-first).
- Evidence: score=6.9947, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 3.17
- Avg cost usd: 0.0000

### 14_materials_discovery

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: medium
- Rationale: Highest weighted score (6.99) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (simulator-first).
- Evidence: score=6.9936, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 3.82
- Avg cost usd: 0.0000

### 15_database_search

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: high
- Rationale: Highest weighted score (14.99) from run-history successes (2), smoke successes (1), failures (0), and strategy mode (simulator-first).
- Evidence: score=14.9859, run_history=2, smoke=1, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 8.48
- Avg cost usd: 0.0000
- Input formats: honeywell.openqasm.v1
- Output formats: honeywell.quantum-results.v1

### 16_error_correction

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: medium
- Rationale: Highest weighted score (6.99) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (simulator-first).
- Evidence: score=6.9949, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 3.05
- Avg cost usd: 0.0000

### 17_nuclear_physics

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: medium
- Rationale: Highest weighted score (7.00) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (simulator-first).
- Evidence: score=6.9951, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 2.97
- Avg cost usd: 0.0000

### 18_photovoltaics

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: medium
- Rationale: Highest weighted score (6.99) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (simulator-first).
- Evidence: score=6.9949, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 3.04
- Avg cost usd: 0.0000

### 19_quantum_chromodynamics

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: medium
- Rationale: Highest weighted score (7.00) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (simulator-first).
- Evidence: score=6.9951, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True
- Avg runtime seconds: 0.00
- Avg queue seconds: 2.91
- Avg cost usd: 0.0000

### 20_space_mission_planning

- Recommended target: quantinuum.sim.h2-1sc
- Confidence: medium
- Rationale: Highest weighted score (7.00) from run-history successes (1), smoke successes (0), failures (0), and strategy mode (simulator-first).
- Evidence: score=7.0, run_history=1, smoke=0, failures=0, global=21
- Simulator target: True

