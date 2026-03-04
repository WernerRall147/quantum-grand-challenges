# 05. QAOA for Max-Cut

This problem prepares the groundwork for implementing the Quantum Approximate Optimization Algorithm on weighted Max-Cut instances. The current milestone provides deterministic classical baselines, representative graph instances, and a working depth-1 QAOA circuit with a coarse parameter sweep.

## Roadmap

- [x] Scaffold directory structure, utilities, and helper scripts
- [x] Provide classical brute-force baseline with summary statistics
- [x] Add parameterized graph instances (small/medium/large)
- [x] Generate diagnostic plots for cut values
- [x] Implement depth-1 QAOA circuit with coarse parameter sweep
- [x] Generalize QAOA optimizer to support depth >= 1 via coordinate search
- [x] Add depth sweep evidence artifacts (`depth_sweep_<instance>.{json,md}` + plot)
- [x] Generalize QAOA driver to consume YAML instances dynamically
- [x] Add uncertainty-bounded multi-trial QAOA reporting to `estimates/`
- [x] Route optimized parameters into the resource estimator profiles

## Quickstart

```bash
cd problems/05_qaoa_maxcut
make classical      # Exhaustive search baseline for each YAML graph instance
make analyze        # Generate plots summarizing best cut values
make build          # Build the Q# project (requires .NET 6.0 runtime)
make run            # Run depth-configurable QAOA with multi-trial uncertainty summary + JSON output
make run-all        # Run depth-configurable QAOA for small/medium/large and write quantum artifacts
make depth-sweep INSTANCE=small DEPTHS=1,2,3 TRIALS=6  # Generate depth-vs-quality evidence artifacts
make noise-sweep INSTANCE=small DEPTH=3 NOISE_LEVELS=0.00,0.01,0.02,0.05,0.10  # Generate readout-noise sensitivity artifacts
make validate-assumptions  # Validate backend/transpilation/connectivity assumptions evidence
make validate-quality  # Validate depth/noise quality thresholds for Stage C evidence
make estimate       # Build estimator params from latest quantum artifact and run estimator automation
make estimate-all   # Build estimator params, run estimator automation for small/medium/large, prune stale artifacts, and refresh markdown summary
make estimate ESTIMATE_MOCK=0  # Optional: run estimator automation without mock mode
make evidence       # One-shot refresh: classical baseline + quantum runs + plots + estimator summaries
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
python python/prepare_estimator_params.py --instance small --depth 1
python ../../tooling/estimator/run_estimation.py --all --problem 05_qaoa_maxcut --params-file estimates/estimator_params_small_d1.json --targets surface_code_generic_v1,qubit_gate_ns_e3 --mock --summary-path ../../tooling/estimator/output/qaoa_summary_small.json
```

Windows helper script (recommended in PowerShell):

```powershell
.\tooling\windows\qaoa-maxcut.ps1 -Action run -Instance small
.\tooling\windows\qaoa-maxcut.ps1 -Action run-all
.\tooling\windows\qaoa-maxcut.ps1 -Action depth-sweep -Instance small -Depths 1,2,3
.\tooling\windows\qaoa-maxcut.ps1 -Action noise-sweep -Instance small -Depth 3 -NoiseLevels 0.00,0.01,0.02,0.05,0.10
.\tooling\windows\qaoa-maxcut.ps1 -Action estimate -Instance small
.\tooling\windows\qaoa-maxcut.ps1 -Action estimate-all
.\tooling\windows\qaoa-maxcut.ps1 -Action estimate -Instance small -LiveEstimate
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
- `estimates/depth_sweep_<instance>.json` – Aggregated depth sweep metrics for the selected instance
- `estimates/depth_sweep_<instance>.md` – Markdown summary table for depth sweep results
- `estimates/noise_sweep_<instance>_d<depth>.json` – Readout-noise sensitivity sweep metrics for a selected baseline depth
- `estimates/noise_sweep_<instance>_d<depth>.md` – Markdown summary table for noise sweep results
- `estimates/backend_assumptions.md` – Backend/transpilation/connectivity assumptions for reported runtime + estimator evidence
- `python/validate_evidence_quality.py` – Enforces depth/noise evidence quality thresholds used by CI/automation
- `estimates/evidence_quality_report.md` – Human-readable snapshot of depth/noise evidence threshold checks
- `estimates/evidence_quality_report.json` – Machine-readable snapshot of depth/noise evidence threshold checks
- `estimates/estimator_params_<instance>_d<depth>.json` – Estimator-ready parameter payload derived from the latest quantum baseline
- `estimates/quantum_classical_summary.md` – Auto-generated markdown table comparing classical optimum vs quantum mean +/- CI
- `estimates/estimator_profile_summary.md` – Auto-generated table summarizing latest estimator metrics across instances and targets
- `estimates/latest_<target>_<instance>.json` – Stable latest estimator artifact for each target/instance pair (used by summary tooling)
- `python/prune_estimator_artifacts.py` – Keeps timestamped estimator artifacts bounded (`--keep-per-target`, default 3)
- `tooling/estimator/output/qaoa_summary_<instance>.json` – Combined estimator summary for QAOA targets (mock/live depending on invocation)
- `plots/best_cut_values.png` – Visual comparison of Max-Cut values across instances
- `plots/value_distribution_small.png` – Distribution of cut values for the small instance
- `plots/quantum_vs_classical_uncertainty.png` – Quantum refined expectation versus classical optimum with 95% CI bars
- `plots/qaoa_depth_sweep_<instance>.png` – Refined expectation versus depth with 95% CI bars
- `plots/qaoa_noise_sweep_<instance>_d<depth>.png` – Refined cut-value sensitivity across readout-noise levels
- `qsharp/bin/Release/net6.0/QaoaMaxCut.dll` – Compiled Q# QAOA implementation

## Current Baseline

The classical baseline enumerates all bit strings to guarantee optimal Max-Cut values and logs diagnostic metrics that translate directly to QAOA objective functions. The Q# host now runs a depth-configurable QAOA coordinate-search optimizer per trial, aggregates uncertainty-bounded expectation metrics across repeated simulator trials, and writes a JSON report for reproducible comparison against the classical optimum. Future work will expand the pipeline to tighter optimizers and estimator-driven hardware profiling.

## Objective Maturity Gate

- **Current gate**: **Stage C complete** (hardware-aware validation evidence with uncertainty-bounded comparisons is in place).
- **Next gate target**: **Stage D** (backend-calibrated performance hardening and stronger hardware-readiness evidence).

Stage C exit criteria for this problem:

- Execute at least one non-placeholder quantum workflow path tied to the problem objective.
- Report uncertainty-bounded comparisons between classical and quantum outputs on `small` and `medium` instances.
- Document transpilation/connectivity and backend assumptions used for reported quantum runs.
- Add calibration/noise-sensitivity evidence for the reported quantum metrics.

Current progress toward Stage C (exit criteria satisfied):

- Depth-1 QAOA host now emits uncertainty-bounded trial statistics and JSON artifacts for reproducible small-instance comparisons.
- Q# optimizer now supports depth >= 1 using coordinate-search updates over beta/gamma layers.
- Depth-2 trial evidence for the small instance is available in `estimates/quantum_baseline_small_d2.json`.
- Depth sweep evidence (`d=1,2,3`) for the small instance is available in `estimates/depth_sweep_small.md`, showing improved refined mean from `1.4927` (d=1) to `1.9247` (d=3).
- Medium-instance depth sweep (`d=1,2`) is available in `estimates/depth_sweep_medium.md` (best refined mean `2.8316` at depth 2).
- Large-instance depth sweep (`d=1,2`) is available in `estimates/depth_sweep_large.md` (best refined mean `4.1578` at depth 2).
- Noise-sensitivity sweeps can now be generated via `make noise-sweep` (or `python/noise_sweep.py`) and are surfaced in the summary dashboard when present.
- Small-instance noise sweep at depth 3 is available in `estimates/noise_sweep_small_d3.md` (degrades from `2.2000` at `p=0.00` to `1.9521` at `p=0.10`).
- Medium-instance noise sweep at depth 2 is available in `estimates/noise_sweep_medium_d2.md` (degrades from `4.0000` at `p=0.00` to `3.3164` at `p=0.10`).
- Large-instance noise sweep at depth 2 is available in `estimates/noise_sweep_large_d2.md` (degrades from `7.3000` at `p=0.00` to `5.9883` at `p=0.10`).
- Medium-instance uncertainty report is now available in `estimates/quantum_baseline_medium_d1.json`.
- Large-instance uncertainty report is now available in `estimates/quantum_baseline_large_d1.json`.
- Hardware-targeted estimator routing is now wired through `python/prepare_estimator_params.py` and `tooling/estimator/run_estimation.py`.
- Backend/transpilation/connectivity assumptions are now documented in `estimates/backend_assumptions.md` and checked via `python/validate_backend_assumptions.py`.
- Depth/noise evidence quality is now enforced via `python/validate_evidence_quality.py` (minimum points, bounded monotonicity behavior, and minimum degradation/gain thresholds).
- Quality checks now emit `estimates/evidence_quality_report.{md,json}` for reproducible CI/local audit trails.

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
