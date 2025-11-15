#!/bin/bash

###############################################################################
# Toggle Kiosk Auto-Restart
# Enable or disable automatic restart of kiosk mode when browser closes
###############################################################################

RESTART_FLAG="/tmp/jetson-kiosk-restart"

echo "======================================"
echo "Kiosk Auto-Restart Toggle"
echo "======================================"
echo ""

if [ -f "$RESTART_FLAG" ]; then
    echo "Current status: Auto-restart ENABLED"
    echo ""
    read -p "Disable auto-restart? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f "$RESTART_FLAG"
        echo "✓ Auto-restart DISABLED"
        echo "  Kiosk will not restart when browser closes"
    fi
else
    echo "Current status: Auto-restart DISABLED"
    echo ""
    read -p "Enable auto-restart? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        touch "$RESTART_FLAG"
        echo "✓ Auto-restart ENABLED"
        echo "  Kiosk will restart when browser closes"
    fi
fi

echo ""
echo "======================================"
echo ""
