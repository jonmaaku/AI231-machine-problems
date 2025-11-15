#!/bin/bash

###############################################################################
# Uninstall Script
# Removes the kiosk setup and systemd service
###############################################################################

CURRENT_USER=$(whoami)

echo "======================================"
echo "Jetson Camera Kiosk Uninstall"
echo "======================================"
echo ""

read -p "This will remove the kiosk setup. Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Stop and disable service
echo "Stopping and disabling service..."
sudo systemctl stop camera-server 2>/dev/null || true
sudo systemctl disable camera-server 2>/dev/null || true

# Remove service file
echo "Removing service file..."
sudo rm -f /etc/systemd/system/camera-server.service

# Reload systemd
sudo systemctl daemon-reload

# Remove autostart entry
echo "Removing autostart entry..."
rm -f ~/.config/autostart/camera-kiosk.desktop

# Remove xsessionrc (optional - prompt user)
echo ""
read -p "Remove screen blanking configuration? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f ~/.xsessionrc
    echo "✓ Screen blanking configuration removed"
fi

# Restore auto-login (optional - prompt user)
echo ""
read -p "Disable auto-login? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f /etc/lightdm/lightdm.conf.backup ]; then
        sudo mv /etc/lightdm/lightdm.conf.backup /etc/lightdm/lightdm.conf
        echo "✓ Auto-login disabled (restored backup)"
    else
        echo "⚠ No backup found, please disable auto-login manually"
    fi
fi

echo ""
echo "======================================"
echo "Uninstall Complete"
echo "======================================"
echo ""
echo "The following were removed:"
echo "  - Systemd service"
echo "  - Autostart configuration"
echo ""
echo "The project directory and virtual environment remain."
echo "To remove completely, run:"
echo "  rm -rf ~/jetson-kiosk"
echo ""
echo "Please reboot to complete the uninstall:"
echo "  sudo reboot"
echo ""
