#!/usr/bin/env python3
"""
Quick zoom control for XY display
Usage: python3 zoom.py [in|out|fit|1|2|5]
"""

import warnings
warnings.filterwarnings('ignore', message='Unable to import Axes3D.*', category=UserWarning)

from rigol_oscilloscope_control import RigolDS1104Z
import config
import sys

def set_zoom(command='fit'):
    scope_ctrl = RigolDS1104Z(config.RIGOL_IP)
    if not scope_ctrl.connect():
        return
    
    scope = scope_ctrl.scope
    
    # Get current scale
    current = float(scope.query(':CHANnel1:SCALe?'))
    
    if command == 'in':
        # Zoom in (smaller scale)
        scales = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5]
        idx = min(range(len(scales)), key=lambda i: abs(scales[i] - current))
        if idx > 0:
            new_scale = scales[idx - 1]
        else:
            new_scale = current
            
    elif command == 'out':
        # Zoom out (larger scale)
        scales = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5]
        idx = min(range(len(scales)), key=lambda i: abs(scales[i] - current))
        if idx < len(scales) - 1:
            new_scale = scales[idx + 1]
        else:
            new_scale = current
            
    elif command.replace('.', '').isdigit():
        # Direct scale value
        new_scale = float(command)
        
    else:  # fit
        # Auto-fit based on measurements
        vpp1 = scope_ctrl.get_measurement(1, 'VPP')
        vpp2 = scope_ctrl.get_measurement(2, 'VPP')
        
        if vpp1 and vpp1 < 9e37:
            scale1 = vpp1 / 6.4
        else:
            scale1 = 0.5
            
        if vpp2 and vpp2 < 9e37:
            scale2 = vpp2 / 6.4
        else:
            scale2 = 0.5
            
        new_scale = max(scale1, scale2)
        
        # Round to standard value
        scales = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5]
        new_scale = min(scales, key=lambda x: abs(x - new_scale))
    
    # Apply new scale to both channels
    scope.write(f':CHANnel1:SCALe {new_scale}')
    scope.write(f':CHANnel2:SCALe {new_scale}')
    
    print(f"Scale: {current} → {new_scale} V/div")
    
    # Calculate screen usage
    vpp1 = scope_ctrl.get_measurement(1, 'VPP')
    vpp2 = scope_ctrl.get_measurement(2, 'VPP')
    
    if vpp1 and vpp1 < 9e37:
        usage = (vpp1 / (new_scale * 8)) * 100
        print(f"Pattern uses ~{usage:.0f}% of screen")
    
    scope.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        set_zoom(sys.argv[1])
    else:
        print("Usage: python3 zoom.py [in|out|fit|0.1|0.5|1]")
        print("  in   - zoom in")
        print("  out  - zoom out") 
        print("  fit  - auto-fit to screen")
        print("  0.1  - set scale to 0.1 V/div")
        set_zoom('fit')