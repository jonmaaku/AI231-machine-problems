# Jetson Orin Camera Kiosk

A complete solution for running a real-time USB camera video feed on Jetson Orin with automatic boot-up in kiosk mode.

## 🎯 Features

- **FastAPI Video Server**: Streams VGA (640x480) video from USB camera via MJPEG
- **Modern Web Interface**: Clean, responsive UI with real-time video display
- **Auto-Start on Boot**: Systemd service starts video server automatically
- **Kiosk Mode**: Chromium launches in fullscreen kiosk mode on startup
- **Auto-Login**: Configured for automatic user login
- **Health Monitoring**: Built-in health check endpoints
- **Error Recovery**: Automatic retry and reconnection logic

## 📋 Requirements

### Hardware
- NVIDIA Jetson Orin (Nano/NX/AGX)
- USB Camera (UVC compatible)
- Display connected to Jetson

### Software
- Ubuntu 20.04 or later (JetPack)
- Python 3.8+
- Chromium browser

## 🚀 Quick Start

### 1. Clone or Copy Project

Transfer the `jetson-kiosk` folder to your Jetson Orin:

```bash
# If using git
git clone <repository-url>
cd jetson-kiosk

# Or copy the folder to your Jetson
scp -r jetson-kiosk/ your-jetson:~/
```

### 2. Run Installation Script

```bash
cd ~/jetson-kiosk
chmod +x scripts/install.sh
./scripts/install.sh
```

The installation script will:
- ✅ Install system dependencies (Python, OpenCV, Chromium)
- ✅ Set up Python virtual environment
- ✅ Configure camera permissions
- ✅ Install and enable systemd service
- ✅ Configure auto-login
- ✅ Set up kiosk mode autostart
- ✅ Disable screen blanking
- ✅ Test camera access

### 3. Start the Server (Manual Test)

```bash
# Start the service
sudo systemctl start camera-server

# Check status
sudo systemctl status camera-server

# View logs
sudo journalctl -u camera-server -f
```

### 4. Test the Web Interface

Open Chromium and navigate to:
```
http://localhost:8000
```

You should see the camera feed with a modern UI.

### 5. Enable Full Kiosk Mode

Reboot the Jetson to test automatic startup:

```bash
sudo reboot
```

After reboot, the system should:
1. Auto-login to your user account
2. Start the video server in the background
3. Launch Chromium in kiosk mode showing the camera feed

## 📁 Project Structure

```
jetson-kiosk/
├── server.py                    # FastAPI video streaming server
├── video_server.py              # Alternative simple server
├── requirements.txt             # Python dependencies
├── web/
│   └── index.html              # Web interface
├── scripts/
│   ├── install.sh              # Main installation script
│   └── start-kiosk.sh          # Kiosk startup script
├── systemd/
│   ├── camera-server.service   # Systemd service file
│   └── camera-kiosk.desktop    # Autostart desktop entry
└── README.md                   # This file
```

## 🔧 Configuration

### Change Camera Settings

Edit `server.py` to modify camera parameters:

```python
CAMERA_INDEX = 0        # USB camera index (0, 1, 2, etc.)
VGA_WIDTH = 640         # Resolution width
VGA_HEIGHT = 480        # Resolution height
FPS = 30                # Frames per second
```

### Change Server Port

Modify the port in `server.py`:

```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

And update `scripts/start-kiosk.sh`:

```bash
http://localhost:8000/
```

### Multiple Cameras

To use a different camera, check available cameras:

```bash
ls -l /dev/video*
```

Then update `CAMERA_INDEX` in `server.py`.

## 🛠️ Troubleshooting

### Camera Not Found

```bash
# List video devices
ls -l /dev/video*

# Test camera with v4l2
v4l2-ctl --list-devices

# Check permissions
groups $USER  # Should include 'video' group
```

### Service Won't Start

```bash
# Check service status
sudo systemctl status camera-server

# View detailed logs
sudo journalctl -u camera-server -n 50 --no-pager

# Test manually
cd ~/jetson-kiosk
source venv/bin/activate
python server.py
```

### Chromium Not Loading

```bash
# Check if server is running
curl http://localhost:8000/health

# Test kiosk script manually
~/jetson-kiosk/scripts/start-kiosk.sh

# Check autostart
ls -l ~/.config/autostart/
```

### Screen Blanking Still Enabled

```bash
# Run these commands manually
xset s off
xset s noblank
xset -dpms

# Add to startup if needed
echo "xset s off; xset s noblank; xset -dpms" >> ~/.xsessionrc
```

## 📡 API Endpoints

### Video Stream
- **GET** `/video_feed` - MJPEG video stream

### Health Check
- **GET** `/health` - Server and camera status
  ```json
  {
    "status": "healthy",
    "camera": "connected",
    "resolution": "640x480",
    "fps": 30
  }
  ```

### Server Info
- **GET** `/api/info` - Server configuration
  ```json
  {
    "server": "Jetson Orin Camera Server",
    "resolution": "640x480",
    "fps": 30,
    "camera_index": 0
  }
  ```

## ⌨️ Keyboard Shortcuts (in Kiosk)

- **ESC** or **Q** - Show exit confirmation dialog
- **F** - Toggle fullscreen
- **R** - Reload page
- **Alt+F4** - Force close browser (Linux)

## 🚪 Exiting Kiosk Mode

### Method 1: Using Exit Button (Recommended)
1. Move your mouse to show the **"EXIT KIOSK"** button (top-right corner)
2. Click the button
3. Confirm exit in the dialog
4. Browser will close or show exit screen

### Method 2: Keyboard Shortcut
1. Press **ESC** or **Q** key
2. Confirm exit in the dialog

### Method 3: Stop from Terminal
```bash
# Stop kiosk and prevent auto-restart
~/jetson-kiosk/scripts/stop-kiosk.sh

# Or manually
rm /tmp/jetson-kiosk-restart
pkill chromium
```

### Method 4: Disable Auto-Restart
```bash
# Toggle auto-restart on/off
~/jetson-kiosk/scripts/toggle-restart.sh

# Or manually disable
rm /tmp/jetson-kiosk-restart
```

### Method 5: Switch to TTY Console
1. Press **Ctrl+Alt+F2** (or F3, F4) to switch to console
2. Login with your credentials
3. Run: `~/jetson-kiosk/scripts/stop-kiosk.sh`
4. Press **Ctrl+Alt+F7** to return to GUI (or F1)

## 🔄 Management Commands

### Service Control

```bash
# Start service
sudo systemctl start camera-server

# Stop service
sudo systemctl stop camera-server

# Restart service
sudo systemctl restart camera-server

# Enable on boot
sudo systemctl enable camera-server

# Disable on boot
sudo systemctl disable camera-server

# View logs
sudo journalctl -u camera-server -f
```

### Disable Kiosk Mode

```bash
# Remove autostart entry
rm ~/.config/autostart/camera-kiosk.desktop

# Disable auto-restart
rm /tmp/jetson-kiosk-restart

# Stop currently running kiosk
~/jetson-kiosk/scripts/stop-kiosk.sh

# Reboot
sudo reboot
```

### Re-enable Kiosk Mode

```bash
# Restore autostart entry
cp ~/jetson-kiosk/systemd/camera-kiosk.desktop ~/.config/autostart/

# Enable auto-restart
touch /tmp/jetson-kiosk-restart

# Reboot
sudo reboot
```

### Temporarily Exit Kiosk (Will Restart on Reboot)

```bash
# Just stop kiosk for now
~/jetson-kiosk/scripts/stop-kiosk.sh

# Or press ESC/Q in the browser and confirm exit
```

## 🎨 Customization

### Modify Web Interface

Edit `web/index.html` to customize:
- Colors and styling (CSS section)
- Layout and components
- JavaScript behavior
- Display information

### Add Authentication

For security, you can add basic authentication to FastAPI. Edit `server.py`:

```python
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

@app.get("/video_feed")
async def video_feed(credentials: HTTPBasicCredentials = Depends(security)):
    # Add authentication logic
    ...
```

## 📊 Performance Optimization

### Reduce Latency
- Lower JPEG quality in `server.py`:
  ```python
  cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
  ```

### Increase Frame Rate
- Ensure camera supports higher FPS
- Modify `FPS` variable in `server.py`

### GPU Acceleration
- For advanced usage, use GStreamer with NVIDIA hardware acceleration:
  ```python
  # Use GStreamer pipeline for hardware encoding
  ```

## 🧪 Testing

### Test Camera Standalone

```bash
# Activate virtual environment
cd ~/jetson-kiosk
source venv/bin/activate

# Test camera
python3 -c "
import cv2
cam = cv2.VideoCapture(0)
print('Camera opened:', cam.isOpened())
ret, frame = cam.read()
print('Frame captured:', ret)
if ret:
    print('Frame shape:', frame.shape)
cam.release()
"
```

### Test Server Locally

```bash
# Start server
cd ~/jetson-kiosk
source venv/bin/activate
python server.py

# In another terminal, test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/info
```

## 🐛 Debug Mode

For troubleshooting, run the server manually with debug output:

```bash
cd ~/jetson-kiosk
source venv/bin/activate
python server.py
```

This will show detailed logs in the terminal.

## 📝 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

Feel free to modify and improve this setup for your specific needs!

## 💡 Tips

1. **Network Access**: To access from another device, use the Jetson's IP address instead of localhost
2. **Monitor Resources**: Use `htop` to monitor CPU/GPU usage
3. **Backup Config**: Keep backups of modified configuration files
4. **Update Regularly**: Keep system and dependencies updated with `apt update && apt upgrade`

## 📞 Support

For issues:
1. Check the troubleshooting section
2. Review logs: `sudo journalctl -u camera-server -n 100`
3. Test components individually
4. Verify camera connectivity: `ls -l /dev/video*`

---

**Enjoy your Jetson Orin Camera Kiosk! 🎥**
