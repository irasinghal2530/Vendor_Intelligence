$ErrorActionPreference = "Stop"

Set-Location (Split-Path $PSScriptRoot -Parent)

if (-not (Test-Path ".\.venv")) {
  python -m venv .venv
}

. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host ""
Write-Host "Setup complete."
Write-Host "Backend:  .\\scripts\\run_backend.ps1"
Write-Host "Frontend: .\\scripts\\run_frontend.ps1"

