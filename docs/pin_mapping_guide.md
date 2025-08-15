# Pin Mapping Guide

Complete wiring diagrams and pin mappings for all supported platforms.

## AS7265x Sensor Pinout

The SparkFun AS7265x Spectral Triad requires these connections:

```
AS7265x Pin    Function    Description
-----------    --------    -----------
3V3            Power       3.3V supply (±10%)
GND            Ground      Power and signal ground
SDA            I2C Data    I2C data line (requires pullup)
SCL            I2C Clock   I2C clock line (requires pullup)  
INT            Interrupt   Data ready interrupt (optional)
RST            Reset       Hardware reset (active low)
```

## Raspberry Pi 4 Wiring

### Standard Configuration
```
AS7265x    →    Pi 4 GPIO    →    Physical Pin
-------         ---------         ------------
3V3        →    3.3V        →    Pin 1
GND        →    Ground      →    Pin 6
SDA        →    GPIO 2      →    Pin 3
SCL        →    GPIO 3      →    Pin 5
INT        →    GPIO 17     →    Pin 11
RST        →    GPIO 5      →    Pin 29

Optional:
Status LED →    GPIO 21     →    Pin 40
```

### Breadboard Layout
```
    AS7265x Breakout
    ┌─────────────────┐
    │ ●3V3    SDA●    │
    │ ●GND    SCL●    │  
    │ ●INT    RST●    │
    └─────────────────┘
      │ │ │     │ │ │
      │ │ │     │ │ └──── GPIO 5 (Pin 29)
      │ │ │     │ └────── GPIO 3 (Pin 5) 
      │ │ │     └──────── GPIO 2 (Pin 3)
      │ │ └────────────── GPIO 17 (Pin 11)
      │ └──────────────── Ground (Pin 6)
      └────────────────── 3.3V (Pin 1)
```

### I2C Bus Configuration
Add to `/boot/config.txt`:
```bash
# Enable I2C bus 3 with custom pins
dtoverlay=i2c-gpio,bus=3,i2c_gpio_sda=02,i2c_gpio_scl=03,i2c_gpio_delay_us=1

# Enable standard I2C (optional)
dtparam=i2c_arm=on
```

## Arduino Leonardo Wiring

### Pin Mapping
```
AS7265x    →    Leonardo    →    Arduino Pin
-------         --------         -----------
3V3        →    3.3V        →    3.3V
GND        →    Ground      →    GND
SDA        →    SDA         →    Pin 2 (SDA)
SCL        →    SCL         →    Pin 3 (SCL)
INT        →    Digital     →    Pin 7
RST        →    Digital     →    Pin 8

Status LED →    Digital     →    Pin 13 (built-in)
```

### Breadboard Connections
```
Leonardo                AS7265x
┌─────────┐            ┌─────────┐
│   3.3V  ●────────────● 3V3     │
│   GND   ●────────────● GND     │
│   SDA   ●────────────● SDA     │
│   SCL   ●────────────● SCL     │
│   D7    ●────────────● INT     │
│   D8    ●────────────● RST     │
│   D13   ●────[LED]              │
└─────────┘            └─────────┘
```

## ESP32 DevKit Wiring

### Pin Assignment
```
AS7265x    →    ESP32       →    GPIO Number
-------         -----             -----------
3V3        →    3.3V        →    3.3V
GND        →    Ground      →    GND
SDA        →    GPIO21      →    21
SCL        →    GPIO22      →    22
INT        →    GPIO26      →    26
RST        →    GPIO25      →    25

Status LED →    GPIO2       →    2 (built-in)
```

### Schematic
```
    ESP32-DevKit-V1          AS7265x
    ┌─────────────────┐     ┌─────────┐
    │ 3V3        GPIO21●─────●SDA      │
    │ GND        GPIO22●─────●SCL      │
    │ EN         GPIO26●─────●INT      │
    │ GPIO2●     GPIO25●─────●RST      │
    │ │          3V3  ●─────●3V3      │
    │ │          GND  ●─────●GND      │
    │ └──[LED]              └─────────┘
    └─────────────────┘
```

## BeagleBone Black Wiring

### Pin Mapping (P9 Header)
```
AS7265x    →    BeagleBone     →    Header Pin
-------         ----------          ----------
3V3        →    VDD_3V3        →    P9_3
GND        →    DGND           →    P9_1
SDA        →    I2C2_SDA       →    P9_20
SCL        →    I2C2_SCL       →    P9_19
INT        →    GPIO1_16       →    P9_15
RST        →    GPIO1_12       →    P9_12

Status LED →    GPIO1_14       →    P9_14
```

### Header Diagram
```
BeagleBone P9 Header (partial)
┌──────────────────────────┐
│  1● GND          3V3 ●3  │
│   ●              ●      │
│ 12● GPIO1_12     ●14    │ GPIO1_14
│ 15● GPIO1_16     ●      │
│   ●              ●      │
│ 19● I2C2_SCL     SDA ●20│ I2C2_SDA
└──────────────────────────┘
```

## Custom Platform Template

### Generic Pinout
```
Function       Platform Pin    Notes
--------       ------------    -----
Power (3.3V)   [POWER_PIN]    Must be 3.3V ±10%
Ground         [GND_PIN]      Common ground
I2C SDA        [SDA_PIN]      Requires 4.7kΩ pullup
I2C SCL        [SCL_PIN]      Requires 4.7kΩ pullup
Interrupt      [INT_PIN]      Optional, for async operation
Reset          [RST_PIN]      Active low, critical for init
Status LED     [LED_PIN]      Optional, for visual feedback
```

## Pullup Resistors

### Required Pullups
All I2C implementations require pullup resistors:
- **SDA**: 4.7kΩ to 3.3V
- **SCL**: 4.7kΩ to 3.3V

### Breadboard Pullup Circuit
```
     3.3V
       │
    ┌──┴──┐
    │4.7kΩ│
    └──┬──┘
       │
    ●──┴─── SDA/SCL to sensor
    │
 Platform
```

## Troubleshooting Wiring

### Common Issues
1. **No I2C Response**
   - Check power (must be 3.3V, not 5V)
   - Verify SDA/SCL connections
   - Ensure pullup resistors present
   - Check ground connections

2. **Intermittent Communication**
   - Check wire connections for loose contacts
   - Verify pullup resistor values (4.7kΩ typical)
   - Check for electrical noise/interference

3. **Reset Problems**
   - Ensure reset pin is properly connected
   - Check platform GPIO permissions
   - Verify active-low operation (0V = reset)

### Testing Connections
```bash
# Test I2C bus (Linux platforms)
i2cdetect -y [bus_number]

# Should show device at address 0x49:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 40: -- -- -- -- -- -- -- -- -- 49 -- -- -- -- -- --
```
