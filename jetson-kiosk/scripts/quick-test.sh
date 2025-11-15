#!/bin/bash

###############################################################################
# Quick Camera Test for Jetson Orin
# Tests camera streaming WITHOUT installing anything
# Just verifies the basic functionality will work
###############################################################################

set -e

echo "========================================"
echo "Jetson Camera Quick Test"
echo "========================================"
echo ""

# Check Python
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    echo "Install with: sudo apt install python3"
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check camera
echo "Checking camera..."
if ! ls /dev/video* &> /dev/null; then
    echo "❌ No camera found!"
    echo "Connect USB camera and check: ls /dev/video*"
    exit 1
fi
echo "✓ Camera device(s) found: $(ls /dev/video* | tr '\n' ' ')"
echo ""

# Test with OpenCV
echo "Testing camera with Python..."
python3 << 'EOF'
import sys

# Check if packages are available
packages_needed = []
try:
    import cv2
except ImportError:
    packages_needed.append('opencv-python')

try:
    import fastapi
except ImportError:
    packages_needed.append('fastapi')

try:
    import uvicorn
except ImportError:
    packages_needed.append('uvicorn')

if packages_needed:
    print("⚠️  Missing Python packages:", ', '.join(packages_needed))
    print("")
    print("Install them with:")
    print(f"  pip3 install {' '.join(packages_needed)}")
    print("")
    print("Or run the full installation script: ./scripts/install.sh")
    sys.exit(2)

# Test camera
print("Testing camera access...")
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("❌ Cannot open camera!")
    sys.exit(1)

ret, frame = camera.read()
camera.release()

if not ret:
    print("❌ Cannot capture frame!")
    sys.exit(1)

print(f"✓ Camera working! Captured {frame.shape[1]}x{frame.shape[0]} frame")
print("")
print("Camera test successful! 🎉")
EOF

TEST_EXIT=$?

if [ $TEST_EXIT -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✓ All tests passed!"
    echo "========================================"
    echo ""
    echo "Your system is ready. Next steps:"
    echo ""
    echo "Option 1 - Quick test (no installation):"
    echo "  pip3 install fastapi uvicorn opencv-python"
    echo "  python3 server.py"
    echo "  # Then open http://localhost:8000 in browser"
    echo ""
    echo "Option 2 - Full installation with auto-start:"
    echo "  ./scripts/install.sh"
    echo ""
    exit 0
elif [ $TEST_EXIT -eq 2 ]; then
    # Missing packages
    exit 2
else
    echo ""
    echo "========================================"
    echo "❌ Camera test failed"
    echo "========================================"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check camera connection: ls /dev/video*"
    echo "  2. Check permissions: groups (should include 'video')"
    echo "  3. Try manual test: python3 -c 'import cv2; print(cv2.VideoCapture(0).isOpened())'"
    echo ""
    exit 1
fi
