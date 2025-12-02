# Genome Cleaner - Helper Script
# This script activates the virtual environment and runs the Streamlit application

Write-Host "🧬 Genome Cleaner - Starting Application..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create a virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor Yellow
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# Check if streamlit is installed
Write-Host "🔍 Checking dependencies..." -ForegroundColor Cyan
$streamlitCheck = & python -c "import streamlit; print('OK')" 2>&1

if ($streamlitCheck -ne "OK") {
    Write-Host "❌ Error: Streamlit not installed in virtual environment!" -ForegroundColor Red
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Run the application
Write-Host ""
Write-Host "🚀 Starting Streamlit application..." -ForegroundColor Green
Write-Host "📱 The app will open in your browser at http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host ""

streamlit run app.py
