#!/usr/bin/env python3
"""
Suppress matplotlib 3D warnings for all Anthroscilloscope modules
"""

import warnings

# Suppress the specific matplotlib 3D warning
warnings.filterwarnings('ignore', message='Unable to import Axes3D.*', category=UserWarning, module='matplotlib.projections')

# Also suppress general matplotlib warnings if needed
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

# Suppress glyph warnings (emoji characters)
warnings.filterwarnings('ignore', message='Glyph .* missing from font.*')