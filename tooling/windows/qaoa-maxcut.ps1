param(
    [ValidateSet("build", "run", "run-all", "depth-sweep", "noise-sweep", "classical", "analyze", "estimate", "estimate-all", "azure-runbook", "azure-manifest", "validate-azure-env", "validate-azure-cli", "validate-azure-manifest", "azure-submit", "azure-submit-auto", "azure-collect", "azure-collect-auto", "evidence")]
    [string]$Action = "evidence",
    [ValidateSet("small", "medium", "large")]
    [string]$Instance = "small",
    [int]$Depth = 1,
    [int]$CoarseShots = 24,
    [int]$RefinedShots = 96,
    [int]$Trials = 6,
    [string]$Depths = "1,2,3",
    [string]$NoiseLevels = "0.00,0.01,0.02,0.05,0.10",
    [int]$NoiseSamples = 256,
    [string]$TargetId = "microsoft.estimator",
    [string]$AzureEnvFile = ".env.azure.local",
    [string]$AzureManualJobId = "",
    [string]$AzureJobInputFile = "",
    [string]$AzureJobInputFormat = "qir.v1",
    [string]$AzureEntryPoint = "",
    [switch]$AzureSubmitExecute,
    [ValidateSet("running", "succeeded", "failed", "cancelled")]
    [string]$AzureResultStatus = "succeeded",
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

function Get-AzureEnvPathArg {
    if ([System.IO.Path]::IsPathRooted($AzureEnvFile)) {
        return $AzureEnvFile
    }
    return "problems/05_qaoa_maxcut/$AzureEnvFile"
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

function Invoke-DepthSweep {
    param(
        [string]$TargetInstance
    )

    Write-Host "Running depth sweep for '$TargetInstance' (depths=$Depths, coarse=$effectiveCoarseShots, refined=$effectiveRefinedShots, trials=$effectiveTrials)..." -ForegroundColor Cyan
    Push-Location $problemRoot
    try {
        & $pythonExe python/depth_sweep.py --instance $TargetInstance --depths $Depths --coarse-shots $effectiveCoarseShots --refined-shots $effectiveRefinedShots --trials $effectiveTrials
        if ($LASTEXITCODE -ne 0) { throw "Depth sweep failed for instance '$TargetInstance'." }
    }
    finally {
        Pop-Location
    }
}

function Invoke-NoiseSweep {
    param(
        [string]$TargetInstance
    )

    Write-Host "Running noise sweep for '$TargetInstance' (depth=$Depth, levels=$NoiseLevels, samples=$NoiseSamples)..." -ForegroundColor Cyan
    Push-Location $problemRoot
    try {
        & $pythonExe python/noise_sweep.py --instance $TargetInstance --depth $Depth --noise-levels $NoiseLevels --samples-per-trial $NoiseSamples
        if ($LASTEXITCODE -ne 0) { throw "Noise sweep failed for instance '$TargetInstance'." }
    }
    finally {
        Pop-Location
    }
}

function Invoke-AzureRunbook {
    Write-Host "Azure Quantum Runbook (QAOA MaxCut)" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host "Current defaults: instance=$Instance depth=$Depth targetId=$TargetId"
    Write-Host ""
    Write-Host "1) Create local auth/workspace file (manual):"
    Write-Host "   Copy-Item .env.azure.example .env.azure.local"
    Write-Host "   Then edit .env.azure.local and replace all CHANGE_ME values."
    Write-Host ""
    Write-Host "2) Validate env gate:"
    Write-Host "   .\\tooling\\windows\\qaoa-maxcut.ps1 -Action validate-azure-env -AzureEnvFile .env.azure.local"
    Write-Host "   .\\tooling\\windows\\qaoa-maxcut.ps1 -Action validate-azure-cli -AzureEnvFile .env.azure.local"
    Write-Host ""
    Write-Host "3) Build/validate manifest:"
    Write-Host "   .\\tooling\\windows\\qaoa-maxcut.ps1 -Action azure-manifest -Instance $Instance -Depth $Depth -TargetId $TargetId"
    Write-Host "   .\\tooling\\windows\\qaoa-maxcut.ps1 -Action validate-azure-manifest -Instance $Instance -Depth $Depth -AzureEnvFile .env.azure.local"
    Write-Host ""
    Write-Host "4) After real Azure submission, stamp job metadata:"
    Write-Host "   .\\tooling\\windows\\qaoa-maxcut.ps1 -Action azure-submit -Instance $Instance -Depth $Depth -AzureEnvFile .env.azure.local -AzureManualJobId <azure_job_id>"
    Write-Host "   or run submit directly via Azure CLI (dry-run default):"
    Write-Host "   .\\tooling\\windows\\qaoa-maxcut.ps1 -Action azure-submit-auto -Instance $Instance -Depth $Depth -TargetId $TargetId -AzureEnvFile .env.azure.local -AzureJobInputFile <path\\to\\program.qir>"
    Write-Host "   .\\tooling\\windows\\qaoa-maxcut.ps1 -Action azure-submit-auto -Instance $Instance -Depth $Depth -TargetId $TargetId -AzureEnvFile .env.azure.local -AzureJobInputFile <path\\to\\program.qir> -AzureSubmitExecute"
    Write-Host ""
    Write-Host "5) After completion, stamp result status:"
    Write-Host "   .\\tooling\\windows\\qaoa-maxcut.ps1 -Action azure-collect -Instance $Instance -Depth $Depth -AzureEnvFile .env.azure.local -AzureResultStatus succeeded"
    Write-Host "   or fetch status directly from Azure CLI:"
    Write-Host "   .\\tooling\\windows\\qaoa-maxcut.ps1 -Action azure-collect-auto -Instance $Instance -Depth $Depth -AzureEnvFile .env.azure.local"
    Write-Host ""
    Write-Host "Manual gate reminder: Azure operations are blocked until .env.azure.local is valid." -ForegroundColor Yellow
}

function Invoke-ValidateAzureEnv {
    Write-Host "Validating Azure env file '$AzureEnvFile'..." -ForegroundColor Cyan
    $envPathArg = Get-AzureEnvPathArg
    Push-Location $repoRoot
    try {
        & $pythonExe problems/05_qaoa_maxcut/python/validate_azure_env.py --env-file $envPathArg
        if ($LASTEXITCODE -ne 0) { throw "Azure env validation failed." }
    }
    finally {
        Pop-Location
    }
}

function Invoke-AzureManifest {
    Write-Host "Preparing Azure manifest for '$Instance' (depth=$Depth, target=$TargetId)..." -ForegroundColor Cyan
    Push-Location $problemRoot
    try {
        & $pythonExe python/prepare_azure_job_manifest.py --instance $Instance --depth $Depth --coarse-shots $effectiveCoarseShots --refined-shots $effectiveRefinedShots --trials $effectiveTrials --target-id $TargetId
        if ($LASTEXITCODE -ne 0) { throw "Azure manifest generation failed." }
    }
    finally {
        Pop-Location
    }
}

function Invoke-ValidateAzureCli {
    Invoke-ValidateAzureEnv
    Write-Host "Validating Azure CLI preflight for '$AzureEnvFile'..." -ForegroundColor Cyan
    $envPathArg = Get-AzureEnvPathArg
    Push-Location $repoRoot
    try {
        & $pythonExe problems/05_qaoa_maxcut/python/validate_azure_cli.py --env-file $envPathArg
        if ($LASTEXITCODE -ne 0) { throw "Azure CLI preflight failed." }
    }
    finally {
        Pop-Location
    }
}

function Invoke-ValidateAzureManifest {
    Invoke-ValidateAzureEnv
    Write-Host "Validating Azure manifest for '$Instance' (depth=$Depth)..." -ForegroundColor Cyan
    Push-Location $repoRoot
    try {
        & $pythonExe problems/05_qaoa_maxcut/python/validate_azure_job_manifest.py --manifest "problems/05_qaoa_maxcut/estimates/azure_job_manifest_${Instance}_d${Depth}.json"
        if ($LASTEXITCODE -ne 0) { throw "Azure manifest validation failed." }
    }
    finally {
        Pop-Location
    }
}

function Invoke-AzureSubmit {
    if ([string]::IsNullOrWhiteSpace($AzureManualJobId)) {
        throw "AzureManualJobId is required for -Action azure-submit."
    }
    Invoke-ValidateAzureEnv
    Write-Host "Recording Azure submission metadata for '$Instance' (depth=$Depth)..." -ForegroundColor Cyan
    $envPathArg = Get-AzureEnvPathArg
    Push-Location $repoRoot
    try {
        & $pythonExe problems/05_qaoa_maxcut/python/submit_azure_job.py --manifest "problems/05_qaoa_maxcut/estimates/azure_job_manifest_${Instance}_d${Depth}.json" --env-file $envPathArg --manual-job-id $AzureManualJobId
        if ($LASTEXITCODE -ne 0) { throw "Azure submit metadata update failed." }
    }
    finally {
        Pop-Location
    }
}

function Invoke-AzureCollect {
    Invoke-ValidateAzureEnv
    Write-Host "Recording Azure result metadata for '$Instance' (depth=$Depth, status=$AzureResultStatus)..." -ForegroundColor Cyan
    $envPathArg = Get-AzureEnvPathArg
    Push-Location $repoRoot
    try {
        & $pythonExe problems/05_qaoa_maxcut/python/collect_azure_job.py --manifest "problems/05_qaoa_maxcut/estimates/azure_job_manifest_${Instance}_d${Depth}.json" --env-file $envPathArg --result-status $AzureResultStatus
        if ($LASTEXITCODE -ne 0) { throw "Azure collect metadata update failed." }
    }
    finally {
        Pop-Location
    }
}

function Invoke-AzureSubmitAuto {
    Invoke-ValidateAzureCli
    Write-Host "Running Azure auto-submit for '$Instance' (depth=$Depth, execute=$($AzureSubmitExecute.IsPresent))..." -ForegroundColor Cyan
    $envPathArg = Get-AzureEnvPathArg
    $submitArgs = @(
        "problems/05_qaoa_maxcut/python/submit_azure_job_auto.py",
        "--manifest", "problems/05_qaoa_maxcut/estimates/azure_job_manifest_${Instance}_d${Depth}.json",
        "--env-file", $envPathArg,
        "--target-id", $TargetId,
        "--job-input-format", $AzureJobInputFormat
    )

    if (-not [string]::IsNullOrWhiteSpace($AzureJobInputFile)) {
        if ([System.IO.Path]::IsPathRooted($AzureJobInputFile)) {
            $submitArgs += @("--job-input-file", $AzureJobInputFile)
        }
        else {
            $submitArgs += @("--job-input-file", (Join-Path $repoRoot $AzureJobInputFile))
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($AzureEntryPoint)) {
        $submitArgs += @("--entry-point", $AzureEntryPoint)
    }

    if ($AzureSubmitExecute.IsPresent) {
        $submitArgs += "--execute"
    }

    Push-Location $repoRoot
    try {
        & $pythonExe @submitArgs
        if ($LASTEXITCODE -ne 0) { throw "Azure auto-submit failed." }
    }
    finally {
        Pop-Location
    }
}

function Invoke-AzureCollectAuto {
    Invoke-ValidateAzureCli
    Write-Host "Fetching Azure result metadata via az CLI for '$Instance' (depth=$Depth)..." -ForegroundColor Cyan
    $envPathArg = Get-AzureEnvPathArg
    Push-Location $repoRoot
    try {
        & $pythonExe problems/05_qaoa_maxcut/python/collect_azure_job.py --manifest "problems/05_qaoa_maxcut/estimates/azure_job_manifest_${Instance}_d${Depth}.json" --env-file $envPathArg --fetch-from-azure
        if ($LASTEXITCODE -ne 0) { throw "Azure auto-collect metadata update failed." }
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
    $summaryPath = Join-Path $repoRoot "tooling\estimator\output\qaoa_summary_$TargetInstance.json"
    $paramsFile = "estimates/estimator_params_$TargetInstance`_d$Depth.json"
    $estimateArgs = @(
        "tooling/estimator/run_estimation.py",
        "--all",
        "--problem", "05_qaoa_maxcut",
        "--params-file", $paramsFile,
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

function Invoke-EstimatorSummary {
    Write-Host "Generating estimator markdown summary..." -ForegroundColor Cyan
    Push-Location $problemRoot
    try {
        & $pythonExe python/summarize_estimator.py
        if ($LASTEXITCODE -ne 0) { throw "Estimator summary generation failed." }
    }
    finally {
        Pop-Location
    }
}

function Invoke-PruneEstimatorArtifacts {
    Write-Host "Pruning stale estimator timestamp artifacts..." -ForegroundColor Cyan
    Push-Location $problemRoot
    try {
        & $pythonExe python/prune_estimator_artifacts.py --keep-per-target 3
        if ($LASTEXITCODE -ne 0) { throw "Estimator artifact prune failed." }
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
    "depth-sweep" {
        if (-not $NoBuild.IsPresent) {
            Invoke-Build
        }
        Invoke-DepthSweep -TargetInstance $Instance
    }
    "noise-sweep" {
        Invoke-NoiseSweep -TargetInstance $Instance
    }
    "analyze" {
        Invoke-Analyze
    }
    "estimate" {
        Invoke-Estimate -TargetInstance $Instance
    }
    "estimate-all" {
        foreach ($target in @("small", "medium", "large")) {
            Invoke-Estimate -TargetInstance $target
        }
        Invoke-PruneEstimatorArtifacts
        Invoke-EstimatorSummary
    }
    "azure-runbook" {
        Invoke-AzureRunbook
    }
    "validate-azure-env" {
        Invoke-ValidateAzureEnv
    }
    "azure-manifest" {
        Invoke-AzureManifest
    }
    "validate-azure-cli" {
        Invoke-ValidateAzureCli
    }
    "validate-azure-manifest" {
        Invoke-ValidateAzureManifest
    }
    "azure-submit" {
        Invoke-AzureSubmit
    }
    "azure-submit-auto" {
        Invoke-AzureSubmitAuto
    }
    "azure-collect" {
        Invoke-AzureCollect
    }
    "azure-collect-auto" {
        Invoke-AzureCollectAuto
    }
    "evidence" {
        if (-not $NoBuild.IsPresent) {
            Invoke-Build
        }
        Invoke-Classical
        foreach ($target in @("small", "medium", "large")) {
            Invoke-RunInstance -TargetInstance $target
        }
        Invoke-DepthSweep -TargetInstance "small"
        Invoke-Analyze
        foreach ($target in @("small", "medium", "large")) {
            Invoke-Estimate -TargetInstance $target
        }
        Invoke-PruneEstimatorArtifacts
        Invoke-EstimatorSummary
    }
}

Write-Host "QAOA helper completed successfully." -ForegroundColor Green
