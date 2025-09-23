#!/usr/bin/env python3
"""
Anthroscilloscope Main Control Interface
Comprehensive oscilloscope control suite with all advanced features
"""

# Suppress matplotlib warnings
import warnings
warnings.filterwarnings('ignore', message='Unable to import Axes3D.*', category=UserWarning)

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
from lissajous_xy_mode import LissajousXYAnalyzer, InteractiveLissajousViewer, LissajousGenerator
from frequency_math import FrequencyAnalyzer, MusicalIntervals, LissajousFrequencyMath
import config


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
            # Try config first
            if hasattr(config, 'RIGOL_IP'):
                ip_address = config.RIGOL_IP
                print(f"Using configured IP: {ip_address}")
            else:
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
        
        print("\n🎨 Lissajous & XY Mode:")
        print("  10. Interactive Lissajous viewer")
        print("  11. XY mode analysis")
        print("  12. Frequency ratio calculator")
        print("  13. Musical interval analysis")
        
        print("\n🔧 Utilities:")
        print("  14. Auto-setup")
        print("  15. Device info")
        print("  16. Change oscilloscope")
        
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
                    self.lissajous_viewer()
                    
                elif choice == '11':
                    self.xy_mode_analysis()
                    
                elif choice == '12':
                    self.frequency_ratio_calculator()
                    
                elif choice == '13':
                    self.musical_interval_analysis()
                    
                elif choice == '14':
                    self.auto_setup()
                    
                elif choice == '15':
                    self.device_info()
                    
                elif choice == '16':
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
    
    def lissajous_viewer(self):
        """Launch interactive Lissajous pattern viewer"""
        print("\n🎨 INTERACTIVE LISSAJOUS VIEWER")
        print("-"*40)
        print("Launching interactive viewer...")
        
        viewer = InteractiveLissajousViewer(self.scope)
        viewer.run()
    
    def xy_mode_analysis(self):
        """Perform XY mode analysis"""
        print("\n📊 XY MODE ANALYSIS")
        print("-"*40)
        
        analyzer = LissajousXYAnalyzer(self.scope)
        
        print("Options:")
        print("1. Enable XY mode")
        print("2. Disable XY mode")
        print("3. Capture and analyze pattern")
        print("4. Back to main menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            if analyzer.enable_xy_mode():
                print("✅ XY mode enabled")
                print("Connect CH1 to X signal, CH2 to Y signal")
        
        elif choice == '2':
            if analyzer.disable_xy_mode():
                print("✅ Returned to YT mode")
        
        elif choice == '3':
            print("Capturing XY data...")
            x_data, y_data = analyzer.capture_xy_data()
            
            if x_data is not None:
                pattern = analyzer.analyze_pattern(x_data, y_data)
                ratio_x, ratio_y = pattern.get_simplified_ratio()
                
                print(f"\n📈 Analysis Results:")
                print(f"Frequency ratio: {ratio_x}:{ratio_y}")
                print(f"Phase difference: {np.degrees(pattern.phase):.1f}°")
                print(f"X amplitude: {pattern.amplitude_x:.3f}")
                print(f"Y amplitude: {pattern.amplitude_y:.3f}")
                
                # Plot the pattern
                x_gen, y_gen = LissajousGenerator.generate(pattern, points=1000)
                
                plt.figure(figsize=(10, 5))
                
                # Captured data
                plt.subplot(1, 2, 1)
                plt.plot(x_data, y_data, 'b-', alpha=0.7)
                plt.xlabel('X (CH1)')
                plt.ylabel('Y (CH2)')
                plt.title('Captured Pattern')
                plt.grid(True, alpha=0.3)
                plt.axis('equal')
                
                # Generated pattern
                plt.subplot(1, 2, 2)
                plt.plot(x_gen, y_gen, 'r-', alpha=0.7)
                plt.xlabel('X')
                plt.ylabel('Y')
                plt.title(f'Generated {ratio_x}:{ratio_y} Pattern')
                plt.grid(True, alpha=0.3)
                plt.axis('equal')
                
                plt.tight_layout()
                plt.show()
    
    def frequency_ratio_calculator(self):
        """Calculate frequency ratios and Lissajous parameters"""
        print("\n🔢 FREQUENCY RATIO CALCULATOR")
        print("-"*40)
        
        print("Enter frequencies (Hz) or 'measure' to get from scope:")
        
        freq_x_str = input("X frequency (CH1): ").strip()
        
        if freq_x_str.lower() == 'measure':
            freq_x = self.scope_controller.get_measurement(1, 'FREQ')
            if freq_x:
                print(f"Measured: {freq_x:.2f} Hz")
        else:
            try:
                freq_x = float(freq_x_str)
            except:
                print("Invalid frequency")
                return
        
        freq_y_str = input("Y frequency (CH2): ").strip()
        
        if freq_y_str.lower() == 'measure':
            freq_y = self.scope_controller.get_measurement(2, 'FREQ')
            if freq_y:
                print(f"Measured: {freq_y:.2f} Hz")
        else:
            try:
                freq_y = float(freq_y_str)
            except:
                print("Invalid frequency")
                return
        
        # Calculate parameters
        print(f"\n📊 Analysis:")
        print(f"Frequencies: {freq_x:.2f} Hz × {freq_y:.2f} Hz")
        
        ratio = freq_x / freq_y if freq_y != 0 else 0
        print(f"Ratio: {ratio:.4f}")
        
        # Find simplified ratio
        from fractions import Fraction
        frac = Fraction(ratio).limit_denominator(20)
        print(f"Simplified: {frac.numerator}:{frac.denominator}")
        
        # Pattern analysis
        period = LissajousFrequencyMath.pattern_period(freq_x, freq_y)
        print(f"Pattern period: {period*1000:.2f} ms")
        
        crossings = LissajousFrequencyMath.crossing_points(frac.numerator, frac.denominator)
        print(f"Crossing points: {crossings}")
        
        complexity = LissajousFrequencyMath.pattern_complexity(frac.numerator, frac.denominator)
        print(f"Complexity: {complexity:.2f}")
        
        # Stability
        stability = LissajousFrequencyMath.stability_analysis(freq_x, freq_y)
        print(f"Pattern stable: {stability['is_stable']}")
        print(f"Drift rate: {stability['drift_rate_hz']:.3f} Hz")
    
    def musical_interval_analysis(self):
        """Analyze musical intervals from frequency measurements"""
        print("\n🎵 MUSICAL INTERVAL ANALYSIS")
        print("-"*40)
        
        print("Measure frequencies from oscilloscope channels...")
        
        # Get frequencies from active channels
        frequencies = []
        for ch in range(1, 5):
            state = self.scope.query(f':CHANnel{ch}:DISPlay?').strip()
            if state == '1':
                freq = self.scope_controller.get_measurement(ch, 'FREQ')
                if freq and freq > 0:
                    frequencies.append((ch, freq))
                    print(f"CH{ch}: {freq:.2f} Hz")
        
        if len(frequencies) < 2:
            print("Need at least 2 active channels with signals")
            return
        
        print("\n📊 Interval Analysis:")
        
        # Analyze all pairs
        for i in range(len(frequencies)):
            for j in range(i+1, len(frequencies)):
                ch1, freq1 = frequencies[i]
                ch2, freq2 = frequencies[j]
                
                ratio = freq1 / freq2 if freq1 > freq2 else freq2 / freq1
                
                interval = MusicalIntervals.find_closest_interval(ratio)
                if interval:
                    print(f"\nCH{ch1} → CH{ch2}:")
                    print(f"  Ratio: {ratio:.4f}")
                    print(f"  Interval: {interval.interval_name}")
                    print(f"  Exact: {interval.numerator}:{interval.denominator}")
                    print(f"  Cents off: {interval.cents:.1f}")
                    print(f"  Consonance: {interval.consonance_rating:.2f}")
        
        # Find fundamental
        all_freqs = [f for _, f in frequencies]
        fundamental = FrequencyAnalyzer.find_fundamental(all_freqs)
        print(f"\nEstimated fundamental: {fundamental:.2f} Hz")
        
        # Check if harmonics
        print("\nHarmonic analysis:")
        for ch, freq in frequencies:
            harmonic = round(freq / fundamental)
            error = abs(freq - fundamental * harmonic)
            if error < fundamental * 0.05:  # 5% tolerance
                print(f"  CH{ch}: Harmonic {harmonic} (error: {error:.1f} Hz)")


def main():
    """Main entry point"""
    app = Anthroscilloscope()
    app.run()


if __name__ == "__main__":
    main()