# Lissajous Text Generation - Dependencies Quick Start

## TL;DR - Fast Install

```bash
cd /home/traxx/Development/Anthroscilloscope

# Install CRITICAL dependencies (required)
./install_dependencies_critical.sh

# Verify installation
python3 verify_dependencies.py

# Optional: Install recommended packages
./install_dependencies_recommended.sh

# Optional: Install extra features
./install_dependencies_optional.sh
```

---

## Current Status

**7 of 17 packages installed (41%)**

### ✓ Already Have
- numpy, scipy, matplotlib
- fonttools, pytest
- System audio (ALSA/PulseAudio)
- USB support

### ✗ Need to Install (CRITICAL)
- **pyvisa** - Oscilloscope control
- **pyvisa-py** - VISA backend
- **pyusb** - USB communication
- **pyserial** - Serial ports
- **sounddevice** - Audio generation

---

## Installation Steps

### Step 1: Critical Dependencies (REQUIRED)

These are **essential** for text generation to work:

```bash
./install_dependencies_critical.sh
```

**Installs:**
- PyVISA ecosystem (oscilloscope control)
- SoundDevice (audio output for Lissajous patterns)
- PortAudio (audio system library)

**Time:** ~2-3 minutes

---

### Step 2: Verify Installation

```bash
python3 verify_dependencies.py
```

**Should show:**
```
✓ STATUS: All critical dependencies installed
          Ready to proceed with development!
```

---

### Step 3: Recommended Packages (OPTIONAL)

Enhanced functionality but not required:

```bash
./install_dependencies_recommended.sh
```

**Installs:**
- FreeType-Py (advanced font rendering)
- Tkinter (GUI toolkit for separate windows)

**Time:** ~1 minute

---

### Step 4: Optional Packages (SKIP FOR NOW)

Advanced features - install only if needed later:

```bash
./install_dependencies_optional.sh
```

**Installs:**
- Shapely (geometric operations)
- HDF5 (large dataset storage)
- PyQt5 (advanced GUI)

---

## Test After Installation

### 1. Test Oscilloscope Connection
```bash
python3 test_rigol_connection.py
```

### 2. Test Audio Generation
```bash
python3 simple_audio_test.py
```

### 3. Run Main Interface
```bash
python3 anthroscilloscope_main.py
```

---

## Manual Installation

If scripts fail, install manually:

### Critical (Required)
```bash
# System packages
sudo apt update
sudo apt install -y portaudio19-dev libusb-1.0-0-dev

# Python packages
pip3 install --user pyvisa pyvisa-py pyusb pyserial sounddevice
```

### Recommended (Optional)
```bash
sudo apt install -y python3-tk
pip3 install --user freetype-py
```

---

## Troubleshooting

### "pip3: command not found"
```bash
sudo apt install python3-pip
```

### "Permission denied" on scripts
```bash
chmod +x install_dependencies_*.sh
```

### "Cannot find oscilloscope"
```bash
# Check oscilloscope IP in config
python3 -c "import config; print(config.RIGOL_IP)"

# Test network connection
ping <oscilloscope_ip>
```

### "No audio devices found"
```bash
# List audio devices
python3 -c "import sounddevice; print(sounddevice.query_devices())"
```

---

## What Each Package Does

| Package | Purpose | Required? |
|---------|---------|-----------|
| **numpy** | Array math, waveform generation | ✓ CRITICAL |
| **scipy** | Signal processing, FFT | ✓ CRITICAL |
| **matplotlib** | Waveform visualization | ✓ CRITICAL |
| **pyvisa** | Oscilloscope communication | ✓ CRITICAL |
| **sounddevice** | Audio output for patterns | ✓ CRITICAL |
| fonttools | Font parsing for text | RECOMMENDED |
| freetype-py | Advanced font rendering | RECOMMENDED |
| tkinter | GUI toolkit | RECOMMENDED |
| shapely | Geometry operations | OPTIONAL |
| h5py | Large dataset storage | OPTIONAL |
| pytest | Unit testing | OPTIONAL |

---

## Next Steps After Installation

1. **Verify everything works:**
   ```bash
   python3 verify_dependencies.py
   ```

2. **Configure oscilloscope IP:**
   ```bash
   cp config_template.py config.py
   # Edit config.py with your oscilloscope's IP address
   ```

3. **Test connection:**
   ```bash
   python3 test_rigol_connection.py
   ```

4. **Start development:**
   - Review project documentation
   - Begin Phase 1: Character stroke library
   - Test basic line-to-Lissajous conversion

---

## Files Created

- `DEPENDENCIES_REPORT.md` - Complete dependency analysis
- `install_dependencies_critical.sh` - Install required packages
- `install_dependencies_recommended.sh` - Install recommended packages
- `install_dependencies_optional.sh` - Install optional packages
- `verify_dependencies.py` - Check installation status
- `DEPENDENCIES_QUICKSTART.md` - This file

---

## Getting Help

- Check `DEPENDENCIES_REPORT.md` for detailed information
- Review troubleshooting section above
- Check existing issues: https://github.com/VonHoltenCodes/Anthroscilloscope/issues
- Ensure oscilloscope is on same network and accessible

---

**Ready to install?** Run: `./install_dependencies_critical.sh`
