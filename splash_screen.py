#!/usr/bin/env python3
"""
Splash screen for Anthroscilloscope GUI
Shows logo and loading message
"""

import matplotlib.pyplot as plt
import branding
import time


def show_splash(duration=2.0):
    """
    Display splash screen with logo

    Args:
        duration: How long to show splash in seconds
    """
    # Create splash window
    fig = plt.figure(figsize=(10, 8))
    fig.patch.set_facecolor('#0a0a0a')
    ax = fig.add_subplot(111)
    ax.axis('off')
    ax.set_facecolor('#0a0a0a')

    # Display compact logo
    ax.text(0.5, 0.7, branding.LOGO_COMPACT,
           ha='center', va='center',
           color='lime', fontsize=12,
           family='monospace',
           transform=ax.transAxes)

    # Version and title
    ax.text(0.5, 0.5, f'Lissajous Text Generator\nVersion {branding.VERSION}',
           ha='center', va='center',
           color='white', fontsize=14,
           transform=ax.transAxes)

    # Author
    ax.text(0.5, 0.35, f'Created by {branding.AUTHOR}',
           ha='center', va='center',
           color='cyan', fontsize=11,
           transform=ax.transAxes)

    # Loading message
    ax.text(0.5, 0.2, 'Loading GUI...',
           ha='center', va='center',
           color='gray', fontsize=10,
           style='italic',
           transform=ax.transAxes)

    # Tagline at bottom
    tagline = branding.TAGLINES[4]
    ax.text(0.5, 0.05, tagline,
           ha='center', va='bottom',
           color='gray', fontsize=9,
           alpha=0.7,
           style='italic',
           transform=ax.transAxes)

    # GitHub link
    ax.text(0.5, 0.01, branding.PROJECT_URL,
           ha='center', va='bottom',
           color='gray', fontsize=8,
           alpha=0.5,
           family='monospace',
           transform=ax.transAxes)

    plt.tight_layout()

    # Show non-blocking
    plt.ion()
    plt.show()
    plt.pause(duration)
    plt.close(fig)


def show_console_banner():
    """Print ASCII banner to console"""
    print(branding.LOGO_COMPACT)
    print()
    print(f"  Version: {branding.VERSION}")
    print(f"  Author:  {branding.AUTHOR}")
    print(f"  GitHub:  {branding.PROJECT_URL}")
    print()
    print("  " + branding.TAGLINES[4])
    print()
    print("=" * 70)


if __name__ == '__main__':
    show_console_banner()
    print("Showing splash screen...")
    show_splash(3.0)
    print("Splash screen closed.")
