#!/bin/bash

# Kiosk startup script for Jetson Orin
# This script launches Chromium in kiosk mode to display the camera feed

# Flag file to control auto-restart
RESTART_FLAG="/tmp/jetson-kiosk-restart"

# Create restart flag (can be deleted to prevent restart)
touch "$RESTART_FLAG"

# Wait for the video server to be ready
echo "Waiting for video server to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "Video server is ready!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 1
done

# Kill any existing Chromium processes
pkill -f chromium

# Wait a moment for processes to terminate
sleep 2

echo "Starting Jetson Camera Kiosk..."
echo "To exit: Press ESC or Q in the browser, or delete $RESTART_FLAG"

# Launch Chromium in kiosk mode
chromium-browser \
    --kiosk \
    --noerrdialogs \
    --disable-infobars \
    --no-first-run \
    --disable-session-crashed-bubble \
    --disable-translate \
    --disable-features=TranslateUI \
    --disable-save-password-bubble \
    --disable-pinch \
    --overscroll-history-navigation=0 \
    --check-for-update-interval=31536000 \
    --simulate-notifi-no-au='Tue, 31 Dec 2099 23:59:59 GMT' \
    http://localhost:8000/

# Check if should restart
if [ -f "$RESTART_FLAG" ]; then
    echo "Kiosk closed. Restarting in 5 seconds..."
    echo "To prevent restart, run: rm $RESTART_FLAG"
    sleep 5
    
    # Check again before restarting
    if [ -f "$RESTART_FLAG" ]; then
        exec "$0"
    else
        echo "Restart cancelled. Exiting kiosk mode."
    fi
else
    echo "Kiosk mode exited (restart flag removed)."
fi
