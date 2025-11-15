# Jetson Orin Camera Kiosk - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Transfer to Jetson
```bash
# Copy the jetson-kiosk folder to your Jetson Orin
scp -r jetson-kiosk/ your-jetson-username@jetson-ip:~/
```

### Step 2: Install
```bash
ssh your-jetson-username@jetson-ip
cd ~/jetson-kiosk
chmod +x scripts/*.sh
./scripts/install.sh
```

### Step 3: Test
```bash
# Start the server
sudo systemctl start camera-server

# Open browser
chromium-browser http://localhost:8000
```

### Step 4: Enable Kiosk Mode
```bash
# Reboot to test auto-start
sudo reboot
```

## 📋 Pre-Installation Checklist

Before running the installation:

- [ ] USB camera connected to Jetson
- [ ] Display connected to Jetson
- [ ] Internet connection available
- [ ] User has sudo privileges

## 🧪 Test Camera First

Before full installation, test your camera:

```bash
chmod +x scripts/test-setup.sh
./scripts/test-setup.sh
```

## 🎯 What You Get

After installation:
- ✅ Video server auto-starts on boot
- ✅ Chromium opens in fullscreen kiosk mode
- ✅ Displays real-time camera feed
- ✅ Auto-login configured
- ✅ Screen blanking disabled

## 🔧 Common Issues

### Camera Not Detected
```bash
# Check USB connection
ls -l /dev/video*

# Try different camera index in server.py
CAMERA_INDEX = 0  # Try 1, 2, etc.
```

### Service Won't Start
```bash
# Check logs
sudo journalctl -u camera-server -n 50

# Test manually
cd ~/jetson-kiosk
source venv/bin/activate
python server.py
```

### Kiosk Not Starting
```bash
# Check autostart
ls ~/.config/autostart/

# Test script manually
~/jetson-kiosk/scripts/start-kiosk.sh
```

## 📞 Need Help?

1. Read the full README.md
2. Check logs: `sudo journalctl -u camera-server -f`
3. Test components individually with test scripts

## 🎨 Customization

Edit these files to customize:
- `server.py` - Camera settings, resolution, FPS
- `web/index.html` - UI appearance and behavior
- `scripts/start-kiosk.sh` - Chromium parameters

## ⚡ Quick Commands

```bash
# Service management
sudo systemctl start camera-server      # Start
sudo systemctl stop camera-server       # Stop
sudo systemctl restart camera-server    # Restart
sudo systemctl status camera-server     # Status

# View logs
sudo journalctl -u camera-server -f     # Follow logs

# Manual testing
./scripts/start-server.sh               # Start server manually
./scripts/test-setup.sh                 # Test camera setup

# Uninstall
./scripts/uninstall.sh                  # Remove kiosk setup
```

## 🌐 Access from Network

To view from another device:
```
http://jetson-ip-address:8000
```

Find Jetson IP:
```bash
hostname -I
```

---

**Ready to start? Run `./scripts/install.sh` now!** 🚀
