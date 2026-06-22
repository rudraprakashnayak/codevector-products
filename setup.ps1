# Run after you set DATABASE_URL in .env
# Usage: .\setup.ps1

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env not found. Copy .env.example to .env and paste your DATABASE_URL." -ForegroundColor Red
    exit 1
}

Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "Applying schema..." -ForegroundColor Cyan
python scripts/apply_schema.py

Write-Host "Seeding 200,000 products (takes a few seconds)..." -ForegroundColor Cyan
python scripts/seed.py

Write-Host ""
Write-Host "Done! Start the server with:" -ForegroundColor Green
Write-Host "  uvicorn app.main:app --reload"
Write-Host ""
Write-Host "Then open http://127.0.0.1:8000"
