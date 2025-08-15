#!/bin/bash
# Install AS7265x Spectral Sensor Tester
echo "Installing AS7265x Spectral Sensor Tester..."

# Install Python dependencies
pip3 install -r requirements.txt

# Copy desktop launcher
cp desktop/AS7265x_Tester.desktop ~/Desktop/
chmod +x ~/Desktop/AS7265x_Tester.desktop

# Make main script executable  
chmod +x as7265x_tester.py

echo "Installation complete!"
echo "Double-click 'AS7265x Tester' icon on desktop to run"