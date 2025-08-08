#!/bin/bash
# Install spectral sensor test application

echo "Installing Spectral Sensor Test Application..."

# Install Python dependencies
pip3 install -r requirements.txt

# Copy desktop launcher
cp desktop/Spectral_Test.desktop ~/Desktop/
chmod +x ~/Desktop/Spectral_Test.desktop

# Make main script executable  
chmod +x spectral_test_gui.py

echo "Installation complete!"
echo "Double-click 'Spectral Test' icon on desktop to run"