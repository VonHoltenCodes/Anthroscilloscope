#!/usr/bin/env python3
"""Capture and analyze the current waveform on the oscilloscope"""

import pyvisa
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import time

print("="*60)
print("WAVEFORM CAPTURE AND ANALYSIS")
print("="*60)

# Connect to scope
rm = pyvisa.ResourceManager('@py')
scope = rm.open_resource('TCPIP::192.168.68.73::INSTR')
scope.timeout = 10000

print("\nConnected to oscilloscope")

# First, let's auto-scale to find the signal
print("Auto-scaling to find signal...")
scope.write(':AUToscale')
time.sleep(3)  # Wait for autoscale to complete

# Check which channels are active
channels_active = []
for ch in range(1, 5):
    state = scope.query(f':CHANnel{ch}:DISPlay?').strip()
    if state == '1':
        channels_active.append(ch)
        print(f"Channel {ch} is active")

if not channels_active:
    print("No active channels found! Enabling Channel 1...")
    scope.write(':CHANnel1:DISPlay ON')
    channels_active = [1]

# Get current settings
print("\n=== Current Oscilloscope Settings ===")
for ch in channels_active:
    scale = float(scope.query(f':CHANnel{ch}:SCALe?'))
    offset = float(scope.query(f':CHANnel{ch}:OFFSet?'))
    coupling = scope.query(f':CHANnel{ch}:COUPling?').strip()
    probe = float(scope.query(f':CHANnel{ch}:PROBe?'))
    print(f"Channel {ch}:")
    print(f"  Scale: {scale:.3f} V/div")
    print(f"  Offset: {offset:.3f} V")
    print(f"  Coupling: {coupling}")
    print(f"  Probe: {probe}X")

timebase = float(scope.query(':TIMebase:MAIN:SCALe?'))
print(f"\nTimebase: {timebase*1000:.3f} ms/div")

# Capture screenshot first
print("\n=== Capturing Screenshot ===")
scope.write(':DISPlay:DATA? ON,0,PNG')
raw_data = scope.read_raw()

# Parse PNG data
header_start = raw_data.find(b'#')
if header_start >= 0:
    n_length_bytes = int(chr(raw_data[header_start + 1]))
    data_length = int(raw_data[header_start + 2:header_start + 2 + n_length_bytes])
    data_start = header_start + 2 + n_length_bytes
    png_data = raw_data[data_start:data_start + data_length]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_file = f'waveform_screenshot_{timestamp}.png'
    with open(screenshot_file, 'wb') as f:
        f.write(png_data)
    print(f"Screenshot saved: {screenshot_file}")

# Now capture waveform data for each active channel
waveform_data = {}
time_data = {}

for ch in channels_active:
    print(f"\n=== Capturing Channel {ch} Waveform ===")
    
    # Configure waveform source
    scope.write(f':WAVeform:SOURce CHANnel{ch}')
    scope.write(':WAVeform:MODE NORMal')
    scope.write(':WAVeform:FORMat BYTE')
    
    # Get preamble for scaling
    preamble = scope.query(':WAVeform:PREamble?').strip().split(',')
    points = int(preamble[2])
    x_increment = float(preamble[4])
    x_origin = float(preamble[5])
    y_increment = float(preamble[7])
    y_origin = float(preamble[8])
    y_reference = float(preamble[9])
    
    # Get waveform data
    scope.write(':WAVeform:DATA?')
    raw_data = scope.read_raw()
    
    # Parse binary data
    header_start = raw_data.find(b'#')
    if header_start >= 0:
        n_length_bytes = int(chr(raw_data[header_start + 1]))
        data_length = int(raw_data[header_start + 2:header_start + 2 + n_length_bytes])
        data_start = header_start + 2 + n_length_bytes
        waveform_bytes = raw_data[data_start:data_start + data_length]
        
        # Convert to voltage
        waveform = np.frombuffer(waveform_bytes, dtype=np.uint8)
        voltage = ((waveform - y_reference) * y_increment) + y_origin
        time = np.arange(len(voltage)) * x_increment + x_origin
        
        waveform_data[ch] = voltage
        time_data[ch] = time
        
        print(f"Captured {len(voltage)} points")

# Perform measurements
print("\n=== Waveform Analysis ===")

for ch in channels_active:
    if ch in waveform_data:
        voltage = waveform_data[ch]
        time = time_data[ch]
        
        print(f"\nChannel {ch} Analysis:")
        print("-" * 40)
        
        # Basic measurements
        vmax = np.max(voltage)
        vmin = np.min(voltage)
        vpp = vmax - vmin
        vavg = np.mean(voltage)
        vrms = np.sqrt(np.mean(voltage**2))
        
        print(f"Voltage Measurements:")
        print(f"  Vmax: {vmax:.3f} V")
        print(f"  Vmin: {vmin:.3f} V")
        print(f"  Vpp: {vpp:.3f} V")
        print(f"  Vavg: {vavg:.3f} V")
        print(f"  Vrms: {vrms:.3f} V")
        
        # Try to detect frequency
        # Find zero crossings
        mean_v = np.mean(voltage)
        zero_crossings = np.where(np.diff(np.sign(voltage - mean_v)))[0]
        
        if len(zero_crossings) > 2:
            # Calculate period from zero crossings
            periods = []
            for i in range(0, len(zero_crossings)-2, 2):
                period = time[zero_crossings[i+2]] - time[zero_crossings[i]]
                if period > 0:
                    periods.append(period)
            
            if periods:
                avg_period = np.mean(periods)
                frequency = 1.0 / avg_period
                print(f"\nFrequency Analysis:")
                print(f"  Period: {avg_period*1000:.3f} ms")
                print(f"  Frequency: {frequency:.3f} Hz")
        
        # Detect waveform shape characteristics
        print(f"\nWaveform Shape Analysis:")
        
        # Check for DC offset
        if abs(vavg) > 0.1 * vpp and vpp > 0:
            print(f"  DC Offset detected: {vavg:.3f} V")
        
        # Calculate rise/fall times if it looks like a pulse
        threshold_low = vmin + 0.1 * vpp
        threshold_high = vmax - 0.1 * vpp
        
        rising_edges = []
        falling_edges = []
        
        for i in range(1, len(voltage)):
            if voltage[i-1] < threshold_low and voltage[i] > threshold_low:
                rising_edges.append(i)
            elif voltage[i-1] > threshold_high and voltage[i] < threshold_high:
                falling_edges.append(i)
        
        if rising_edges and falling_edges:
            print(f"  Rising edges detected: {len(rising_edges)}")
            print(f"  Falling edges detected: {len(falling_edges)}")
        
        # Check for noise
        if len(voltage) > 100:
            noise_estimate = np.std(voltage[0:100])  # Use first part for noise
            snr = vpp / (2 * noise_estimate) if noise_estimate > 0 else float('inf')
            if snr < 10:
                print(f"  High noise level detected (SNR: {snr:.1f})")
        
        # Identify waveform type
        if vpp < 0.01:
            print("  Appears to be: No signal or very weak signal")
        elif len(rising_edges) > 0 and len(falling_edges) > 0:
            duty_cycle_estimates = []
            for i in range(min(len(rising_edges), len(falling_edges))):
                if i < len(falling_edges) and falling_edges[i] > rising_edges[i]:
                    high_time = time[falling_edges[i]] - time[rising_edges[i]]
                    if i+1 < len(rising_edges):
                        period = time[rising_edges[i+1]] - time[rising_edges[i]]
                        if period > 0:
                            duty = high_time / period * 100
                            duty_cycle_estimates.append(duty)
            
            if duty_cycle_estimates:
                avg_duty = np.mean(duty_cycle_estimates)
                if 45 < avg_duty < 55:
                    print("  Appears to be: Square wave")
                else:
                    print(f"  Appears to be: Pulse wave (duty cycle ~{avg_duty:.1f}%)")
        
        # Check for exponential decay (RC circuit behavior)
        if vpp > 0.1:
            # Look for exponential characteristics
            peak_indices = []
            for i in range(1, len(voltage)-1):
                if voltage[i] > voltage[i-1] and voltage[i] > voltage[i+1]:
                    if voltage[i] > vavg + 0.3*vpp:
                        peak_indices.append(i)
            
            if len(peak_indices) > 1:
                # Check decay after first peak
                start_idx = peak_indices[0]
                end_idx = min(start_idx + 1000, len(voltage))
                decay_segment = voltage[start_idx:end_idx]
                
                if len(decay_segment) > 10:
                    # Simple exponential check: voltage should decrease monotonically
                    decreasing = sum(np.diff(decay_segment) < 0) / len(decay_segment)
                    if decreasing > 0.8:
                        print("  Possible exponential decay detected (RC circuit?)")

# Create plot
print("\n=== Generating Plot ===")
plt.figure(figsize=(12, 8))
plt.style.use('dark_background')

for ch in channels_active:
    if ch in waveform_data:
        plt.plot(time_data[ch]*1000, waveform_data[ch], 
                label=f'Channel {ch}', linewidth=2)

plt.xlabel('Time (ms)')
plt.ylabel('Voltage (V)')
plt.title('Captured Waveform Analysis')
plt.grid(True, alpha=0.3)
plt.legend()

plot_file = f'waveform_analysis_{timestamp}.png'
plt.savefig(plot_file, dpi=150, bbox_inches='tight')
print(f"Plot saved: {plot_file}")

# Close connection
scope.close()
rm.close()

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)
print(f"\nFiles created:")
print(f"  1. {screenshot_file} - Oscilloscope display")
print(f"  2. {plot_file} - Waveform analysis plot")