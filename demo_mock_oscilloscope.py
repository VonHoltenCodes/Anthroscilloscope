#!/usr/bin/env python3
"""
Demo script showing mock oscilloscope capabilities
Displays various Lissajous patterns using the mock infrastructure
"""

import matplotlib.pyplot as plt
from core.oscilloscope_factory import create_oscilloscope
from core.signal_generators import (
    LissajousSignalGenerator,
    CircleSignalGenerator,
    Figure8SignalGenerator
)


def demo_pattern(scope, title, pattern_name):
    """Display a single pattern"""
    scope.enable_xy_mode()

    # Get waveform data
    t1, x = scope.get_waveform_data(1)
    t2, y = scope.get_waveform_data(2)

    # Plot XY pattern
    plt.figure(figsize=(8, 8))
    plt.plot(x, y, 'lime', linewidth=2)
    plt.title(f'{title}\n{pattern_name}', fontsize=14, fontweight='bold')
    plt.xlabel('X (Channel 1)', fontsize=12)
    plt.ylabel('Y (Channel 2)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.tight_layout()


def main():
    """Main demo function"""
    print("=" * 60)
    print("Mock Oscilloscope XY Mode Demo")
    print("=" * 60)
    print()

    # Pattern 1: Circle (1:1 ratio, 90° phase)
    print("Pattern 1: Circle")
    scope1 = create_oscilloscope(mock=True, signal_generator=CircleSignalGenerator())
    scope1.connect()
    demo_pattern(scope1, "Circle", "1:1 ratio, 90° phase")

    # Pattern 2: Figure-8 (2:1 ratio)
    print("Pattern 2: Figure-8")
    scope2 = create_oscilloscope(mock=True, signal_generator=Figure8SignalGenerator())
    scope2.connect()
    demo_pattern(scope2, "Figure-8", "2:1 ratio")

    # Pattern 3: Lissajous 3:2
    print("Pattern 3: Lissajous 3:2")
    scope3 = create_oscilloscope(mock=True, signal_generator=LissajousSignalGenerator(3, 2, 0))
    scope3.connect()
    demo_pattern(scope3, "Lissajous 3:2", "3:2 ratio, 0° phase")

    # Pattern 4: Lissajous 5:4 with phase
    print("Pattern 4: Lissajous 5:4")
    import numpy as np
    scope4 = create_oscilloscope(mock=True, signal_generator=LissajousSignalGenerator(5, 4, np.pi/4))
    scope4.connect()
    demo_pattern(scope4, "Lissajous 5:4", "5:4 ratio, 45° phase")

    print()
    print("✅ All patterns generated successfully!")
    print("Close the plot windows to exit...")
    plt.show()


if __name__ == '__main__':
    main()
