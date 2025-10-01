# Anthroscilloscope Launcher Scripts

Quick reference for all launcher scripts across platforms.

## Text Rendering GUIs (New! Phases 3-4)

### Standard GUI (Phase 3)
**Linux/macOS:**
```bash
./launch_text_gui.sh
```

**Windows:**
```batch
launch_text_gui.bat
```

**Features:**
- Text input and preview
- Font size control (0.3x-3.0x)
- Speed control (0.1x-5.0x)
- WAV export
- Preset management

### Advanced GUI (Phase 4)
**Linux/macOS:**
```bash
./launch_text_gui_advanced.sh
```

**Windows:**
```batch
launch_text_gui_advanced.bat
```

**Features:**
- All Phase 3 features, plus:
- Rotation (0-360°)
- Independent X/Y scaling
- Skew/italics effect
- Shadow effect
- 3D perspective
- Wave distortion

## Main Oscilloscope Control

### Main Interface
**Linux/macOS:**
```bash
./launcher.sh
# or
python3 anthroscilloscope_main.py
```

**Windows:**
```batch
anthroscilloscope.bat
```

## Direct Script Execution

### Text GUIs
```bash
# Standard GUI
python3 text_gui.py

# Advanced GUI
python3 text_gui_advanced.py

# Demo GUI
python3 demo_gui.py
```

### Oscilloscope Functions
```bash
# Main menu interface
python3 anthroscilloscope_main.py

# Live waveform display
python3 rigol_display_fixed.py

# Lissajous XY mode
python3 lissajous_xy_mode.py

# Interactive Lissajous demo
python3 interactive_lissajous_demo.py
```

## Setup Scripts

### Initial Setup
**Linux/macOS:**
```bash
./anthroscilloscope_setup.sh
```

**Windows:**
```batch
anthroscilloscope_setup.bat
```

### Dependency Installation (Linux/macOS)
```bash
# Critical dependencies only
./install_dependencies_critical.sh

# Recommended packages
./install_dependencies_recommended.sh

# Optional packages
./install_dependencies_optional.sh
```

## Platform Notes

### macOS
- All `.sh` scripts work natively
- May need to grant Terminal permissions
- Use `chmod +x *.sh` if scripts aren't executable

### Windows
- All `.bat` scripts work natively
- Run from Command Prompt or PowerShell
- May need to "Run as Administrator" for installations

### Linux
- All `.sh` scripts work natively
- Scripts are marked executable in repository
- If needed: `chmod +x *.sh`

## Troubleshooting

### "Permission denied" on macOS/Linux
```bash
chmod +x launch_text_gui.sh
chmod +x launch_text_gui_advanced.sh
chmod +x launcher.sh
```

### Python not found (Windows)
1. Install Python 3.10+ from python.org
2. Check "Add Python to PATH" during installation
3. Or run: `anthroscilloscope_setup.bat`

### Dependencies missing
**Any platform:**
Run the setup script for your platform to install all dependencies.

## Quick Start Guide

1. **First time setup:**
   - Run setup script for your platform
   - Wait for dependencies to install

2. **Try text rendering:**
   - Run `launch_text_gui.sh` (macOS/Linux) or `launch_text_gui.bat` (Windows)
   - Enter text and see real-time preview
   - Export to WAV for oscilloscope playback

3. **Try advanced effects:**
   - Run `launch_text_gui_advanced.sh` or `launch_text_gui_advanced.bat`
   - Experiment with rotation, 3D, and shadow effects

4. **Use with oscilloscope:**
   - Configure `config.py` with your scope's IP
   - Run main launcher for oscilloscope control
   - Or use exported WAV files with audio input

---

**Created by Trenton Von Holten** | [@VonHoltenCodes](https://github.com/VonHoltenCodes)
