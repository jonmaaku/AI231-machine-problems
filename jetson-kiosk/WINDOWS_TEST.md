# Quick Windows Test - Manual Steps

## TEST RIGHT NOW ON WINDOWS:

### Option 1: With Real Webcam
1. Open PowerShell in the jetson-kiosk directory
2. Run these commands:

```powershell
# Install dependencies (one time)
pip install fastapi uvicorn opencv-python python-multipart

# Start server
python server.py
```

3. Open browser to: http://localhost:8000
4. You should see your webcam feed!

### Option 2: Without Webcam (Virtual Camera)
1. Run these commands:

```powershell
# Install dependencies (one time)
pip install fastapi uvicorn opencv-python numpy python-multipart

# Start test server with synthetic video
python test_server.py
```

2. Open browser to: http://localhost:8000
3. You'll see animated test video!

## That's it! 🎉

The server works identically on Windows and Jetson.
Only difference: auto-start/kiosk features are Linux-specific.
