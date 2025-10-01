#!/bin/bash
# Anthroscilloscope Advanced Text GUI Launcher (macOS/Linux)
# Launches the Phase 4 advanced text rendering GUI with effects

cd "$(dirname "$0")"

echo "========================================================================"
echo "ANTHROSCILLOSCOPE - Advanced Lissajous Text Generator (Phase 4)"
echo "========================================================================"
echo ""
echo "Launching Advanced GUI with Effects..."
echo "Features: Rotation, Scaling, 3D, Shadow, Wave effects"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 not found!"
    echo "Please install Python 3.10+ or run: ./anthroscilloscope_setup.sh"
    exit 1
fi

# Check dependencies
if ! python3 -c "import matplotlib, numpy" 2>/dev/null; then
    echo "⚠️  WARNING: Required packages not found"
    echo "Installing dependencies..."
    ./anthroscilloscope_setup.sh
fi

# Launch Advanced GUI
python3 text_gui_advanced.py "$@"

echo ""
echo "Advanced GUI closed."
