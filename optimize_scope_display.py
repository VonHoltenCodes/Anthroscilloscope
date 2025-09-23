#!/usr/bin/env python3
"""
Optimize Oscilloscope Display for Clean Lissajous Patterns
"""

from rigol_oscilloscope_control import RigolDS1104Z
import config
import time

print("🔧 OSCILLOSCOPE DISPLAY OPTIMIZER")
print("="*50)

# Connect
scope_ctrl = RigolDS1104Z(config.RIGOL_IP)
if not scope_ctrl.connect():
    print("Failed to connect!")
    exit(1)

scope = scope_ctrl.scope
print("✅ Connected to oscilloscope")

print("\n📊 Applying optimizations for clean Lissajous patterns...")

# Step 1: Channel setup
print("\n1️⃣ Configuring channels...")
for ch in [1, 2]:
    scope.write(f':CHANnel{ch}:DISPlay ON')
    scope.write(f':CHANnel{ch}:COUPling AC')   # AC for audio
    scope.write(f':CHANnel{ch}:SCALe 0.5')     # 0.5V/div standard
    scope.write(f':CHANnel{ch}:OFFSet 0')      # Center
    scope.write(f':CHANnel{ch}:BWLimit 20M')   # Reduce noise
    scope.write(f':CHANnel{ch}:INVert OFF')
    scope.write(f':CHANnel{ch}:PROBe 1')       # 1x probe
print("✅ Channels configured")

# Step 2: Acquisition mode
print("\n2️⃣ Setting acquisition mode...")
scope.write(':ACQuire:TYPE AVERages')  # Average to reduce noise
scope.write(':ACQuire:AVERages 4')     # 4x averaging (adjustable)
print("✅ Averaging enabled (4x)")

# Step 3: Display settings  
print("\n3️⃣ Optimizing display...")
scope.write(':DISPlay:TYPE VECTors')       # Connected dots
scope.write(':DISPlay:PERSistence 0.1')    # Short persistence
scope.write(':DISPlay:GRADing:TIME 0.05')  # Fast decay
scope.write(':DISPlay:WBRightness 60')     # Medium brightness
print("✅ Display optimized")

# Step 4: XY Mode
print("\n4️⃣ Enabling XY mode...")
scope.write(':TIMebase:MODE XY')
print("✅ XY mode active")

# Step 5: Fine adjustments
print("\n5️⃣ Fine-tuning...")
scope.write(':TRIGger:MODE AUTO')  # Auto trigger
scope.write(':RUN')  # Ensure running
print("✅ Trigger set to AUTO")

# Check current settings
print("\n📋 Current Settings:")
for ch in [1, 2]:
    scale = scope.query(f':CHANnel{ch}:SCALe?').strip()
    coupling = scope.query(f':CHANnel{ch}:COUPling?').strip()
    bw = scope.query(f':CHANnel{ch}:BWLimit?').strip()
    print(f"  CH{ch}: {scale}V/div, {coupling} coupling, BW limit: {bw}")

acq_type = scope.query(':ACQuire:TYPE?').strip()
avg_count = scope.query(':ACQuire:AVERages?').strip()
print(f"  Acquisition: {acq_type} mode, {avg_count} averages")

mode = scope.query(':TIMebase:MODE?').strip()
print(f"  Display mode: {mode}")

print("\n💡 MANUAL ADJUSTMENTS:")
print("• If still fuzzy, try:")
print("  1. Press ACQUIRE button")
print("  2. Select Average → adjust count (2, 4, 8, 16)")
print("  3. Higher averaging = cleaner but slower response")
print("\n• For brightness:")
print("  1. Press DISPLAY button")
print("  2. Adjust Intensity (waveform brightness)")
print("  3. Adjust Grid brightness separately")
print("\n• Quick improvements:")
print("  - Press AUTO to auto-scale")
print("  - Adjust vertical POSITION knobs to center")
print("  - Use HORIZONTAL position to center pattern")

# Keep connection open for manual testing
print("\n✅ Optimization complete!")
print("🎵 Play audio through Sound Blaster to see patterns")
print("Press Ctrl+C to exit and close connection")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\nClosing connection...")
    scope.close()
    print("Done!")