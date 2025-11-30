# POS System Setup and Usage Guide

## 🎯 Overview

This is a complete Point-of-Sale (POS) system with YOLO object detection for the NVIDIA Jetson Orin platform. It provides real-time product scanning with <0.5 seconds latency, displaying scanned items, prices, quantities, and totals in kiosk mode.

## ✨ Features

- **Real-time YOLO Detection**: YOLOv8/v11 object detection optimized for Jetson
- **Low Latency**: <500ms inference time for real-time scanning
- **Auto-Scan Mode**: Automatically adds detected products to cart
- **Manual Scan**: On-demand scanning with button press
- **Shopping Cart**: Real-time cart management with quantity controls
- **Product Database**: Pre-configured products with prices and categories
- **Checkout System**: Complete transaction processing with receipt generation
- **Kiosk Mode**: Full-screen, touch-friendly interface
- **TensorRT Optimization**: Automatic GPU acceleration for Jetson hardware

## 📋 System Requirements

### Hardware
- NVIDIA Jetson Orin (Nano/NX/AGX)
- USB Camera (UVC compatible, 1080x720 or higher recommended)
- Display (1920x1080 recommended for optimal UI)
- 8GB+ RAM recommended
- 16GB+ storage

### Software
- Ubuntu 20.04/22.04 (JetPack 5.0+)
- Python 3.8+
- CUDA 11.4+ (included in JetPack)
- cuDNN (included in JetPack)

## 🚀 Installation

### Step 1: Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv chromium-browser
sudo apt install -y libopencv-dev python3-opencv
```

### Step 2: Clone Repository

```bash
cd ~
git clone <your-repo-url>
cd jetson-kiosk
```

### Step 3: Create Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Python Requirements

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: Installing PyTorch and Ultralytics on Jetson may take some time. For Jetson-optimized builds:

```bash
# Install PyTorch for Jetson (if not already installed)
wget https://nvidia.box.com/shared/static/ssf2v7pf5i245fk4i0q926hy4imzs2ph.whl -O torch-2.0.0-cp38-cp38-linux_aarch64.whl
pip install torch-2.0.0-cp38-cp38-linux_aarch64.whl

# Install torchvision
sudo apt install -y libjpeg-dev zlib1g-dev
pip install torchvision
```

### Step 5: Download YOLO Model

The system will automatically download the YOLO model on first run. To pre-download:

```bash
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

For better accuracy (slower):
- `yolov8s.pt` - Small model
- `yolov8m.pt` - Medium model
- `yolov11n.pt` - YOLO11 nano

### Step 6: Test Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Run test server
python server.py
```

Visit `http://localhost:8000/pos.html` in a browser to test.

## 🎮 Usage

### Starting the Server

```bash
cd ~/jetson-kiosk
source venv/bin/activate
python server.py
```

The server will start on `http://0.0.0.0:8000`

### Accessing the POS Interface

1. **Local Access**: `http://localhost:8000/pos.html`
2. **Network Access**: `http://<jetson-ip>:8000/pos.html`

### Using the POS System

#### Auto-Scan Mode (Default)
1. Enable "Auto-Scan Mode" toggle (enabled by default)
2. Place products in front of camera
3. System automatically detects and adds items to cart every second
4. Items appear in the shopping cart with quantity controls

#### Manual Scan Mode
1. Disable "Auto-Scan Mode" toggle
2. Place product in front of camera
3. Click "📸 Scan Now" button
4. Product is detected and added to cart

#### Cart Management
- **Adjust Quantity**: Use +/- buttons on each item
- **Remove Item**: Click ✕ button on item
- **Clear Cart**: Click "🗑️ Clear" button
- **Checkout**: Click "💳 Checkout" button

#### Checkout Process
1. Review items in cart
2. Click "💳 Checkout"
3. Receipt modal appears with transaction details
4. Transaction ID and timestamp generated
5. Cart is automatically cleared

### Performance Monitoring

The interface displays real-time metrics:
- **Latency**: Inference time in milliseconds
  - Green (FAST): <500ms
  - Orange (OK): 500-1000ms
  - Red (SLOW): >1000ms
- **Detections**: Number of objects detected in current frame
- **FPS**: Video stream frame rate

## 🛠️ Configuration

### Customize Camera Settings

Edit `server.py`:

```python
CAMERA_INDEX = 0  # Change to 1, 2, etc. for different cameras
VGA_WIDTH = 1080  # Resolution width
VGA_HEIGHT = 720  # Resolution height
FPS = 60          # Frame rate
```

### Customize YOLO Model

```python
YOLO_MODEL = "yolov8n.pt"  # Change to yolov8s.pt, yolov8m.pt, yolov11n.pt
CONFIDENCE_THRESHOLD = 0.5  # Detection confidence (0.0-1.0)
IOU_THRESHOLD = 0.45        # Overlap threshold
INFERENCE_SIZE = 640        # Input image size (smaller = faster)
```

### Add Products to Database

Edit the `PRODUCT_DATABASE` in `server.py`:

```python
PRODUCT_DATABASE = {
    "bottle": {"name": "Water Bottle", "price": 1.50, "category": "Beverages"},
    "apple": {"name": "Apple", "price": 1.29, "category": "Fruits"},
    # Add more products...
}
```

Products must match YOLO class names. Default uses COCO dataset classes.

### Train Custom YOLO Model

For store-specific products:

1. Collect product images
2. Label using tools like Roboflow or LabelImg
3. Train YOLOv8 model:

```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
results = model.train(data='your-dataset.yaml', epochs=100, imgsz=640)
```

4. Update `YOLO_MODEL` in server.py to your custom model path

## 🚀 Kiosk Mode Setup

### Auto-Start on Boot

Create systemd service:

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

Enable service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable pos-server
sudo systemctl start pos-server
```

### Kiosk Browser Setup

Create autostart entry:

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
NoDisplay=false
X-GNOME-Autostart-enabled=true
```

### Disable Screen Blanking

```bash
gsettings set org.gnome.desktop.session idle-delay 0
gsettings set org.gnome.desktop.screensaver lock-enabled false
```

## 📊 API Endpoints

### Video Stream
- `GET /video_feed` - MJPEG video stream with YOLO annotations

### Detection
- `GET /api/detect` - Single frame detection
  - Returns: `{detections: [...], inference_time_ms: float, timestamp: string}`

### Cart Management
- `GET /api/cart` - Get current cart
- `POST /api/cart/add` - Add item to cart
- `POST /api/cart/remove?item_name=<name>` - Remove item
- `POST /api/cart/update?item_name=<name>&quantity=<qty>` - Update quantity
- `POST /api/cart/clear` - Clear cart
- `POST /api/cart/checkout` - Process checkout

### System Info
- `GET /health` - Health check
- `GET /api/info` - Server information
- `GET /api/products` - Available products

## 🔧 Troubleshooting

### Low FPS / High Latency

1. **Reduce YOLO model size**: Use `yolov8n.pt` instead of larger models
2. **Lower camera resolution**: Set to 640x480
3. **Reduce inference size**: Set `INFERENCE_SIZE = 416`
4. **Enable TensorRT**: Model automatically exports on first run
5. **Check GPU usage**: `sudo tegrastats`

### Camera Not Detected

```bash
# List available cameras
ls /dev/video*

# Test camera
v4l2-ctl --list-devices

# Change CAMERA_INDEX in server.py
```

### YOLO Not Detecting Products

1. **Check lighting**: Ensure good lighting conditions
2. **Adjust confidence threshold**: Lower `CONFIDENCE_THRESHOLD` to 0.3
3. **Verify product in COCO classes**: Only COCO-trained classes are detected
4. **Train custom model**: For store-specific products

### Memory Issues

```bash
# Increase swap space
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📈 Performance Optimization

### TensorRT Acceleration

First run will export model to TensorRT engine:

```python
# Automatic during first detection
# Or manually:
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
model.export(format='engine', device=0, half=True)
```

### Jetson Power Mode

```bash
# Maximum performance
sudo nvpmodel -m 0
sudo jetson_clocks
```

### Camera Optimization

```python
# In server.py, add after VideoCapture
camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce latency
camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
```

## 📝 Testing

Test individual components:

```bash
# Test camera only
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera:', cap.isOpened())"

# Test YOLO
python -c "from ultralytics import YOLO; m = YOLO('yolov8n.pt'); print('YOLO OK')"

# Test server
curl http://localhost:8000/health

# Test detection
curl http://localhost:8000/api/detect
```

## 🎓 Next Steps

1. **Custom Product Training**: Train YOLO on your specific products
2. **Barcode Integration**: Add barcode scanning for labeled products
3. **Payment Integration**: Connect to payment processing APIs
4. **Receipt Printer**: Add thermal printer support
5. **Database Backend**: Store transactions in SQLite/PostgreSQL
6. **Multi-Camera**: Support multiple camera angles
7. **Analytics Dashboard**: Track sales and inventory

## 📄 License

See LICENSE file in repository.

## 🤝 Contributing

Contributions welcome! Please submit pull requests or open issues.

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review Jetson forums: https://forums.developer.nvidia.com/
3. Ultralytics docs: https://docs.ultralytics.com/

---

**Built for NVIDIA Jetson Orin | Powered by YOLOv8/v11 | FastAPI Backend**
