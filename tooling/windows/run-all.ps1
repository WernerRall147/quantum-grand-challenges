param(
    [switch]$SkipValidation,
    [switch]$SkipEstimator,
    [switch]$SkipWebsite,
    [switch]$SkipNpmInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $repoRoot

. "$PSScriptRoot\bootstrap-env.ps1" -HeadlessPlots

$logsDir = Join-Path $repoRoot "tooling\windows\logs"
New-Item -ItemType Directory -Path $logsDir -Force | Out-Null

$summary = [ordered]@{
    generated_at = (Get-Date).ToString("s")
    repo_root = $repoRoot
    validation = "skipped"
    estimator = "skipped"
    website_build = "skipped"
}

if (-not $SkipValidation.IsPresent) {
    Write-Host "Running full validation sweep..." -ForegroundColor Cyan
    & "$PSScriptRoot\validate-all.ps1"
    if ($LASTEXITCODE -ne 0) {
        $summary.validation = "fail"
    } else {
        $summary.validation = "pass"
    }
}

if (-not $SkipEstimator.IsPresent) {
    Write-Host "Running estimator mock pipeline..." -ForegroundColor Cyan
    $estimatorSummary = Join-Path $repoRoot "tooling\estimator\output\local_mock_summary.json"
    python tooling\estimator\run_estimation.py --all --mock --summary-path $estimatorSummary
    if ($LASTEXITCODE -ne 0) {
        $summary.estimator = "fail"
    } else {
        $summary.estimator = "pass"
    }
}

if (-not $SkipWebsite.IsPresent) {
    $websiteDir = Join-Path $repoRoot "website"
    if (Test-Path (Join-Path $websiteDir "package.json")) {
        Push-Location $websiteDir
        try {
            if (-not $SkipNpmInstall.IsPresent) {
                Write-Host "Installing website dependencies..." -ForegroundColor Cyan
                npm install
                if ($LASTEXITCODE -ne 0) {
                    throw "npm install failed"
                }
            }

            Write-Host "Building website..." -ForegroundColor Cyan
            npm run build
            if ($LASTEXITCODE -ne 0) {
                $summary.website_build = "fail"
            } else {
                $summary.website_build = "pass"
            }
        }
        finally {
            Pop-Location
        }
    } else {
        $summary.website_build = "no-website"
    }
}

$overall = "pass"
foreach ($k in @("validation", "estimator", "website_build")) {
    if ($summary[$k] -eq "fail") {
        $overall = "fail"
    }
}
$summary.overall = $overall

$summaryPath = Join-Path $logsDir "run-all-summary.json"
$summary | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 $summaryPath

Write-Host ""
Write-Host "Run-all summary: $summaryPath" -ForegroundColor Green
$summary
