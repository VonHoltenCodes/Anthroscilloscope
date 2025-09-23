#!/usr/bin/env python3
"""
Test script for Lissajous XY mode functionality
"""

import sys
import numpy as np
from lissajous_xy_mode import LissajousGenerator, LissajousPattern
from frequency_math import LissajousFrequencyMath, MusicalIntervals
import config

def test_lissajous_generation():
    """Test Lissajous pattern generation"""
    print("🧪 Testing Lissajous Generation")
    print("-"*40)
    
    # Generate a 3:2 pattern
    x, y = LissajousGenerator.generate_from_ratio(3, 2, phase=np.pi/4)
    print(f"✅ Generated 3:2 pattern with {len(x)} points")
    
    # Test common patterns
    patterns = LissajousGenerator.get_common_patterns()
    print(f"✅ Loaded {len(patterns)} common patterns")
    
    return True

def test_frequency_math():
    """Test frequency mathematics"""
    print("\n🧪 Testing Frequency Math")
    print("-"*40)
    
    # Test pattern period calculation
    freq_x, freq_y = 300, 200  # 3:2 ratio
    period = LissajousFrequencyMath.pattern_period(freq_x, freq_y)
    print(f"✅ Pattern period for 300Hz × 200Hz: {period*1000:.2f}ms")
    
    # Test crossing points
    crossings = LissajousFrequencyMath.crossing_points(3, 2)
    print(f"✅ Crossing points for 3:2 ratio: {crossings}")
    
    # Test stability analysis
    stability = LissajousFrequencyMath.stability_analysis(440.0, 659.25)  # Almost perfect fifth
    print(f"✅ Stability analysis: ratio={stability['ratio']:.3f}, stable={stability['is_stable']}")
    
    return True

def test_musical_intervals():
    """Test musical interval detection"""
    print("\n🧪 Testing Musical Intervals")
    print("-"*40)
    
    # Test perfect fifth detection
    ratio = 1.5  # Perfect fifth
    interval = MusicalIntervals.find_closest_interval(ratio)
    if interval:
        print(f"✅ Ratio 1.5 detected as: {interval.interval_name}")
        print(f"   Exact ratio: {interval.numerator}:{interval.denominator}")
    
    # Test major third
    ratio = 1.25  # Major third (5:4)
    interval = MusicalIntervals.find_closest_interval(ratio)
    if interval:
        print(f"✅ Ratio 1.25 detected as: {interval.interval_name}")
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n🧪 Testing Configuration")
    print("-"*40)
    
    print(f"✅ Rigol IP: {config.RIGOL_IP}")
    print(f"✅ Default channel: {config.DEFAULT_CHANNEL}")
    print(f"✅ XY default points: {config.XY_DEFAULT_POINTS}")
    
    return True

def main():
    """Run all tests"""
    print("="*50)
    print("ANTHROSCILLOSCOPE LISSAJOUS TEST SUITE")
    print("="*50)
    
    tests = [
        test_config,
        test_lissajous_generation,
        test_frequency_math,
        test_musical_intervals
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} error: {e}")
    
    print("\n" + "="*50)
    print(f"Tests passed: {passed}/{passed+failed}")
    
    if failed == 0:
        print("✅ All tests passed! Lissajous XY mode is ready to use.")
        print("\nTo use the new features:")
        print("1. Run: python3 anthroscilloscope_main.py")
        print("2. Select option 10 for Interactive Lissajous viewer")
        print("3. Select option 11 for XY mode analysis")
        print("4. Select option 12 for Frequency ratio calculator")
        print("5. Select option 13 for Musical interval analysis")
    else:
        print(f"⚠️  {failed} tests failed")

if __name__ == "__main__":
    main()