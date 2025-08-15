# Desktop Launcher Setup

## Installation Instructions

### 1. Save the GUI Script
Save the GUI program as `/home/pi/spectral_test_gui.py`:

```bash
# Make it executable
chmod +x /home/pi/spectral_test_gui.py
```

### 2. Create Desktop Launcher
Create a file `/home/pi/Desktop/Spectral_Test.desktop`:

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=Spectral Sensor Test
Comment=Test AS7265x Spectral Sensors
Exec=python3 /home/pi/spectral_test_gui.py
Icon=/home/pi/spectral_icon.png
Terminal=false
Categories=Development;
StartupNotify=true
```

### 3. Make Desktop File Executable
```bash
chmod +x /home/pi/Desktop/Spectral_Test.desktop
```

### 4. Optional: Create Icon
Save this as `/home/pi/spectral_icon.png` (or use any 48x48 PNG image):
- You can download a sensor/electronics icon or create a simple one
- Or skip this step - the launcher will work without an icon

### 5. Enable I2C Bus 3
Add to `/boot/config.txt`:
```
dtoverlay=i2c-gpio,bus=3,i2c_gpio_sda=02,i2c_gpio_scl=03,i2c_gpio_delay_us=1
```

Then reboot: `sudo reboot`

## Usage

### Starting the Program
1. **Double-click** the "Spectral Sensor Test" icon on the desktop
2. The GUI window will open
3. Connection status will show if a sensor is detected

### Testing a Sensor
1. **Connect** the 6-wire harness to your test fixture
2. **Enter serial number** (optional)
3. **Click "START TEST"** button
4. **Wait** for results (10-15 seconds)
5. **Read result**: Green checkmark = PASS, Red X = FAIL

### Features
- **Real-time connection status** - Shows if sensor is connected
- **Progress indication** - Progress bar during testing
- **Detailed log** - Shows exactly what's being tested
- **Serial number tracking** - Optional logging
- **Save results** - Export test data to JSON files
- **Reset sensor** - Hardware reset button
- **Test counter** - Shows how many tests have been run

### Results are Saved To:
`/home/pi/spectral_test_results/spectral_tests_YYYYMMDD_HHMMSS.json`

## Troubleshooting

### "No Connection" Status
- Check I2C wiring (SDA/SCL)
- Verify 3.3V power to sensor
- Ensure I2C bus 3 is enabled

### "GPIO not available" Warning
- Program will still work but without hardware reset
- Install RPi.GPIO: `pip3 install RPi.GPIO`

### Permission Errors
- Run: `sudo usermod -a -G gpio pi`
- Logout and login again

### Program Won't Start
- Open terminal and run: `python3 /home/pi/spectral_test_gui.py`
- Check error messages
- Install missing dependencies: `pip3 install smbus2`

## Quick Test (No Hardware)
You can run the GUI without hardware connected - it will show "No Connection" but all buttons work. This is useful for testing the interface.