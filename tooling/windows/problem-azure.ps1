param(
    [ValidateSet("validate-env", "validate-cli", "prepare-manifest", "submit-auto", "collect", "smoke")]
    [string]$Action = "smoke",
    [string]$Problem = "03_qae_risk",
    [string]$Instance = "small",
    [int]$Depth = 1,
    [int]$Shots = 256,
    [int]$Trials = 1,
    [string]$TargetId = "microsoft.estimator",
    [string]$EnvFile = "problems/05_qaoa_maxcut/.env.azure.local",
    [string]$EvidenceFile = "",
    [string]$JobInputFile = "",
    [string]$JobInputFormat = "qir.v1",
    [string]$EntryPoint = "",
    [switch]$Execute,
    [switch]$Collect
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
. "$PSScriptRoot\bootstrap-env.ps1" -HeadlessPlots

$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

function Resolve-ArgPath([string]$Value) {
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return ""
    }
    if ([System.IO.Path]::IsPathRooted($Value)) {
        return $Value
    }
    return (Join-Path $repoRoot $Value)
}

$envPath = Resolve-ArgPath $EnvFile
$evidencePath = Resolve-ArgPath $EvidenceFile
$jobInputPath = Resolve-ArgPath $JobInputFile

function Invoke-AzureTool([string[]]$Cmd) {
    Push-Location $repoRoot
    try {
        & $pythonExe @Cmd
        if ($LASTEXITCODE -ne 0) {
            throw "Azure tooling command failed"
        }
    }
    finally {
        Pop-Location
    }
}

switch ($Action) {
    "validate-env" {
        Invoke-AzureTool @("tooling/azure/validate_azure_env.py", "--env-file", $envPath)
    }
    "validate-cli" {
        Invoke-AzureTool @("tooling/azure/validate_azure_cli.py", "--env-file", $envPath)
    }
    "prepare-manifest" {
        $cmdList = @(
            "tooling/azure/prepare_problem_manifest.py",
            "--problem", $Problem,
            "--instance", $Instance,
            "--depth", $Depth,
            "--shots", $Shots,
            "--trials", $Trials,
            "--target-id", $TargetId
        )
        if (-not [string]::IsNullOrWhiteSpace($evidencePath)) {
            $cmdList += @("--evidence-file", $evidencePath)
        }
        Invoke-AzureTool $cmdList
    }
    "submit-auto" {
        $manifest = "problems/$Problem/estimates/azure_job_manifest_${Instance}_d${Depth}.json"
        $cmdList = @(
            "tooling/azure/submit_job_auto.py",
            "--manifest", $manifest,
            "--env-file", $envPath,
            "--target-id", $TargetId,
            "--job-input-format", $JobInputFormat
        )
        if (-not [string]::IsNullOrWhiteSpace($jobInputPath)) {
            $cmdList += @("--job-input-file", $jobInputPath)
        }
        if (-not [string]::IsNullOrWhiteSpace($EntryPoint)) {
            $cmdList += @("--entry-point", $EntryPoint)
        }
        if ($Execute.IsPresent) {
            $cmdList += "--execute"
        }
        Invoke-AzureTool $cmdList
    }
    "collect" {
        $manifest = "problems/$Problem/estimates/azure_job_manifest_${Instance}_d${Depth}.json"
        Invoke-AzureTool @(
            "tooling/azure/collect_job.py",
            "--manifest", $manifest,
            "--env-file", $envPath,
            "--fetch-from-azure"
        )
    }
    "smoke" {
        $cmdList = @(
            "tooling/azure/smoke_problem.py",
            "--problem", $Problem,
            "--instance", $Instance,
            "--depth", $Depth,
            "--shots", $Shots,
            "--trials", $Trials,
            "--target-id", $TargetId,
            "--env-file", $envPath,
            "--job-input-format", $JobInputFormat
        )
        if (-not [string]::IsNullOrWhiteSpace($evidencePath)) {
            $cmdList += @("--evidence-file", $evidencePath)
        }
        if (-not [string]::IsNullOrWhiteSpace($jobInputPath)) {
            $cmdList += @("--job-input-file", $jobInputPath)
        }
        if (-not [string]::IsNullOrWhiteSpace($EntryPoint)) {
            $cmdList += @("--entry-point", $EntryPoint)
        }
        if ($Execute.IsPresent) {
            $cmdList += "--execute"
        }
        if ($Collect.IsPresent) {
            $cmdList += "--collect"
        }
        Invoke-AzureTool $cmdList
    }
}

Write-Host "Azure problem helper completed." -ForegroundColor Green
