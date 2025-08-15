#!/usr/bin/env python3
"""
AS7265x Spectral Sensor Test GUI v1.1.0
Multi-platform support with LED feedback

Author: Dylan Parsons
Created: August 2025
Status: Open Source (MIT License)

Background:
Expanded to support multiple hardware platforms, JSON platform configs, 
GPIO LED status patterns, and streamlined UI with integrated setup assistant.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import time
import json
import os
import glob
from datetime import datetime

# Application version
APP_VERSION = "1.1.0"
APP_DATE = "2025-08-14"

class PlatformManager:
    def __init__(self):
        self.configs = {}
        self.current_platform = None
        self.load_platform_configs()
        
    def load_platform_configs(self):
        """Load all platform configuration files"""
        config_dir = os.path.join(os.path.dirname(__file__), 'configs')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            return
            
        for config_file in glob.glob(os.path.join(config_dir, '*.json')):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    platform_id = config.get('platform', os.path.basename(config_file)[:-5])
                    self.configs[platform_id] = config
            except Exception as e:
                print("Error loading config " + config_file + ": " + str(e))
                
    def get_platforms(self):
        """Get list of available platforms"""
        return [(pid, config['name']) for pid, config in self.configs.items()]
        
    def select_platform(self, platform_id):
        """Select and apply platform configuration"""
        if platform_id in self.configs:
            self.current_platform = self.configs[platform_id]
            return True
        return False
        
    def get_command(self, cmd_name, **kwargs):
        """Get platform-specific command with parameter substitution"""
        if not self.current_platform:
            return None
            
        cmd_template = self.current_platform.get('commands', {}).get(cmd_name)
        if not cmd_template:
            return None
            
        # Add platform-specific parameters
        params = {
            'bus': self.current_platform.get('i2c_bus', 1),
            'addr': 0x49,  # AS7265x address
            **kwargs
        }
        
        # Add pin numbers
        pins = self.current_platform.get('pins', {})
        params.update(pins)
        
        try:
            return cmd_template.format(**params)
        except KeyError as e:
            print("Missing parameter for command template: " + str(e))
            return None

class SpectralEvalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AS7265x Spectral Sensor Tester")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        self.platform_manager = PlatformManager()
        self.testing = False
        self.test_results = []
        
        self.create_widgets()
        self.populate_platform_selector()
        
    def create_widgets(self):
        """Create GUI widgets"""
        # Title frame
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=100)
        title_frame.pack(fill='x', padx=10, pady=(10,5))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="AS7265x Spectral Sensor Evaluation Tool", 
                              font=('Arial', 18, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        version_label = tk.Label(title_frame, text="Version " + APP_VERSION + " - Multi-Platform Support", 
                               font=('Arial', 10), fg='#bdc3c7', bg='#2c3e50')
        version_label.pack(side='bottom', pady=(0,5))
        
        # Main content
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left panel
        left_panel = tk.LabelFrame(main_frame, text="Configuration & Control", 
                                  font=('Arial', 12, 'bold'), bg='#f0f0f0', pady=10)
        left_panel.pack(side='left', fill='y', padx=(0,5))
        
        # Platform selection with integrated setup
        platform_frame = tk.LabelFrame(left_panel, text="Platform", bg='#f0f0f0')
        platform_frame.pack(fill='x', pady=(0,10))
        
        # Platform dropdown with info button
        platform_select_frame = tk.Frame(platform_frame, bg='#f0f0f0')
        platform_select_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(platform_select_frame, text="Hardware:", bg='#f0f0f0').pack(side='left')
        self.platform_var = tk.StringVar()
        self.platform_combo = ttk.Combobox(platform_select_frame, textvariable=self.platform_var, 
                                          state='readonly', width=20)
        self.platform_combo.pack(side='left', padx=(5,0), fill='x', expand=True)
        self.platform_combo.bind('<<ComboboxSelected>>', self.on_platform_changed)
        
        # Setup info button (replaces redundant "Platform Setup" button)
        setup_btn = tk.Button(platform_select_frame, text="ⓘ", width=3, 
                             command=self.show_platform_setup, bg='#95a5a6', fg='white')
        setup_btn.pack(side='right', padx=(5,0))
        
        # Compact platform info (replaces large text box)
        self.platform_status = tk.Label(platform_frame, text="Select hardware platform", 
                                       font=('Arial', 9), bg='#f0f0f0', fg='#666', 
                                       wraplength=200, justify='left')
        self.platform_status.pack(fill='x', padx=5, pady=(0,5))
        
        # Connection status
        status_frame = tk.Frame(left_panel, bg='#f0f0f0')
        status_frame.pack(fill='x', pady=10)
        
        tk.Label(status_frame, text="Connection Status:", font=('Arial', 10, 'bold'),
                bg='#f0f0f0').pack()
        
        self.status_label = tk.Label(status_frame, text="Select Platform First", 
                                   font=('Arial', 10), bg='#f0f0f0', fg='orange')
        self.status_label.pack()
        
        # Test controls
        test_frame = tk.LabelFrame(left_panel, text="Test Control", bg='#f0f0f0')
        test_frame.pack(fill='x', pady=10)
        
        self.test_button = tk.Button(test_frame, text="START TEST", 
                                   command=self.start_test, font=('Arial', 14, 'bold'),
                                   bg='#27ae60', fg='white', height=2, width=15)
        self.test_button.pack(pady=10)
        self.test_button.config(state='disabled')
        
        self.progress = ttk.Progressbar(test_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=5)
        
        # Test result
        result_frame = tk.Frame(test_frame, bg='#f0f0f0')
        result_frame.pack(fill='x', pady=5)
        
        tk.Label(result_frame, text="Test Result:", font=('Arial', 10, 'bold'),
                bg='#f0f0f0').pack()
        
        self.result_label = tk.Label(result_frame, text="Ready", 
                                   font=('Arial', 12, 'bold'), bg='#f0f0f0', fg='gray')
        self.result_label.pack()
        
        # Streamlined actions (removed redundant buttons)
        actions_frame = tk.LabelFrame(left_panel, text="Actions", bg='#f0f0f0')
        actions_frame.pack(fill='x', pady=10)
        
        tk.Button(actions_frame, text="Test Connection", command=self.test_connection,
                 bg='#3498db', fg='white').pack(fill='x', pady=2)
        
        tk.Button(actions_frame, text="Reset Sensor", command=self.reset_sensor,
                 bg='#f39c12', fg='white').pack(fill='x', pady=2)
        
        tk.Button(actions_frame, text="Save Results", command=self.save_results,
                 bg='#2ecc71', fg='white').pack(fill='x', pady=2)
        
        # Right panel - Results
        right_panel = tk.LabelFrame(main_frame, text="Test Results & Log", 
                                   font=('Arial', 12, 'bold'), bg='#f0f0f0')
        right_panel.pack(side='right', fill='both', expand=True, padx=(5,0))
        
        self.results_text = scrolledtext.ScrolledText(right_panel, height=25, width=60,
                                                     font=('Courier', 9))
        self.results_text.pack(fill='both', expand=True, pady=10)
        
        # Status bar
        status_bar = tk.Frame(self.root, bg='#34495e', height=30)
        status_bar.pack(fill='x', padx=10, pady=(0,10))
        status_bar.pack_propagate(False)
        
        self.status_bar_label = tk.Label(status_bar, text="Ready - v" + APP_VERSION, 
                                        fg='white', bg='#34495e')
        self.status_bar_label.pack(side='left', padx=10, pady=5)
        
        self.test_counter_label = tk.Label(status_bar, text="Tests: 0", fg='white', bg='#34495e')
        self.test_counter_label.pack(side='right', padx=10, pady=5)
        
    def populate_platform_selector(self):
        """Populate platform selection dropdown"""
        platforms = self.platform_manager.get_platforms()
        if platforms:
            platform_names = [name for pid, name in platforms]
            self.platform_combo['values'] = platform_names
            self.platform_combo.current(0)  # Select first platform by default
            self.on_platform_changed()
        else:
            self.log_message("No platform configurations found in configs/ directory", 'ERROR')
            
    def on_platform_changed(self, event=None):
        """Handle platform selection change"""
        selection = self.platform_combo.current()
        if selection >= 0:
            platforms = self.platform_manager.get_platforms()
            platform_id, platform_name = platforms[selection]
            
            if self.platform_manager.select_platform(platform_id):
                self.log_message("Selected platform: " + platform_name)
                self.update_platform_info()
                self.test_button.config(state='normal')
                self.update_connection_status()
            else:
                self.log_message("Failed to load platform: " + platform_name, 'ERROR')
                
    def update_platform_info(self):
        """Update platform information display"""
        if not self.platform_manager.current_platform:
            return
            
        config = self.platform_manager.current_platform
        # Compact status message instead of large text box
        bus = config.get('i2c_bus', 'N/A')
        reset_pin = config.get('pins', {}).get('reset', 'N/A')
        status_text = "I2C: " + str(bus) + " | Reset: " + str(reset_pin)
        
        self.platform_status.config(text=status_text, fg='#2c3e50')
        
    def run_platform_command(self, cmd_name, **kwargs):
        """Execute platform-specific command"""
        cmd = self.platform_manager.get_command(cmd_name, **kwargs)
        if not cmd:
            return False, "", "Command not available for platform"
            
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, 
                                  text=True, timeout=10)
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "", "Command timeout"
        except Exception as e:
            return False, "", str(e)
            
    def test_connection(self):
        """Test platform connection and I2C communication"""
        if not self.platform_manager.current_platform:
            messagebox.showerror("Error", "No platform selected")
            return
            
        self.log_message("Testing platform connection...")
        
        # Test I2C scan
        success, stdout, stderr = self.run_platform_command('i2c_scan')
        if success and "49" in stdout:
            self.log_message("✓ AS7265x sensor detected at 0x49", 'SUCCESS')
            self.status_label.config(text="✓ Sensor Connected", fg='green')
        else:
            self.log_message("✗ Sensor not detected on I2C bus", 'ERROR')
            self.status_label.config(text="✗ No Sensor", fg='red')
            
    def reset_sensor(self):
        """Reset sensor using platform-specific GPIO command"""
        if not self.platform_manager.current_platform:
            return
            
        self.log_message("Resetting sensor...")
        
        # Reset sequence
        success1, _, _ = self.run_platform_command('gpio_set_low', pin=self.platform_manager.current_platform['pins']['reset'])
        time.sleep(0.5)
        success2, _, _ = self.run_platform_command('gpio_set_high', pin=self.platform_manager.current_platform['pins']['reset'])
        
        if success1 and success2:
            self.log_message("✓ Sensor reset complete", 'SUCCESS')
        else:
            self.log_message("⚠ GPIO reset failed (check permissions)", 'WARNING')
            
    def flash_status_led(self, times=3):
        """Flash status LED using platform commands"""
        if not self.platform_manager.current_platform:
            return
            
        led_pin = self.platform_manager.current_platform['pins']['status_led']
        for _ in range(times):
            self.run_platform_command('gpio_set_high', pin=led_pin)
            time.sleep(0.1)
            self.run_platform_command('gpio_set_low', pin=led_pin)
            time.sleep(0.1)
            
    def show_platform_setup(self):
        """Show platform setup instructions"""
        if not self.platform_manager.current_platform:
            messagebox.showwarning("Warning", "No platform selected")
            return
            
        config = self.platform_manager.current_platform
        setup_window = tk.Toplevel(self.root)
        setup_window.title("Platform Setup - " + config['name'])
        setup_window.geometry("600x400")
        
        setup_text = scrolledtext.ScrolledText(setup_window, wrap=tk.WORD)
        setup_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        content = "Setup Instructions for " + config['name'] + "\n"
        content += "=" * 50 + "\n\n"
        
        for step in config.get('setup_instructions', []):
            content += "• " + step + "\n"
            
        content += "\nPin Configuration:\n"
        for pin_name, pin_num in config.get('pins', {}).items():
            content += "  " + pin_name + ": " + str(pin_num) + "\n"
            
        content += "\nDependencies:\n"
        deps = config.get('dependencies', {})
        if 'python_packages' in deps:
            content += "  Python: " + ", ".join(deps['python_packages']) + "\n"
        if 'system_packages' in deps:
            content += "  System: " + ", ".join(deps['system_packages']) + "\n"
            
        setup_text.insert(1.0, content)
        setup_text.config(state='disabled')
        
    def update_connection_status(self):
        """Update connection status in background"""
        def check():
            self.test_connection()
            
        threading.Thread(target=check, daemon=True).start()
        
    def log_message(self, message, level='INFO'):
        """Add message to results display"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.results_text.insert(tk.END, "[" + timestamp + "] " + message + "\n")
        self.results_text.see(tk.END)
        self.root.update()
        
    def start_test(self):
        """Start sensor test sequence"""
        if not self.platform_manager.current_platform:
            messagebox.showerror("Error", "No platform selected")
            return
            
        if self.testing:
            return
            
        self.testing = True
        self.test_button.config(text="TESTING...", state='disabled', bg='#f39c12')
        self.progress.start()
        
        def test_thread():
            try:
                self.run_sensor_test()
            finally:
                self.testing = False
                self.test_button.config(text="START TEST", state='normal', bg='#27ae60')
                self.progress.stop()
                
        threading.Thread(target=test_thread, daemon=True).start()
        
    def run_sensor_test(self):
        """Run basic sensor test sequence"""
        self.log_message("=" * 60)
        self.log_message("STARTING AS7265x SENSOR TEST")
        platform_name = self.platform_manager.current_platform['name']
        self.log_message("Platform: " + platform_name)
        self.log_message("=" * 60)
        
        # Flash LED to indicate test start
        self.flash_status_led(3)
        
        # Basic I2C communication test
        success, stdout, stderr = self.run_platform_command('i2c_scan')
        if success and "49" in stdout:
            self.log_message("✓ I2C communication successful", 'SUCCESS')
            self.result_label.config(text="✓ PASS", fg='green')
            self.flash_status_led(5)  # Success pattern
        else:
            self.log_message("✗ I2C communication failed", 'ERROR')
            self.result_label.config(text="✗ FAIL", fg='red')
            self.flash_status_led(2)  # Failure pattern
            
        self.log_message("Test complete")
        
    def save_results(self):
        """Save test results to file"""
        if not self.test_results:
            messagebox.showwarning("Warning", "No test results to save")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        platform_name = self.platform_manager.current_platform['name'].replace(' ', '_')
        filename = "as7265x_test_" + platform_name + "_" + timestamp + ".json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            self.log_message("Results saved to: " + filename, 'SUCCESS')
            messagebox.showinfo("Saved", "Results saved to:\n" + filename)
        except Exception as e:
            self.log_message("Save failed: " + str(e), 'ERROR')

def main():
    root = tk.Tk()
    app = SpectralEvalGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()