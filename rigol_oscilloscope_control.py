#!/usr/bin/env python3
"""
Rigol DS1104Z Plus Oscilloscope Control Script
Connects to oscilloscope via Ethernet for waveform viewing and screenshot capture
Compatible with Linux using pyvisa-py backend (no NI-VISA required)
"""

import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pyvisa
from datetime import datetime

class RigolDS1104Z:
    """Class to control Rigol DS1104Z Plus oscilloscope over Ethernet"""
    
    def __init__(self, ip_address):
        """
        Initialize connection to oscilloscope
        
        Args:
            ip_address: IP address of the oscilloscope (e.g., '192.168.1.100')
        """
        self.ip_address = ip_address
        self.scope = None
        self.rm = None
        
    def connect(self):
        """Establish connection to the oscilloscope"""
        try:
            # Use pyvisa-py backend for Linux compatibility (no NI-VISA needed)
            self.rm = pyvisa.ResourceManager('@py')
            
            # Connect via TCP/IP using VISA resource string format
            visa_address = f'TCPIP::{self.ip_address}::INSTR'
            print(f"Connecting to oscilloscope at {self.ip_address}...")
            
            self.scope = self.rm.open_resource(visa_address)
            self.scope.timeout = 5000  # 5 second timeout
            
            # Query IDN to verify connection
            idn = self.scope.query('*IDN?')
            print(f"Connected successfully!")
            print(f"Device: {idn.strip()}")
            
            # Clear status and reset to known state
            self.scope.write('*CLS')
            
            return True
            
        except pyvisa.errors.VisaIOError as e:
            print(f"Connection failed: {e}")
            print("Please verify:")
            print("  1. Oscilloscope IP address is correct")
            print("  2. Oscilloscope is on the same network")
            print("  3. LAN/DHCP is enabled on the oscilloscope (Utility -> IO -> LAN)")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    
    def get_waveform_data(self, channel=1):
        """
        Fetch waveform data from specified channel
        
        Args:
            channel: Channel number (1-4)
            
        Returns:
            tuple: (time_data, voltage_data) as numpy arrays
        """
        try:
            # Set waveform source to specified channel
            self.scope.write(f':WAVeform:SOURce CHANnel{channel}')
            
            # Set waveform mode to normal
            self.scope.write(':WAVeform:MODE NORMal')
            
            # Set return format to byte
            self.scope.write(':WAVeform:FORMat BYTE')
            
            # Get waveform preamble for scaling information
            preamble = self.scope.query(':WAVeform:PREamble?').strip().split(',')
            
            # Extract scaling parameters from preamble
            # Format: format, type, points, count, xincrement, xorigin, xreference, yincrement, yorigin, yreference
            points = int(float(preamble[2]))
            x_increment = float(preamble[4])  # Time between samples
            x_origin = float(preamble[5])     # Time of first sample
            x_reference = float(preamble[6])  # Reference time
            y_increment = float(preamble[7])  # Voltage scale
            y_origin = float(preamble[8])     # Voltage offset
            y_reference = float(preamble[9])  # Reference voltage (usually 127 for byte format)
            
            # Request waveform data
            self.scope.write(':WAVeform:DATA?')
            
            # Read raw data (binary block format)
            raw_data = self.scope.read_raw()
            
            # Parse IEEE 488.2 binary block header
            # Format: #NXXXXXXX where N is number of digits in XXXXXXX (data length)
            header_start = raw_data.find(b'#')
            if header_start == -1:
                raise ValueError("Invalid waveform data format")
            
            n_length_bytes = int(chr(raw_data[header_start + 1]))
            data_length = int(raw_data[header_start + 2:header_start + 2 + n_length_bytes])
            data_start = header_start + 2 + n_length_bytes
            
            # Extract waveform bytes
            waveform_bytes = raw_data[data_start:data_start + data_length]
            
            # Convert bytes to voltage values
            waveform_data = np.frombuffer(waveform_bytes, dtype=np.uint8)
            
            # Apply scaling to get actual voltage values
            voltage_data = ((waveform_data - y_reference) * y_increment) + y_origin
            
            # Generate time axis
            time_data = np.arange(len(voltage_data)) * x_increment + x_origin
            
            # Get channel status for display
            channel_enabled = self.scope.query(f':CHANnel{channel}:DISPlay?').strip()
            if channel_enabled == '0':
                print(f"Warning: Channel {channel} is disabled on oscilloscope display")
            
            return time_data, voltage_data
            
        except Exception as e:
            print(f"Error fetching waveform data: {e}")
            return None, None
    
    def save_screenshot(self, filename=None):
        """
        Capture and save oscilloscope display screenshot
        
        Args:
            filename: Output filename (default: rigol_screenshot_YYYYMMDD_HHMMSS.png)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"rigol_screenshot_{timestamp}.png"
            
            print(f"Capturing screenshot...")
            
            # Set display data format to PNG
            self.scope.write(':DISPlay:DATA? ON,0,PNG')
            
            # Read screenshot data (binary block format)
            raw_data = self.scope.read_raw()
            
            # Parse IEEE 488.2 binary block header
            header_start = raw_data.find(b'#')
            if header_start == -1:
                raise ValueError("Invalid screenshot data format")
            
            n_length_bytes = int(chr(raw_data[header_start + 1]))
            data_length = int(raw_data[header_start + 2:header_start + 2 + n_length_bytes])
            data_start = header_start + 2 + n_length_bytes
            
            # Extract PNG data
            png_data = raw_data[data_start:data_start + data_length]
            
            # Save to file
            with open(filename, 'wb') as f:
                f.write(png_data)
            
            print(f"Screenshot saved to: {filename}")
            return True
            
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            return False
    
    def get_measurement(self, channel, measurement_type):
        """
        Get specific measurement from channel
        
        Args:
            channel: Channel number (1-4)
            measurement_type: Type of measurement (e.g., 'VPP', 'VAVG', 'FREQ', 'PERiod')
            
        Returns:
            float: Measurement value or None if error
        """
        try:
            result = self.scope.query(f':MEASure:ITEM? {measurement_type},CHANnel{channel}')
            return float(result)
        except Exception as e:
            print(f"Error getting measurement: {e}")
            return None
    
    def plot_waveform(self, channel=1, continuous=False):
        """
        Plot waveform data from specified channel
        
        Args:
            channel: Channel number (1-4)
            continuous: If True, continuously update plot (live view)
        """
        if continuous:
            # Set up live plot
            fig, ax = plt.subplots(figsize=(10, 6))
            line, = ax.plot([], [], 'b-', linewidth=1)
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Voltage (V)')
            ax.set_title(f'Rigol DS1104Z - Channel {channel} (Live)')
            ax.grid(True, alpha=0.3)
            
            def update_plot(frame):
                """Update function for animation"""
                time_data, voltage_data = self.get_waveform_data(channel)
                if time_data is not None and voltage_data is not None:
                    line.set_data(time_data, voltage_data)
                    ax.relim()
                    ax.autoscale_view()
                    
                    # Get and display measurements
                    vpp = self.get_measurement(channel, 'VPP')
                    freq = self.get_measurement(channel, 'FREQ')
                    if vpp and freq:
                        ax.set_title(f'Channel {channel} - Vpp: {vpp:.3f}V, Freq: {freq/1000:.3f}kHz')
                return line,
            
            # Create animation (update every 500ms)
            ani = FuncAnimation(fig, update_plot, interval=500, blit=True)
            plt.show()
            
        else:
            # Single shot plot
            time_data, voltage_data = self.get_waveform_data(channel)
            
            if time_data is None or voltage_data is None:
                print("Failed to retrieve waveform data")
                return
            
            # Create plot
            plt.figure(figsize=(10, 6))
            plt.plot(time_data, voltage_data, 'b-', linewidth=1)
            plt.xlabel('Time (s)')
            plt.ylabel('Voltage (V)')
            plt.title(f'Rigol DS1104Z - Channel {channel}')
            plt.grid(True, alpha=0.3)
            
            # Add measurements to plot
            vpp = self.get_measurement(channel, 'VPP')
            vavg = self.get_measurement(channel, 'VAVG')
            freq = self.get_measurement(channel, 'FREQ')
            
            info_text = []
            if vpp: info_text.append(f'Vpp: {vpp:.3f}V')
            if vavg: info_text.append(f'Vavg: {vavg:.3f}V')
            if freq: info_text.append(f'Freq: {freq/1000:.3f}kHz')
            
            if info_text:
                plt.text(0.02, 0.98, '\n'.join(info_text), 
                        transform=plt.gca().transAxes,
                        verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            plt.tight_layout()
            plt.show()
    
    def close(self):
        """Close connection to oscilloscope"""
        if self.scope:
            self.scope.close()
        if self.rm:
            self.rm.close()
        print("Connection closed")


def main():
    """Main function with interactive menu"""
    print("=" * 60)
    print("Rigol DS1104Z Plus Oscilloscope Control")
    print("=" * 60)
    
    # Get IP address from user
    ip_address = input("Enter oscilloscope IP address (e.g., 192.168.1.100): ").strip()
    
    if not ip_address:
        ip_address = "192.168.1.100"  # Default IP
        print(f"Using default IP: {ip_address}")
    
    # Create oscilloscope instance and connect
    scope = RigolDS1104Z(ip_address)
    
    if not scope.connect():
        sys.exit(1)
    
    try:
        while True:
            print("\n" + "=" * 40)
            print("Options:")
            print("1. Plot single waveform capture")
            print("2. Start live waveform view")
            print("3. Save screenshot")
            print("4. Get measurements")
            print("5. Exit")
            print("=" * 40)
            
            choice = input("Select option (1-5): ").strip()
            
            if choice == '1':
                channel = input("Enter channel number (1-4) [1]: ").strip()
                channel = int(channel) if channel else 1
                print(f"Capturing waveform from channel {channel}...")
                scope.plot_waveform(channel, continuous=False)
                
            elif choice == '2':
                channel = input("Enter channel number (1-4) [1]: ").strip()
                channel = int(channel) if channel else 1
                print(f"Starting live view of channel {channel}...")
                print("Close plot window to return to menu")
                scope.plot_waveform(channel, continuous=True)
                
            elif choice == '3':
                filename = input("Enter filename (or press Enter for auto): ").strip()
                filename = filename if filename else None
                scope.save_screenshot(filename)
                
            elif choice == '4':
                channel = input("Enter channel number (1-4) [1]: ").strip()
                channel = int(channel) if channel else 1
                print(f"\nMeasurements for Channel {channel}:")
                print("-" * 30)
                
                measurements = [
                    ('Vpp', 'VPP'),
                    ('Vmax', 'VMAX'),
                    ('Vmin', 'VMIN'),
                    ('Vavg', 'VAVG'),
                    ('Vrms', 'VRMS'),
                    ('Frequency', 'FREQ'),
                    ('Period', 'PERiod'),
                ]
                
                for name, cmd in measurements:
                    value = scope.get_measurement(channel, cmd)
                    if value:
                        if 'FREQ' in cmd:
                            print(f"{name}: {value/1000:.3f} kHz")
                        elif 'PER' in cmd:
                            print(f"{name}: {value*1000:.3f} ms")
                        else:
                            print(f"{name}: {value:.3f} V")
                
            elif choice == '5':
                print("Exiting...")
                break
                
            else:
                print("Invalid option. Please try again.")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        scope.close()


if __name__ == "__main__":
    main()