# 📋 Jetson POS System - Deployment Checklist

## Pre-Deployment

### Hardware Setup
- [ ] NVIDIA Jetson Orin installed and powered
- [ ] USB camera connected and tested
- [ ] Display connected (HDMI/DisplayPort)
- [ ] Network connectivity verified (Ethernet/WiFi)
- [ ] Power supply adequate (Jetson Orin requires 15W-60W depending on model)
- [ ] Adequate cooling (fan/heatsink installed)

### Software Prerequisites
- [ ] Ubuntu 20.04/22.04 installed (JetPack 5.0+)
- [ ] System updated: `sudo apt update && sudo apt upgrade`
- [ ] Python 3.8+ installed: `python3 --version`
- [ ] Pip installed: `pip3 --version`
- [ ] Git installed (if cloning): `git --version`
- [ ] Chromium browser installed: `chromium-browser --version`

## Installation Steps

### 1. Project Setup
- [ ] Project copied to Jetson: `~/jetson-kiosk/`
- [ ] Navigate to directory: `cd ~/jetson-kiosk`
- [ ] Make scripts executable: `chmod +x *.sh scripts/*.sh`

### 2. Environment Setup
- [ ] Virtual environment created: `python3 -m venv venv`
- [ ] Virtual environment activated: `source venv/bin/activate`
- [ ] Pip upgraded: `pip install --upgrade pip`
- [ ] Requirements installed: `pip install -r requirements.txt`

### 3. YOLO Model
- [ ] Model downloaded: YOLO will auto-download on first run
- [ ] Test model loading: `python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"`
- [ ] TensorRT export completed (happens automatically on first inference)

### 4. Camera Configuration
- [ ] Camera detected: `ls /dev/video*`
- [ ] Camera accessible: `v4l2-ctl --list-devices`
- [ ] User in video group: `groups $USER` (should show 'video')
- [ ] If not: `sudo usermod -aG video $USER` then logout/login
- [ ] Camera index correct in `server.py` (usually 0)

### 5. Testing
- [ ] Diagnostic test passed: `python test_pos.py`
- [ ] All tests showing ✅ PASS
- [ ] Server starts manually: `python server.py`
- [ ] Health endpoint responding: `curl http://localhost:8000/health`
- [ ] Camera feed visible: Open `http://localhost:8000/`
- [ ] POS interface working: Open `http://localhost:8000/pos.html`
- [ ] Detection working: Products detected in camera view
- [ ] Cart operations working: Add/remove/checkout tested

## Configuration

### Server Settings
- [ ] Camera index verified: `CAMERA_INDEX = 0` in `server.py`
- [ ] Resolution appropriate: `VGA_WIDTH = 1080, VGA_HEIGHT = 720`
- [ ] FPS suitable: `FPS = 60` (or lower if needed)
- [ ] YOLO model selected: `YOLO_MODEL = "yolov8n.pt"`
- [ ] Confidence threshold tuned: `CONFIDENCE_THRESHOLD = 0.5`

### Product Database
- [ ] Products added to `PRODUCT_DATABASE` in `server.py`
- [ ] Prices configured correctly
- [ ] Categories assigned
- [ ] Product names match YOLO classes (or custom model trained)

### Performance Optimization
- [ ] Jetson in max performance mode: `sudo nvpmodel -m 0`
- [ ] Clocks maximized: `sudo jetson_clocks`
- [ ] Inference latency <500ms verified
- [ ] TensorRT acceleration working (check logs on first run)

## Production Deployment

### Auto-Start Configuration

#### 1. Server Service
- [ ] Service file created: `/etc/systemd/system/pos-server.service`
- [ ] Username updated in service file
- [ ] Paths corrected in service file
- [ ] Service enabled: `sudo systemctl enable pos-server`
- [ ] Service started: `sudo systemctl start pos-server`
- [ ] Service status verified: `sudo systemctl status pos-server`
- [ ] Logs checked: `sudo journalctl -u pos-server -f`

#### 2. Kiosk Mode
- [ ] Autostart directory exists: `mkdir -p ~/.config/autostart`
- [ ] Desktop entry created: `~/.config/autostart/pos-kiosk.desktop`
- [ ] Chromium kiosk URL correct: `http://localhost:8000/pos.html`
- [ ] Auto-login configured (optional but recommended)

#### 3. Display Settings
- [ ] Screen blanking disabled: `gsettings set org.gnome.desktop.session idle-delay 0`
- [ ] Screensaver disabled: `gsettings set org.gnome.desktop.screensaver lock-enabled false`
- [ ] Power saving off: `gsettings set org.gnome.settings-daemon.plugins.power idle-dim false`
- [ ] Display brightness set appropriately

### System Settings
- [ ] Hostname set: `sudo hostnamectl set-hostname jetson-pos-01`
- [ ] Timezone configured: `sudo timedatectl set-timezone Your/Timezone`
- [ ] Network configured (static IP recommended for production)
- [ ] Firewall configured if needed: `sudo ufw allow 8000/tcp`

## Final Testing

### Functionality Tests
- [ ] Reboot test: System auto-starts after reboot
- [ ] Camera detection: Products detected correctly
- [ ] Cart operations: Add/update/remove/clear working
- [ ] Checkout: Receipt generated correctly
- [ ] Auto-scan mode: Automatic detection working
- [ ] Manual scan: On-demand scanning working
- [ ] Performance: Latency consistently <500ms
- [ ] UI responsive: No lag or freezing

### Stress Testing
- [ ] Multiple rapid scans: System handles continuous scanning
- [ ] Large cart: 50+ items in cart performs well
- [ ] Extended operation: Runs 8+ hours without issues
- [ ] Memory stable: No memory leaks (check with `htop`)
- [ ] Temperature: Jetson stays cool (check `sudo tegrastats`)

### Error Recovery
- [ ] Camera disconnect/reconnect: System recovers
- [ ] Network interruption: System continues operating
- [ ] Server restart: Service restarts automatically
- [ ] Browser crash: Kiosk auto-restarts (if configured)

## Documentation

### User Documentation
- [ ] Operating instructions created
- [ ] Checkout procedure documented
- [ ] Troubleshooting guide available
- [ ] Emergency contact information posted

### Technical Documentation
- [ ] Network configuration documented
- [ ] Product database documented
- [ ] Credentials stored securely
- [ ] Backup procedures documented

## Maintenance Setup

### Monitoring
- [ ] Log rotation configured: `sudo nano /etc/logrotate.d/pos-server`
- [ ] Disk space monitoring set up
- [ ] Performance monitoring enabled: `tegrastats` logging

### Backups
- [ ] Product database backup schedule
- [ ] Transaction logs backup plan
- [ ] System configuration backup
- [ ] Recovery procedure tested

### Updates
- [ ] Update procedure documented
- [ ] YOLO model update process defined
- [ ] Python dependencies update schedule
- [ ] System update policy established

## Security

### Access Control
- [ ] Root access restricted
- [ ] User accounts properly configured
- [ ] SSH access secured (if enabled)
- [ ] Physical access to Jetson secured

### Network Security
- [ ] Firewall configured: `sudo ufw enable`
- [ ] Unnecessary services disabled
- [ ] Network segmentation considered
- [ ] HTTPS considered for production (with reverse proxy)

## Training

### Staff Training
- [ ] Operating procedures trained
- [ ] Basic troubleshooting trained
- [ ] Checkout process trained
- [ ] Emergency procedures trained

### Technical Training
- [ ] Server restart procedure
- [ ] Log access and interpretation
- [ ] Basic configuration changes
- [ ] Contact information for advanced support

## Go-Live Checklist

### Pre-Launch (1 day before)
- [ ] All tests passing
- [ ] Performance verified
- [ ] Documentation complete
- [ ] Staff trained
- [ ] Support plan in place

### Launch Day
- [ ] System powered on and auto-started
- [ ] Initial smoke test completed
- [ ] Staff ready and confident
- [ ] Support available
- [ ] Monitoring active

### Post-Launch (1 week)
- [ ] Daily health checks
- [ ] Performance monitoring
- [ ] User feedback collected
- [ ] Issues logged and resolved
- [ ] Fine-tuning as needed

## Troubleshooting Reference

### Quick Diagnostics
```bash
# Check service status
sudo systemctl status pos-server

# View recent logs
sudo journalctl -u pos-server -n 100

# Test camera
ls /dev/video* && v4l2-ctl --list-devices

# Check server response
curl http://localhost:8000/health

# Monitor system
sudo tegrastats

# Check processes
ps aux | grep python

# Check disk space
df -h

# Check memory
free -h
```

### Emergency Procedures
- [ ] Server restart: `sudo systemctl restart pos-server`
- [ ] Full reboot: `sudo reboot`
- [ ] Stop kiosk: `pkill chromium`
- [ ] Manual server: `cd ~/jetson-kiosk && source venv/bin/activate && python server.py`

## Sign-Off

- [ ] **Hardware Setup**: Verified by _________________ Date: _______
- [ ] **Software Installation**: Verified by _________________ Date: _______
- [ ] **Testing Complete**: Verified by _________________ Date: _______
- [ ] **Production Ready**: Verified by _________________ Date: _______
- [ ] **Staff Trained**: Verified by _________________ Date: _______
- [ ] **Go-Live Approved**: Approved by _________________ Date: _______

## Notes

```
Installation Date: __________________
Jetson Serial Number: __________________
Camera Model: __________________
Network IP: __________________
Support Contact: __________________

Additional Notes:
_____________________________________________________
_____________________________________________________
_____________________________________________________
```

---

**Deployment Status**: ☐ Not Started | ☐ In Progress | ☐ Complete | ☐ Production

**Last Updated**: ___________________
**Updated By**: ___________________
