#!/usr/bin/env python3
"""
Lissajous XY Mode Analyzer and Generator
Real-time XY mode visualization and frequency ratio analysis for oscilloscopes
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button, TextBox
import time
from dataclasses import dataclass
from typing import Tuple, Optional, List
import pyvisa


@dataclass
class LissajousPattern:
    """Data class for Lissajous pattern parameters"""
    freq_x: float  # X frequency in Hz
    freq_y: float  # Y frequency in Hz
    phase: float   # Phase difference in radians
    amplitude_x: float = 1.0
    amplitude_y: float = 1.0
    ratio_x: int = 1  # Frequency ratio numerator
    ratio_y: int = 1  # Frequency ratio denominator
    
    @property
    def frequency_ratio(self) -> float:
        """Get the frequency ratio as a decimal"""
        return self.freq_x / self.freq_y if self.freq_y != 0 else 0
    
    def get_simplified_ratio(self) -> Tuple[int, int]:
        """Get simplified integer frequency ratio"""
        from math import gcd
        if self.freq_y == 0:
            return (0, 0)
        
        # Convert to integer ratio
        ratio = self.freq_x / self.freq_y
        # Find closest rational approximation
        max_denominator = 20
        best_num, best_den = 1, 1
        min_error = abs(ratio - 1)
        
        for den in range(1, max_denominator + 1):
            num = round(ratio * den)
            if num > 0 and num <= max_denominator:
                error = abs(ratio - num/den)
                if error < min_error:
                    min_error = error
                    best_num, best_den = num, den
        
        # Simplify
        g = gcd(best_num, best_den)
        return (best_num // g, best_den // g)


class LissajousXYAnalyzer:
    """Analyzer for XY mode Lissajous patterns on oscilloscope"""
    
    def __init__(self, scope=None):
        self.scope = scope
        self.xy_mode_enabled = False
        
    def enable_xy_mode(self) -> bool:
        """Enable XY display mode on oscilloscope"""
        if not self.scope:
            print("No oscilloscope connected")
            return False
            
        try:
            # Set timebase to XY mode
            self.scope.write(':TIMebase:MODE XY')
            self.xy_mode_enabled = True
            print("✅ XY mode enabled")
            return True
        except Exception as e:
            print(f"❌ Failed to enable XY mode: {e}")
            return False
    
    def disable_xy_mode(self) -> bool:
        """Return to normal YT (time) mode"""
        if not self.scope:
            return False
            
        try:
            self.scope.write(':TIMebase:MODE MAIN')
            self.xy_mode_enabled = False
            print("✅ Returned to YT mode")
            return True
        except Exception as e:
            print(f"❌ Failed to disable XY mode: {e}")
            return False
    
    def analyze_pattern(self, x_data: np.ndarray, y_data: np.ndarray) -> LissajousPattern:
        """Analyze captured XY data to determine Lissajous parameters"""
        
        # Remove DC offset
        x_data = x_data - np.mean(x_data)
        y_data = y_data - np.mean(y_data)
        
        # Get amplitudes
        amp_x = np.max(np.abs(x_data))
        amp_y = np.max(np.abs(y_data))
        
        # Normalize
        if amp_x > 0:
            x_norm = x_data / amp_x
        else:
            x_norm = x_data
            
        if amp_y > 0:
            y_norm = y_data / amp_y
        else:
            y_norm = y_data
        
        # Estimate frequencies using zero crossings
        x_crossings = self._count_zero_crossings(x_norm)
        y_crossings = self._count_zero_crossings(y_norm)
        
        # Estimate phase difference
        phase = self._estimate_phase(x_norm, y_norm)
        
        # Create pattern object (frequencies are relative)
        pattern = LissajousPattern(
            freq_x=x_crossings,
            freq_y=y_crossings,
            phase=phase,
            amplitude_x=amp_x,
            amplitude_y=amp_y
        )
        
        # Get simplified ratio
        ratio_x, ratio_y = pattern.get_simplified_ratio()
        pattern.ratio_x = ratio_x
        pattern.ratio_y = ratio_y
        
        return pattern
    
    def _count_zero_crossings(self, data: np.ndarray) -> int:
        """Count zero crossings in signal"""
        signs = np.sign(data)
        signs[signs == 0] = 1
        crossings = np.sum(np.abs(np.diff(signs)) > 0)
        return crossings // 2  # Divide by 2 for full cycles
    
    def _estimate_phase(self, x: np.ndarray, y: np.ndarray) -> float:
        """Estimate phase difference between signals"""
        # Find maximum correlation lag
        correlation = np.correlate(x, y, mode='same')
        lag = np.argmax(correlation) - len(x) // 2
        
        # Convert lag to phase
        phase = 2 * np.pi * lag / len(x)
        return phase % (2 * np.pi)
    
    def capture_xy_data(self, points: int = 1200) -> Tuple[np.ndarray, np.ndarray]:
        """Capture data from CH1 (X) and CH2 (Y) for XY analysis"""
        if not self.scope:
            return None, None
            
        try:
            # Get data from channel 1 (X)
            self.scope.write(':WAV:SOURce CHANnel1')
            self.scope.write(':WAV:MODE NORMal')
            self.scope.write(f':WAV:POINts {points}')
            self.scope.write(':WAV:FORMat BYTE')
            
            x_raw = self.scope.query_binary_values(':WAV:DATA?', datatype='B')
            
            # Get data from channel 2 (Y)
            self.scope.write(':WAV:SOURce CHANnel2')
            y_raw = self.scope.query_binary_values(':WAV:DATA?', datatype='B')
            
            # Get scaling parameters
            x_scale = float(self.scope.query(':CHANnel1:SCALe?'))
            y_scale = float(self.scope.query(':CHANnel2:SCALe?'))
            x_offset = float(self.scope.query(':CHANnel1:OFFSet?'))
            y_offset = float(self.scope.query(':CHANnel2:OFFSet?'))
            
            # Convert to voltages
            x_data = ((np.array(x_raw) - 127) * x_scale / 25) - x_offset
            y_data = ((np.array(y_raw) - 127) * y_scale / 25) - y_offset
            
            return x_data, y_data
            
        except Exception as e:
            print(f"Error capturing XY data: {e}")
            return None, None


class LissajousGenerator:
    """Generate Lissajous patterns with various parameters"""
    
    @staticmethod
    def generate(pattern: LissajousPattern, points: int = 1000, 
                 duration: float = 2*np.pi) -> Tuple[np.ndarray, np.ndarray]:
        """Generate Lissajous curve from pattern parameters"""
        t = np.linspace(0, duration, points)
        
        x = pattern.amplitude_x * np.sin(pattern.freq_x * t + pattern.phase)
        y = pattern.amplitude_y * np.sin(pattern.freq_y * t)
        
        return x, y
    
    @staticmethod
    def generate_from_ratio(ratio_x: int, ratio_y: int, 
                           phase: float = 0, points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Generate normalized Lissajous pattern from frequency ratio"""
        pattern = LissajousPattern(
            freq_x=ratio_x,
            freq_y=ratio_y,
            phase=phase,
            amplitude_x=1.0,
            amplitude_y=1.0
        )
        return LissajousGenerator.generate(pattern, points)
    
    @staticmethod
    def get_common_patterns() -> List[LissajousPattern]:
        """Return list of common/interesting Lissajous patterns"""
        patterns = [
            LissajousPattern(1, 1, 0),  # Circle (0°)
            LissajousPattern(1, 1, np.pi/2),  # Circle (90°)
            LissajousPattern(1, 1, np.pi/4),  # Ellipse (45°)
            LissajousPattern(1, 2, 0),  # Figure-8 Vertical
            LissajousPattern(2, 1, 0),  # Figure-8 Horizontal
            LissajousPattern(2, 3, 0),  # 2:3 Pattern
            LissajousPattern(3, 4, 0),  # 3:4 Pattern
            LissajousPattern(3, 2, np.pi/2),  # 3:2 Pattern (90°)
            LissajousPattern(5, 4, 0),  # 5:4 Complex
            LissajousPattern(3, 5, np.pi/4),  # 3:5 Complex (45°)
            LissajousPattern(7, 6, 0),  # 7:6 Dense
            LissajousPattern(8, 5, np.pi/3),  # 8:5 Pattern (60°)
        ]
        
        # Add names as attributes
        names = [
            "Circle (0°)", "Circle (90°)", "Ellipse (45°)",
            "Figure-8 Vertical", "Figure-8 Horizontal", "2:3 Pattern",
            "3:4 Pattern", "3:2 Pattern (90°)", "5:4 Complex",
            "3:5 Complex (45°)", "7:6 Dense", "8:5 Pattern (60°)"
        ]
        
        for p, name in zip(patterns, names):
            p.name = name
            
        return patterns


class InteractiveLissajousViewer:
    """Interactive viewer for exploring Lissajous patterns"""
    
    def __init__(self, scope=None):
        self.scope = scope
        self.analyzer = LissajousXYAnalyzer(scope) if scope else None
        
        # Create figure and axis
        self.fig = plt.figure(figsize=(12, 10), facecolor='#1a1a1a')
        
        # Main plot
        self.ax = plt.subplot2grid((6, 6), (0, 0), colspan=4, rowspan=4)
        self.ax.set_facecolor('black')
        self.ax.set_xlim(-1.2, 1.2)
        self.ax.set_ylim(-1.2, 1.2)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.2, color='green')
        self.ax.set_xlabel('X (CH1)', color='cyan')
        self.ax.set_ylabel('Y (CH2)', color='cyan')
        self.ax.set_title('Lissajous Pattern Viewer', color='white', fontsize=14)
        
        # Initialize pattern
        self.current_pattern = LissajousPattern(3, 2, 0)
        
        # Plot line
        self.line, = self.ax.plot([], [], 'lime', linewidth=2, alpha=0.9)
        self.trace_line, = self.ax.plot([], [], 'lime', linewidth=0.5, alpha=0.3)
        
        # Control panel
        self.setup_controls()
        
        # Info display
        self.info_ax = plt.subplot2grid((6, 6), (0, 4), colspan=2, rowspan=2)
        self.info_ax.axis('off')
        self.info_text = self.info_ax.text(0.1, 0.9, '', transform=self.info_ax.transAxes,
                                           color='white', fontsize=10, 
                                           verticalalignment='top', fontfamily='monospace')
        
        # Pattern gallery
        self.setup_pattern_gallery()
        
        # Animation
        self.animation = None
        self.is_animating = False
        self.trace_points = []
        self.max_trace_points = 500
        
        self.update_pattern()
        
    def setup_controls(self):
        """Setup interactive controls"""
        # Frequency X slider
        ax_freq_x = plt.axes([0.15, 0.25, 0.4, 0.03], facecolor='#333333')
        self.slider_freq_x = Slider(ax_freq_x, 'Freq X', 1, 20, 
                                    valinit=self.current_pattern.freq_x, 
                                    valstep=1, color='cyan')
        self.slider_freq_x.on_changed(self.on_slider_change)
        
        # Frequency Y slider
        ax_freq_y = plt.axes([0.15, 0.20, 0.4, 0.03], facecolor='#333333')
        self.slider_freq_y = Slider(ax_freq_y, 'Freq Y', 1, 20, 
                                    valinit=self.current_pattern.freq_y, 
                                    valstep=1, color='cyan')
        self.slider_freq_y.on_changed(self.on_slider_change)
        
        # Phase slider
        ax_phase = plt.axes([0.15, 0.15, 0.4, 0.03], facecolor='#333333')
        self.slider_phase = Slider(ax_phase, 'Phase', 0, 360, 
                                   valinit=np.degrees(self.current_pattern.phase), 
                                   color='cyan')
        self.slider_phase.on_changed(self.on_slider_change)
        
        # Amplitude X slider
        ax_amp_x = plt.axes([0.15, 0.10, 0.4, 0.03], facecolor='#333333')
        self.slider_amp_x = Slider(ax_amp_x, 'Amp X', 0.1, 1.0, 
                                   valinit=self.current_pattern.amplitude_x, 
                                   color='cyan')
        self.slider_amp_x.on_changed(self.on_slider_change)
        
        # Amplitude Y slider
        ax_amp_y = plt.axes([0.15, 0.05, 0.4, 0.03], facecolor='#333333')
        self.slider_amp_y = Slider(ax_amp_y, 'Amp Y', 0.1, 1.0, 
                                   valinit=self.current_pattern.amplitude_y, 
                                   color='cyan')
        self.slider_amp_y.on_changed(self.on_slider_change)
        
        # Buttons
        ax_animate = plt.axes([0.65, 0.20, 0.1, 0.04])
        self.btn_animate = Button(ax_animate, 'Animate', color='#444444', hovercolor='#666666')
        self.btn_animate.on_clicked(self.toggle_animation)
        
        ax_capture = plt.axes([0.65, 0.15, 0.1, 0.04])
        self.btn_capture = Button(ax_capture, 'Capture', color='#444444', hovercolor='#666666')
        self.btn_capture.on_clicked(self.capture_from_scope)
        
        ax_reset = plt.axes([0.65, 0.10, 0.1, 0.04])
        self.btn_reset = Button(ax_reset, 'Reset', color='#444444', hovercolor='#666666')
        self.btn_reset.on_clicked(self.reset_pattern)
        
        ax_xy_mode = plt.axes([0.65, 0.05, 0.1, 0.04])
        self.btn_xy_mode = Button(ax_xy_mode, 'XY Mode', color='#444444', hovercolor='#666666')
        self.btn_xy_mode.on_clicked(self.toggle_xy_mode)
    
    def setup_pattern_gallery(self):
        """Setup pattern gallery buttons"""
        patterns = LissajousGenerator.get_common_patterns()
        
        # Create small preview axes for each pattern
        for i, pattern in enumerate(patterns[:8]):
            row = i // 4
            col = i % 4
            
            ax = plt.subplot2grid((6, 6), (4 + row, col), colspan=1, rowspan=1)
            ax.set_facecolor('black')
            ax.set_xlim(-1.1, 1.1)
            ax.set_ylim(-1.1, 1.1)
            ax.set_aspect('equal')
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Generate mini pattern
            x, y = LissajousGenerator.generate(pattern, points=200)
            ax.plot(x, y, 'lime', linewidth=1, alpha=0.7)
            
            # Add label
            ratio_x, ratio_y = pattern.get_simplified_ratio()
            ax.set_title(f"{ratio_x}:{ratio_y}", color='cyan', fontsize=8)
            
            # Make clickable
            ax.figure.canvas.mpl_connect('button_press_event', 
                lambda event, p=pattern: self.load_pattern(p) if event.inaxes == ax else None)
    
    def on_slider_change(self, val):
        """Handle slider changes"""
        self.current_pattern.freq_x = self.slider_freq_x.val
        self.current_pattern.freq_y = self.slider_freq_y.val
        self.current_pattern.phase = np.radians(self.slider_phase.val)
        self.current_pattern.amplitude_x = self.slider_amp_x.val
        self.current_pattern.amplitude_y = self.slider_amp_y.val
        
        self.update_pattern()
    
    def update_pattern(self):
        """Update the displayed pattern"""
        x, y = LissajousGenerator.generate(self.current_pattern, points=1000)
        self.line.set_data(x, y)
        
        # Update info display
        ratio_x, ratio_y = self.current_pattern.get_simplified_ratio()
        info = f"Frequency Ratio: {ratio_x}:{ratio_y}\n"
        info += f"X Frequency: {self.current_pattern.freq_x:.0f}\n"
        info += f"Y Frequency: {self.current_pattern.freq_y:.0f}\n"
        info += f"Phase: {np.degrees(self.current_pattern.phase):.1f}°\n"
        info += f"X Amplitude: {self.current_pattern.amplitude_x:.2f}\n"
        info += f"Y Amplitude: {self.current_pattern.amplitude_y:.2f}\n"
        
        self.info_text.set_text(info)
        
        if not self.is_animating:
            self.fig.canvas.draw_idle()
    
    def toggle_animation(self, event):
        """Toggle animation on/off"""
        if self.is_animating:
            if self.animation:
                self.animation.event_source.stop()
            self.is_animating = False
            self.btn_animate.label.set_text('Animate')
            self.trace_points = []
        else:
            self.animation = animation.FuncAnimation(
                self.fig, self.animate_frame, interval=20, blit=False
            )
            self.is_animating = True
            self.btn_animate.label.set_text('Stop')
        
        self.fig.canvas.draw_idle()
    
    def animate_frame(self, frame):
        """Animation frame update"""
        # Rotating phase animation
        animated_phase = self.current_pattern.phase + frame * 0.02
        
        pattern = LissajousPattern(
            self.current_pattern.freq_x,
            self.current_pattern.freq_y,
            animated_phase,
            self.current_pattern.amplitude_x,
            self.current_pattern.amplitude_y
        )
        
        x, y = LissajousGenerator.generate(pattern, points=1000)
        self.line.set_data(x, y)
        
        # Add to trace
        if len(self.trace_points) > self.max_trace_points:
            self.trace_points.pop(0)
        
        # Sample a point for the trace
        idx = (frame * 10) % len(x)
        self.trace_points.append((x[idx], y[idx]))
        
        if self.trace_points:
            trace_x, trace_y = zip(*self.trace_points)
            self.trace_line.set_data(trace_x, trace_y)
        
        return self.line, self.trace_line
    
    def capture_from_scope(self, event):
        """Capture pattern from oscilloscope"""
        if not self.analyzer:
            print("No oscilloscope connected")
            return
        
        print("Capturing from oscilloscope...")
        x_data, y_data = self.analyzer.capture_xy_data()
        
        if x_data is not None:
            pattern = self.analyzer.analyze_pattern(x_data, y_data)
            self.load_pattern(pattern)
            print(f"✅ Captured pattern: {pattern.ratio_x}:{pattern.ratio_y}")
    
    def toggle_xy_mode(self, event):
        """Toggle XY mode on oscilloscope"""
        if not self.analyzer:
            print("No oscilloscope connected")
            return
        
        if self.analyzer.xy_mode_enabled:
            self.analyzer.disable_xy_mode()
            self.btn_xy_mode.label.set_text('XY Mode')
        else:
            self.analyzer.enable_xy_mode()
            self.btn_xy_mode.label.set_text('YT Mode')
        
        self.fig.canvas.draw_idle()
    
    def load_pattern(self, pattern):
        """Load a pattern into the viewer"""
        self.current_pattern = pattern
        
        # Update sliders
        self.slider_freq_x.set_val(pattern.freq_x)
        self.slider_freq_y.set_val(pattern.freq_y)
        self.slider_phase.set_val(np.degrees(pattern.phase))
        self.slider_amp_x.set_val(pattern.amplitude_x)
        self.slider_amp_y.set_val(pattern.amplitude_y)
        
        self.update_pattern()
    
    def reset_pattern(self, event):
        """Reset to default pattern"""
        self.load_pattern(LissajousPattern(3, 2, 0))
    
    def run(self):
        """Start the interactive viewer"""
        plt.tight_layout()
        plt.show()


def main():
    """Main entry point for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Lissajous XY Pattern Analyzer')
    parser.add_argument('--scope-ip', help='Oscilloscope IP address')
    parser.add_argument('--demo', action='store_true', help='Run in demo mode without scope')
    
    args = parser.parse_args()
    
    scope = None
    if args.scope_ip and not args.demo:
        try:
            rm = pyvisa.ResourceManager()
            scope = rm.open_resource(f'TCPIP::{args.scope_ip}::INSTR')
            print(f"✅ Connected to oscilloscope at {args.scope_ip}")
        except Exception as e:
            print(f"❌ Failed to connect to scope: {e}")
            print("Running in demo mode...")
    
    # Create and run viewer
    viewer = InteractiveLissajousViewer(scope)
    viewer.run()
    
    if scope:
        scope.close()


if __name__ == "__main__":
    main()