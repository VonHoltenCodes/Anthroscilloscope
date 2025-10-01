"""
Signal generators for mock oscilloscope
Provides various test signal patterns for development without hardware
"""

from abc import ABC, abstractmethod
import numpy as np
from dataclasses import dataclass


@dataclass
class LissajousParams:
    """Parameters for Lissajous pattern generation"""
    freq_x: float = 3.0  # Frequency ratio for X axis
    freq_y: float = 2.0  # Frequency ratio for Y axis
    phase: float = 0.0   # Phase offset in radians
    amplitude_x: float = 1.0
    amplitude_y: float = 1.0


class SignalGenerator(ABC):
    """Abstract base class for signal generators"""

    @abstractmethod
    def generate_ch1(self, t: np.ndarray) -> np.ndarray:
        """Generate signal for channel 1 (X-axis)"""
        pass

    @abstractmethod
    def generate_ch2(self, t: np.ndarray) -> np.ndarray:
        """Generate signal for channel 2 (Y-axis)"""
        pass


class LissajousSignalGenerator(SignalGenerator):
    """Generate Lissajous pattern signals for XY display"""

    def __init__(self, freq_x: float = 3, freq_y: float = 2, phase: float = 0):
        self.freq_x = freq_x * 1000  # Convert to Hz
        self.freq_y = freq_y * 1000  # Convert to Hz
        self.phase = phase

    def generate_ch1(self, t: np.ndarray) -> np.ndarray:
        """Generate X-axis signal"""
        return np.sin(2 * np.pi * self.freq_x * t)

    def generate_ch2(self, t: np.ndarray) -> np.ndarray:
        """Generate Y-axis signal"""
        return np.sin(2 * np.pi * self.freq_y * t + self.phase)


class DefaultSignalGenerator(SignalGenerator):
    """Generate standard test signals"""

    def generate_ch1(self, t: np.ndarray) -> np.ndarray:
        """1 kHz sine wave"""
        return np.sin(2 * np.pi * 1000 * t)

    def generate_ch2(self, t: np.ndarray) -> np.ndarray:
        """2 kHz sine wave at half amplitude"""
        return 0.5 * np.sin(2 * np.pi * 2000 * t)


class CircleSignalGenerator(SignalGenerator):
    """Generate circular Lissajous pattern (1:1 ratio, 90° phase)"""

    def generate_ch1(self, t: np.ndarray) -> np.ndarray:
        return np.sin(2 * np.pi * 1000 * t)

    def generate_ch2(self, t: np.ndarray) -> np.ndarray:
        return np.sin(2 * np.pi * 1000 * t + np.pi/2)


class Figure8SignalGenerator(SignalGenerator):
    """Generate figure-8 Lissajous pattern (2:1 ratio)"""

    def generate_ch1(self, t: np.ndarray) -> np.ndarray:
        return np.sin(2 * np.pi * 2000 * t)

    def generate_ch2(self, t: np.ndarray) -> np.ndarray:
        return np.sin(2 * np.pi * 1000 * t)
