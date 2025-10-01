#!/usr/bin/env python3
"""
Interactive GUI for Lissajous Text Rendering
Phase 3: Interactive UI with matplotlib widgets

Features:
- Text input field
- Font size slider
- Real-time preview
- Speed control
- Save/load text sequences
- Export to WAV

Created by VonHolten
https://github.com/VonHoltenCodes/Anthroscilloscope
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Slider, Button
import matplotlib.patches as mpatches
from text_rendering.lissajous_text_renderer import LissajousTextRenderer
import numpy as np
import json
import os
from datetime import datetime
import branding


class LissajousTextGUI:
    """Interactive GUI for text-to-Lissajous conversion"""

    def __init__(self):
        self.renderer = LissajousTextRenderer()
        self.current_text = "HELLO"
        self.font_scale = 1.0
        self.speed_scale = 1.0
        self.sample_rate = 44100

        # Create figure and layout
        self.fig = plt.figure(figsize=(14, 9))

        # Title with version and attribution
        title = f'Anthroscilloscope - Lissajous Text Generator v{branding.VERSION}'
        self.fig.suptitle(title, fontsize=14, fontweight='bold', color='white')
        self.fig.patch.set_facecolor('#1a1a1a')

        # Add watermark in corner
        self.fig.text(0.99, 0.01, branding.get_watermark(),
                     ha='right', va='bottom', fontsize=7,
                     color='gray', alpha=0.6, family='monospace')

        # Define axes layout
        # Main preview (large, centered)
        self.ax_preview = plt.subplot2grid((12, 3), (1, 0), colspan=3, rowspan=6)

        # Controls on left side
        self.ax_textbox = plt.subplot2grid((12, 3), (8, 0), colspan=2)
        self.ax_size_slider = plt.subplot2grid((12, 3), (9, 0), colspan=2)
        self.ax_speed_slider = plt.subplot2grid((12, 3), (10, 0), colspan=2)

        # Buttons on right side
        self.ax_export_btn = plt.subplot2grid((12, 3), (8, 2))
        self.ax_save_btn = plt.subplot2grid((12, 3), (9, 2))
        self.ax_load_btn = plt.subplot2grid((12, 3), (10, 2))
        self.ax_about_btn = plt.subplot2grid((12, 3), (0, 2))

        # Info panel at bottom
        self.ax_info = plt.subplot2grid((12, 3), (11, 0), colspan=3)

        self._setup_preview()
        self._setup_controls()
        self._setup_info()

        # Initial render
        self.update_preview(self.current_text)

    def _setup_preview(self):
        """Setup the main preview canvas"""
        self.ax_preview.set_facecolor('black')
        self.ax_preview.set_xlabel('X Channel (Left Audio)', color='white')
        self.ax_preview.set_ylabel('Y Channel (Right Audio)', color='white')
        self.ax_preview.tick_params(colors='white')
        self.ax_preview.spines['bottom'].set_color('white')
        self.ax_preview.spines['top'].set_color('white')
        self.ax_preview.spines['left'].set_color('white')
        self.ax_preview.spines['right'].set_color('white')
        self.ax_preview.grid(True, alpha=0.2, color='gray')
        self.ax_preview.set_aspect('equal')

    def _setup_controls(self):
        """Setup all control widgets"""

        # Text input box
        self.ax_textbox.set_facecolor('#2a2a2a')
        self.textbox = TextBox(
            self.ax_textbox,
            'Text:',
            initial=self.current_text,
            color='#3a3a3a',
            hovercolor='#4a4a4a',
            label_pad=0.01
        )
        self.textbox.label.set_color('white')
        self.textbox.on_submit(self.on_text_change)

        # Font size slider
        self.ax_size_slider.set_facecolor('#2a2a2a')
        self.size_slider = Slider(
            self.ax_size_slider,
            'Font Size',
            0.3, 3.0,
            valinit=1.0,
            color='lime',
            track_color='#3a3a3a'
        )
        self.size_slider.label.set_color('white')
        self.size_slider.valtext.set_color('white')
        self.size_slider.on_changed(self.on_size_change)

        # Speed slider
        self.ax_speed_slider.set_facecolor('#2a2a2a')
        self.speed_slider = Slider(
            self.ax_speed_slider,
            'Speed',
            0.1, 5.0,
            valinit=1.0,
            color='cyan',
            track_color='#3a3a3a'
        )
        self.speed_slider.label.set_color('white')
        self.speed_slider.valtext.set_color('white')
        self.speed_slider.on_changed(self.on_speed_change)

        # Export button
        self.ax_export_btn.set_facecolor('#2a2a2a')
        self.export_btn = Button(
            self.ax_export_btn,
            'Export WAV',
            color='#3a3a3a',
            hovercolor='#4a4a4a'
        )
        self.export_btn.label.set_color('lime')
        self.export_btn.on_clicked(self.on_export)

        # Save button
        self.ax_save_btn.set_facecolor('#2a2a2a')
        self.save_btn = Button(
            self.ax_save_btn,
            'Save Preset',
            color='#3a3a3a',
            hovercolor='#4a4a4a'
        )
        self.save_btn.label.set_color('yellow')
        self.save_btn.on_clicked(self.on_save)

        # Load button
        self.ax_load_btn.set_facecolor('#2a2a2a')
        self.load_btn = Button(
            self.ax_load_btn,
            'Load Preset',
            color='#3a3a3a',
            hovercolor='#4a4a4a'
        )
        self.load_btn.label.set_color('orange')
        self.load_btn.on_clicked(self.on_load)

        # About button
        self.ax_about_btn.set_facecolor('#2a2a2a')
        self.about_btn = Button(
            self.ax_about_btn,
            'About',
            color='#3a3a3a',
            hovercolor='#4a4a4a'
        )
        self.about_btn.label.set_color('cyan')
        self.about_btn.on_clicked(self.on_about)

    def _setup_info(self):
        """Setup info panel"""
        self.ax_info.axis('off')
        self.ax_info.set_facecolor('#1a1a1a')
        self.info_text = self.ax_info.text(
            0.5, 0.5, '',
            ha='center', va='center',
            color='white', fontsize=10,
            family='monospace'
        )

    def update_preview(self, text):
        """Update the preview with new text"""
        try:
            # Clear previous plot
            self.ax_preview.clear()
            self._setup_preview()

            # Generate path with current settings
            x, y = self.renderer.text_to_path.text_to_path(text)

            if len(x) == 0:
                self.ax_preview.text(0, 0, 'No renderable characters',
                                    ha='center', va='center',
                                    color='red', fontsize=14)
                self.update_info("⚠️  No renderable characters in text")
                self.fig.canvas.draw_idle()
                return

            # Apply font scaling
            x = np.array(x) * self.font_scale
            y = np.array(y) * self.font_scale

            # Plot the path
            self.ax_preview.plot(x, y, 'lime', linewidth=2, alpha=0.9)

            # Mark start and end points
            self.ax_preview.plot(x[0], y[0], 'ro', markersize=8,
                               label='Start', zorder=10)
            self.ax_preview.plot(x[-1], y[-1], 'bs', markersize=8,
                               label='End', zorder=10)

            # Add title with current text
            self.ax_preview.set_title(f'Preview: "{text}"',
                                     color='white', fontsize=12, pad=10)

            # Legend
            legend = self.ax_preview.legend(
                facecolor='#2a2a2a',
                edgecolor='white',
                labelcolor='white',
                loc='upper right'
            )

            # Update info
            num_points = len(x)
            duration = num_points / self.sample_rate * self.speed_scale
            self.update_info(
                f"Points: {num_points} | "
                f"Duration: {duration:.2f}s | "
                f"Sample Rate: {self.sample_rate}Hz | "
                f"Font Scale: {self.font_scale:.2f}x | "
                f"Speed: {self.speed_scale:.2f}x"
            )

            self.fig.canvas.draw_idle()

        except Exception as e:
            self.ax_preview.text(0, 0, f'Error: {str(e)}',
                               ha='center', va='center',
                               color='red', fontsize=12)
            self.update_info(f"❌ Error: {str(e)}")
            self.fig.canvas.draw_idle()

    def update_info(self, message):
        """Update the info panel"""
        self.info_text.set_text(message)

    def on_text_change(self, text):
        """Handle text input change"""
        self.current_text = text.upper()  # Convert to uppercase
        self.update_preview(self.current_text)

    def on_size_change(self, val):
        """Handle font size slider change"""
        self.font_scale = val
        self.update_preview(self.current_text)

    def on_speed_change(self, val):
        """Handle speed slider change"""
        self.speed_scale = val
        self.update_preview(self.current_text)

    def on_export(self, event):
        """Export current text to WAV file"""
        try:
            # Generate filename with branding
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_text = "".join(c for c in self.current_text if c.isalnum())[:20]
            filename = f"output/Anthroscilloscope_{safe_text}_{timestamp}.wav"

            # Create output directory if needed
            os.makedirs('output', exist_ok=True)

            # Generate path with scaling
            x, y = self.renderer.text_to_path.text_to_path(self.current_text)
            x = np.array(x) * self.font_scale
            y = np.array(y) * self.font_scale

            # Calculate duration
            base_duration = self.renderer.path_to_audio.calculate_audio_duration(len(x))
            duration = base_duration * self.speed_scale

            # Save WAV
            self.renderer.path_to_audio.save_wav(
                x, y, filename,
                duration=duration,
                loop_count=60
            )

            # Print attribution with export
            print(f"✅ Exported WAV: {filename}")
            print(f"   Generated by {branding.get_short_attribution()}")

            self.update_info(f"✅ Exported: {filename}")

        except Exception as e:
            self.update_info(f"❌ Export failed: {str(e)}")
            print(f"❌ Export error: {e}")

    def on_save(self, event):
        """Save current settings as preset"""
        try:
            preset = {
                'text': self.current_text,
                'font_scale': self.font_scale,
                'speed_scale': self.speed_scale,
                'timestamp': datetime.now().isoformat()
            }

            # Create presets directory
            os.makedirs('presets', exist_ok=True)

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"presets/preset_{timestamp}.json"

            # Save preset
            with open(filename, 'w') as f:
                json.dump(preset, f, indent=2)

            self.update_info(f"✅ Saved preset: {filename}")
            print(f"✅ Saved preset: {filename}")

        except Exception as e:
            self.update_info(f"❌ Save failed: {str(e)}")
            print(f"❌ Save error: {e}")

    def on_load(self, event):
        """Load most recent preset"""
        try:
            presets_dir = 'presets'
            if not os.path.exists(presets_dir):
                self.update_info("⚠️  No presets directory found")
                return

            # Find most recent preset
            presets = [f for f in os.listdir(presets_dir) if f.endswith('.json')]
            if not presets:
                self.update_info("⚠️  No presets found")
                return

            latest = max(presets, key=lambda f: os.path.getmtime(
                os.path.join(presets_dir, f)))
            filepath = os.path.join(presets_dir, latest)

            # Load preset
            with open(filepath, 'r') as f:
                preset = json.load(f)

            # Apply settings
            self.current_text = preset['text']
            self.font_scale = preset['font_scale']
            self.speed_scale = preset['speed_scale']

            # Update UI controls
            self.textbox.set_val(self.current_text)
            self.size_slider.set_val(self.font_scale)
            self.speed_slider.set_val(self.speed_scale)

            # Update preview
            self.update_preview(self.current_text)

            self.update_info(f"✅ Loaded: {latest}")
            print(f"✅ Loaded preset: {filepath}")

        except Exception as e:
            self.update_info(f"❌ Load failed: {str(e)}")
            print(f"❌ Load error: {e}")

    def on_about(self, event):
        """Show about dialog"""
        # Create about dialog window
        about_fig = plt.figure(figsize=(10, 8))
        about_fig.patch.set_facecolor('#1a1a1a')
        about_ax = about_fig.add_subplot(111)
        about_ax.axis('off')
        about_ax.set_facecolor('#1a1a1a')

        # Display logo and credits
        credits_text = branding.get_credits_text()
        about_ax.text(0.5, 0.5, credits_text,
                     ha='center', va='center',
                     color='lime', fontsize=9,
                     family='monospace',
                     transform=about_ax.transAxes)

        # Add tagline
        tagline = branding.TAGLINES[4]  # "Transform text into waveforms..."
        about_ax.text(0.5, 0.05, tagline,
                     ha='center', va='bottom',
                     color='cyan', fontsize=10,
                     style='italic',
                     transform=about_ax.transAxes)

        plt.tight_layout()
        plt.show()

        self.update_info("ℹ️  About dialog displayed")

    def show(self):
        """Display the GUI"""
        plt.tight_layout()
        plt.show()


def main():
    """Launch the GUI"""
    # Show console banner
    print(branding.LOGO_COMPACT)
    print()
    print(f"  {branding.PROJECT_NAME} v{branding.VERSION}")
    print(f"  Created by {branding.AUTHOR}")
    print(f"  {branding.PROJECT_URL}")
    print()
    print("=" * 70)
    print("LISSAJOUS TEXT GENERATOR - Interactive GUI")
    print("=" * 70)
    print()
    print("Features:")
    print("  ✓ Text input field (enter text and press Enter)")
    print("  ✓ Font size slider (0.3x - 3.0x)")
    print("  ✓ Speed control (0.1x - 5.0x)")
    print("  ✓ Real-time preview")
    print("  ✓ Export to WAV")
    print("  ✓ Save/Load presets")
    print("  ✓ About dialog (click About button)")
    print()
    print(f"Available characters: A-Z, 0-9, space, . , ! ? -")
    print()
    print(f"Tagline: {branding.TAGLINES[4]}")
    print()
    print("Launching GUI...")
    print("=" * 70)
    print()

    gui = LissajousTextGUI()
    gui.show()


if __name__ == '__main__':
    main()
