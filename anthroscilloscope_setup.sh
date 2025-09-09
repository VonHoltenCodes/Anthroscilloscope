#!/bin/bash

# Anthroscilloscope Complete Setup Script
# Installs all required dependencies for the comprehensive oscilloscope control suite

echo "╔════════════════════════════════════════════════════════════╗"
echo "║              ANTHROSCILLOSCOPE SETUP                      ║"
echo "║     Advanced Oscilloscope Control Suite for Linux         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3 first:"
    echo "  sudo apt install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $PYTHON_VERSION detected"
echo ""

# Update pip
echo "📦 Updating pip..."
python3 -m pip install --upgrade pip --quiet

# Core dependencies
echo "📦 Installing core dependencies..."
pip3 install --user --upgrade pyvisa pyvisa-py pyusb pyserial matplotlib numpy

# Scientific computing packages
echo "📦 Installing scientific packages..."
pip3 install --user --upgrade scipy

# Data export packages
echo "📦 Installing data export packages..."
pip3 install --user --upgrade h5py

# Optional packages (with fallback)
echo "📦 Installing optional packages..."
pip3 install --user --upgrade pandas 2>/dev/null || echo "  ⚠ pandas (optional) - skipped"
pip3 install --user --upgrade zeroconf 2>/dev/null || echo "  ⚠ zeroconf (mDNS discovery) - skipped"

echo ""
echo "🔍 Verifying installations..."
echo ""

# Verification function
check_package() {
    if python3 -c "import $1" 2>/dev/null; then
        VERSION=$(python3 -c "import $1; print($1.__version__ if hasattr($1, '__version__') else 'installed')" 2>/dev/null)
        echo "  ✓ $2 ($VERSION)"
        return 0
    else
        echo "  ❌ $2 - not installed"
        return 1
    fi
}

# Check all packages
echo "Core packages:"
check_package "pyvisa" "PyVISA"
check_package "matplotlib" "Matplotlib"
check_package "numpy" "NumPy"
check_package "serial" "PySerial"
check_package "usb" "PyUSB"

echo ""
echo "Analysis packages:"
check_package "scipy" "SciPy"

echo ""
echo "Export packages:"
check_package "h5py" "HDF5 support"

echo ""
echo "Optional packages:"
check_package "pandas" "Pandas" || true
check_package "zeroconf" "mDNS Discovery" || true

# Create shortcuts
echo ""
echo "📝 Creating command shortcuts..."

# Create a launcher script
cat > anthroscilloscope << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 anthroscilloscope_main.py "$@"
EOF
chmod +x anthroscilloscope

echo "  ✓ Created './anthroscilloscope' launcher"

# Set permissions for all Python scripts
echo ""
echo "🔧 Setting executable permissions..."
chmod +x *.py 2>/dev/null

# Test VISA backend
echo ""
echo "🔌 Testing PyVISA backend..."
python3 -c "
import pyvisa
try:
    rm = pyvisa.ResourceManager('@py')
    print('  ✓ PyVISA-py backend is working')
except:
    print('  ⚠ PyVISA backend issue - may need troubleshooting')
"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  SETUP COMPLETE! 🎉                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📚 Available Commands:"
echo "  ./anthroscilloscope          - Launch main interface"
echo "  python3 anthroscilloscope_main.py   - Full-featured interface"
echo "  python3 test_suite.py         - Run test suite"
echo "  python3 device_discovery.py   - Find oscilloscopes on network"
echo ""
echo "🚀 Quick Start:"
echo "  1. Turn on your Rigol oscilloscope"
echo "  2. Connect it to your network (Ethernet cable)"
echo "  3. Enable LAN: Utility → I/O → LAN → DHCP ON"
echo "  4. Note the IP address shown"
echo "  5. Run: ./anthroscilloscope"
echo ""
echo "✨ New Features Available:"
echo "  • Device auto-discovery (no IP needed!)"
echo "  • Long memory capture (up to 12M points)"
echo "  • FFT spectrum analyzer with peak detection"
echo "  • Advanced trigger modes (edge, pulse, pattern, video)"
echo "  • Export to CSV, HDF5, JSON, MATLAB, WAV"
echo "  • Acquisition modes (normal, average, peak detect, high-res)"
echo ""
echo "📖 Documentation:"
echo "  README.md - Full documentation"
echo "  test_suite.py --quick - Quick connectivity test"
echo ""
echo "💡 Tip: Run './anthroscilloscope' to start!"
echo ""