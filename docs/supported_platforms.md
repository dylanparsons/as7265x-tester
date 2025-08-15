# Supported Platforms

This document lists all officially supported platforms for the AS7265x Spectral Sensor Tester.

## Current Platforms

### ✅ Raspberry Pi 4
- **Status**: Fully Supported
- **Communication**: Direct I2C + GPIO
- **Setup Difficulty**: Easy
- **Features**: Hardware reset, status LED, comprehensive logging
- **Best For**: Production testing, development, education

**Pros:**
- Native Linux I2C support
- Excellent GPIO control
- Large community
- Rich development environment

**Cons:**
- Requires Linux knowledge
- Higher power consumption
- More expensive than microcontrollers

### ✅ Arduino Leonardo
- **Status**: Beta Support
- **Communication**: Serial bridge
- **Setup Difficulty**: Medium
- **Features**: Basic I2C communication, limited GPIO
- **Best For**: Simple testing, embedded applications

**Pros:**
- Low cost
- Simple programming model
- Good for beginners
- Low power consumption

**Cons:**
- Limited processing power
- Requires custom firmware
- No native networking

### ✅ ESP32 DevKit
- **Status**: Beta Support
- **Communication**: WiFi TCP/UDP
- **Setup Difficulty**: Medium-Hard
- **Features**: Wireless testing, web interface potential
- **Best For**: Remote testing, IoT applications

**Pros:**
- Built-in WiFi/Bluetooth
- Low cost
- Good processing power
- OTA update capable

**Cons:**
- More complex networking setup
- WiFi reliability concerns
- Limited GPIO pins

### ✅ BeagleBone Black
- **Status**: Beta Support
- **Communication**: Direct I2C + sysfs GPIO
- **Setup Difficulty**: Hard
- **Features**: Linux-based, multiple I2C buses
- **Best For**: Industrial applications, advanced users

**Pros:**
- Full Linux environment
- Multiple I2C/SPI buses
- Real-time capabilities
- Industrial temperature range

**Cons:**
- Complex pin configuration
- Steep learning curve
- Higher cost
- Less community support

## Platform Comparison Matrix

| Feature | RPi 4 | Arduino | ESP32 | BeagleBone |
|---------|-------|---------|--------|------------|
| **Ease of Setup** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Cost** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **GPIO Control** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **I2C Support** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Networking** | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Community** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Documentation** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

## Recommended Platform Selection

### For Production Testing
**Raspberry Pi 4** - Most reliable, comprehensive features, excellent tooling

### For Cost-Sensitive Applications  
**ESP32 DevKit** - Low cost, wireless capabilities, good performance

### For Educational Use
**Arduino Leonardo** - Simple to understand, well-documented, beginner-friendly

### For Industrial Applications
**BeagleBone Black** - Robust, real-time capable, industrial temperature range

## Future Platform Support

### Planned
- **Raspberry Pi 5** - Next-generation Pi support
- **Arduino Uno R4** - Latest Arduino platform
- **STM32 Nucleo** - Professional ARM development
- **NVIDIA Jetson Nano** - AI/ML applications

### Under Consideration
- **Raspberry Pi Pico** - RP2040 microcontroller
- **NodeMCU ESP8266** - Lower-cost WiFi option
- **Teensy 4.0** - High-performance microcontroller
- **Rock Pi** - Alternative SBC option
