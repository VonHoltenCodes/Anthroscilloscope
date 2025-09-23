# Anthroscilloscope Lissajous XY Mode Features

## Overview
Advanced Lissajous pattern generation and analysis suite for Rigol DS1104Z Plus oscilloscopes. Create beautiful mathematical art through audio signals!

## Features

### 🎨 Lissajous Pattern Generation
- **Interactive Control Panel** (`waveform_generator_control.py`)
  - Real-time frequency control for left/right channels
  - Phase adjustment (0-360°)
  - Multiple waveform types (sine, square, triangle, sawtooth)
  - Preset frequency ratios for common patterns
  - Live oscilloscope measurement integration

### 📊 XY Mode Analysis
- **Pattern Analysis** (`lissajous_xy_mode.py`)
  - Automatic frequency ratio detection
  - Phase measurement
  - Musical interval identification
  - Pattern complexity calculation

### 🎵 Musical Mathematics
- **Frequency Analysis** (`frequency_math.py`)
  - Musical interval detection with cent accuracy
  - Harmonic series analysis
  - Consonance ratings
  - Temperament comparisons

### 🔧 Oscilloscope Control
- **Auto-scaling** (`auto_scale_xy.py`)
  - Automatic display optimization
  - Pattern centering
  - Zoom control
- **Display Optimization** (`optimize_scope_display.py`)
  - Noise reduction settings
  - Averaging configuration
  - Bandwidth limiting

## Installation

1. Clone the repository
2. Copy `config_template.py` to `config.py`
3. Update `config.py` with your oscilloscope's IP address
4. Install dependencies:
   ```bash
   pip install pyvisa pyvisa-py numpy matplotlib scipy sounddevice
   ```

## Quick Start

### 1. Basic Setup
```python
# config.py
RIGOL_IP = "YOUR_OSCILLOSCOPE_IP"  # e.g., "192.168.1.100"
```

### 2. Generate Patterns
```bash
# Interactive waveform generator with GUI
python3 waveform_generator_control.py

# Simple audio test patterns
python3 simple_audio_test.py
```

### 3. Analyze Patterns
```bash
# Interactive Lissajous viewer
python3 interactive_lissajous_demo.py

# Auto-scale display for best view
python3 auto_scale_xy.py
```

## Connection Guide

### Hardware Setup
1. **Audio Output → Oscilloscope Input**
   - Connect LEFT channel (3.5mm) → CH1 (BNC)
   - Connect RIGHT channel (3.5mm) → CH2 (BNC)
   - Ensure good ground connection

2. **Oscilloscope Settings**
   - Enable XY mode (Menu → Horizontal → Time Base → XY)
   - Set both channels to 0.5V/div initially
   - Use AC coupling for audio signals
   - Enable averaging (Acquire → Average → 4)

### Software Audio Routing
- Set system audio output to your sound card
- Use analog output (not digital)
- Adjust volume to achieve 1-2 Vpp on oscilloscope

## Common Patterns

| Ratio | Pattern | Musical Interval |
|-------|---------|-----------------|
| 1:1   | Circle/Line | Unison |
| 2:1   | Figure-8 | Octave |
| 3:2   | Complex loop | Perfect Fifth |
| 4:3   | Four-leaf | Perfect Fourth |
| 5:4   | Five loops | Major Third |

## Troubleshooting

### Fuzzy Patterns
- Enable bandwidth limiting (20MHz)
- Increase averaging (4x or 8x)
- Check cable quality and connections
- Reduce system volume if clipping

### No Signal
- Verify audio output is set correctly
- Check cable connections
- Ensure oscilloscope is in XY mode
- Try increasing amplitude in generator

### Pattern Drifting
- Frequencies not perfectly locked
- Use integer ratio frequencies
- Check for ground loops

## Advanced Usage

### Custom Frequency Ratios
```python
from lissajous_xy_mode import LissajousGenerator

# Generate golden ratio pattern
x, y = LissajousGenerator.generate_from_ratio(8, 5, phase=np.pi/4)
```

### Musical Interval Analysis
```python
from frequency_math import MusicalIntervals

# Analyze frequency relationship
interval = MusicalIntervals.find_closest_interval(1.5)  # Perfect fifth
print(f"Interval: {interval.interval_name}")
print(f"Consonance: {interval.consonance_rating:.2%}")
```

## File Descriptions

- `lissajous_xy_mode.py` - Core XY mode functionality
- `frequency_math.py` - Mathematical and musical calculations
- `waveform_generator_control.py` - Interactive GUI control
- `audio_lissajous.py` - Audio-based pattern generation
- `auto_scale_xy.py` - Automatic display optimization
- `optimize_scope_display.py` - Oscilloscope settings optimization
- `test_lissajous.py` - Test suite for verification

## Safety Notes
- Keep audio levels reasonable to protect equipment
- Use proper cables rated for your signal levels
- Ensure proper grounding to avoid noise
- Don't exceed oscilloscope input ratings

## License
See main repository license

## Contributing
Contributions welcome! Please ensure no hardcoded IPs or credentials in code.