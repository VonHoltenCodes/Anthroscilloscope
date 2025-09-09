#!/usr/bin/env python3
"""Live display of Rigol DS1104Z Plus oscilloscope on your screen"""

import pyvisa
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
from datetime import datetime

class RigolLiveDisplay:
    def __init__(self, ip_address="192.168.68.73"):
        self.ip = ip_address
        self.rm = pyvisa.ResourceManager('@py')
        self.scope = None
        self.fig = None
        self.ax = None
        self.line = None
        
    def connect(self):
        """Connect to oscilloscope"""
        print(f"Connecting to Rigol DS1104Z Plus at {self.ip}...")
        try:
            self.scope = self.rm.open_resource(f'TCPIP::{self.ip}::INSTR')
            self.scope.timeout = 5000
            idn = self.scope.query('*IDN?').strip()
            print(f"Connected: {idn}")
            
            # Press AUTO to find signal
            print("Sending AUTO command to find signal...")
            self.scope.write(':AUToscale')
            time.sleep(2)
            
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def setup_plot(self):
        """Set up the matplotlib window"""
        plt.ion()  # Interactive mode
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Top plot for waveform
        self.line, = self.ax1.plot([], [], 'yellow', linewidth=2, label='CH1')
        self.ax1.set_facecolor('black')
        self.ax1.grid(True, color='gray', alpha=0.3)
        self.ax1.set_xlabel('Time', color='white')
        self.ax1.set_ylabel('Voltage (V)', color='white')
        self.ax1.set_title('Rigol DS1104Z Plus - Live Display', color='white', fontsize=14)
        self.ax1.tick_params(colors='white')
        
        # Bottom area for measurements
        self.ax2.axis('off')
        self.ax2.set_facecolor('black')
        self.measurement_text = self.ax2.text(0.05, 0.5, '', 
                                             transform=self.ax2.transAxes,
                                             color='yellow', 
                                             fontsize=12,
                                             family='monospace',
                                             verticalalignment='center')
        
        # Set window background
        self.fig.patch.set_facecolor('black')
        plt.tight_layout()
        
    def get_waveform(self, channel=1):
        """Fetch waveform data from oscilloscope"""
        try:
            # Configure waveform readout
            self.scope.write(f':WAVeform:SOURce CHANnel{channel}')
            self.scope.write(':WAVeform:MODE NORMal')
            self.scope.write(':WAVeform:FORMat BYTE')
            
            # Get preamble for scaling
            preamble = self.scope.query(':WAVeform:PREamble?').strip().split(',')
            x_increment = float(preamble[4])
            x_origin = float(preamble[5])
            y_increment = float(preamble[7])
            y_origin = float(preamble[8])
            y_reference = float(preamble[9])
            
            # Get waveform data
            self.scope.write(':WAVeform:DATA?')
            raw_data = self.scope.read_raw()
            
            # Parse binary data
            header_start = raw_data.find(b'#')
            if header_start == -1:
                return None, None
                
            n_length_bytes = int(chr(raw_data[header_start + 1]))
            data_length = int(raw_data[header_start + 2:header_start + 2 + n_length_bytes])
            data_start = header_start + 2 + n_length_bytes
            waveform_bytes = raw_data[data_start:data_start + data_length]
            
            # Convert to voltage
            waveform_data = np.frombuffer(waveform_bytes, dtype=np.uint8)
            voltage_data = ((waveform_data - y_reference) * y_increment) + y_origin
            time_data = np.arange(len(voltage_data)) * x_increment + x_origin
            
            return time_data, voltage_data
            
        except Exception as e:
            print(f"Error getting waveform: {e}")
            return None, None
    
    def get_measurements(self, channel=1):
        """Get scope measurements"""
        measurements = {}
        try:
            # Get various measurements
            meas_types = {
                'Vpp': 'VPP',
                'Vmax': 'VMAX', 
                'Vmin': 'VMIN',
                'Vavg': 'VAVG',
                'Freq': 'FREQ',
                'Period': 'PERiod'
            }
            
            for name, cmd in meas_types.items():
                try:
                    result = self.scope.query(f':MEASure:ITEM? {cmd},CHANnel{channel}')
                    value = float(result)
                    # Check for out-of-range values
                    if abs(value) < 9.9e37:
                        measurements[name] = value
                except:
                    pass
                    
            # Get channel settings
            scale = float(self.scope.query(f':CHANnel{channel}:SCALe?'))
            offset = float(self.scope.query(f':CHANnel{channel}:OFFSet?'))
            coupling = self.scope.query(f':CHANnel{channel}:COUPling?').strip()
            
            measurements['Scale'] = scale
            measurements['Offset'] = offset  
            measurements['Coupling'] = coupling
            
            # Get timebase
            timebase = float(self.scope.query(':TIMebase:MAIN:SCALe?'))
            measurements['Timebase'] = timebase
            
        except Exception as e:
            print(f"Error getting measurements: {e}")
            
        return measurements
    
    def update_display(self, frame):
        """Update the display with new data"""
        # Get waveform
        time_data, voltage_data = self.get_waveform()
        
        if time_data is not None and voltage_data is not None:
            # Update waveform plot
            self.line.set_data(time_data * 1000, voltage_data)  # Convert to ms
            self.ax1.relim()
            self.ax1.autoscale_view()
            
            # Get measurements
            meas = self.get_measurements()
            
            # Format measurement text
            meas_text = "MEASUREMENTS\n" + "="*40 + "\n"
            
            if 'Vpp' in meas:
                meas_text += f"Vpp:      {meas['Vpp']:.3f} V\n"
            if 'Vmax' in meas:
                meas_text += f"Vmax:     {meas['Vmax']:.3f} V\n"
            if 'Vmin' in meas:
                meas_text += f"Vmin:     {meas['Vmin']:.3f} V\n"
            if 'Vavg' in meas:
                meas_text += f"Vavg:     {meas['Vavg']:.3f} V\n"
            if 'Freq' in meas:
                freq = meas['Freq']
                if freq > 1000:
                    meas_text += f"Freq:     {freq/1000:.3f} kHz\n"
                else:
                    meas_text += f"Freq:     {freq:.1f} Hz\n"
            if 'Period' in meas:
                period = meas['Period']
                if period < 0.001:
                    meas_text += f"Period:   {period*1e6:.1f} µs\n"
                else:
                    meas_text += f"Period:   {period*1000:.3f} ms\n"
                    
            meas_text += "\n" + "="*40 + "\n"
            meas_text += f"CH1 Scale: {meas.get('Scale', 0):.3f} V/div\n"
            meas_text += f"Timebase:  {meas.get('Timebase', 0)*1000:.1f} ms/div\n"
            meas_text += f"Coupling:  {meas.get('Coupling', 'DC')}"
            
            self.measurement_text.set_text(meas_text)
            
            # Update title with timestamp
            self.ax1.set_title(f'Rigol DS1104Z Plus - Live Display - {datetime.now().strftime("%H:%M:%S")}',
                              color='white', fontsize=14)
        
        return self.line, self.measurement_text
    
    def run_live_display(self):
        """Start the live display"""
        print("\nStarting live display...")
        print("Close the window to exit.\n")
        
        self.setup_plot()
        
        # Create animation (updates every 500ms)
        self.ani = FuncAnimation(self.fig, self.update_display, 
                                interval=500, blit=True, cache_frame_data=False)
        
        try:
            plt.show()
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            if self.scope:
                self.scope.close()
            self.rm.close()

def main():
    print("="*60)
    print("RIGOL DS1104Z PLUS - LIVE DISPLAY")
    print("="*60)
    print("\nMAKE SURE YOU HAVE:")
    print("1. Connected probe to CH1")
    print("2. Set probe to 10X")
    print("3. Connected probe tip to Probe Comp signal terminal")
    print("4. Connected ground clip to ground terminal")
    print("="*60)
    
    display = RigolLiveDisplay("192.168.68.65")
    
    if display.connect():
        display.run_live_display()
    else:
        print("Failed to connect to oscilloscope")

if __name__ == "__main__":
    main()