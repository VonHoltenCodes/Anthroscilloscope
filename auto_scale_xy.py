#!/usr/bin/env python3
"""
Auto-Scale XY Display for Perfect Lissajous View
Automatically adjusts oscilloscope scales to show the entire pattern
"""

import warnings
warnings.filterwarnings('ignore', message='Unable to import Axes3D.*', category=UserWarning)

from rigol_oscilloscope_control import RigolDS1104Z
import config
import time
import numpy as np

def auto_scale_xy():
    print("🔧 AUTO-SCALE XY DISPLAY")
    print("="*50)
    
    # Connect
    scope_ctrl = RigolDS1104Z(config.RIGOL_IP)
    if not scope_ctrl.connect():
        return
    
    scope = scope_ctrl.scope
    
    print("\n📊 Current settings:")
    
    # Get current scales
    ch1_scale = float(scope.query(':CHANnel1:SCALe?'))
    ch2_scale = float(scope.query(':CHANnel2:SCALe?'))
    ch1_offset = float(scope.query(':CHANnel1:OFFSet?'))
    ch2_offset = float(scope.query(':CHANnel2:OFFSet?'))
    
    print(f"  CH1: {ch1_scale} V/div, offset: {ch1_offset} V")
    print(f"  CH2: {ch2_scale} V/div, offset: {ch2_offset} V")
    
    # Measure peak-to-peak values
    print("\n📏 Measuring signal levels...")
    
    vpp1 = scope_ctrl.get_measurement(1, 'VPP')
    vmax1 = scope_ctrl.get_measurement(1, 'VMAX')
    vmin1 = scope_ctrl.get_measurement(1, 'VMIN')
    
    vpp2 = scope_ctrl.get_measurement(2, 'VPP')
    vmax2 = scope_ctrl.get_measurement(2, 'VMAX')
    vmin2 = scope_ctrl.get_measurement(2, 'VMIN')
    
    if vpp1 and vpp1 < 9e37:
        print(f"  CH1: {vpp1:.3f} Vpp ({vmin1:.3f} to {vmax1:.3f} V)")
    else:
        print(f"  CH1: No signal detected")
        vpp1 = ch1_scale * 6  # Use current scale as fallback
        vmax1 = ch1_scale * 3
        vmin1 = -ch1_scale * 3
    
    if vpp2 and vpp2 < 9e37:
        print(f"  CH2: {vpp2:.3f} Vpp ({vmin2:.3f} to {vmax2:.3f} V)")
    else:
        print(f"  CH2: No signal detected")
        vpp2 = ch2_scale * 6
        vmax2 = ch2_scale * 3
        vmin2 = -ch2_scale * 3
    
    print("\n🎯 Optimizing display...")
    
    # Calculate optimal scale
    # We want the signal to use about 80% of the screen (8 divisions total)
    # So ideal scale = Vpp / 6.4 (leaving some margin)
    
    optimal_scale_ch1 = vpp1 / 6.4
    optimal_scale_ch2 = vpp2 / 6.4
    
    # Round to nearest standard scale value
    standard_scales = [0.001, 0.002, 0.005,
                       0.01, 0.02, 0.05,
                       0.1, 0.2, 0.5,
                       1, 2, 5, 10]
    
    # Find closest standard scale
    scale_ch1 = min(standard_scales, key=lambda x: abs(x - optimal_scale_ch1))
    scale_ch2 = min(standard_scales, key=lambda x: abs(x - optimal_scale_ch2))
    
    # For XY mode, it often looks better if both channels have the same scale
    # Use the larger of the two for both channels to ensure nothing is cut off
    unified_scale = max(scale_ch1, scale_ch2)
    
    print(f"\n📐 Applying new settings:")
    print(f"  Optimal scale CH1: {scale_ch1} V/div")
    print(f"  Optimal scale CH2: {scale_ch2} V/div")
    print(f"  Using unified scale: {unified_scale} V/div")
    
    # Apply the new scale
    scope.write(f':CHANnel1:SCALe {unified_scale}')
    scope.write(f':CHANnel2:SCALe {unified_scale}')
    
    # Calculate and apply optimal offset to center the pattern
    center_v1 = (vmax1 + vmin1) / 2
    center_v2 = (vmax2 + vmin2) / 2
    
    # In XY mode, offset moves the pattern on screen
    # We want to center it, so set offset to negative of center
    scope.write(f':CHANnel1:OFFSet {-center_v1}')
    scope.write(f':CHANnel2:OFFSet {-center_v2}')
    
    print(f"  Centered at: ({-center_v1:.3f}, {-center_v2:.3f}) V")
    
    # Additional optimizations for clean display
    print("\n🎨 Additional optimizations:")
    
    # Set position to center
    scope.write(':CHANnel1:POSition 0')
    scope.write(':CHANnel2:POSition 0')
    
    # Ensure we're in XY mode
    current_mode = scope.query(':TIMebase:MODE?').strip()
    if current_mode != 'XY':
        scope.write(':TIMebase:MODE XY')
        print("  ✓ Switched to XY mode")
    
    # Set display parameters
    scope.write(':DISPlay:TYPE VECTors')  # Connected dots
    scope.write(':DISPlay:GRADing:TIME 0.2')  # Medium persistence
    scope.write(':DISPlay:PERSistence 0.5')   # Some persistence for smooth display
    print("  ✓ Display type: Vectors with persistence")
    
    # Acquisition settings
    scope.write(':ACQuire:TYPE AVERages')
    scope.write(':ACQuire:AVERages 4')
    print("  ✓ Averaging: 4x for cleaner display")
    
    # Grid brightness
    scope.write(':DISPlay:GRID FULl')
    scope.write(':DISPlay:GBRightness 30')  # Medium grid brightness
    print("  ✓ Grid: Full with medium brightness")
    
    print("\n✅ Auto-scaling complete!")
    
    # Final measurements
    time.sleep(0.5)
    vpp1_new = scope_ctrl.get_measurement(1, 'VPP')
    vpp2_new = scope_ctrl.get_measurement(2, 'VPP')
    
    if vpp1_new and vpp1_new < 9e37:
        screen_usage_1 = (vpp1_new / (unified_scale * 8)) * 100
        screen_usage_2 = (vpp2_new / (unified_scale * 8)) * 100
        
        print(f"\n📊 Pattern now uses:")
        print(f"  CH1: {screen_usage_1:.0f}% of screen")
        print(f"  CH2: {screen_usage_2:.0f}% of screen")
    
    print("\n💡 MANUAL ADJUSTMENTS:")
    print("  • Use HORIZONTAL POSITION knob to center X")
    print("  • Use VERTICAL POSITION knobs to center Y")
    print("  • Press DISPLAY → Intensity to adjust brightness")
    print("  • Try ACQUIRE → Average → 2, 4, 8, or 16 for preference")
    
    # Show comparison
    print("\n📋 BEFORE → AFTER:")
    print(f"  CH1 Scale: {ch1_scale} → {unified_scale} V/div")
    print(f"  CH2 Scale: {ch2_scale} → {unified_scale} V/div")
    
    scope.close()

def quick_zoom(zoom_level='fit'):
    """Quick zoom presets for XY display"""
    print(f"🔍 Quick Zoom: {zoom_level}")
    
    scope_ctrl = RigolDS1104Z(config.RIGOL_IP)
    if not scope_ctrl.connect():
        return
    
    scope = scope_ctrl.scope
    
    if zoom_level == 'fit':
        # Auto-fit to screen
        auto_scale_xy()
    
    elif zoom_level == 'zoom_in':
        # Zoom in by decreasing scale
        ch1_scale = float(scope.query(':CHANnel1:SCALe?'))
        ch2_scale = float(scope.query(':CHANnel2:SCALe?'))
        
        standard_scales = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10]
        
        # Find next smaller scale
        idx1 = min(range(len(standard_scales)), key=lambda i: abs(standard_scales[i] - ch1_scale))
        if idx1 > 0:
            new_scale = standard_scales[idx1 - 1]
            scope.write(f':CHANnel1:SCALe {new_scale}')
            scope.write(f':CHANnel2:SCALe {new_scale}')
            print(f"  Zoomed in to {new_scale} V/div")
    
    elif zoom_level == 'zoom_out':
        # Zoom out by increasing scale
        ch1_scale = float(scope.query(':CHANnel1:SCALe?'))
        
        standard_scales = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10]
        
        # Find next larger scale
        idx1 = min(range(len(standard_scales)), key=lambda i: abs(standard_scales[i] - ch1_scale))
        if idx1 < len(standard_scales) - 1:
            new_scale = standard_scales[idx1 + 1]
            scope.write(f':CHANnel1:SCALe {new_scale}')
            scope.write(f':CHANnel2:SCALe {new_scale}')
            print(f"  Zoomed out to {new_scale} V/div")
    
    scope.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'in':
            quick_zoom('zoom_in')
        elif sys.argv[1] == 'out':
            quick_zoom('zoom_out')
        else:
            auto_scale_xy()
    else:
        auto_scale_xy()