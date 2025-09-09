# Anthroscilloscope

```
                 ╔════════════════════════════════════════════════════════════╗
                 ║  ┌────────────────────────────────────────────────────┐    ║
                 ║  │                                                    │    ║
                 ║  │     ╱╲    ╱╲    ╱╲    ╱╲    ╱╲    ╱╲    ╱╲     │    ║
                 ║  │    ╱  ╲  ╱  ╲  ╱  ╲  ╱  ╲  ╱  ╲  ╱  ╲  ╱  ╲    │    ║
                 ║  │   ╱    ╲╱    ╲╱    ╲╱    ╲╱    ╲╱    ╲╱    ╲   │    ║
                 ║  │ ──┼────────────────────────────────────────────┼── │    ║
                 ║  │   │   ANTHROSCILLOSCOPE                        │   │    ║
                 ║  │   │                                            │   │    ║
                 ║  │ ──┼────────────────────────────────────────────┼── │    ║
                 ║  └────────────────────────────────────────────────────┘    ║
                 ║                                                            ║
                 ║  VERTICAL            HORIZONTAL         TRIGGER           ║
                 ║  ┌─────┐ ┌─────┐    ┌─────┐ ┌─────┐    ┌─────┐ ┌─────┐  ║
                 ║  │ ◉   │ │   ◉ │    │  ◉  │ │ ◉   │    │   ◉ │ │  ◉  │  ║
                 ║  └─────┘ └─────┘    └─────┘ └─────┘    └─────┘ └─────┘  ║
                 ║  VOLTS/DIV  POS     TIME/DIV  POS       LEVEL   MODE    ║
                 ║                                                            ║
                 ║  [CH1] [CH2] [MATH] [REF]    [AUTO] [RUN/STOP] [SINGLE]  ║
                 ║   ▀▀▀   ───   ───    ───       ▀▀▀     ───       ───     ║
                 ║                                                            ║
                 ║  ○ CH1  ○ CH2  ○ EXT  ○ LINE         ■ POWER             ║
                 ║  └─BNC─┘└─BNC─┘└─BNC─┘└─BNC─┘         ON/OFF             ║
                 ╚════════════════════════════════════════════════════════════╝
                       ╱│                                          │╲
                      ╱ └──────────────────────────────────────────┘ ╲
                     ╱________________________________________________╲

         ╔═╗╔╗╔╔╦╗╦ ╦╦═╗╔═╗╔═╗╔═╗╦╦  ╦  ╔═╗╔═╗╔═╗╔═╗╔═╗╔═╗
         ╠═╣║║║ ║ ╠═╣╠╦╝║ ║╚═╗║  ║║  ║  ║ ║╚═╗║  ║ ║╠═╝║╣ 
         ╩ ╩╝╚╝ ╩ ╩ ╩╩╚═╚═╝╚═╝╚═╝╩╩═╝╩═╝╚═╝╚═╝╚═╝╚═╝╩  ╚═╝
```

> **Transform your Rigol DS1104Z Plus into a powerful PC-controlled measurement station**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyVISA](https://img.shields.io/badge/PyVISA-1.15.0-green.svg)](https://pyvisa.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)](https://github.com/VonHoltenCodes/Anthroscilloscope)

## 📡 What is Anthroscilloscope?

Anthroscilloscope is a comprehensive Python toolkit that brings your Rigol DS1104Z Plus oscilloscope to life on your computer. Whether you're debugging circuits, analyzing signals, or automating measurements, this suite provides everything you need for seamless remote control and data acquisition.

### ✨ Key Features

- **🎯 Real-Time Waveform Display** - Stream live waveforms directly to your PC with matplotlib visualization
- **📸 Screenshot Capture** - Save high-resolution oscilloscope displays as PNG files
- **📊 Automated Measurements** - Programmatically capture Vpp, Vmax, Vmin, Frequency, Period, and more
- **🔧 No Proprietary Drivers** - Uses pure Python PyVISA backend - no NI-VISA required
- **🖥️ Interactive CLI** - User-friendly menu system for quick measurements
- **🐍 Python API** - Full programmatic control for custom automation scripts
- **🌐 Ethernet/LAN Control** - Fast, reliable connection over your network

## 🚀 Quick Start

### Prerequisites

- Rigol DS1104Z Plus Oscilloscope (or compatible DS1000Z series)
- Python 3.10 or higher
- Ethernet connection between PC and oscilloscope

### Installation

```bash
# Clone the repository
git clone https://github.com/VonHoltenCodes/Anthroscilloscope.git
cd Anthroscilloscope

# Run the complete setup script (Linux/Mac)
chmod +x anthroscilloscope_setup.sh
./anthroscilloscope_setup.sh

# Or install manually
pip3 install pyvisa pyvisa-py pyusb pyserial matplotlib numpy scipy h5py
# Optional: pip3 install pandas zeroconf
```

### First Connection

1. **Configure your oscilloscope for LAN access:**
   ```
   Utility → I/O → LAN Config → DHCP/Static IP
   ```
   Note the IP address displayed

2. **Test the connection:**
   ```bash
   python3 test_rigol_connection.py
   ```

3. **Run the main control interface:**
   ```bash
   python3 anthroscilloscope_main.py
   # Or use the launcher:
   ./anthroscilloscope
   ```

## 📖 Usage Examples

### Interactive Menu System

```bash
$ python3 rigol_oscilloscope_control.py

Anthroscilloscope - Rigol DS1104Z Control
==========================================
Enter oscilloscope IP address: 192.168.1.100

Main Menu:
1. Single waveform capture
2. Live waveform display
3. Save screenshot
4. Display measurements
5. Exit

Select option: 2
[Live waveform streaming begins...]
```

### Python API Usage

```python
from rigol_oscilloscope_control import RigolDS1104Z
import matplotlib.pyplot as plt

# Connect to your oscilloscope
scope = RigolDS1104Z("192.168.1.100")
scope.connect()

# Capture waveform data
time_data, voltage_data = scope.get_waveform_data(channel=1)

# Make measurements
measurements = {
    'Vpp': scope.get_measurement(1, 'VPP'),
    'Frequency': scope.get_measurement(1, 'FREQ'),
    'RMS': scope.get_measurement(1, 'VRMS')
}

print(f"Signal: {measurements['Vpp']:.3f} Vpp @ {measurements['Frequency']:.1f} Hz")

# Save oscilloscope screenshot
scope.save_screenshot("measurement_capture.png")

# Plot the waveform
plt.figure(figsize=(10, 6))
plt.plot(time_data, voltage_data)
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.title('Captured Waveform')
plt.grid(True)
plt.show()

scope.close()
```

### Automated Testing Script

```python
# Quick probe compensation check
from quick_scope_test import quick_probe_test

# Automatically captures and analyzes the probe compensation signal
results = quick_probe_test("192.168.1.100")
print(f"Probe compensation: {results['status']}")
```

## 🛠️ Available Scripts

### Core Scripts
| Script | Description |
|--------|-------------|
| `anthroscilloscope_main.py` | **Main interface with all features** |
| `rigol_oscilloscope_control.py` | Basic control interface |
| `rigol_display_fixed.py` | Optimized live waveform display |
| `test_suite.py` | Comprehensive test suite |

### Feature Modules
| Module | Description |
|--------|-------------|
| `long_memory_capture.py` | Deep memory acquisition (up to 12M points) |
| `spectrum_analyzer.py` | FFT analysis with peak detection |
| `trigger_control.py` | Advanced trigger configuration |
| `acquisition_control.py` | Acquisition modes and sampling control |
| `device_discovery.py` | Auto-discovery of oscilloscopes |
| `data_export.py` | Multi-format data export |

### Utility Scripts
| Script | Description |
|--------|-------------|
| `quick_scope_test.py` | Probe compensation verification |
| `capture_and_analyze.py` | Advanced waveform analysis |
| `test_connection_quick.py` | Quick connectivity test |
| `anthroscilloscope_setup.sh` | Complete installation script |

## 📋 Supported SCPI Commands

The toolkit implements the full Rigol DS1000Z SCPI command set:

### Waveform Acquisition
- `:WAVeform:SOURce` - Select channel source
- `:WAVeform:DATA?` - Retrieve waveform data
- `:WAVeform:PREamble?` - Get scaling parameters

### Measurements
- `:MEASure:ITEM?` - Query specific measurements
  - Voltage: `VPP`, `VMAX`, `VMIN`, `VAVG`, `VRMS`
  - Time: `FREQ`, `PERiod`, `RISetime`, `FALLtime`
  - Pulse: `PWIDth`, `NWIDth`, `PDUTy`, `NDUTy`

### Display Control
- `:DISPlay:DATA?` - Capture screenshot
- `:CHANnel<n>:DISPlay` - Enable/disable channels
- `:AUToscale` - Auto-setup signal display

## 🔧 Troubleshooting

### Connection Issues

```bash
# Check network connectivity
ping <oscilloscope_ip>

# Verify SCPI port is accessible
telnet <oscilloscope_ip> 5555

# Run connection test
python3 test_rigol_connection.py
```

### Common Problems & Solutions

| Issue | Solution |
|-------|----------|
| No connection | Check IP address in Utility → I/O → LAN Config |
| Timeout errors | Increase timeout: `scope.timeout = 10000` |
| No waveform display | Use `rigol_display_fixed.py` for Linux systems |
| Invalid measurements (9.9E+37) | Channel disabled or no signal present |

## 🏗️ Architecture

```
Anthroscilloscope/
├── Core Control
│   ├── rigol_oscilloscope_control.py  # Main control class
│   └── test_rigol_connection.py       # Connection utilities
├── Display & Visualization
│   ├── rigol_display_fixed.py         # Live display (stable)
│   └── rigol_live_display.py          # Alternative display
├── Analysis Tools
│   ├── capture_and_analyze.py         # Waveform analysis
│   └── quick_scope_test.py            # Probe testing
└── Setup & Configuration
    └── rigol_setup.sh                  # Dependency installer
```

## 🤝 Contributing

Contributions are welcome! Whether it's bug fixes, new features, or documentation improvements, feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the Rigol DS1104Z Plus community
- PyVISA team for the excellent VISA implementation
- All contributors and testers

## 📬 Support

Having issues? Found a bug? Have a feature request?

- Open an [Issue](https://github.com/VonHoltenCodes/Anthroscilloscope/issues)
- Check existing issues for solutions
- Include your oscilloscope model and firmware version

---

<div align="center">
<b>Anthroscilloscope</b> - Bringing professional oscilloscope control to your desktop<br>
Made with ❤️ for the electronics community
</div>