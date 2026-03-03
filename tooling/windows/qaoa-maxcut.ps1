param(
    [ValidateSet("build", "run", "run-all", "classical", "analyze", "evidence")]
    [string]$Action = "evidence",
    [ValidateSet("small", "medium", "large")]
    [string]$Instance = "small",
    [int]$Depth = 1,
    [int]$CoarseShots = 24,
    [int]$RefinedShots = 96,
    [int]$Trials = 6,
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
    "evidence" {
        if (-not $NoBuild.IsPresent) {
            Invoke-Build
        }
        Invoke-Classical
        foreach ($target in @("small", "medium", "large")) {
            Invoke-RunInstance -TargetInstance $target
        }
        Invoke-Analyze
    }
}

Write-Host "QAOA helper completed successfully." -ForegroundColor Green
