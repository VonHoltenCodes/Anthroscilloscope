#!/usr/bin/env python3
"""
Acquisition Control Module for Anthroscilloscope
Manages acquisition modes, sampling, and averaging
"""

import pyvisa
import time
import numpy as np
from enum import Enum


class AcquisitionType(Enum):
    """Acquisition type enumeration"""
    NORMAL = "NORM"      # Normal acquisition
    AVERAGE = "AVER"     # Average multiple acquisitions
    PEAK = "PEAK"        # Peak detect mode
    HIGH_RES = "HRES"    # High resolution mode


class AcquisitionControl:
    """Control acquisition settings for Rigol oscilloscopes"""
    
    def __init__(self, scope):
        """
        Initialize acquisition control
        
        Args:
            scope: Connected PyVISA oscilloscope instance
        """
        self.scope = scope
    
    def set_acquisition_type(self, acq_type):
        """
        Set acquisition type
        
        Args:
            acq_type: AcquisitionType enum or string ('NORM', 'AVER', 'PEAK', 'HRES')
        """
        try:
            if isinstance(acq_type, AcquisitionType):
                type_str = acq_type.value
            else:
                type_str = acq_type.upper()
            
            self.scope.write(f':ACQuire:TYPE {type_str}')
            
            # Configure averaging if selected
            if type_str == 'AVER':
                self.set_averaging(16)  # Default to 16 averages
            
            print(f"Acquisition type set to: {type_str}")
            
            return True
            
        except Exception as e:
            print(f"Failed to set acquisition type: {e}")
            return False
    
    def set_averaging(self, num_averages=16):
        """
        Configure averaging mode
        
        Args:
            num_averages: Number of waveforms to average (2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)
        """
        valid_averages = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
        
        if num_averages not in valid_averages:
            # Find closest valid value
            num_averages = min(valid_averages, key=lambda x: abs(x - num_averages))
            print(f"Adjusted to valid average count: {num_averages}")
        
        try:
            # Set to average mode
            self.scope.write(':ACQuire:TYPE AVER')
            
            # Set number of averages
            self.scope.write(f':ACQuire:AVERages {num_averages}')
            
            print(f"Averaging enabled: {num_averages} waveforms")
            return True
            
        except Exception as e:
            print(f"Failed to set averaging: {e}")
            return False
    
    def get_acquisition_info(self):
        """Get current acquisition settings"""
        try:
            info = {}
            
            # Acquisition type
            info['type'] = self.scope.query(':ACQuire:TYPE?').strip()
            
            # Memory depth
            info['memory_depth'] = self.scope.query(':ACQuire:MDEPth?').strip()
            
            # Sample rate
            try:
                info['sample_rate'] = float(self.scope.query(':ACQuire:SRATe?').strip())
            except:
                info['sample_rate'] = 0
            
            # Number of averages (if in average mode)
            if info['type'] == 'AVER':
                info['averages'] = int(self.scope.query(':ACQuire:AVERages?').strip())
            
            # Number of points
            try:
                info['points'] = int(float(self.scope.query(':ACQuire:POINts?').strip()))
            except:
                info['points'] = 0
            
            return info
            
        except Exception as e:
            print(f"Error getting acquisition info: {e}")
            return {}
    
    def set_memory_depth(self, depth='AUTO'):
        """
        Set memory depth
        
        Args:
            depth: Memory depth setting ('AUTO', '12k', '120k', '1.2M', '12M', etc.)
        """
        valid_depths = ['AUTO', '12k', '120k', '1.2M', '3M', '6M', '12M', '24M']
        
        if depth not in valid_depths:
            print(f"Invalid depth. Valid options: {valid_depths}")
            return False
        
        try:
            self.scope.write(f':ACQuire:MDEPth {depth}')
            print(f"Memory depth set to: {depth}")
            return True
            
        except Exception as e:
            print(f"Failed to set memory depth: {e}")
            return False
    
    def optimize_for_signal(self, signal_freq=None, capture_time=None):
        """
        Optimize acquisition settings for a specific signal
        
        Args:
            signal_freq: Expected signal frequency in Hz
            capture_time: Desired capture time in seconds
        """
        try:
            if signal_freq:
                # Calculate required sample rate (at least 10x signal frequency)
                required_sr = signal_freq * 10
                
                # Calculate required memory depth
                if capture_time:
                    required_points = required_sr * capture_time
                    
                    # Select appropriate memory depth
                    if required_points <= 12000:
                        self.set_memory_depth('12k')
                    elif required_points <= 120000:
                        self.set_memory_depth('120k')
                    elif required_points <= 1200000:
                        self.set_memory_depth('1.2M')
                    elif required_points <= 12000000:
                        self.set_memory_depth('12M')
                    else:
                        self.set_memory_depth('12M')
                        print(f"Warning: Requested {required_points:,} points exceeds maximum")
                
                # Set timebase to show at least 10 cycles
                period = 1.0 / signal_freq
                timebase = (period * 10) / 12  # 12 divisions on screen
                self.scope.write(f':TIMebase:MAIN:SCALe {timebase}')
                
                print(f"Optimized for {signal_freq:.1f} Hz signal")
                
            elif capture_time:
                # Optimize for capture time only
                timebase = capture_time / 12
                self.scope.write(f':TIMebase:MAIN:SCALe {timebase}')
                self.set_memory_depth('AUTO')
                
                print(f"Optimized for {capture_time:.3f} second capture")
            
            return True
            
        except Exception as e:
            print(f"Optimization failed: {e}")
            return False
    
    def set_bandwidth_limit(self, channel, enabled=False):
        """
        Enable/disable 20MHz bandwidth limit
        
        Args:
            channel: Channel number (1-4)
            enabled: True to enable bandwidth limit
        """
        try:
            state = 'ON' if enabled else 'OFF'
            self.scope.write(f':CHANnel{channel}:BWLimit {state}')
            
            print(f"Channel {channel} bandwidth limit: {'20MHz' if enabled else 'Full'}")
            return True
            
        except Exception as e:
            print(f"Failed to set bandwidth limit: {e}")
            return False
    
    def set_sampling_mode(self, mode='RTIM'):
        """
        Set sampling mode
        
        Args:
            mode: 'RTIM' for real-time or 'ETIM' for equivalent-time
        """
        try:
            self.scope.write(f':ACQuire:MODE {mode}')
            mode_name = 'Real-time' if mode == 'RTIM' else 'Equivalent-time'
            print(f"Sampling mode: {mode_name}")
            return True
            
        except Exception as e:
            print(f"Failed to set sampling mode: {e}")
            return False
    
    def run_acquisition(self):
        """Start acquisition"""
        try:
            self.scope.write(':RUN')
            print("Acquisition started")
            return True
        except:
            return False
    
    def stop_acquisition(self):
        """Stop acquisition"""
        try:
            self.scope.write(':STOP')
            print("Acquisition stopped")
            return True
        except:
            return False
    
    def single_acquisition(self):
        """Perform single acquisition"""
        try:
            self.scope.write(':SINGle')
            print("Single acquisition triggered")
            return True
        except:
            return False
    
    def auto_setup(self):
        """Perform automatic setup"""
        try:
            self.scope.write(':AUToscale')
            print("Auto-setup initiated...")
            time.sleep(3)  # Wait for auto-setup to complete
            print("Auto-setup complete")
            return True
        except:
            return False
    
    def clear_display(self):
        """Clear the display"""
        try:
            self.scope.write(':CLEar')
            print("Display cleared")
            return True
        except:
            return False
    
    def get_statistics(self, channel=1, measurement='VPP'):
        """
        Get measurement statistics (requires statistics mode)
        
        Args:
            channel: Channel number
            measurement: Measurement type (VPP, VMAX, VMIN, etc.)
        
        Returns:
            dict: Statistics including current, mean, min, max, stddev
        """
        try:
            # Enable statistics
            self.scope.write(':MEASure:STATistic:MODE ON')
            self.scope.write(':MEASure:STATistic:RESet')
            
            # Add measurement
            self.scope.write(f':MEASure:STATistic:ITEM {measurement},CHANnel{channel}')
            
            # Wait for some acquisitions
            time.sleep(2)
            
            # Get statistics
            current = float(self.scope.query(f':MEASure:STATistic:ITEM? CURRent,{measurement},CHANnel{channel}'))
            mean = float(self.scope.query(f':MEASure:STATistic:ITEM? AVERages,{measurement},CHANnel{channel}'))
            minimum = float(self.scope.query(f':MEASure:STATistic:ITEM? MINimum,{measurement},CHANnel{channel}'))
            maximum = float(self.scope.query(f':MEASure:STATistic:ITEM? MAXimum,{measurement},CHANnel{channel}'))
            
            # Check for valid values
            if abs(current) < 9e37:
                return {
                    'current': current,
                    'mean': mean,
                    'min': minimum,
                    'max': maximum,
                    'valid': True
                }
            else:
                return {'valid': False}
                
        except Exception as e:
            print(f"Statistics error: {e}")
            return {'valid': False}


def acquisition_wizard(scope):
    """Interactive acquisition setup wizard"""
    acq = AcquisitionControl(scope)
    
    print("\n" + "="*60)
    print("ACQUISITION SETUP WIZARD")
    print("="*60)
    
    # Display current settings
    info = acq.get_acquisition_info()
    print("\nCurrent acquisition settings:")
    for key, value in info.items():
        if key == 'sample_rate' and value > 0:
            print(f"  {key}: {value/1e6:.1f} MSa/s")
        else:
            print(f"  {key}: {value}")
    
    print("\nAcquisition options:")
    print("1. Normal mode")
    print("2. Averaging mode")
    print("3. Peak detect mode")
    print("4. High resolution mode")
    print("5. Optimize for frequency")
    print("6. Set memory depth")
    print("7. Auto-setup")
    print("0. Exit")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == '1':
        acq.set_acquisition_type(AcquisitionType.NORMAL)
        
    elif choice == '2':
        num = int(input("Number of averages (2-1024) [16]: ").strip() or '16')
        acq.set_averaging(num)
        
    elif choice == '3':
        acq.set_acquisition_type(AcquisitionType.PEAK)
        
    elif choice == '4':
        acq.set_acquisition_type(AcquisitionType.HIGH_RES)
        
    elif choice == '5':
        freq = float(input("Signal frequency (Hz): ").strip())
        time = float(input("Capture time (s) [0.01]: ").strip() or '0.01')
        acq.optimize_for_signal(signal_freq=freq, capture_time=time)
        
    elif choice == '6':
        print("Memory depth options: AUTO, 12k, 120k, 1.2M, 12M")
        depth = input("Select depth [AUTO]: ").strip() or 'AUTO'
        acq.set_memory_depth(depth)
        
    elif choice == '7':
        acq.auto_setup()
    
    if choice != '0':
        # Show updated settings
        info = acq.get_acquisition_info()
        print("\nUpdated settings:")
        for key, value in info.items():
            if key == 'sample_rate' and value > 0:
                print(f"  {key}: {value/1e6:.1f} MSa/s")
            else:
                print(f"  {key}: {value}")


if __name__ == "__main__":
    # Example usage
    import pyvisa
    
    rm = pyvisa.ResourceManager('@py')
    scope = rm.open_resource('TCPIP::192.168.68.73::INSTR')
    scope.timeout = 5000
    
    # Run acquisition wizard
    acquisition_wizard(scope)
    
    scope.close()