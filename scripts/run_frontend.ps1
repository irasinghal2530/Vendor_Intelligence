param(
  [int]$Port = 8501,
  [string]$BackendUrl = $null
)

$ErrorActionPreference = "Stop"

Set-Location (Split-Path $PSScriptRoot -Parent)

if (Test-Path ".\.venv\Scripts\Activate.ps1") {
  . .\.venv\Scripts\Activate.ps1
}

function Get-PortOwnerPid([int]$p) {
  try {
    $c = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction Stop | Select-Object -First 1
    return $c.OwningProcess
  } catch {
    return $null
  }
}

$ownerPid = Get-PortOwnerPid $Port
if ($ownerPid) {
  $proc = Get-Process -Id $ownerPid -ErrorAction SilentlyContinue
  $suffix = ""
  if ($proc -and $proc.ProcessName) {
    $suffix = " ($($proc.ProcessName))"
  }
  Write-Host "Port $Port is already in use by PID $ownerPid$suffix"
  Write-Host "Stop it with: Stop-Process -Id $ownerPid -Force"
  Write-Host "Or run frontend on a different port: .\scripts\run_frontend.ps1 -Port 8502"
  exit 1
}

# Ensure BACKEND_URL exists for Streamlit (frontend/app.py requires it)
if ($BackendUrl) {
  $env:BACKEND_URL = $BackendUrl
} elseif (-not $env:BACKEND_URL) {
  $env:BACKEND_URL = "http://127.0.0.1:8000"
}

streamlit run frontend/app.py --server.port $Port --server.address 127.0.0.1

