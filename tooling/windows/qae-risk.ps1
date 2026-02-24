param(
    [ValidateSet("run", "analyze", "calibrate")]
    [string]$Action = "analyze",
    [switch]$Quick,
    [ValidateSet("small", "medium")]
    [string]$Instance = "small",
    [int]$CalibrationRuns = 20,
    [int]$LossQubits = 4,
    [double]$Threshold = 2.5,
    [double]$Mean = 0.0,
    [double]$StdDev = 1.0,
    [int]$PrecisionBits = 6,
    [int]$Repetitions = 120,
    [switch]$RunSanityCheck
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
. "$PSScriptRoot\bootstrap-env.ps1" -HeadlessPlots

$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

$problemRoot = Join-Path $repoRoot "problems\03_qae_risk"
$pythonDir = Join-Path $problemRoot "python"
$qsharpDir = Join-Path $problemRoot "qsharp"
$sanityValue = if ($RunSanityCheck.IsPresent) { "true" } else { "false" }

$effectiveLossQubits = $LossQubits
$effectiveThreshold = $Threshold
$effectiveMean = $Mean
$effectiveStdDev = $StdDev
$effectivePrecisionBits = $PrecisionBits
$effectiveRepetitions = $Repetitions

if ($Quick.IsPresent) {
    if (-not $PSBoundParameters.ContainsKey("PrecisionBits")) {
        $effectivePrecisionBits = 4
    }
    if (-not $PSBoundParameters.ContainsKey("Repetitions")) {
        $effectiveRepetitions = 24
    }
}

Write-Host "QAE helper action=$Action instance=$Instance quick=$($Quick.IsPresent)" -ForegroundColor Cyan

switch ($Action) {
    "run" {
        Push-Location $pythonDir
        try {
            & $pythonExe write_runtime_config.py `
                --loss-qubits $effectiveLossQubits `
                --threshold $effectiveThreshold `
                --mean $effectiveMean `
                --std-dev $effectiveStdDev `
                --precision-bits $effectivePrecisionBits `
                --repetitions $effectiveRepetitions `
                --run-sanity-check $sanityValue
            if ($LASTEXITCODE -ne 0) { throw "Runtime config generation failed." }
        }
        finally {
            Pop-Location
        }

        Push-Location $qsharpDir
        try {
            dotnet build --configuration Release
            if ($LASTEXITCODE -ne 0) { throw "Q# build failed." }

            dotnet run --configuration Release --no-build
            if ($LASTEXITCODE -ne 0) { throw "Q# run failed." }
        }
        finally {
            Pop-Location
        }
    }
    "analyze" {
        Push-Location $pythonDir
        try {
            $argsList = @(
                "analyze.py",
                "--instance-file", "../instances/$Instance.yaml",
                "--loss-qubits", "$effectiveLossQubits",
                "--threshold", "$effectiveThreshold",
                "--mean", "$effectiveMean",
                "--std-dev", "$effectiveStdDev",
                "--precision-bits", "$effectivePrecisionBits",
                "--repetitions", "$effectiveRepetitions"
            )
            if ($RunSanityCheck.IsPresent) {
                $argsList += "--run-sanity-check"
            } else {
                $argsList += "--skip-sanity-check"
            }

            & $pythonExe @argsList
            if ($LASTEXITCODE -ne 0) { throw "Analyze run failed." }
        }
        finally {
            Pop-Location
        }
    }
    "calibrate" {
        Push-Location $pythonDir
        try {
            $argsList = @(
                "analyze.py",
                "--instance-file", "../instances/$Instance.yaml",
                "--ensemble-runs", "$CalibrationRuns",
                "--loss-qubits", "$effectiveLossQubits",
                "--threshold", "$effectiveThreshold",
                "--mean", "$effectiveMean",
                "--std-dev", "$effectiveStdDev",
                "--precision-bits", "$effectivePrecisionBits",
                "--repetitions", "$effectiveRepetitions"
            )
            if ($RunSanityCheck.IsPresent) {
                $argsList += "--run-sanity-check"
            } else {
                $argsList += "--skip-sanity-check"
            }

            & $pythonExe @argsList
            if ($LASTEXITCODE -ne 0) { throw "Calibration run failed." }
        }
        finally {
            Pop-Location
        }
    }
}

Write-Host "QAE helper completed successfully." -ForegroundColor Green
