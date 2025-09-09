#!/usr/bin/env python3
"""Quick test script to verify Rigol oscilloscope connection"""

import pyvisa
import sys

print("=" * 60)
print("Rigol DS1104Z Plus Connection Test")
print("=" * 60)

# Test PyVISA installation
try:
    rm = pyvisa.ResourceManager('@py')
    print("✓ PyVISA-py backend loaded successfully")
except Exception as e:
    print(f"✗ Failed to load PyVISA: {e}")
    sys.exit(1)

# Get IP address
ip = input("\nEnter oscilloscope IP address (or press Enter to skip): ").strip()

if ip:
    try:
        # Try to connect
        visa_address = f'TCPIP::{ip}::INSTR'
        print(f"\nConnecting to {ip}...")
        
        scope = rm.open_resource(visa_address)
        scope.timeout = 5000
        
        # Query IDN
        idn = scope.query('*IDN?')
        print(f"✓ Connection successful!")
        print(f"Device: {idn.strip()}")
        
        # Close connection
        scope.close()
        
        print("\n" + "=" * 60)
        print("SUCCESS! Your oscilloscope is ready.")
        print("Run: python3 rigol_oscilloscope_control.py")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check oscilloscope IP (Utility → I/O → LAN)")
        print("2. Verify network connectivity (ping the IP)")
        print("3. Ensure oscilloscope LAN is enabled")
else:
    print("\nSkipping connection test.")
    print("To run the main script: python3 rigol_oscilloscope_control.py")

rm.close()