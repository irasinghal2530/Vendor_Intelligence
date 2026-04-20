param(
  [int]$Port = 8000
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
  Write-Host "Or run backend on a different port: .\scripts\run_backend.ps1 -Port 8001"
  exit 1
}

python -m uvicorn backend.main:app --host 127.0.0.1 --port $Port

