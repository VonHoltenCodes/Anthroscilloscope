#!/usr/bin/env python3
"""
Advanced Trigger Control Module for Anthroscilloscope
Provides comprehensive trigger configuration and control
"""

import pyvisa
import time
from enum import Enum


class TriggerMode(Enum):
    """Trigger mode enumeration"""
    EDGE = "EDGE"
    PULSE = "PULS"
    SLOPE = "SLOP"
    VIDEO = "VID"
    PATTERN = "PATT"
    DURATION = "DUR"
    TIMEOUT = "TIM"
    RUNT = "RUNT"
    WINDOW = "WIND"
    DELAY = "DEL"
    SETUP_HOLD = "SHOL"
    NEDGE = "NEDG"


class TriggerControl:
    """Advanced trigger control for Rigol oscilloscopes"""
    
    def __init__(self, scope):
        """
        Initialize trigger control
        
        Args:
            scope: Connected PyVISA oscilloscope instance
        """
        self.scope = scope
    
    def get_trigger_status(self):
        """Get current trigger status"""
        try:
            status = self.scope.query(':TRIGger:STATus?').strip()
            
            status_map = {
                'TD': 'Triggered',
                'WAIT': 'Waiting for trigger',
                'RUN': 'Running',
                'AUTO': 'Auto mode',
                'STOP': 'Stopped'
            }
            
            return status_map.get(status, status)
        except:
            return "Unknown"
    
    def setup_edge_trigger(self, source='CHANnel1', level=0.0, slope='POSitive', 
                          coupling='DC', holdoff=None):
        """
        Configure edge trigger
        
        Args:
            source: Trigger source (CHANnel1-4, EXT, LINE, AC)
            level: Trigger level in volts
            slope: POSitive, NEGative, or BOTH
            coupling: DC, AC, HF, LF
            holdoff: Holdoff time in seconds (None for minimum)
        """
        try:
            # Set trigger mode to edge
            self.scope.write(':TRIGger:MODE EDGE')
            
            # Set source
            self.scope.write(f':TRIGger:EDGE:SOURce {source}')
            
            # Set slope
            self.scope.write(f':TRIGger:EDGE:SLOPe {slope}')
            
            # Set level
            self.scope.write(f':TRIGger:EDGE:LEVel {level}')
            
            # Set coupling
            self.scope.write(f':TRIGger:COUPling {coupling}')
            
            # Set holdoff if specified
            if holdoff is not None:
                self.scope.write(f':TRIGger:HOLDoff {holdoff}')
            
            print(f"Edge trigger configured:")
            print(f"  Source: {source}")
            print(f"  Level: {level}V")
            print(f"  Slope: {slope}")
            print(f"  Coupling: {coupling}")
            
            return True
            
        except Exception as e:
            print(f"Failed to setup edge trigger: {e}")
            return False
    
    def setup_pulse_trigger(self, source='CHANnel1', polarity='POSitive', 
                           width_condition='LESS', width=1e-6):
        """
        Configure pulse width trigger
        
        Args:
            source: Trigger source
            polarity: POSitive or NEGative
            width_condition: LESS, GREater, or GLESs (within range)
            width: Pulse width in seconds
        """
        try:
            # Set trigger mode to pulse
            self.scope.write(':TRIGger:MODE PULSe')
            
            # Set source
            self.scope.write(f':TRIGger:PULSe:SOURce {source}')
            
            # Set polarity
            self.scope.write(f':TRIGger:PULSe:POLarity {polarity}')
            
            # Set width condition
            self.scope.write(f':TRIGger:PULSe:WHEN {width_condition}')
            
            # Set width
            self.scope.write(f':TRIGger:PULSe:WIDTh {width}')
            
            print(f"Pulse trigger configured:")
            print(f"  Source: {source}")
            print(f"  Polarity: {polarity}")
            print(f"  Condition: Width {width_condition} {width*1e6:.2f}µs")
            
            return True
            
        except Exception as e:
            print(f"Failed to setup pulse trigger: {e}")
            return False
    
    def setup_pattern_trigger(self, pattern, channels=[1, 2, 3, 4]):
        """
        Configure pattern trigger
        
        Args:
            pattern: 4-bit pattern string (H=high, L=low, X=don't care)
                    e.g., "HLXX" for CH1 high, CH2 low, CH3/4 don't care
            channels: List of channel numbers to include in pattern
        """
        try:
            # Set trigger mode to pattern
            self.scope.write(':TRIGger:MODE PATTern')
            
            # Set pattern for each channel
            pattern_map = {'H': 'HIGH', 'L': 'LOW', 'X': 'DONT_CARE'}
            
            for i, ch in enumerate(channels[:4]):
                if i < len(pattern):
                    level = pattern_map.get(pattern[i].upper(), 'DONT_CARE')
                    self.scope.write(f':TRIGger:PATTern:PATTern CHANnel{ch},{level}')
            
            print(f"Pattern trigger configured: {pattern}")
            return True
            
        except Exception as e:
            print(f"Failed to setup pattern trigger: {e}")
            return False
    
    def setup_video_trigger(self, source='CHANnel1', standard='NTSC', 
                           sync='ALL', line=None):
        """
        Configure video trigger
        
        Args:
            source: Video source channel
            standard: NTSC, PAL, or SECAM
            sync: ALL, LINE, FIELD
            line: Specific line number (if sync='LINE')
        """
        try:
            # Set trigger mode to video
            self.scope.write(':TRIGger:MODE VIDeo')
            
            # Set source
            self.scope.write(f':TRIGger:VIDeo:SOURce {source}')
            
            # Set standard
            self.scope.write(f':TRIGger:VIDeo:STANdard {standard}')
            
            # Set sync
            self.scope.write(f':TRIGger:VIDeo:MODE {sync}')
            
            # Set line if specified
            if line is not None and sync == 'LINE':
                self.scope.write(f':TRIGger:VIDeo:LINE {line}')
            
            print(f"Video trigger configured:")
            print(f"  Source: {source}")
            print(f"  Standard: {standard}")
            print(f"  Sync: {sync}")
            
            return True
            
        except Exception as e:
            print(f"Failed to setup video trigger: {e}")
            return False
    
    def setup_slope_trigger(self, source='CHANnel1', condition='POSitive',
                           time=1e-6, level_high=1.0, level_low=-1.0):
        """
        Configure slope trigger (rise/fall time)
        
        Args:
            source: Trigger source
            condition: POSitive, NEGative, or BOTH
            time: Time threshold in seconds
            level_high: Upper threshold voltage
            level_low: Lower threshold voltage
        """
        try:
            # Set trigger mode to slope
            self.scope.write(':TRIGger:MODE SLOPe')
            
            # Set source
            self.scope.write(f':TRIGger:SLOPe:SOURce {source}')
            
            # Set condition
            self.scope.write(f':TRIGger:SLOPe:WHEN {condition}')
            
            # Set time
            self.scope.write(f':TRIGger:SLOPe:TIME {time}')
            
            # Set levels
            self.scope.write(f':TRIGger:SLOPe:LEVelH {level_high}')
            self.scope.write(f':TRIGger:SLOPe:LEVelL {level_low}')
            
            print(f"Slope trigger configured:")
            print(f"  Source: {source}")
            print(f"  Condition: {condition} slope")
            print(f"  Time: {time*1e6:.2f}µs")
            print(f"  Levels: {level_low}V to {level_high}V")
            
            return True
            
        except Exception as e:
            print(f"Failed to setup slope trigger: {e}")
            return False
    
    def set_trigger_coupling(self, coupling='DC'):
        """
        Set trigger coupling
        
        Args:
            coupling: DC, AC, HFReject, LFReject
        """
        try:
            self.scope.write(f':TRIGger:COUPling {coupling}')
            print(f"Trigger coupling set to: {coupling}")
            return True
        except Exception as e:
            print(f"Failed to set coupling: {e}")
            return False
    
    def set_trigger_mode(self, mode='EDGE'):
        """
        Set trigger mode
        
        Args:
            mode: EDGE, PULSe, SLOPe, VIDeo, PATTern, DURation, etc.
        """
        try:
            self.scope.write(f':TRIGger:MODE {mode}')
            print(f"Trigger mode set to: {mode}")
            return True
        except Exception as e:
            print(f"Failed to set trigger mode: {e}")
            return False
    
    def set_trigger_sweep(self, sweep='AUTO'):
        """
        Set trigger sweep mode
        
        Args:
            sweep: AUTO, NORMal, or SINGle
        """
        try:
            self.scope.write(f':TRIGger:SWEep {sweep}')
            print(f"Trigger sweep set to: {sweep}")
            return True
        except Exception as e:
            print(f"Failed to set sweep: {e}")
            return False
    
    def force_trigger(self):
        """Force a trigger event"""
        try:
            self.scope.write(':TRIGger:FORCe')
            print("Trigger forced")
            return True
        except:
            return False
    
    def auto_trigger_level(self, channel=1):
        """
        Automatically set trigger level to 50% of signal
        
        Args:
            channel: Channel to use for auto level
        """
        try:
            # Get signal measurements
            vmax = float(self.scope.query(f':MEASure:ITEM? VMAX,CHANnel{channel}'))
            vmin = float(self.scope.query(f':MEASure:ITEM? VMIN,CHANnel{channel}'))
            
            # Check for valid signal
            if abs(vmax) > 9e37 or abs(vmin) > 9e37:
                print("No valid signal detected")
                return False
            
            # Set level to midpoint
            level = (vmax + vmin) / 2
            self.scope.write(f':TRIGger:EDGE:LEVel {level}')
            
            print(f"Auto trigger level set to: {level:.3f}V")
            print(f"  (Midpoint between {vmin:.3f}V and {vmax:.3f}V)")
            
            return True
            
        except Exception as e:
            print(f"Auto level failed: {e}")
            return False
    
    def get_trigger_info(self):
        """Get comprehensive trigger information"""
        info = {}
        
        try:
            # Basic trigger info
            info['mode'] = self.scope.query(':TRIGger:MODE?').strip()
            info['status'] = self.get_trigger_status()
            info['sweep'] = self.scope.query(':TRIGger:SWEep?').strip()
            info['coupling'] = self.scope.query(':TRIGger:COUPling?').strip()
            info['holdoff'] = float(self.scope.query(':TRIGger:HOLDoff?').strip())
            
            # Mode-specific info
            if info['mode'] == 'EDGE':
                info['source'] = self.scope.query(':TRIGger:EDGE:SOURce?').strip()
                info['slope'] = self.scope.query(':TRIGger:EDGE:SLOPe?').strip()
                info['level'] = float(self.scope.query(':TRIGger:EDGE:LEVel?').strip())
            
            elif info['mode'] == 'PULS':
                info['source'] = self.scope.query(':TRIGger:PULSe:SOURce?').strip()
                info['polarity'] = self.scope.query(':TRIGger:PULSe:POLarity?').strip()
                info['width'] = float(self.scope.query(':TRIGger:PULSe:WIDTh?').strip())
            
            return info
            
        except Exception as e:
            print(f"Error getting trigger info: {e}")
            return info
    
    def wait_for_trigger(self, timeout=10):
        """
        Wait for trigger event
        
        Args:
            timeout: Maximum time to wait in seconds
        
        Returns:
            True if triggered, False if timeout
        """
        print(f"Waiting for trigger (timeout: {timeout}s)...")
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            status = self.get_trigger_status()
            if status == 'Triggered':
                print("Triggered!")
                return True
            time.sleep(0.1)
        
        print("Trigger timeout")
        return False


def trigger_wizard(scope):
    """Interactive trigger configuration wizard"""
    trigger = TriggerControl(scope)
    
    print("\n" + "="*60)
    print("TRIGGER CONFIGURATION WIZARD")
    print("="*60)
    
    # Display current trigger info
    info = trigger.get_trigger_info()
    print("\nCurrent trigger settings:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\nTrigger modes:")
    print("1. Edge trigger")
    print("2. Pulse width trigger")
    print("3. Pattern trigger")
    print("4. Video trigger")
    print("5. Slope trigger")
    print("6. Auto-level edge trigger")
    print("0. Exit")
    
    choice = input("\nSelect trigger mode: ").strip()
    
    if choice == '1':
        # Edge trigger
        channel = input("Channel (1-4) [1]: ").strip() or '1'
        level = float(input("Level (V) [0]: ").strip() or '0')
        slope = input("Slope (POS/NEG/BOTH) [POS]: ").strip().upper() or 'POS'
        
        trigger.setup_edge_trigger(
            source=f'CHANnel{channel}',
            level=level,
            slope=slope + 'itive' if slope in ['POS', 'NEG'] else 'BOTH'
        )
        
    elif choice == '2':
        # Pulse trigger
        channel = input("Channel (1-4) [1]: ").strip() or '1'
        width = float(input("Width (µs) [1]: ").strip() or '1') * 1e-6
        condition = input("Condition (LESS/GREATER) [LESS]: ").strip().upper() or 'LESS'
        
        trigger.setup_pulse_trigger(
            source=f'CHANnel{channel}',
            width=width,
            width_condition=condition
        )
        
    elif choice == '6':
        # Auto-level
        channel = int(input("Channel (1-4) [1]: ").strip() or '1')
        trigger.auto_trigger_level(channel)
    
    print("\nTrigger configured successfully!")


if __name__ == "__main__":
    # Example usage
    import pyvisa
    
    rm = pyvisa.ResourceManager('@py')
    scope = rm.open_resource('TCPIP::192.168.68.73::INSTR')
    scope.timeout = 5000
    
    # Run trigger wizard
    trigger_wizard(scope)
    
    scope.close()