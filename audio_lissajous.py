#!/usr/bin/env python3
"""
Audio Lissajous Generator - Interactive Mode
Generate Lissajous patterns through sound card
"""

import numpy as np
import sounddevice as sd
import time
from rigol_oscilloscope_control import RigolDS1104Z
from lissajous_xy_mode import LissajousXYAnalyzer
import config

print("🎵 AUDIO LISSAJOUS PATTERN GENERATOR")
print("="*50)

# Connect to scope
print(f"Connecting to oscilloscope at {config.RIGOL_IP}...")
scope_ctrl = RigolDS1104Z(config.RIGOL_IP)
if not scope_ctrl.connect():
    print("Failed to connect!")
    exit(1)

scope = scope_ctrl.scope
analyzer = LissajousXYAnalyzer(scope)

# Configure scope for audio
print("\n📋 Setting up oscilloscope for audio...")
scope.write(':CHANnel1:DISPlay ON')
scope.write(':CHANnel1:COUPling AC')
scope.write(':CHANnel1:SCALe 0.5')
scope.write(':CHANnel1:OFFSet 0')

scope.write(':CHANnel2:DISPlay ON')
scope.write(':CHANnel2:COUPling AC')
scope.write(':CHANnel2:SCALe 0.5')
scope.write(':CHANnel2:OFFSet 0')

# Enable XY mode
print("Enabling XY mode...")
analyzer.enable_xy_mode()

print("\n✅ Setup complete!")
print("\n🔌 CONNECTIONS:")
print("  LEFT channel (3.5mm) → CH1 (BNC)")
print("  RIGHT channel (3.5mm) → CH2 (BNC)")
print("  Ground → Ground")

# Generate test patterns
sample_rate = 48000
duration = 10  # seconds

patterns = [
    {'name': 'Circle (1:1 @ 90°)', 'freq_x': 440, 'freq_y': 440, 'phase': np.pi/2},
    {'name': 'Figure-8 (2:1)', 'freq_x': 880, 'freq_y': 440, 'phase': 0},
    {'name': 'Perfect Fifth (3:2)', 'freq_x': 660, 'freq_y': 440, 'phase': 0},
    {'name': 'Perfect Fourth (4:3)', 'freq_x': 586.67, 'freq_y': 440, 'phase': 0},
    {'name': 'Major Third (5:4)', 'freq_x': 550, 'freq_y': 440, 'phase': np.pi/4},
]

for i, pattern in enumerate(patterns, 1):
    print(f"\n[{i}/{len(patterns)}] Generating: {pattern['name']}")
    print(f"    X: {pattern['freq_x']:.1f} Hz, Y: {pattern['freq_y']:.1f} Hz")
    
    # Generate stereo signal
    t = np.linspace(0, duration, int(sample_rate * duration))
    left = 0.8 * np.sin(2 * np.pi * pattern['freq_x'] * t + pattern['phase'])
    right = 0.8 * np.sin(2 * np.pi * pattern['freq_y'] * t)
    
    stereo = np.column_stack((left, right))
    
    print(f"    Playing for {duration} seconds...")
    sd.play(stereo, sample_rate)
    
    # Wait a bit for pattern to stabilize
    time.sleep(2)
    
    # Capture and analyze
    print("    Capturing pattern...")
    x_data, y_data = analyzer.capture_xy_data()
    
    if x_data is not None:
        pattern_analysis = analyzer.analyze_pattern(x_data, y_data)
        ratio_x, ratio_y = pattern_analysis.get_simplified_ratio()
        print(f"    ✅ Detected: {ratio_x}:{ratio_y} @ {np.degrees(pattern_analysis.phase):.0f}°")
    
    sd.wait()  # Wait for playback to finish
    print("    Done!")
    
    time.sleep(1)

print("\n🎵 Demo complete!")
print("Returning to YT mode...")
analyzer.disable_xy_mode()
scope.close()

print("\nTo generate custom patterns, edit the 'patterns' list in this script!")