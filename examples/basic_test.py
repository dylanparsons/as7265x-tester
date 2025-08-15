#!/usr/bin/env python3
"""
Basic AS7265x Test Example
Simple command-line test without GUI
"""

import sys
import os
import json
import subprocess
import time

# Add parent directory to path to import platform manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from platform_manager import PlatformManager

class BasicTester:
    def __init__(self):
        self.pm = PlatformManager()
        
    def list_platforms(self):
        """List available platforms"""
        platforms = self.pm.get_platforms()
        print("Available platforms:")
        for i, (pid, name) in enumerate(platforms):
            print(f"  {i}: {name} ({pid})")
        return platforms
        
    def select_platform(self, platform_id):
        """Select platform by ID"""
        if self.pm.select_platform(platform_id):
            config = self.pm.current_platform
            print(f"Selected: {config['name']}")
            print(f"I2C Bus: {config['i2c_bus']}")
            print(f"Reset Pin: {config['pins']['reset']}")
            return True
        else:
            print(f"Failed to load platform: {platform_id}")
            return False
            
    def run_command(self, cmd_name, **kwargs):
        """Execute platform command"""
        cmd = self.pm.get_command(cmd_name, **kwargs)
        if not cmd:
            print(f"Command '{cmd_name}' not available")
            return False, "", ""
            
        print(f"Executing: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, 
                                  text=True, timeout=10)
            success = result.returncode == 0
            print(f"Result: {'SUCCESS' if success else 'FAILED'}")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
            if result.stderr:
                print(f"Error: {result.stderr.strip()}")
            return success, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            print("Command timeout")
            return False, "", "timeout"
        except Exception as e:
            print(f"Exception: {e}")
            return False, "", str(e)
            
    def test_i2c_scan(self):
        """Test I2C bus scanning"""
        print("\n=== I2C Bus Scan ===")
        success, stdout, stderr = self.run_command('i2c_scan')
        
        if success and "49" in stdout:
            print("✓ AS7265x sensor detected at address 0x49")
            return True
        else:
            print("✗ AS7265x sensor NOT detected")
            return False
            
    def test_gpio_control(self):
        """Test GPIO control"""
        print("\n=== GPIO Control Test ===")
        
        if not self.pm.current_platform:
            print("No platform selected")
            return False
            
        led_pin = self.pm.current_platform['pins']['status_led']
        print(f"Testing status LED on pin {led_pin}")
        
        # Flash LED 3 times
        for i in range(3):
            print(f"Flash {i+1}/3")
            self.run_command('gpio_set_high', pin=led_pin)
            time.sleep(0.2)
            self.run_command('gpio_set_low', pin=led_pin)
            time.sleep(0.2)
            
        print("✓ GPIO test complete")
        return True
        
    def test_sensor_reset(self):
        """Test sensor reset sequence"""
        print("\n=== Sensor Reset Test ===")
        
        if not self.pm.current_platform:
            print("No platform selected")
            return False
            
        reset_pin = self.pm.current_platform['pins']['reset']
        print(f"Resetting sensor using pin {reset_pin}")
        
        # Reset sequence: low for 500ms, then high
        print("Pulling reset low...")
        self.run_command('gpio_set_low', pin=reset_pin)
        time.sleep(0.5)
        
        print("Releasing reset...")
        self.run_command('gpio_set_high', pin=reset_pin)
        time.sleep(0.5)
        
        print("✓ Reset sequence complete")
        return True
        
    def run_basic_test(self, platform_id):
        """Run basic sensor test sequence"""
        print(f"\n{'='*50}")
        print(f"BASIC AS7265x TEST - Platform: {platform_id}")
        print(f"{'='*50}")
        
        # Select platform
        if not self.select_platform(platform_id):
            return False
            
        # Run tests
        tests = [
            ("I2C Communication", self.test_i2c_scan),
            ("GPIO Control", self.test_gpio_control),
            ("Sensor Reset", self.test_sensor_reset),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            result = test_func()
            results.append(result)
            
        # Summary
        print(f"\n{'='*50}")
        passed = sum(results)
        total = len(results)
        print(f"TEST SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            print("🟢 ALL TESTS PASSED")
            return True
        else:
            print("🔴 SOME TESTS FAILED")
            return False

def main():
    """Main function"""
    tester = BasicTester()
    
    # List available platforms
    platforms = tester.list_platforms()
    
    if not platforms:
        print("No platform configurations found!")
        print("Make sure config files exist in configs/ directory")
        return 1
        
    # Interactive platform selection
    print("\nSelect platform:")
    try:
        choice = int(input("Enter platform number: "))
        if 0 <= choice < len(platforms):
            platform_id, platform_name = platforms[choice]
            print(f"Testing with {platform_name}")
            
            # Run test
            success = tester.run_basic_test(platform_id)
            return 0 if success else 1
        else:
            print("Invalid selection")
            return 1
    except (ValueError, KeyboardInterrupt):
        print("Test cancelled")
        return 1

if __name__ == "__main__":
    exit(main())