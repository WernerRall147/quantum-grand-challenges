<#
.SYNOPSIS
    Open or re-lock the Azure Quantum storage exclusions used for the Azure Friday demo.

.DESCRIPTION
    The tenant policy `mcapsgovdeploypolicies` forces publicNetworkAccess=Disabled and
    allowSharedKeyAccess=false on every storage account in the subscription. When that is
    applied to the Quantum workspace's linked storage account, two things break:

      1. The workspace itself goes provisioningState=Failed, because any full PUT to it
         fails while it cannot reach its own storage. It still reports usable=Yes, but a
         red "Failed" on screen is not something to explain on camera.
      2. Job detail and job output cannot be read.

    The policy has a sanctioned exclusion - a SecurityControl=Ignore tag on the resource or
    its resource group - which is what this applies. It is deliberately temporary.

    WHAT THIS CANNOT FIX. The original workspace's older jobs stored their payloads in the
    service-managed account 7ffkjkws4bgsw, inside a Microsoft-managed resource group behind
    a deny assignment. Nobody in this tenant can open it, so `az quantum job show` and
    `job output` still fail for those jobs. Use the qgc-af-demo workspace for anything that
    needs to open a job. See deck-notes.md C7.

.PARAMETER Check
    Report the current posture and change nothing.

.PARAMETER Apply
    Add the exclusion tags, open the linked storage account, and reconcile the workspace so
    provisioningState returns to Succeeded.

.PARAMETER Revert
    Re-lock the storage account and remove the exclusion tags. Run this after the recording.
    The workspace will go back to Failed the next time something PUTs it - that is expected,
    and is the honest resting state under the policy.

.EXAMPLE
    .\Set-AzureDemoAccess.ps1 -Check
    .\Set-AzureDemoAccess.ps1 -Apply     # before the recording
    .\Set-AzureDemoAccess.ps1 -Revert    # after the recording
#>
[CmdletBinding(DefaultParameterSetName = 'Check')]
param(
    [Parameter(ParameterSetName = 'Check')][switch]$Check,
    [Parameter(ParameterSetName = 'Apply')][switch]$Apply,
    [Parameter(ParameterSetName = 'Revert')][switch]$Revert
)

$ErrorActionPreference = 'Stop'

$Subscription = '82cd08af-0dac-4fc5-8a3a-f2ab9e4679c3'
$ResourceGroup = 'Quantum-Grand-Challenges'
$Workspace = 'Quantum-Grand-Challenges'
$StorageAccount = 'qgcqstore20260304'

$RgId = "/subscriptions/$Subscription/resourceGroups/$ResourceGroup"
$StorageId = "$RgId/providers/Microsoft.Storage/storageAccounts/$StorageAccount"
$WorkspaceId = "$RgId/providers/Microsoft.Quantum/Workspaces/$Workspace"

function Get-Posture {
    $sa = az storage account show --ids $StorageId -o json --only-show-errors 2>$null | ConvertFrom-Json
    $ws = az quantum workspace show -g $ResourceGroup -w $Workspace -o json --only-show-errors 2>$null | ConvertFrom-Json
    $rg = az group show -n $ResourceGroup -o json --only-show-errors 2>$null | ConvertFrom-Json
    [pscustomobject]@{
        PublicNetwork  = $sa.publicNetworkAccess
        SharedKey      = $sa.allowSharedKeyAccess
        StorageTag     = if ($sa.tags.SecurityControl) { $sa.tags.SecurityControl } else { '(none)' }
        ResourceGroupTag = if ($rg.tags.SecurityControl) { $rg.tags.SecurityControl } else { '(none)' }
        Workspace      = $ws.properties.provisioningState
        Usable         = $ws.properties.usable
    }
}

function Write-Posture {
    param($P, [string]$Label)
    Write-Host ""
    Write-Host "== $Label " -NoNewline
    Write-Host ('=' * [Math]::Max(0, 60 - $Label.Length))
    Write-Host ("  storage publicNetworkAccess : {0}" -f $P.PublicNetwork)
    Write-Host ("  storage allowSharedKeyAccess: {0}" -f $P.SharedKey)
    Write-Host ("  storage SecurityControl tag : {0}" -f $P.StorageTag)
    Write-Host ("  resource group tag          : {0}" -f $P.ResourceGroupTag)
    Write-Host ("  workspace provisioningState : {0}" -f $P.Workspace)
    Write-Host ("  workspace usable            : {0}" -f $P.Usable)
}

function Invoke-Reconcile {
    <# A tags-only PATCH does not re-provision. A full PUT does, and that is what clears a
       stale Failed - but only once the storage it validates is reachable. #>
    $stamp = Get-Date -Format 'HHmmss'
    az resource update --ids $WorkspaceId --set "tags.reconcile=$stamp" -o none --only-show-errors 2>$null
    Start-Sleep -Seconds 30
    az tag update --resource-id $WorkspaceId --operation Delete --tags reconcile= -o none --only-show-errors 2>$null
    Start-Sleep -Seconds 10
}

if ($PSCmdlet.ParameterSetName -eq 'Check' -or $Check) {
    Write-Posture (Get-Posture) 'Current posture'
    Write-Host ""
    Write-Host "  -Apply opens it for the recording. -Revert locks it again afterwards."
    return
}

if ($Apply) {
    Write-Posture (Get-Posture) 'Before'

    Write-Host "`nApplying the policy's sanctioned exclusion (SecurityControl=Ignore)..."
    az tag update --resource-id $RgId --operation Merge --tags SecurityControl=Ignore -o none --only-show-errors
    az storage account update --ids $StorageId --set tags.SecurityControl=Ignore -o none --only-show-errors
    az storage account update --ids $StorageId --public-network-access Enabled `
        --default-action Allow --bypass AzureServices -o none --only-show-errors
    az resource update --ids $StorageId --set properties.allowSharedKeyAccess=true -o none --only-show-errors
    Start-Sleep -Seconds 20

    Write-Host "Reconciling the workspace so provisioningState clears..."
    Invoke-Reconcile

    $after = Get-Posture
    Write-Posture $after 'After'

    # Assert on the values, not on the exit codes above: every one of those commands
    # returns 0 even when a Modify policy silently discards the write.
    $problems = @()
    if ($after.PublicNetwork -ne 'Enabled') { $problems += "publicNetworkAccess is $($after.PublicNetwork), expected Enabled" }
    if (-not $after.SharedKey) { $problems += "allowSharedKeyAccess is still false" }
    if ($after.Workspace -ne 'Succeeded') { $problems += "workspace is $($after.Workspace), expected Succeeded" }

    Write-Host ""
    if ($problems) {
        $problems | ForEach-Object { Write-Host "  FAIL  $_" }
        exit 1
    }
    Write-Host "  OK    open, and the workspace reads Succeeded."
    Write-Host "  NOTE  older jobs on this workspace still cannot be opened - their data is in"
    Write-Host "        the managed account nobody in this tenant can unlock. Use qgc-af-demo."
    Write-Host "  AFTER THE RECORDING: .\Set-AzureDemoAccess.ps1 -Revert"
    return
}

if ($Revert) {
    Write-Posture (Get-Posture) 'Before'

    Write-Host "`nRe-locking the storage account while the tag still permits the write..."
    az storage account update --ids $StorageId --public-network-access Disabled `
        --default-action Allow -o none --only-show-errors
    az resource update --ids $StorageId --set properties.allowSharedKeyAccess=false -o none --only-show-errors
    Write-Host "Removing the exclusion tags..."
    az storage account update --ids $StorageId --remove tags.SecurityControl -o none --only-show-errors 2>$null
    az tag update --resource-id $RgId --operation Delete --tags SecurityControl= -o none --only-show-errors 2>$null
    Start-Sleep -Seconds 20

    $after = Get-Posture
    Write-Posture $after 'After'

    $problems = @()
    if ($after.PublicNetwork -ne 'Disabled') { $problems += "publicNetworkAccess is $($after.PublicNetwork), expected Disabled" }
    if ($after.SharedKey) { $problems += "allowSharedKeyAccess is still true" }
    if ($after.StorageTag -ne '(none)') { $problems += "storage still tagged $($after.StorageTag)" }
    if ($after.ResourceGroupTag -ne '(none)') { $problems += "resource group still tagged $($after.ResourceGroupTag)" }

    Write-Host ""
    if ($problems) {
        $problems | ForEach-Object { Write-Host "  FAIL  $_" }
        exit 1
    }
    Write-Host "  OK    locked down and untagged - back to the policy's intended posture."
    Write-Host "  NOTE  the workspace will report Failed again after its next full PUT."
    return
}
