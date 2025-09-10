#!/usr/bin/env python3
"""
Configuration Example for Anthroscilloscope
Copy this file to config.py and update with your settings
"""

# Default oscilloscope IP address
# Update this with your oscilloscope's IP address
DEFAULT_IP = "192.168.1.100"  # Example IP

# Known device IPs for quick discovery
# Add your commonly used oscilloscope IPs here
KNOWN_DEVICES = [
    "192.168.1.100",
    "192.168.0.100",
    "10.0.0.100",
]

# Timeout settings (milliseconds)
DEFAULT_TIMEOUT = 5000
LONG_MEMORY_TIMEOUT = 30000

# Default settings
DEFAULT_CHANNEL = 1
DEFAULT_MEMORY_DEPTH = "AUTO"

# Export settings
EXPORT_FORMATS = ["csv", "hdf5", "numpy", "json"]
DEFAULT_EXPORT_PATH = "./exports/"

# Display settings
LIVE_DISPLAY_UPDATE_RATE = 500  # milliseconds
PLOT_STYLE = "dark_background"

# Network settings
SCPI_PORT = 5555
DISCOVERY_TIMEOUT = 10  # seconds

# Debug mode
DEBUG = False