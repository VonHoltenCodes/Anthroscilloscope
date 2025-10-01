"""
Text to Path Converter
Converts text strings into continuous paths for oscilloscope rendering
"""

import numpy as np
from typing import List, Tuple
from dataclasses import dataclass
from .hershey_font import HersheyFont, CharacterStroke


@dataclass
class PathPoint:
    """A single point in a path"""
    x: float
    y: float
    pen_down: bool = True  # False for pen-up movements


class TextToPath:
    """
    Converts text strings to drawable paths suitable for XY oscilloscope display
    """

    def __init__(self, font: HersheyFont = None):
        """
        Initialize text to path converter

        Args:
            font: HersheyFont instance (creates default if None)
        """
        self.font = font or HersheyFont()
        self.char_spacing = 2.0  # Space between characters
        self.line_spacing = 5.0  # Space between lines

    def text_to_strokes(self, text: str) -> List[CharacterStroke]:
        """
        Convert text to list of strokes with proper positioning

        Args:
            text: Text string to convert

        Returns:
            List of positioned strokes for entire text
        """
        all_strokes = []
        x_offset = 0

        for char in text:
            char_data = self.font.get_character(char)

            if char_data is None:
                # Skip unknown characters
                continue

            if not char_data.strokes:
                # Space or empty character
                x_offset += char_data.width + self.char_spacing
                continue

            # Add strokes with x_offset applied
            for stroke in char_data.strokes:
                offset_stroke = CharacterStroke(
                    x1=stroke.x1 + x_offset,
                    y1=stroke.y1,
                    x2=stroke.x2 + x_offset,
                    y2=stroke.y2,
                    pen_up=stroke.pen_up
                )
                all_strokes.append(offset_stroke)

            # Advance cursor
            x_offset += char_data.width + self.char_spacing

        return all_strokes

    def strokes_to_path_points(self, strokes: List[CharacterStroke],
                               points_per_stroke: int = 10) -> List[PathPoint]:
        """
        Convert strokes to sequence of path points with interpolation

        Args:
            strokes: List of character strokes
            points_per_stroke: Number of interpolation points per stroke

        Returns:
            List of path points forming continuous path
        """
        if not strokes:
            return []

        path_points = []
        current_pos = None

        for stroke in strokes:
            # Check if we need to move pen (discontinuous)
            if current_pos is None or \
               not np.isclose(current_pos[0], stroke.x1) or \
               not np.isclose(current_pos[1], stroke.y1):
                # Pen up movement to start of stroke
                if current_pos is not None:
                    # Add rapid transition points (pen up)
                    transition_points = 5
                    t = np.linspace(0, 1, transition_points)
                    for ti in t[1:]:  # Skip first point (already there)
                        x = current_pos[0] + ti * (stroke.x1 - current_pos[0])
                        y = current_pos[1] + ti * (stroke.y1 - current_pos[1])
                        path_points.append(PathPoint(x, y, pen_down=False))

            # Interpolate along stroke
            t = np.linspace(0, 1, points_per_stroke)
            for ti in t:
                x = stroke.x1 + ti * (stroke.x2 - stroke.x1)
                y = stroke.y1 + ti * (stroke.y2 - stroke.y1)
                path_points.append(PathPoint(x, y, pen_down=not stroke.pen_up))

            current_pos = (stroke.x2, stroke.y2)

        return path_points

    def text_to_path(self, text: str,
                    normalize: bool = True,
                    center: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert text to XY path arrays

        Args:
            text: Text string to convert
            normalize: Normalize coordinates to [-1, 1] range
            center: Center the text at origin

        Returns:
            Tuple of (x_array, y_array) for path
        """
        # Convert text to strokes
        strokes = self.text_to_strokes(text)

        if not strokes:
            # Return empty arrays for empty text
            return np.array([]), np.array([])

        # Convert to path points
        path_points = self.strokes_to_path_points(strokes)

        # Extract x and y coordinates
        x_coords = np.array([p.x for p in path_points])
        y_coords = np.array([p.y for p in path_points])

        # Normalize if requested
        if normalize:
            # Find bounds
            x_min, x_max = x_coords.min(), x_coords.max()
            y_min, y_max = y_coords.min(), y_coords.max()

            x_range = x_max - x_min if x_max > x_min else 1
            y_range = y_max - y_min if y_max > y_min else 1

            # Use larger range to maintain aspect ratio
            max_range = max(x_range, y_range)

            # Normalize to [-1, 1] maintaining aspect ratio
            x_coords = 2 * (x_coords - x_min) / max_range - 1
            y_coords = 2 * (y_coords - y_min) / max_range - 1

        # Center if requested
        if center:
            x_coords = x_coords - np.mean(x_coords)
            y_coords = y_coords - np.mean(y_coords)

        return x_coords, y_coords

    def get_text_info(self, text: str) -> dict:
        """
        Get information about text rendering

        Args:
            text: Text string

        Returns:
            Dictionary with text metrics
        """
        strokes = self.text_to_strokes(text)
        path_points = self.strokes_to_path_points(strokes)

        pen_down_points = sum(1 for p in path_points if p.pen_down)
        pen_up_points = sum(1 for p in path_points if not p.pen_down)

        return {
            'character_count': len(text),
            'stroke_count': len(strokes),
            'total_points': len(path_points),
            'pen_down_points': pen_down_points,
            'pen_up_points': pen_up_points,
            'estimated_width': self.font.get_text_width(text, self.char_spacing)
        }
