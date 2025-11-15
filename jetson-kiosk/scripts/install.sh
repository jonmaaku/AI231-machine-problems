#!/bin/bash

###############################################################################
# Jetson Orin Camera Kiosk Setup Script
# This script sets up the video streaming server and kiosk mode
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the current user
CURRENT_USER=$(whoami)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Jetson Orin Camera Kiosk Setup${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Project directory: $PROJECT_DIR"
echo "Current user: $CURRENT_USER"
echo ""

# Function to check if running on Jetson
check_jetson() {
    if [ -f /etc/nv_tegra_release ]; then
        echo -e "${GREEN}✓ Running on NVIDIA Jetson${NC}"
    else
        echo -e "${YELLOW}⚠ Warning: This doesn't appear to be a Jetson device${NC}"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Function to install system dependencies
install_dependencies() {
    echo -e "${YELLOW}Installing system dependencies...${NC}"
    
    sudo apt-get update
    sudo apt-get install -y \
        python3-pip \
        python3-venv \
        python3-opencv \
        chromium-browser \
        unclutter \
        x11-xserver-utils \
        curl
    
    echo -e "${GREEN}✓ System dependencies installed${NC}"
}

# Function to set up Python virtual environment
setup_python_env() {
    echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
    
    cd "$PROJECT_DIR"
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    pip install -r requirements.txt
    
    echo -e "${GREEN}✓ Python environment configured${NC}"
}

# Function to configure camera permissions
setup_camera_permissions() {
    echo -e "${YELLOW}Configuring camera permissions...${NC}"
    
    # Add user to video group
    sudo usermod -a -G video "$CURRENT_USER"
    
    echo -e "${GREEN}✓ Camera permissions configured${NC}"
    echo -e "${YELLOW}Note: You may need to log out and back in for group changes to take effect${NC}"
}

# Function to install systemd service
install_service() {
    echo -e "${YELLOW}Installing systemd service...${NC}"
    
    # Update service file with correct paths and username
    SERVICE_FILE="$PROJECT_DIR/systemd/camera-server.service"
    TEMP_SERVICE="/tmp/camera-server.service"
    
    sed "s|YOUR_USERNAME|$CURRENT_USER|g" "$SERVICE_FILE" | \
    sed "s|/home/YOUR_USERNAME/jetson-kiosk|$PROJECT_DIR|g" > "$TEMP_SERVICE"
    
    # Copy service file to systemd directory
    sudo cp "$TEMP_SERVICE" /etc/systemd/system/camera-server.service
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Enable service
    sudo systemctl enable camera-server.service
    
    echo -e "${GREEN}✓ Systemd service installed and enabled${NC}"
}

# Function to configure auto-login
configure_autologin() {
    echo -e "${YELLOW}Configuring auto-login...${NC}"
    
    # Check if using LightDM (common on Ubuntu)
    if [ -f /etc/lightdm/lightdm.conf ]; then
        # Backup existing config
        sudo cp /etc/lightdm/lightdm.conf /etc/lightdm/lightdm.conf.backup
        
        # Configure auto-login
        sudo bash -c "cat > /etc/lightdm/lightdm.conf <<EOF
[Seat:*]
autologin-user=$CURRENT_USER
autologin-user-timeout=0
user-session=ubuntu
EOF"
        
        echo -e "${GREEN}✓ Auto-login configured (LightDM)${NC}"
    elif [ -f /etc/gdm3/custom.conf ]; then
        # GDM3 configuration
        echo -e "${YELLOW}Detected GDM3. Please configure auto-login manually:${NC}"
        echo "1. Edit /etc/gdm3/custom.conf"
        echo "2. Under [daemon] section, add:"
        echo "   AutomaticLoginEnable=true"
        echo "   AutomaticLogin=$CURRENT_USER"
    else
        echo -e "${YELLOW}⚠ Display manager not detected. Please configure auto-login manually${NC}"
    fi
}

# Function to install kiosk autostart
install_kiosk_autostart() {
    echo -e "${YELLOW}Installing kiosk autostart...${NC}"
    
    # Make start script executable
    chmod +x "$PROJECT_DIR/scripts/start-kiosk.sh"
    
    # Update desktop entry with correct paths and username
    DESKTOP_FILE="$PROJECT_DIR/systemd/camera-kiosk.desktop"
    AUTOSTART_DIR="$HOME/.config/autostart"
    
    mkdir -p "$AUTOSTART_DIR"
    
    sed "s|YOUR_USERNAME|$CURRENT_USER|g" "$DESKTOP_FILE" | \
    sed "s|/home/YOUR_USERNAME/jetson-kiosk|$PROJECT_DIR|g" > "$AUTOSTART_DIR/camera-kiosk.desktop"
    
    chmod +x "$AUTOSTART_DIR/camera-kiosk.desktop"
    
    echo -e "${GREEN}✓ Kiosk autostart configured${NC}"
}

# Function to disable screen blanking
disable_screen_blanking() {
    echo -e "${YELLOW}Disabling screen blanking...${NC}"
    
    XSESSION_FILE="$HOME/.xsessionrc"
    
    cat > "$XSESSION_FILE" <<EOF
#!/bin/bash
# Disable screen blanking and power management
xset s off
xset s noblank
xset -dpms

# Hide mouse cursor after inactivity
unclutter -idle 0.1 -root &
EOF
    
    chmod +x "$XSESSION_FILE"
    
    echo -e "${GREEN}✓ Screen blanking disabled${NC}"
}

# Function to test the setup
test_setup() {
    echo -e "${YELLOW}Testing camera access...${NC}"
    
    # Test camera
    python3 -c "
import cv2
import sys

camera = cv2.VideoCapture(0)
if camera.isOpened():
    print('✓ Camera accessible')
    camera.release()
    sys.exit(0)
else:
    print('✗ Camera not accessible')
    sys.exit(1)
" && echo -e "${GREEN}✓ Camera test passed${NC}" || echo -e "${RED}✗ Camera test failed${NC}"
}

# Main installation
main() {
    check_jetson
    install_dependencies
    setup_python_env
    setup_camera_permissions
    install_service
    configure_autologin
    install_kiosk_autostart
    disable_screen_blanking
    test_setup
    
    echo ""
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}Installation Complete!${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start the video server now (or it will start on boot):"
    echo -e "   ${YELLOW}sudo systemctl start camera-server${NC}"
    echo ""
    echo "2. Check server status:"
    echo -e "   ${YELLOW}sudo systemctl status camera-server${NC}"
    echo ""
    echo "3. View logs:"
    echo -e "   ${YELLOW}sudo journalctl -u camera-server -f${NC}"
    echo ""
    echo "4. Test the web interface:"
    echo -e "   ${YELLOW}chromium-browser http://localhost:8000${NC}"
    echo ""
    echo "5. Reboot to test full kiosk mode:"
    echo -e "   ${YELLOW}sudo reboot${NC}"
    echo ""
    echo -e "${YELLOW}Note: You may need to log out and back in for group changes to take effect${NC}"
}

# Run main installation
main
