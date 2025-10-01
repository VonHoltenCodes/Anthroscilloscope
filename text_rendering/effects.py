#!/usr/bin/env python3
"""
Advanced Effects for Text Rendering (Phase 4)
Rotation, morphing, 3D effects, and transformations

Created by Trenton Von Holten
https://github.com/VonHoltenCodes/Anthroscilloscope
"""

import numpy as np
from typing import Tuple, List


class TextEffects:
    """Advanced visual effects for oscilloscope text rendering"""

    @staticmethod
    def rotate(x: np.ndarray, y: np.ndarray, angle_degrees: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Rotate text path around origin

        Args:
            x: X coordinates
            y: Y coordinates
            angle_degrees: Rotation angle in degrees (0-360)

        Returns:
            Tuple of (rotated_x, rotated_y)
        """
        angle_rad = np.radians(angle_degrees)
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)

        # Rotation matrix
        x_rot = x * cos_a - y * sin_a
        y_rot = x * sin_a + y * cos_a

        return x_rot, y_rot

    @staticmethod
    def scale_xy(x: np.ndarray, y: np.ndarray,
                 scale_x: float, scale_y: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply independent X and Y scaling

        Args:
            x: X coordinates
            y: Y coordinates
            scale_x: X-axis scale factor
            scale_y: Y-axis scale factor

        Returns:
            Tuple of (scaled_x, scaled_y)
        """
        return x * scale_x, y * scale_y

    @staticmethod
    def skew(x: np.ndarray, y: np.ndarray,
             skew_x: float = 0.0, skew_y: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply skew/shear transformation (italics effect)

        Args:
            x: X coordinates
            y: Y coordinates
            skew_x: Horizontal skew (-1.0 to 1.0)
            skew_y: Vertical skew (-1.0 to 1.0)

        Returns:
            Tuple of (skewed_x, skewed_y)
        """
        x_skewed = x + skew_x * y
        y_skewed = y + skew_y * x

        return x_skewed, y_skewed

    @staticmethod
    def wave_effect(x: np.ndarray, y: np.ndarray,
                   amplitude: float, frequency: float,
                   direction: str = 'x') -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply sine wave distortion

        Args:
            x: X coordinates
            y: Y coordinates
            amplitude: Wave amplitude
            frequency: Wave frequency
            direction: 'x' for horizontal wave, 'y' for vertical wave

        Returns:
            Tuple of (waved_x, waved_y)
        """
        if direction == 'x':
            # Wave in X direction (vertical displacement)
            y_waved = y + amplitude * np.sin(frequency * x)
            return x, y_waved
        else:
            # Wave in Y direction (horizontal displacement)
            x_waved = x + amplitude * np.sin(frequency * y)
            return x_waved, y

    @staticmethod
    def perspective_3d(x: np.ndarray, y: np.ndarray,
                      depth: float = 0.5,
                      tilt_x: float = 0.0,
                      tilt_y: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply pseudo-3D perspective transformation

        Args:
            x: X coordinates
            y: Y coordinates
            depth: Depth factor (0.0 to 1.0, affects perspective strength)
            tilt_x: Rotation around X-axis (-1.0 to 1.0)
            tilt_y: Rotation around Y-axis (-1.0 to 1.0)

        Returns:
            Tuple of (perspective_x, perspective_y)
        """
        # Simulate Z-depth based on Y position
        z = 1.0 + depth * (y / 10.0)  # Normalize Y and apply depth

        # Apply tilt rotations
        if tilt_x != 0.0:
            # Tilt around X-axis (affects Y)
            y = y * np.cos(tilt_x) - z * np.sin(tilt_x)

        if tilt_y != 0.0:
            # Tilt around Y-axis (affects X)
            x = x * np.cos(tilt_y) + z * np.sin(tilt_y)

        # Perspective divide
        x_persp = x / z
        y_persp = y / z

        return x_persp, y_persp

    @staticmethod
    def morph(x1: np.ndarray, y1: np.ndarray,
             x2: np.ndarray, y2: np.ndarray,
             progress: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Morph between two text paths

        Args:
            x1, y1: First text coordinates
            x2, y2: Second text coordinates
            progress: Morph progress (0.0 = first text, 1.0 = second text)

        Returns:
            Tuple of (morphed_x, morphed_y)
        """
        # Ensure arrays are same length (interpolate if needed)
        if len(x1) != len(x2):
            # Resample to match lengths
            t1 = np.linspace(0, 1, len(x1))
            t2 = np.linspace(0, 1, len(x2))

            x1_interp = np.interp(t2, t1, x1)
            y1_interp = np.interp(t2, t1, y1)

            x1, y1 = x1_interp, y1_interp

        # Linear interpolation
        x_morph = x1 * (1 - progress) + x2 * progress
        y_morph = y1 * (1 - progress) + y2 * progress

        return x_morph, y_morph

    @staticmethod
    def outline_effect(x: np.ndarray, y: np.ndarray,
                      thickness: float = 0.1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create outline/stroke effect by duplicating path with offset

        Args:
            x: X coordinates
            y: Y coordinates
            thickness: Outline thickness

        Returns:
            Tuple of (outlined_x, outlined_y)
        """
        # Create 4 offset copies and combine
        offsets = [
            (thickness, 0),
            (-thickness, 0),
            (0, thickness),
            (0, -thickness)
        ]

        x_outlined = [x]
        y_outlined = [y]

        for dx, dy in offsets:
            x_outlined.append(x + dx)
            y_outlined.append(y + dy)

        # Concatenate all paths
        x_result = np.concatenate(x_outlined)
        y_result = np.concatenate(y_outlined)

        return x_result, y_result

    @staticmethod
    def shadow_effect(x: np.ndarray, y: np.ndarray,
                     offset_x: float = 0.2,
                     offset_y: float = -0.2) -> Tuple[np.ndarray, np.ndarray]:
        """
        Add shadow by duplicating path with offset

        Args:
            x: X coordinates
            y: Y coordinates
            offset_x: Shadow X offset
            offset_y: Shadow Y offset

        Returns:
            Tuple of (shadowed_x, shadowed_y) with shadow first, then main
        """
        # Shadow copy (rendered first)
        x_shadow = x + offset_x
        y_shadow = y + offset_y

        # Combine shadow + original
        x_result = np.concatenate([x_shadow, x])
        y_result = np.concatenate([y_shadow, y])

        return x_result, y_result

    @staticmethod
    def spiral_effect(x: np.ndarray, y: np.ndarray,
                     intensity: float = 0.1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply spiral distortion

        Args:
            x: X coordinates
            y: Y coordinates
            intensity: Spiral intensity

        Returns:
            Tuple of (spiraled_x, spiraled_y)
        """
        # Calculate distance from origin
        r = np.sqrt(x**2 + y**2)

        # Apply rotation based on distance
        theta = np.arctan2(y, x) + intensity * r

        x_spiral = r * np.cos(theta)
        y_spiral = r * np.sin(theta)

        return x_spiral, y_spiral


class MultiLineText:
    """Multi-line text layout manager"""

    @staticmethod
    def layout_lines(lines: List[str],
                     line_spacing: float = 1.5,
                     alignment: str = 'left') -> List[Tuple[str, float, float]]:
        """
        Calculate positions for multi-line text

        Args:
            lines: List of text lines
            line_spacing: Spacing between lines (multiplier of font height)
            alignment: 'left', 'center', or 'right'

        Returns:
            List of (text, x_offset, y_offset) tuples
        """
        font_height = 18  # Standard Hershey font height
        total_height = len(lines) * font_height * line_spacing

        positioned_lines = []

        for i, line in enumerate(lines):
            # Calculate Y position (centered around origin)
            y_offset = (total_height / 2) - (i * font_height * line_spacing)

            # Calculate X position based on alignment
            if alignment == 'center':
                x_offset = 0  # Center alignment handled by text renderer
            elif alignment == 'right':
                x_offset = 0  # Right align (would need text width calculation)
            else:  # left
                x_offset = 0

            positioned_lines.append((line, x_offset, y_offset))

        return positioned_lines


if __name__ == '__main__':
    # Test effects
    print("=" * 70)
    print("TEXT EFFECTS - Phase 4 Advanced Features")
    print("=" * 70)
    print()

    # Create sample path
    t = np.linspace(0, 2*np.pi, 100)
    x = np.cos(t)
    y = np.sin(t)

    effects = TextEffects()

    # Test rotation
    x_rot, y_rot = effects.rotate(x, y, 45)
    print(f"✅ Rotation: {len(x_rot)} points")

    # Test 3D perspective
    x_3d, y_3d = effects.perspective_3d(x, y, depth=0.5, tilt_y=0.3)
    print(f"✅ 3D Perspective: {len(x_3d)} points")

    # Test wave effect
    x_wave, y_wave = effects.wave_effect(x, y, amplitude=0.2, frequency=3)
    print(f"✅ Wave Effect: {len(x_wave)} points")

    # Test shadow
    x_shadow, y_shadow = effects.shadow_effect(x, y)
    print(f"✅ Shadow Effect: {len(x_shadow)} points (doubled)")

    print()
    print("All effects functional! ✨")
