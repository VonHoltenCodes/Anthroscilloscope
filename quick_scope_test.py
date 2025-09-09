#!/usr/bin/env python3
"""Quick test to check oscilloscope probe compensation signal"""

import pyvisa
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

print("Connecting to Rigol DS1104Z Plus at 192.168.68.73...")
rm = pyvisa.ResourceManager('@py')
scope = rm.open_resource('TCPIP::192.168.68.73::INSTR')
scope.timeout = 10000

# Set Channel 1 for probe comp measurement
print("\nSetting up Channel 1 for probe compensation signal...")
scope.write(':CHANnel1:DISPlay ON')
scope.write(':CHANnel1:COUPling DC')
scope.write(':CHANnel1:PROBe 10')  # Set 10X probe
scope.write(':CHANnel1:SCALe 1')    # 1V/div

# Set timebase for 1kHz signal
scope.write(':TIMebase:MAIN:SCALe 0.0002')  # 200us/div

# Auto trigger setup
scope.write(':TRIGger:EDGE:SOURce CHANnel1')
scope.write(':TRIGger:EDGE:LEVel 1.5')  # 1.5V trigger level

# Let scope acquire data
print("Acquiring data...")
scope.write(':RUN')
import time
time.sleep(2)

# Get waveform
scope.write(':WAVeform:SOURce CHANnel1')
scope.write(':WAVeform:MODE NORMal')
scope.write(':WAVeform:FORMat BYTE')

# Get scaling info
preamble = scope.query(':WAVeform:PREamble?').strip().split(',')
y_increment = float(preamble[7])
y_origin = float(preamble[8])
y_reference = float(preamble[9])
x_increment = float(preamble[4])

# Get data
scope.write(':WAVeform:DATA?')
raw_data = scope.read_raw()

# Parse data
header_start = raw_data.find(b'#')
n_length_bytes = int(chr(raw_data[header_start + 1]))
data_length = int(raw_data[header_start + 2:header_start + 2 + n_length_bytes])
data_start = header_start + 2 + n_length_bytes
waveform_bytes = raw_data[data_start:data_start + data_length]

# Convert to voltage
waveform_data = np.frombuffer(waveform_bytes, dtype=np.uint8)
voltage_data = ((waveform_data - y_reference) * y_increment) + y_origin
time_data = np.arange(len(voltage_data)) * x_increment

# Calculate measurements
vmax = np.max(voltage_data)
vmin = np.min(voltage_data)
vpp = vmax - vmin
vavg = np.mean(voltage_data)

print(f"\n=== Probe Compensation Signal Measurements ===")
print(f"Vpp (peak-to-peak): {vpp:.3f}V")
print(f"Vmax: {vmax:.3f}V")
print(f"Vmin: {vmin:.3f}V")
print(f"Vavg: {vavg:.3f}V")

# Estimate frequency from zero crossings
mean_v = np.mean(voltage_data)
crossings = np.where(np.diff(np.sign(voltage_data - mean_v)))[0]
if len(crossings) > 2:
    period = 2 * np.mean(np.diff(crossings)) * x_increment
    freq = 1 / period
    print(f"Frequency: {freq:.1f}Hz")

# Save plot
plt.figure(figsize=(10, 6))
plt.plot(time_data * 1000, voltage_data, 'b-', linewidth=1)
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (V)')
plt.title('Probe Compensation Signal (1kHz Square Wave)')
plt.grid(True, alpha=0.3)
plt.savefig('probe_comp_signal.png')
print(f"\nPlot saved to probe_comp_signal.png")

# Save screenshot
print("Capturing oscilloscope screenshot...")
scope.write(':DISPlay:DATA? ON,0,PNG')
raw_data = scope.read_raw()
header_start = raw_data.find(b'#')
n_length_bytes = int(chr(raw_data[header_start + 1]))
data_length = int(raw_data[header_start + 2:header_start + 2 + n_length_bytes])
data_start = header_start + 2 + n_length_bytes
png_data = raw_data[data_start:data_start + data_length]
with open('scope_display.png', 'wb') as f:
    f.write(png_data)
print("Screenshot saved to scope_display.png")

scope.close()
rm.close()

print("\n=== Expected Values for Probe Comp Signal ===")
print("- Square wave: ~3V peak-to-peak")
print("- Frequency: ~1kHz")
print("- If probe is properly compensated, edges should be square")
print("- If overcompensated: overshoot on edges")
print("- If undercompensated: rounded edges")
print("\nTo adjust probe compensation, use the small screwdriver")
print("that came with your probe to adjust the trimmer capacitor")