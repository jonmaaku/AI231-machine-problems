# Testing the Camera Kiosk on Non-Jetson Systems

## 🖥️ Test on Windows (Current System)

### Option 1: Quick Test with Python

1. **Install Python dependencies** (in your current directory):
```powershell
cd C:\Users\jhon\Desktop\Coding\AI\AI231-machine-problems\jetson-kiosk
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. **Run the server**:
```powershell
python server.py
```

3. **Open browser**:
   - Navigate to: `http://localhost:8000`
   - You should see the camera feed from your webcam

### Option 2: Test Individual Components

#### Test Camera Access:
```powershell
python -c "import cv2; cam = cv2.VideoCapture(0); print('Camera opened:', cam.isOpened()); cam.release()"
```

#### Test Video Server Only:
```powershell
cd jetson-kiosk
python server.py
# Then open http://localhost:8000 in any browser
```

### Windows-Specific Notes:
- ✅ USB webcam will work the same way
- ✅ FastAPI server works identically
- ✅ Web interface works in any browser (Chrome, Edge, Firefox)
- ❌ Kiosk mode auto-start won't work (Linux-only systemd)
- ❌ Auto-login scripts are Linux-specific

---

## 🐧 Test on Ubuntu/Linux Desktop

### Quick Test (No Installation):

1. **Install dependencies**:
```bash
cd ~/jetson-kiosk
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Run server**:
```bash
python server.py
```

3. **Test in browser**:
```bash
firefox http://localhost:8000
# or
chromium-browser http://localhost:8000
```

### Full Kiosk Test:

Run the full installation script, but skip Jetson-specific checks:
```bash
./scripts/install.sh
```

---

## 🍎 Test on macOS

### Setup:

1. **Install dependencies**:
```bash
cd ~/jetson-kiosk
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Run server**:
```bash
python server.py
```

3. **Open browser**:
```bash
open http://localhost:8000
```

### macOS-Specific:
- USB webcam should work with OpenCV
- May need to grant camera permissions in System Preferences
- Auto-start scripts won't work (different from Linux systemd)

---

## 🐳 Test with Docker (Any Platform)

### Create Dockerfile:

```dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY server.py .
COPY web/ ./web/

EXPOSE 8000

CMD ["python", "server.py"]
```

### Run:
```bash
docker build -t camera-kiosk .
docker run --device=/dev/video0 -p 8000:8000 camera-kiosk
```

---

## 🧪 Test Without Real Camera

If you don't have a USB camera, test with a virtual camera:

### Create a Test Server with Fake Video:

```python
# test_server_fake.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
import cv2
import time
from pathlib import Path

app = FastAPI()

def generate_fake_frames():
    """Generate synthetic video frames"""
    width, height = 640, 480
    frame_count = 0
    
    while True:
        # Create a frame with changing colors
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Animate with changing colors
        hue = (frame_count % 180)
        frame[:, :, 0] = hue  # H channel
        frame[:, :, 1] = 255  # S channel
        frame[:, :, 2] = 255  # V channel
        
        # Convert HSV to BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
        
        # Add text
        text = f"Test Frame {frame_count}"
        cv2.putText(frame, text, (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 
                    2, (255, 255, 255), 3)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        frame_count += 1
        time.sleep(1/30)  # 30 FPS

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(
        generate_fake_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/health")
async def health():
    return {"status": "healthy", "camera": "virtual"}

# Serve web interface
WEB_DIR = Path(__file__).parent / "web"
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Run with:
```powershell
python test_server_fake.py
```

---

## 📱 Test from Mobile Device

1. **Find your computer's IP address**:
   - Windows: `ipconfig` (look for IPv4)
   - Linux/Mac: `ifconfig` or `ip addr`

2. **Start the server** on your computer

3. **Open on mobile browser**:
   ```
   http://YOUR_IP_ADDRESS:8000
   ```

---

## ✅ What You Can Test on Non-Jetson:

| Feature | Windows | Linux | macOS | Notes |
|---------|---------|-------|-------|-------|
| Video Server | ✅ | ✅ | ✅ | Works everywhere |
| USB Camera | ✅ | ✅ | ✅ | Any webcam |
| Web Interface | ✅ | ✅ | ✅ | Any browser |
| FastAPI Endpoints | ✅ | ✅ | ✅ | Platform independent |
| Network Access | ✅ | ✅ | ✅ | Same network |
| Auto-start (systemd) | ❌ | ✅ | ❌ | Linux only |
| Kiosk Mode | ⚠️ | ✅ | ⚠️ | Manual on Win/Mac |
| Auto-login | ❌ | ✅ | ⚠️ | Linux specific |

---

## 🎯 Recommended Quick Test:

**On your current Windows machine:**

```powershell
# 1. Navigate to project
cd C:\Users\jhon\Desktop\Coding\AI\AI231-machine-problems\jetson-kiosk

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install fastapi uvicorn opencv-python python-multipart

# 4. Run server
python server.py

# 5. Open browser to http://localhost:8000
```

This will let you test the entire video streaming system with your Windows webcam!
