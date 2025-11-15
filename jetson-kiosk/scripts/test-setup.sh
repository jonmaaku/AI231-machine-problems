#!/bin/bash

###############################################################################
# Quick Test Script for Camera Server
# Tests camera access and server functionality before full installation
###############################################################################

set -e

echo "======================================"
echo "Jetson Camera Server Quick Test"
echo "======================================"
echo ""

# Test 1: Check if camera is available
echo "Test 1: Checking camera availability..."
if ls /dev/video* > /dev/null 2>&1; then
    echo "✓ Camera devices found:"
    ls -l /dev/video*
else
    echo "✗ No camera devices found!"
    exit 1
fi

echo ""

# Test 2: Check Python
echo "Test 2: Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Python found: $PYTHON_VERSION"
else
    echo "✗ Python not found!"
    exit 1
fi

echo ""

# Test 3: Check if OpenCV can access camera
echo "Test 3: Testing OpenCV camera access..."
python3 << 'PYTHON_SCRIPT'
import sys
try:
    import cv2
    print("✓ OpenCV imported successfully")
    
    camera = cv2.VideoCapture(0)
    if camera.isOpened():
        print("✓ Camera opened successfully")
        
        ret, frame = camera.read()
        if ret:
            print(f"✓ Frame captured: {frame.shape[1]}x{frame.shape[0]}")
        else:
            print("✗ Failed to capture frame")
            sys.exit(1)
        
        camera.release()
    else:
        print("✗ Failed to open camera")
        sys.exit(1)
        
except ImportError:
    print("✗ OpenCV not installed")
    print("Install with: pip install opencv-python")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
PYTHON_SCRIPT

echo ""

# Test 4: Check if Chromium is installed
echo "Test 4: Checking Chromium browser..."
if command -v chromium-browser &> /dev/null; then
    echo "✓ Chromium browser found"
else
    echo "⚠ Chromium browser not found"
    echo "  Install with: sudo apt-get install chromium-browser"
fi

echo ""

# Test 5: Check user groups
echo "Test 5: Checking user permissions..."
if groups | grep -q video; then
    echo "✓ User is in 'video' group"
else
    echo "⚠ User is NOT in 'video' group"
    echo "  Add with: sudo usermod -a -G video $USER"
    echo "  Then log out and back in"
fi

echo ""
echo "======================================"
echo "Test Summary"
echo "======================================"
echo "All critical tests passed!"
echo ""
echo "You can now proceed with installation:"
echo "  ./scripts/install.sh"
echo ""
