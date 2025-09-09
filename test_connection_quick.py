#!/usr/bin/env python3
"""Quick connection test for Rigol DS1104Z Plus at new IP"""

import pyvisa

print("Testing connection to Rigol DS1104Z Plus at 192.168.68.73...")

try:
    rm = pyvisa.ResourceManager('@py')
    scope = rm.open_resource('TCPIP::192.168.68.73::INSTR')
    scope.timeout = 5000
    
    # Query identity
    idn = scope.query('*IDN?').strip()
    print(f"✓ Connected successfully!")
    print(f"Device: {idn}")
    
    # Get some basic info
    ch1_scale = scope.query(':CHANnel1:SCALe?').strip()
    timebase = scope.query(':TIMebase:MAIN:SCALe?').strip()
    
    print(f"\nCurrent settings:")
    print(f"  CH1 Scale: {ch1_scale} V/div")
    print(f"  Timebase: {timebase} s/div")
    
    scope.close()
    rm.close()
    print("\n✓ Connection test completed successfully!")
    
except Exception as e:
    print(f"✗ Connection failed: {e}")