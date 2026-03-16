$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "Virtual environment python not found at $Python"
}

Write-Host "Starting local API server on http://localhost:9000 ..."
$apiProcess = Start-Process -FilePath $Python -ArgumentList "-m", "src.api.local_server", "--host", "localhost", "--port", "9000" -WorkingDirectory $Root -PassThru

Start-Sleep -Seconds 1

Write-Host "Starting static web server on http://localhost:8084 ..."
$webProcess = Start-Process -FilePath $Python -ArgumentList "-m", "http.server", "8084", "--bind", "localhost", "--directory", "webapp" -WorkingDirectory $Root -PassThru

Write-Host ""
Write-Host "Local profile started."
Write-Host "Web UI: http://localhost:8084"
Write-Host "API:    http://localhost:9000"
Write-Host ""
Write-Host "Press Enter to stop both servers..."
[void][System.Console]::ReadLine()

if (-not $apiProcess.HasExited) {
    Stop-Process -Id $apiProcess.Id -Force
}
if (-not $webProcess.HasExited) {
    Stop-Process -Id $webProcess.Id -Force
}

Write-Host "Local profile stopped."
