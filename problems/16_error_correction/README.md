# Problem 16 · Quantum Error Correction

## Overview

Fault-tolerant quantum computing demands error correction codes that suppress noisy qubit failures faster than they accumulate. This scaffold supplies a reproducible classical baseline for repetition-code style logical error analysis while standing up a Q# project that will ultimately host stabilizer simulations and surface-code primitives. By comparing physical error rates against logical failure probabilities we track where quantum error correction (QEC) begins to pay off.

## Directory Layout

```text
16_error_correction/
├── estimates/                       # JSON artifacts from classical / quantum workflows
├── instances/                       # Code distances and physical error-rate sweeps
├── plots/                           # Generated figures from analyze.py
├── python/
│   ├── classical_baseline.py        # Analytical repetition-code logical error model
│   └── analyze.py                   # Visualization of suppression factors and pseudo-thresholds
└── qsharp/
    ├── qsharp.json            # Modern QDK project file
    └── Program.qs                   # Stubbed quantum workflow
```

## Quick Start

```bash
cd problems/16_error_correction

# Classical logical error analysis
python python/classical_baseline.py

# Plot logical error curves and suppression heatmaps
python python/analyze.py

# Quantum placeholder (uses modern QDK  qsharp Python package)
python -c "import qsharp; qsharp.init(project_root='qsharp'); print('Build OK')"
 python tooling/run_all_qsharp.py  # runs via qsharp Python package
```

## What the Baseline Computes

`python/classical_baseline.py` flips each of the `code_distance` data bits independently with probability p in each of `measurement_rounds` rounds, applies no correction between rounds, and takes one majority vote at the end, with perfect measurements. It folds the rounds into `effective_p = 1 - (1 - p)^rounds`, the probability that a bit flips at least once. Two flips on one bit cancel, so the probability that a bit ends up flipped is (1 - (1 - 2p)^rounds)/2, which is smaller when there is more than one round. The logical errors in `estimates/classical_baseline.json` and `plots/` are therefore exact for instances with one round and upper bounds, within 2% of the exact value of the same model, for instances with more; the suppression factors are correspondingly lower bounds. `python/test_baseline.py` checks both against the exact model. `pseudo_threshold` is the smallest swept physical error rate at which the logical error is at or below it, not the crossing point the name usually means. A `bias` other than 1.0 applies a heuristic weighting, not a noise model. The model has no syndrome extraction and no measurement errors, so it does not describe a repetition-code memory experiment.

## Next Quantum Milestones

1. **Stabilizer Simulation** – Implement syndrome extraction cycles for repetition or surface codes.
2. **Decoder Integration** – Explore minimum-weight matching or belief propagation within Q#.
3. **Resource Accounting** – Track qubit counts, circuit depth, and ancilla demand per cycle.
4. **Fault-Tolerant Benchmarks** – Compare logical error suppression across physical noise models.

This scaffold keeps the analytical QEC baseline reproducible while we build toward full stabilizer simulations in Q#. 🛡️⚛️

## Objective Maturity Gate

- **Current gate**: **Stage C complete** (hardware-aware validation evidence in place: 3-qubit repetition code runnable, calibration ensemble across runs, backend assumptions documented, dual-model estimator profile, OpenQASM export, real Azure resource estimate captured).
- **Next gate target**: Maintenance  QEC is infrastructure not application; track surface-code/QLDPC roadmap rather than escalate the claim.

Stage C evidence references for this problem:

- Calibration ensemble: `estimates/quantum_calibration_ensemble.json` and `estimates/calibration_evidence.json`.
- Backend assumptions: `estimates/backend_assumptions.md`.
- Estimator profile (ns-e3 + surface-code-generic): `estimates/estimator_profile_summary.md`, `estimates/latest_qubit_gate_ns_e3.json`, `estimates/latest_surface_code_generic_v1.json`.
- Real Azure resource estimate: `estimates/real_resource_estimate_2026-03-25T091444Z.json`.
- Cross-platform OpenQASM export: `estimates/repetition_code_3q.qasm`.
- Azure smoke validation: `estimates/azure_smoke_report_small_d1.md`, `estimates/azure_job_manifest_small_d1.json`.

## DiVincenzo Readiness (Stage C/D Overlay)

| Criterion | Status | Evidence / Notes |
|---|---|---|
| Scalable qubit system | partial | Problem-scoped instance baselines are in place; full hardware-scale projections are tracked as Stage C work. |
| Initialization | partial | Input/state initialization path is defined for current workflows, with backend-ready loading fidelity still to be hardened. |
| Coherence vs gate time | not-yet | Backend-calibrated coherence-vs-depth evidence is pending and required for Stage C/D promotion. |
| Universal gate set | partial | Q# scaffold/build path exists; gate-basis decomposition and transpilation evidence remain Stage C tasks. |
| Qubit-specific measurement | partial | Measurement outputs are defined for current validation flows; hardware readout characterization is pending. |
## Advantage Claim Contract

- **Claim category (current)**: `theoretical`.
- **Problem class and regime**: Problem-specific challenge instances defined in this directory.
- **Fair baseline**: Problem-local classical baseline in `python/` outputs.
- **Quantum resource scaling claim**: Expected asymptotic advantage depends on algorithm family and implementation assumptions; no hardware-demonstrated speedup claim yet.
- **Data-loading and I/O assumptions**: Must be documented alongside future advantage claims.
- **Noise/error model assumptions**: Backend-specific model and calibration assumptions to be added at Stage C.
- **Confidence/uncertainty method**: To be reported using shot-based confidence intervals or equivalent statistical bounds.
- **Residual risks**: Oracle/state-preparation/transpilation overhead may dominate for near-term instance sizes.
