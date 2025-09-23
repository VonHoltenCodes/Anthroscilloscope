#!/usr/bin/env python3
"""
Anthroscilloscope Configuration Template
Copy this to config.py and update with your settings
"""

# Rigol DS1104Z Plus Configuration
RIGOL_IP = "YOUR_OSCILLOSCOPE_IP"  # e.g., "192.168.1.100"
RIGOL_PORT = 5555
RIGOL_TIMEOUT = 5000  # milliseconds

# Default settings
DEFAULT_CHANNEL = 1
DEFAULT_MEMORY_DEPTH = "AUTO"
DEFAULT_SAMPLE_RATE = 1e9  # 1 GSa/s

# Display settings
PLOT_STYLE = "dark"
GRID_ALPHA = 0.3
LINE_WIDTH = 1.5

# XY Mode settings
XY_DEFAULT_POINTS = 1200
XY_ANIMATION_INTERVAL = 20  # milliseconds

# Lissajous pattern defaults
LISSAJOUS_DEFAULT_RATIO_X = 3
LISSAJOUS_DEFAULT_RATIO_Y = 2
LISSAJOUS_DEFAULT_PHASE = 0  # radians

# File paths
DATA_DIRECTORY = "./data"
SCREENSHOT_DIRECTORY = "./screenshots"
EXPORT_DIRECTORY = "./exports"