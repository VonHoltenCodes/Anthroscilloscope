"""
Mock oscilloscope implementation for development without hardware
Simulates Rigol DS1104Z Plus behavior for testing
"""

import numpy as np
from typing import Tuple, Optional
from .oscilloscope_interface import OscilloscopeInterface
from .signal_generators import SignalGenerator, DefaultSignalGenerator


class MockOscilloscope(OscilloscopeInterface):
    """Simulated oscilloscope for testing without hardware"""

    def __init__(self, signal_generator: Optional[SignalGenerator] = None):
        """
        Initialize mock oscilloscope

        Args:
            signal_generator: Optional signal generator for custom waveforms
        """
        self.signal_generator = signal_generator or DefaultSignalGenerator()
        self.connected = False
        self.channels = {1: True, 2: True, 3: False, 4: False}
        self.xy_mode = False
        self.timebase_scale = 1e-3  # 1ms/div
        self.sample_rate = 1e9  # 1 GSa/s (matches Rigol DS1104Z Plus)
        self.channel_settings = {
            1: {'scale': 1.0, 'offset': 0.0, 'coupling': 'DC'},
            2: {'scale': 1.0, 'offset': 0.0, 'coupling': 'DC'},
            3: {'scale': 1.0, 'offset': 0.0, 'coupling': 'DC'},
            4: {'scale': 1.0, 'offset': 0.0, 'coupling': 'DC'},
        }

    def connect(self) -> bool:
        """Establish mock connection"""
        self.connected = True
        print("✅ Connected to MOCK oscilloscope (simulation mode)")
        return True

    def disconnect(self):
        """Close mock connection"""
        self.connected = False
        print("🔌 Disconnected from mock oscilloscope")

    def get_waveform_data(self, channel: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic waveform data

        Args:
            channel: Channel number (1-4)

        Returns:
            Tuple of (time_array, voltage_array)
        """
        if not self.connected:
            raise ConnectionError("Mock oscilloscope not connected")

        if channel not in self.channels or not self.channels[channel]:
            raise ValueError(f"Channel {channel} not enabled")

        # Generate 1200 points (typical for Rigol)
        points = 1200
        t = np.linspace(0, 10 * self.timebase_scale, points)

        # Generate signal based on channel
        if channel == 1:
            voltage = self.signal_generator.generate_ch1(t)
        elif channel == 2:
            voltage = self.signal_generator.generate_ch2(t)
        else:
            # Default sine wave for other channels
            voltage = np.sin(2 * np.pi * 1000 * t)

        # Add realistic noise (1% of signal)
        voltage += np.random.normal(0, 0.01, len(voltage))

        # Apply channel settings
        voltage = voltage * self.channel_settings[channel]['scale']
        voltage = voltage + self.channel_settings[channel]['offset']

        return t, voltage

    def get_measurement(self, channel: int, measurement_type: str) -> float:
        """
        Return simulated measurements

        Args:
            channel: Channel number
            measurement_type: Type of measurement

        Returns:
            Measurement value
        """
        t, v = self.get_waveform_data(channel)

        measurements = {
            'VPP': np.ptp(v),           # Peak-to-peak voltage
            'VMAX': np.max(v),          # Maximum voltage
            'VMIN': np.min(v),          # Minimum voltage
            'VAVG': np.mean(v),         # Average voltage
            'VRMS': np.sqrt(np.mean(v**2)),  # RMS voltage
            'FREQ': 1000.0,             # Frequency in Hz
            'PER': 0.001,               # Period in seconds
            'RISE': 1e-6,               # Rise time
            'FALL': 1e-6,               # Fall time
        }

        return measurements.get(measurement_type.upper(), 0.0)

    def query(self, command: str) -> str:
        """
        Simulate SCPI command responses

        Args:
            command: SCPI command string

        Returns:
            Simulated response
        """
        if not self.connected:
            raise ConnectionError("Mock oscilloscope not connected")

        command = command.strip()

        # Identification
        if '*IDN?' in command:
            return 'MOCK,OSCILLOSCOPE,SIM001,v1.0.0'

        # Timebase mode
        if ':TIMebase:MODE?' in command:
            return 'XY' if self.xy_mode else 'MAIN'

        # Channel display status
        for ch in range(1, 5):
            if f':CHANnel{ch}:DISPlay?' in command:
                return '1' if self.channels[ch] else '0'

        # Channel scale
        for ch in range(1, 5):
            if f':CHANnel{ch}:SCALe?' in command:
                return str(self.channel_settings[ch]['scale'])

        # Timebase scale
        if ':TIMebase:SCALe?' in command:
            return str(self.timebase_scale)

        # Default response
        return 'OK'

    def write(self, command: str):
        """
        Simulate SCPI command writes

        Args:
            command: SCPI command string
        """
        if not self.connected:
            raise ConnectionError("Mock oscilloscope not connected")

        command = command.strip()

        # XY mode control
        if ':TIMebase:MODE XY' in command:
            self.xy_mode = True
        elif ':TIMebase:MODE MAIN' in command:
            self.xy_mode = False

        # Channel enable/disable
        for ch in range(1, 5):
            if f':CHANnel{ch}:DISPlay ON' in command:
                self.channels[ch] = True
            elif f':CHANnel{ch}:DISPlay OFF' in command:
                self.channels[ch] = False

        # Channel scale
        for ch in range(1, 5):
            if f':CHANnel{ch}:SCALe' in command:
                try:
                    value = float(command.split()[-1])
                    self.channel_settings[ch]['scale'] = value
                except:
                    pass

    def enable_xy_mode(self) -> bool:
        """Enable XY display mode"""
        if not self.connected:
            return False
        self.xy_mode = True
        print("✅ Mock XY mode enabled")
        return True

    def disable_xy_mode(self) -> bool:
        """Return to normal YT mode"""
        if not self.connected:
            return False
        self.xy_mode = False
        print("✅ Mock returned to YT mode")
        return True

    def is_xy_mode(self) -> bool:
        """Check if XY mode is enabled"""
        return self.xy_mode

    def set_signal_generator(self, generator: SignalGenerator):
        """Change the signal generator for different patterns"""
        self.signal_generator = generator
