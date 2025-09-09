#!/usr/bin/env python3
"""Fixed live display for Rigol DS1104Z Plus oscilloscope"""

import pyvisa
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime

def main():
    print("="*60)
    print("RIGOL DS1104Z PLUS - LIVE DISPLAY")
    print("="*60)
    
    # Connect to scope
    ip = "192.168.68.73"
    rm = pyvisa.ResourceManager('@py')
    
    try:
        print(f"Connecting to {ip}...")
        scope = rm.open_resource(f'TCPIP::{ip}::INSTR')
        scope.timeout = 5000
        print("Connected!")
        
        # Set up matplotlib for interactive display
        plt.ion()  # Turn on interactive mode
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.patch.set_facecolor('black')
        
        # Configure top plot for waveform
        ax1.set_facecolor('black')
        ax1.grid(True, color='gray', alpha=0.3)
        ax1.set_xlabel('Time (ms)', color='white')
        ax1.set_ylabel('Voltage (V)', color='white')
        ax1.tick_params(colors='white')
        line, = ax1.plot([], [], 'yellow', linewidth=2)
        
        # Configure bottom area for measurements
        ax2.axis('off')
        ax2.set_facecolor('black')
        meas_text = ax2.text(0.05, 0.5, '', transform=ax2.transAxes,
                            color='yellow', fontsize=12, family='monospace',
                            verticalalignment='center')
        
        plt.tight_layout()
        plt.show(block=False)  # Show but don't block
        
        print("\nLive display started! Press Ctrl+C to stop.\n")
        
        # Main update loop
        while True:
            try:
                # Get waveform data
                scope.write(':WAVeform:SOURce CHANnel1')
                scope.write(':WAVeform:MODE NORMal')
                scope.write(':WAVeform:FORMat BYTE')
                
                # Get scaling parameters
                preamble = scope.query(':WAVeform:PREamble?').strip().split(',')
                x_increment = float(preamble[4])
                x_origin = float(preamble[5])
                y_increment = float(preamble[7])
                y_origin = float(preamble[8])
                y_reference = float(preamble[9])
                
                # Get waveform data
                scope.write(':WAVeform:DATA?')
                raw_data = scope.read_raw()
                
                # Parse binary data
                header_start = raw_data.find(b'#')
                if header_start != -1:
                    n_length_bytes = int(chr(raw_data[header_start + 1]))
                    data_length = int(raw_data[header_start + 2:header_start + 2 + n_length_bytes])
                    data_start = header_start + 2 + n_length_bytes
                    waveform_bytes = raw_data[data_start:data_start + data_length]
                    
                    # Convert to voltage
                    waveform_data = np.frombuffer(waveform_bytes, dtype=np.uint8)
                    voltage_data = ((waveform_data - y_reference) * y_increment) + y_origin
                    time_data = np.arange(len(voltage_data)) * x_increment + x_origin
                    
                    # Update plot
                    line.set_data(time_data * 1000, voltage_data)  # Convert to ms
                    ax1.relim()
                    ax1.autoscale_view()
                    ax1.set_title(f'Rigol DS1104Z Plus - {datetime.now().strftime("%H:%M:%S")}',
                                 color='white', fontsize=14)
                
                # Get measurements
                meas_types = [
                    ('Vpp', 'VPP'),
                    ('Vmax', 'VMAX'),
                    ('Vmin', 'VMIN'),
                    ('Vavg', 'VAVG'),
                    ('Freq', 'FREQ'),
                ]
                
                meas_str = "MEASUREMENTS\n" + "="*40 + "\n"
                for name, cmd in meas_types:
                    try:
                        result = scope.query(f':MEASure:ITEM? {cmd},CHANnel1')
                        value = float(result)
                        if abs(value) < 9.9e37:  # Valid measurement
                            if name == 'Freq':
                                if value > 1000:
                                    meas_str += f"{name:8s}: {value/1000:8.3f} kHz\n"
                                else:
                                    meas_str += f"{name:8s}: {value:8.1f} Hz\n"
                            else:
                                meas_str += f"{name:8s}: {value:8.3f} V\n"
                    except:
                        pass
                
                # Get settings
                scale = float(scope.query(':CHANnel1:SCALe?'))
                timebase = float(scope.query(':TIMebase:MAIN:SCALe?'))
                meas_str += "\n" + "="*40 + "\n"
                meas_str += f"CH1 Scale: {scale:.3f} V/div\n"
                meas_str += f"Timebase:  {timebase*1000:.1f} ms/div"
                
                meas_text.set_text(meas_str)
                
                # Update display
                plt.draw()
                plt.pause(0.5)  # Update every 500ms
                
            except KeyboardInterrupt:
                print("\nStopping...")
                break
            except Exception as e:
                print(f"Update error: {e}")
                time.sleep(1)
        
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        scope.close()
        rm.close()
        plt.close('all')
        print("Display closed.")

if __name__ == "__main__":
    main()