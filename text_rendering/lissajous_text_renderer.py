"""
Main Lissajous Text Renderer
High-level interface for rendering text on oscilloscope
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple
from .hershey_font import HersheyFont
from .text_to_path import TextToPath
from .path_to_audio import PathToAudio


class LissajousTextRenderer:
    """
    Complete text rendering system for oscilloscope XY mode display
    """

    def __init__(self, sample_rate: int = 44100):
        """
        Initialize text renderer

        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.font = HersheyFont()
        self.text_to_path = TextToPath(self.font)
        self.path_to_audio = PathToAudio(sample_rate)

    def render_text(self, text: str,
                   duration: float = 1.0,
                   loop_count: int = 60) -> Tuple[np.ndarray, np.ndarray]:
        """
        Render text to audio signals

        Args:
            text: Text string to render
            duration: Duration per loop in seconds
            loop_count: Number of times to repeat (for persistence)

        Returns:
            Tuple of (left_channel, right_channel) audio arrays
        """
        # Convert text to path
        x_path, y_path = self.text_to_path.text_to_path(text)

        if len(x_path) == 0:
            print(f"⚠️  No renderable characters in '{text}'")
            return np.array([]), np.array([])

        # Convert path to audio
        left, right = self.path_to_audio.path_to_audio(
            x_path, y_path,
            duration=duration,
            loop_count=loop_count
        )

        return left, right

    def preview_text(self, text: str, show_points: bool = False):
        """
        Display preview of text rendering

        Args:
            text: Text to preview
            show_points: Show individual path points
        """
        x_path, y_path = self.text_to_path.text_to_path(text)

        if len(x_path) == 0:
            print(f"⚠️  No renderable characters in '{text}'")
            return

        plt.figure(figsize=(10, 8))

        if show_points:
            plt.plot(x_path, y_path, 'lime', linewidth=1.5, marker='o',
                    markersize=2, alpha=0.7)
        else:
            plt.plot(x_path, y_path, 'lime', linewidth=2)

        plt.title(f'Text Preview: "{text}"', fontsize=14, fontweight='bold')
        plt.xlabel('X (Channel 1)', fontsize=12)
        plt.ylabel('Y (Channel 2)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        plt.tight_layout()
        plt.show()

    def save_text_audio(self, text: str, filename: str,
                       duration: float = 1.0, loop_count: int = 60):
        """
        Save text as WAV audio file

        Args:
            text: Text to render
            filename: Output filename (should end in .wav)
            duration: Duration per loop
            loop_count: Number of loops
        """
        x_path, y_path = self.text_to_path.text_to_path(text)

        if len(x_path) == 0:
            print(f"⚠️  Cannot save empty text '{text}'")
            return

        self.path_to_audio.save_wav(x_path, y_path, filename, duration, loop_count)

    def get_text_stats(self, text: str) -> dict:
        """
        Get statistics about text rendering

        Args:
            text: Text to analyze

        Returns:
            Dictionary with rendering statistics
        """
        info = self.text_to_path.get_text_info(text)
        x_path, y_path = self.text_to_path.text_to_path(text)

        info['audio_samples_per_loop'] = len(x_path)
        info['recommended_duration'] = self.path_to_audio.calculate_audio_duration(len(x_path))

        return info

    def available_characters(self) -> str:
        """Get string of available characters"""
        chars = self.font.available_characters()
        return ''.join(chars)

    def render_text_to_audio(self, text: str,
                            scale: float = 1.0,
                            speed_scale: float = 1.0,
                            loop_count: int = 60) -> Tuple[np.ndarray, np.ndarray]:
        """
        Render text to audio with scaling options (for GUI)

        Args:
            text: Text to render
            scale: Font scale factor (affects size)
            speed_scale: Speed multiplier (affects duration)
            loop_count: Number of loops for persistence

        Returns:
            Tuple of (left_channel, right_channel) audio arrays
        """
        # Convert text to path
        x_path, y_path = self.text_to_path.text_to_path(text)

        if len(x_path) == 0:
            return np.array([]), np.array([])

        # Apply scaling
        x_path = np.array(x_path) * scale
        y_path = np.array(y_path) * scale

        # Calculate duration based on speed
        base_duration = self.path_to_audio.calculate_audio_duration(len(x_path))
        duration = base_duration * speed_scale

        # Convert path to audio
        left, right = self.path_to_audio.path_to_audio(
            x_path, y_path,
            duration=duration,
            loop_count=loop_count
        )

        return left, right

    def demo(self, text: str = "HELLO"):
        """
        Run a quick demo with preview

        Args:
            text: Text to demonstrate
        """
        print("=" * 60)
        print(f"Lissajous Text Rendering Demo: '{text}'")
        print("=" * 60)

        # Show stats
        stats = self.get_text_stats(text)
        print(f"\nText Statistics:")
        print(f"  Characters: {stats['character_count']}")
        print(f"  Strokes: {stats['stroke_count']}")
        print(f"  Total points: {stats['total_points']}")
        print(f"  Pen down: {stats['pen_down_points']}")
        print(f"  Pen up: {stats['pen_up_points']}")
        print(f"  Recommended duration: {stats['recommended_duration']:.3f}s")

        # Show available characters
        print(f"\nAvailable characters: {self.available_characters()}")

        # Preview
        print(f"\nShowing preview...")
        self.preview_text(text)
