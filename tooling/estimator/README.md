# Estimator Automation

The `run_estimation.py` script wraps the Azure Quantum Resource Estimator CLI and provides
config-driven automation for Quantum Grand Challenges.

## Quick Start

```pwsh
python tooling/estimator/run_estimation.py --help
python tooling/estimator/run_estimation.py --all --dry-run
python tooling/estimator/run_estimation.py --all --mock --summary-path tooling/estimator/output/nightly_summary.json
```

Key CLI options:

- `--all` / `--config`: run every problem listed in `config/default.yaml` (or a custom config).
- `--problem`: limit execution to one or more problem IDs (repeatable).
- `--targets`: limit to specific estimator targets.
- `--summary-path`: write a consolidated plan/summary JSON (works with `--dry-run`).
- `--mock`: skip Azure calls and generate standardized mock metrics based on instance metadata.

The script produces per-problem JSON estimates under `problems/<id>/estimates/` and a consolidated
summary in `tooling/estimator/output/`.

## Configuration

Default settings live in `tooling/estimator/config/default.yaml`. Each entry identifies a problem,
algorithm label, instance metadata file, estimator entry point, and target profiles.

Optional `mock_metrics` blocks can override the auto-generated metrics when running in mock mode:

```yaml
estimator_params:
  entry_point: "RunQAERiskAnalysis"
  mock_metrics:
    surface_code_generic_v1:
      logical_qubits: 14
      runtime_seconds: 120
```

## CI Integration

The nightly `full-estimation-sweep` GitHub Actions job now calls this script in `--mock` mode and uploads
the generated artifacts, enabling downstream analysis without requiring Azure credentials.
