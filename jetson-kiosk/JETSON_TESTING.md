# Testing on Jetson Orin - Complete Guide

This guide shows how to verify the camera kiosk will work on your Jetson Orin BEFORE doing a full installation.

## 🎯 Three Testing Levels

### Level 1: System Check (2 minutes) ⭐ START HERE
### Level 2: Quick Test (5 minutes)
### Level 3: Manual Test (10 minutes)

---

## 📋 Level 1: System Check (Recommended First Step)

This comprehensive check verifies all requirements WITHOUT installing anything.

### Run the Check:

```bash
cd ~/jetson-kiosk
chmod +x scripts/check-system.sh
./scripts/check-system.sh
```

### What It Tests (15 Checks):

1. ✅ **Jetson Platform** - Confirms running on NVIDIA Jetson
2. ✅ **JetPack Version** - Checks JetPack installation
3. ✅ **Python Version** - Verifies Python 3.8+
4. ✅ **pip** - Checks pip3 availability
5. ✅ **USB Camera** - Detects /dev/video* devices
6. ✅ **Camera Access** - Tests OpenCV camera capture
7. ✅ **Video Group** - Checks user permissions
8. ✅ **Chromium Browser** - Verifies browser installed
9. ✅ **Display Server** - Checks X11/Wayland running
10. ✅ **Network** - Tests internet connectivity
11. ✅ **Disk Space** - Verifies sufficient storage
12. ✅ **systemd** - Checks service manager
13. ✅ **Port 8000** - Verifies port available
14. ✅ **System Tools** - Checks curl, wget, etc.
15. ✅ **Sudo Access** - Verifies installation privileges

### Expected Output:

```
======================================
Jetson Orin Camera Kiosk
Pre-Installation Check
======================================

[1/15] Checking Jetson platform...
✓ PASS - Running on NVIDIA Jetson
        # R35 (release), REVISION: 4.1

[2/15] Checking JetPack version...
✓ PASS - JetPack installed
        Version: 5.1.2-b104

[3/15] Checking Python...
✓ PASS - Python 3.8 found
        Python 3.8.10

... (continues for all 15 checks) ...

======================================
Test Summary
======================================
Passed:  13
Warnings: 2
Failed:  0

✓ System is ready for installation!
```

### If You See Failures:

The script will tell you exactly what to fix:

```bash
# Example fixes:
sudo apt update

# Install Python
sudo apt install python3 python3-pip python3-venv

# Install Chromium
sudo apt install chromium-browser

# Add user to video group
sudo usermod -a -G video $USER
# Then log out and back in
```

---

## 🚀 Level 2: Quick Test (Minimal Installation)

Tests camera streaming with minimal package installation.

### Steps:

```bash
cd ~/jetson-kiosk
chmod +x scripts/quick-test.sh
./scripts/quick-test.sh
```

### What It Does:

1. Checks Python is installed
2. Checks camera is detected
3. Tests if packages are available (or tells you what to install)
4. Tests actual camera capture
5. Verifies frame capture works

### Expected Output:

```
========================================
Jetson Camera Quick Test
========================================

Checking Python...
✓ Python 3 found: Python 3.8.10

Checking camera...
✓ Camera device(s) found: /dev/video0 /dev/video1

Testing camera with Python...
⚠️  Missing Python packages: fastapi, uvicorn, opencv-python

Install them with:
  pip3 install fastapi uvicorn opencv-python
```

### Install Packages & Test:

```bash
# Install required packages
pip3 install fastapi uvicorn opencv-python

# Run quick test again
./scripts/quick-test.sh

# Should now show:
# ✓ Camera working! Captured 640x480 frame
# Camera test successful! 🎉
```

---

## 🧪 Level 3: Manual Test (Full Functionality)

Tests the actual server and web interface WITHOUT systemd/autostart.

### Step 1: Install Packages Locally

```bash
cd ~/jetson-kiosk

# Option A: Install globally
pip3 install -r requirements.txt

# Option B: Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Test Camera Access

```bash
# Test camera manually
python3 -c "
import cv2
cam = cv2.VideoCapture(0)
print('Camera opened:', cam.isOpened())
ret, frame = cam.read()
print('Frame captured:', ret)
if ret:
    print('Resolution:', frame.shape[1], 'x', frame.shape[0])
cam.release()
"
```

**Expected output:**
```
Camera opened: True
Frame captured: True
Resolution: 640 x 480
```

### Step 3: Start Video Server

```bash
# Make sure you're in the jetson-kiosk directory
cd ~/jetson-kiosk

# If using venv, activate it:
source venv/bin/activate

# Start the server
python3 server.py
```

**Expected output:**
```
INFO:     Started server process [1234]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 4: Test in Browser

**Option 1: On the Jetson (GUI)**
```bash
# Open in another terminal
chromium-browser http://localhost:8000
```

**Option 2: From Another Computer**
```bash
# Find Jetson IP
hostname -I

# On another computer, open browser to:
http://jetson-ip-address:8000
```

### Step 5: Test Features

In the browser, verify:
- [ ] Video feed shows camera image
- [ ] Video is smooth (not choppy)
- [ ] Status shows "Live Stream Active"
- [ ] Exit button appears on mouse hover
- [ ] Press ESC shows exit dialog
- [ ] Fullscreen works (F key)
- [ ] Page reload works (R key)

### Step 6: Test Exit

1. Press **ESC** or **Q**
2. Click **"Yes, Exit"** in dialog
3. Browser should close or show exit screen

### Step 7: Stop Server

```bash
# In terminal where server is running:
# Press Ctrl+C

# Server should stop gracefully:
# INFO:     Shutting down
# INFO:     Application shutdown complete.
```

---

## ✅ Success Criteria

### Minimum Requirements (Must Pass):
- ✅ Python 3.8+ installed
- ✅ Camera detected at /dev/video*
- ✅ Camera accessible with OpenCV
- ✅ Server starts without errors
- ✅ Web page loads
- ✅ Video stream displays

### Recommended (Should Pass):
- ✅ Chromium browser installed
- ✅ User in 'video' group
- ✅ Display server running
- ✅ Network connectivity
- ✅ Sufficient disk space
- ✅ systemd available

### Nice to Have:
- ✅ Running on actual Jetson
- ✅ JetPack installed
- ✅ GPU acceleration available

---

## 🐛 Common Issues & Fixes

### Issue: "Cannot open camera"

**Check:**
```bash
# 1. Camera is connected
lsusb | grep -i camera

# 2. Video devices exist
ls -l /dev/video*

# 3. Permissions
groups | grep video

# 4. Try different camera index
python3 -c "import cv2; print(cv2.VideoCapture(1).isOpened())"
```

**Fix:**
```bash
# Add to video group
sudo usermod -a -G video $USER
# Log out and back in

# Or try different camera in server.py:
# Change CAMERA_INDEX = 0 to CAMERA_INDEX = 1
```

### Issue: "ModuleNotFoundError: No module named 'cv2'"

**Fix:**
```bash
# Install OpenCV
pip3 install opencv-python

# Or if using system Python:
sudo apt install python3-opencv
```

### Issue: "Address already in use (port 8000)"

**Check:**
```bash
# See what's using port 8000
sudo netstat -tlnp | grep :8000
# or
sudo ss -tlnp | grep :8000
```

**Fix:**
```bash
# Kill process using port 8000
sudo kill -9 <PID>

# Or change port in server.py:
# uvicorn.run(app, host="0.0.0.0", port=8080)
```

### Issue: "No display"

**Check:**
```bash
echo $DISPLAY
# Should show something like :0 or :1
```

**Fix:**
```bash
# Make sure you're in GUI mode, not SSH/terminal only
# Or set DISPLAY variable:
export DISPLAY=:0
```

### Issue: Video is choppy/slow

**Try:**
1. Lower resolution in server.py:
   ```python
   VGA_WIDTH = 320
   VGA_HEIGHT = 240
   ```

2. Lower FPS:
   ```python
   FPS = 15
   ```

3. Lower JPEG quality:
   ```python
   cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
   ```

---

## 🎯 Quick Decision Tree

```
Start → Run check-system.sh
          ↓
     All passed?
      ↓         ↓
     YES        NO → Fix issues → Retry
      ↓
  Run quick-test.sh
      ↓
  Packages OK?
      ↓         ↓
     YES        NO → Install packages → Retry
      ↓
  Camera works?
      ↓         ↓
     YES        NO → Fix camera → Retry
      ↓
Test manually (python3 server.py)
      ↓
  Server starts & video shows?
      ↓         ↓
     YES        NO → Debug → Retry
      ↓
Ready for full installation!
      ↓
  ./scripts/install.sh
```

---

## 📊 Testing Checklist

Before running full installation, verify:

**System Checks:**
- [ ] check-system.sh passes (0 failures)
- [ ] quick-test.sh shows camera working
- [ ] Python 3.8+ installed
- [ ] pip3 working

**Camera Tests:**
- [ ] Camera detected (/dev/video*)
- [ ] Can capture with OpenCV
- [ ] User in video group
- [ ] Frame resolution correct

**Server Tests:**
- [ ] server.py starts without errors
- [ ] Port 8000 available
- [ ] No module import errors
- [ ] Logs show "Application startup complete"

**Web Interface Tests:**
- [ ] Browser can access localhost:8000
- [ ] Video feed displays
- [ ] Video is smooth
- [ ] Exit button works
- [ ] Keyboard shortcuts work

**If all checked:** ✅ Ready for installation!

---

## 🚀 After Testing Successfully

Once all tests pass, proceed with full installation:

```bash
# Full installation with auto-start
./scripts/install.sh

# Or just install without auto-start
pip3 install -r requirements.txt
# Then start manually when needed
```

---

## 📝 Test Log Template

Keep track of your testing:

```
Date: ___________
Jetson Model: ___________
JetPack Version: ___________

System Check Results:
- check-system.sh: PASS / FAIL
  Failures: ___________

Camera Tests:
- Camera detected: YES / NO
- OpenCV capture: YES / NO
- Resolution: ___________

Server Tests:
- Server starts: YES / NO
- Web access: YES / NO
- Video quality: GOOD / OK / POOR

Issues Found:
1. ___________
2. ___________

Next Steps:
___________
```

---

**Ready to test? Start with:** `./scripts/check-system.sh` 🚀
