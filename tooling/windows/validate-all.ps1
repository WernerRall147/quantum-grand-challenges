param(
    [switch]$SkipClassical,
    [switch]$SkipAnalyze,
    [switch]$SkipBuild
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $repoRoot

. "$PSScriptRoot\bootstrap-env.ps1" -HeadlessPlots

$results = @()
$logsDir = Join-Path $repoRoot "tooling\windows\logs"
New-Item -ItemType Directory -Path $logsDir -Force | Out-Null

$problems = Get-ChildItem "$repoRoot\problems" -Directory |
    Sort-Object Name |
    Where-Object { $_.Name -match '^[0-9]{2}_' }

foreach ($problem in $problems) {
    $entry = [ordered]@{
        Problem = $problem.Name
        Classical = if ($SkipClassical) { "skipped" } else { "pass" }
        Analyze = if ($SkipAnalyze) { "skipped" } else { "pass" }
        Build = if ($SkipBuild) { "skipped" } else { "pass" }
    }

    $makefilePath = Join-Path $problem.FullName "Makefile"
    if (-not (Test-Path $makefilePath)) {
        $entry.Classical = "no-makefile"
        $entry.Analyze = "no-makefile"
        $entry.Build = "no-makefile"
        $results += [pscustomobject]$entry
        continue
    }

    Push-Location $problem.FullName
    try {
        if (-not $SkipClassical) {
            $classicalLog = Join-Path $logsDir ("{0}_classical.log" -f $problem.Name)
            & make classical *> $classicalLog
            if ($LASTEXITCODE -ne 0) {
                $entry.Classical = "fail"
            }
        }

        if (-not $SkipAnalyze) {
            $analyzeLog = Join-Path $logsDir ("{0}_analyze.log" -f $problem.Name)
            & make analyze *> $analyzeLog
            if ($LASTEXITCODE -ne 0) {
                $entry.Analyze = "fail"
            }
        }

        if (-not $SkipBuild) {
            $buildLog = Join-Path $logsDir ("{0}_build.log" -f $problem.Name)
            & make build *> $buildLog
            if ($LASTEXITCODE -ne 0) {
                $entry.Build = "fail"
            }
        }
    }
    finally {
        Pop-Location
    }

    $results += [pscustomobject]$entry
}

$results | Format-Table -AutoSize

$summary = [ordered]@{
    generated_at = (Get-Date).ToString("s")
    repo_root = $repoRoot
    py_utf8 = $env:PYTHONUTF8
    mpl_backend = $env:MPLBACKEND
    results = $results
}

$summaryPath = Join-Path $logsDir "validation-summary.json"
$summary | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 $summaryPath
Write-Host ""
Write-Host "Validation summary: $summaryPath" -ForegroundColor Cyan
Write-Host "Logs directory: $logsDir" -ForegroundColor Cyan
