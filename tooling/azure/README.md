# Shared Azure Quantum Workflow (All Problems)

This folder provides a single reusable Azure Quantum workflow for every problem under `problems/XX_*`.

## Goal

Use one mechanism for:

- env validation
- Azure CLI preflight
- manifest preparation
- submit (dry-run or execute)
- status collection
- smoke audit report generation

Once a problem has a runnable quantum program and at least one evidence artifact, it can use this flow without creating problem-specific Azure scripts.

## Files

- `problem_registry.json`: list of all 20 problem IDs and default target IDs.
- `.env.azure.example`: template for local Azure auth/workspace values.
- `validate_azure_env.py`: validates manual env file values.
- `validate_azure_cli.py`: validates Azure CLI login and workspace access.
- `prepare_problem_manifest.py`: writes `problems/<problem>/estimates/azure_job_manifest_<instance>_d<depth>.json`.
- `submit_job_auto.py`: dry-run-safe submit and manifest stamping.
- `collect_job.py`: fetches/records latest job status.
- `write_smoke_report.py`: writes `azure_smoke_report_<instance>_d<depth>.{json,md}`.
- `smoke_problem.py`: one-command orchestrator for the full smoke workflow.
- `assess_problem_readiness.py`: emits `tooling/azure/readiness_report.json` with all-problem readiness status.

## Quickstart (Cross-Problem)

```bash
# 1) Copy env template into a problem-local file and fill values manually
cp tooling/azure/.env.azure.example problems/03_qae_risk/.env.azure.local

# 2) Dry-run smoke for a problem (no Azure submission)
python tooling/azure/smoke_problem.py \
  --problem 03_qae_risk \
  --instance small \
  --depth 1 \
  --env-file problems/03_qae_risk/.env.azure.local

# 3) Real submit (requires --job-input-file and valid Azure auth/workspace)
python tooling/azure/smoke_problem.py \
  --problem 03_qae_risk \
  --instance small \
  --depth 1 \
  --env-file problems/03_qae_risk/.env.azure.local \
  --job-input-file <path/to/program.qir> \
  --execute \
  --collect
```

## Windows Helper

Use `tooling/windows/problem-azure.ps1` for the same operations:

```powershell
.\tooling\windows\problem-azure.ps1 -Action smoke -Problem 03_qae_risk -Instance small -Depth 1 -EnvFile problems/03_qae_risk/.env.azure.local
```

## Notes

- This workflow is intentionally env-gated; placeholder values are blocked.
- `submit_job_auto.py` is dry-run by default and only submits with `--execute`.
- If automatic evidence detection cannot find a suitable file, pass `--evidence-file` explicitly.

## Readiness Report

Generate an all-problem readiness snapshot:

```bash
python tooling/azure/assess_problem_readiness.py
```

This writes `tooling/azure/readiness_report.json` and reports how many registered problems are ready for the shared workflow.
