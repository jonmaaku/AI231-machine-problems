# 🚀 Jetson POS System - Quick Reference Card

## One-Line Start
```bash
./start_pos.sh  # Linux/Jetson
# OR
.\start_pos.ps1  # Windows (testing)
```

## Essential URLs
- **POS Interface**: http://localhost:8000/pos.html
- **Camera Only**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Quick Test
```bash
python test_pos.py
```

## Core Configuration (server.py)

### Camera
```python
CAMERA_INDEX = 0      # 0, 1, 2 for different cameras
VGA_WIDTH = 1080      # Resolution width
VGA_HEIGHT = 720      # Resolution height
FPS = 60              # Frame rate
```

### YOLO
```python
YOLO_MODEL = "yolov8n.pt"     # yolov8n/s/m, yolov11n
CONFIDENCE_THRESHOLD = 0.5    # 0.3-0.7 recommended
INFERENCE_SIZE = 640          # 416/640 (lower=faster)
```

### Products
```python
PRODUCT_DATABASE = {
    "bottle": {"name": "Water", "price": 1.50, "category": "Drinks"},
    # Add more products matching COCO classes
}
```

## API Quick Reference

### Detection
```bash
curl http://localhost:8000/api/detect
```

### Cart
```bash
# Get cart
curl http://localhost:8000/api/cart

# Add item
curl -X POST http://localhost:8000/api/cart/add \
  -H "Content-Type: application/json" \
  -d '{"name":"Water","price":1.50,"category":"Drinks"}'

# Clear cart
curl -X POST http://localhost:8000/api/cart/clear

# Checkout
curl -X POST http://localhost:8000/api/cart/checkout
```

## Performance Tuning

### Max Performance (Jetson)
```bash
sudo nvpmodel -m 0        # Max power mode
sudo jetson_clocks         # Max clock speeds
```

### Fast Inference
- Use `yolov8n.pt` (fastest)
- Lower `INFERENCE_SIZE` to 416
- Reduce camera resolution to 640x480
- Enable TensorRT (automatic on first run)

### Monitor
```bash
sudo tegrastats           # CPU/GPU/Mem usage
htop                      # System monitor
```

## Troubleshooting

### Camera Issues
```bash
ls /dev/video*            # List cameras
v4l2-ctl --list-devices   # Camera details
# Update CAMERA_INDEX in server.py
```

### Low FPS
1. Use `yolov8n.pt` model
2. Set `INFERENCE_SIZE = 416`
3. Enable max performance mode
4. Check `sudo tegrastats` for bottlenecks

### YOLO Not Detecting
1. Improve lighting
2. Lower `CONFIDENCE_THRESHOLD = 0.3`
3. Check object is in COCO classes
4. Train custom model for your products

### Memory Errors
```bash
# Add swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Production Deployment

### Auto-Start Service
```bash
# Edit service file
sudo nano /etc/systemd/system/pos-server.service

# Enable
sudo systemctl enable pos-server
sudo systemctl start pos-server

# Check
sudo systemctl status pos-server
```

### Kiosk Mode
```bash
# Create autostart
nano ~/.config/autostart/pos-kiosk.desktop

# Disable screen blanking
gsettings set org.gnome.desktop.session idle-delay 0
```

## Common Commands

```bash
# Start server manually
python server.py

# Test system
python test_pos.py

# Check server
curl http://localhost:8000/health

# View logs (if using systemd)
sudo journalctl -u pos-server -f

# Stop server
# Ctrl+C (if running manually)
sudo systemctl stop pos-server  # (if using systemd)
```

## UI Controls

### POS Interface
- **Auto-Scan Toggle**: Enable/disable automatic scanning
- **📸 Scan Now**: Manual scan
- **+/- Buttons**: Adjust quantities
- **✕ Button**: Remove item
- **🗑️ Clear**: Clear all items
- **💳 Checkout**: Process transaction

### Performance Indicators
- 🟢 **<500ms**: FAST - Optimal
- 🟡 **500-1000ms**: OK - Acceptable
- 🔴 **>1000ms**: SLOW - Needs optimization

## File Locations

```
~/jetson-kiosk/
├── server.py              # Main server
├── web/pos.html          # POS UI
├── test_pos.py           # Tests
├── POS_SETUP_GUIDE.md    # Full docs
└── start_pos.sh          # Quick start
```

## Getting Help

1. Check `POS_SETUP_GUIDE.md` for detailed setup
2. Run `python test_pos.py` for diagnostics
3. Review logs: `sudo journalctl -u pos-server -f`
4. Check troubleshooting section in README.md

## Custom YOLO Model (Advanced)

```python
from ultralytics import YOLO

# Train
model = YOLO('yolov8n.pt')
model.train(data='your-data.yaml', epochs=100)

# Export to TensorRT
model.export(format='engine', device=0, half=True)

# Update server.py
YOLO_MODEL = "path/to/your/model.pt"
```

## System Requirements Met ✅

- ✅ YOLO Detection (YOLOv8/v11)
- ✅ Live Camera (1080x720 @ 60fps)
- ✅ <500ms Latency (with optimization)
- ✅ Cart Management (items, price, quantity, totals)
- ✅ Jetson Compatible (TensorRT optimized)
- ✅ Kiosk Mode (full-screen operation)

---

**Need more help?** See `POS_SETUP_GUIDE.md` for comprehensive documentation.
