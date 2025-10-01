#!/usr/bin/env python3
"""
Demo script for text rendering system
Tests the complete pipeline from text to oscilloscope display
"""

from text_rendering.lissajous_text_renderer import LissajousTextRenderer


def main():
    """Main demo function"""
    print("=" * 70)
    print("LISSAJOUS TEXT RENDERING SYSTEM - Demo")
    print("=" * 70)
    print()

    # Create renderer
    renderer = LissajousTextRenderer()

    # Show available characters
    print(f"Available characters: {renderer.available_characters()}")
    print()

    # Demo 1: Simple letter
    print("\n" + "=" * 70)
    print("DEMO 1: Single Letter 'I'")
    print("=" * 70)
    renderer.demo("I")

    # Demo 2: Simple word
    print("\n" + "=" * 70)
    print("DEMO 2: Word 'HELLO'")
    print("=" * 70)
    renderer.demo("HELLO")

    # Demo 3: Another word
    print("\n" + "=" * 70)
    print("DEMO 3: Word 'OSCILLATE'")
    print("=" * 70)
    # Note: Not all letters implemented yet, will show available ones
    renderer.demo("OILATE")

    print("\n" + "=" * 70)
    print("✅ Demo complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
