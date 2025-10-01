#!/usr/bin/env python3
"""
Quick non-interactive test of text rendering system
"""

from text_rendering.lissajous_text_renderer import LissajousTextRenderer
import matplotlib.pyplot as plt

def main():
    """Quick test without interactive plots"""
    print("=" * 70)
    print("TEXT RENDERING QUICK TEST")
    print("=" * 70)

    renderer = LissajousTextRenderer()

    # Test 1: Single letter
    print("\nTest 1: Letter 'I'")
    stats = renderer.get_text_stats("I")
    print(f"  ✅ Strokes: {stats['stroke_count']}, Points: {stats['total_points']}")

    # Test 2: Word HELLO
    print("\nTest 2: Word 'HELLO'")
    stats = renderer.get_text_stats("HELLO")
    print(f"  ✅ Strokes: {stats['stroke_count']}, Points: {stats['total_points']}")

    # Test 3: Get available chars
    print(f"\nAvailable characters: {renderer.available_characters()}")

    # Test 4: Generate audio
    print("\nTest 4: Generate audio for 'HELLO'")
    left, right = renderer.render_text("HELLO", duration=0.5, loop_count=1)
    print(f"  ✅ Audio samples: {len(left)} (left), {len(right)} (right)")

    # Test 5: Save to file
    print("\nTest 5: Save 'HELLO' to WAV file")
    renderer.save_text_audio("HELLO", "hello_test.wav", duration=0.5, loop_count=30)

    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)

if __name__ == '__main__':
    main()
