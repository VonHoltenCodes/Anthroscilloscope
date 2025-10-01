#!/bin/bash
# Anthroscilloscope Text GUI Launcher (macOS/Linux)
# Launches the Phase 3 standard text rendering GUI

cd "$(dirname "$0")"

echo "========================================================================"
echo "ANTHROSCILLOSCOPE - Lissajous Text Generator"
echo "========================================================================"
echo ""
echo "Launching Phase 3 Standard GUI..."
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 not found!"
    echo "Please install Python 3.10+ or run: ./anthroscilloscope_setup.sh"
    exit 1
fi

# Check dependencies
if ! python3 -c "import matplotlib" 2>/dev/null; then
    echo "⚠️  WARNING: matplotlib not found"
    echo "Installing dependencies..."
    ./anthroscilloscope_setup.sh
fi

# Launch GUI
python3 text_gui.py "$@"

echo ""
echo "GUI closed."
