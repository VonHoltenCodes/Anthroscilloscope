# Anthroscilloscope

Python control suite for Rigol DS1104Z Plus oscilloscope with real-time waveform display and measurements.

## Features

- **Live Waveform Display**: Real-time plotting of oscilloscope channels
- **Screenshot Capture**: Save oscilloscope display as PNG files
- **Measurements**: Read Vpp, Vmax, Vmin, Frequency, Period, etc.
- **Cross-platform**: Works on Linux without NI-VISA (uses pyvisa-py backend)
- **Interactive Menu**: User-friendly command-line interface

## Hardware Requirements

- Rigol DS1104Z Plus Oscilloscope (or compatible DS1000Z series)
- Ethernet connection between PC and oscilloscope
- Network configuration on same subnet

## Installation

### Quick Setup (Linux)

```bash
# Make setup script executable and run it
chmod +x rigol_setup.sh
./rigol_setup.sh
```

### Manual Installation

```bash
# Install Python dependencies
pip3 install --user pyvisa pyvisa-py pyusb pyserial matplotlib numpy

# Or using apt (Ubuntu/Debian)
sudo apt update
sudo apt install python3-pyvisa python3-matplotlib python3-numpy python3-usb python3-serial
```

## Oscilloscope Configuration

1. **Enable LAN/Ethernet on the oscilloscope:**
   - Press `Utility` button
   - Navigate to `I/O` 
   - Select `LAN Config`
   - Configure DHCP or Static IP
   - Note the IP address shown

2. **Verify network connection:**
   ```bash
   ping <oscilloscope_ip>
   ```

## Usage

### Basic Usage

```bash
python3 rigol_oscilloscope_control.py
```

Enter the oscilloscope's IP address when prompted, then select from the menu:
1. Single waveform capture
2. Live waveform view (updates every 500ms)
3. Save screenshot
4. Display measurements
5. Exit

### Available Scripts

- `rigol_oscilloscope_control.py` - Main control interface with menu
- `rigol_display_fixed.py` - Fixed live display (recommended)
- `quick_scope_test.py` - Quick probe compensation test
- `capture_and_analyze.py` - Capture and analyze waveforms
- `test_rigol_connection.py` - Test connection to oscilloscope

### Python Script Example

```python
from rigol_oscilloscope_control import RigolDS1104Z

# Connect to oscilloscope
scope = RigolDS1104Z("192.168.1.100")  # Replace with your scope's IP
scope.connect()

# Get waveform data
time_data, voltage_data = scope.get_waveform_data(channel=1)

# Save screenshot
scope.save_screenshot("my_capture.png")

# Get measurements
vpp = scope.get_measurement(1, 'VPP')
freq = scope.get_measurement(1, 'FREQ')

# Close connection
scope.close()
```

## Supported SCPI Commands

The script uses standard Rigol DS1000Z series SCPI commands:

- **Waveform Commands:**
  - `:WAVeform:SOURce CHANnel<n>` - Select channel
  - `:WAVeform:DATA?` - Get waveform data
  - `:WAVeform:PREamble?` - Get scaling parameters

- **Display Commands:**
  - `:DISPlay:DATA? ON,0,PNG` - Capture screenshot

- **Measurement Commands:**
  - `:MEASure:ITEM? <type>,CHANnel<n>` - Get measurement
  - Types: VPP, VMAX, VMIN, VAVG, VRMS, FREQ, PERiod

## Troubleshooting

### Connection Issues

1. **Verify IP address is correct:**
   - Check on scope: Utility → I/O → LAN Config

2. **Check network connectivity:**
   ```bash
   ping <oscilloscope_ip>
   ```

3. **Firewall issues:**
   - Temporarily disable firewall to test
   - Add exception for port 5555 (SCPI)

### No Display Window

- Matplotlib backend issues on Linux
- Solution: Use `rigol_display_fixed.py` instead of `rigol_live_display.py`

### Invalid Measurements (9.9E+37)

- Indicates no signal or channel disabled
- Check channel is ON and probe connected
- Use AUTO button on scope to find signal

## Network Setup Tips

### Static IP Configuration (Recommended)

On the oscilloscope:
1. Utility → I/O → LAN Config
2. DHCP/Static: Static
3. Set IP: 192.168.1.100 (example)
4. Set Mask: 255.255.255.0
5. Gateway: 192.168.1.1 (your router)

## Performance Notes

- Waveform transfer speed: ~10-50 Hz depending on network
- Screenshot capture: ~1-2 seconds
- For faster updates, reduce number of points

## Tested With

- Rigol DS1104Z Plus (100MHz, 4 channels)
- Firmware: 00.04.05.SP2
- Python 3.10+ on Linux (Pop!_OS, Ubuntu)
- PyVISA 1.15.0 with pyvisa-py backend

## License

This project is provided as-is for educational and personal use.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.