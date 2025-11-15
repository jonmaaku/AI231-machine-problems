# Jetson Testing - Quick Reference Card

## 🏃 Quick Commands

```bash
# 1. CHECK SYSTEM FIRST (2 min)
./scripts/check-system.sh

# 2. QUICK CAMERA TEST (1 min)
./scripts/quick-test.sh

# 3. MANUAL TEST (5 min)
pip3 install fastapi uvicorn opencv-python
python3 server.py
# Open browser to http://localhost:8000

# 4. FULL INSTALL (if tests pass)
./scripts/install.sh
```

---

## ✅ Must Pass Before Installation

| Check | Command | Expected |
|-------|---------|----------|
| Python | `python3 --version` | Python 3.8+ |
| Camera | `ls /dev/video*` | Shows /dev/video0 |
| Capture | `python3 -c "import cv2; print(cv2.VideoCapture(0).isOpened())"` | True |
| Browser | `chromium-browser --version` | Shows version |
| Groups | `groups` | Includes "video" |

---

## 🚨 Common Fixes

```bash
# No camera?
lsusb                                    # Check USB devices
ls /dev/video*                          # Check video devices

# Permission denied?
sudo usermod -a -G video $USER          # Add to video group
# Then log out and back in

# Python missing?
sudo apt install python3 python3-pip    # Install Python

# Chromium missing?
sudo apt install chromium-browser       # Install browser

# Packages missing?
pip3 install fastapi uvicorn opencv-python
```

---

## 📊 Decision Flow

```
1. Transfer files to Jetson
   ↓
2. Run: ./scripts/check-system.sh
   ↓
   Passed? → YES → Go to step 5
   ↓ NO
3. Fix issues shown in output
   ↓
4. Re-run check-system.sh
   ↓
5. Run: ./scripts/install.sh
   ↓
6. Reboot
   ↓
7. Kiosk starts automatically! 🎉
```

---

## 🎯 Test Results Interpretation

### check-system.sh Output:
- **0 Failures:** ✅ Ready for installation
- **1-2 Failures:** ⚠️ Fix issues, then proceed
- **3+ Failures:** ❌ Major problems, see output

### quick-test.sh Output:
- **"Camera test successful!"** → ✅ Ready
- **"Missing packages"** → Install packages shown
- **"Cannot open camera"** → Check connections/permissions

---

## 📞 Help Resources

- **Full Testing Guide:** See `JETSON_TESTING.md`
- **Quick Start:** See `QUICKSTART.md`
- **Full Docs:** See `README.md`
- **Exit Help:** See `EXIT_GUIDE.md`

---

**Start here:** `./scripts/check-system.sh` 🚀
