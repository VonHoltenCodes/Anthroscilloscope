"""
Unit tests for mock oscilloscope implementation
"""

import pytest
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.mock_oscilloscope import MockOscilloscope
from core.signal_generators import (
    LissajousSignalGenerator,
    CircleSignalGenerator,
    Figure8SignalGenerator
)


def test_mock_connection():
    """Test mock oscilloscope connection"""
    mock = MockOscilloscope()
    assert mock.connect() == True
    assert mock.connected == True
    mock.disconnect()
    assert mock.connected == False


def test_waveform_generation():
    """Test waveform data generation"""
    mock = MockOscilloscope()
    mock.connect()

    t, v = mock.get_waveform_data(1)

    assert len(t) == 1200  # Standard Rigol point count
    assert len(v) == 1200
    assert isinstance(t, np.ndarray)
    assert isinstance(v, np.ndarray)


def test_measurements():
    """Test measurement calculations"""
    mock = MockOscilloscope()
    mock.connect()

    freq = mock.get_measurement(1, 'FREQ')
    assert freq == 1000.0

    vpp = mock.get_measurement(1, 'VPP')
    assert vpp > 0


def test_xy_mode():
    """Test XY mode control"""
    mock = MockOscilloscope()
    mock.connect()

    assert mock.is_xy_mode() == False

    mock.enable_xy_mode()
    assert mock.is_xy_mode() == True

    mock.disable_xy_mode()
    assert mock.is_xy_mode() == False


def test_scpi_commands():
    """Test SCPI command simulation"""
    mock = MockOscilloscope()
    mock.connect()

    # Test query
    idn = mock.query('*IDN?')
    assert 'MOCK' in idn

    # Test write
    mock.write(':TIMebase:MODE XY')
    assert mock.is_xy_mode() == True

    mode = mock.query(':TIMebase:MODE?')
    assert mode == 'XY'


def test_lissajous_generator():
    """Test Lissajous signal generator"""
    gen = LissajousSignalGenerator(freq_x=3, freq_y=2, phase=0)
    mock = MockOscilloscope(signal_generator=gen)
    mock.connect()

    t1, v1 = mock.get_waveform_data(1)
    t2, v2 = mock.get_waveform_data(2)

    # Signals should be different (different frequencies)
    assert not np.allclose(v1, v2)


def test_circle_generator():
    """Test circle pattern generator"""
    gen = CircleSignalGenerator()
    mock = MockOscilloscope(signal_generator=gen)
    mock.connect()

    t1, v1 = mock.get_waveform_data(1)
    t2, v2 = mock.get_waveform_data(2)

    # For a circle, amplitudes should be similar
    assert np.abs(np.ptp(v1) - np.ptp(v2)) < 0.2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
