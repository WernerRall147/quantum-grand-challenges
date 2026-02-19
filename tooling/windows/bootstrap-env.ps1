param(
    [string]$PythonDir = "$env:LOCALAPPDATA\Programs\Python\Python311",
    [string]$MakeDir = "C:\Program Files (x86)\GnuWin32\bin",
    [switch]$HeadlessPlots
)

$pathsToPrepend = @()

if (Test-Path (Join-Path $PythonDir "python.exe")) {
    $pathsToPrepend += $PythonDir
    $pythonScripts = Join-Path $PythonDir "Scripts"
    if (Test-Path $pythonScripts) {
        $pathsToPrepend += $pythonScripts
    }
} else {
    Write-Warning "Python not found at $PythonDir. Install Python 3.11 or pass -PythonDir."
}

if (Test-Path (Join-Path $MakeDir "make.exe")) {
    $pathsToPrepend += $MakeDir
} else {
    Write-Warning "GNU Make not found at $MakeDir. Install GnuWin32.Make or pass -MakeDir."
}

if ($pathsToPrepend.Count -gt 0) {
    $env:Path = (($pathsToPrepend -join ';') + ';' + $env:Path)
}

# Force UTF-8 output so scripts that print symbols do not fail under cp1252.
$env:PYTHONUTF8 = "1"

if ($HeadlessPlots.IsPresent) {
    # Prevent matplotlib show() from blocking in terminal-only sessions.
    $env:MPLBACKEND = "Agg"
}

Write-Host "Quantum Grand Challenges Windows environment bootstrapped." -ForegroundColor Green
Write-Host "  python: $(Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue)"
Write-Host "  make:   $(Get-Command make -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue)"
Write-Host "  PYTHONUTF8=$env:PYTHONUTF8"
if ($HeadlessPlots.IsPresent) {
    Write-Host "  MPLBACKEND=$env:MPLBACKEND"
}

Write-Host ""
Write-Host "Usage in current shell:" -ForegroundColor Cyan
Write-Host "  . .\tooling\windows\bootstrap-env.ps1 -HeadlessPlots"
