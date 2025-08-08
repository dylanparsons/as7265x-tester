#!/usr/bin/env python3
"""
Custom Platform Setup Helper
Interactive tool to create new platform configurations
"""

import json
import os

def get_user_input(prompt, default=None):
    """Get user input with optional default"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def get_pin_config():
    """Get pin configuration from user"""
    print("\n=== Pin Configuration ===")
    print("Enter pin numbers/names for your platform:")
    
    pins = {}
    pin_types = [
        ('reset', 'Reset pin (active low)'),
        ('status_led', 'Status LED pin'),
        ('sda', 'I2C SDA pin'),
        ('scl', 'I2C SCL pin'),
        ('interrupt', 'Interrupt pin (optional)')
    ]
    
    for pin_name, description in pin_types:
        while True:
            pin_value = get_user_input(f"{description}")
            if pin_value:
                # Try to convert to int, otherwise keep as string
                try:
                    pins[pin_name] = int(pin_value)
                except ValueError:
                    pins[pin_name] = pin_value
                break
            else:
                print("Pin configuration required!")
                
    return pins

def get_commands():
    """Get command templates from user"""
    print("\n=== Command Templates ===")
    print("Enter command templates using {pin}, {bus}, {addr}, {reg}, {val} placeholders:")
    
    commands = {}
    command_types = [
        ('gpio_set_high', 'Command to set GPIO pin high'),
        ('gpio_set_low', 'Command to set GPIO pin low'),
        ('gpio_get', 'Command to read GPIO pin state'),
        ('i2c_read', 'Command to read I2C register'),
        ('i2c_write', 'Command to write I2C register'),
        ('i2c_scan', 'Command to scan I2C bus')
    ]
    
    for cmd_name, description in command_types:
        cmd = get_user_input(f"{description}")
        if cmd:
            commands[cmd_name] = cmd
            
    return commands

def get_communication_config():
    """Get communication configuration"""
    print("\n=== Communication Configuration ===")
    comm_types = ['direct', 'serial', 'tcp', 'custom']
    
    print("Communication types:")
    for i, comm_type in enumerate(comm_types, 1):
        print(f"{i}. {comm_type}")
        
    while True:
        choice = get_user_input("Select communication type (1-4)", "1")
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(comm_types):
                comm_type = comm_types[choice_idx]
                break
        except ValueError:
            pass
        print("Invalid choice, please enter 1-4")
        
    config = {"type": comm_type}
    
    if comm_type == "serial":
        config["baudrate"] = int(get_user_input("Baudrate", "115200"))
        config["timeout"] = int(get_user_input("Timeout (seconds)", "5"))
    elif comm_type == "tcp":
        config["ip"] = get_user_input("IP Address", "192.168.1.100")
        config["port"] = int(get_user_input("Port", "8080"))
        
    return config

def get_dependencies():
    """Get dependency information"""
    print("\n=== Dependencies ===")
    
    deps = {}
    
    python_packages = get_user_input("Python packages (comma-separated)", "")
    if python_packages:
        deps["python_packages"] = [pkg.strip() for pkg in python_packages.split(",")]
        
    system_packages = get_user_input("System packages (comma-separated)", "")
    if system_packages:
        deps["system_packages"] = [pkg.strip() for pkg in system_packages.split(",")]
        
    return deps

def get_setup_instructions():
    """Get setup instructions"""
    print("\n=== Setup Instructions ===")
    print("Enter setup instructions (one per line, empty line to finish):")
    
    instructions = []
    while True:
        instruction = input("Step: ").strip()
        if not instruction:
            break
        instructions.append(instruction)
        
    return instructions

def create_platform_config():
    """Interactive platform configuration creator"""
    print("=" * 60)
    print("AS7265x Platform Configuration Creator")
    print("=" * 60)
    
    # Basic platform info
    print("\n=== Platform Information ===")
    name = get_user_input("Platform name (e.g., 'Arduino Uno')")
    platform_id = get_user_input("Platform ID (e.g., 'arduino_uno')", 
                                name.lower().replace(' ', '_'))
    description = get_user_input("Description", f"{name} with AS7265x support")
    i2c_bus = get_user_input("I2C bus number/name", "1")
    
    # Try to convert to int
    try:
        i2c_bus = int(i2c_bus)
    except ValueError:
        pass  # Keep as string
    
    # Get detailed configuration
    pins = get_pin_config()
    commands = get_commands()
    communication = get_communication_config()
    dependencies = get_dependencies()
    setup_instructions = get_setup_instructions()
    
    # Build configuration
    config = {
        "name": name,
        "platform": platform_id,
        "description": description,
        "i2c_bus": i2c_bus,
        "pins": pins,
        "commands": commands,
        "setup_instructions": setup_instructions,
        "dependencies": dependencies
    }
    
    if communication["type"] != "direct":
        config["communication"] = communication
        
    # Save configuration
    print("\n=== Configuration Summary ===")
    print(json.dumps(config, indent=2))
    
    save = get_user_input("\nSave this configuration? (y/n)", "y")
    if save.lower() in ['y', 'yes']:
        # Create configs directory if it doesn't exist
        config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configs')
        os.makedirs(config_dir, exist_ok=True)
        
        filename = os.path.join(config_dir, f"{platform_id}.json")
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
            
        print(f"Configuration saved to: {filename}")
        print("\nTo use this platform:")
        print("1. Restart the AS7265x Evaluation GUI")
        print("2. Select your new platform from the dropdown")
        print("3. Follow the setup instructions")
    else:
        print("Configuration not saved")

def main():
    """Main entry point"""
    try:
        create_platform_config()
    except KeyboardInterrupt:
        print("\n\nConfiguration cancelled by user")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()