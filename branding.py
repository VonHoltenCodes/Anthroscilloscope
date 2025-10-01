#!/usr/bin/env python3
"""
Branding and maker's mark for Anthroscilloscope
ASCII art logo and attribution information
"""

# Main ASCII logo (compact version for GUI)
LOGO_COMPACT = r"""
╔═╗╔╗╔╔╦╗╦ ╦╦═╗╔═╗╔═╗╔═╗╦╦  ╦  ╔═╗╔═╗╔═╗╔═╗╔═╗╔═╗
╠═╣║║║ ║ ╠═╣╠╦╝║ ║╚═╗║  ║║  ║  ║ ║╚═╗║  ║ ║╠═╝║╣
╩ ╩╝╚╝ ╩ ╩ ╩╩╚═╚═╝╚═╝╚═╝╩╩═╝╩═╝╚═╝╚═╝╚═╝╚═╝╩  ╚═╝
"""

# Oscilloscope illustration (full version)
LOGO_FULL = r"""
         ╔════════════════════════════════════════════════════════════╗
         ║  ┌────────────────────────────────────────────────────┐    ║
         ║  │                                                    │    ║
         ║  │     ╱╲    ╱╲    ╱╲    ╱╲    ╱╲    ╱╲    ╱╲         │    ║
         ║  │    ╱  ╲  ╱  ╲  ╱  ╲  ╱  ╲  ╱  ╲  ╱  ╲  ╱  ╲        │    ║
         ║  │   ╱    ╲╱    ╲╱    ╲╱    ╲╱    ╲╱    ╲╱    ╲       │    ║
         ║  │ ──┼────────────────────────────────────────────┼── │    ║
         ║  │   │   ANTHROSCILLOSCOPE                        │   │    ║
         ║  │   │                                            │   │    ║
         ║  │ ──┼────────────────────────────────────────────┼── │    ║
         ║  └────────────────────────────────────────────────────┘    ║
         ║                                                            ║
         ║  VERTICAL            HORIZONTAL         TRIGGER            ║
         ║  ┌─────┐ ┌─────┐    ┌─────┐ ┌─────┐    ┌─────┐ ┌─────┐     ║
         ║  │ ◉   │ │   ◉ │    │  ◉  │ │ ◉   │    │   ◉ │ │  ◉  │     ║
         ║  └─────┘ └─────┘    └─────┘ └─────┘    └─────┘ └─────┘     ║
         ║  VOLTS/DIV  POS     TIME/DIV  POS       LEVEL   MODE       ║
         ║                                                            ║
         ║  [CH1] [CH2] [MATH] [REF]    [AUTO] [RUN/STOP] [SINGLE]    ║
         ║   ▀▀▀   ───   ───    ───       ▀▀▀     ───       ───       ║
         ║                                                            ║
         ║  ○ CH1  ○ CH2  ○ EXT  ○ LINE         ■ POWER               ║
         ║  └─BNC─┘└─BNC─┘└─BNC─┘└─BNC─┘         ON/OFF               ║
         ╚════════════════════════════════════════════════════════════╝
               ╱│                                          │╲
              ╱ └──────────────────────────────────────────┘ ╲
             ╱________________________________________________╲

         ╔═╗╔╗╔╔╦╗╦ ╦╦═╗╔═╗╔═╗╔═╗╦╦  ╦  ╔═╗╔═╗╔═╗╔═╗╔═╗╔═╗
         ╠═╣║║║ ║ ╠═╣╠╦╝║ ║╚═╗║  ║║  ║  ║ ║╚═╗║  ║ ║╠═╝║╣
         ╩ ╩╝╚╝ ╩ ╩ ╩╩╚═╚═╝╚═╝╚═╝╩╩═╝╩═╝╚═╝╚═╝╚═╝╚═╝╩  ╚═╝
"""

# Waveform icon (minimal version for corners/watermark)
LOGO_MINI = r"""
 ╱╲  ╱╲  ╱╲
╱  ╲╱  ╲╱  ╲
"""

# Attribution
AUTHOR = "Trenton Von Holten"
AUTHOR_HANDLE = "VonHoltenCodes"
AUTHOR_GITHUB = "https://github.com/VonHoltenCodes"
PROJECT_URL = "https://github.com/VonHoltenCodes/Anthroscilloscope"
PROJECT_NAME = "Anthroscilloscope"
VERSION = "1.0.0"

# Credits
CREDITS = """
╔══════════════════════════════════════════════════════════════╗
║                     ANTHROSCILLOSCOPE                        ║
║              Lissajous Text Generation System                ║
╚══════════════════════════════════════════════════════════════╝

Version: {version}

Created by: {author}
GitHub: {github}
Project: {project}

Features:
  • Hershey Vector Font Rendering
  • Real-time Oscilloscope Text Preview
  • XY Mode Audio Generation
  • Interactive GUI Controls
  • Advanced Effects (Rotation, 3D, Shadows)
  • Preset Management

Technology Stack:
  • Python 3.10+
  • Matplotlib (Interactive Widgets)
  • NumPy (Signal Processing)
  • SciPy (Audio Export)

Development:
  • Built with Claude Code (Anthropic)
  • Powered by Claude Sonnet 4.5
  • Phases 1-4 developed with AI assistance

Built for hardware hackers, signal enthusiasts, and
oscilloscope artists everywhere.

═══════════════════════════════════════════════════════════════
        Transform text into waveforms, one stroke at a time
═══════════════════════════════════════════════════════════════
"""

# Tagline options
TAGLINES = [
    "Transform your oscilloscope into an art machine",
    "Text → Waveforms → Oscilloscope Magic",
    "Making oscilloscopes speak since 2025",
    "Where signals meet typography",
    "Transform text into waveforms, one stroke at a time",
    "Hershey fonts meet XY mode",
    "Your oscilloscope deserves better text",
]

# License
LICENSE_SHORT = "MIT License © 2025 Trenton Von Holten"
LICENSE_FULL = """
MIT License

Copyright (c) 2025 Trenton Von Holten

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def get_credits_text():
    """Get formatted credits text"""
    return CREDITS.format(
        version=VERSION,
        author=AUTHOR,
        github=AUTHOR_GITHUB,
        project=PROJECT_URL
    )


def get_short_attribution():
    """Get short one-line attribution"""
    return f"{PROJECT_NAME} v{VERSION} by {AUTHOR} | {PROJECT_URL}"


def get_watermark():
    """Get watermark text for exports"""
    return f"{PROJECT_NAME} v{VERSION} | github.com/VonHoltenCodes"


if __name__ == '__main__':
    print(LOGO_FULL)
    print()
    print(get_credits_text())
    print()
    print("Taglines:")
    for i, tagline in enumerate(TAGLINES, 1):
        print(f"  {i}. {tagline}")
