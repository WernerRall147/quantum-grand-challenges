# QAOA Backend, Transpilation, and Connectivity Assumptions

This document records the backend and transpilation assumptions used for reported QAOA Max-Cut results in this folder.

## Execution Modes

| Mode | Backend | Purpose | Evidence Inputs |
|---|---|---|---|
| Runtime simulation | QDK full-state simulator via `QuantumSimulator` | Generate trial statistics and uncertainty-bounded QAOA metrics | `quantum_baseline_*_d*.json`, `depth_sweep_*.json`, `noise_sweep_*_d*.json` |
| Resource estimation | Azure Quantum Resource Estimator targets (`surface_code_generic_v1`, `qubit_gate_ns_e3`) | Hardware-oriented resource profiling from parameterized QAOA payloads | `estimator_params_*_d*.json`, `estimator_profile_summary.md` |

## Circuit and Gate Assumptions

- QAOA ansatz uses alternating cost and mixer layers in `qsharp/Program.qs`.
- Cost layer uses `Exp([PauliZ, PauliZ], ...)` over weighted graph edges.
- Mixer layer uses single-qubit `Rx` rotations.
- Reported depth values correspond to `p = depth` layers in `RunQaoaAnalysis`.

## Connectivity and Mapping Assumptions

- Runtime evidence is produced on an ideal simulator with no explicit hardware coupling-map constraints.
- Logical edge interactions are directly expressed by ZZ exponentials on qubit pairs; no explicit SWAP insertion is modeled in runtime artifacts.
- Hardware connectivity overhead is therefore not represented in `quantum_baseline_*`, `depth_sweep_*`, or `noise_sweep_*` runtime values.

## Transpilation Assumptions

- No backend-specific transpilation report is produced for runtime simulator outputs.
- Hardware compilation/decomposition impacts are approximated through estimator targets, not through calibrated device transpilation logs.
- Estimator runs consume parameterized problem payloads prepared by `python/prepare_estimator_params.py` and executed by `tooling/estimator/run_estimation.py`.

## Noise and Measurement Assumptions

- Runtime trial statistics in `quantum_baseline_*_d*.json` are simulator-based and do not include calibrated hardware noise.
- Readout sensitivity evidence is approximated with an independent bit-flip proxy in `python/noise_sweep.py` over `RefinedAssignment` samples.
- Noise sweep outputs (`noise_sweep_*_d*.{json,md}`) are therefore stress tests, not hardware-calibrated error bars.

## Reproducibility References

- QAOA algorithm and coordinate search: `qsharp/Program.qs`
- Host runtime driver and report schema: `host/Program.cs`
- Estimator payload preparation: `python/prepare_estimator_params.py`
- Estimator orchestration: `tooling/estimator/run_estimation.py`
- Depth evidence: `estimates/depth_sweep_small.md`, `estimates/depth_sweep_medium.md`, `estimates/depth_sweep_large.md`
- Noise evidence: `estimates/noise_sweep_small_d3.md`, `estimates/noise_sweep_medium_d2.md`, `estimates/noise_sweep_large_d2.md`

## Known Gaps for Stage C to D

- Add backend-specific transpilation artifacts (native gate counts, routing overhead, depth inflation) from at least one concrete hardware topology model.
- Add calibrated readout and two-qubit error assumptions tied to a concrete backend profile.
- Add connectivity-aware sensitivity sweeps that include explicit routing assumptions.
