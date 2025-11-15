#!/bin/bash

###############################################################################
# Stop Kiosk Script
# Gracefully stops the kiosk mode and prevents auto-restart
###############################################################################

echo "======================================"
echo "Stopping Jetson Camera Kiosk"
echo "======================================"
echo ""

# Remove restart flag to prevent auto-restart
RESTART_FLAG="/tmp/jetson-kiosk-restart"
if [ -f "$RESTART_FLAG" ]; then
    rm -f "$RESTART_FLAG"
    echo "✓ Disabled auto-restart"
fi

# Kill Chromium browser
if pgrep -f chromium > /dev/null; then
    echo "✓ Closing Chromium browser..."
    pkill -f chromium
    sleep 2
else
    echo "⚠ Chromium is not running"
fi

# Kill kiosk startup script if still running
if pgrep -f start-kiosk.sh > /dev/null; then
    echo "✓ Stopping kiosk script..."
    pkill -f start-kiosk.sh
else
    echo "⚠ Kiosk script is not running"
fi

echo ""
echo "======================================"
echo "Kiosk Stopped"
echo "======================================"
echo ""
echo "To restart kiosk mode, run:"
echo "  ~/jetson-kiosk/scripts/start-kiosk.sh"
echo ""
echo "Or reboot the system:"
echo "  sudo reboot"
echo ""
