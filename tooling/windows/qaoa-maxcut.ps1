param(
    [ValidateSet("build", "run", "run-all", "classical", "analyze", "estimate", "evidence")]
    [string]$Action = "evidence",
    [ValidateSet("small", "medium", "large")]
    [string]$Instance = "small",
    [int]$Depth = 1,
    [int]$CoarseShots = 24,
    [int]$RefinedShots = 96,
    [int]$Trials = 6,
    [switch]$LiveEstimate,
    [switch]$Quick,
    [switch]$NoBuild
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
. "$PSScriptRoot\bootstrap-env.ps1" -HeadlessPlots

$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

$problemRoot = Join-Path $repoRoot "problems\05_qaoa_maxcut"

$effectiveCoarseShots = $CoarseShots
$effectiveRefinedShots = $RefinedShots
$effectiveTrials = $Trials

if ($Quick.IsPresent) {
    if (-not $PSBoundParameters.ContainsKey("CoarseShots")) {
        $effectiveCoarseShots = 12
    }
    if (-not $PSBoundParameters.ContainsKey("RefinedShots")) {
        $effectiveRefinedShots = 48
    }
    if (-not $PSBoundParameters.ContainsKey("Trials")) {
        $effectiveTrials = 3
    }
}

function Invoke-Build {
    Write-Host "Building QAOA Max-Cut host and Q# project..." -ForegroundColor Cyan
    Push-Location $problemRoot
    try {
        dotnet build host/QaoaMaxCut.Driver.csproj --configuration Release
        if ($LASTEXITCODE -ne 0) { throw "Build failed." }
    }
    finally {
        Pop-Location
    }
}

function Invoke-RunInstance {
    param(
        [string]$TargetInstance
    )

    Write-Host "Running QAOA instance '$TargetInstance' (depth=$Depth, coarse=$effectiveCoarseShots, refined=$effectiveRefinedShots, trials=$effectiveTrials)..." -ForegroundColor Cyan
    Push-Location $problemRoot
    try {
        dotnet run --project host/QaoaMaxCut.Driver.csproj -- --instance $TargetInstance --depth $Depth --coarse-shots $effectiveCoarseShots --refined-shots $effectiveRefinedShots --trials $effectiveTrials
        if ($LASTEXITCODE -ne 0) { throw "Run failed for instance '$TargetInstance'." }
    }
    finally {
        Pop-Location
    }
}

function Invoke-Classical {
    Write-Host "Generating classical baseline..." -ForegroundColor Cyan
    Push-Location $problemRoot
    try {
        & $pythonExe python/classical_baseline.py
        if ($LASTEXITCODE -ne 0) { throw "Classical baseline failed." }
    }
    finally {
        Pop-Location
    }
}

function Invoke-Analyze {
    Write-Host "Generating plots and markdown comparison summary..." -ForegroundColor Cyan
    Push-Location $problemRoot
    try {
        & $pythonExe python/analyze.py
        if ($LASTEXITCODE -ne 0) { throw "Analyze script failed." }

        & $pythonExe python/compare.py
        if ($LASTEXITCODE -ne 0) { throw "Compare script failed." }
    }
    finally {
        Pop-Location
    }
}

function Invoke-Estimate {
    param(
        [string]$TargetInstance
    )

    Write-Host "Preparing estimator parameters for '$TargetInstance'..." -ForegroundColor Cyan
    Push-Location $problemRoot
    try {
        & $pythonExe python/prepare_estimator_params.py --instance $TargetInstance --depth $Depth
        if ($LASTEXITCODE -ne 0) { throw "Estimator parameter preparation failed." }
    }
    finally {
        Pop-Location
    }

    Write-Host "Running estimator automation for '$TargetInstance'..." -ForegroundColor Cyan
    $summaryPath = Join-Path $repoRoot "tooling\estimator\output\qaoa_summary.json"
    $estimateArgs = @(
        "tooling/estimator/run_estimation.py",
        "--all",
        "--problem", "05_qaoa_maxcut",
        "--targets", "surface_code_generic_v1,qubit_gate_ns_e3",
        "--summary-path", $summaryPath
    )
    if (-not $LiveEstimate.IsPresent) {
        $estimateArgs += "--mock"
    }

    Push-Location $repoRoot
    try {
        & $pythonExe @estimateArgs
        if ($LASTEXITCODE -ne 0) { throw "Estimator automation failed." }
    }
    finally {
        Pop-Location
    }
}

Write-Host "QAOA helper action=$Action quick=$($Quick.IsPresent) noBuild=$($NoBuild.IsPresent)" -ForegroundColor Cyan

switch ($Action) {
    "build" {
        Invoke-Build
    }
    "run" {
        if (-not $NoBuild.IsPresent) {
            Invoke-Build
        }
        Invoke-RunInstance -TargetInstance $Instance
    }
    "run-all" {
        if (-not $NoBuild.IsPresent) {
            Invoke-Build
        }
        foreach ($target in @("small", "medium", "large")) {
            Invoke-RunInstance -TargetInstance $target
        }
    }
    "classical" {
        Invoke-Classical
    }
    "analyze" {
        Invoke-Analyze
    }
    "estimate" {
        Invoke-Estimate -TargetInstance $Instance
    }
    "evidence" {
        if (-not $NoBuild.IsPresent) {
            Invoke-Build
        }
        Invoke-Classical
        foreach ($target in @("small", "medium", "large")) {
            Invoke-RunInstance -TargetInstance $target
        }
        Invoke-Analyze
        Invoke-Estimate -TargetInstance "small"
    }
}

Write-Host "QAOA helper completed successfully." -ForegroundColor Green
