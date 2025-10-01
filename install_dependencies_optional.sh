#!/bin/bash
#
# Lissajous Text Generation System - Optional Dependencies Installer
# Installs OPTIONAL packages for advanced features
#

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  LISSAJOUS TEXT GENERATION - OPTIONAL DEPENDENCIES         ║"
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

echo -e "${YELLOW}→ This script will install optional dependencies:${NC}"
echo "  • Shapely (geometric operations)"
echo "  • HDF5 (large dataset storage)"
echo "  • PyQt5 (advanced GUI toolkit)"
echo ""
echo "Note: These are NOT required for basic text generation"
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

echo -e "\n${YELLOW}→ Installing system libraries...${NC}"
sudo apt update
sudo apt install -y libgeos-dev libhdf5-dev

echo -e "${GREEN}✓ System libraries installed${NC}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "PHASE 2: Python Packages"
echo "═══════════════════════════════════════════════════════════"

echo -e "\n${YELLOW}→ Installing Python packages...${NC}"
pip3 install --user shapely h5py PyQt5

echo -e "${GREEN}✓ Python packages installed${NC}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "VERIFICATION"
echo "═══════════════════════════════════════════════════════════"

echo -e "\n${YELLOW}→ Verifying installations...${NC}\n"

python3 << 'EOF'
import sys

packages = [
    ('shapely', 'Shapely', False),
    ('h5py', 'HDF5', False),
    ('PyQt5', 'PyQt5', False),
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
    echo "All optional packages installed successfully!"
else
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ✗ INSTALLATION FAILED                                     ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Some packages failed to install. Check errors above."
    exit 1
fi
