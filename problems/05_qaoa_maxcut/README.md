# 05. QAOA for Max-Cut

This problem prepares the groundwork for implementing the Quantum Approximate Optimization Algorithm on weighted Max-Cut instances. The current milestone provides deterministic classical baselines, representative graph instances, and a working depth-1 QAOA circuit with a coarse parameter sweep.

## Roadmap

- [x] Scaffold directory structure, utilities, and helper scripts
- [x] Provide classical brute-force baseline with summary statistics
- [x] Add parameterized graph instances (small/medium/large)
- [x] Generate diagnostic plots for cut values
- [x] Implement depth-1 QAOA circuit with coarse parameter sweep
- [x] Generalize QAOA driver to consume YAML instances dynamically
- [x] Add uncertainty-bounded multi-trial QAOA reporting to `estimates/`
- [ ] Route optimized parameters into the resource estimator profiles

## Quickstart

```bash
cd problems/05_qaoa_maxcut
make classical      # Exhaustive search baseline for each YAML graph instance
make analyze        # Generate plots summarizing best cut values
make build          # Build the Q# project (requires .NET 6.0 runtime)
make run            # Run depth-1 QAOA with multi-trial uncertainty summary + JSON output
make run-all        # Run depth-1 QAOA for small/medium/large and write quantum artifacts
make evidence       # One-shot refresh: classical baseline + quantum runs + plots + markdown summary
```

If `make` is unavailable on Windows PowerShell, run the equivalent sequence directly:

```powershell
dotnet build host/QaoaMaxCut.Driver.csproj --configuration Release
python python/classical_baseline.py
dotnet run --project host/QaoaMaxCut.Driver.csproj -- --instance small --depth 1 --coarse-shots 24 --refined-shots 96 --trials 6
dotnet run --project host/QaoaMaxCut.Driver.csproj -- --instance medium --depth 1 --coarse-shots 24 --refined-shots 96 --trials 6
dotnet run --project host/QaoaMaxCut.Driver.csproj -- --instance large --depth 1 --coarse-shots 24 --refined-shots 96 --trials 6
python python/analyze.py
python python/compare.py
```

Windows helper script (recommended in PowerShell):

```powershell
.\tooling\windows\qaoa-maxcut.ps1 -Action run -Instance small
.\tooling\windows\qaoa-maxcut.ps1 -Action run-all
.\tooling\windows\qaoa-maxcut.ps1 -Action evidence
.\tooling\windows\qaoa-maxcut.ps1 -Action evidence -Quick
```

CMD wrapper equivalent:

```bat
tooling\windows\qaoa-maxcut.cmd -Action evidence -Quick
tooling\windows\qaoa-maxcut-quick.cmd
```

## Outputs

- `estimates/classical_baseline.json` – Maximum cut assignments and values for every graph instance
- `estimates/quantum_baseline_<instance>_d<depth>.json` – Multi-trial QAOA statistics with confidence intervals
- `estimates/quantum_classical_summary.md` – Auto-generated markdown table comparing classical optimum vs quantum mean +/- CI
- `plots/best_cut_values.png` – Visual comparison of Max-Cut values across instances
- `plots/value_distribution_small.png` – Distribution of cut values for the small instance
- `plots/quantum_vs_classical_uncertainty.png` – Quantum refined expectation versus classical optimum with 95% CI bars
- `qsharp/bin/Release/net6.0/QaoaMaxCut.dll` – Compiled Q# QAOA implementation

## Current Baseline

The classical baseline enumerates all bit strings to guarantee optimal Max-Cut values and logs diagnostic metrics that translate directly to QAOA objective functions. The Q# host now runs a depth-1 QAOA grid search per trial, aggregates uncertainty-bounded expectation metrics across repeated simulator trials, and writes a JSON report for reproducible comparison against the classical optimum. Future work will expand the pipeline to tighter optimizers and estimator-driven hardware profiling.

## Objective Maturity Gate

- **Current gate**: **Stage B complete** (classical baseline and Q# scaffold/build path are in place).
- **Next gate target**: **Stage C** (hardware-aware validation with uncertainty-bounded comparisons).

Stage C exit criteria for this problem:

- Execute at least one non-placeholder quantum workflow path tied to the problem objective.
- Report uncertainty-bounded comparisons between classical and quantum outputs on `small` and `medium` instances.
- Document transpilation/connectivity and backend assumptions used for reported quantum runs.
- Add calibration/noise-sensitivity evidence for the reported quantum metrics.

Current progress toward Stage C:

- Depth-1 QAOA host now emits uncertainty-bounded trial statistics and JSON artifacts for reproducible small-instance comparisons.
- Medium-instance uncertainty report is now available in `estimates/quantum_baseline_medium_d1.json`.
- Large-instance uncertainty report is now available in `estimates/quantum_baseline_large_d1.json`.
- Hardware-targeted estimator routing remains open.

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
