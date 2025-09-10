#!/usr/bin/env python3
"""
Waveform Generator Control Module for Anthroscilloscope
Controls the built-in signal generator in Rigol DS1104Z Plus (-S models)
"""

import pyvisa
import numpy as np
from enum import Enum


class WaveformType(Enum):
    """Available waveform types"""
    SINE = "SIN"
    SQUARE = "SQU"
    RAMP = "RAMP"
    PULSE = "PULS"
    NOISE = "NOIS"
    DC = "DC"
    # Advanced waveforms (if supported)
    CARDIAC = "CARD"
    GAUSSIAN = "GAUS"
    ARBITRARY = "ARB"


class WaveformGenerator:
    """Control the built-in waveform generator"""
    
    def __init__(self, scope):
        """
        Initialize generator control
        
        Args:
            scope: Connected PyVISA oscilloscope instance
        """
        self.scope = scope
        self.channel = 1  # SOURCE1
        
    def is_available(self):
        """Check if generator is available"""
        try:
            response = self.scope.query(':SOURCE1:OUTPUT?').strip()
            return response in ['ON', 'OFF', '1', '0']
        except:
            return False
    
    def enable(self):
        """Turn on the generator output"""
        try:
            self.scope.write(':SOURCE1:OUTPUT ON')
            print("✅ Generator output enabled")
            return True
        except Exception as e:
            print(f"❌ Failed to enable generator: {e}")
            return False
    
    def disable(self):
        """Turn off the generator output"""
        try:
            self.scope.write(':SOURCE1:OUTPUT OFF')
            print("✅ Generator output disabled")
            return True
        except Exception as e:
            print(f"❌ Failed to disable generator: {e}")
            return False
    
    def set_sine(self, frequency=1000, amplitude=1.0, offset=0.0):
        """
        Generate sine wave
        
        Args:
            frequency: Frequency in Hz (1 Hz to 25 MHz)
            amplitude: Peak-to-peak voltage (0.001V to 10V)
            offset: DC offset voltage (-5V to +5V)
        """
        try:
            # Set function type
            self.scope.write(':SOURCE1:FUNCTION SIN')
            
            # Set parameters
            self.scope.write(f':SOURCE1:FREQUENCY {frequency}')
            self.scope.write(f':SOURCE1:VOLTAGE {amplitude}')
            self.scope.write(f':SOURCE1:VOLTAGE:OFFSET {offset}')
            
            print(f"✅ Sine wave: {frequency} Hz, {amplitude} Vpp, {offset}V offset")
            return True
            
        except Exception as e:
            print(f"❌ Failed to set sine wave: {e}")
            return False
    
    def set_square(self, frequency=1000, amplitude=1.0, offset=0.0, duty_cycle=50):
        """
        Generate square wave
        
        Args:
            frequency: Frequency in Hz
            amplitude: Peak-to-peak voltage
            offset: DC offset voltage
            duty_cycle: Duty cycle percentage (10-90)
        """
        try:
            self.scope.write(':SOURCE1:FUNCTION SQU')
            self.scope.write(f':SOURCE1:FREQUENCY {frequency}')
            self.scope.write(f':SOURCE1:VOLTAGE {amplitude}')
            self.scope.write(f':SOURCE1:VOLTAGE:OFFSET {offset}')
            self.scope.write(f':SOURCE1:SQUARE:DUTY {duty_cycle}')
            
            print(f"✅ Square wave: {frequency} Hz, {amplitude} Vpp, {duty_cycle}% duty")
            return True
            
        except Exception as e:
            print(f"❌ Failed to set square wave: {e}")
            return False
    
    def set_ramp(self, frequency=1000, amplitude=1.0, offset=0.0, symmetry=50):
        """
        Generate ramp/triangle wave
        
        Args:
            frequency: Frequency in Hz
            amplitude: Peak-to-peak voltage
            offset: DC offset voltage
            symmetry: Ramp symmetry percentage (0-100)
        """
        try:
            self.scope.write(':SOURCE1:FUNCTION RAMP')
            self.scope.write(f':SOURCE1:FREQUENCY {frequency}')
            self.scope.write(f':SOURCE1:VOLTAGE {amplitude}')
            self.scope.write(f':SOURCE1:VOLTAGE:OFFSET {offset}')
            self.scope.write(f':SOURCE1:RAMP:SYMMETRY {symmetry}')
            
            print(f"✅ Ramp wave: {frequency} Hz, {amplitude} Vpp, {symmetry}% symmetry")
            return True
            
        except Exception as e:
            print(f"❌ Failed to set ramp wave: {e}")
            return False
    
    def set_pulse(self, frequency=1000, amplitude=1.0, offset=0.0, width=0.0001):
        """
        Generate pulse wave
        
        Args:
            frequency: Frequency in Hz
            amplitude: Peak-to-peak voltage
            offset: DC offset voltage
            width: Pulse width in seconds
        """
        try:
            self.scope.write(':SOURCE1:FUNCTION PULS')
            self.scope.write(f':SOURCE1:FREQUENCY {frequency}')
            self.scope.write(f':SOURCE1:VOLTAGE {amplitude}')
            self.scope.write(f':SOURCE1:VOLTAGE:OFFSET {offset}')
            self.scope.write(f':SOURCE1:PULSE:WIDTH {width}')
            
            print(f"✅ Pulse wave: {frequency} Hz, {amplitude} Vpp, {width*1e6:.1f}µs width")
            return True
            
        except Exception as e:
            print(f"❌ Failed to set pulse wave: {e}")
            return False
    
    def set_noise(self, amplitude=1.0, offset=0.0):
        """
        Generate noise signal
        
        Args:
            amplitude: Peak-to-peak voltage
            offset: DC offset voltage
        """
        try:
            self.scope.write(':SOURCE1:FUNCTION NOIS')
            self.scope.write(f':SOURCE1:VOLTAGE {amplitude}')
            self.scope.write(f':SOURCE1:VOLTAGE:OFFSET {offset}')
            
            print(f"✅ Noise: {amplitude} Vpp, {offset}V offset")
            return True
            
        except Exception as e:
            print(f"❌ Failed to set noise: {e}")
            return False
    
    def set_dc(self, voltage=0.0):
        """
        Generate DC voltage
        
        Args:
            voltage: DC voltage level (-5V to +5V)
        """
        try:
            self.scope.write(':SOURCE1:FUNCTION DC')
            self.scope.write(f':SOURCE1:VOLTAGE:OFFSET {voltage}')
            
            print(f"✅ DC output: {voltage}V")
            return True
            
        except Exception as e:
            print(f"❌ Failed to set DC: {e}")
            return False
    
    def sweep_frequency(self, start_freq=100, stop_freq=10000, sweep_time=1.0):
        """
        Perform frequency sweep
        
        Args:
            start_freq: Start frequency in Hz
            stop_freq: Stop frequency in Hz
            sweep_time: Sweep duration in seconds
        """
        try:
            # Enable sweep mode
            self.scope.write(':SOURCE1:SWEEP:STATE ON')
            self.scope.write(f':SOURCE1:FREQUENCY:START {start_freq}')
            self.scope.write(f':SOURCE1:FREQUENCY:STOP {stop_freq}')
            self.scope.write(f':SOURCE1:SWEEP:TIME {sweep_time}')
            
            print(f"✅ Frequency sweep: {start_freq} Hz to {stop_freq} Hz in {sweep_time}s")
            return True
            
        except Exception as e:
            print(f"❌ Failed to set sweep: {e}")
            return False
    
    def modulate_am(self, carrier_freq=1000, mod_freq=100, mod_depth=50):
        """
        Apply amplitude modulation
        
        Args:
            carrier_freq: Carrier frequency in Hz
            mod_freq: Modulation frequency in Hz
            mod_depth: Modulation depth percentage (0-100)
        """
        try:
            self.scope.write(f':SOURCE1:FREQUENCY {carrier_freq}')
            self.scope.write(':SOURCE1:MOD:TYPE AM')
            self.scope.write(f':SOURCE1:MOD:AM:FREQUENCY {mod_freq}')
            self.scope.write(f':SOURCE1:MOD:AM:DEPTH {mod_depth}')
            self.scope.write(':SOURCE1:MOD:STATE ON')
            
            print(f"✅ AM modulation: {carrier_freq} Hz carrier, {mod_freq} Hz mod, {mod_depth}% depth")
            return True
            
        except Exception as e:
            print(f"❌ Failed to set AM modulation: {e}")
            return False
    
    def get_status(self):
        """Get current generator settings"""
        try:
            status = {}
            status['output'] = self.scope.query(':SOURCE1:OUTPUT?').strip()
            status['function'] = self.scope.query(':SOURCE1:FUNCTION?').strip()
            status['frequency'] = float(self.scope.query(':SOURCE1:FREQUENCY?').strip())
            status['amplitude'] = float(self.scope.query(':SOURCE1:VOLTAGE?').strip())
            
            # Try to get offset
            try:
                status['offset'] = float(self.scope.query(':SOURCE1:VOLTAGE:OFFSET?').strip())
            except:
                status['offset'] = 0.0
            
            # Get full apply string
            status['apply'] = self.scope.query(':SOURCE1:APPLY?').strip()
            
            return status
            
        except Exception as e:
            print(f"Error getting status: {e}")
            return None
    
    def audio_test_signals(self):
        """Generate common audio test signals"""
        print("\n🎵 AUDIO TEST SIGNAL MENU")
        print("-" * 40)
        print("1. 1kHz sine (standard test tone)")
        print("2. 440Hz sine (A4 tuning)")
        print("3. 20Hz-20kHz sweep (hearing test)")
        print("4. Pink noise")
        print("5. 1kHz square (harmonic test)")
        print("6. DTMF tones")
        print("7. Custom frequency")
        
        choice = input("\nSelect signal: ").strip()
        
        if choice == '1':
            self.set_sine(1000, 1.0)
        elif choice == '2':
            self.set_sine(440, 1.0)
        elif choice == '3':
            self.sweep_frequency(20, 20000, 10)
        elif choice == '4':
            self.set_noise(1.0)
        elif choice == '5':
            self.set_square(1000, 1.0)
        elif choice == '6':
            # DTMF example (would need two-tone generation)
            print("DTMF requires dual-tone - using 697Hz")
            self.set_sine(697, 1.0)
        elif choice == '7':
            freq = float(input("Frequency (Hz): "))
            amp = float(input("Amplitude (Vpp) [1.0]: ") or "1.0")
            self.set_sine(freq, amp)


def generator_wizard(scope):
    """Interactive waveform generator configuration"""
    gen = WaveformGenerator(scope)
    
    if not gen.is_available():
        print("❌ No waveform generator detected")
        print("   Your oscilloscope may not have the -S option")
        return
    
    print("\n" + "="*60)
    print("WAVEFORM GENERATOR CONTROL")
    print("="*60)
    
    # Get current status
    status = gen.get_status()
    if status:
        print("\nCurrent settings:")
        print(f"  Output: {status['output']}")
        print(f"  Function: {status['function']}")
        print(f"  Frequency: {status['frequency']} Hz")
        print(f"  Amplitude: {status['amplitude']} Vpp")
        print(f"  Offset: {status['offset']} V")
    
    print("\nWaveform types:")
    print("1. Sine wave")
    print("2. Square wave")
    print("3. Ramp/Triangle")
    print("4. Pulse")
    print("5. Noise")
    print("6. DC voltage")
    print("7. Audio test signals")
    print("8. Toggle output ON/OFF")
    print("0. Exit")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == '1':
        freq = float(input("Frequency (Hz) [1000]: ") or "1000")
        amp = float(input("Amplitude (Vpp) [1.0]: ") or "1.0")
        offset = float(input("Offset (V) [0]: ") or "0")
        gen.set_sine(freq, amp, offset)
        gen.enable()
        
    elif choice == '2':
        freq = float(input("Frequency (Hz) [1000]: ") or "1000")
        amp = float(input("Amplitude (Vpp) [1.0]: ") or "1.0")
        duty = float(input("Duty cycle (%) [50]: ") or "50")
        gen.set_square(freq, amp, duty_cycle=duty)
        gen.enable()
        
    elif choice == '7':
        gen.audio_test_signals()
        gen.enable()
        
    elif choice == '8':
        if status['output'] == 'ON':
            gen.disable()
        else:
            gen.enable()
    
    print("\n✅ Generator configured!")


if __name__ == "__main__":
    # Test the generator
    import pyvisa
    
    rm = pyvisa.ResourceManager('@py')
    scope = rm.open_resource('TCPIP::192.168.68.72::INSTR')
    scope.timeout = 5000
    
    generator_wizard(scope)
    
    scope.close()