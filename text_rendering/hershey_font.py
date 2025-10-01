"""
Hershey Font Loader
Loads and manages Hershey vector fonts for oscilloscope text rendering
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass


@dataclass
class CharacterStroke:
    """Represents a single stroke (line segment) in a character"""
    x1: float
    y1: float
    x2: float
    y2: float
    pen_up: bool = False  # True if this is a pen-up movement


@dataclass
class Character:
    """Represents a complete character with all its strokes"""
    char: str
    strokes: List[CharacterStroke]
    width: float
    left_bearing: float = 0.0
    right_bearing: float = 0.0


class HersheyFont:
    """
    Hershey font manager for vector-based character rendering
    Uses simplified Hershey font data for oscilloscope display
    """

    def __init__(self):
        self.characters: Dict[str, Character] = {}
        self._load_basic_font()

    def _load_basic_font(self):
        """Load basic ASCII characters (simplified Hershey Simplex style)"""

        # For now, we'll define a few simple characters manually
        # In Phase 2, we'll integrate the full Hershey-Fonts library

        # Letter 'I' - Simple vertical line
        self.characters['I'] = Character(
            char='I',
            strokes=[
                CharacterStroke(0, -9, 0, 9),  # Vertical line
                CharacterStroke(-2, -9, 2, -9),  # Top serif
                CharacterStroke(-2, 9, 2, 9),    # Bottom serif
            ],
            width=4
        )

        # Letter 'L' - Vertical line with horizontal base
        self.characters['L'] = Character(
            char='L',
            strokes=[
                CharacterStroke(0, -9, 0, 9),   # Vertical line
                CharacterStroke(0, 9, 6, 9),    # Horizontal base
            ],
            width=7
        )

        # Letter 'T' - Horizontal top with vertical stem
        self.characters['T'] = Character(
            char='T',
            strokes=[
                CharacterStroke(-4, -9, 4, -9),  # Horizontal top
                CharacterStroke(0, -9, 0, 9),    # Vertical stem
            ],
            width=8
        )

        # Letter 'O' - Circle (approximated with line segments)
        o_strokes = []
        segments = 16
        radius = 6
        for i in range(segments):
            angle1 = 2 * np.pi * i / segments
            angle2 = 2 * np.pi * (i + 1) / segments
            x1 = radius * np.cos(angle1)
            y1 = radius * np.sin(angle1)
            x2 = radius * np.cos(angle2)
            y2 = radius * np.sin(angle2)
            o_strokes.append(CharacterStroke(x1, y1, x2, y2))

        self.characters['O'] = Character(
            char='O',
            strokes=o_strokes,
            width=13
        )

        # Letter 'H' - Two verticals with horizontal crossbar
        self.characters['H'] = Character(
            char='H',
            strokes=[
                CharacterStroke(-3, -9, -3, 9),  # Left vertical
                CharacterStroke(3, -9, 3, 9),    # Right vertical
                CharacterStroke(-3, 0, 3, 0),    # Horizontal crossbar
            ],
            width=7
        )

        # Letter 'E' - Vertical with three horizontals
        self.characters['E'] = Character(
            char='E',
            strokes=[
                CharacterStroke(0, -9, 0, 9),    # Vertical
                CharacterStroke(0, -9, 6, -9),   # Top horizontal
                CharacterStroke(0, 0, 5, 0),     # Middle horizontal
                CharacterStroke(0, 9, 6, 9),     # Bottom horizontal
            ],
            width=7
        )

        # Letter 'A' - Two diagonals with crossbar
        self.characters['A'] = Character(
            char='A',
            strokes=[
                CharacterStroke(0, -9, -4, 9),   # Left diagonal
                CharacterStroke(0, -9, 4, 9),    # Right diagonal
                CharacterStroke(-2, 3, 2, 3),    # Crossbar
            ],
            width=9
        )

        # Space character
        self.characters[' '] = Character(
            char=' ',
            strokes=[],
            width=5
        )

    def get_character(self, char: str) -> Optional[Character]:
        """
        Get character data

        Args:
            char: Character to retrieve

        Returns:
            Character object or None if not found
        """
        # Convert to uppercase for now (we only have uppercase defined)
        char = char.upper()
        return self.characters.get(char, None)

    def has_character(self, char: str) -> bool:
        """Check if character is available"""
        return char.upper() in self.characters

    def get_text_width(self, text: str, spacing: float = 2.0) -> float:
        """
        Calculate total width of text string

        Args:
            text: Text string
            spacing: Additional spacing between characters

        Returns:
            Total width in font units
        """
        width = 0
        for char in text:
            char_data = self.get_character(char)
            if char_data:
                width += char_data.width + spacing
        return width - spacing if width > 0 else 0

    def available_characters(self) -> List[str]:
        """Get list of available characters"""
        return sorted(self.characters.keys())


def normalize_strokes(strokes: List[CharacterStroke],
                     target_range: Tuple[float, float] = (-1.0, 1.0)) -> List[CharacterStroke]:
    """
    Normalize stroke coordinates to target range

    Args:
        strokes: List of character strokes
        target_range: Tuple of (min, max) for output range

    Returns:
        List of normalized strokes
    """
    if not strokes:
        return []

    # Find bounding box
    all_x = []
    all_y = []
    for stroke in strokes:
        all_x.extend([stroke.x1, stroke.x2])
        all_y.extend([stroke.y1, stroke.y2])

    x_min, x_max = min(all_x), max(all_x)
    y_min, y_max = min(all_y), max(all_y)

    # Normalize to [0, 1]
    x_range = x_max - x_min if x_max > x_min else 1
    y_range = y_max - y_min if y_max > y_min else 1

    def normalize_coord(val, val_min, val_range):
        norm = (val - val_min) / val_range
        scale = target_range[1] - target_range[0]
        return norm * scale + target_range[0]

    normalized = []
    for stroke in strokes:
        normalized.append(CharacterStroke(
            x1=normalize_coord(stroke.x1, x_min, x_range),
            y1=normalize_coord(stroke.y1, y_min, y_range),
            x2=normalize_coord(stroke.x2, x_min, x_range),
            y2=normalize_coord(stroke.y2, y_min, y_range),
            pen_up=stroke.pen_up
        ))

    return normalized
