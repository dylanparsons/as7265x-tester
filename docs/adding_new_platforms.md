# Adding New Platforms

Guide for developers to add support for additional hardware platforms.

## Overview

The AS7265x tester uses a JSON-based configuration system that allows easy addition of new platforms without modifying the core application code.

## Platform Configuration Structure

### Basic Template
```json
{
  "name": "Platform Display Name",
  "platform": "platform_id",
  "description": "Brief description of the platform",
  "i2c_bus": 1,
  "pins": {
    "reset": 0,
    "status_led": 0,
    "sda": 0,
    "scl": 0,
    "interrupt": 0
  },
  "commands": {
    "gpio_set_high": "command to set GPIO high",
    "gpio_set_low": "command to set GPIO low",
    "gpio_get": "command to read GPIO state",
    "i2c_read": "command to read I2C register",
    "i2c_write": "command to write I2C register",
    "i2c_scan": "command to scan I2C bus"
  },
  "communication": {
    "type": "direct|serial|tcp|custom"
  },
  "setup_instructions": [
    "Step 1: Description",
    "Step 2: Description"
  ],
  "dependencies": {
    "python_packages": ["package1", "package2"],
    "system_packages": ["pkg1", "pkg2"]
  }
}
```

## Command Templates

Commands use Python string formatting with these available parameters:

### Available Parameters
- `{pin}` - Pin number from pins section
- `{bus}` - I2C bus number
- `{addr}` - I2C device address (0x49 for AS7265x)
- `{reg}` - Register address
- `{val}` - Value to write

### Command Examples

#### GPIO Commands
```json
"gpio_set_high": "echo 1 > /sys/class/gpio/gpio{pin}/value",
"gpio_set_low": "echo 0 > /sys/class/gpio/gpio{pin}/value",
"gpio_get": "cat /sys/class/gpio/gpio{pin}/value"
```

#### I2C Commands  
```json
"i2c_read": "i2cget -y {bus} 0x{addr:02X} 0x{reg:02X}",
"i2c_write": "i2cset -y {bus} 0x{addr:02X} 0x{reg:02X} 0x{val:02X}",
"i2c_scan": "i2cdetect -y {bus}"
```

## Step-by-Step Platform Addition

### 1. Create Configuration File
Create `configs/your_platform.json`:

```json
{
  "name": "Your Platform Name",
  "platform": "your_platform_id",
  "description": "Platform description",
  "i2c_bus": 1,
  "pins": {
    "reset": 18,
    "status_led": 25,
    "sda": 2,
    "scl": 3,
    "interrupt": 24
  },
  "commands": {
    "gpio_set_high": "your_gpio_high_command {pin}",
    "gpio_set_low": "your_gpio_low_command {pin}",
    "i2c_read": "your_i2c_read_command {bus} {addr} {reg}",
    "i2c_write": "your_i2c_write_command {bus} {addr} {reg} {val}",
    "i2c_scan": "your_i2c_scan_command {bus}"
  },
  "setup_instructions": [
    "Configure your platform for I2C",
    "Set up GPIO permissions",
    "Install required drivers"
  ]
}
```

### 2. Test Configuration
Use the platform tester:

```python
# examples/test_platform_config.py
from platform_manager import PlatformManager

pm = PlatformManager()
pm.select_platform('your_platform_id')

# Test GPIO
cmd = pm.get_command('gpio_set_high', pin=18)
print("GPIO High Command:", cmd)

# Test I2C
cmd = pm.get_command('i2c_scan')
print("I2C Scan Command:", cmd)
```

### 3. Validate Commands
Test each command manually:

```bash
# Test the generated commands
echo "Testing GPIO high command..."
your_gpio_high_command 18

echo "Testing I2C scan..."
your_i2c_scan_command 1
```

## Platform-Specific Considerations

### Linux-based Platforms
- Use sysfs GPIO interface or platform-specific tools
- Leverage existing I2C tools (i2c-tools package)
- Consider permission requirements (sudo, gpio group)

```json
"commands": {
  "gpio_set_high": "echo 1 > /sys/class/gpio/gpio{pin}/value",
  "i2c_read": "i2cget -y {bus} 0x{addr:02X} 0x{reg:02X}"
}
```

### Microcontroller Platforms
- Require serial communication bridge
- Need custom firmware on the microcontroller
- JSON commands represent protocol messages

```json
{
  "communication": {
    "type": "serial",
    "baudrate": 115200,
    "port": "/dev/ttyUSB0"
  },
  "commands": {
    "gpio_set_high": "GPIO:HIGH:{pin}",
    "i2c_read": "I2C:READ:{addr}:{reg}"
  }
}
```

### Network-based Platforms
- Use TCP/UDP for communication
- Commands become API calls or protocol messages

```json
{
  "communication": {
    "type": "tcp",
    "host": "192.168.1.100",
    "port": 8080
  },
  "commands": {
    "gpio_set_high": "POST /gpio/{pin}/high",
    "i2c_read": "GET /i2c/{bus}/{addr}/{reg}"
  }
}
```

## Testing New Platforms

### 1. Basic Connectivity
```python
# Test I2C scanning
success, output, error = run_platform_command('i2c_scan')
assert success and "49" in output
```

### 2. GPIO Control
```python
# Test GPIO toggle
run_platform_command('gpio_set_high', pin=led_pin)
time.sleep(0.5)
run_platform_command('gpio_set_low', pin=led_pin)
```

### 3. AS7265x Communication
```python
# Test sensor communication
hw_version = read_sensor_register(0x01)
assert hw_version == 0x41
```

## Common Pitfalls

### Pin Numbering
Different platforms use different pin numbering schemes:
- **Physical pin numbers** (1-40)
- **GPIO numbers** (GPIO0-GPIO27)  
- **Board-specific labels** (P9_12, etc.)

Make sure your pin numbers match the platform's expected format.

### Permissions
Many platforms require special permissions for GPIO/I2C access:
- Add `sudo` to commands if needed
- Configure user groups (gpio, i2c)
- Set proper udev rules

### Command Formats
Test command templates carefully:
- Verify parameter substitution works
- Check return codes and output formats
- Handle error conditions gracefully

## Example: Adding STM32 Nucleo Support

```json
{
  "name": "STM32 Nucleo-64",
  "platform": "stm32_nucleo",
  "description": "STM32 Nucleo development board with serial bridge",
  "i2c_bus": 1,
  "pins": {
    "reset": "PA8",
    "status_led": "PA5",
    "sda": "PB9", 
    "scl": "PB8",
    "interrupt": "PA9"
  },
  "communication": {
    "type": "serial",
    "baudrate": 115200,
    "port": "/dev/ttyACM0",
    "timeout": 2
  },
  "commands": {
    "gpio_set_high": "GPIO_HIGH:{pin}\\n",
    "gpio_set_low": "GPIO_LOW:{pin}\\n",
    "i2c_read": "I2C_READ:{addr:02X}:{reg:02X}\\n",
    "i2c_write": "I2C_WRITE:{addr:02X}:{reg:02X}:{val:02X}\\n",
    "i2c_scan": "I2C_SCAN:\\n"
  },
  "setup_instructions": [
    "Flash STM32 with AS7265x bridge firmware",
    "Connect via USB (creates /dev/ttyACM0)",
    "Ensure user has access to serial port: sudo usermod -a -G dialout $USER"
  ],
  "dependencies": {
    "python_packages": ["pyserial"],
    "firmware": ["stm32_as7265x_bridge.bin"]
  }
}
```

## Contributing Your Platform

1. **Test thoroughly** on actual hardware
2. **Document setup process** clearly
3. **Include wiring diagrams** if complex
4. **Submit pull request** with config file and documentation
5. **Provide hardware for testing** if possible

Your contribution helps the entire AS7265x community!
