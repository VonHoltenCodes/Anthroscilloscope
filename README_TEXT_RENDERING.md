# Lissajous Text Rendering System

**Transform text into oscilloscope art using XY mode and audio signals**

![Status](https://img.shields.io/badge/Status-Phase%201%20Complete-success)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 Overview

This system converts text strings into vector paths and generates stereo audio signals that, when fed into an oscilloscope in XY mode, render the text as Lissajous-style patterns. No external function generator required - just your computer's audio output!

**Key Features**:
- ✨ Text-to-oscilloscope rendering via audio signals
- 🔤 Vector-based Hershey font system
- 🎵 Stereo audio output (Left=X, Right=Y)
- 🔬 Mock oscilloscope for development without hardware
- 📊 WAV file export for playback

---

## 🚀 Quick Start

### Installation
```bash
# Install dependencies
pip install numpy scipy matplotlib sounddevice Hershey-Fonts pyvisa pyvisa-py

# Clone repository
git clone https://github.com/VonHoltenCodes/Anthroscilloscope.git
cd Anthroscilloscope
```

### Basic Usage
```python
from text_rendering.lissajous_text_renderer import LissajousTextRenderer

# Create renderer
renderer = LissajousTextRenderer()

# Preview text
renderer.preview_text("HELLO")

# Save as audio file
renderer.save_text_audio("HELLO", "hello.wav", duration=0.5, loop_count=60)

# Get rendering statistics
stats = renderer.get_text_stats("HELLO")
print(stats)
```

### Running Demos
```bash
# Interactive GUI (Phase 3)
python3 text_gui.py
# or
python3 demo_gui.py

# Test mock oscilloscope patterns
python3 demo_mock_oscilloscope.py

# Test text rendering
python3 test_text_quick.py
```

---

## 📐 How It Works

### The Pipeline

```
TEXT → STROKES → PATH POINTS → AUDIO SAMPLES → OSCILLOSCOPE
  ↓        ↓           ↓             ↓              ↓
"HELLO"  Vector    XY coords    Stereo WAV    XY Display
         Font      Normalized   L=X, R=Y
```

### Technical Details

1. **Font Vectorization**
   - Uses Hershey vector fonts (stroke-based, perfect for plotters)
   - Each character = series of line segments (strokes)
   - Example: Letter 'H' = 3 strokes (2 verticals + 1 crossbar)

2. **Path Generation**
   - Converts strokes to parametric line segments: `x(t) = x₁ + t(x₂-x₁)`
   - Interpolates points along each stroke
   - Handles pen-up transitions between disconnected segments
   - Normalizes to [-1, 1] range maintaining aspect ratio

3. **Audio Synthesis**
   - Resamples path to audio sample rate (44.1kHz)
   - Left channel = X-axis coordinates
   - Right channel = Y-axis coordinates
   - Low-pass filtering for smooth transitions
   - Loops pattern for persistence on display

4. **Oscilloscope Display**
   - Connect audio output to oscilloscope inputs (CH1, CH2)
   - Enable XY mode (CH1 = X-axis, CH2 = Y-axis)
   - Oscilloscope traces the path, rendering the text

---

## 🏗️ Architecture

### Module Structure

```
core/
├── oscilloscope_interface.py   # Abstract base class for scope control
├── mock_oscilloscope.py         # Simulated oscilloscope (no hardware needed)
├── signal_generators.py         # Test signal patterns (Lissajous, circles, etc.)
└── oscilloscope_factory.py      # Factory for hardware/mock switching

text_rendering/
├── hershey_font.py              # Vector font manager
├── text_to_path.py              # Text → XY path conversion
├── path_to_audio.py             # Path → stereo audio conversion
└── lissajous_text_renderer.py  # Main high-level API

tests/
└── test_mock_oscilloscope.py    # Unit tests (7/7 passing)
```

### Key Classes

**`HersheyFont`**: Manages vector character definitions
- Currently supports: A, E, H, I, L, O, T, space
- Each character stored as list of `CharacterStroke` objects
- Handles character spacing and width calculations

**`TextToPath`**: Converts text to drawable paths
- Positions characters with proper spacing
- Interpolates smooth paths between strokes
- Manages pen-up/pen-down transitions

**`PathToAudio`**: Generates audio signals
- Resamples paths to audio sample rate
- Applies smoothing filters
- Creates stereo WAV files

**`LissajousTextRenderer`**: Main interface
- Simple API: `render_text()`, `preview_text()`, `save_text_audio()`
- Handles entire pipeline from text to audio

---

## 🧪 Development Without Hardware

### Mock Oscilloscope

We built a complete hardware abstraction layer allowing development without physical oscilloscope:

```python
from core.oscilloscope_factory import create_oscilloscope

# Create mock oscilloscope
scope = create_oscilloscope(mock=True)
scope.connect()
scope.enable_xy_mode()

# Get simulated waveform data
t, voltage = scope.get_waveform_data(1)
```

**Features**:
- Simulates Rigol DS1104Z Plus SCPI commands
- Generates synthetic waveforms with realistic noise
- Supports multiple signal generators (Lissajous, circles, figure-8)
- Full XY mode simulation
- 7/7 unit tests passing

---

## 📊 Current Capabilities

### ✅ Implemented (Phase 1 Complete)
- Single character rendering: **I, L, T, H, E, A, O** + space
- Multi-character words: "HELLO", "HELLO", "OILATE"
- Text-to-path conversion with proper spacing
- Path-to-audio with smoothing filters
- WAV file export
- Visual preview with matplotlib
- Mock oscilloscope infrastructure
- Comprehensive testing suite

### Example Output
**Text**: "HELLO"
- Strokes: 27
- Path points: 306
- Audio samples: 22,050 (0.5s @ 44.1kHz)
- File size: ~88KB WAV (30-loop version)

---

## 🎨 Example Renders

### Simple Characters
```python
renderer.preview_text("I")     # 3 strokes (vertical + serifs)
renderer.preview_text("O")     # 16-segment circle
renderer.preview_text("HELLO") # 27 strokes, clean rendering
```

### Audio Generation
```python
# Generate 1-second loop
left, right = renderer.render_text("TEST", duration=1.0, loop_count=1)

# Save for oscilloscope playback (30 loops = 15 seconds)
renderer.save_text_audio("HELLO", "output.wav", loop_count=30)
```

---

## 🔬 Technical Specifications

### Audio Parameters
- **Sample Rate**: 44,100 Hz (CD quality)
- **Bit Depth**: 16-bit signed integer
- **Channels**: 2 (stereo)
- **Format**: WAV (uncompressed)
- **Amplitude Range**: [-1.0, 1.0] float → [-32768, 32767] int16

### Path Parameters
- **Coordinate Range**: Normalized to [-1, 1]
- **Aspect Ratio**: Preserved during normalization
- **Interpolation Points**: ~10 per stroke (configurable)
- **Smoothing Filter**: Butterworth 4th order, cutoff ~2.2kHz

### Performance
- Text-to-path: ~1ms for 5-character word
- Path-to-audio: ~10ms for 22k samples
- Memory: ~200KB per second of audio
- Recommended render speed: 5,000 points/second

---

## 📚 API Reference

### `LissajousTextRenderer`

```python
class LissajousTextRenderer:
    def __init__(self, sample_rate: int = 44100)

    def render_text(self, text: str, duration: float = 1.0,
                   loop_count: int = 60) -> Tuple[ndarray, ndarray]
        """Returns (left_channel, right_channel) audio arrays"""

    def preview_text(self, text: str, show_points: bool = False)
        """Display matplotlib preview of text path"""

    def save_text_audio(self, text: str, filename: str,
                       duration: float = 1.0, loop_count: int = 60)
        """Save text as WAV file"""

    def get_text_stats(self, text: str) -> dict
        """Get rendering statistics"""

    def available_characters(self) -> str
        """Get string of available characters"""
```

---

## 🧩 Integration with Existing Anthroscilloscope

This text rendering system integrates seamlessly with the existing Anthroscilloscope project:

### Shared Components
- Uses existing `waveform_generator_control.py` for audio output
- Compatible with `lissajous_xy_mode.py` XY mode functions
- Leverages existing `frequency_math.py` for analysis

### Future Integration Points
- Add menu option "14. Text Rendering Mode" to `anthroscilloscope_main.py`
- Combine with existing pattern generation (morphing text ↔ Lissajous)
- Use existing capture/analysis tools for feedback

---

## 🛣️ Roadmap

### Phase 2: Multi-Character & Full Alphabet (Next)
- [ ] Integrate full Hershey-Fonts library
- [ ] Implement all uppercase A-Z
- [ ] Implement numbers 0-9
- [ ] Add basic punctuation (. , ! ? -)
- [ ] Optimize path generation for complex characters

### Phase 3: Interactive UI ✅
- [x] Create GUI with text input field
- [x] Font size slider (0.3x - 3.0x)
- [x] Real-time preview
- [x] Speed control (0.1x - 5.0x)
- [x] Save/load text sequences (JSON presets)

### Phase 4: Advanced Features
- [ ] Rotation and scaling effects
- [ ] Character morphing animations
- [ ] Multiple font styles
- [ ] 3D pseudo-effects
- [ ] Multi-line text support

---

## 🧪 Testing

### Run Tests
```bash
# Unit tests
pytest tests/test_mock_oscilloscope.py -v

# Quick verification
python3 test_text_quick.py

# Visual demo
python3 demo_text_rendering.py
```

### Test Coverage
- Mock oscilloscope: 7/7 tests passing
- Waveform generation ✅
- XY mode control ✅
- SCPI command simulation ✅
- Multiple signal generators ✅

---

## 🤝 Contributing

### Development Setup
1. Install dependencies (see Quick Start)
2. Set environment variable for mock mode: `export ANTHRO_MOCK=true`
3. Run existing demos to verify setup
4. Create feature branch
5. Add tests for new features
6. Submit pull request

### Adding New Characters
```python
# In hershey_font.py
self.characters['X'] = Character(
    char='X',
    strokes=[
        CharacterStroke(-4, -9, 4, 9),   # Diagonal \
        CharacterStroke(4, -9, -4, 9),   # Diagonal /
    ],
    width=9
)
```

---

## 📖 References

### Documentation
- [Hershey Font Format](https://paulbourke.net/dataformats/hershey/)
- [PyVISA Documentation](https://pyvisa.readthedocs.io/)
- [Rigol DS1104Z Plus Programming Guide](https://www.rigolna.com/products/digital-oscilloscopes/1000z/)

### Similar Projects
- [OscilloText](https://github.com/nwtaf/OscilloText) - Text to oscilloscope visuals
- [osci-render](https://github.com/jameshball/osci-render) - Full oscilloscope synthesizer
- [XYScope](https://github.com/ffd8/xyscope) - Processing vector display library

---

## 📄 License

MIT License - See main repository LICENSE file

---

## 🙏 Acknowledgments

- Hershey Fonts: Dr. Allen Vincent Hershey (1967)
- Anthroscilloscope base project: VonHoltenCodes
- Claude Code: Development assistance and contest platform

---

**Built with ❤️ for the oscilloscope art community**

*Developed for the Claude Code Contest - October 2025*
