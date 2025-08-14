# AS7265x Spectral Sensor Tester

Desktop test tool for SparkFun AS7265x Spectral Triad sensors. Built this because there wasn't a good way to test these sensors before integrating them into projects.

## What it does

Tests the basic functionality of AS7265x sensors:
- I2C communication 
- Hardware version detection
- All three sensor devices (UV/Visible/NIR)
- Temperature readings
- Device selection

Shows clear pass/fail results so you know if your sensor is working before you build it into something.

## Hardware setup

Works with Raspberry Pi (tested on Pi 4). Connect your AS7265x like this:

```
AS7265x Pin    Pi GPIO
-----------    -------
GND            Pin 6 (Ground)
3V3            Pin 1 (3.3V)  
SDA            Pin 3 (GPIO 2)
SCL            Pin 5 (GPIO 3)
INT            Pin 11 (GPIO 17) 
RST            Pin 29 (GPIO 5)
```

Enable I2C bus 3 in `/boot/config.txt`:
```
dtoverlay=i2c-gpio,bus=3,i2c_gpio_sda=02,i2c_gpio_scl=03,i2c_gpio_delay_us=1
```

## Running it

```bash
git clone https://github.com/dylanparsons/as7265x-tester.git
cd as7265x-tester
pip3 install smbus2
python3 as7265x_tester.py
```

Connect your sensor, click "START TEST", get a pass/fail result. That's it.

## Why I built this

Was working on a project that needed AS7265x sensors and kept getting bad boards from suppliers. Needed a quick way to test them before soldering into the final design. SparkFun's examples are fine for development but didn't give me the simple go/no-go testing I needed.

This tool saved me from building several prototypes with dead sensors.

## Files and logs

Test results get saved to:
- `~/spectral_test_results/` - JSON files with detailed results
- `~/spectral_test_logs/` - Text logs you can read

## If it doesn't work

**"No I2C Response"** - Check your wiring and make sure I2C bus 3 is enabled

**"Wrong Hardware Version"** - You might have a different sensor (AS7262x instead of AS7265x)

**GPIO errors** - Make sure you can run `sudo raspi-gpio` commands

## License

MIT - use it however you want. If it helps your project, great. If you improve it, even better.

## Contributing

Found a bug? Have a better way to do something? Pull requests welcome. This started as a quick tool for my own use, so there's definitely room for improvement.
