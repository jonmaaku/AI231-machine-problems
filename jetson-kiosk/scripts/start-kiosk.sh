#!/bin/bash

# Kiosk startup script for Jetson Orin
# This script launches Chromium in kiosk mode to display the camera feed

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
    --simulate-outdated-no-au='Tue, 31 Dec 2099 23:59:59 GMT' \
    http://localhost:8000/

# If Chromium exits, wait a bit and restart
sleep 5
exec $0
