#!/bin/bash

###############################################################################
# Jetson Orin Pre-Installation Check Script
# Run this FIRST to verify your system is ready for the camera kiosk
###############################################################################

set +e  # Don't exit on errors, we want to check everything

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0
WARN=0

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Jetson Orin Camera Kiosk${NC}"
echo -e "${BLUE}Pre-Installation Check${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Function to print test result
print_result() {
    local status=$1
    local message=$2
    local detail=$3
    
    if [ "$status" == "PASS" ]; then
        echo -e "${GREEN}✓ PASS${NC} - $message"
        [ -n "$detail" ] && echo -e "        $detail"
        ((PASS++))
    elif [ "$status" == "FAIL" ]; then
        echo -e "${RED}✗ FAIL${NC} - $message"
        [ -n "$detail" ] && echo -e "        ${RED}$detail${NC}"
        ((FAIL++))
    elif [ "$status" == "WARN" ]; then
        echo -e "${YELLOW}⚠ WARN${NC} - $message"
        [ -n "$detail" ] && echo -e "        ${YELLOW}$detail${NC}"
        ((WARN++))
    fi
}

# Test 1: Check if running on Jetson
echo -e "${YELLOW}[1/15] Checking Jetson platform...${NC}"
if [ -f /etc/nv_tegra_release ]; then
    JETSON_INFO=$(cat /etc/nv_tegra_release | head -n 1)
    print_result "PASS" "Running on NVIDIA Jetson" "$JETSON_INFO"
else
    print_result "WARN" "Not running on Jetson" "This may still work on other Linux systems"
fi
echo ""

# Test 2: Check JetPack version (if on Jetson)
echo -e "${YELLOW}[2/15] Checking JetPack version...${NC}"
if command -v dpkg &> /dev/null; then
    JETPACK_VERSION=$(dpkg -l | grep nvidia-jetpack | awk '{print $3}' | head -n 1)
    if [ -n "$JETPACK_VERSION" ]; then
        print_result "PASS" "JetPack installed" "Version: $JETPACK_VERSION"
    else
        print_result "WARN" "JetPack not detected" "Not critical if not on Jetson"
    fi
else
    print_result "WARN" "Cannot check JetPack" "dpkg not available"
fi
echo ""

# Test 3: Check Python version
echo -e "${YELLOW}[3/15] Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)' 2>/dev/null)
    if [ "$PYTHON_MINOR" -ge 8 ]; then
        print_result "PASS" "Python 3.$PYTHON_MINOR found" "$PYTHON_VERSION"
    else
        print_result "FAIL" "Python too old" "Need Python 3.8+, found 3.$PYTHON_MINOR"
    fi
else
    print_result "FAIL" "Python 3 not found" "Install with: sudo apt install python3"
fi
echo ""

# Test 4: Check pip
echo -e "${YELLOW}[4/15] Checking pip...${NC}"
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version 2>&1)
    print_result "PASS" "pip3 found" "$PIP_VERSION"
else
    print_result "FAIL" "pip3 not found" "Install with: sudo apt install python3-pip"
fi
echo ""

# Test 5: Check for USB camera
echo -e "${YELLOW}[5/15] Checking for USB camera...${NC}"
if ls /dev/video* &> /dev/null; then
    CAMERAS=$(ls /dev/video* | tr '\n' ' ')
    print_result "PASS" "Camera device(s) found" "$CAMERAS"
else
    print_result "FAIL" "No camera devices found" "Connect USB camera and try: ls /dev/video*"
fi
echo ""

# Test 6: Test camera access with Python
echo -e "${YELLOW}[6/15] Testing camera with Python/OpenCV...${NC}"
python3 << 'PYTHON_TEST' > /tmp/camera_test.txt 2>&1
import sys
try:
    import cv2
    camera = cv2.VideoCapture(0)
    if camera.isOpened():
        ret, frame = camera.read()
        if ret:
            print("SUCCESS: Camera captured {}x{} frame".format(frame.shape[1], frame.shape[0]))
            camera.release()
            sys.exit(0)
        else:
            print("ERROR: Failed to capture frame")
            camera.release()
            sys.exit(1)
    else:
        print("ERROR: Cannot open camera")
        sys.exit(1)
except ImportError:
    print("INFO: OpenCV not installed (will be installed during setup)")
    sys.exit(2)
except Exception as e:
    print("ERROR: {}".format(str(e)))
    sys.exit(1)
PYTHON_TEST

CAMERA_EXIT=$?
CAMERA_MSG=$(cat /tmp/camera_test.txt)

if [ $CAMERA_EXIT -eq 0 ]; then
    print_result "PASS" "Camera accessible via OpenCV" "$CAMERA_MSG"
elif [ $CAMERA_EXIT -eq 2 ]; then
    print_result "WARN" "OpenCV not installed yet" "$CAMERA_MSG"
else
    print_result "FAIL" "Camera not accessible" "$CAMERA_MSG"
fi
rm -f /tmp/camera_test.txt
echo ""

# Test 7: Check user permissions (video group)
echo -e "${YELLOW}[7/15] Checking video group membership...${NC}"
if groups | grep -q video; then
    print_result "PASS" "User in 'video' group" "$(whoami) can access camera"
else
    print_result "WARN" "User NOT in 'video' group" "Run: sudo usermod -a -G video $(whoami)"
fi
echo ""

# Test 8: Check for Chromium browser
echo -e "${YELLOW}[8/15] Checking Chromium browser...${NC}"
if command -v chromium-browser &> /dev/null; then
    CHROMIUM_VERSION=$(chromium-browser --version 2>&1)
    print_result "PASS" "Chromium installed" "$CHROMIUM_VERSION"
elif command -v chromium &> /dev/null; then
    CHROMIUM_VERSION=$(chromium --version 2>&1)
    print_result "PASS" "Chromium installed" "$CHROMIUM_VERSION"
else
    print_result "FAIL" "Chromium not found" "Install with: sudo apt install chromium-browser"
fi
echo ""

# Test 9: Check for X11/Display
echo -e "${YELLOW}[9/15] Checking display server...${NC}"
if [ -n "$DISPLAY" ]; then
    print_result "PASS" "Display server running" "DISPLAY=$DISPLAY"
else
    print_result "WARN" "No display detected" "Are you running in GUI mode?"
fi
echo ""

# Test 10: Check network connectivity
echo -e "${YELLOW}[10/15] Checking network...${NC}"
if ping -c 1 8.8.8.8 &> /dev/null; then
    print_result "PASS" "Network connectivity OK" "Can reach internet"
else
    print_result "WARN" "No internet connection" "Needed for package installation"
fi
echo ""

# Test 11: Check disk space
echo -e "${YELLOW}[11/15] Checking disk space...${NC}"
AVAILABLE=$(df -h / | awk 'NR==2 {print $4}')
AVAILABLE_MB=$(df -m / | awk 'NR==2 {print $4}')
if [ "$AVAILABLE_MB" -gt 1000 ]; then
    print_result "PASS" "Sufficient disk space" "$AVAILABLE available"
else
    print_result "WARN" "Low disk space" "Only $AVAILABLE available, recommend 1GB+"
fi
echo ""

# Test 12: Check systemd
echo -e "${YELLOW}[12/15] Checking systemd...${NC}"
if command -v systemctl &> /dev/null; then
    print_result "PASS" "systemd available" "Can use systemd services"
else
    print_result "WARN" "systemd not found" "Auto-start may not work"
fi
echo ""

# Test 13: Check if port 8000 is available
echo -e "${YELLOW}[13/15] Checking port 8000...${NC}"
if netstat -tuln 2>/dev/null | grep -q ":8000 "; then
    print_result "WARN" "Port 8000 already in use" "May need to change server port"
elif ss -tuln 2>/dev/null | grep -q ":8000 "; then
    print_result "WARN" "Port 8000 already in use" "May need to change server port"
else
    print_result "PASS" "Port 8000 available" "Server can use default port"
fi
echo ""

# Test 14: Check for required system packages
echo -e "${YELLOW}[14/15] Checking system dependencies...${NC}"
MISSING_PKGS=""
for pkg in curl wget; do
    if ! command -v $pkg &> /dev/null; then
        MISSING_PKGS="$MISSING_PKGS $pkg"
    fi
done

if [ -z "$MISSING_PKGS" ]; then
    print_result "PASS" "Required tools installed" "curl, wget available"
else
    print_result "WARN" "Missing packages" "Install: sudo apt install$MISSING_PKGS"
fi
echo ""

# Test 15: Check sudo access
echo -e "${YELLOW}[15/15] Checking sudo privileges...${NC}"
if sudo -n true 2>/dev/null; then
    print_result "PASS" "Sudo access available" "Can install system packages"
else
    print_result "WARN" "Sudo may require password" "You'll need sudo for installation"
fi
echo ""

# Summary
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}Passed:${NC}  $PASS"
echo -e "${YELLOW}Warnings:${NC} $WARN"
echo -e "${RED}Failed:${NC}  $FAIL"
echo ""

# Recommendations
if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ System is ready for installation!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review any warnings above"
    echo "  2. Run the installation: ./scripts/install.sh"
    echo ""
elif [ $FAIL -le 2 ]; then
    echo -e "${YELLOW}⚠ System has minor issues${NC}"
    echo ""
    echo "Please fix the failed checks above, then run:"
    echo "  ./scripts/install.sh"
    echo ""
else
    echo -e "${RED}✗ System has major issues${NC}"
    echo ""
    echo "Please fix the following before installation:"
    echo ""
    
    # Print specific fixes needed
    if ! command -v python3 &> /dev/null; then
        echo "  • Install Python 3.8+:"
        echo "    sudo apt update"
        echo "    sudo apt install python3 python3-pip python3-venv"
        echo ""
    fi
    
    if ! ls /dev/video* &> /dev/null; then
        echo "  • Connect a USB camera"
        echo "    Check with: ls /dev/video*"
        echo ""
    fi
    
    if ! command -v chromium-browser &> /dev/null && ! command -v chromium &> /dev/null; then
        echo "  • Install Chromium browser:"
        echo "    sudo apt install chromium-browser"
        echo ""
    fi
fi

# Additional recommendations
if [ $WARN -gt 0 ]; then
    echo -e "${YELLOW}Recommendations:${NC}"
    
    if ! groups | grep -q video; then
        echo "  • Add user to video group:"
        echo "    sudo usermod -a -G video $(whoami)"
        echo "    Then log out and back in"
        echo ""
    fi
    
    if [ -z "$DISPLAY" ]; then
        echo "  • Make sure you're in GUI mode"
        echo "    The kiosk requires a graphical environment"
        echo ""
    fi
fi

echo -e "${BLUE}======================================${NC}"
echo ""

# Exit with appropriate code
if [ $FAIL -eq 0 ]; then
    exit 0
else
    exit 1
fi
