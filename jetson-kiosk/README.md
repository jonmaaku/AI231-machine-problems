# Jetson Orin POS System with YOLO Detection

A complete Point-of-Sale (POS) system with real-time YOLO object detection for NVIDIA Jetson Orin. Features <0.5s latency, automatic product scanning, shopping cart management, and kiosk mode operation.

## 🎯 Features

### Core POS Features
- **Real-time YOLO Detection**: YOLOv8/v11 object detection optimized for Jetson hardware
- **Low Latency**: <500ms inference time for real-time product scanning
- **Auto-Scan Mode**: Automatically detects and adds products to cart
- **Shopping Cart**: Real-time cart management with quantity controls
- **Checkout System**: Complete transaction processing with receipt generation
- **Product Database**: Pre-configured retail products with prices and categories

### Technical Features
- **FastAPI Backend**: High-performance async API server
- **Modern Web Interface**: Responsive, touch-friendly POS interface
- **TensorRT Optimization**: GPU-accelerated inference on Jetson
- **Kiosk Mode**: Full-screen operation for retail environments
- **Live Video Feed**: 1080x720 camera stream with YOLO annotations
- **Performance Monitoring**: Real-time latency and FPS display

## 📋 Requirements

### Hardware
- NVIDIA Jetson Orin (Nano/NX/AGX)
- USB Camera (UVC compatible, 1080x720+ recommended)
- Display (1920x1080 recommended)
- 8GB+ RAM recommended

### Software
- Ubuntu 20.04/22.04 (JetPack 5.0+)
- Python 3.8+
- CUDA 11.4+ (included in JetPack)
- Chromium browser (for kiosk mode)

## 🚀 Quick Start

### Method 1: Automated Setup (Recommended)

```bash
cd ~/jetson-kiosk
chmod +x start_pos.sh
./start_pos.sh
```

The script will:
- Create virtual environment (if needed)
- Install all dependencies
- Download YOLO model
- Start the POS server

### Method 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Start server
python server.py
```

### Access the POS System

1. **POS Interface**: http://localhost:8000/pos.html
2. **Camera Only**: http://localhost:8000/index.html
3. **API Docs**: http://localhost:8000/docs

## 🎮 Usage Guide

### Auto-Scan Mode (Default)
1. Enable "Auto-Scan Mode" toggle
2. Place products in front of camera
3. System automatically detects and adds items every second
4. Review items in shopping cart

### Manual Scan Mode
1. Disable "Auto-Scan Mode"
2. Position product in camera view
3. Click "📸 Scan Now" button
4. Item is added to cart

### Cart Operations
- **Adjust Quantity**: Use +/- buttons
- **Remove Item**: Click ✕ button
- **Clear All**: Click "🗑️ Clear" button
- **Checkout**: Click "💳 Checkout" button

### Performance Metrics
The interface displays real-time performance:
- **Latency**: Inference time (target: <500ms)
  - 🟢 Green (FAST): <500ms
  - 🟡 Orange (OK): 500-1000ms
  - 🔴 Red (SLOW): >1000ms
- **Detections**: Number of objects detected
- **FPS**: Video stream frame rate

## 🛠️ Configuration

### Camera Settings

Edit `server.py`:

```python
CAMERA_INDEX = 0      # Camera device index (0, 1, 2...)
VGA_WIDTH = 1080      # Resolution width
VGA_HEIGHT = 720      # Resolution height
FPS = 60              # Target frame rate
```

### YOLO Model

```python
YOLO_MODEL = "yolov8n.pt"  # Model options:
                            # yolov8n.pt - Fastest (recommended)
                            # yolov8s.pt - Balanced
                            # yolov8m.pt - More accurate
                            # yolov11n.pt - Latest YOLO11

CONFIDENCE_THRESHOLD = 0.5  # Detection confidence (0.0-1.0)
IOU_THRESHOLD = 0.45        # Overlap threshold
INFERENCE_SIZE = 640        # Input size (lower = faster)
```

### Product Database

Add custom products in `server.py`:

```python
PRODUCT_DATABASE = {
    "bottle": {
        "name": "Water Bottle",
        "price": 1.50,
        "category": "Beverages"
    },
    "apple": {
        "name": "Fresh Apple",
        "price": 1.29,
        "category": "Fruits"
    },
    # Add more products...
}
```

**Note**: Product keys must match YOLO class names from the COCO dataset, or train a custom model.

## 📊 API Endpoints

### Video & Detection
- `GET /video_feed` - MJPEG stream with YOLO annotations
- `GET /api/detect` - Single frame detection with inference time

### Cart Management
- `GET /api/cart` - Get current cart contents
- `POST /api/cart/add` - Add item to cart
- `POST /api/cart/remove` - Remove item from cart
- `POST /api/cart/update` - Update item quantity
- `POST /api/cart/clear` - Clear all items
- `POST /api/cart/checkout` - Process checkout & generate receipt

### System
- `GET /health` - Server health check
- `GET /api/info` - Server and YOLO configuration
- `GET /api/products` - Available products database

## 🧪 Testing

Run the diagnostic test script:

```bash
python test_pos.py
```

This tests:
- Python dependencies
- Camera access
- YOLO model loading
- Inference speed
- API endpoints
- Cart operations

## 🚀 Production Deployment

### Auto-Start on Boot

1. **Create systemd service**:

```bash
sudo nano /etc/systemd/system/pos-server.service
```

Add:

```ini
[Unit]
Description=Jetson POS Server
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/jetson-kiosk
ExecStart=/home/YOUR_USERNAME/jetson-kiosk/venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **Enable service**:

```bash
sudo systemctl daemon-reload
sudo systemctl enable pos-server
sudo systemctl start pos-server
```

### Kiosk Mode Setup

1. **Create autostart entry**:

```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/pos-kiosk.desktop
```

Add:

```ini
[Desktop Entry]
Type=Application
Name=POS Kiosk
Exec=chromium-browser --kiosk --app=http://localhost:8000/pos.html
Hidden=false
X-GNOME-Autostart-enabled=true
```

2. **Disable screen blanking**:

```bash
gsettings set org.gnome.desktop.session idle-delay 0
gsettings set org.gnome.desktop.screensaver lock-enabled false
```

## 🔧 Troubleshooting

### Camera Not Detected

```bash
# List available cameras
ls /dev/video*

# Test specific camera
v4l2-ctl --list-devices

# Update CAMERA_INDEX in server.py
```

### Low FPS / High Latency

1. **Use smaller YOLO model**: `yolov8n.pt` (fastest)
2. **Reduce camera resolution**: 640x480
3. **Lower inference size**: `INFERENCE_SIZE = 416`
4. **Enable max performance**:
   ```bash
   sudo nvpmodel -m 0  # Max performance mode
   sudo jetson_clocks   # Max clock speeds
   ```

### YOLO Not Detecting Products

1. **Improve lighting**: Ensure good lighting conditions
2. **Lower confidence threshold**: Set to 0.3-0.4
3. **Check product classes**: Only COCO-trained objects are detected
4. **Train custom model**: For store-specific products (see POS_SETUP_GUIDE.md)

### Memory Issues

```bash
# Increase swap space
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Import Errors

```bash
# Reinstall dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 📈 Performance Optimization

### TensorRT Acceleration

The system automatically exports YOLO to TensorRT on first run for optimal Jetson performance.

### Jetson Power Modes

```bash
# Check current mode
sudo nvpmodel -q

# Set to maximum performance
sudo nvpmodel -m 0

# Enable max clock speeds
sudo jetson_clocks

# Check GPU/CPU usage
sudo tegrastats
```

## 📚 Documentation

- **[POS_SETUP_GUIDE.md](POS_SETUP_GUIDE.md)** - Complete setup and configuration guide
- **[test_pos.py](test_pos.py)** - Run diagnostic tests
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when server running)

## 📁 Project Structure

```
jetson-kiosk/
├── server.py              # Main POS server with YOLO
├── requirements.txt       # Python dependencies
├── test_pos.py           # Diagnostic test script
├── start_pos.sh          # Quick start script (Linux)
├── start_pos.ps1         # Quick start script (Windows)
├── POS_SETUP_GUIDE.md    # Complete setup guide
├── README.md             # This file
├── web/
│   ├── pos.html          # POS interface
│   └── index.html        # Camera-only interface
└── scripts/              # Installation and utility scripts
```

## ⚡ Quick Commands

```bash
# Start server
python server.py

# Run tests
python test_pos.py

# Check server status
curl http://localhost:8000/health

# Perform detection
curl http://localhost:8000/api/detect

# View cart
curl http://localhost:8000/api/cart

# Max performance mode
sudo nvpmodel -m 0 && sudo jetson_clocks
```

## 📡 API Endpoints

### Video & Detection
- `GET /video_feed` - MJPEG stream with YOLO annotations
- `GET /api/detect` - Single frame detection

### Cart Management
- `GET /api/cart` - Get cart contents
- `POST /api/cart/add` - Add item
- `POST /api/cart/remove` - Remove item
- `POST /api/cart/update` - Update quantity
- `POST /api/cart/clear` - Clear cart
- `POST /api/cart/checkout` - Process checkout

### System
- `GET /health` - Server health
- `GET /api/info` - Configuration
- `GET /api/products` - Product database

---

**Built for NVIDIA Jetson Orin | Powered by YOLOv8/v11 | FastAPI Backend**

*Real-time object detection meets point-of-sale efficiency*

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
