#!/bin/bash
#
# Lissajous Text Generation System - Critical Dependencies Installer
# Installs only REQUIRED packages for basic functionality
#

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  LISSAJOUS TEXT GENERATION - CRITICAL DEPENDENCIES         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}✗ Do not run this script as root${NC}"
   echo "  Run without sudo - script will prompt for sudo when needed"
   exit 1
fi

echo -e "${YELLOW}→ This script will install critical dependencies:${NC}"
echo "  • PyVISA ecosystem (oscilloscope control)"
echo "  • SoundDevice (audio generation)"
echo "  • PortAudio (audio system)"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "PHASE 1: System Packages"
echo "═══════════════════════════════════════════════════════════"

# Update package list
echo -e "\n${YELLOW}→ Updating package list...${NC}"
sudo apt update

# Install system dependencies
echo -e "\n${YELLOW}→ Installing system packages...${NC}"
sudo apt install -y \
    portaudio19-dev \
    libusb-1.0-0-dev

echo -e "${GREEN}✓ System packages installed${NC}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "PHASE 2: Python Packages - Oscilloscope Control"
echo "═══════════════════════════════════════════════════════════"

echo -e "\n${YELLOW}→ Installing PyVISA ecosystem...${NC}"
pip3 install --user pyvisa pyvisa-py pyusb pyserial

echo -e "${GREEN}✓ PyVISA packages installed${NC}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "PHASE 3: Python Packages - Audio Generation"
echo "═══════════════════════════════════════════════════════════"

echo -e "\n${YELLOW}→ Installing SoundDevice...${NC}"
pip3 install --user sounddevice

echo -e "${GREEN}✓ SoundDevice installed${NC}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "VERIFICATION"
echo "═══════════════════════════════════════════════════════════"

echo -e "\n${YELLOW}→ Verifying installations...${NC}\n"

python3 << 'EOF'
import sys

packages = [
    ('pyvisa', 'PyVISA', True),
    ('pyvisa_py', 'PyVISA-Py', True),
    ('usb', 'PyUSB', True),
    ('serial', 'PySerial', True),
    ('sounddevice', 'SoundDevice', True),
]

success = True
for module, name, critical in packages:
    try:
        mod = __import__(module)
        ver = getattr(mod, '__version__', 'unknown')
        print(f"  ✓ {name:15} v{ver}")
    except ImportError as e:
        print(f"  ✗ {name:15} FAILED TO IMPORT")
        if critical:
            success = False

sys.exit(0 if success else 1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✓ INSTALLATION SUCCESSFUL                                 ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Test oscilloscope connection:"
    echo "     python3 test_rigol_connection.py"
    echo ""
    echo "  2. Test audio generation:"
    echo "     python3 simple_audio_test.py"
    echo ""
    echo "  3. Run main interface:"
    echo "     python3 anthroscilloscope_main.py"
    echo ""
    echo "Optional: Install recommended packages with:"
    echo "  ./install_dependencies_recommended.sh"
else
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ✗ INSTALLATION FAILED                                     ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Some packages failed to install. Check errors above."
    exit 1
fi
