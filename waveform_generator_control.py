#!/usr/bin/env python3
"""
Integrated Waveform Generator Control
Generate test signals through sound card while monitoring on oscilloscope
"""

import warnings
warnings.filterwarnings('ignore', message='Unable to import Axes3D.*', category=UserWarning)

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import threading
import time
from rigol_oscilloscope_control import RigolDS1104Z
import config

class WaveformGeneratorControl:
    def __init__(self):
        self.sample_rate = 48000
        self.is_playing = False
        self.stream = None
        
        # Default parameters
        self.freq_left = 440.0
        self.freq_right = 440.0
        self.phase = 0.0
        self.amplitude = 0.5
        self.waveform_type = 'sine'
        
        # Oscilloscope connection
        self.scope_ctrl = None
        self.scope = None
        
    def connect_scope(self):
        """Connect to oscilloscope for monitoring"""
        try:
            self.scope_ctrl = RigolDS1104Z(config.RIGOL_IP)
            if self.scope_ctrl.connect():
                self.scope = self.scope_ctrl.scope
                print("✅ Oscilloscope connected")
                return True
        except:
            pass
        print("⚠️  No oscilloscope connection - generator only mode")
        return False
    
    def audio_callback(self, outdata, frames, time_info, status):
        """Real-time audio generation callback"""
        if status:
            print(status)
        
        t = np.arange(frames) / self.sample_rate
        
        # Generate waveforms based on type
        if self.waveform_type == 'sine':
            left = self.amplitude * np.sin(2 * np.pi * self.freq_left * t)
            right = self.amplitude * np.sin(2 * np.pi * self.freq_right * t + self.phase)
        
        elif self.waveform_type == 'square':
            left = self.amplitude * np.sign(np.sin(2 * np.pi * self.freq_left * t))
            right = self.amplitude * np.sign(np.sin(2 * np.pi * self.freq_right * t + self.phase))
        
        elif self.waveform_type == 'triangle':
            left = self.amplitude * 2 * np.arcsin(np.sin(2 * np.pi * self.freq_left * t)) / np.pi
            right = self.amplitude * 2 * np.arcsin(np.sin(2 * np.pi * self.freq_right * t + self.phase)) / np.pi
        
        elif self.waveform_type == 'sawtooth':
            left = self.amplitude * 2 * ((self.freq_left * t) % 1 - 0.5)
            right = self.amplitude * 2 * ((self.freq_right * t + self.phase/(2*np.pi)) % 1 - 0.5)
        
        else:  # noise
            left = self.amplitude * np.random.randn(frames) * 0.3
            right = self.amplitude * np.random.randn(frames) * 0.3
        
        outdata[:, 0] = left
        outdata[:, 1] = right
    
    def start_generator(self):
        """Start waveform generation"""
        if not self.is_playing:
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=2,
                callback=self.audio_callback,
                blocksize=256
            )
            self.stream.start()
            self.is_playing = True
            return True
        return False
    
    def stop_generator(self):
        """Stop waveform generation"""
        if self.is_playing and self.stream:
            self.stream.stop()
            self.stream.close()
            self.is_playing = False
            return True
        return False
    
    def measure_output(self):
        """Measure actual output on oscilloscope"""
        if not self.scope:
            return None
        
        measurements = {}
        for ch in [1, 2]:
            vpp = self.scope_ctrl.get_measurement(ch, 'VPP')
            freq = self.scope_ctrl.get_measurement(ch, 'FREQ')
            
            measurements[f'ch{ch}'] = {
                'vpp': vpp if vpp and vpp < 9e37 else 0,
                'freq': freq if freq and freq > 0 and freq < 9e37 else 0
            }
        
        return measurements
    
    def create_gui(self):
        """Create interactive control panel"""
        # Create figure
        self.fig = plt.figure(figsize=(14, 10), facecolor='#1a1a1a')
        self.fig.suptitle('Waveform Generator Control Panel', color='cyan', fontsize=16)
        
        # Main display area
        self.ax_display = plt.subplot2grid((5, 3), (0, 0), colspan=2, rowspan=2)
        self.ax_display.set_facecolor('black')
        self.ax_display.set_xlim(-1.2, 1.2)
        self.ax_display.set_ylim(-1.2, 1.2)
        self.ax_display.set_aspect('equal')
        self.ax_display.grid(True, alpha=0.2, color='green')
        self.ax_display.set_xlabel('Left Channel', color='cyan')
        self.ax_display.set_ylabel('Right Channel', color='cyan')
        self.ax_display.set_title('XY Preview (Lissajous)', color='white')
        
        # Waveform preview
        self.line_preview, = self.ax_display.plot([], [], 'lime', linewidth=2)
        
        # Control sliders
        slider_color = '#444444'
        
        # Frequency controls
        ax_freq_l = plt.axes([0.15, 0.45, 0.35, 0.03], facecolor=slider_color)
        self.slider_freq_l = Slider(ax_freq_l, 'Left Freq (Hz)', 20, 2000, 
                                    valinit=self.freq_left, valstep=1, color='cyan')
        
        ax_freq_r = plt.axes([0.15, 0.40, 0.35, 0.03], facecolor=slider_color)
        self.slider_freq_r = Slider(ax_freq_r, 'Right Freq (Hz)', 20, 2000, 
                                    valinit=self.freq_right, valstep=1, color='yellow')
        
        # Phase control
        ax_phase = plt.axes([0.15, 0.35, 0.35, 0.03], facecolor=slider_color)
        self.slider_phase = Slider(ax_phase, 'Phase (°)', 0, 360, 
                                  valinit=0, color='magenta')
        
        # Amplitude control
        ax_amp = plt.axes([0.15, 0.30, 0.35, 0.03], facecolor=slider_color)
        self.slider_amp = Slider(ax_amp, 'Amplitude', 0, 1, 
                                valinit=self.amplitude, color='lime')
        
        # Preset frequency ratios
        ax_presets = plt.axes([0.15, 0.05, 0.15, 0.2], facecolor=slider_color)
        self.radio_presets = RadioButtons(ax_presets, 
            ('1:1', '2:1', '3:2', '4:3', '5:4', '3:1', 'Custom'),
            active=0)
        
        # Waveform type
        ax_wave = plt.axes([0.35, 0.05, 0.15, 0.2], facecolor=slider_color)
        self.radio_wave = RadioButtons(ax_wave,
            ('Sine', 'Square', 'Triangle', 'Saw', 'Noise'),
            active=0)
        
        # Control buttons
        ax_start = plt.axes([0.55, 0.15, 0.08, 0.04])
        self.btn_start = Button(ax_start, 'START', color='green', hovercolor='lightgreen')
        
        ax_stop = plt.axes([0.55, 0.10, 0.08, 0.04])
        self.btn_stop = Button(ax_stop, 'STOP', color='red', hovercolor='pink')
        
        ax_measure = plt.axes([0.55, 0.05, 0.08, 0.04])
        self.btn_measure = Button(ax_measure, 'Measure', color='blue', hovercolor='lightblue')
        
        # Info display
        self.ax_info = plt.subplot2grid((5, 3), (0, 2), colspan=1, rowspan=2)
        self.ax_info.axis('off')
        self.info_text = self.ax_info.text(0.05, 0.95, '', transform=self.ax_info.transAxes,
                                           color='white', fontsize=9, fontfamily='monospace',
                                           verticalalignment='top')
        
        # Connect callbacks
        self.slider_freq_l.on_changed(self.update_params)
        self.slider_freq_r.on_changed(self.update_params)
        self.slider_phase.on_changed(self.update_params)
        self.slider_amp.on_changed(self.update_params)
        self.radio_presets.on_clicked(self.set_preset)
        self.radio_wave.on_clicked(self.set_waveform)
        self.btn_start.on_clicked(self.on_start)
        self.btn_stop.on_clicked(self.on_stop)
        self.btn_measure.on_clicked(self.on_measure)
        
        # Initial update
        self.update_preview()
        self.update_info()
    
    def update_params(self, val):
        """Update parameters from sliders"""
        self.freq_left = self.slider_freq_l.val
        self.freq_right = self.slider_freq_r.val
        self.phase = np.radians(self.slider_phase.val)
        self.amplitude = self.slider_amp.val
        self.update_preview()
        self.update_info()
    
    def set_preset(self, label):
        """Set preset frequency ratio"""
        presets = {
            '1:1': (440, 440),
            '2:1': (880, 440),
            '3:2': (660, 440),
            '4:3': (586.67, 440),
            '5:4': (550, 440),
            '3:1': (1320, 440),
        }
        
        if label in presets:
            freq_l, freq_r = presets[label]
            self.slider_freq_l.set_val(freq_l)
            self.slider_freq_r.set_val(freq_r)
    
    def set_waveform(self, label):
        """Set waveform type"""
        self.waveform_type = label.lower()
        self.update_preview()
    
    def update_preview(self):
        """Update Lissajous preview"""
        t = np.linspace(0, 2*np.pi, 1000)
        
        if self.waveform_type == 'sine':
            x = np.sin(self.freq_left/440 * t)
            y = np.sin(self.freq_right/440 * t + self.phase)
        else:
            # Simplified preview for other waveforms
            x = np.sin(self.freq_left/440 * t)
            y = np.sin(self.freq_right/440 * t + self.phase)
        
        self.line_preview.set_data(x, y)
        self.fig.canvas.draw_idle()
    
    def update_info(self):
        """Update info display"""
        ratio = self.freq_left / self.freq_right if self.freq_right > 0 else 0
        
        info = f"GENERATOR STATUS\n"
        info += f"{'='*20}\n"
        info += f"Status: {'PLAYING' if self.is_playing else 'STOPPED'}\n\n"
        info += f"LEFT CHANNEL:\n"
        info += f"  Freq: {self.freq_left:.1f} Hz\n"
        info += f"  Amplitude: {self.amplitude*100:.0f}%\n\n"
        info += f"RIGHT CHANNEL:\n"
        info += f"  Freq: {self.freq_right:.1f} Hz\n"
        info += f"  Amplitude: {self.amplitude*100:.0f}%\n\n"
        info += f"PATTERN:\n"
        info += f"  Ratio: {ratio:.3f}\n"
        info += f"  Phase: {np.degrees(self.phase):.0f}°\n"
        info += f"  Type: {self.waveform_type}\n\n"
        
        if self.scope:
            info += f"SCOPE: Connected\n"
        else:
            info += f"SCOPE: Not connected\n"
        
        self.info_text.set_text(info)
        self.fig.canvas.draw_idle()
    
    def on_start(self, event):
        """Start button callback"""
        if self.start_generator():
            print("✅ Generator started")
        self.update_info()
    
    def on_stop(self, event):
        """Stop button callback"""
        if self.stop_generator():
            print("⏹️  Generator stopped")
        self.update_info()
    
    def on_measure(self, event):
        """Measure button callback"""
        if self.scope:
            measurements = self.measure_output()
            if measurements:
                print("\n📏 MEASUREMENTS:")
                print(f"  CH1: {measurements['ch1']['vpp']:.3f} Vpp @ {measurements['ch1']['freq']:.1f} Hz")
                print(f"  CH2: {measurements['ch2']['vpp']:.3f} Vpp @ {measurements['ch2']['freq']:.1f} Hz")
        else:
            print("No oscilloscope connected")
    
    def run(self):
        """Run the GUI"""
        self.create_gui()
        plt.show()

def main():
    print("🎛️ WAVEFORM GENERATOR CONTROL")
    print("="*50)
    
    generator = WaveformGeneratorControl()
    
    # Try to connect to oscilloscope
    generator.connect_scope()
    
    print("\n📊 Controls:")
    print("  • Adjust frequency sliders for each channel")
    print("  • Use presets for common ratios")
    print("  • Phase slider creates different patterns")
    print("  • Amplitude controls output level")
    print("\nLaunching control panel...")
    
    generator.run()
    
    # Cleanup
    generator.stop_generator()
    if generator.scope:
        generator.scope.close()
    
    print("\n✅ Generator closed")

if __name__ == "__main__":
    main()