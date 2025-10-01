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

        # Letter 'L' - Vertical line with horizontal base (FIXED: flipped Y)
        self.characters['L'] = Character(
            char='L',
            strokes=[
                CharacterStroke(0, 9, 0, -9),   # Vertical line (top to bottom)
                CharacterStroke(0, -9, 6, -9),  # Horizontal base (at bottom)
            ],
            width=7
        )

        # Letter 'T' - Horizontal top with vertical stem (FIXED: flipped Y)
        self.characters['T'] = Character(
            char='T',
            strokes=[
                CharacterStroke(-4, 9, 4, 9),    # Horizontal top
                CharacterStroke(0, 9, 0, -9),    # Vertical stem (top to bottom)
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

        # Letter 'A' - Two diagonals with crossbar (FIXED: flipped Y)
        self.characters['A'] = Character(
            char='A',
            strokes=[
                CharacterStroke(0, 9, -4, -9),   # Left diagonal (apex at top)
                CharacterStroke(0, 9, 4, -9),    # Right diagonal (apex at top)
                CharacterStroke(-2, -3, 2, -3),  # Crossbar
            ],
            width=9
        )

        # Letter 'B' - Vertical with two bumps
        self.characters['B'] = Character(
            char='B',
            strokes=[
                CharacterStroke(0, -9, 0, 9),    # Vertical
                CharacterStroke(0, -9, 5, -9),   # Top horizontal
                CharacterStroke(5, -9, 6, -7),   # Top curve 1
                CharacterStroke(6, -7, 6, -2),   # Top curve 2
                CharacterStroke(6, -2, 5, 0),    # Top curve 3
                CharacterStroke(5, 0, 0, 0),     # Middle horizontal
                CharacterStroke(0, 0, 5, 0),     # Bottom start
                CharacterStroke(5, 0, 6, 2),     # Bottom curve 1
                CharacterStroke(6, 2, 6, 7),     # Bottom curve 2
                CharacterStroke(6, 7, 5, 9),     # Bottom curve 3
                CharacterStroke(5, 9, 0, 9),     # Bottom horizontal
            ],
            width=7
        )

        # Letter 'C' - Arc (left-open circle)
        c_strokes = []
        segments = 12
        radius = 6
        for i in range(2, segments-1):  # Skip right side
            angle1 = 2 * np.pi * i / segments
            angle2 = 2 * np.pi * (i + 1) / segments
            x1 = radius * np.cos(angle1)
            y1 = radius * np.sin(angle1)
            x2 = radius * np.cos(angle2)
            y2 = radius * np.sin(angle2)
            c_strokes.append(CharacterStroke(x1, y1, x2, y2))
        self.characters['C'] = Character(char='C', strokes=c_strokes, width=12)

        # Letter 'D' - Vertical with curved right side
        self.characters['D'] = Character(
            char='D',
            strokes=[
                CharacterStroke(0, -9, 0, 9),    # Vertical
                CharacterStroke(0, -9, 4, -9),   # Top
                CharacterStroke(4, -9, 6, -6),   # Curve 1
                CharacterStroke(6, -6, 6, 6),    # Right side
                CharacterStroke(6, 6, 4, 9),     # Curve 2
                CharacterStroke(4, 9, 0, 9),     # Bottom
            ],
            width=7
        )

        # Letter 'F' - Like E but no bottom horizontal
        self.characters['F'] = Character(
            char='F',
            strokes=[
                CharacterStroke(0, -9, 0, 9),    # Vertical
                CharacterStroke(0, -9, 6, -9),   # Top horizontal
                CharacterStroke(0, 0, 5, 0),     # Middle horizontal
            ],
            width=7
        )

        # Letter 'G' - Like C with horizontal bar
        g_strokes = []
        segments = 12
        radius = 6
        for i in range(2, segments-1):
            angle1 = 2 * np.pi * i / segments
            angle2 = 2 * np.pi * (i + 1) / segments
            x1 = radius * np.cos(angle1)
            y1 = radius * np.sin(angle1)
            x2 = radius * np.cos(angle2)
            y2 = radius * np.sin(angle2)
            g_strokes.append(CharacterStroke(x1, y1, x2, y2))
        g_strokes.append(CharacterStroke(6, 0, 3, 0))  # Horizontal bar
        self.characters['G'] = Character(char='G', strokes=g_strokes, width=12)

        # Letter 'J' - Vertical with bottom curve (FIXED: proper orientation)
        self.characters['J'] = Character(
            char='J',
            strokes=[
                CharacterStroke(3, 9, 3, -6),    # Vertical (top to bottom)
                CharacterStroke(3, -6, 2, -8),   # Curve 1
                CharacterStroke(2, -8, 0, -9),   # Curve 2
                CharacterStroke(0, -9, -2, -8),  # Curve 3 (hook at bottom)
            ],
            width=6
        )

        # Letter 'K' - Vertical with two diagonals
        self.characters['K'] = Character(
            char='K',
            strokes=[
                CharacterStroke(0, -9, 0, 9),    # Vertical
                CharacterStroke(6, -9, 0, 0),    # Top diagonal
                CharacterStroke(0, 0, 6, 9),     # Bottom diagonal
            ],
            width=7
        )

        # Letter 'M' - Four lines forming M (FIXED: flipped Y)
        self.characters['M'] = Character(
            char='M',
            strokes=[
                CharacterStroke(-5, 9, -5, -9),  # Left vertical (top to bottom)
                CharacterStroke(-5, 9, 0, -4),   # Left diagonal (top to middle)
                CharacterStroke(0, -4, 5, 9),    # Right diagonal (middle to top)
                CharacterStroke(5, 9, 5, -9),    # Right vertical (top to bottom)
            ],
            width=11
        )

        # Letter 'N' - Three lines forming N (FIXED: correct diagonal direction)
        self.characters['N'] = Character(
            char='N',
            strokes=[
                CharacterStroke(-3, 9, -3, -9),  # Left vertical (top to bottom)
                CharacterStroke(-3, 9, 3, -9),   # Diagonal (top-left to bottom-right)
                CharacterStroke(3, -9, 3, 9),    # Right vertical (bottom to top)
            ],
            width=7
        )

        # Letter 'P' - Vertical with top bump (FIXED: flipped Y)
        self.characters['P'] = Character(
            char='P',
            strokes=[
                CharacterStroke(0, 9, 0, -9),    # Vertical (top to bottom)
                CharacterStroke(0, 9, 5, 9),     # Top horizontal
                CharacterStroke(5, 9, 6, 7),     # Curve 1
                CharacterStroke(6, 7, 6, 2),     # Curve 2
                CharacterStroke(6, 2, 5, 0),     # Curve 3
                CharacterStroke(5, 0, 0, 0),     # Middle horizontal
            ],
            width=7
        )

        # Letter 'Q' - Circle with tail
        q_strokes = []
        segments = 16
        radius = 6
        for i in range(segments):
            angle1 = 2 * np.pi * i / segments
            angle2 = 2 * np.pi * (i + 1) / segments
            x1 = radius * np.cos(angle1)
            y1 = radius * np.sin(angle1)
            x2 = radius * np.cos(angle2)
            y2 = radius * np.sin(angle2)
            q_strokes.append(CharacterStroke(x1, y1, x2, y2))
        q_strokes.append(CharacterStroke(3, -3, 7, -9))  # Tail (FIXED)
        self.characters['Q'] = Character(char='Q', strokes=q_strokes, width=13)

        # Letter 'R' - Like P with diagonal leg (FIXED: flipped Y)
        self.characters['R'] = Character(
            char='R',
            strokes=[
                CharacterStroke(0, 9, 0, -9),    # Vertical (top to bottom)
                CharacterStroke(0, 9, 5, 9),     # Top horizontal
                CharacterStroke(5, 9, 6, 7),     # Curve 1
                CharacterStroke(6, 7, 6, 2),     # Curve 2
                CharacterStroke(6, 2, 5, 0),     # Curve 3
                CharacterStroke(5, 0, 0, 0),     # Middle horizontal
                CharacterStroke(0, 0, 6, -9),    # Diagonal leg (down to bottom)
            ],
            width=7
        )

        # Letter 'S' - Snake curve (FIXED: flipped X to correct mirroring)
        self.characters['S'] = Character(
            char='S',
            strokes=[
                CharacterStroke(-6, -7, -5, -9),   # Top curve 1
                CharacterStroke(-5, -9, -2, -9),   # Top horizontal
                CharacterStroke(-2, -9, 0, -7),    # Top curve 2
                CharacterStroke(0, -7, 0, -3),     # Top straight
                CharacterStroke(0, -3, -3, 0),     # Middle diagonal
                CharacterStroke(-3, 0, -6, 3),     # Middle curve
                CharacterStroke(-6, 3, -6, 7),     # Bottom straight
                CharacterStroke(-6, 7, -4, 9),     # Bottom curve 1
                CharacterStroke(-4, 9, -1, 9),     # Bottom horizontal
                CharacterStroke(-1, 9, 0, 7),      # Bottom curve 2
            ],
            width=7
        )

        # Letter 'U' - Vertical down, curve, vertical up (FIXED: flipped Y)
        self.characters['U'] = Character(
            char='U',
            strokes=[
                CharacterStroke(-3, 9, -3, -6),  # Left vertical (top to bottom)
                CharacterStroke(-3, -6, -2, -8), # Curve 1
                CharacterStroke(-2, -8, 0, -9),  # Curve 2 (bottom of U)
                CharacterStroke(0, -9, 2, -8),   # Curve 3
                CharacterStroke(2, -8, 3, -6),   # Curve 4
                CharacterStroke(3, -6, 3, 9),    # Right vertical (bottom to top)
            ],
            width=7
        )

        # Letter 'V' - Two diagonals meeting at bottom (FIXED: flipped Y)
        self.characters['V'] = Character(
            char='V',
            strokes=[
                CharacterStroke(-4, 9, 0, -9),   # Left diagonal (top to bottom point)
                CharacterStroke(0, -9, 4, 9),    # Right diagonal (bottom point to top)
            ],
            width=9
        )

        # Letter 'W' - Four lines forming W (FIXED: flipped Y)
        self.characters['W'] = Character(
            char='W',
            strokes=[
                CharacterStroke(-5, 9, -2, -9),  # Left diagonal down (top to bottom)
                CharacterStroke(-2, -9, 0, 4),   # Left diagonal up (bottom to middle)
                CharacterStroke(0, 4, 2, -9),    # Right diagonal down (middle to bottom)
                CharacterStroke(2, -9, 5, 9),    # Right diagonal up (bottom to top)
            ],
            width=11
        )

        # Letter 'X' - Two diagonals crossing (FIXED: flipped Y)
        self.characters['X'] = Character(
            char='X',
            strokes=[
                CharacterStroke(-4, 9, 4, -9),   # Diagonal \ (top-left to bottom-right)
                CharacterStroke(4, 9, -4, -9),   # Diagonal / (top-right to bottom-left)
            ],
            width=9
        )

        # Letter 'Y' - Two diagonals meeting, vertical down (FIXED: flipped Y)
        self.characters['Y'] = Character(
            char='Y',
            strokes=[
                CharacterStroke(-4, 9, 0, 0),    # Left diagonal (top to center)
                CharacterStroke(4, 9, 0, 0),     # Right diagonal (top to center)
                CharacterStroke(0, 0, 0, -9),    # Vertical stem (center to bottom)
            ],
            width=9
        )

        # Letter 'Z' - Horizontal, diagonal, horizontal (FIXED: flipped Y)
        self.characters['Z'] = Character(
            char='Z',
            strokes=[
                CharacterStroke(-3, 9, 3, 9),    # Top horizontal (at top)
                CharacterStroke(3, 9, -3, -9),   # Diagonal (top-right to bottom-left)
                CharacterStroke(-3, -9, 3, -9),  # Bottom horizontal (at bottom)
            ],
            width=7
        )

        # Numbers 0-9

        # Number '0' - Circle/oval
        zero_strokes = []
        segments = 16
        radius_x = 5
        radius_y = 7
        for i in range(segments):
            angle1 = 2 * np.pi * i / segments
            angle2 = 2 * np.pi * (i + 1) / segments
            x1 = radius_x * np.cos(angle1)
            y1 = radius_y * np.sin(angle1)
            x2 = radius_x * np.cos(angle2)
            y2 = radius_y * np.sin(angle2)
            zero_strokes.append(CharacterStroke(x1, y1, x2, y2))
        self.characters['0'] = Character(char='0', strokes=zero_strokes, width=11)

        # Number '1' - Vertical line with top angle (FIXED: flipped Y)
        self.characters['1'] = Character(
            char='1',
            strokes=[
                CharacterStroke(-2, 6, 0, 9),    # Top angle (to apex at top)
                CharacterStroke(0, 9, 0, -9),    # Vertical (top to bottom)
            ],
            width=4
        )

        # Number '2' - Top curve, diagonal, bottom horizontal (FIXED: flipped Y)
        self.characters['2'] = Character(
            char='2',
            strokes=[
                CharacterStroke(-3, 7, -2, 9),   # Top curve 1 (at top)
                CharacterStroke(-2, 9, 2, 9),    # Top horizontal (at top)
                CharacterStroke(2, 9, 3, 7),     # Top curve 2 (at top)
                CharacterStroke(3, 7, 3, 3),     # Right curve
                CharacterStroke(3, 3, -3, -9),   # Diagonal (down to bottom)
                CharacterStroke(-3, -9, 3, -9),  # Bottom horizontal (at bottom)
            ],
            width=7
        )

        # Number '3' - Two curves stacked
        self.characters['3'] = Character(
            char='3',
            strokes=[
                CharacterStroke(-3, -9, 3, -9),  # Top horizontal
                CharacterStroke(3, -9, 4, -7),   # Top curve 1
                CharacterStroke(4, -7, 4, -2),   # Top curve 2
                CharacterStroke(4, -2, 2, 0),    # Top curve 3
                CharacterStroke(2, 0, 4, 2),     # Bottom curve 1
                CharacterStroke(4, 2, 4, 7),     # Bottom curve 2
                CharacterStroke(4, 7, 3, 9),     # Bottom curve 3
                CharacterStroke(3, 9, -3, 9),    # Bottom horizontal
            ],
            width=7
        )

        # Number '4' - Two lines and crossbar (FIXED: flipped Y)
        self.characters['4'] = Character(
            char='4',
            strokes=[
                CharacterStroke(3, 9, -3, -4),   # Diagonal (top-right to bottom-left)
                CharacterStroke(-3, -4, 5, -4),  # Horizontal crossbar
                CharacterStroke(3, 2, 3, -9),    # Vertical (extends down)
            ],
            width=8
        )

        # Number '5' - Horizontal, vertical, curve (FIXED: flipped Y)
        self.characters['5'] = Character(
            char='5',
            strokes=[
                CharacterStroke(4, 9, -3, 9),    # Top horizontal (at top)
                CharacterStroke(-3, 9, -3, 0),   # Vertical (down from top)
                CharacterStroke(-3, 0, 3, 0),    # Middle horizontal
                CharacterStroke(3, 0, 4, -2),    # Curve 1 (down)
                CharacterStroke(4, -2, 4, -7),   # Curve 2 (down)
                CharacterStroke(4, -7, 3, -9),   # Curve 3 (to bottom)
                CharacterStroke(3, -9, -3, -9),  # Bottom horizontal (at bottom)
            ],
            width=7
        )

        # Number '6' - Curve with loop (FIXED: flipped Y)
        self.characters['6'] = Character(
            char='6',
            strokes=[
                CharacterStroke(3, 7, 2, 9),     # Top curve 1 (at top)
                CharacterStroke(2, 9, -1, 9),    # Top horizontal (at top)
                CharacterStroke(-1, 9, -3, 7),   # Top curve 2 (at top)
                CharacterStroke(-3, 7, -3, -6),  # Left vertical (down)
                CharacterStroke(-3, -6, -2, -8), # Bottom curve 1
                CharacterStroke(-2, -8, 0, -9),  # Bottom curve 2
                CharacterStroke(0, -9, 2, -8),   # Bottom curve 3
                CharacterStroke(2, -8, 3, -6),   # Bottom curve 4
                CharacterStroke(3, -6, 3, -2),   # Right curve
                CharacterStroke(3, -2, 2, 0),    # Circle curve 1
                CharacterStroke(2, 0, -2, 0),    # Circle horizontal
                CharacterStroke(-2, 0, -3, -2),  # Circle curve 2
            ],
            width=7
        )

        # Number '7' - Horizontal top with diagonal (FIXED: flipped Y)
        self.characters['7'] = Character(
            char='7',
            strokes=[
                CharacterStroke(-3, 9, 4, 9),    # Top horizontal (at top)
                CharacterStroke(4, 9, -1, -9),   # Diagonal (down to bottom)
            ],
            width=7
        )

        # Number '8' - Two circles stacked (FIXED: flipped Y and brought closer)
        eight_strokes = []
        # Top circle (at top, y=4 center)
        for i in range(8):
            angle1 = 2 * np.pi * i / 8
            angle2 = 2 * np.pi * (i + 1) / 8
            x1 = 2.5 * np.cos(angle1)
            y1 = 4 + 2.5 * np.sin(angle1)  # Flipped: now at top
            x2 = 2.5 * np.cos(angle2)
            y2 = 4 + 2.5 * np.sin(angle2)  # Flipped: now at top
            eight_strokes.append(CharacterStroke(x1, y1, x2, y2))
        # Bottom circle (at bottom, y=-4 center, closer together)
        for i in range(8):
            angle1 = 2 * np.pi * i / 8
            angle2 = 2 * np.pi * (i + 1) / 8
            x1 = 3 * np.cos(angle1)
            y1 = -4 + 3 * np.sin(angle1)  # Flipped: now at bottom
            x2 = 3 * np.cos(angle2)
            y2 = -4 + 3 * np.sin(angle2)  # Flipped: now at bottom
            eight_strokes.append(CharacterStroke(x1, y1, x2, y2))
        self.characters['8'] = Character(char='8', strokes=eight_strokes, width=7)

        # Number '9' - Like inverted 6 (FIXED: flipped Y)
        self.characters['9'] = Character(
            char='9',
            strokes=[
                CharacterStroke(-3, -7, -2, -9), # Bottom curve 1 (at bottom)
                CharacterStroke(-2, -9, 1, -9),  # Bottom horizontal (at bottom)
                CharacterStroke(1, -9, 3, -7),   # Bottom curve 2 (at bottom)
                CharacterStroke(3, -7, 3, 6),    # Right vertical (up)
                CharacterStroke(3, 6, 2, 8),     # Top curve 1 (at top)
                CharacterStroke(2, 8, 0, 9),     # Top curve 2 (at top)
                CharacterStroke(0, 9, -2, 8),    # Top curve 3 (at top)
                CharacterStroke(-2, 8, -3, 6),   # Top curve 4 (at top)
                CharacterStroke(-3, 6, -3, 2),   # Left curve
                CharacterStroke(-3, 2, -2, 0),   # Circle curve 1
                CharacterStroke(-2, 0, 2, 0),    # Circle horizontal
                CharacterStroke(2, 0, 3, 2),     # Circle curve 2
            ],
            width=7
        )

        # Basic punctuation

        # Period '.' (FIXED: changed to small circle)
        period_strokes = []
        for i in range(6):
            angle1 = 2 * np.pi * i / 6
            angle2 = 2 * np.pi * (i + 1) / 6
            x1 = 0.5 * np.cos(angle1)
            y1 = -8 + 0.5 * np.sin(angle1)  # Small circle at bottom
            x2 = 0.5 * np.cos(angle2)
            y2 = -8 + 0.5 * np.sin(angle2)
            period_strokes.append(CharacterStroke(x1, y1, x2, y2))
        self.characters['.'] = Character(char='.', strokes=period_strokes, width=2)

        # Comma ','
        self.characters[','] = Character(
            char=',',
            strokes=[
                CharacterStroke(0, 8, 0, 9),     # Dot
                CharacterStroke(0, 9, -1, 11),   # Tail
            ],
            width=2
        )

        # Exclamation mark '!' (FIXED: changed dot to circle at bottom)
        exclaim_strokes = [
            CharacterStroke(0, 9, 0, -4),    # Vertical line (top to middle)
        ]
        # Add small circle at bottom
        for i in range(6):
            angle1 = 2 * np.pi * i / 6
            angle2 = 2 * np.pi * (i + 1) / 6
            x1 = 0.5 * np.cos(angle1)
            y1 = -8 + 0.5 * np.sin(angle1)  # Small circle at bottom
            x2 = 0.5 * np.cos(angle2)
            y2 = -8 + 0.5 * np.sin(angle2)
            exclaim_strokes.append(CharacterStroke(x1, y1, x2, y2))
        self.characters['!'] = Character(char='!', strokes=exclaim_strokes, width=2)

        # Question mark '?' (FIXED: flipped Y, changed dot to circle)
        question_strokes = [
            CharacterStroke(-2, 7, -1, 9),   # Top curve 1 (at top)
            CharacterStroke(-1, 9, 1, 9),    # Top horizontal (at top)
            CharacterStroke(1, 9, 2, 7),     # Top curve 2 (at top)
            CharacterStroke(2, 7, 2, 3),     # Right curve
            CharacterStroke(2, 3, 0, 0),     # Curve to stem
            CharacterStroke(0, 0, 0, -3),    # Stem (down)
        ]
        # Add small circle at bottom
        for i in range(6):
            angle1 = 2 * np.pi * i / 6
            angle2 = 2 * np.pi * (i + 1) / 6
            x1 = 0.5 * np.cos(angle1)
            y1 = -8 + 0.5 * np.sin(angle1)  # Small circle at bottom
            x2 = 0.5 * np.cos(angle2)
            y2 = -8 + 0.5 * np.sin(angle2)
            question_strokes.append(CharacterStroke(x1, y1, x2, y2))
        self.characters['?'] = Character(char='?', strokes=question_strokes, width=5)

        # Hyphen/minus '-'
        self.characters['-'] = Character(
            char='-',
            strokes=[
                CharacterStroke(-3, 0, 3, 0),    # Horizontal line
            ],
            width=7
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
