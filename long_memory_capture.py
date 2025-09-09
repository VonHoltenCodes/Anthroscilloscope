#!/usr/bin/env python3
"""
Long Memory Capture Module for Rigol DS1104Z Plus
Captures up to 12M points using deep memory mode
"""

import pyvisa
import numpy as np
import time
from datetime import datetime
import struct

class LongMemoryCapture:
    """Advanced memory capture for Rigol oscilloscopes"""
    
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.scope = None
        self.rm = None
        
    def connect(self):
        """Connect to oscilloscope with optimized settings for large transfers"""
        try:
            self.rm = pyvisa.ResourceManager('@py')
            visa_address = f'TCPIP::{self.ip_address}::INSTR'
            
            # Connect with larger chunk size and timeout for big transfers
            self.scope = self.rm.open_resource(
                visa_address,
                timeout=30000,  # 30 second timeout
                chunk_size=1024000  # 1MB chunks
            )
            
            # Increase termination character timeout
            self.scope.read_termination = '\n'
            self.scope.write_termination = '\n'
            
            idn = self.scope.query('*IDN?')
            print(f"Connected: {idn.strip()}")
            return True
            
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def get_memory_depth(self):
        """Query current memory depth setting"""
        try:
            # DS1104Z supports AUTO, 12k, 120k, 1.2M, 12M points
            mdepth = self.scope.query(':ACQuire:MDEPth?').strip()
            print(f"Current memory depth: {mdepth}")
            return mdepth
        except:
            return "AUTO"
    
    def set_memory_depth(self, depth='12M'):
        """
        Set memory depth
        Options: AUTO, 12k, 120k, 1.2M, 12M (for single channel)
        Note: Maximum depth depends on number of active channels
        """
        valid_depths = ['AUTO', '12k', '120k', '1.2M', '12M', '6M', '3M']
        
        if depth not in valid_depths:
            print(f"Invalid depth. Valid options: {valid_depths}")
            return False
            
        try:
            # Stop acquisition first
            self.scope.write(':STOP')
            time.sleep(0.5)
            
            # Count active channels
            active_channels = 0
            for ch in range(1, 5):
                if self.scope.query(f':CHANnel{ch}:DISPlay?').strip() == '1':
                    active_channels += 1
            
            # Adjust depth based on active channels
            # 1 channel: 12M, 2 channels: 6M, 3-4 channels: 3M
            if depth == '12M' and active_channels > 1:
                if active_channels == 2:
                    depth = '6M'
                    print(f"Adjusted to {depth} (2 channels active)")
                else:
                    depth = '3M'
                    print(f"Adjusted to {depth} ({active_channels} channels active)")
            
            self.scope.write(f':ACQuire:MDEPth {depth}')
            time.sleep(0.5)
            
            # Verify setting
            actual = self.get_memory_depth()
            print(f"Memory depth set to: {actual}")
            
            # Resume acquisition
            self.scope.write(':RUN')
            return True
            
        except Exception as e:
            print(f"Failed to set memory depth: {e}")
            return False
    
    def capture_long_memory(self, channel=1, points='MAX'):
        """
        Capture waveform using maximum memory depth
        
        Args:
            channel: Channel number (1-4)
            points: Number of points to capture ('MAX' or specific number)
        
        Returns:
            tuple: (time_data, voltage_data, sample_rate, memory_depth)
        """
        try:
            print(f"Starting long memory capture on channel {channel}...")
            
            # Stop acquisition for consistent capture
            self.scope.write(':STOP')
            time.sleep(0.5)
            
            # Set to RAW mode for maximum points
            self.scope.write(':WAVeform:MODE RAW')
            self.scope.write(f':WAVeform:SOURce CHANnel{channel}')
            self.scope.write(':WAVeform:FORMat BYTE')
            
            # Get actual memory depth
            mdepth_str = self.scope.query(':ACQuire:MDEPth?').strip()
            if mdepth_str == 'AUTO':
                # Query actual points available
                mdepth_value = int(float(self.scope.query(':ACQuire:POINts?').strip()))
            else:
                # Convert string to number
                mdepth_value = self._parse_memory_depth(mdepth_str)
            
            print(f"Memory depth: {mdepth_value:,} points")
            
            # Get preamble for scaling
            preamble = self.scope.query(':WAVeform:PREamble?').strip().split(',')
            x_increment = float(preamble[4])
            x_origin = float(preamble[5])
            x_reference = float(preamble[6])
            y_increment = float(preamble[7])
            y_origin = float(preamble[8])
            y_reference = float(preamble[9])
            
            # Calculate sample rate
            sample_rate = 1.0 / x_increment
            print(f"Sample rate: {sample_rate/1e6:.1f} MSa/s")
            
            # Determine points to read
            if points == 'MAX':
                points_to_read = mdepth_value
            else:
                points_to_read = min(int(points), mdepth_value)
            
            print(f"Capturing {points_to_read:,} points...")
            
            # For large captures, read in chunks
            if points_to_read > 250000:
                voltage_data = self._capture_in_chunks(
                    points_to_read, y_increment, y_origin, y_reference
                )
            else:
                # Single capture for smaller amounts
                self.scope.write(':WAVeform:DATA?')
                raw_data = self.scope.read_raw()
                voltage_data = self._parse_waveform_data(
                    raw_data, y_increment, y_origin, y_reference
                )
            
            # Generate time axis
            time_data = np.arange(len(voltage_data)) * x_increment + x_origin
            
            print(f"Captured {len(voltage_data):,} points successfully")
            print(f"Time span: {time_data[-1]*1000:.3f} ms")
            
            # Resume acquisition
            self.scope.write(':RUN')
            
            return time_data, voltage_data, sample_rate, mdepth_value
            
        except Exception as e:
            print(f"Capture failed: {e}")
            self.scope.write(':RUN')  # Try to resume
            return None, None, None, None
    
    def _capture_in_chunks(self, total_points, y_inc, y_orig, y_ref, chunk_size=250000):
        """Capture large waveforms in chunks to avoid timeouts"""
        voltage_data = []
        chunks = (total_points + chunk_size - 1) // chunk_size
        
        for i in range(chunks):
            start = i * chunk_size + 1
            stop = min((i + 1) * chunk_size, total_points)
            
            print(f"  Chunk {i+1}/{chunks}: points {start:,} to {stop:,}")
            
            # Set start and stop points
            self.scope.write(f':WAVeform:STARt {start}')
            self.scope.write(f':WAVeform:STOP {stop}')
            
            # Request data
            self.scope.write(':WAVeform:DATA?')
            raw_data = self.scope.read_raw()
            
            # Parse and append
            chunk_data = self._parse_waveform_data(raw_data, y_inc, y_orig, y_ref)
            voltage_data.extend(chunk_data)
        
        return np.array(voltage_data)
    
    def _parse_waveform_data(self, raw_data, y_inc, y_orig, y_ref):
        """Parse binary waveform data"""
        # Find start of data
        header_start = raw_data.find(b'#')
        if header_start == -1:
            raise ValueError("Invalid data format")
        
        # Parse IEEE 488.2 binary block
        n_length_bytes = int(chr(raw_data[header_start + 1]))
        data_length = int(raw_data[header_start + 2:header_start + 2 + n_length_bytes])
        data_start = header_start + 2 + n_length_bytes
        waveform_bytes = raw_data[data_start:data_start + data_length]
        
        # Convert to voltage
        waveform_data = np.frombuffer(waveform_bytes, dtype=np.uint8)
        voltage_data = ((waveform_data - y_ref) * y_inc) + y_orig
        
        return voltage_data
    
    def _parse_memory_depth(self, depth_str):
        """Convert memory depth string to integer"""
        depth_map = {
            '12k': 12000,
            '120k': 120000,
            '1.2M': 1200000,
            '3M': 3000000,
            '6M': 6000000,
            '12M': 12000000,
            '24M': 24000000  # Some models support 24M
        }
        return depth_map.get(depth_str, 12000)
    
    def capture_all_channels_long(self):
        """Capture all active channels with maximum memory depth"""
        results = {}
        
        # Get active channels
        active_channels = []
        for ch in range(1, 5):
            if self.scope.query(f':CHANnel{ch}:DISPlay?').strip() == '1':
                active_channels.append(ch)
        
        if not active_channels:
            print("No active channels found!")
            return results
        
        # Set appropriate memory depth
        if len(active_channels) == 1:
            self.set_memory_depth('12M')
        elif len(active_channels) == 2:
            self.set_memory_depth('6M')
        else:
            self.set_memory_depth('3M')
        
        # Capture each channel
        for ch in active_channels:
            print(f"\n=== Capturing Channel {ch} ===")
            time_data, voltage_data, sample_rate, depth = self.capture_long_memory(ch)
            if time_data is not None:
                results[f'CH{ch}'] = {
                    'time': time_data,
                    'voltage': voltage_data,
                    'sample_rate': sample_rate,
                    'memory_depth': depth
                }
        
        return results
    
    def close(self):
        """Close connection"""
        if self.scope:
            self.scope.close()
        if self.rm:
            self.rm.close()


def main():
    """Example usage of long memory capture"""
    import matplotlib.pyplot as plt
    
    # Connect to oscilloscope
    capture = LongMemoryCapture("192.168.68.73")
    if not capture.connect():
        return
    
    # Set maximum memory depth
    capture.set_memory_depth('12M')
    
    # Capture long memory trace
    time_data, voltage_data, sample_rate, depth = capture.capture_long_memory(channel=1)
    
    if time_data is not None:
        # Plot the results
        plt.figure(figsize=(15, 8))
        
        # Full view
        plt.subplot(2, 1, 1)
        plt.plot(time_data * 1000, voltage_data, 'b-', linewidth=0.5)
        plt.xlabel('Time (ms)')
        plt.ylabel('Voltage (V)')
        plt.title(f'Long Memory Capture - {depth:,} points @ {sample_rate/1e6:.1f} MSa/s')
        plt.grid(True, alpha=0.3)
        
        # Zoomed view (first 10%)
        zoom_points = len(time_data) // 10
        plt.subplot(2, 1, 2)
        plt.plot(time_data[:zoom_points] * 1000, voltage_data[:zoom_points], 'b-')
        plt.xlabel('Time (ms)')
        plt.ylabel('Voltage (V)')
        plt.title('Zoomed View (First 10%)')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save high-res capture
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'long_memory_{timestamp}.png'
        plt.savefig(filename, dpi=150)
        print(f"\nPlot saved as {filename}")
        
        plt.show()
    
    capture.close()


if __name__ == "__main__":
    main()