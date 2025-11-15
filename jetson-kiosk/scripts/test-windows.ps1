# Windows Test Script for Camera Kiosk
# Run this to test on Windows without Jetson

Write-Host "========================================" -ForegroundColor Green
Write-Host "Camera Kiosk - Windows Test" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$ProjectDir = Split-Path -Parent $PSScriptRoot

# Test 1: Check Python
Write-Host "Test 1: Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 2: Check if virtual environment exists
Write-Host "Test 2: Checking virtual environment..." -ForegroundColor Yellow
$venvPath = Join-Path $ProjectDir "venv"
if (Test-Path $venvPath) {
    Write-Host "✓ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "⚠ Virtual environment not found. Creating..." -ForegroundColor Yellow
    Set-Location $ProjectDir
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

Write-Host ""

# Test 3: Activate virtual environment and install dependencies
Write-Host "Test 3: Installing dependencies..." -ForegroundColor Yellow
Set-Location $ProjectDir
& "$venvPath\Scripts\Activate.ps1"

# Check if dependencies are installed
$depCheck = python -c "import fastapi, uvicorn, cv2" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies already installed" -ForegroundColor Green
} else {
    Write-Host "Installing packages..." -ForegroundColor Yellow
    pip install -q fastapi uvicorn opencv-python python-multipart numpy
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
}

Write-Host ""

# Test 4: Check for camera
Write-Host "Test 4: Testing camera access..." -ForegroundColor Yellow

$pythonCode = @'
import cv2
import sys
try:
    cam = cv2.VideoCapture(0)
    if cam.isOpened():
        ret, frame = cam.read()
        if ret:
            print('Camera working: {}x{}'.format(frame.shape[1], frame.shape[0]))
            cam.release()
            sys.exit(0)
    print('Camera not accessible')
    sys.exit(1)
except Exception as e:
    print('Camera error: {}'.format(str(e)))
    sys.exit(1)
'@

$cameraTest = python -c $pythonCode 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ $cameraTest" -ForegroundColor Green
    $hasCamera = $true
} else {
    Write-Host "⚠ $cameraTest" -ForegroundColor Yellow
    Write-Host "  Don't worry - you can still test with virtual camera!" -ForegroundColor Cyan
    $hasCamera = $false
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Test Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Offer to start server
Write-Host "Ready to test! Choose an option:" -ForegroundColor Cyan
Write-Host ""
if ($hasCamera) {
    Write-Host "1. Start server with REAL camera" -ForegroundColor White
    Write-Host "2. Start server with VIRTUAL camera (synthetic video)" -ForegroundColor White
    Write-Host "3. Exit" -ForegroundColor White
    Write-Host ""
    $choice = Read-Host "Enter choice (1-3)"
    
    if ($choice -eq "1") {
        Write-Host ""
        Write-Host "Starting server with real camera..." -ForegroundColor Green
        Write-Host "Open browser to: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
        Write-Host ""
        python server.py
    } elseif ($choice -eq "2") {
        Write-Host ""
        Write-Host "Starting server with virtual camera..." -ForegroundColor Green
        Write-Host "Open browser to: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
        Write-Host ""
        python test_server.py
    }
} else {
    Write-Host "1. Start server with VIRTUAL camera (synthetic video)" -ForegroundColor White
    Write-Host "2. Try REAL camera anyway" -ForegroundColor White
    Write-Host "3. Exit" -ForegroundColor White
    Write-Host ""
    $choice = Read-Host "Enter choice (1-3)"
    
    if ($choice -eq "1") {
        Write-Host ""
        Write-Host "Starting server with virtual camera..." -ForegroundColor Green
        Write-Host "Open browser to: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
        Write-Host ""
        python test_server.py
    } elseif ($choice -eq "2") {
        Write-Host ""
        Write-Host "Starting server with real camera..." -ForegroundColor Green
        Write-Host "Open browser to: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
        Write-Host ""
        python server.py
    }
}

Write-Host ""
Write-Host "Test complete!" -ForegroundColor Green
