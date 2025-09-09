#!/bin/bash

# Rigol DS1104Z Plus Oscilloscope Control - Setup Script
# This script installs all required dependencies on Linux (Ubuntu/Debian)

echo "================================================"
echo "Rigol DS1104Z Plus - Python Control Setup"
echo "================================================"

# Update pip first
echo "Updating pip..."
python3 -m pip install --upgrade pip

# Install required Python packages
echo "Installing Python dependencies..."
pip3 install --user pyvisa pyvisa-py pyusb pyserial matplotlib numpy

# Alternative: Use system package manager (uncomment if preferred)
# sudo apt update
# sudo apt install python3-pyvisa python3-matplotlib python3-numpy python3-usb python3-serial

echo ""
echo "================================================"
echo "Installation Complete!"
echo "================================================"
echo ""
echo "To test your setup:"
echo "1. Make sure your oscilloscope is connected to the network"
echo "2. Find its IP address (Utility -> IO -> LAN on the scope)"
echo "3. Run: python3 rigol_oscilloscope_control.py"
echo ""
echo "Troubleshooting:"
echo "- If you get permission errors, add your user to the dialout group:"
echo "  sudo usermod -a -G dialout $USER"
echo "  (then logout and login again)"
echo ""
echo "- For USB connection support, create udev rule:"
echo "  echo 'SUBSYSTEM==\"usb\", ATTR{idVendor}==\"1ab1\", MODE=\"0666\"' | sudo tee /etc/udev/rules.d/99-rigol.rules"
echo "  sudo udevadm control --reload-rules"
echo ""