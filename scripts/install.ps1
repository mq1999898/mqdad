param(
    [switch]$SkipTests
)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw 'Python 3.10+ is required.' }
python -m venv .venv
$Python = Join-Path $Root '.venv\Scripts\python.exe'
& $Python -m pip install --upgrade pip
& $Python -m pip install -e '.[desktop,test,ssh]'
if (-not $SkipTests) { & $Python -m pytest }
Write-Host 'Installation complete. Start the app with: .\scripts\start.ps1'
