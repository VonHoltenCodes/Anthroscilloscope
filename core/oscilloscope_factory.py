"""
Factory for creating oscilloscope instances
Provides convenient switching between hardware and mock implementations
"""

import os
from typing import Optional
from .oscilloscope_interface import OscilloscopeInterface
from .mock_oscilloscope import MockOscilloscope
from .signal_generators import SignalGenerator


def create_oscilloscope(
    ip_address: Optional[str] = None,
    mock: bool = False,
    signal_generator: Optional[SignalGenerator] = None
) -> OscilloscopeInterface:
    """
    Factory function to create oscilloscope instance

    Args:
        ip_address: IP address of hardware oscilloscope (e.g., '192.168.1.100')
        mock: Force mock mode even if IP provided
        signal_generator: Optional signal generator for mock mode

    Returns:
        OscilloscopeInterface implementation (either hardware or mock)

    Examples:
        # Create mock oscilloscope
        scope = create_oscilloscope(mock=True)

        # Create hardware oscilloscope
        scope = create_oscilloscope(ip_address='192.168.1.100')

        # Use environment variable
        os.environ['ANTHRO_MOCK'] = 'true'
        scope = create_oscilloscope()  # Will be mock
    """

    # Check environment variable for mock mode
    env_mock = os.getenv('ANTHRO_MOCK', 'false').lower() == 'true'

    # Determine if we should use mock
    use_mock = mock or env_mock or (ip_address is None)

    if use_mock:
        print("🔧 Creating mock oscilloscope for development")
        return MockOscilloscope(signal_generator=signal_generator)
    else:
        print(f"🔌 Connecting to hardware oscilloscope at {ip_address}")
        # Import here to avoid dependency if mock mode
        try:
            import pyvisa
            from ..rigol_oscilloscope_control import RigolDS1104Z
            return RigolDS1104Z(ip_address)
        except ImportError as e:
            print(f"⚠️  Hardware dependencies not available: {e}")
            print("🔧 Falling back to mock oscilloscope")
            return MockOscilloscope(signal_generator=signal_generator)
