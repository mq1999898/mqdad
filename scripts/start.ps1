$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Exe = Join-Path $Root '.venv\Scripts\ard-intelligence.exe'
if (-not (Test-Path $Exe)) { throw 'ARD is not installed. Run .\scripts\install.ps1 first.' }
& $Exe
exit $LASTEXITCODE
