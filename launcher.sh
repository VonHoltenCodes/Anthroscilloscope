#!/bin/bash
# Anthroscilloscope Launcher Script
# This is the public version - no hardcoded IPs

cd "$(dirname "$0")"

# Check if config exists
if [ ! -f "config.py" ]; then
    echo "⚠️  No config.py found. Creating from example..."
    cp config_example.py config.py
    echo "✅ Created config.py - please edit it with your oscilloscope IP"
    echo ""
fi

# Launch main interface
python3 anthroscilloscope_main.py "$@"