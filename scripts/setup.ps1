$ErrorActionPreference = "Stop"

Set-Location (Split-Path $PSScriptRoot -Parent)

if (-not (Test-Path ".\.venv")) {
  python -m venv .venv
}

$venvPy = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
  Write-Error "Expected venv python at $venvPy"
}

# Broken venvs sometimes ship without pip; ensurepip installs it into the venv only.
& $venvPy -m ensurepip --upgrade 2>$null

& $venvPy -m pip install --upgrade pip
& $venvPy -m pip install -r requirements.txt

Write-Host ""
Write-Host "Setup complete."
Write-Host "Backend:  .\\scripts\\run_backend.ps1"
Write-Host "Frontend: .\\scripts\\run_frontend.ps1"

