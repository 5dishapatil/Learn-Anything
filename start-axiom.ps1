# Axiom OS — Windows PowerShell Startup Script
$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  AXIOM OS — Personal AI Research, Learning & Creation OS   " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"

Write-Host "[1/3] Checking Backend Python Environment & Migrations..." -ForegroundColor Yellow
Push-Location $BackendDir
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    & .\.venv\Scripts\python.exe -m pip install -q wheel
    $env:DISABLE_SQLALCHEMY_CEXT = "1"
    & .\.venv\Scripts\python.exe -m pip install -q --no-binary sqlalchemy --no-build-isolation "sqlalchemy==2.0.36"
    & .\.venv\Scripts\python.exe -m pip install -q -r requirements.txt
}
& .\.venv\Scripts\python.exe -m alembic upgrade head
Pop-Location

Write-Host "[2/3] Checking Frontend Dependencies..." -ForegroundColor Yellow
Push-Location $FrontendDir
if (-not (Test-Path "node_modules")) {
    npm install --no-audit --no-fund
    node node_modules/esbuild/install.js 2>$null
}
Pop-Location

Write-Host "[3/3] Starting Backend (:8000) and Frontend (:5173)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$BackendDir'; .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$FrontendDir'; npm run dev -- --host 127.0.0.1 --port 5173"

Write-Host "Axiom OS Backend API Docs : http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "Axiom OS Web Application  : http://127.0.0.1:5173" -ForegroundColor Cyan
