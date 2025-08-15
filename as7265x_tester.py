#!/usr/bin/env python3
"""
Spectral Sensor Pre-Assembly Test GUI
Professional test application for AS7265x Spectral Triad sensors
Version 1.0.0 - Production Ready
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import time
from datetime import datetime
import json
import os

# Try to import smbus2 - if not available, we'll use command line
try:
    import smbus2
    HAVE_SMBUS = True
except ImportError:
    HAVE_SMBUS = False
    print("Warning: smbus2 not available, using command line I2C")

# Constants
I2C_BUS = 3
AS7263_ADDR = 0x49
RESET_PIN = 5

# Application version
APP_VERSION = "1.0.0"
APP_DATE = "2024-12-19"

# Virtual register addresses - CORRECTED from C++ header
AS7263_REG_DEVICE_TYPE = 0x00      # Returns 0x40
AS7263_REG_HW_VERSION = 0x01       # Returns 0x41
AS7265X_DEVICE_TEMP = 0x06
AS7265X_DEV_SELECT_CONTROL = 0x4F

# I2C slave control registers
I2C_AS72XX_SLAVE_STATUS_REG = 0x00
I2C_AS72XX_SLAVE_WRITE_REG = 0x01
I2C_AS72XX_SLAVE_READ_REG = 0x02
I2C_AS72XX_SLAVE_TX_VALID = 0x02
I2C_AS72XX_SLAVE_RX_VALID = 0x01

# Device IDs
AS72651_NIR = 0x00
AS72652_VISIBLE = 0x01
AS72653_UV = 0x02

class SpectralTestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Spectral Sensor Pre-Assembly Test")
        self.root.geometry("800x650")
        self.root.configure(bg='#f0f0f0')
        
        self.testing = False
        self.test_results = []
        self.bus = None
        
        self.create_widgets()
        self.init_i2c()
        self.update_status()
        
    def init_i2c(self):
        """Initialize I2C bus"""
        try:
            if HAVE_SMBUS:
                self.bus = smbus2.SMBus(I2C_BUS)
                self.log_message("I2C bus initialized with smbus2", 'SUCCESS')
            else:
                self.log_message("Using command-line I2C tools", 'WARNING')
        except Exception as e:
            self.log_message("I2C initialization failed: " + str(e), 'ERROR')
            
    def run_command(self, command, timeout=5):
        """Run shell command"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, 
                                  text=True, timeout=timeout)
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "", "Command timeout"
        except Exception as e:
            return False, "", str(e)
            
    def hardware_reset(self):
        """Hardware reset using exact GPIO method"""
        self.log_message("Performing hardware reset...")
        
        # Reset low
        success, _, stderr = self.run_command("sudo raspi-gpio set " + str(RESET_PIN) + " op dl")
        if not success:
            self.log_message("Failed to set reset low: " + stderr, 'ERROR')
            return False
            
        time.sleep(1)  # 1 second like your shell script
        
        # Reset high  
        success, _, stderr = self.run_command("sudo raspi-gpio set " + str(RESET_PIN) + " op dh")
        if not success:
            self.log_message("Failed to set reset high: " + stderr, 'ERROR')
            return False
            
        time.sleep(2)  # Let sensor boot
        self.log_message("Hardware reset complete", 'SUCCESS')
        return True
        
    def read_direct_register(self, reg):
        """Read I2C register directly (not virtual)"""
        if HAVE_SMBUS and self.bus:
            try:
                return self.bus.read_byte_data(AS7263_ADDR, reg)
            except:
                return None
        else:
            # Fallback to command line
            cmd = "i2cget -y " + str(I2C_BUS) + " 0x" + format(AS7263_ADDR, '02X') + " 0x" + format(reg, '02X')
            success, stdout, _ = self.run_command(cmd)
            if success and stdout:
                try:
                    return int(stdout, 16)
                except:
                    return None
            return None
            
    def write_direct_register(self, reg, value):
        """Write I2C register directly (not virtual)"""
        if HAVE_SMBUS and self.bus:
            try:
                self.bus.write_byte_data(AS7263_ADDR, reg, value)
                return True
            except:
                return False
        else:
            # Fallback to command line
            cmd = "i2cset -y " + str(I2C_BUS) + " 0x" + format(AS7263_ADDR, '02X') + " 0x" + format(reg, '02X') + " 0x" + format(value, '02X')
            success, _, _ = self.run_command(cmd)
            return success
            
    def read_virtual_register(self, virtual_reg):
        """Read virtual register with proper timeout handling"""
        try:
            # Wait for TX buffer ready
            for _ in range(50):  # 5 second timeout
                status = self.read_direct_register(I2C_AS72XX_SLAVE_STATUS_REG)
                if status is not None and (status & I2C_AS72XX_SLAVE_TX_VALID) == 0:
                    break
                time.sleep(0.1)
            else:
                return None
                
            # Send virtual register address
            if not self.write_direct_register(I2C_AS72XX_SLAVE_WRITE_REG, virtual_reg):
                return None
                
            # Wait for RX data ready
            for _ in range(50):  # 5 second timeout
                status = self.read_direct_register(I2C_AS72XX_SLAVE_STATUS_REG)
                if status is not None and (status & I2C_AS72XX_SLAVE_RX_VALID) != 0:
                    break
                time.sleep(0.1)
            else:
                return None
                
            # Read the data
            data = self.read_direct_register(I2C_AS72XX_SLAVE_READ_REG)
            return data
            
        except Exception as e:
            self.log_message("Virtual register read error: " + str(e), 'ERROR')
            return None
            
    def write_virtual_register(self, virtual_reg, data):
        """Write virtual register with proper timeout handling"""
        try:
            # Wait for TX buffer ready
            for _ in range(50):
                status = self.read_direct_register(I2C_AS72XX_SLAVE_STATUS_REG)
                if status is not None and (status & I2C_AS72XX_SLAVE_TX_VALID) == 0:
                    break
                time.sleep(0.1)
            else:
                return False
                
            # Send virtual register address with write bit
            if not self.write_direct_register(I2C_AS72XX_SLAVE_WRITE_REG, virtual_reg | 0x80):
                return False
                
            # Wait for TX buffer ready again
            for _ in range(50):
                status = self.read_direct_register(I2C_AS72XX_SLAVE_STATUS_REG)
                if status is not None and (status & I2C_AS72XX_SLAVE_TX_VALID) == 0:
                    break
                time.sleep(0.1)
            else:
                return False
                
            # Send the data
            return self.write_direct_register(I2C_AS72XX_SLAVE_WRITE_REG, data)
            
        except Exception as e:
            self.log_message("Virtual register write error: " + str(e), 'ERROR')
            return False

    def create_widgets(self):
        """Create GUI widgets"""
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x', padx=10, pady=(10,5))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="Spectral Sensor Pre-Assembly Test", 
                              font=('Arial', 18, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        # Version label
        version_label = tk.Label(title_frame, text="Version " + APP_VERSION + " (" + APP_DATE + ")", 
                               font=('Arial', 10), fg='#bdc3c7', bg='#2c3e50')
        version_label.pack(side='bottom', pady=(0,5))
        
        # Main content
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left panel
        left_panel = tk.LabelFrame(main_frame, text="Test Controls", font=('Arial', 12, 'bold'),
                                  bg='#f0f0f0', pady=10)
        left_panel.pack(side='left', fill='y', padx=(0,5))
        
        # Connection status
        self.status_frame = tk.Frame(left_panel, bg='#f0f0f0')
        self.status_frame.pack(fill='x', pady=10)
        
        tk.Label(self.status_frame, text="Connection Status:", font=('Arial', 10, 'bold'),
                bg='#f0f0f0').pack()
        
        self.status_label = tk.Label(self.status_frame, text="Checking...", 
                                   font=('Arial', 10), bg='#f0f0f0', fg='orange')
        self.status_label.pack()
        
        # Test button
        self.test_button = tk.Button(left_panel, text="START TEST", 
                                   command=self.start_test, font=('Arial', 14, 'bold'),
                                   bg='#27ae60', fg='white', height=2, width=15)
        self.test_button.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(left_panel, mode='indeterminate')
        self.progress.pack(fill='x', pady=10)
        
        # Test result indicator
        result_frame = tk.Frame(left_panel, bg='#f0f0f0')
        result_frame.pack(fill='x', pady=10)
        
        tk.Label(result_frame, text="Test Result:", font=('Arial', 10, 'bold'),
                bg='#f0f0f0').pack()
        
        self.result_label = tk.Label(result_frame, text="Ready to test", 
                                   font=('Arial', 12, 'bold'), bg='#f0f0f0', fg='gray')
        self.result_label.pack()
        
        # Actions
        actions_frame = tk.LabelFrame(left_panel, text="Actions", bg='#f0f0f0')
        actions_frame.pack(fill='x', pady=10)
        
        tk.Button(actions_frame, text="Reset Sensor", command=self.reset_sensor,
                 bg='#f39c12', fg='white').pack(fill='x', pady=2)
        
        tk.Button(actions_frame, text="Clear Log", command=self.clear_log,
                 bg='#e74c3c', fg='white').pack(fill='x', pady=2)
        
        tk.Button(actions_frame, text="Save Log", command=self.save_log,
                 bg='#3498db', fg='white').pack(fill='x', pady=2)
        
        # Quick reference at bottom
        fault_frame = tk.LabelFrame(left_panel, text="Quick Reference", bg='#f0f0f0', fg='#666')
        fault_frame.pack(fill='x', pady=(10,0))
        
        fault_labels = [
            ("✓ PASS", "Ready for assembly", 'green'),
            ("✗ FAIL", "Sensor defective", 'red'),
            ("i2c ERR", "Check connections", 'blue')
        ]
        
        for icon, desc, color in fault_labels:
            row = tk.Frame(fault_frame, bg='#f0f0f0')
            row.pack(fill='x', padx=5, pady=2)
            
            tk.Label(row, text=icon, font=('Arial', 10), bg='#f0f0f0', 
                    fg=color, width=12, anchor='w').pack(side='left')
            tk.Label(row, text=desc, font=('Arial', 9), bg='#f0f0f0', 
                    fg='#666', anchor='w').pack(side='left', fill='x', expand=True)
        
        # Right panel
        right_panel = tk.LabelFrame(main_frame, text="Test Results", font=('Arial', 12, 'bold'),
                                   bg='#f0f0f0')
        right_panel.pack(side='right', fill='both', expand=True, padx=(5,0))
        
        # Results display
        self.results_text = scrolledtext.ScrolledText(right_panel, height=20, width=50,
                                                     font=('Courier', 10))
        self.results_text.pack(fill='both', expand=True, pady=10)
        
        # Status bar
        status_bar = tk.Frame(self.root, bg='#34495e', height=30)
        status_bar.pack(fill='x', padx=10, pady=(0,10))
        status_bar.pack_propagate(False)
        
        self.status_bar_label = tk.Label(status_bar, text="Ready - v" + APP_VERSION, fg='white', bg='#34495e')
        self.status_bar_label.pack(side='left', padx=10, pady=5)
        
        self.test_counter_label = tk.Label(status_bar, text="Tests: 0", fg='white', bg='#34495e')
        self.test_counter_label.pack(side='right', padx=10, pady=5)
        
    def log_message(self, message, level='INFO'):
        """Add message to results"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.results_text.insert(tk.END, "[" + timestamp + "] " + message + "\n")
        self.results_text.see(tk.END)
        self.root.update()
        
    def update_status(self):
        """Update connection status"""
        def check():
            # Simple test - try to read any register
            data = self.read_direct_register(I2C_AS72XX_SLAVE_STATUS_REG)
            if data is not None:
                # Try virtual register read
                hw_ver = self.read_virtual_register(AS7263_REG_HW_VERSION)
                if hw_ver == 0x41:
                    self.status_label.config(text="✓ Sensor Connected", fg='green')
                elif hw_ver is not None:
                    self.status_label.config(text="⚠ Wrong HW: 0x" + format(hw_ver, '02X'), fg='orange')
                else:
                    self.status_label.config(text="⚠ Virtual Reg Issue", fg='orange')
            else:
                self.status_label.config(text="✗ No I2C Response", fg='red')
                
        threading.Thread(target=check, daemon=True).start()
        self.root.after(5000, self.update_status)
        
    def reset_sensor(self):
        """Reset sensor"""
        self.status_bar_label.config(text="Resetting...")
        if self.hardware_reset():
            self.status_bar_label.config(text="Reset complete - v" + APP_VERSION)
        else:
            self.status_bar_label.config(text="Reset failed - v" + APP_VERSION)
            
    def clear_log(self):
        """Clear log"""
        if messagebox.askyesno("Clear Log", "Clear the test log display?"):
            self.results_text.delete(1.0, tk.END)
            self.result_label.config(text="Ready to test", fg='gray')
            self.log_message("Test log cleared")
            
    def save_log(self):
        """Save current log to file"""
        try:
            # Create logs directory
            logs_dir = os.path.expanduser("~/spectral_test_logs")
            os.makedirs(logs_dir, exist_ok=True)
            
            # Save current log content
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = os.path.join(logs_dir, "spectral_test_log_" + timestamp + ".txt")
            
            log_content = self.results_text.get(1.0, tk.END)
            with open(log_filename, 'w') as f:
                f.write("Spectral Sensor Pre-Assembly Test Log\n")
                f.write("Application Version: " + APP_VERSION + " (" + APP_DATE + ")\n")
                f.write("Generated: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
                f.write("=" * 60 + "\n\n")
                f.write(log_content)
                
            self.log_message("Log saved to: " + log_filename, 'SUCCESS')
            messagebox.showinfo("Log Saved", "Test log saved to:\n" + log_filename)
            
        except Exception as e:
            self.log_message("Failed to save log: " + str(e), 'ERROR')
            messagebox.showerror("Save Error", "Failed to save log:\n" + str(e))
        
    def test_basic_communication(self):
        """Test basic I2C communication"""
        self.log_message("Testing I2C communication...")
        
        # Test 1: Read status register
        status = self.read_direct_register(I2C_AS72XX_SLAVE_STATUS_REG)
        if status is not None:
            self.log_message("✓ Status register: 0x" + format(status, '02X'), 'SUCCESS')
        else:
            self.log_message("✗ Cannot read status register", 'ERROR')
            self.log_message("FAULT: Check 6-wire harness connections", 'ERROR')
            self.log_message("FAULT: Verify 3.3V power supply", 'ERROR')
            return False
            
        # Test 2: Read device type
        device_type = self.read_virtual_register(AS7263_REG_DEVICE_TYPE)
        if device_type == 0x40:
            self.log_message("✓ Device type: 0x" + format(device_type, '02X'), 'SUCCESS')
        elif device_type is not None:
            self.log_message("⚠ Unexpected device type: 0x" + format(device_type, '02X'), 'WARNING')
        else:
            self.log_message("✗ Cannot read device type", 'ERROR')
            return False
            
        # Test 3: Read hardware version
        hw_ver = self.read_virtual_register(AS7263_REG_HW_VERSION)
        if hw_ver == 0x41:
            self.log_message("✓ Hardware version: 0x" + format(hw_ver, '02X'), 'SUCCESS')
            return True
        elif hw_ver is not None:
            self.log_message("✗ Wrong hardware version: 0x" + format(hw_ver, '02X') + " (expected 0x41)", 'ERROR')
            self.log_message("FAULT: Incorrect sensor type or firmware", 'ERROR')
            return False
        else:
            self.log_message("✗ Cannot read hardware version", 'ERROR')
            self.log_message("FAULT: Virtual register communication failed", 'ERROR')
            return False
            
    def test_device_selection(self):
        """Test device selection functionality"""
        devices = [(AS72651_NIR, "NIR"), (AS72652_VISIBLE, "Visible"), (AS72653_UV, "UV")]
        results = []
        
        self.log_message("Testing device selection...")
        
        for device_id, name in devices:
            if self.write_virtual_register(AS7265X_DEV_SELECT_CONTROL, device_id):
                time.sleep(0.2)  # Let device switch settle
                
                # Try to read temperature register
                temp = self.read_virtual_register(AS7265X_DEVICE_TEMP)
                
                if temp is not None and 0 <= temp <= 85:
                    self.log_message("✓ " + name + " sensor OK (temp: " + str(temp) + "°C)", 'SUCCESS')
                    results.append(True)
                elif temp is not None:
                    self.log_message("⚠ " + name + " sensor temp: " + str(temp) + "°C (unusual)", 'WARNING')
                    results.append(True)  # Still responding
                else:
                    self.log_message("✗ " + name + " sensor not responding", 'ERROR')
                    results.append(False)
            else:
                self.log_message("✗ Cannot select " + name + " sensor", 'ERROR')
                results.append(False)
                
        if not all(results):
            self.log_message("FAULT: One or more spectral devices failed", 'ERROR')
            
        return all(results)
        
    def run_full_test(self):
        """Run complete test sequence"""
        test_start = datetime.now()
        self.log_message("=" * 60)
        self.log_message("SPECTRAL SENSOR PRE-ASSEMBLY TEST")
        self.log_message("=" * 60)
        
        self.result_label.config(text="Testing...", fg='orange')
        
        test_result = {
            'timestamp': test_start.isoformat(),
            'app_version': APP_VERSION,
            'app_date': APP_DATE,
            'tests': {},
            'overall_result': 'UNKNOWN'
        }
        
        # Test sequence
        tests = [
            ("Hardware Reset", lambda: self.hardware_reset()),
            ("I2C Communication", self.test_basic_communication),
            ("Device Selection", self.test_device_selection)
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            self.log_message("--- " + test_name + " Test ---")
            self.status_bar_label.config(text="Testing: " + test_name)
            
            try:
                passed = test_func()
                test_result['tests'][test_name] = {'passed': passed}
                    
                if not passed:
                    all_passed = False
                    break  # Stop on first failure
                    
            except Exception as e:
                self.log_message("✗ " + test_name + " test crashed: " + str(e), 'ERROR')
                test_result['tests'][test_name] = {'passed': False, 'error': str(e)}
                all_passed = False
                break
                
        # Final result
        test_result['overall_result'] = 'PASS' if all_passed else 'FAIL'
        test_result['duration'] = (datetime.now() - test_start).total_seconds()
        
        self.log_message("\n" + "=" * 60)
        if all_passed:
            self.log_message("*** SENSOR TEST PASSED - READY FOR ASSEMBLY ***", 'SUCCESS')
            self.result_label.config(text="✓ PASS", fg='green', font=('Arial', 14, 'bold'))
            self.test_button.config(bg='#27ae60')
        else:
            self.log_message("*** SENSOR TEST FAILED - DO NOT ASSEMBLE ***", 'ERROR')
            self.log_message("RECOMMENDATION: Mark sensor as defective", 'ERROR')
            self.result_label.config(text="✗ FAIL", fg='red', font=('Arial', 14, 'bold'))
            self.test_button.config(bg='#e74c3c')
            
        self.log_message("Test duration: " + str(round(test_result['duration'], 1)) + " seconds")
        self.log_message("=" * 60)
        
        # Store result
        self.test_results.append(test_result)
        self.test_counter_label.config(text="Tests: " + str(len(self.test_results)))
        
        # Auto-save result
        self.auto_save_result(test_result)
        
        return all_passed
        
    def auto_save_result(self, test_result):
        """Automatically save test result"""
        try:
            # Create results directory
            results_dir = os.path.expanduser("~/spectral_test_results")
            os.makedirs(results_dir, exist_ok=True)
            
            # Save to daily results file
            date_str = datetime.now().strftime('%Y%m%d')
            results_file = os.path.join(results_dir, "spectral_results_" + date_str + ".json")
            
            # Read existing results or create new list
            if os.path.exists(results_file):
                with open(results_file, 'r') as f:
                    daily_results = json.load(f)
            else:
                daily_results = []
                
            # Add new result
            daily_results.append(test_result)
            
            # Write back to file
            with open(results_file, 'w') as f:
                json.dump(daily_results, f, indent=2, default=str)
                
            self.log_message(f"Result auto-saved to daily log", 'SUCCESS')
            
        except Exception as e:
            self.log_message("Auto-save failed: " + str(e), 'ERROR')
        
    def start_test(self):
        """Start test in thread"""
        if self.testing:
            return
            
        self.testing = True
        self.test_button.config(text="TESTING...", state='disabled', bg='#f39c12')
        self.progress.start()
        
        def test_thread():
            try:
                result = self.run_full_test()
                if result:
                    self.test_button.config(bg='#27ae60')
                else:
                    self.test_button.config(bg='#e74c3c')
            finally:
                self.testing = False
                self.test_button.config(text="START TEST", state='normal')
                self.progress.stop()
                self.status_bar_label.config(text="Test complete - v" + APP_VERSION)
                
        threading.Thread(target=test_thread, daemon=True).start()
        
    def cleanup(self):
        """Cleanup"""
        if self.bus:
            try:
                self.bus.close()
            except:
                pass

def main():
    root = tk.Tk()
    app = SpectralTestGUI(root)
    
    def on_closing():
        app.cleanup()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()