# Exiting Kiosk Mode - Complete Guide

This guide explains all the ways to exit the Jetson Camera Kiosk mode.

## 🎯 Quick Exit Methods

### 1. **EXIT Button** (Easiest) ⭐
- **How:** Move your mouse anywhere on the screen
- **What appears:** Red "✕ EXIT KIOSK" button in top-right corner
- **Action:** Click the button and confirm
- **Result:** Browser closes or shows exit screen

### 2. **Keyboard Shortcuts**
- **Press:** `ESC` or `Q` key
- **What appears:** Exit confirmation dialog
- **Action:** Click "Yes, Exit" to confirm
- **Result:** Kiosk closes

### 3. **Force Close Browser**
- **Press:** `Alt+F4` (Linux) or `Ctrl+W`
- **Result:** Browser closes immediately
- **Note:** May auto-restart if enabled

---

## 🛠️ Advanced Exit Methods

### 4. **Stop from Terminal (Console)**
1. **Switch to console:** Press `Ctrl+Alt+F2` (or F3, F4)
2. **Login:** Enter your username and password
3. **Stop kiosk:**
   ```bash
   ~/jetson-kiosk/scripts/stop-kiosk.sh
   ```
4. **Return to GUI:** Press `Ctrl+Alt+F7` (or F1)

### 5. **Stop via SSH (Remote)**
```bash
# From another computer
ssh your-username@jetson-ip-address

# Stop the kiosk
~/jetson-kiosk/scripts/stop-kiosk.sh
```

### 6. **Manual Terminal Commands**
```bash
# Disable auto-restart
rm /tmp/jetson-kiosk-restart

# Close browser
pkill chromium

# Stop kiosk script
pkill -f start-kiosk.sh
```

---

## 🔄 Auto-Restart Behavior

The kiosk can be configured to automatically restart when closed.

### Check Auto-Restart Status
```bash
# If this file exists, auto-restart is enabled
ls /tmp/jetson-kiosk-restart
```

### Disable Auto-Restart
```bash
# Method 1: Use toggle script
~/jetson-kiosk/scripts/toggle-restart.sh

# Method 2: Manual
rm /tmp/jetson-kiosk-restart
```

### Enable Auto-Restart
```bash
# Method 1: Use toggle script
~/jetson-kiosk/scripts/toggle-restart.sh

# Method 2: Manual
touch /tmp/jetson-kiosk-restart
```

---

## 📋 Exit Scenarios

### Scenario 1: Temporary Exit (Will Restart After Reboot)
**Situation:** You want to close kiosk now, but have it restart on next boot.

**Solution:**
1. Press `ESC` or click EXIT button
2. Confirm exit
3. Kiosk closes but autostart remains configured

**On next reboot:** Kiosk will start automatically

### Scenario 2: Permanent Exit (Disable Completely)
**Situation:** You want to stop kiosk and prevent it from starting again.

**Solution:**
```bash
# 1. Stop kiosk
~/jetson-kiosk/scripts/stop-kiosk.sh

# 2. Remove autostart
rm ~/.config/autostart/camera-kiosk.desktop

# 3. Disable auto-restart
rm /tmp/jetson-kiosk-restart

# 4. Reboot (optional)
sudo reboot
```

**On next reboot:** Kiosk will NOT start

### Scenario 3: Exit But Keep Auto-Restart Off
**Situation:** You want to close kiosk now and prevent immediate restart, but keep autostart configured.

**Solution:**
```bash
# Disable auto-restart first
rm /tmp/jetson-kiosk-restart

# Then close browser
pkill chromium
```

**Result:** Kiosk closes and won't restart until you enable auto-restart or reboot

---

## 🚨 Emergency Exit Methods

### If Mouse/Keyboard Don't Work

**Option 1: Power Button**
- Press and hold power button for 5 seconds
- System will shut down
- Restart and disable kiosk before GUI loads

**Option 2: SSH from Another Device**
```bash
ssh user@jetson-ip
~/jetson-kiosk/scripts/stop-kiosk.sh
sudo reboot
```

**Option 3: Physical Access**
1. Connect keyboard (if not already connected)
2. Press `Ctrl+Alt+F2` to switch to console
3. Login and run stop script

---

## 🎛️ Control Scripts Reference

### stop-kiosk.sh
**Purpose:** Gracefully stop kiosk mode
```bash
~/jetson-kiosk/scripts/stop-kiosk.sh
```
**What it does:**
- Removes auto-restart flag
- Closes Chromium browser
- Stops kiosk script
- Displays status

### toggle-restart.sh
**Purpose:** Enable/disable auto-restart
```bash
~/jetson-kiosk/scripts/toggle-restart.sh
```
**What it does:**
- Shows current auto-restart status
- Toggles the setting
- Confirms new status

### start-kiosk.sh
**Purpose:** Manually start kiosk mode
```bash
~/jetson-kiosk/scripts/start-kiosk.sh
```
**What it does:**
- Waits for video server
- Launches Chromium in kiosk mode
- Handles auto-restart if enabled

---

## 📝 Notes

### Auto-Restart Flag Location
- **Path:** `/tmp/jetson-kiosk-restart`
- **Type:** Empty flag file
- **Persistence:** Deleted on reboot (must be recreated by startup script)

### Exit Instructions Visibility
- **On-screen hint:** Hover mouse to see "Press ESC or Q to exit..."
- **Location:** Bottom center of screen
- **Timing:** Appears when mouse moves

### Confirmation Dialog
- **Purpose:** Prevent accidental exits
- **Options:** "Yes, Exit" or "Cancel"
- **Triggered by:** ESC key, Q key, or EXIT button

---

## ✅ Verification

After exiting, verify kiosk is stopped:

```bash
# Check if Chromium is running
pgrep chromium
# (should return nothing)

# Check if kiosk script is running
pgrep -f start-kiosk.sh
# (should return nothing)

# Check auto-restart status
ls /tmp/jetson-kiosk-restart
# (should show "No such file" if disabled)
```

---

## 🔧 Troubleshooting

### "Browser won't close"
**Try:**
1. `pkill -9 chromium` (force kill)
2. Reboot system
3. Disable autostart before reboot

### "Kiosk keeps restarting"
**Try:**
1. `rm /tmp/jetson-kiosk-restart`
2. `pkill -f start-kiosk.sh`
3. `pkill chromium`

### "Can't access terminal"
**Try:**
1. `Ctrl+Alt+F2` for console
2. SSH from another device
3. Use power button to reboot

### "Exit button doesn't appear"
**Try:**
1. Move mouse around the screen
2. Press ESC or Q key instead
3. Use Alt+F4 to force close

---

## 📞 Quick Reference Card

| Method | Command/Action | Prevents Restart? |
|--------|---------------|-------------------|
| Exit Button | Click "EXIT KIOSK" | No |
| ESC/Q Key | Press ESC or Q | No |
| Alt+F4 | Press Alt+F4 | No |
| Stop Script | `stop-kiosk.sh` | Yes |
| Manual | `rm /tmp/jetson-kiosk-restart; pkill chromium` | Yes |
| Console | Ctrl+Alt+F2, then stop-kiosk.sh | Yes |
| SSH | SSH in, run stop-kiosk.sh | Yes |

**Note:** Methods that prevent restart require removing the auto-restart flag.

---

**Need more help?** Check the main README.md for full documentation.
