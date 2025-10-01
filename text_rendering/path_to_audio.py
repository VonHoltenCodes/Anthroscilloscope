"""
Path to Audio Converter
Converts XY path data into stereo audio signals for oscilloscope display
"""

import numpy as np
from typing import Tuple
from scipy import signal


class PathToAudio:
    """
    Converts path coordinates to stereo audio signals
    Left channel = X axis, Right channel = Y axis
    """

    def __init__(self, sample_rate: int = 44100):
        """
        Initialize path to audio converter

        Args:
            sample_rate: Audio sample rate in Hz (default 44.1kHz)
        """
        self.sample_rate = sample_rate

    def path_to_audio(self,
                     x_path: np.ndarray,
                     y_path: np.ndarray,
                     duration: float = 1.0,
                     loop_count: int = 1,
                     smooth: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert XY path to stereo audio signals

        Args:
            x_path: X coordinates of path
            y_path: Y coordinates of path
            duration: Duration in seconds for one loop
            loop_count: Number of times to repeat the pattern
            smooth: Apply smoothing filter to reduce harsh transitions

        Returns:
            Tuple of (left_channel, right_channel) audio arrays
        """
        if len(x_path) == 0 or len(y_path) == 0:
            # Return silence for empty paths
            samples = int(duration * self.sample_rate)
            return np.zeros(samples), np.zeros(samples)

        # Calculate number of samples for one loop
        samples_per_loop = int(duration * self.sample_rate)

        # Resample path to match audio sample rate
        path_length = len(x_path)
        time_original = np.linspace(0, 1, path_length)
        time_resampled = np.linspace(0, 1, samples_per_loop)

        x_resampled = np.interp(time_resampled, time_original, x_path)
        y_resampled = np.interp(time_resampled, time_original, y_path)

        # Apply smoothing if requested
        if smooth:
            # Low-pass filter to smooth transitions
            # Cutoff at Nyquist/10 (about 2.2kHz for 44.1kHz sample rate)
            cutoff = self.sample_rate / 20
            sos = signal.butter(4, cutoff, 'low', fs=self.sample_rate, output='sos')
            x_resampled = signal.sosfilt(sos, x_resampled)
            y_resampled = signal.sosfilt(sos, y_resampled)

        # Ensure values are in [-1, 1] range
        x_audio = np.clip(x_resampled, -1.0, 1.0)
        y_audio = np.clip(y_resampled, -1.0, 1.0)

        # Loop if requested
        if loop_count > 1:
            x_audio = np.tile(x_audio, loop_count)
            y_audio = np.tile(y_audio, loop_count)

        return x_audio, y_audio

    def path_to_stereo(self,
                      x_path: np.ndarray,
                      y_path: np.ndarray,
                      duration: float = 1.0,
                      loop_count: int = 1) -> np.ndarray:
        """
        Convert XY path to interleaved stereo audio

        Args:
            x_path: X coordinates
            y_path: Y coordinates
            duration: Duration in seconds
            loop_count: Number of loops

        Returns:
            Stereo audio array with shape (samples, 2)
        """
        left, right = self.path_to_audio(x_path, y_path, duration, loop_count)
        stereo = np.column_stack([left, right])
        return stereo

    def save_wav(self,
                x_path: np.ndarray,
                y_path: np.ndarray,
                filename: str,
                duration: float = 1.0,
                loop_count: int = 1):
        """
        Save path as WAV file

        Args:
            x_path: X coordinates
            y_path: Y coordinates
            filename: Output WAV filename
            duration: Duration in seconds
            loop_count: Number of loops
        """
        from scipy.io import wavfile

        stereo = self.path_to_stereo(x_path, y_path, duration, loop_count)

        # Convert to int16 format
        audio_int16 = (stereo * 32767).astype(np.int16)

        # Save WAV file
        wavfile.write(filename, self.sample_rate, audio_int16)
        print(f"✅ Saved audio to {filename}")

    def calculate_audio_duration(self, path_length: int,
                                points_per_second: int = 5000) -> float:
        """
        Calculate appropriate audio duration for given path

        Args:
            path_length: Number of points in path
            points_per_second: Target rendering speed

        Returns:
            Recommended duration in seconds
        """
        return path_length / points_per_second
