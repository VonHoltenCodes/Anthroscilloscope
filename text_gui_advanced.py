#!/usr/bin/env python3
"""
Advanced Interactive GUI for Lissajous Text Rendering
Phase 4: Advanced features - rotation, effects, multi-line

Created by Trenton Von Holten
https://github.com/VonHoltenCodes/Anthroscilloscope
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Slider, Button, RadioButtons, CheckButtons
import matplotlib.patches as mpatches
from text_rendering.lissajous_text_renderer import LissajousTextRenderer
from text_rendering.effects import TextEffects, MultiLineText
import numpy as np
import json
import os
from datetime import datetime
import branding


class AdvancedLissajousTextGUI:
    """Advanced GUI with Phase 4 features"""

    def __init__(self):
        self.renderer = LissajousTextRenderer()
        self.effects = TextEffects()
        self.current_text = "HELLO"
        self.font_scale = 1.0
        self.speed_scale = 1.0
        self.sample_rate = 44100

        # Phase 4 parameters
        self.rotation = 0.0
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.skew_x = 0.0
        self.wave_enabled = False
        self.wave_amplitude = 0.0
        self.wave_frequency = 1.0
        self.effect_3d_enabled = False
        self.depth_3d = 0.0
        self.tilt_3d = 0.0
        self.shadow_enabled = False
        self.multiline_enabled = False

        # Create figure and layout
        self.fig = plt.figure(figsize=(16, 10))

        # Title with version
        title = f'Anthroscilloscope Advanced - Lissajous Text Generator v{branding.VERSION} (Phase 4)'
        self.fig.suptitle(title, fontsize=14, fontweight='bold', color='white')
        self.fig.patch.set_facecolor('#1a1a1a')

        # Watermark
        self.fig.text(0.99, 0.01, branding.get_watermark(),
                     ha='right', va='bottom', fontsize=7,
                     color='gray', alpha=0.6, family='monospace')

        # Layout: Main preview (larger) + lots of controls
        self.ax_preview = plt.subplot2grid((16, 4), (1, 0), colspan=3, rowspan=8)

        # Basic controls (left column)
        self.ax_textbox = plt.subplot2grid((16, 4), (10, 0), colspan=2)
        self.ax_size_slider = plt.subplot2grid((16, 4), (11, 0), colspan=2)
        self.ax_speed_slider = plt.subplot2grid((16, 4), (12, 0), colspan=2)

        # Phase 4 Transform controls (middle column)
        self.ax_rotation_slider = plt.subplot2grid((16, 4), (10, 2))
        self.ax_scalex_slider = plt.subplot2grid((16, 4), (11, 2))
        self.ax_scaley_slider = plt.subplot2grid((16, 4), (12, 2))
        self.ax_skew_slider = plt.subplot2grid((16, 4), (13, 2))

        # Effects checkboxes (right column)
        self.ax_effects = plt.subplot2grid((16, 4), (1, 3), rowspan=6)

        # Buttons (right column, bottom)
        self.ax_export_btn = plt.subplot2grid((16, 4), (10, 3))
        self.ax_save_btn = plt.subplot2grid((16, 4), (11, 3))
        self.ax_load_btn = plt.subplot2grid((16, 4), (12, 3))
        self.ax_about_btn = plt.subplot2grid((16, 4), (0, 3))

        # Info panel
        self.ax_info = plt.subplot2grid((16, 4), (15, 0), colspan=4)

        self._setup_preview()
        self._setup_controls()
        self._setup_info()

        # Initial render
        self.update_preview(self.current_text)

    def _setup_preview(self):
        """Setup main preview canvas"""
        self.ax_preview.set_facecolor('black')
        self.ax_preview.set_xlabel('X Channel (Left Audio)', color='white')
        self.ax_preview.set_ylabel('Y Channel (Right Audio)', color='white')
        self.ax_preview.tick_params(colors='white')
        for spine in self.ax_preview.spines.values():
            spine.set_color('white')
        self.ax_preview.grid(True, alpha=0.2, color='gray')
        self.ax_preview.set_aspect('equal')

    def _setup_controls(self):
        """Setup all control widgets"""

        # Text input
        self.ax_textbox.set_facecolor('#2a2a2a')
        self.textbox = TextBox(self.ax_textbox, 'Text:', initial=self.current_text,
                              color='#3a3a3a', hovercolor='#4a4a4a')
        self.textbox.label.set_color('white')
        self.textbox.on_submit(self.on_text_change)

        # Font size
        self.ax_size_slider.set_facecolor('#2a2a2a')
        self.size_slider = Slider(self.ax_size_slider, 'Size', 0.3, 3.0,
                                 valinit=1.0, color='lime', track_color='#3a3a3a')
        self.size_slider.label.set_color('white')
        self.size_slider.valtext.set_color('white')
        self.size_slider.on_changed(self.on_size_change)

        # Speed
        self.ax_speed_slider.set_facecolor('#2a2a2a')
        self.speed_slider = Slider(self.ax_speed_slider, 'Speed', 0.1, 5.0,
                                  valinit=1.0, color='cyan', track_color='#3a3a3a')
        self.speed_slider.label.set_color('white')
        self.speed_slider.valtext.set_color('white')
        self.speed_slider.on_changed(self.on_speed_change)

        # Rotation
        self.ax_rotation_slider.set_facecolor('#2a2a2a')
        self.rotation_slider = Slider(self.ax_rotation_slider, 'Rotate', 0, 360,
                                     valinit=0, color='orange', track_color='#3a3a3a')
        self.rotation_slider.label.set_color('white')
        self.rotation_slider.valtext.set_color('white')
        self.rotation_slider.on_changed(self.on_rotation_change)

        # Scale X
        self.ax_scalex_slider.set_facecolor('#2a2a2a')
        self.scalex_slider = Slider(self.ax_scalex_slider, 'Scale X', 0.1, 3.0,
                                   valinit=1.0, color='magenta', track_color='#3a3a3a')
        self.scalex_slider.label.set_color('white')
        self.scalex_slider.valtext.set_color('white')
        self.scalex_slider.on_changed(self.on_scalex_change)

        # Scale Y
        self.ax_scaley_slider.set_facecolor('#2a2a2a')
        self.scaley_slider = Slider(self.ax_scaley_slider, 'Scale Y', 0.1, 3.0,
                                   valinit=1.0, color='magenta', track_color='#3a3a3a')
        self.scaley_slider.label.set_color('white')
        self.scaley_slider.valtext.set_color('white')
        self.scaley_slider.on_changed(self.on_scaley_change)

        # Skew
        self.ax_skew_slider.set_facecolor('#2a2a2a')
        self.skew_slider = Slider(self.ax_skew_slider, 'Skew', -1.0, 1.0,
                                 valinit=0.0, color='yellow', track_color='#3a3a3a')
        self.skew_slider.label.set_color('white')
        self.skew_slider.valtext.set_color('white')
        self.skew_slider.on_changed(self.on_skew_change)

        # Effects checkboxes
        self.ax_effects.set_facecolor('#2a2a2a')
        self.ax_effects.set_title('Effects', color='white', fontsize=10)
        self.effects_check = CheckButtons(
            self.ax_effects,
            ['Shadow', '3D', 'Wave'],
            [False, False, False]
        )
        for label in self.effects_check.labels:
            label.set_color('white')
        self.effects_check.on_clicked(self.on_effects_toggle)

        # Buttons
        self.ax_export_btn.set_facecolor('#2a2a2a')
        self.export_btn = Button(self.ax_export_btn, 'Export WAV',
                                color='#3a3a3a', hovercolor='#4a4a4a')
        self.export_btn.label.set_color('lime')
        self.export_btn.on_clicked(self.on_export)

        self.ax_save_btn.set_facecolor('#2a2a2a')
        self.save_btn = Button(self.ax_save_btn, 'Save Preset',
                              color='#3a3a3a', hovercolor='#4a4a4a')
        self.save_btn.label.set_color('yellow')
        self.save_btn.on_clicked(self.on_save)

        self.ax_load_btn.set_facecolor('#2a2a2a')
        self.load_btn = Button(self.ax_load_btn, 'Load Preset',
                              color='#3a3a3a', hovercolor='#4a4a4a')
        self.load_btn.label.set_color('orange')
        self.load_btn.on_clicked(self.on_load)

        self.ax_about_btn.set_facecolor('#2a2a2a')
        self.about_btn = Button(self.ax_about_btn, 'About',
                               color='#3a3a3a', hovercolor='#4a4a4a')
        self.about_btn.label.set_color('cyan')
        self.about_btn.on_clicked(self.on_about)

    def _setup_info(self):
        """Setup info panel"""
        self.ax_info.axis('off')
        self.ax_info.set_facecolor('#1a1a1a')
        self.info_text = self.ax_info.text(
            0.5, 0.5, '',
            ha='center', va='center',
            color='white', fontsize=9,
            family='monospace'
        )

    def apply_effects(self, x, y):
        """Apply all active effects to coordinates"""
        # Apply rotation
        if self.rotation != 0:
            x, y = self.effects.rotate(x, y, self.rotation)

        # Apply scaling
        if self.scale_x != 1.0 or self.scale_y != 1.0:
            x, y = self.effects.scale_xy(x, y, self.scale_x, self.scale_y)

        # Apply skew
        if self.skew_x != 0:
            x, y = self.effects.skew(x, y, self.skew_x, 0)

        # Apply shadow
        if self.shadow_enabled:
            x, y = self.effects.shadow_effect(x, y, offset_x=0.15, offset_y=-0.15)

        # Apply 3D
        if self.effect_3d_enabled:
            x, y = self.effects.perspective_3d(x, y, depth=self.depth_3d, tilt_y=self.tilt_3d)

        # Apply wave
        if self.wave_enabled:
            x, y = self.effects.wave_effect(x, y, self.wave_amplitude, self.wave_frequency)

        return x, y

    def update_preview(self, text):
        """Update preview with effects"""
        try:
            self.ax_preview.clear()
            self._setup_preview()

            # Generate base path
            x, y = self.renderer.text_to_path.text_to_path(text)

            if len(x) == 0:
                self.ax_preview.text(0, 0, 'No renderable characters',
                                    ha='center', va='center', color='red', fontsize=14)
                self.update_info("⚠️  No renderable characters")
                self.fig.canvas.draw_idle()
                return

            # Apply font scaling
            x = np.array(x) * self.font_scale
            y = np.array(y) * self.font_scale

            # Apply effects
            x, y = self.apply_effects(x, y)

            # Plot
            self.ax_preview.plot(x, y, 'lime', linewidth=2, alpha=0.9)
            self.ax_preview.plot(x[0], y[0], 'ro', markersize=8, label='Start', zorder=10)
            self.ax_preview.plot(x[-1], y[-1], 'bs', markersize=8, label='End', zorder=10)

            effects_str = []
            if self.rotation != 0: effects_str.append(f"Rot:{self.rotation:.0f}°")
            if self.shadow_enabled: effects_str.append("Shadow")
            if self.effect_3d_enabled: effects_str.append("3D")
            if self.wave_enabled: effects_str.append("Wave")

            title = f'Preview: "{text}"'
            if effects_str:
                title += f" [{', '.join(effects_str)}]"

            self.ax_preview.set_title(title, color='white', fontsize=12, pad=10)
            legend = self.ax_preview.legend(facecolor='#2a2a2a', edgecolor='white',
                                           labelcolor='white', loc='upper right')

            # Update info
            num_points = len(x)
            duration = num_points / self.sample_rate * self.speed_scale
            self.update_info(
                f"Points: {num_points} | Duration: {duration:.2f}s | "
                f"Rotation: {self.rotation:.0f}° | Scale: {self.scale_x:.2f}x{self.scale_y:.2f} | "
                f"Effects: {len([e for e in [self.shadow_enabled, self.effect_3d_enabled, self.wave_enabled] if e])}"
            )

            self.fig.canvas.draw_idle()

        except Exception as e:
            self.ax_preview.text(0, 0, f'Error: {str(e)}',
                               ha='center', va='center', color='red', fontsize=12)
            self.update_info(f"❌ Error: {str(e)}")
            self.fig.canvas.draw_idle()

    def update_info(self, message):
        """Update info panel"""
        self.info_text.set_text(message)

    def on_text_change(self, text):
        """Text input handler"""
        self.current_text = text.upper()
        self.update_preview(self.current_text)

    def on_size_change(self, val):
        """Font size handler"""
        self.font_scale = val
        self.update_preview(self.current_text)

    def on_speed_change(self, val):
        """Speed handler"""
        self.speed_scale = val
        self.update_preview(self.current_text)

    def on_rotation_change(self, val):
        """Rotation handler"""
        self.rotation = val
        self.update_preview(self.current_text)

    def on_scalex_change(self, val):
        """Scale X handler"""
        self.scale_x = val
        self.update_preview(self.current_text)

    def on_scaley_change(self, val):
        """Scale Y handler"""
        self.scale_y = val
        self.update_preview(self.current_text)

    def on_skew_change(self, val):
        """Skew handler"""
        self.skew_x = val
        self.update_preview(self.current_text)

    def on_effects_toggle(self, label):
        """Effects toggle handler"""
        if label == 'Shadow':
            self.shadow_enabled = not self.shadow_enabled
        elif label == '3D':
            self.effect_3d_enabled = not self.effect_3d_enabled
            self.depth_3d = 0.5 if self.effect_3d_enabled else 0.0
            self.tilt_3d = 0.3 if self.effect_3d_enabled else 0.0
        elif label == 'Wave':
            self.wave_enabled = not self.wave_enabled
            self.wave_amplitude = 0.15 if self.wave_enabled else 0.0
            self.wave_frequency = 5.0 if self.wave_enabled else 1.0

        self.update_preview(self.current_text)

    def on_export(self, event):
        """Export with effects"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_text = "".join(c for c in self.current_text if c.isalnum())[:20]
            filename = f"output/Anthroscilloscope_Advanced_{safe_text}_{timestamp}.wav"

            os.makedirs('output', exist_ok=True)

            # Generate with effects
            x, y = self.renderer.text_to_path.text_to_path(self.current_text)
            x = np.array(x) * self.font_scale
            y = np.array(y) * self.font_scale
            x, y = self.apply_effects(x, y)

            duration = self.renderer.path_to_audio.calculate_audio_duration(len(x)) * self.speed_scale

            self.renderer.path_to_audio.save_wav(x, y, filename, duration=duration, loop_count=60)

            print(f"✅ Exported WAV with Phase 4 effects: {filename}")
            print(f"   Generated by {branding.get_short_attribution()}")
            self.update_info(f"✅ Exported: {filename}")

        except Exception as e:
            self.update_info(f"❌ Export failed: {str(e)}")
            print(f"❌ Export error: {e}")

    def on_save(self, event):
        """Save preset with Phase 4 settings"""
        try:
            preset = {
                'text': self.current_text,
                'font_scale': self.font_scale,
                'speed_scale': self.speed_scale,
                'rotation': self.rotation,
                'scale_x': self.scale_x,
                'scale_y': self.scale_y,
                'skew_x': self.skew_x,
                'shadow': self.shadow_enabled,
                '3d': self.effect_3d_enabled,
                'wave': self.wave_enabled,
                'timestamp': datetime.now().isoformat(),
                'version': 'phase4'
            }

            os.makedirs('presets', exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"presets/preset_advanced_{timestamp}.json"

            with open(filename, 'w') as f:
                json.dump(preset, f, indent=2)

            self.update_info(f"✅ Saved advanced preset: {filename}")
            print(f"✅ Saved preset: {filename}")

        except Exception as e:
            self.update_info(f"❌ Save failed: {str(e)}")

    def on_load(self, event):
        """Load preset (Phase 4 compatible)"""
        try:
            presets_dir = 'presets'
            if not os.path.exists(presets_dir):
                self.update_info("⚠️  No presets directory")
                return

            presets = [f for f in os.listdir(presets_dir) if f.endswith('.json')]
            if not presets:
                self.update_info("⚠️  No presets found")
                return

            latest = max(presets, key=lambda f: os.path.getmtime(os.path.join(presets_dir, f)))
            filepath = os.path.join(presets_dir, latest)

            with open(filepath, 'r') as f:
                preset = json.load(f)

            # Load basic settings
            self.current_text = preset['text']
            self.font_scale = preset['font_scale']
            self.speed_scale = preset['speed_scale']

            # Load Phase 4 settings if available
            if preset.get('version') == 'phase4':
                self.rotation = preset.get('rotation', 0)
                self.scale_x = preset.get('scale_x', 1.0)
                self.scale_y = preset.get('scale_y', 1.0)
                self.skew_x = preset.get('skew_x', 0.0)
                self.shadow_enabled = preset.get('shadow', False)
                self.effect_3d_enabled = preset.get('3d', False)
                self.wave_enabled = preset.get('wave', False)

                # Update sliders
                self.rotation_slider.set_val(self.rotation)
                self.scalex_slider.set_val(self.scale_x)
                self.scaley_slider.set_val(self.scale_y)
                self.skew_slider.set_val(self.skew_x)

            # Update basic controls
            self.textbox.set_val(self.current_text)
            self.size_slider.set_val(self.font_scale)
            self.speed_slider.set_val(self.speed_scale)

            self.update_preview(self.current_text)
            self.update_info(f"✅ Loaded: {latest}")

        except Exception as e:
            self.update_info(f"❌ Load failed: {str(e)}")

    def on_about(self, event):
        """Show about dialog"""
        about_fig = plt.figure(figsize=(10, 8))
        about_fig.patch.set_facecolor('#1a1a1a')
        about_ax = about_fig.add_subplot(111)
        about_ax.axis('off')
        about_ax.set_facecolor('#1a1a1a')

        credits_text = branding.get_credits_text()
        about_ax.text(0.5, 0.6, credits_text,
                     ha='center', va='center',
                     color='lime', fontsize=9,
                     family='monospace',
                     transform=about_ax.transAxes)

        phase4_info = """
        Phase 4 Advanced Features:
        • Rotation (0-360°)
        • Independent X/Y Scaling
        • Skew/Italics Effect
        • Shadow Effect
        • 3D Perspective
        • Wave Distortion
        """

        about_ax.text(0.5, 0.3, phase4_info,
                     ha='center', va='center',
                     color='cyan', fontsize=10,
                     family='monospace',
                     transform=about_ax.transAxes)

        tagline = branding.TAGLINES[4]
        about_ax.text(0.5, 0.05, tagline,
                     ha='center', va='bottom',
                     color='cyan', fontsize=10,
                     style='italic',
                     transform=about_ax.transAxes)

        plt.tight_layout()
        plt.show()

        self.update_info("ℹ️  About dialog displayed")

    def show(self):
        """Display GUI"""
        plt.tight_layout()
        plt.show()


def main():
    """Launch advanced GUI"""
    print(branding.LOGO_COMPACT)
    print()
    print(f"  {branding.PROJECT_NAME} v{branding.VERSION} - Phase 4")
    print(f"  Created by {branding.AUTHOR}")
    print(f"  {branding.PROJECT_URL}")
    print()
    print("=" * 70)
    print("ADVANCED TEXT GENERATOR - Phase 4 Features")
    print("=" * 70)
    print()
    print("New Phase 4 Features:")
    print("  ✓ Rotation (0-360°)")
    print("  ✓ Independent X/Y scaling")
    print("  ✓ Skew/Italics effect")
    print("  ✓ Shadow effect")
    print("  ✓ 3D perspective")
    print("  ✓ Wave distortion")
    print()
    print("Plus all Phase 3 features:")
    print("  ✓ Real-time preview")
    print("  ✓ Font size & speed control")
    print("  ✓ Export to WAV")
    print("  ✓ Save/Load presets")
    print()
    print("=" * 70)
    print("Launching Advanced GUI...")
    print("=" * 70)
    print()

    gui = AdvancedLissajousTextGUI()
    gui.show()


if __name__ == '__main__':
    main()
