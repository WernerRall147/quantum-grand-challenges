Param(
    [string]$Owner = "WernerRall147",
    [string]$Repo = "quantum-grand-challenges",
    [string]$Branch = "main",
    [int]$RequiredApprovals = 0
)

$ghPath = "C:\Program Files\GitHub CLI\gh.exe"
if (!(Test-Path $ghPath)) {
    $ghPath = "gh"
}

Write-Host "Checking GitHub authentication..."
& $ghPath auth status | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "GitHub CLI is not authenticated. Run: gh auth login"
    exit 1
}

$payload = @{
    required_status_checks = @{
        strict = $true
        checks = @(
            @{ context = "Stage D Readiness Gate / stage-d-readiness"; app_id = -1 }
        )
    }
    enforce_admins = $true
    required_pull_request_reviews = @{
        dismiss_stale_reviews = $true
        require_code_owner_reviews = $false
        required_approving_review_count = $RequiredApprovals
    }
    restrictions = $null
    required_conversation_resolution = $true
    allow_force_pushes = $false
    allow_deletions = $false
    block_creations = $false
    required_linear_history = $false
    lock_branch = $false
    allow_fork_syncing = $false
} | ConvertTo-Json -Depth 6 -Compress

Write-Host "Applying branch protection to $Owner/${Repo}:$Branch..."
$tempFile = [System.IO.Path]::GetTempFileName()
Set-Content -Path $tempFile -Value $payload -Encoding Ascii

& $ghPath api --method PUT "repos/$Owner/$Repo/branches/$Branch/protection" --input $tempFile
$exitCode = $LASTEXITCODE
Remove-Item -Path $tempFile -ErrorAction SilentlyContinue

if ($exitCode -ne 0) {
    Write-Error "Failed to apply branch protection."
    exit 1
}

Write-Host "Branch protection updated successfully."
