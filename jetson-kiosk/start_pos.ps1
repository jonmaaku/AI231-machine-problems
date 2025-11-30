# Quick Start Script for Jetson POS System (Windows)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Jetson POS System - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
    pip install --upgrade pip
    pip install -r requirements.txt
    
    Write-Host "✓ Setup complete!" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Check if YOLO model exists
if (-not (Test-Path "yolov8n.pt")) {
    Write-Host "Downloading YOLO model (first time only)..." -ForegroundColor Yellow
    python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
}

# Start server
Write-Host ""
Write-Host "Starting POS server..." -ForegroundColor Green
Write-Host ""
Write-Host "Access the POS system at:"
Write-Host "  → http://localhost:8000/pos.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server"
Write-Host ""

python server.py
