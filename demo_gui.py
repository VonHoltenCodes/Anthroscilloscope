#!/usr/bin/env python3
"""
Quick demo of the GUI with preset examples
"""

from text_gui import LissajousTextGUI
import matplotlib.pyplot as plt

def main():
    print("=" * 70)
    print("PHASE 3 DEMO: Interactive GUI")
    print("=" * 70)
    print()
    print("This demo showcases the Phase 3 Interactive UI features:")
    print()
    print("✅ Text Input Field")
    print("   - Type any text (A-Z, 0-9, punctuation)")
    print("   - Press Enter to update preview")
    print()
    print("✅ Font Size Slider")
    print("   - Range: 0.3x to 3.0x")
    print("   - Real-time preview updates")
    print()
    print("✅ Speed Control")
    print("   - Range: 0.1x to 5.0x")
    print("   - Affects audio playback duration")
    print()
    print("✅ Real-time Preview")
    print("   - Live Lissajous pattern visualization")
    print("   - Shows start (red) and end (blue) points")
    print()
    print("✅ Export to WAV")
    print("   - Saves stereo audio file")
    print("   - Ready for oscilloscope playback")
    print()
    print("✅ Save/Load Presets")
    print("   - Save current settings as JSON")
    print("   - Quick reload of favorites")
    print()
    print("=" * 70)
    print("Launching GUI...")
    print("=" * 70)
    print()

    gui = LissajousTextGUI()
    gui.show()


if __name__ == '__main__':
    main()
