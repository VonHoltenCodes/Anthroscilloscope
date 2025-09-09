#!/usr/bin/env python3
"""
Anthroscilloscope Main Control Interface
Comprehensive oscilloscope control suite with all advanced features
"""

import sys
import os
import time
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import pyvisa

# Import all modules
from rigol_oscilloscope_control import RigolDS1104Z
from device_discovery import RigolDiscovery, interactive_discovery
from long_memory_capture import LongMemoryCapture
from data_export import DataExporter, export_suite
from trigger_control import TriggerControl, trigger_wizard
from spectrum_analyzer import SpectrumAnalyzer, analyze_waveform
from acquisition_control import AcquisitionControl, acquisition_wizard


class Anthroscilloscope:
    """Main control interface for Anthroscilloscope suite"""
    
    def __init__(self):
        self.scope = None
        self.scope_controller = None
        self.ip_address = None
        self.last_waveform = None
        self.last_time = None
        
    def connect(self, ip_address=None):
        """Connect to oscilloscope"""
        if ip_address is None:
            # Use device discovery
            print("\n🔍 DEVICE DISCOVERY")
            print("="*60)
            ip_address = interactive_discovery()
            
            if not ip_address:
                print("No device selected. Exiting.")
                return False
        
        self.ip_address = ip_address
        self.scope_controller = RigolDS1104Z(ip_address)
        
        if self.scope_controller.connect():
            self.scope = self.scope_controller.scope
            return True
        else:
            return False
    
    def display_banner(self):
        """Display ASCII art banner"""
        banner = """
         ╔═╗╔╗╔╔╦╗╦ ╦╦═╗╔═╗╔═╗╔═╗╦╦  ╦  ╔═╗╔═╗╔═╗╔═╗╔═╗╔═╗
         ╠═╣║║║ ║ ╠═╣╠╦╝║ ║╚═╗║  ║║  ║  ║ ║╚═╗║  ║ ║╠═╝║╣ 
         ╩ ╩╝╚╝ ╩ ╩ ╩╩╚═╚═╝╚═╝╚═╝╩╩═╝╩═╝╚═╝╚═╝╚═╝╚═╝╩  ╚═╝
                    Advanced Oscilloscope Control Suite
        """
        print(banner)
    
    def main_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("MAIN MENU")
        print("="*60)
        print("\n📊 Basic Operations:")
        print("  1. Single waveform capture")
        print("  2. Live waveform display")
        print("  3. Save screenshot")
        print("  4. Display measurements")
        
        print("\n🚀 Advanced Features:")
        print("  5. Long memory capture (up to 12M points)")
        print("  6. FFT spectrum analysis")
        print("  7. Export data (CSV/HDF5/JSON)")
        print("  8. Trigger configuration")
        print("  9. Acquisition settings")
        
        print("\n🔧 Utilities:")
        print("  10. Auto-setup")
        print("  11. Device info")
        print("  12. Change oscilloscope")
        
        print("\n  0. Exit")
        print("-"*60)
    
    def run(self):
        """Main control loop"""
        self.display_banner()
        
        # Connect to oscilloscope
        if not self.connect():
            print("Failed to connect to oscilloscope.")
            return
        
        try:
            while True:
                self.main_menu()
                choice = input("\nSelect option: ").strip()
                
                if choice == '1':
                    self.single_capture()
                    
                elif choice == '2':
                    self.live_display()
                    
                elif choice == '3':
                    self.save_screenshot()
                    
                elif choice == '4':
                    self.display_measurements()
                    
                elif choice == '5':
                    self.long_memory_capture_menu()
                    
                elif choice == '6':
                    self.spectrum_analysis()
                    
                elif choice == '7':
                    self.export_data_menu()
                    
                elif choice == '8':
                    trigger_wizard(self.scope)
                    
                elif choice == '9':
                    acquisition_wizard(self.scope)
                    
                elif choice == '10':
                    self.auto_setup()
                    
                elif choice == '11':
                    self.device_info()
                    
                elif choice == '12':
                    self.change_oscilloscope()
                    
                elif choice == '0':
                    print("\nExiting Anthroscilloscope...")
                    break
                    
                else:
                    print("❌ Invalid option. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
        
        finally:
            if self.scope:
                self.scope.close()
            print("Connection closed. Goodbye!")
    
    def single_capture(self):
        """Perform single waveform capture"""
        print("\n📸 SINGLE WAVEFORM CAPTURE")
        print("-"*40)
        
        channel = input("Channel (1-4) [1]: ").strip() or '1'
        time_data, voltage_data = self.scope_controller.get_waveform_data(int(channel))
        
        if time_data is not None:
            self.last_time = time_data
            self.last_waveform = voltage_data
            
            # Plot waveform
            plt.figure(figsize=(12, 6))
            plt.plot(time_data * 1000, voltage_data, 'b-')
            plt.xlabel('Time (ms)')
            plt.ylabel('Voltage (V)')
            plt.title(f'Channel {channel} Waveform - {datetime.now().strftime("%H:%M:%S")}')
            plt.grid(True, alpha=0.3)
            plt.show()
            
            print(f"✅ Captured {len(voltage_data)} points")
    
    def live_display(self):
        """Launch live waveform display"""
        print("\n🔴 LIVE WAVEFORM DISPLAY")
        print("-"*40)
        print("Starting live display...")
        print("Press Ctrl+C to stop")
        
        # Import and run the fixed live display
        import subprocess
        subprocess.run(['python3', 'rigol_display_fixed.py'])
    
    def save_screenshot(self):
        """Save oscilloscope screenshot"""
        print("\n📷 SAVE SCREENSHOT")
        print("-"*40)
        
        filename = input("Filename (without extension) [screenshot]: ").strip() or 'screenshot'
        if not filename.endswith('.png'):
            filename += f'_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        
        if self.scope_controller.save_screenshot(filename):
            print(f"✅ Screenshot saved as {filename}")
    
    def display_measurements(self):
        """Display oscilloscope measurements"""
        print("\n📏 MEASUREMENTS")
        print("-"*40)
        
        measurements = [
            ('Vpp', 'VPP'),
            ('Vmax', 'VMAX'),
            ('Vmin', 'VMIN'),
            ('Vavg', 'VAVG'),
            ('Vrms', 'VRMS'),
            ('Frequency', 'FREQ'),
            ('Period', 'PER'),
        ]
        
        for channel in range(1, 5):
            # Check if channel is active
            state = self.scope.query(f':CHANnel{channel}:DISPlay?').strip()
            if state == '1':
                print(f"\nChannel {channel}:")
                for name, cmd in measurements:
                    value = self.scope_controller.get_measurement(channel, cmd)
                    if value is not None:
                        if cmd == 'FREQ':
                            print(f"  {name}: {value/1000:.3f} kHz")
                        elif cmd == 'PER':
                            print(f"  {name}: {value*1000:.3f} ms")
                        else:
                            print(f"  {name}: {value:.3f} V")
    
    def long_memory_capture_menu(self):
        """Long memory capture menu"""
        print("\n💾 LONG MEMORY CAPTURE")
        print("-"*40)
        
        capture = LongMemoryCapture(self.ip_address)
        if not capture.connect():
            print("Failed to connect for long memory capture")
            return
        
        print("Memory depth options:")
        print("1. 12k points")
        print("2. 120k points")
        print("3. 1.2M points")
        print("4. 12M points (single channel)")
        print("5. Auto")
        
        depth_map = {'1': '12k', '2': '120k', '3': '1.2M', '4': '12M', '5': 'AUTO'}
        choice = input("\nSelect depth: ").strip()
        depth = depth_map.get(choice, 'AUTO')
        
        capture.set_memory_depth(depth)
        
        channel = int(input("Channel (1-4) [1]: ").strip() or '1')
        
        print("\nCapturing...")
        time_data, voltage_data, sample_rate, depth_actual = capture.capture_long_memory(channel)
        
        if time_data is not None:
            self.last_time = time_data
            self.last_waveform = voltage_data
            
            print(f"✅ Captured {len(voltage_data):,} points")
            print(f"Sample rate: {sample_rate/1e6:.1f} MSa/s")
            print(f"Time span: {time_data[-1]*1000:.3f} ms")
            
            # Ask if user wants to plot
            if input("\nPlot waveform? (Y/n): ").strip().lower() != 'n':
                plt.figure(figsize=(15, 8))
                
                # Full view
                plt.subplot(2, 1, 1)
                plt.plot(time_data * 1000, voltage_data, 'b-', linewidth=0.5)
                plt.xlabel('Time (ms)')
                plt.ylabel('Voltage (V)')
                plt.title(f'Long Memory Capture - {depth_actual:,} points')
                plt.grid(True, alpha=0.3)
                
                # Zoomed view
                zoom_points = min(10000, len(time_data))
                plt.subplot(2, 1, 2)
                plt.plot(time_data[:zoom_points] * 1000, voltage_data[:zoom_points], 'b-')
                plt.xlabel('Time (ms)')
                plt.ylabel('Voltage (V)')
                plt.title('Zoomed View (First portion)')
                plt.grid(True, alpha=0.3)
                
                plt.tight_layout()
                plt.show()
        
        capture.close()
    
    def spectrum_analysis(self):
        """Perform FFT spectrum analysis"""
        print("\n📊 SPECTRUM ANALYSIS")
        print("-"*40)
        
        if self.last_waveform is None:
            print("No waveform data available.")
            capture = input("Capture now? (Y/n): ").strip().lower()
            if capture != 'n':
                self.single_capture()
        
        if self.last_waveform is not None:
            print("Analyzing frequency spectrum...")
            analyze_waveform(self.last_time, self.last_waveform, plot=True)
    
    def export_data_menu(self):
        """Export data menu"""
        print("\n💾 EXPORT DATA")
        print("-"*40)
        
        if self.last_waveform is None:
            print("No waveform data available.")
            capture = input("Capture now? (Y/n): ").strip().lower()
            if capture != 'n':
                self.single_capture()
        
        if self.last_waveform is not None:
            print("\nExport formats:")
            print("1. CSV")
            print("2. HDF5")
            print("3. NumPy (.npz)")
            print("4. JSON")
            print("5. MATLAB (.mat)")
            print("6. WAV audio")
            print("7. All formats")
            
            choice = input("\nSelect format: ").strip()
            
            base_filename = input("Base filename [waveform]: ").strip() or 'waveform'
            base_filename += f'_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            
            format_map = {
                '1': ['csv'],
                '2': ['hdf5'],
                '3': ['numpy'],
                '4': ['json'],
                '5': ['matlab'],
                '6': ['wav'],
                '7': ['csv', 'hdf5', 'numpy', 'json', 'matlab']
            }
            
            formats = format_map.get(choice, ['csv'])
            
            metadata = {
                'oscilloscope': 'Rigol DS1104Z Plus',
                'ip_address': self.ip_address,
                'timestamp': datetime.now().isoformat(),
                'points': len(self.last_waveform)
            }
            
            if 'wav' in formats:
                # Special handling for WAV export
                sample_rate = 1.0 / (self.last_time[1] - self.last_time[0])
                exporter = DataExporter()
                exporter.export_wav(base_filename, self.last_waveform, sample_rate)
            else:
                export_suite(self.last_time, self.last_waveform, 
                           base_filename, formats=formats, metadata=metadata)
            
            print("✅ Export complete!")
    
    def auto_setup(self):
        """Perform auto-setup"""
        print("\n🔧 AUTO-SETUP")
        print("-"*40)
        print("Performing automatic setup...")
        
        acq = AcquisitionControl(self.scope)
        acq.auto_setup()
        
        print("✅ Auto-setup complete")
    
    def device_info(self):
        """Display device information"""
        print("\n📋 DEVICE INFORMATION")
        print("-"*40)
        
        idn = self.scope.query('*IDN?').strip()
        print(f"Device: {idn}")
        print(f"IP Address: {self.ip_address}")
        
        # Get acquisition info
        acq = AcquisitionControl(self.scope)
        info = acq.get_acquisition_info()
        
        print("\nAcquisition Settings:")
        for key, value in info.items():
            if key == 'sample_rate' and value > 0:
                print(f"  {key}: {value/1e6:.1f} MSa/s")
            else:
                print(f"  {key}: {value}")
        
        # Get trigger info
        trigger = TriggerControl(self.scope)
        trig_info = trigger.get_trigger_info()
        
        print("\nTrigger Settings:")
        for key, value in trig_info.items():
            print(f"  {key}: {value}")
    
    def change_oscilloscope(self):
        """Change to a different oscilloscope"""
        print("\n🔄 CHANGE OSCILLOSCOPE")
        print("-"*40)
        
        if self.scope:
            self.scope.close()
        
        if self.connect():
            print("✅ Connected to new oscilloscope")
        else:
            print("❌ Failed to connect")
            sys.exit(1)


def main():
    """Main entry point"""
    app = Anthroscilloscope()
    app.run()


if __name__ == "__main__":
    main()