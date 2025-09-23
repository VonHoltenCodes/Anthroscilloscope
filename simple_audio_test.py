#!/usr/bin/env python3
"""
Simple Audio Lissajous Test
Direct audio generation test with minimal scope interaction
"""

import numpy as np
import sounddevice as sd
import time

print("🔊 SIMPLE AUDIO LISSAJOUS TEST")
print("="*50)

# List audio devices
print("\n📢 Audio devices:")
devices = sd.query_devices()
for i, dev in enumerate(devices):
    if 'output' in str(dev).lower():
        print(f"  [{i}] {dev['name']} ({dev['max_output_channels']} ch)")

# Audio parameters
sample_rate = 48000
amplitude = 0.5  # Conservative amplitude

print(f"\n🎵 Using sample rate: {sample_rate} Hz")
print(f"📊 Amplitude: {amplitude * 100}%")

# Test patterns
patterns = [
    {"name": "Test Tone (440Hz both)", "freq_l": 440, "freq_r": 440, "phase": 0},
    {"name": "Circle Pattern", "freq_l": 440, "freq_r": 440, "phase": np.pi/2},
    {"name": "Octave (2:1)", "freq_l": 880, "freq_r": 440, "phase": 0},
    {"name": "Perfect Fifth (3:2)", "freq_l": 660, "freq_r": 440, "phase": 0},
    {"name": "Perfect Fourth (4:3)", "freq_l": 586.67, "freq_r": 440, "phase": 0},
    {"name": "Major Third (5:4)", "freq_l": 550, "freq_r": 440, "phase": 0},
    {"name": "Minor Third (6:5)", "freq_l": 528, "freq_r": 440, "phase": 0},
    {"name": "Major Second (9:8)", "freq_l": 495, "freq_r": 440, "phase": 0},
]

print("\n🔌 SETUP INSTRUCTIONS:")
print("1. Connect Sound Blaster LEFT output → Oscilloscope CH1")
print("2. Connect Sound Blaster RIGHT output → Oscilloscope CH2")
print("3. Set oscilloscope to XY mode manually:")
print("   - Press MENU → Horizontal → Time Base → XY")
print("   - Or press HORIZ → Mode → XY")
print("4. Set both channels to 0.5V/div, AC coupling")
print("\n📊 Starting audio test in 3 seconds...")
time.sleep(3)

def generate_stereo_tone(freq_left, freq_right, phase, duration=3):
    """Generate stereo tone with specified frequencies and phase"""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, endpoint=False)
    
    # Generate signals
    left = amplitude * np.sin(2 * np.pi * freq_left * t)
    right = amplitude * np.sin(2 * np.pi * freq_right * t + phase)
    
    # Add fade in/out to prevent pops
    fade_len = int(0.01 * sample_rate)  # 10ms
    fade_in = np.linspace(0, 1, fade_len)
    fade_out = np.linspace(1, 0, fade_len)
    
    left[:fade_len] *= fade_in
    left[-fade_len:] *= fade_out
    right[:fade_len] *= fade_in
    right[-fade_len:] *= fade_out
    
    return np.column_stack((left, right))

print("\n🎨 Playing patterns:\n")

for i, pattern in enumerate(patterns, 1):
    print(f"[{i}/{len(patterns)}] {pattern['name']}")
    
    # Calculate ratio
    ratio = pattern['freq_l'] / pattern['freq_r']
    print(f"    Left: {pattern['freq_l']:.1f} Hz")
    print(f"    Right: {pattern['freq_r']:.1f} Hz")
    print(f"    Ratio: {ratio:.3f}")
    print(f"    Phase: {np.degrees(pattern['phase']):.0f}°")
    
    # Generate and play
    signal = generate_stereo_tone(
        pattern['freq_l'], 
        pattern['freq_r'], 
        pattern['phase'],
        duration=3
    )
    
    print("    ▶️  Playing...")
    sd.play(signal, sample_rate)
    sd.wait()  # Wait for playback to complete
    
    print("    ✅ Done\n")
    time.sleep(1)  # Pause between patterns

print("🏁 Test complete!")
print("\n💡 TROUBLESHOOTING:")
print("• If patterns are fuzzy:")
print("  - Reduce oscilloscope bandwidth (BW Limit → 20MHz)")
print("  - Enable averaging (Acquire → Average → 4 or 8)")
print("  - Adjust intensity/brightness")
print("  - Check cable connections")
print("\n• If no signal:")
print("  - Check system audio output is set to Sound Blaster")
print("  - Verify cable connections")
print("  - Try increasing amplitude in the script")
print("\n• For best results:")
print("  - Use shortest possible cables")
print("  - Keep audio volume at 75-85%")
print("  - Ensure good ground connection")