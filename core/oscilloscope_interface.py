"""
Abstract base class for oscilloscope implementations
Defines the interface that all oscilloscope types must implement
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional
import numpy as np


class OscilloscopeInterface(ABC):
    """Abstract interface for oscilloscope control"""

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to oscilloscope
        Returns True if successful, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self):
        """Close connection to oscilloscope"""
        pass

    @abstractmethod
    def get_waveform_data(self, channel: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Capture waveform data from specified channel

        Args:
            channel: Channel number (1-4)

        Returns:
            Tuple of (time_array, voltage_array)
        """
        pass

    @abstractmethod
    def get_measurement(self, channel: int, measurement_type: str) -> float:
        """
        Get measurement from channel

        Args:
            channel: Channel number (1-4)
            measurement_type: Type of measurement (VPP, VMAX, VMIN, VAVG, VRMS, FREQ, PER)

        Returns:
            Measurement value
        """
        pass

    @abstractmethod
    def query(self, command: str) -> str:
        """
        Send SCPI query command and return response

        Args:
            command: SCPI command string

        Returns:
            Response string from oscilloscope
        """
        pass

    @abstractmethod
    def write(self, command: str):
        """
        Send SCPI write command

        Args:
            command: SCPI command string
        """
        pass

    @abstractmethod
    def enable_xy_mode(self) -> bool:
        """Enable XY display mode"""
        pass

    @abstractmethod
    def disable_xy_mode(self) -> bool:
        """Return to normal YT (time) mode"""
        pass

    @abstractmethod
    def is_xy_mode(self) -> bool:
        """Check if XY mode is currently enabled"""
        pass
