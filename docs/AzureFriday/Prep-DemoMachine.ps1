#Requires -Version 5.1
<#
.SYNOPSIS
    One-command PC prep for the Azure Friday recording of the Quantum Advantage Evaluator.

.DESCRIPTION
    Does the machine setup the Azure Friday team asked for, then proves the demo still
    works, so neither costs you time on the day.

    Sources for every item, so you can argue with it:
      - Chris's prep mail (docs/AzureFriday/IntroCallOverview.md, "Machine prep")
      - The production prep doc (docs/AzureFriday/Prep.docx, "Technical")
      - MPS Best Practices for Remote Recordings.pdf (computer, network, audio, video)
      - The runbook checklist (README.md section 9, storyboard.md section 7)

    Four modes:

      -Check      Audit only. Changes nothing. Tells you what is not yet set.
      (default)   Full prep. Applies every setting a script can apply. Run the day before.
      -PreFlight  Day-of. Re-audits the machine, runs the live smoke test, pre-executes
                  the beats that are meant to be pre-executed, opens the tabs in order.
      -Restore    Puts every setting this script changed back the way it was.
      -SelfTest   Verifies the script's own machinery without touching your settings.

    No administrator rights are needed: everything is per-user (HKCU, user display mode,
    per-user power scheme).

    A status of PASS means behaviour was observed - a call was made, a value was read back
    after the change, a process was confirmed gone. SET means a setting was written and
    read back, but the visible effect was not observed by this script and you should glance
    at it. MANUAL means a human has to do it. That distinction is deliberate: this repo has
    a documented history of checks that measured shape instead of behaviour and stayed
    green while the thing they guarded was broken.

.PARAMETER Check
    Audit only. No changes, no state file written.

.PARAMETER PreFlight
    Day-of readiness: machine audit, uptime issue check, smoke test, pre-executed beats,
    demo tabs opened in the order the storyboard asks for.

.PARAMETER Restore
    Undo everything recorded in the state file written by a prep run.

.PARAMETER SelfTest
    Exercise the script's helpers (registry write/read/restore on a scratch key, display
    P/Invoke, powercfg parsing, runbook prompt parsing) and confirm a health check goes red
    when pointed at something unreachable. Changes no real setting.

.PARAMETER Force
    Force-close apps that ignore a graceful close request. Without this, a stubborn app is
    reported and left alone so you cannot lose unsaved work.

.EXAMPLE
    PS> .\Prep-DemoMachine.ps1 -Check
    Audit this machine against the Azure Friday requirements and change nothing.

.EXAMPLE
    PS> .\Prep-DemoMachine.ps1
    Full prep. Run this the day before the recording.

.EXAMPLE
    PS> .\Prep-DemoMachine.ps1 -PreFlight
    Run this about 20 minutes before you go live. Takes 5-8 minutes, mostly the smoke test.

.EXAMPLE
    PS> .\Prep-DemoMachine.ps1 -Restore
    Put the machine back afterwards.

.NOTES
    If PowerShell refuses to run this:
        powershell -ExecutionPolicy Bypass -File .\docs\AzureFriday\Prep-DemoMachine.ps1
#>

[CmdletBinding()]
param(
    [switch]$Check,
    [switch]$PreFlight,
    [switch]$Restore,
    [switch]$SelfTest,
    [switch]$Force,
    [switch]$SkipAppClose,
    [switch]$SkipSmokeTest,
    [switch]$SkipPreExecute,
    [switch]$NoTabs,
    [switch]$NoExplorerRestart,
    [int]$Width = 1920,
    [int]$Height = 1080,
    [string]$BackgroundColor = '#1E1E1E',
    [string]$ApiBase = 'https://qgc-eval-api.jollysea-98a0f8cb.eastus.azurecontainerapps.io',
    [string]$SiteUrl = 'https://wernerrall147.github.io/quantum-grand-challenges/',
    [string]$CtaUrl = 'https://github.com/WernerRall147/quantum-grand-challenges',
    [string]$Repo = 'WernerRall147/quantum-grand-challenges',
    [string]$ArtifactDir = (Join-Path $env:LOCALAPPDATA 'AzureFridayPrep')
)

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

# ---------------------------------------------------------------------------
# Mode
# ---------------------------------------------------------------------------

$requested = @()
if ($Check) { $requested += 'Check' }
if ($PreFlight) { $requested += 'PreFlight' }
if ($Restore) { $requested += 'Restore' }
if ($SelfTest) { $requested += 'SelfTest' }

if ($requested.Count -gt 1) {
    throw "Pick one mode. You asked for: $($requested -join ', ')."
}
$Mode = if ($requested.Count -eq 1) { $requested[0] } else { 'Prep' }

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Runbook = Join-Path $PSScriptRoot 'README.md'
$StatePath = Join-Path $ArtifactDir 'restore-state.json'

$ADVANCED = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
$POLICY_EXPLORER = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer'
$PUSH_NOTIFY = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\PushNotifications'
$NOTIFY_SETTINGS = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings'
$DESKTOP = 'HKCU:\Control Panel\Desktop'
$COLORS = 'HKCU:\Control Panel\Colors'
$FEEDS = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Feeds'

# powercfg GUIDs
$SUB_VIDEO = '7516b95f-f776-4464-8c53-06167f40cc99'
$VIDEOIDLE = '3c0bc021-c8a8-4e07-a973-6b14cbcb2b7e'
$SUB_SLEEP = '238c9fa8-0aad-41ed-83f4-97be242c8f20'
$STANDBYIDLE = '29f6c1db-86da-48c5-9fdb-f2b67b1f44da'

# Apps that pop, ping, or leak something confidential onto a shared screen.
$NoisyApps = @(
    @{ Name = 'outlook'; Label = 'Outlook (classic)' }
    @{ Name = 'olk'; Label = 'Outlook (new)' }
    @{ Name = 'ms-teams'; Label = 'Microsoft Teams' }
    @{ Name = 'Teams'; Label = 'Microsoft Teams (classic)' }
    @{ Name = 'lync'; Label = 'Skype for Business' }
    @{ Name = 'Skype'; Label = 'Skype' }
    @{ Name = 'Slack'; Label = 'Slack' }
    @{ Name = 'Discord'; Label = 'Discord' }
    @{ Name = 'WhatsApp'; Label = 'WhatsApp' }
    @{ Name = 'Telegram'; Label = 'Telegram' }
    @{ Name = 'Signal'; Label = 'Signal' }
    @{ Name = 'Spotify'; Label = 'Spotify' }
    @{ Name = 'steam'; Label = 'Steam' }
)

$script:Results = New-Object System.Collections.ArrayList
$script:State = @{
    capturedUtc = (Get-Date).ToUniversalTime().ToString('s')
    registry    = @{}
    display     = @{}
    power       = @{}
    wallpaper   = @{}
}
$script:StateLoaded = $false
$script:Artifacts = New-Object System.Collections.ArrayList

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

function Write-Section {
    param([string]$Title)
    Write-Host ''
    Write-Host "== $Title " -ForegroundColor Cyan -NoNewline
    Write-Host ('=' * [Math]::Max(4, 72 - $Title.Length)) -ForegroundColor DarkCyan
}

function Add-Result {
    param(
        [Parameter(Mandatory)][string]$Area,
        [Parameter(Mandatory)][string]$Item,
        [Parameter(Mandatory)][ValidateSet('PASS', 'SET', 'WARN', 'FAIL', 'INFO', 'SKIP', 'MANUAL')][string]$Status,
        [string]$Detail = ''
    )
    $null = $script:Results.Add([pscustomobject]@{
            Area   = $Area
            Item   = $Item
            Status = $Status
            Detail = $Detail
        })
    $colour = switch ($Status) {
        'PASS' { 'Green' }
        'SET' { 'Green' }
        'WARN' { 'Yellow' }
        'FAIL' { 'Red' }
        'MANUAL' { 'Cyan' }
        default { 'DarkGray' }
    }
    Write-Host ('  {0,-6} ' -f $Status) -ForegroundColor $colour -NoNewline
    Write-Host ('{0,-40} ' -f $Item) -NoNewline
    Write-Host $Detail -ForegroundColor DarkGray
}

# ---------------------------------------------------------------------------
# Native interop
# ---------------------------------------------------------------------------

function Initialize-Native {
    if ('AfNative' -as [type]) { return $true }
    $source = @'
using System;
using System.Runtime.InteropServices;

public static class AfNative
{
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    public struct DEVMODE
    {
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
        public string dmDeviceName;
        public short dmSpecVersion;
        public short dmDriverVersion;
        public short dmSize;
        public short dmDriverExtra;
        public int dmFields;
        public int dmPositionX;
        public int dmPositionY;
        public int dmDisplayOrientation;
        public int dmDisplayFixedOutput;
        public short dmColor;
        public short dmDuplex;
        public short dmYResolution;
        public short dmTTOption;
        public short dmCollate;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
        public string dmFormName;
        public short dmLogPixels;
        public int dmBitsPerPel;
        public int dmPelsWidth;
        public int dmPelsHeight;
        public int dmDisplayFlags;
        public int dmDisplayFrequency;
        public int dmICMMethod;
        public int dmICMIntent;
        public int dmMediaType;
        public int dmDitherType;
        public int dmReserved1;
        public int dmReserved2;
        public int dmPanningWidth;
        public int dmPanningHeight;
    }

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern bool EnumDisplaySettings(string deviceName, int modeNum, ref DEVMODE devMode);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int ChangeDisplaySettings(ref DEVMODE devMode, int flags);

    private const int ENUM_CURRENT_SETTINGS = -1;
    private const int CDS_UPDATEREGISTRY = 0x01;
    private const int CDS_TEST = 0x02;
    private const int DM_PELSWIDTH = 0x80000;
    private const int DM_PELSHEIGHT = 0x100000;

    // The struct is filled here rather than from PowerShell on purpose: a DEVMODE built by
    // New-Object has null ByValTStr fields, and EnumDisplaySettings then fails silently -
    // it returns false and you are left reading 0x0.
    private static DEVMODE NewDevMode()
    {
        DEVMODE dm = new DEVMODE();
        dm.dmDeviceName = String.Empty;
        dm.dmFormName = String.Empty;
        dm.dmSize = (short)Marshal.SizeOf(typeof(DEVMODE));
        return dm;
    }

    public static DEVMODE GetCurrentMode(out bool ok)
    {
        DEVMODE dm = NewDevMode();
        ok = EnumDisplaySettings(null, ENUM_CURRENT_SETTINGS, ref dm);
        return dm;
    }

    /// <summary>Returns 0 on success, or the ChangeDisplaySettings error code. -100 means
    /// the current mode could not be read at all.</summary>
    public static int TrySetResolution(int width, int height, bool testOnly)
    {
        DEVMODE dm = NewDevMode();
        if (!EnumDisplaySettings(null, ENUM_CURRENT_SETTINGS, ref dm)) { return -100; }
        dm.dmPelsWidth = width;
        dm.dmPelsHeight = height;
        dm.dmFields = DM_PELSWIDTH | DM_PELSHEIGHT;
        return ChangeDisplaySettings(ref dm, testOnly ? CDS_TEST : CDS_UPDATEREGISTRY);
    }

    [DllImport("user32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern bool SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SetSysColors(int cElements, int[] lpaElements, int[] lpaRgbValues);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern IntPtr FindWindow(string className, string windowName);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern IntPtr FindWindowEx(IntPtr parent, IntPtr childAfter, string className, string windowName);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern IntPtr SendMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    public static IntPtr FindDefView()
    {
        IntPtr progman = FindWindow("Progman", null);
        IntPtr defView = FindWindowEx(progman, IntPtr.Zero, "SHELLDLL_DefView", null);
        if (defView != IntPtr.Zero) { return defView; }

        IntPtr worker = IntPtr.Zero;
        do
        {
            worker = FindWindowEx(IntPtr.Zero, worker, "WorkerW", null);
            if (worker == IntPtr.Zero) { break; }
            defView = FindWindowEx(worker, IntPtr.Zero, "SHELLDLL_DefView", null);
        } while (defView == IntPtr.Zero);
        return defView;
    }

    /// <summary>1 if desktop icons are on screen, 0 if they are not, -1 if it cannot be
    /// determined. The HideIcons registry value is not this: writing it does not move the
    /// icons, so reading it can say "visible" while the desktop is bare.</summary>
    public static int IconsVisible()
    {
        IntPtr defView = FindDefView();
        if (defView == IntPtr.Zero) { return -1; }
        IntPtr list = FindWindowEx(defView, IntPtr.Zero, "SysListView32", null);
        if (list == IntPtr.Zero) { return -1; }
        return IsWindowVisible(list) ? 1 : 0;
    }

    /// <summary>Asks the shell to toggle desktop icons. This is what Explorer's own
    /// right-click menu sends, so it moves the icons and updates the registry.</summary>
    public static bool ToggleIcons()
    {
        IntPtr defView = FindDefView();
        if (defView == IntPtr.Zero) { return false; }
        SendMessage(defView, 0x0111, (IntPtr)0x7402, IntPtr.Zero);
        return true;
    }
}
'@
    try {
        Add-Type -TypeDefinition $source -ErrorAction Stop
        return $true
    }
    catch {
        Add-Result -Area 'Display' -Item 'Native interop' -Status 'FAIL' -Detail $_.Exception.Message
        return $false
    }
}

# ---------------------------------------------------------------------------
# State (so -Restore can put things back)
# ---------------------------------------------------------------------------

function ConvertTo-HashtableSafe {
    param($Object)
    $table = @{}
    if ($null -ne $Object) {
        foreach ($property in $Object.PSObject.Properties) { $table[$property.Name] = $property.Value }
    }
    return $table
}

function Import-PrepState {
    if (-not (Test-Path $StatePath)) { return $false }
    try {
        $raw = Get-Content -Path $StatePath -Raw -Encoding UTF8 | ConvertFrom-Json
        $script:State = @{
            capturedUtc = $raw.capturedUtc
            registry    = ConvertTo-HashtableSafe $raw.registry
            display     = ConvertTo-HashtableSafe $raw.display
            power       = ConvertTo-HashtableSafe $raw.power
            wallpaper   = ConvertTo-HashtableSafe $raw.wallpaper
        }
        $script:StateLoaded = $true
        return $true
    }
    catch {
        Write-Warning "Could not read $StatePath : $($_.Exception.Message)"
        return $false
    }
}

function Export-PrepState {
    if ($Mode -ne 'Prep') { return }
    if (-not (Test-Path $ArtifactDir)) { $null = New-Item -ItemType Directory -Path $ArtifactDir -Force }
    $script:State | ConvertTo-Json -Depth 10 | Set-Content -Path $StatePath -Encoding UTF8
}

function Save-Original {
    # First write wins. A second prep run must not record the already-prepped value as
    # the original, or -Restore becomes a no-op that claims to have restored something.
    param([Parameter(Mandatory)][string]$Bucket, [Parameter(Mandatory)][string]$Key, $Value)
    if (-not $script:State[$Bucket].ContainsKey($Key)) {
        $script:State[$Bucket][$Key] = $Value
    }
}

# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------

function Get-RegValue {
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][string]$Name)
    try {
        return (Get-ItemProperty -Path $Path -Name $Name -ErrorAction Stop).$Name
    }
    catch { return $null }
}

function Set-RegValue {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)]$Value,
        [ValidateSet('DWord', 'String')][string]$Type = 'DWord'
    )
    if (-not (Test-Path $Path)) { $null = New-Item -Path $Path -Force -ErrorAction Stop }
    $null = New-ItemProperty -Path $Path -Name $Name -Value $Value -PropertyType $Type -Force -ErrorAction Stop
}

function Test-PolicyBlocked {
    param($Exception)
    if ($null -eq $Exception) { return $false }
    $type = $Exception.GetType().FullName
    return ($type -match 'UnauthorizedAccessException|SecurityException' -or
        $Exception.Message -match 'not allowed|is denied|unauthorized operation')
}

function Set-PreparedRegistryValue {
    <#
      Capture, write, read back. The read-back is the point: a write that silently did not
      take is the failure mode this whole script exists to avoid.
    #>
    param(
        [Parameter(Mandatory)][string]$Area,
        [Parameter(Mandatory)][string]$Item,
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)]$Desired,
        [ValidateSet('DWord', 'String')][string]$Type = 'DWord',
        [switch]$Apply,
        [string]$Detail = '',
        [string]$ManualRoute = 'Set it by hand in Settings.'
    )
    $current = Get-RegValue -Path $Path -Name $Name
    $matches_ = ("$current" -eq "$Desired")
    $shown = if ($null -eq $current) { 'not set' } else { "'$current'" }

    if (-not $Apply) {
        if ($matches_) { Add-Result -Area $Area -Item $Item -Status 'PASS' -Detail "already $Desired" }
        else { Add-Result -Area $Area -Item $Item -Status 'WARN' -Detail "is $shown, wants '$Desired'. $Detail" }
        return
    }

    $stateKey = "$Path|$Name|$Type"
    $hadCapture = $script:State['registry'].ContainsKey($stateKey)
    Save-Original -Bucket 'registry' -Key $stateKey -Value $current
    try {
        Set-RegValue -Path $Path -Name $Name -Value $Desired -Type $Type
    }
    catch {
        # Nothing changed, so nothing should be restored later - but do not throw away a
        # capture an earlier run made and did change.
        if (-not $hadCapture) { $script:State['registry'].Remove($stateKey) }
        if (Test-PolicyBlocked -Exception $_.Exception) {
            Add-Result -Area $Area -Item $Item -Status 'WARN' `
                -Detail "your device policy locks this value. $ManualRoute"
        }
        else {
            Add-Result -Area $Area -Item $Item -Status 'FAIL' -Detail $_.Exception.Message
        }
        return
    }
    $after = Get-RegValue -Path $Path -Name $Name
    if ("$after" -eq "$Desired") {
        Add-Result -Area $Area -Item $Item -Status 'SET' -Detail "$shown -> '$after'. $Detail"
    }
    else {
        Add-Result -Area $Area -Item $Item -Status 'FAIL' -Detail "wrote '$Desired', read back '$after'"
    }
}

# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

function Get-CurrentMode {
    if (-not (Initialize-Native)) { return $null }
    $ok = $false
    $dm = [AfNative]::GetCurrentMode([ref]$ok)
    if ($ok) { return $dm }
    return $null
}

function Set-DisplayResolution {
    param([int]$TargetWidth, [int]$TargetHeight, [switch]$Apply)

    $dm = Get-CurrentMode
    if ($null -eq $dm) {
        Add-Result -Area 'Display' -Item 'Resolution' -Status 'FAIL' -Detail 'could not read the current display mode'
        return
    }

    $now = "$($dm.dmPelsWidth)x$($dm.dmPelsHeight)"
    $want = "${TargetWidth}x${TargetHeight}"

    if ($now -eq $want) {
        Add-Result -Area 'Display' -Item 'Resolution' -Status 'PASS' -Detail "$now at $($dm.dmDisplayFrequency)Hz"
        return
    }
    if (-not $Apply) {
        Add-Result -Area 'Display' -Item 'Resolution' -Status 'WARN' -Detail "is $now, wants $want"
        return
    }

    Save-Original -Bucket 'display' -Key 'width'  -Value $dm.dmPelsWidth
    Save-Original -Bucket 'display' -Key 'height' -Value $dm.dmPelsHeight

    $test = [AfNative]::TrySetResolution($TargetWidth, $TargetHeight, $true)
    if ($test -ne 0) {
        Add-Result -Area 'Display' -Item 'Resolution' -Status 'FAIL' -Detail "adapter rejected $want (code $test). Set it by hand in Display settings."
        return
    }
    $null = [AfNative]::TrySetResolution($TargetWidth, $TargetHeight, $false)

    Start-Sleep -Milliseconds 800
    $after = Get-CurrentMode
    $applied = if ($after) { "$($after.dmPelsWidth)x$($after.dmPelsHeight)" } else { 'unknown' }
    if ($applied -eq $want) {
        Add-Result -Area 'Display' -Item 'Resolution' -Status 'PASS' -Detail "$now -> $applied, read back from the adapter"
    }
    else {
        Add-Result -Area 'Display' -Item 'Resolution' -Status 'FAIL' -Detail "asked for $want, adapter reports $applied"
    }
}

function Test-MonitorCount {
    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
        $screens = [System.Windows.Forms.Screen]::AllScreens
        if ($screens.Count -le 1) {
            Add-Result -Area 'Display' -Item 'Monitor count' -Status 'PASS' -Detail '1 display attached'
        }
        else {
            Add-Result -Area 'Display' -Item 'Monitor count' -Status 'WARN' -Detail "$($screens.Count) displays. Duplicate, do not extend, and share the primary."
        }
    }
    catch {
        Add-Result -Area 'Display' -Item 'Monitor count' -Status 'SKIP' -Detail $_.Exception.Message
    }
}

function Set-SolidBackground {
    param([string]$Hex, [switch]$Apply)

    if (-not (Initialize-Native)) { return }
    if ($Hex -notmatch '^#?([0-9A-Fa-f]{6})$') {
        Add-Result -Area 'Desktop' -Item 'Solid background' -Status 'FAIL' -Detail "'$Hex' is not a #RRGGBB colour"
        return
    }
    $clean = $Matches[1]
    $r = [Convert]::ToInt32($clean.Substring(0, 2), 16)
    $g = [Convert]::ToInt32($clean.Substring(2, 2), 16)
    $b = [Convert]::ToInt32($clean.Substring(4, 2), 16)
    $wantColour = "$r $g $b"

    $currentPaper = Get-RegValue -Path $DESKTOP -Name 'WallPaper'
    $currentColour = Get-RegValue -Path $COLORS -Name 'Background'

    if ([string]::IsNullOrWhiteSpace($currentPaper) -and "$currentColour" -eq $wantColour) {
        Add-Result -Area 'Desktop' -Item 'Solid background' -Status 'PASS' -Detail "no picture, colour $wantColour"
        return
    }
    if (-not $Apply) {
        $what = if ([string]::IsNullOrWhiteSpace($currentPaper)) { "colour $currentColour" } else { "picture $currentPaper" }
        Add-Result -Area 'Desktop' -Item 'Solid background' -Status 'WARN' -Detail "is $what, wants a solid $wantColour"
        return
    }

    Save-Original -Bucket 'wallpaper' -Key 'path'       -Value $currentPaper
    Save-Original -Bucket 'wallpaper' -Key 'style'      -Value (Get-RegValue -Path $DESKTOP -Name 'WallpaperStyle')
    Save-Original -Bucket 'wallpaper' -Key 'tile'       -Value (Get-RegValue -Path $DESKTOP -Name 'TileWallpaper')
    Save-Original -Bucket 'wallpaper' -Key 'background' -Value $currentColour

    Set-RegValue -Path $COLORS -Name 'Background' -Value $wantColour -Type String
    $colourRef = $r -bor ($g -shl 8) -bor ($b -shl 16)
    $applied = [AfNative]::SetSysColors(1, @(1), @($colourRef))          # COLOR_DESKTOP
    $cleared = [AfNative]::SystemParametersInfo(0x0014, 0, '', 0x03)     # SPI_SETDESKWALLPAPER

    $afterPaper = Get-RegValue -Path $DESKTOP -Name 'WallPaper'
    if ($applied -and $cleared -and [string]::IsNullOrWhiteSpace($afterPaper)) {
        Add-Result -Area 'Desktop' -Item 'Solid background' -Status 'PASS' -Detail "picture cleared, desktop colour set to #$clean"
    }
    else {
        Add-Result -Area 'Desktop' -Item 'Solid background' -Status 'WARN' -Detail "colour written; wallpaper still '$afterPaper'. Check the desktop."
    }
}

function Set-DesktopIconVisibility {
    <#
      Asks the shell, not the registry.

      Writing HideIcons does not move anything until Explorer reloads, so a restore that
      only writes the value leaves a bare desktop while reporting that the icons are back.
      That happened here during testing, and it is why this reads IsWindowVisible on the
      desktop list view instead.
    #>
    param([Parameter(Mandatory)][bool]$Visible, [switch]$Apply)

    if (-not (Initialize-Native)) { return }
    $state = [AfNative]::IconsVisible()

    if ($state -lt 0) {
        # No desktop window to ask. Fall back to the registry and say so.
        $desired = if ($Visible) { 0 } else { 1 }
        Set-PreparedRegistryValue -Area 'Desktop' -Item 'Desktop icons' `
            -Path $ADVANCED -Name 'HideIcons' -Desired $desired -Apply:$Apply `
            -Detail 'desktop window not found, so this needs an Explorer restart to show up'
        return
    }

    $isVisible = ($state -eq 1)
    $wanted = if ($Visible) { 'visible' } else { 'hidden' }

    if ($isVisible -eq $Visible) {
        Add-Result -Area 'Desktop' -Item 'Desktop icons' -Status 'PASS' -Detail "already $wanted (asked the shell, not the registry)"
        return
    }
    if (-not $Apply) {
        Add-Result -Area 'Desktop' -Item 'Desktop icons' -Status 'WARN' -Detail 'icons are on screen; MPS asks for a clean desktop'
        return
    }

    Save-Original -Bucket 'registry' -Key "$ADVANCED|HideIcons|DWord" -Value (Get-RegValue -Path $ADVANCED -Name 'HideIcons')

    if (-not [AfNative]::ToggleIcons()) {
        Add-Result -Area 'Desktop' -Item 'Desktop icons' -Status 'FAIL' -Detail 'the desktop window went away mid-run'
        return
    }
    Start-Sleep -Milliseconds 700

    $after = [AfNative]::IconsVisible()
    if (($after -eq 1) -eq $Visible) {
        Add-Result -Area 'Desktop' -Item 'Desktop icons' -Status 'PASS' -Detail "icons are now $wanted on screen"
    }
    else {
        Add-Result -Area 'Desktop' -Item 'Desktop icons' -Status 'FAIL' -Detail "asked for $wanted, the shell still reports the other"
    }
}

# ---------------------------------------------------------------------------
# Taskbar, clock, notifications
# ---------------------------------------------------------------------------

function Set-TaskbarAndNotifications {
    param([switch]$Apply)

    $build = [System.Environment]::OSVersion.Version.Build
    $isWin11 = $build -ge 22000
    Add-Result -Area 'Taskbar' -Item 'Windows build' -Status 'INFO' -Detail "$([System.Environment]::OSVersion.Version) ($(if ($isWin11) { 'Windows 11' } else { 'Windows 10' }))"

    # "Turn off your clock." - Chris. Win11 hides time and date with one value; the policy
    # key is what Windows 10 honours, so both go in.
    Set-PreparedRegistryValue -Area 'Taskbar' -Item 'Tray clock and date hidden' `
        -Path $ADVANCED -Name 'ShowSystrayDateTimeValueName' -Desired 0 -Apply:$Apply `
        -Detail 'Windows 11 setting' `
        -ManualRoute 'Settings > Personalization > Taskbar > Taskbar behaviors > untick "Show time and date in the System tray".'
    Set-PreparedRegistryValue -Area 'Taskbar' -Item 'Clock hidden (policy)' `
        -Path $POLICY_EXPLORER -Name 'HideClock' -Desired 1 -Apply:$Apply `
        -Detail 'Windows 10 setting, needs an Explorer restart' `
        -ManualRoute 'Only needed on Windows 10; on Windows 11 the setting above does the job.'

    # "Turn off desktop widgets."
    Set-PreparedRegistryValue -Area 'Taskbar' -Item 'Widgets button off' `
        -Path $ADVANCED -Name 'TaskbarDa' -Desired 0 -Apply:$Apply `
        -ManualRoute 'Settings > Personalization > Taskbar > turn Widgets off.'
    Set-PreparedRegistryValue -Area 'Taskbar' -Item 'News and interests off' `
        -Path $FEEDS -Name 'ShellFeedsTaskbarViewMode' -Desired 2 -Apply:$Apply `
        -Detail 'Windows 10 news feed' `
        -ManualRoute 'Only applies to Windows 10; ignore this on Windows 11.'
    Set-PreparedRegistryValue -Area 'Taskbar' -Item 'Chat button off' `
        -Path $ADVANCED -Name 'TaskbarMn' -Desired 0 -Apply:$Apply `
        -ManualRoute 'Settings > Personalization > Taskbar > turn Chat off.'
    Set-PreparedRegistryValue -Area 'Taskbar' -Item 'Task view button off' `
        -Path $ADVANCED -Name 'ShowTaskViewButton' -Desired 0 -Apply:$Apply `
        -ManualRoute 'Settings > Personalization > Taskbar > turn Task view off.'

    # "Please turn off all notifications as to avoid any unwanted pop-ups." - MPS.
    $notifyRoute = 'Settings > System > Notifications > turn Notifications off, or turn on Do not disturb.'
    Set-PreparedRegistryValue -Area 'Notifications' -Item 'Toasts disabled' `
        -Path $PUSH_NOTIFY -Name 'ToastEnabled' -Desired 0 -Apply:$Apply -ManualRoute $notifyRoute
    Set-PreparedRegistryValue -Area 'Notifications' -Item 'Global toast setting off' `
        -Path $NOTIFY_SETTINGS -Name 'NOC_GLOBAL_SETTING_TOASTS_ENABLED' -Desired 0 -Apply:$Apply -ManualRoute $notifyRoute
    Set-PreparedRegistryValue -Area 'Notifications' -Item 'Notification sounds off' `
        -Path $NOTIFY_SETTINGS -Name 'NOC_GLOBAL_SETTING_ALLOW_NOTIFICATION_SOUND' -Desired 0 -Apply:$Apply -ManualRoute $notifyRoute
}

function Restart-ShellExplorer {
    <#
      HideClock and some taskbar values only appear after Explorer reloads. Nothing but
      File Explorer windows are lost.
    #>
    $processes = @(Get-Process -Name 'explorer' -ErrorAction SilentlyContinue)
    if ($processes.Count -eq 0) {
        Add-Result -Area 'Taskbar' -Item 'Explorer restart' -Status 'SKIP' -Detail 'explorer is not running'
        return
    }
    foreach ($process in $processes) {
        try { Stop-Process -Id $process.Id -Force -ErrorAction Stop } catch { }
    }
    $deadline = (Get-Date).AddSeconds(20)
    do {
        Start-Sleep -Milliseconds 700
        $back = @(Get-Process -Name 'explorer' -ErrorAction SilentlyContinue)
    } while ($back.Count -eq 0 -and (Get-Date) -lt $deadline)

    if ($back.Count -gt 0) {
        Add-Result -Area 'Taskbar' -Item 'Explorer restart' -Status 'PASS' -Detail 'taskbar reloaded, settings are live'
    }
    else {
        Add-Result -Area 'Taskbar' -Item 'Explorer restart' -Status 'FAIL' -Detail 'explorer did not come back. Start it from Task Manager (File > Run new task > explorer.exe).'
    }
}

# ---------------------------------------------------------------------------
# Power and sleep
# ---------------------------------------------------------------------------

function Get-PowerTimeout {
    <#
      Returns the AC timeout in seconds for one power setting, or null.

      powercfg prints several hex values per setting (increment, units, minimum, maximum)
      before the two that matter, and the last two are always AC then DC. So the English
      label is tried first and the structure is the fallback, rather than grabbing the
      first hex on the line - that would silently return the increment.
    #>
    param([string]$SubGuid, [string]$SettingGuid)
    try {
        $output = @(& powercfg /query SCHEME_CURRENT $SubGuid $SettingGuid 2>&1 | ForEach-Object { "$_" })

        $labelled = $output | Where-Object { $_ -cmatch 'Current AC Power Setting Index:\s*(0x[0-9a-fA-F]+)' } | Select-Object -First 1
        if ($labelled -and $labelled -cmatch 'Current AC Power Setting Index:\s*(0x[0-9a-fA-F]+)') {
            return [Convert]::ToInt32($Matches[1], 16)
        }

        $hexLines = @($output | Where-Object { $_ -match '0x[0-9a-fA-F]{8}' })
        if ($hexLines.Count -ge 2) {
            $acLine = $hexLines[$hexLines.Count - 2]
            if ($acLine -match '(0x[0-9a-fA-F]{8})') { return [Convert]::ToInt32($Matches[1], 16) }
        }
    }
    catch { }
    return $null
}

function Set-PowerForRecording {
    param([switch]$Apply)

    $battery = Get-CimInstance -ClassName Win32_Battery -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -eq $battery) {
        Add-Result -Area 'Power' -Item 'Mains power' -Status 'PASS' -Detail 'no battery detected, desktop machine'
    }
    elseif ($battery.BatteryStatus -eq 2 -or $battery.BatteryStatus -ge 6) {
        Add-Result -Area 'Power' -Item 'Mains power' -Status 'PASS' -Detail "on mains, charge $($battery.EstimatedChargeRemaining)%"
    }
    else {
        Add-Result -Area 'Power' -Item 'Mains power' -Status 'FAIL' -Detail "on battery ($($battery.EstimatedChargeRemaining)%). MPS item 1: plug into a power outlet."
    }

    $monitor = Get-PowerTimeout -SubGuid $SUB_VIDEO -SettingGuid $VIDEOIDLE
    $standby = Get-PowerTimeout -SubGuid $SUB_SLEEP -SettingGuid $STANDBYIDLE

    if ($null -eq $monitor -and $null -eq $standby) {
        Add-Result -Area 'Power' -Item 'Sleep timeouts' -Status 'WARN' -Detail 'could not read powercfg. Set screen and sleep to Never by hand.'
    }
    elseif ($monitor -eq 0 -and $standby -eq 0) {
        Add-Result -Area 'Power' -Item 'Sleep timeouts' -Status 'PASS' -Detail 'screen and sleep already Never on AC'
    }
    elseif (-not $Apply) {
        Add-Result -Area 'Power' -Item 'Sleep timeouts' -Status 'WARN' -Detail "screen ${monitor}s, sleep ${standby}s on AC; both want 0 (Never)"
    }
    else {
        Save-Original -Bucket 'power' -Key 'monitorAc' -Value $monitor
        Save-Original -Bucket 'power' -Key 'standbyAc' -Value $standby
        $null = & powercfg /change monitor-timeout-ac 0 2>&1
        $null = & powercfg /change standby-timeout-ac 0 2>&1
        $monitorAfter = Get-PowerTimeout -SubGuid $SUB_VIDEO -SettingGuid $VIDEOIDLE
        $standbyAfter = Get-PowerTimeout -SubGuid $SUB_SLEEP -SettingGuid $STANDBYIDLE
        if ($monitorAfter -eq 0 -and $standbyAfter -eq 0) {
            Add-Result -Area 'Power' -Item 'Sleep timeouts' -Status 'PASS' -Detail "screen ${monitor}s -> Never, sleep ${standby}s -> Never (read back)"
        }
        else {
            Add-Result -Area 'Power' -Item 'Sleep timeouts' -Status 'FAIL' -Detail "after the change powercfg reports screen ${monitorAfter}s, sleep ${standbyAfter}s"
        }
    }

    Set-PreparedRegistryValue -Area 'Power' -Item 'Screen saver off' `
        -Path $DESKTOP -Name 'ScreenSaveActive' -Desired '0' -Type String -Apply:$Apply
    if ($Apply -and (Initialize-Native)) {
        $null = [AfNative]::SystemParametersInfo(0x0011, 0, $null, 0x03)  # SPI_SETSCREENSAVEACTIVE
    }
}

# ---------------------------------------------------------------------------
# Network and audio
# ---------------------------------------------------------------------------

function Test-NetworkPath {
    try {
        $route = Get-NetRoute -DestinationPrefix '0.0.0.0/0' -ErrorAction Stop |
            Sort-Object RouteMetric, InterfaceMetric | Select-Object -First 1
        $adapter = Get-NetAdapter -InterfaceIndex $route.InterfaceIndex -ErrorAction Stop
        $speed = if ($adapter.LinkSpeed) { $adapter.LinkSpeed } else { 'unknown speed' }

        if ($adapter.PhysicalMediaType -match '802.11' -or $adapter.InterfaceDescription -match 'Wi-?Fi|Wireless') {
            Add-Result -Area 'Network' -Item 'Wired connection' -Status 'FAIL' `
                -Detail "traffic is going over Wi-Fi ($($adapter.InterfaceDescription)). Chris asks for hardwired ethernet."
        }
        else {
            Add-Result -Area 'Network' -Item 'Wired connection' -Status 'PASS' `
                -Detail "$($adapter.InterfaceDescription), $speed"
        }
    }
    catch {
        Add-Result -Area 'Network' -Item 'Wired connection' -Status 'WARN' -Detail "could not resolve the default route: $($_.Exception.Message)"
    }

    try {
        $target = ([Uri]$ApiBase).Host
        $ping = Test-Connection -ComputerName $target -Count 4 -ErrorAction Stop
        # ResponseTime on Windows PowerShell 5.1, Latency on PowerShell 7.
        $times = $ping | ForEach-Object { if ($null -ne $_.Latency) { $_.Latency } else { $_.ResponseTime } }
        $average = ($times | Measure-Object -Average).Average
        # This is the round trip to East US, not the video path. A couple of hundred
        # milliseconds from outside North America is geography, not a fault - it only
        # matters if it has moved a long way from what you rehearsed against.
        $status = if ($average -lt 300) { 'PASS' } elseif ($average -lt 600) { 'WARN' } else { 'FAIL' }
        Add-Result -Area 'Network' -Item 'Round trip to the API' -Status $status -Detail ("{0:N0} ms average to {1}" -f $average, $target)
    }
    catch {
        Add-Result -Area 'Network' -Item 'Round trip to the API' -Status 'SKIP' -Detail 'ICMP blocked or unavailable; the health check below is the real test'
    }
}

function Test-AudioDevices {
    <#
      Chris's prep mail asks for a wired headset. You are deliberately going with Bluetooth,
      so this reports what is connected instead of arguing about it. The useful thing before
      a recording is confirming the headset you intend to talk into is actually paired.
    #>
    try {
        $endpoints = @(Get-PnpDevice -Class 'AudioEndpoint' -Status 'OK' -ErrorAction Stop)
        $wireless = @($endpoints | Where-Object { $_.InstanceId -match 'BTHENUM|BTHHFENUM' -or $_.FriendlyName -match 'Bluetooth' })
        if ($wireless.Count -gt 0) {
            Add-Result -Area 'Audio' -Item 'Audio devices' -Status 'INFO' `
                -Detail "$($endpoints.Count) endpoints, including $(($wireless.FriendlyName | Select-Object -First 2) -join '; ')"
        }
        else {
            Add-Result -Area 'Audio' -Item 'Audio devices' -Status 'INFO' `
                -Detail "$($endpoints.Count) endpoints, none over Bluetooth. Pair your headset if you meant to use it."
        }
    }
    catch {
        Add-Result -Area 'Audio' -Item 'Audio devices' -Status 'SKIP' -Detail 'could not enumerate audio endpoints'
    }
}

# ---------------------------------------------------------------------------
# Apps
# ---------------------------------------------------------------------------

function Close-NoisyApps {
    param([switch]$Apply)

    $found = @()
    foreach ($app in $NoisyApps) {
        $processes = @(Get-Process -Name $app.Name -ErrorAction SilentlyContinue)
        if ($processes.Count -gt 0) { $found += , @{ App = $app; Processes = $processes } }
    }

    if ($found.Count -eq 0) {
        Add-Result -Area 'Apps' -Item 'Messaging and noisy apps' -Status 'PASS' -Detail 'none of the watched apps are running'
        return
    }

    if (-not $Apply) {
        $names = ($found | ForEach-Object { $_.App.Label }) -join ', '
        Add-Result -Area 'Apps' -Item 'Messaging and noisy apps' -Status 'WARN' -Detail "running: $names"
        return
    }

    foreach ($entry in $found) {
        $label = $entry.App.Label
        foreach ($process in $entry.Processes) {
            try { $null = $process.CloseMainWindow() } catch { }
        }
        Start-Sleep -Seconds 2
        $still = @(Get-Process -Name $entry.App.Name -ErrorAction SilentlyContinue)

        if ($still.Count -gt 0 -and $Force) {
            foreach ($process in $still) {
                try { Stop-Process -Id $process.Id -Force -ErrorAction Stop } catch { }
            }
            Start-Sleep -Seconds 1
            $still = @(Get-Process -Name $entry.App.Name -ErrorAction SilentlyContinue)
        }

        if ($still.Count -eq 0) {
            Add-Result -Area 'Apps' -Item "Closed: $label" -Status 'PASS' -Detail 'process is gone'
        }
        elseif ($Force) {
            Add-Result -Area 'Apps' -Item "Closed: $label" -Status 'FAIL' -Detail "$($still.Count) process(es) survived a forced close"
        }
        else {
            Add-Result -Area 'Apps' -Item "Closed: $label" -Status 'WARN' -Detail 'ignored the close request, probably unsaved work. Close it yourself or re-run with -Force.'
        }
    }

    Add-Result -Area 'Apps' -Item 'Signed out of web clients' -Status 'MANUAL' `
        -Detail 'closing the app is not signing out of Outlook or Teams in a browser tab'
}

# ---------------------------------------------------------------------------
# Browser
# ---------------------------------------------------------------------------

function Get-BrowserPath {
    param([ValidateSet('Edge', 'Chrome')][string]$Browser)

    $roots = @($env:ProgramFiles, ${env:ProgramFiles(x86)}, $env:LOCALAPPDATA) | Where-Object { $_ }
    $suffix = if ($Browser -eq 'Edge') { 'Microsoft\Edge\Application\msedge.exe' } else { 'Google\Chrome\Application\chrome.exe' }

    foreach ($root in $roots) {
        $candidate = Join-Path $root $suffix
        if (Test-Path $candidate) { return $candidate }
    }
    return $null
}

function Test-RegistryWritable {
    param([Parameter(Mandatory)][string]$Path)
    try {
        if (Test-Path $Path) {
            $probe = '__afprep_probe'
            $null = New-ItemProperty -Path $Path -Name $probe -Value 1 -PropertyType DWord -Force -ErrorAction Stop
            Remove-ItemProperty -Path $Path -Name $probe -ErrorAction SilentlyContinue
            return $true
        }
        $null = New-Item -Path $Path -Force -ErrorAction Stop
        return $true
    }
    catch { return $false }
}

function Set-BrowserBlankStart {
    param([switch]$Apply)

    $browsers = @(
        @{ Name = 'Edge'; Policy = 'HKCU:\Software\Policies\Microsoft\Edge'; Settings = 'edge://settings/onStartup' }
        @{ Name = 'Chrome'; Policy = 'HKCU:\Software\Policies\Google\Chrome'; Settings = 'chrome://settings/onStartup' }
    )

    foreach ($browser in $browsers) {
        if (-not (Get-BrowserPath -Browser $browser.Name)) {
            Add-Result -Area 'Browser' -Item "$($browser.Name) start page" -Status 'SKIP' -Detail 'not installed'
            continue
        }

        # A managed device usually locks the whole Software\Policies subtree. Find that out
        # once, rather than reporting the same denial four times.
        if ($Apply -and -not (Test-RegistryWritable -Path $browser.Policy)) {
            Add-Result -Area 'Browser' -Item "$($browser.Name) opens about:blank" -Status 'WARN' `
                -Detail "your device policy locks $($browser.Policy). Open $($browser.Settings), choose 'Open these pages', and set about:blank. Twenty seconds, once."
            continue
        }

        $route = "Open $($browser.Settings) and set 'Open these pages' to about:blank."
        Set-PreparedRegistryValue -Area 'Browser' -Item "$($browser.Name) opens about:blank" `
            -Path $browser.Policy -Name 'RestoreOnStartup' -Desired 4 -Apply:$Apply -ManualRoute $route
        Set-PreparedRegistryValue -Area 'Browser' -Item "$($browser.Name) startup URL" `
            -Path "$($browser.Policy)\RestoreOnStartupURLs" -Name '1' -Desired 'about:blank' -Type String -Apply:$Apply -ManualRoute $route
        Set-PreparedRegistryValue -Area 'Browser' -Item "$($browser.Name) new tab blank" `
            -Path $browser.Policy -Name 'NewTabPageLocation' -Desired 'about:blank' -Type String -Apply:$Apply -ManualRoute $route
        Set-PreparedRegistryValue -Area 'Browser' -Item "$($browser.Name) home button URL" `
            -Path $browser.Policy -Name 'HomepageLocation' -Desired 'about:blank' -Type String -Apply:$Apply -ManualRoute $route
    }

    if ($Apply) {
        Add-Result -Area 'Browser' -Item 'Confirm a blank tab by eye' -Status 'MANUAL' `
            -Detail 'open the browser once and check the tab is blank. Restart it if it was already running.'
    }
}

function Open-DemoTabs {
    param([string[]]$Urls)

    $browserPath = Get-BrowserPath -Browser 'Edge'
    if (-not $browserPath) { $browserPath = Get-BrowserPath -Browser 'Chrome' }

    try {
        if ($browserPath) {
            Start-Process -FilePath $browserPath -ArgumentList $Urls
        }
        else {
            foreach ($url in $Urls) {
                Start-Process $url
                Start-Sleep -Milliseconds 1200
            }
        }
        Add-Result -Area 'Browser' -Item 'Demo tabs opened in order' -Status 'PASS' `
            -Detail "$($Urls.Count) tabs; the last one is the closing background"
    }
    catch {
        Add-Result -Area 'Browser' -Item 'Demo tabs opened in order' -Status 'FAIL' -Detail $_.Exception.Message
    }
}

# ---------------------------------------------------------------------------
# Demo readiness
# ---------------------------------------------------------------------------

function Get-DemoPrompts {
    <#
      Read the prompts out of the runbook table rather than repeating them here. Two copies
      of the same fact in this repo have already drifted into describing different demos.
    #>
    if (-not (Test-Path $Runbook)) { return @() }
    $pattern = '^\|\s*"(?<prompt>[^"]+)"\s*\|\s*`(?<verdict>[A-Z_]+)`\s*\|'
    $rows = @()
    foreach ($line in (Get-Content -Path $Runbook -Encoding UTF8)) {
        if ($line -match $pattern) {
            $rows += , [pscustomobject]@{ Prompt = $Matches['prompt']; Verdict = $Matches['verdict'] }
        }
    }
    return $rows
}

function Test-ApiHealth {
    param([string]$Base)
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    }
    catch { }
    try {
        $started = Get-Date
        $response = Invoke-RestMethod -Uri "$Base/" -Method Get -TimeoutSec 60
        $ms = ((Get-Date) - $started).TotalMilliseconds
        # 200 is not the assertion. The body saying status=ok is.
        if ($response.status -eq 'ok') {
            Add-Result -Area 'Demo' -Item 'API health' -Status 'PASS' -Detail ("status=ok, service={0}, {1:N0} ms" -f $response.service, $ms)
            return $true
        }
        Add-Result -Area 'Demo' -Item 'API health' -Status 'FAIL' -Detail "responded, but status is '$($response.status)'"
        return $false
    }
    catch {
        Add-Result -Area 'Demo' -Item 'API health' -Status 'FAIL' -Detail $_.Exception.Message
        return $false
    }
}

function Test-UptimeIssue {
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if (-not $gh) {
        Add-Result -Area 'Demo' -Item 'No open uptime issue' -Status 'SKIP' -Detail 'gh CLI not found; check github.com/issues?q=label:uptime by hand'
        return
    }
    try {
        $json = & gh issue list --repo $Repo --label uptime --state open --json number,title 2>&1
        if ($LASTEXITCODE -ne 0) {
            Add-Result -Area 'Demo' -Item 'No open uptime issue' -Status 'WARN' -Detail "gh failed: $($json | Select-Object -First 1)"
            return
        }
        # Windows PowerShell 5.1 turns an empty JSON array into a single $null element, so
        # @(...) counts 1 and an all-clear reads as an open issue. Filter before counting.
        $issues = @($json | ConvertFrom-Json | Where-Object { $_ })
        if ($issues.Count -eq 0) {
            Add-Result -Area 'Demo' -Item 'No open uptime issue' -Status 'PASS' -Detail 'the 30-minute probe has not filed anything'
        }
        else {
            $titles = ($issues | ForEach-Object { "#$($_.number) $($_.title)" }) -join '; '
            Add-Result -Area 'Demo' -Item 'No open uptime issue' -Status 'FAIL' -Detail $titles
        }
    }
    catch {
        Add-Result -Area 'Demo' -Item 'No open uptime issue' -Status 'WARN' -Detail $_.Exception.Message
    }
}

function Get-PythonCommand {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { return @{ File = $python.Source; Prefix = @() } }
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) { return @{ File = $launcher.Source; Prefix = @('-3') } }
    return $null
}

function Invoke-SmokeTest {
    $tool = Join-Path $RepoRoot 'tooling\verify_demo_prompts.py'
    if (-not (Test-Path $tool)) {
        Add-Result -Area 'Demo' -Item 'Five prompts + code generation' -Status 'FAIL' -Detail "not found at $tool"
        return
    }
    $python = Get-PythonCommand
    if (-not $python) {
        Add-Result -Area 'Demo' -Item 'Five prompts + code generation' -Status 'FAIL' -Detail 'no python on PATH'
        return
    }

    Write-Host '  ... running the smoke test against the live API. Four to six minutes.' -ForegroundColor DarkGray
    $env:PYTHONUTF8 = '1'
    Push-Location $RepoRoot
    try {
        $arguments = @($python.Prefix + @($tool, '--base', $ApiBase)) | Where-Object { $_ }
        $output = & $python.File @arguments 2>&1
        $exit = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }

    $text = ($output | Out-String)
    $logPath = Join-Path $ArtifactDir 'smoke-test.log'
    if (-not (Test-Path $ArtifactDir)) { $null = New-Item -ItemType Directory -Path $ArtifactDir -Force }
    $text | Set-Content -Path $logPath -Encoding UTF8
    $null = $script:Artifacts.Add($logPath)

    # Exit code alone is not evidence: a run that printed nothing also exits 0 if it never
    # got as far as a request. Assert on what it reported.
    $mismatchLine = [regex]::Match($text, 'mismatches:\s*(\d+)\s+of\s+(\d+)')
    $codegenLine = [regex]::Match($text, 'OK\s+(\d+)\s+chars of Q#')

    if (-not $mismatchLine.Success) {
        Add-Result -Area 'Demo' -Item 'Five prompts + code generation' -Status 'FAIL' `
            -Detail "the tool never reported a mismatch count. See $logPath"
        return
    }
    $bad = [int]$mismatchLine.Groups[1].Value
    $total = [int]$mismatchLine.Groups[2].Value

    if ($exit -eq 0 -and $bad -eq 0 -and $total -ge 5 -and $codegenLine.Success) {
        Add-Result -Area 'Demo' -Item 'Five prompts + code generation' -Status 'PASS' `
            -Detail "$total/$total verdicts matched, $($codegenLine.Groups[1].Value) chars of Q# compiled and estimated"
    }
    elseif ($exit -eq 0 -and $bad -eq 0 -and $total -ge 5) {
        Add-Result -Area 'Demo' -Item 'Five prompts + code generation' -Status 'WARN' `
            -Detail "verdicts matched but no Q# line was printed. Beat 3 is unproven. See $logPath"
    }
    else {
        Add-Result -Area 'Demo' -Item 'Five prompts + code generation' -Status 'FAIL' `
            -Detail "$bad of $total prompts drifted (exit $exit). Do not record against this. See $logPath"
    }

    $latency = [regex]::Match($text, 'latency: median ([\d.]+)s, min ([\d.]+)s, max ([\d.]+)s')
    if ($latency.Success) {
        Add-Result -Area 'Demo' -Item 'Latency today' -Status 'INFO' `
            -Detail "median $($latency.Groups[1].Value)s, max $($latency.Groups[3].Value)s. Do not quote a number on air."
    }
}

function Invoke-Evaluate {
    param([string]$Problem, [switch]$GenerateCode, [int]$TimeoutSec = 600)
    $body = @{ problem = $Problem; generate_code = [bool]$GenerateCode } | ConvertTo-Json -Compress
    return Invoke-RestMethod -Uri "$ApiBase/api/evaluate" -Method Post -Body $body `
        -ContentType 'application/json' -TimeoutSec $TimeoutSec
}

function Invoke-PreExecutedBeats {
    <#
      The storyboard promises beat 2 pre-loaded in a second tab and beat 3 pre-executed
      because code generation costs about a minute. Doing it here means it is a real
      response from today, not a screenshot from last week.
    #>
    $prompts = Get-DemoPrompts
    if ($prompts.Count -lt 5) {
        Add-Result -Area 'Beats' -Item 'Prompt table' -Status 'FAIL' `
            -Detail "parsed $($prompts.Count) prompts from README.md section 5, expected 5. The table changed shape."
        return @()
    }
    Add-Result -Area 'Beats' -Item 'Prompt table' -Status 'PASS' -Detail "$($prompts.Count) prompts read from the runbook"

    if (-not (Test-Path $ArtifactDir)) { $null = New-Item -ItemType Directory -Path $ArtifactDir -Force }
    $files = @()

    $declined = $prompts | Where-Object { $_.Verdict -ne 'QUANTUM_ADVANTAGE' } | Select-Object -First 1
    $accepted = $prompts | Where-Object { $_.Verdict -eq 'QUANTUM_ADVANTAGE' } | Select-Object -First 1

    # Beat 2: the same prompt twice, same answer. That claim gets made on camera, so it is
    # worth checking rather than hoping.
    if ($declined) {
        try {
            Write-Host "  ... beat 2: '$($declined.Prompt.Substring(0, [Math]::Min(48, $declined.Prompt.Length)))...' twice" -ForegroundColor DarkGray
            $first = Invoke-Evaluate -Problem $declined.Prompt
            $second = Invoke-Evaluate -Problem $declined.Prompt

            $path = Join-Path $ArtifactDir 'beat2-raw.json'
            $first | ConvertTo-Json -Depth 20 | Set-Content -Path $path -Encoding UTF8
            $files += $path
            $null = $script:Artifacts.Add($path)

            if ($first.verdict -ne $declined.Verdict) {
                Add-Result -Area 'Beats' -Item 'Beat 2 verdict' -Status 'FAIL' `
                    -Detail "expected $($declined.Verdict), got $($first.verdict)"
            }
            elseif ($first.verdict -eq $second.verdict -and $first.confidence -eq $second.confidence) {
                $dissent = if ($first.model_dissent -and @($first.model_dissent.PSObject.Properties).Count -gt 0) { 'recorded' } else { 'none' }
                Add-Result -Area 'Beats' -Item 'Beat 2 determinism' -Status 'PASS' `
                    -Detail "$($first.verdict) at $($first.confidence) both times, model_dissent $dissent"
            }
            else {
                Add-Result -Area 'Beats' -Item 'Beat 2 determinism' -Status 'FAIL' `
                    -Detail "same prompt gave $($first.verdict)/$($first.confidence) then $($second.verdict)/$($second.confidence). Do not claim determinism on air."
            }
        }
        catch {
            Add-Result -Area 'Beats' -Item 'Beat 2 pre-execution' -Status 'FAIL' -Detail $_.Exception.Message
        }
    }

    # Beat 3: FeMoco with code generation, which is the ~50s path.
    #
    # Generation is not deterministic. On one run here the API returned 3,990 characters of
    # Q# whose every compile attempt failed on an R1Frac type error, minutes after the same
    # prompt produced 2,784 characters that compiled and estimated cleanly. So this asks
    # again rather than reporting a red light you would have fixed by pressing go twice -
    # and it tells you how many goes it took, because that is the number that decides
    # whether you trust this beat live.
    if ($accepted) {
        $maxAttempts = 3
        $succeeded = $false
        for ($attempt = 1; $attempt -le $maxAttempts -and -not $succeeded; $attempt++) {
            try {
                Write-Host "  ... beat 3: the quantum prompt with code generation, attempt $attempt of $maxAttempts. Around a minute." -ForegroundColor DarkGray
                $response = Invoke-Evaluate -Problem $accepted.Prompt -GenerateCode

                $path = Join-Path $ArtifactDir 'beat3-raw.json'
                $response | ConvertTo-Json -Depth 20 | Set-Content -Path $path -Encoding UTF8
                if ($files -notcontains $path) {
                    $files += $path
                    $null = $script:Artifacts.Add($path)
                }

                $code = "$($response.qsharp_code)"
                $qubits = $response.estimation.physical_qubits
                $broken = @($response.resource_estimate_pareto | Where-Object { $_.error })
                $reason = $null

                if ([string]::IsNullOrWhiteSpace($code)) {
                    $reason = "no Q# came back at all. $($response.estimation.error)"
                }
                elseif ($response.estimation.error) {
                    $firstLine = (("$($response.estimation.error)" -split "`n") | Select-Object -First 1)
                    $reason = "$($code.Length) chars of Q# that did not build after $($response.estimation.attempt_count) compile attempts: $firstLine"
                }
                elseif ($null -eq $qubits) {
                    $reason = "Q# built but no physical_qubits came back. entry=$($response.estimation.entry_expression)"
                }
                elseif ($broken.Count -gt 0) {
                    $reason = "$($broken.Count) Pareto rows errored: $("$($broken[0].error)" -replace '\s+', ' ')"
                }

                if ($null -eq $reason) {
                    $succeeded = $true
                    $qsPath = Join-Path $ArtifactDir 'beat3-generated.qs'
                    $code | Set-Content -Path $qsPath -Encoding UTF8
                    if ($files -notcontains $qsPath) {
                        $files += $qsPath
                        $null = $script:Artifacts.Add($qsPath)
                    }
                    $status = if ($attempt -eq 1) { 'PASS' } else { 'WARN' }
                    $note = if ($attempt -eq 1) { '' } else { " It took $attempt requests - generation is flaky, so keep the fallback recording to hand." }
                    Add-Result -Area 'Beats' -Item 'Beat 3 Q# and resource estimate' -Status $status `
                        -Detail "$($code.Length) chars of Q#, $qubits physical qubits, $(@($response.resource_estimate_pareto).Count) clean Pareto rows.$note"
                }
                elseif ($attempt -eq $maxAttempts) {
                    Add-Result -Area 'Beats' -Item 'Beat 3 Q# and resource estimate' -Status 'FAIL' `
                        -Detail "$maxAttempts requests all failed. Last: $reason"
                }
                else {
                    Write-Host "      attempt $attempt failed: $reason" -ForegroundColor DarkYellow
                }
            }
            catch {
                if ($attempt -eq $maxAttempts) {
                    Add-Result -Area 'Beats' -Item 'Beat 3 pre-execution' -Status 'FAIL' -Detail $_.Exception.Message
                }
                else {
                    Write-Host "      attempt $attempt errored: $($_.Exception.Message)" -ForegroundColor DarkYellow
                }
            }
        }
    }

    return $files
}

function Test-SiteReachable {
    try {
        $response = Invoke-WebRequest -Uri $SiteUrl -TimeoutSec 60 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Add-Result -Area 'Demo' -Item 'Site reachable' -Status 'PASS' -Detail "HTTP 200 from $SiteUrl"
            Add-Result -Area 'Demo' -Item 'Site is not in DEMO MODE' -Status 'MANUAL' `
                -Detail 'DEMO MODE is decided in the browser after the API call. Click one evaluation through and look.'
        }
        else {
            Add-Result -Area 'Demo' -Item 'Site reachable' -Status 'FAIL' -Detail "HTTP $($response.StatusCode)"
        }
    }
    catch {
        Add-Result -Area 'Demo' -Item 'Site reachable' -Status 'FAIL' -Detail $_.Exception.Message
    }
}

# ---------------------------------------------------------------------------
# The things a script cannot do
# ---------------------------------------------------------------------------

function Show-ManualChecklist {
    param([switch]$DayOf)

    Write-Section 'Left for you (no script can do these)'

    $dayBefore = @(
        'Decide the name and title for your display card and send it to Chris.',
        'Hardwired ethernet in, and nothing else on the network hammering the uplink.',
        'Headset charged and paired, and tested in StreamYard - listen back before you commit. Windows can drop a Bluetooth headset to the hands-free profile once the browser opens the mic, which sounds much worse.',
        'Camera at or above eye level, arm''s length away, three feet of space behind your head.',
        'Two lights at a diagonal in front of you. No window behind you.',
        'Muted solid colours, no logos, no tight patterns, no noisy jewellery, no all-white.',
        'Quiet room. Sit still for a minute and listen for fans, aircon and corridor noise.',
        'Browser zoom set so the verdict and the Troyer filters are legible at 1080p.',
        'Nothing confidential on the desktop, in your tabs, or in your bookmarks bar.',
        'Full timed dry run, including one deliberate "no".',
        'Record a fallback video of each prompt in README.md section 5.'
    )
    $onTheDay = @(
        'Phone and any other noise-making device off, not just silent.',
        'Fallback recording open and ready before you start.',
        'StreamYard opened and tested; camera, mic and screen share all confirmed.',
        'Notes on screen near the webcam, big enough to read without leaning in.',
        'Speak to Scott, not the camera. Do not open an answer with "by the time you see this".'
    )

    $items = if ($DayOf) { $onTheDay } else { $dayBefore + $onTheDay }
    foreach ($item in $items) { Write-Host "  [ ] $item" -ForegroundColor Cyan }
}

# ---------------------------------------------------------------------------
# Restore
# ---------------------------------------------------------------------------

function Restore-RegistryEntries {
    <#
      Put captured registry values back. A captured null means the value did not exist
      before, so restoring it means removing it, not writing an empty string.
    #>
    param([Parameter(Mandatory)][hashtable]$Entries, [string]$Area = 'Restore')

    foreach ($key in @($Entries.Keys)) {
        $parts = $key -split '\|'
        if ($parts.Count -ne 3) { continue }
        $path = $parts[0]; $name = $parts[1]; $type = $parts[2]
        $original = $Entries[$key]
        try {
            if ($null -eq $original -or "$original" -eq '') {
                Remove-ItemProperty -Path $path -Name $name -ErrorAction SilentlyContinue
                $after = Get-RegValue -Path $path -Name $name
                if ($null -eq $after) { Add-Result -Area $Area -Item $name -Status 'SET' -Detail 'removed (it did not exist before)' }
                else { Add-Result -Area $Area -Item $name -Status 'FAIL' -Detail "still reads '$after'" }
            }
            else {
                Set-RegValue -Path $path -Name $name -Value $original -Type $type
                $after = Get-RegValue -Path $path -Name $name
                if ("$after" -eq "$original") { Add-Result -Area $Area -Item $name -Status 'SET' -Detail "back to '$original'" }
                else { Add-Result -Area $Area -Item $name -Status 'FAIL' -Detail "wanted '$original', reads '$after'" }
            }
        }
        catch {
            Add-Result -Area $Area -Item $name -Status 'FAIL' -Detail $_.Exception.Message
        }
    }
}

function Restore-Machine {
    if (-not (Import-PrepState)) {
        Add-Result -Area 'Restore' -Item 'State file' -Status 'FAIL' -Detail "nothing to restore: $StatePath does not exist"
        return
    }
    Add-Result -Area 'Restore' -Item 'State file' -Status 'INFO' -Detail "captured $($script:State.capturedUtc) UTC"

    # Desktop icons come out of the registry loop: writing HideIcons back does not put the
    # icons back on screen. Decide from the captured value, then ask the shell to do it.
    # No capture means prep found them the way it wanted and changed nothing, so leaving
    # them alone is the correct restore - the alternative un-hides icons you hid yourself.
    $iconKey = "$ADVANCED|HideIcons|DWord"
    $restoreIcons = $script:State.registry.ContainsKey($iconKey)
    $iconsWereVisible = $true
    if ($restoreIcons) {
        $iconsWereVisible = ("$($script:State.registry[$iconKey])" -ne '1')
        $script:State.registry.Remove($iconKey)
    }

    Restore-RegistryEntries -Entries $script:State.registry

    if ($script:State.wallpaper.Count -gt 0 -and (Initialize-Native)) {
        $paper = $script:State.wallpaper['path']
        $colour = $script:State.wallpaper['background']
        if ($colour) { Set-RegValue -Path $COLORS -Name 'Background' -Value $colour -Type String }
        if ($script:State.wallpaper['style']) { Set-RegValue -Path $DESKTOP -Name 'WallpaperStyle' -Value $script:State.wallpaper['style'] -Type String }
        if ($script:State.wallpaper['tile']) { Set-RegValue -Path $DESKTOP -Name 'TileWallpaper' -Value $script:State.wallpaper['tile'] -Type String }
        if ($paper) {
            $ok = [AfNative]::SystemParametersInfo(0x0014, 0, $paper, 0x03)
            $status = if ($ok) { 'PASS' } else { 'FAIL' }
            Add-Result -Area 'Restore' -Item 'Wallpaper' -Status $status -Detail $paper
        }
        else {
            Add-Result -Area 'Restore' -Item 'Wallpaper' -Status 'INFO' -Detail 'there was no wallpaper picture before'
        }
    }

    if ($script:State.display.Count -gt 0) {
        $w = $script:State.display['width']; $h = $script:State.display['height']
        if ($w -and $h) { Set-DisplayResolution -TargetWidth ([int]$w) -TargetHeight ([int]$h) -Apply }
    }

    if ($script:State.power.Count -gt 0) {
        $monitor = $script:State.power['monitorAc']
        $standby = $script:State.power['standbyAc']
        if ($null -ne $monitor) { $null = & powercfg /change monitor-timeout-ac ([int]([int]$monitor / 60)) 2>&1 }
        if ($null -ne $standby) { $null = & powercfg /change standby-timeout-ac ([int]([int]$standby / 60)) 2>&1 }
        $monitorAfter = Get-PowerTimeout -SubGuid $SUB_VIDEO -SettingGuid $VIDEOIDLE
        Add-Result -Area 'Restore' -Item 'Sleep timeouts' -Status 'SET' -Detail "screen back to ${monitorAfter}s on AC"
    }

    if ($restoreIcons) {
        Set-DesktopIconVisibility -Visible $iconsWereVisible -Apply
    }
    else {
        Add-Result -Area 'Restore' -Item 'Desktop icons' -Status 'INFO' -Detail 'prep did not change them, so they are left alone'
    }

    Remove-Item -Path $StatePath -Force -ErrorAction SilentlyContinue
    Add-Result -Area 'Restore' -Item 'State file' -Status 'INFO' -Detail 'consumed and deleted'
    Write-Host ''
    Write-Host '  Sign out and back in (or restart Explorer) if the clock is still hidden.' -ForegroundColor Yellow
}

# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

function Invoke-SelfTest {
    Write-Section 'Self-test: does this script''s machinery actually work'

    # 1. Registry write / read-back / removal, on a scratch key.
    $scratch = 'HKCU:\Software\AzureFridayPrepSelfTest'
    try {
        Set-RegValue -Path $scratch -Name 'Probe' -Value 41 -Type DWord
        $read = Get-RegValue -Path $scratch -Name 'Probe'
        if ($read -eq 41) { Add-Result -Area 'SelfTest' -Item 'Registry write and read-back' -Status 'PASS' -Detail 'wrote 41, read 41' }
        else { Add-Result -Area 'SelfTest' -Item 'Registry write and read-back' -Status 'FAIL' -Detail "read '$read'" }

        Remove-ItemProperty -Path $scratch -Name 'Probe' -ErrorAction SilentlyContinue
        $gone = Get-RegValue -Path $scratch -Name 'Probe'
        if ($null -eq $gone) { Add-Result -Area 'SelfTest' -Item 'Registry removal' -Status 'PASS' -Detail 'value is gone, so -Restore can un-set things' }
        else { Add-Result -Area 'SelfTest' -Item 'Registry removal' -Status 'FAIL' -Detail "still reads '$gone'" }
    }
    finally {
        Remove-Item -Path $scratch -Recurse -Force -ErrorAction SilentlyContinue
    }

    # 2. Missing values must read as null, not throw. -Restore depends on that.
    $absent = Get-RegValue -Path 'HKCU:\Software\AzureFridayPrepSelfTest\Nope' -Name 'Nothing'
    if ($null -eq $absent) { Add-Result -Area 'SelfTest' -Item 'Absent value reads as null' -Status 'PASS' -Detail 'no exception' }
    else { Add-Result -Area 'SelfTest' -Item 'Absent value reads as null' -Status 'FAIL' -Detail "got '$absent'" }

    # 3. Display interop.
    $dm = Get-CurrentMode
    if ($dm -and $dm.dmPelsWidth -gt 0) {
        Add-Result -Area 'SelfTest' -Item 'Display mode read' -Status 'PASS' -Detail "$($dm.dmPelsWidth)x$($dm.dmPelsHeight) at $($dm.dmDisplayFrequency)Hz"
    }
    else {
        Add-Result -Area 'SelfTest' -Item 'Display mode read' -Status 'FAIL' -Detail 'EnumDisplaySettings returned nothing'
    }

    # 4. Desktop window handle, needed to move icons without restarting Explorer. Toggling
    #    twice proves the mechanism works and leaves the desktop exactly as it was, and it
    #    asserts what is on screen rather than what the registry says.
    if (Initialize-Native) {
        $defView = [AfNative]::FindDefView()
        if ($defView -ne [IntPtr]::Zero) {
            Add-Result -Area 'SelfTest' -Item 'Desktop window found' -Status 'PASS' -Detail "SHELLDLL_DefView at $defView"

            $before = [AfNative]::IconsVisible()
            $null = [AfNative]::ToggleIcons()
            Start-Sleep -Milliseconds 700
            $mid = [AfNative]::IconsVisible()
            $null = [AfNative]::ToggleIcons()
            Start-Sleep -Milliseconds 700
            $after = [AfNative]::IconsVisible()

            if ($before -ge 0 -and $mid -ne $before -and $after -eq $before) {
                Add-Result -Area 'SelfTest' -Item 'Desktop icon toggle' -Status 'PASS' `
                    -Detail "on screen: $before -> $mid -> $after (1 visible, 0 hidden)"
            }
            else {
                Add-Result -Area 'SelfTest' -Item 'Desktop icon toggle' -Status 'FAIL' `
                    -Detail "on screen: $before -> $mid -> $after, expected it to flip and come back"
            }
        }
        else {
            Add-Result -Area 'SelfTest' -Item 'Desktop window found' -Status 'WARN' -Detail 'not found; icon hiding will fall back to the registry and need an Explorer restart'
        }

        # CDS_TEST asks the adapter whether it would accept the mode. It changes nothing,
        # and it is the same code path -Prep uses, so a pass here means the real one works.
        $accepted = [AfNative]::TrySetResolution($Width, $Height, $true)
        if ($accepted -eq 0) {
            Add-Result -Area 'SelfTest' -Item 'Resolution change accepted' -Status 'PASS' -Detail "the adapter would accept ${Width}x${Height} (test call, nothing changed)"
        }
        else {
            Add-Result -Area 'SelfTest' -Item 'Resolution change accepted' -Status 'FAIL' -Detail "ChangeDisplaySettings test returned $accepted for ${Width}x${Height}"
        }
    }

    # 5. powercfg parsing.
    $monitor = Get-PowerTimeout -SubGuid $SUB_VIDEO -SettingGuid $VIDEOIDLE
    if ($null -ne $monitor) { Add-Result -Area 'SelfTest' -Item 'powercfg parsing' -Status 'PASS' -Detail "screen timeout on AC reads ${monitor}s" }
    else { Add-Result -Area 'SelfTest' -Item 'powercfg parsing' -Status 'WARN' -Detail 'could not parse powercfg output on this locale' }

    # 6. The runbook table still parses. If it does not, the pre-executed beats would
    #    quietly check nothing.
    $prompts = Get-DemoPrompts
    if ($prompts.Count -ge 5) {
        Add-Result -Area 'SelfTest' -Item 'Runbook prompt table' -Status 'PASS' -Detail "$($prompts.Count) prompts, first verdict $($prompts[0].Verdict)"
    }
    else {
        Add-Result -Area 'SelfTest' -Item 'Runbook prompt table' -Status 'FAIL' -Detail "parsed $($prompts.Count) from $Runbook, expected 5"
    }

    # 7. The apply-then-restore round trip, on a scratch key. This is the machinery that
    #    promises to give the machine back, so it is worth more than a green tick on a
    #    setting that was never un-set.
    $scratch2 = 'HKCU:\Software\AzureFridayPrepSelfTest'
    $savedState = $script:State['registry']
    $script:State['registry'] = @{}
    try {
        # 7a. A value that did not exist before must end up removed, not blanked.
        Set-PreparedRegistryValue -Area 'SelfTest' -Item 'Round trip: new value written' `
            -Path $scratch2 -Name 'Fresh' -Desired 1 -Apply
        Restore-RegistryEntries -Entries $script:State['registry'] -Area 'SelfTest'
        $fresh = Get-RegValue -Path $scratch2 -Name 'Fresh'
        if ($null -eq $fresh) { Add-Result -Area 'SelfTest' -Item 'Round trip: new value removed' -Status 'PASS' -Detail 'gone, as it was before' }
        else { Add-Result -Area 'SelfTest' -Item 'Round trip: new value removed' -Status 'FAIL' -Detail "still reads '$fresh'" }

        # 7b. A value that did exist must come back with its old contents.
        $script:State['registry'] = @{}
        Set-RegValue -Path $scratch2 -Name 'Existing' -Value 7 -Type DWord
        Set-PreparedRegistryValue -Area 'SelfTest' -Item 'Round trip: existing value changed' `
            -Path $scratch2 -Name 'Existing' -Desired 9 -Apply
        $changed = Get-RegValue -Path $scratch2 -Name 'Existing'
        Restore-RegistryEntries -Entries $script:State['registry'] -Area 'SelfTest'
        $restored = Get-RegValue -Path $scratch2 -Name 'Existing'
        if ($changed -eq 9 -and $restored -eq 7) {
            Add-Result -Area 'SelfTest' -Item 'Round trip: existing value restored' -Status 'PASS' -Detail '7 -> 9 -> 7'
        }
        else {
            Add-Result -Area 'SelfTest' -Item 'Round trip: existing value restored' -Status 'FAIL' -Detail "changed to '$changed', restored to '$restored', wanted 9 then 7"
        }
    }
    finally {
        $script:State['registry'] = $savedState
        Remove-Item -Path $scratch2 -Recurse -Force -ErrorAction SilentlyContinue
    }

    # 8. Watch a check fail on purpose. A health check that cannot go red is decoration.
    Write-Host '  The next red line is deliberate: the health check is being pointed at a dead port.' -ForegroundColor DarkGray
    $before = $script:Results.Count
    $null = Test-ApiHealth -Base 'http://127.0.0.1:9'
    $recorded = $script:Results[$script:Results.Count - 1]
    $script:Results.RemoveRange($before, $script:Results.Count - $before)
    if ($recorded.Status -eq 'FAIL') {
        Add-Result -Area 'SelfTest' -Item 'Health check goes red when it should' -Status 'PASS' `
            -Detail 'a dead port produced FAIL, so a green health check means something'
    }
    else {
        Add-Result -Area 'SelfTest' -Item 'Health check goes red when it should' -Status 'FAIL' `
            -Detail "a dead port produced '$($recorded.Status)'. Do not trust a green health check."
    }
}

# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

function Invoke-MachineSection {
    param([switch]$Apply)

    Write-Section 'Display and desktop'
    Set-DisplayResolution -TargetWidth $Width -TargetHeight $Height -Apply:$Apply
    Test-MonitorCount
    Set-SolidBackground -Hex $BackgroundColor -Apply:$Apply
    Set-DesktopIconVisibility -Visible $false -Apply:$Apply

    Write-Section 'Taskbar and notifications'
    Set-TaskbarAndNotifications -Apply:$Apply

    Write-Section 'Power'
    Set-PowerForRecording -Apply:$Apply

    Write-Section 'Browser'
    Set-BrowserBlankStart -Apply:$Apply

    Write-Section 'Apps'
    if ($SkipAppClose -and $Apply) {
        Add-Result -Area 'Apps' -Item 'Messaging and noisy apps' -Status 'SKIP' -Detail '-SkipAppClose was passed'
    }
    else {
        Close-NoisyApps -Apply:$Apply
    }

    Write-Section 'Hardware'
    Test-NetworkPath
    Test-AudioDevices
}

function Invoke-ReadinessSection {
    param([switch]$RunSmoke, [switch]$PreExecute, [switch]$Tabs)

    Write-Section 'Demo readiness'
    $healthy = Test-ApiHealth -Base $ApiBase
    Test-SiteReachable
    Test-UptimeIssue

    if ($RunSmoke -and $healthy) { Invoke-SmokeTest }
    elseif ($RunSmoke) { Add-Result -Area 'Demo' -Item 'Five prompts + code generation' -Status 'SKIP' -Detail 'API health failed, so the smoke test would only repeat it' }

    $beatFiles = @()
    if ($PreExecute -and $healthy) {
        Write-Section 'Pre-executed beats'
        $beatFiles = Invoke-PreExecutedBeats
    }

    if ($Tabs) {
        Write-Section 'Tabs'
        $urls = @($SiteUrl)
        foreach ($file in $beatFiles) { $urls += ([Uri]$file).AbsoluteUri }
        $urls += $CtaUrl   # last tab is the closing background - Chris asks for this
        if (-not $NoTabs) { Open-DemoTabs -Urls $urls }
        else { Add-Result -Area 'Browser' -Item 'Demo tabs opened in order' -Status 'SKIP' -Detail '-NoTabs was passed' }
    }
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

Write-Host ''
Write-Host 'Azure Friday - Quantum Advantage Evaluator' -ForegroundColor White
Write-Host "Machine prep, mode: $Mode" -ForegroundColor White
Write-Host "Repo: $RepoRoot" -ForegroundColor DarkGray
Write-Host "Artifacts: $ArtifactDir" -ForegroundColor DarkGray
if ($Mode -eq 'Check') { Write-Host 'Nothing will be changed.' -ForegroundColor DarkGray }

switch ($Mode) {
    'SelfTest' {
        Invoke-SelfTest
    }
    'Restore' {
        Write-Section 'Restoring the settings this script changed'
        Restore-Machine
    }
    'Check' {
        $null = Import-PrepState
        Invoke-MachineSection
        Invoke-ReadinessSection
        Show-ManualChecklist
    }
    'PreFlight' {
        $null = Import-PrepState
        Invoke-MachineSection
        Invoke-ReadinessSection -RunSmoke:(-not $SkipSmokeTest) -PreExecute:(-not $SkipPreExecute) -Tabs
        Show-ManualChecklist -DayOf
    }
    'Prep' {
        $null = Import-PrepState
        Invoke-MachineSection -Apply
        if (-not $NoExplorerRestart) {
            Write-Section 'Applying taskbar changes'
            Restart-ShellExplorer
        }
        else {
            Add-Result -Area 'Taskbar' -Item 'Explorer restart' -Status 'SKIP' -Detail '-NoExplorerRestart was passed; sign out and back in to apply the clock change'
        }
        Invoke-ReadinessSection
        Export-PrepState
        Show-ManualChecklist
    }
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

Write-Section 'Summary'

$failed = @($script:Results | Where-Object { $_.Status -eq 'FAIL' })
$warned = @($script:Results | Where-Object { $_.Status -eq 'WARN' })
$passed = @($script:Results | Where-Object { $_.Status -in @('PASS', 'SET') })

Write-Host ("  {0} done, {1} to look at, {2} blocking" -f $passed.Count, $warned.Count, $failed.Count)

if ($warned.Count -gt 0) {
    Write-Host ''
    Write-Host '  Look at:' -ForegroundColor Yellow
    foreach ($result in $warned) { Write-Host "    - $($result.Item): $($result.Detail)" -ForegroundColor Yellow }
}
if ($failed.Count -gt 0) {
    Write-Host ''
    Write-Host '  Blocking:' -ForegroundColor Red
    foreach ($result in $failed) { Write-Host "    - $($result.Item): $($result.Detail)" -ForegroundColor Red }
}

if ($script:Artifacts.Count -gt 0) {
    Write-Host ''
    Write-Host '  Files written:' -ForegroundColor DarkGray
    foreach ($artifact in $script:Artifacts) { Write-Host "    $artifact" -ForegroundColor DarkGray }
}

if ($Mode -eq 'Prep') {
    Write-Host ''
    Write-Host "  Undo all of this afterwards with: .\Prep-DemoMachine.ps1 -Restore" -ForegroundColor DarkGray
}

Write-Host ''
if ($failed.Count -gt 0) { exit 1 }
exit 0
