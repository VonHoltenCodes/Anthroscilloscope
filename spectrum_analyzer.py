#!/usr/bin/env python3
"""
FFT Spectrum Analyzer Module for Anthroscilloscope
Provides frequency domain analysis of oscilloscope waveforms
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import fft, fftfreq, rfft, rfftfreq
import warnings
warnings.filterwarnings('ignore', category=UserWarning)


class SpectrumAnalyzer:
    """FFT-based spectrum analyzer for oscilloscope data"""
    
    def __init__(self):
        self.window_functions = {
            'hann': np.hanning,
            'hamming': np.hamming,
            'blackman': np.blackman,
            'bartlett': np.bartlett,
            'flattop': signal.windows.flattop,
            'kaiser': lambda N: np.kaiser(N, 5),
            'tukey': lambda N: signal.windows.tukey(N, 0.5),
            'none': np.ones
        }
    
    def compute_fft(self, time_data, voltage_data, window='hann', 
                    remove_dc=True, zero_pad=True):
        """
        Compute FFT of waveform data
        
        Args:
            time_data: Time axis data (numpy array)
            voltage_data: Voltage data (numpy array)
            window: Window function name
            remove_dc: Remove DC component
            zero_pad: Zero-pad to next power of 2 for faster FFT
        
        Returns:
            tuple: (frequencies, magnitudes, phases)
        """
        # Calculate sample rate
        dt = time_data[1] - time_data[0]
        sample_rate = 1.0 / dt
        n_samples = len(voltage_data)
        
        # Remove DC component if requested
        if remove_dc:
            voltage_data = voltage_data - np.mean(voltage_data)
        
        # Apply window function
        if window in self.window_functions:
            window_func = self.window_functions[window](n_samples)
            windowed_data = voltage_data * window_func
            
            # Window compensation factor
            window_correction = np.sum(window_func) / n_samples
        else:
            windowed_data = voltage_data
            window_correction = 1.0
        
        # Zero padding for better frequency resolution
        if zero_pad:
            # Next power of 2
            n_fft = 2 ** int(np.ceil(np.log2(n_samples)))
            if n_fft < 2 * n_samples:
                n_fft = 2 * n_fft
        else:
            n_fft = n_samples
        
        # Compute FFT (use rfft for real signals - more efficient)
        fft_values = rfft(windowed_data, n=n_fft)
        frequencies = rfftfreq(n_fft, dt)
        
        # Compute magnitude and phase
        magnitudes = np.abs(fft_values) / (n_samples * window_correction)
        magnitudes[1:] *= 2  # Double non-DC components (single-sided spectrum)
        
        phases = np.angle(fft_values, deg=True)
        
        return frequencies, magnitudes, phases, sample_rate
    
    def compute_power_spectrum(self, time_data, voltage_data, window='hann',
                              scaling='density', nperseg=None):
        """
        Compute power spectral density or power spectrum
        
        Args:
            time_data: Time axis data
            voltage_data: Voltage data
            window: Window function
            scaling: 'density' for PSD (V²/Hz) or 'spectrum' for power spectrum (V²)
            nperseg: Segment length for Welch's method (None for full length)
        
        Returns:
            tuple: (frequencies, power)
        """
        dt = time_data[1] - time_data[0]
        sample_rate = 1.0 / dt
        
        if nperseg is None:
            nperseg = min(256, len(voltage_data))
        
        # Use Welch's method for better noise reduction
        frequencies, power = signal.welch(
            voltage_data,
            fs=sample_rate,
            window=window,
            nperseg=nperseg,
            scaling=scaling,
            detrend='constant'
        )
        
        return frequencies, power, sample_rate
    
    def find_peaks(self, frequencies, magnitudes, num_peaks=10, 
                   min_height=None, min_distance_hz=None):
        """
        Find dominant frequency peaks
        
        Args:
            frequencies: Frequency array
            magnitudes: Magnitude array
            num_peaks: Maximum number of peaks to find
            min_height: Minimum peak height (None for auto)
            min_distance_hz: Minimum distance between peaks in Hz
        
        Returns:
            dict: Peak frequencies, magnitudes, and indices
        """
        # Convert to dB for better peak detection
        magnitudes_db = 20 * np.log10(magnitudes + 1e-12)
        
        # Auto threshold if not specified
        if min_height is None:
            noise_floor = np.median(magnitudes_db)
            min_height = noise_floor + 10  # 10 dB above noise floor
        
        # Convert Hz distance to samples
        if min_distance_hz is not None:
            df = frequencies[1] - frequencies[0]
            min_distance = int(min_distance_hz / df)
        else:
            min_distance = 1
        
        # Find peaks
        peaks, properties = signal.find_peaks(
            magnitudes_db,
            height=min_height,
            distance=min_distance,
            prominence=3  # At least 3 dB prominence
        )
        
        # Sort by magnitude
        sorted_indices = np.argsort(magnitudes[peaks])[::-1]
        peaks = peaks[sorted_indices][:num_peaks]
        
        # Extract peak information
        peak_freqs = frequencies[peaks]
        peak_mags = magnitudes[peaks]
        peak_mags_db = magnitudes_db[peaks]
        
        return {
            'frequencies': peak_freqs,
            'magnitudes': peak_mags,
            'magnitudes_db': peak_mags_db,
            'indices': peaks
        }
    
    def compute_thd(self, frequencies, magnitudes, fundamental_freq=None,
                    num_harmonics=5):
        """
        Compute Total Harmonic Distortion (THD)
        
        Args:
            frequencies: Frequency array
            magnitudes: Magnitude array
            fundamental_freq: Fundamental frequency (None to auto-detect)
            num_harmonics: Number of harmonics to include
        
        Returns:
            dict: THD percentage and harmonic information
        """
        # Find fundamental if not specified
        if fundamental_freq is None:
            peaks = self.find_peaks(frequencies, magnitudes, num_peaks=1)
            if len(peaks['frequencies']) > 0:
                fundamental_freq = peaks['frequencies'][0]
                fundamental_mag = peaks['magnitudes'][0]
            else:
                return {'thd': 0, 'fundamental': 0, 'harmonics': []}
        else:
            # Find magnitude at fundamental
            idx = np.argmin(np.abs(frequencies - fundamental_freq))
            fundamental_mag = magnitudes[idx]
        
        # Find harmonics
        harmonics = []
        harmonic_sum = 0
        
        for n in range(2, num_harmonics + 2):
            harmonic_freq = n * fundamental_freq
            
            # Find closest frequency bin
            if harmonic_freq < frequencies[-1]:
                idx = np.argmin(np.abs(frequencies - harmonic_freq))
                harmonic_mag = magnitudes[idx]
                harmonics.append({
                    'n': n,
                    'frequency': frequencies[idx],
                    'magnitude': harmonic_mag,
                    'magnitude_db': 20 * np.log10(harmonic_mag / fundamental_mag + 1e-12)
                })
                harmonic_sum += harmonic_mag ** 2
        
        # Calculate THD
        thd = 100 * np.sqrt(harmonic_sum) / fundamental_mag if fundamental_mag > 0 else 0
        
        return {
            'thd': thd,
            'fundamental': fundamental_freq,
            'fundamental_magnitude': fundamental_mag,
            'harmonics': harmonics
        }
    
    def compute_snr(self, frequencies, magnitudes, signal_freq, 
                    signal_bandwidth=None):
        """
        Compute Signal-to-Noise Ratio (SNR)
        
        Args:
            frequencies: Frequency array
            magnitudes: Magnitude array
            signal_freq: Signal frequency
            signal_bandwidth: Bandwidth around signal (None for auto)
        
        Returns:
            dict: SNR in dB and related metrics
        """
        # Find signal peak
        if signal_bandwidth is None:
            # Estimate bandwidth as 5% of signal frequency
            signal_bandwidth = signal_freq * 0.05
        
        # Find signal power
        signal_mask = (frequencies >= signal_freq - signal_bandwidth/2) & \
                     (frequencies <= signal_freq + signal_bandwidth/2)
        signal_power = np.sum(magnitudes[signal_mask] ** 2)
        
        # Find noise power (everything except signal)
        noise_mask = ~signal_mask
        noise_power = np.sum(magnitudes[noise_mask] ** 2)
        
        # Calculate SNR
        if noise_power > 0:
            snr_db = 10 * np.log10(signal_power / noise_power)
        else:
            snr_db = float('inf')
        
        return {
            'snr_db': snr_db,
            'signal_power': signal_power,
            'noise_power': noise_power,
            'signal_frequency': signal_freq,
            'signal_bandwidth': signal_bandwidth
        }
    
    def plot_spectrum(self, frequencies, magnitudes, peaks=None, 
                     title="Frequency Spectrum", log_scale=True,
                     max_freq=None):
        """
        Plot frequency spectrum
        
        Args:
            frequencies: Frequency array
            magnitudes: Magnitude array
            peaks: Peak information dictionary (optional)
            title: Plot title
            log_scale: Use logarithmic magnitude scale
            max_freq: Maximum frequency to display
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Limit frequency range
        if max_freq is not None:
            mask = frequencies <= max_freq
            frequencies = frequencies[mask]
            magnitudes = magnitudes[mask]
        
        # Magnitude plot
        if log_scale:
            magnitudes_plot = 20 * np.log10(magnitudes + 1e-12)
            ylabel = 'Magnitude (dB)'
        else:
            magnitudes_plot = magnitudes
            ylabel = 'Magnitude (V)'
        
        ax1.plot(frequencies / 1000, magnitudes_plot, 'b-', linewidth=0.5)
        
        # Mark peaks if provided
        if peaks is not None:
            if log_scale:
                peak_mags = peaks['magnitudes_db']
            else:
                peak_mags = peaks['magnitudes']
            
            ax1.plot(peaks['frequencies'] / 1000, peak_mags, 'ro', markersize=8)
            
            # Annotate peaks
            for freq, mag in zip(peaks['frequencies'][:5], peak_mags[:5]):
                ax1.annotate(f'{freq:.1f} Hz',
                           xy=(freq/1000, mag),
                           xytext=(5, 5),
                           textcoords='offset points',
                           fontsize=8)
        
        ax1.set_xlabel('Frequency (kHz)')
        ax1.set_ylabel(ylabel)
        ax1.set_title(title)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([0, frequencies[-1]/1000])
        
        # Phase plot (for lower frequencies)
        # Recompute for phase display
        phases = np.angle(np.fft.rfft(magnitudes), deg=True)
        freq_phase = frequencies[:len(phases)]
        
        # Only show phase for lower frequencies where it's meaningful
        max_phase_freq = min(10000, frequencies[-1] / 4)
        phase_mask = freq_phase <= max_phase_freq
        
        ax2.plot(freq_phase[phase_mask] / 1000, phases[phase_mask], 'g-', linewidth=0.5)
        ax2.set_xlabel('Frequency (kHz)')
        ax2.set_ylabel('Phase (degrees)')
        ax2.set_title('Phase Spectrum')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([0, max_phase_freq/1000])
        ax2.set_ylim([-180, 180])
        
        plt.tight_layout()
        return fig
    
    def plot_spectrogram(self, time_data, voltage_data, nperseg=256,
                         noverlap=None, cmap='viridis'):
        """
        Plot spectrogram (time-frequency representation)
        
        Args:
            time_data: Time axis data
            voltage_data: Voltage data
            nperseg: Segment length for STFT
            noverlap: Overlap between segments
            cmap: Colormap for display
        """
        dt = time_data[1] - time_data[0]
        sample_rate = 1.0 / dt
        
        if noverlap is None:
            noverlap = nperseg // 2
        
        # Compute spectrogram
        frequencies, times, Sxx = signal.spectrogram(
            voltage_data,
            fs=sample_rate,
            nperseg=nperseg,
            noverlap=noverlap,
            window='hann',
            scaling='density'
        )
        
        # Plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Convert to dB
        Sxx_db = 10 * np.log10(Sxx + 1e-12)
        
        # Plot spectrogram
        im = ax.pcolormesh(times, frequencies/1000, Sxx_db,
                          shading='gouraud', cmap=cmap)
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frequency (kHz)')
        ax.set_title('Spectrogram')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Power Spectral Density (dB/Hz)')
        
        # Limit frequency range for better visibility
        max_freq = min(sample_rate / 2, 100000)
        ax.set_ylim([0, max_freq/1000])
        
        plt.tight_layout()
        return fig


def analyze_waveform(time_data, voltage_data, plot=True):
    """
    Complete frequency analysis of waveform
    
    Args:
        time_data: Time axis data
        voltage_data: Voltage data
        plot: Whether to generate plots
    
    Returns:
        dict: Analysis results
    """
    analyzer = SpectrumAnalyzer()
    
    print("\n" + "="*60)
    print("FREQUENCY DOMAIN ANALYSIS")
    print("="*60)
    
    # Compute FFT
    frequencies, magnitudes, phases, sample_rate = analyzer.compute_fft(
        time_data, voltage_data, window='hann'
    )
    
    print(f"\nSample Rate: {sample_rate/1e6:.2f} MSa/s")
    print(f"Frequency Resolution: {frequencies[1]:.2f} Hz")
    print(f"Maximum Frequency: {frequencies[-1]/1000:.2f} kHz")
    
    # Find peaks
    peaks = analyzer.find_peaks(frequencies, magnitudes, num_peaks=10)
    
    print("\nDominant Frequencies:")
    for i, (freq, mag) in enumerate(zip(peaks['frequencies'][:5], 
                                        peaks['magnitudes'][:5]), 1):
        print(f"  {i}. {freq:.1f} Hz ({mag*1000:.3f} mV)")
    
    # Compute THD if there's a clear fundamental
    if len(peaks['frequencies']) > 0:
        thd_result = analyzer.compute_thd(frequencies, magnitudes)
        if thd_result['thd'] > 0:
            print(f"\nTotal Harmonic Distortion: {thd_result['thd']:.2f}%")
            print(f"Fundamental: {thd_result['fundamental']:.1f} Hz")
    
    # Compute SNR for strongest signal
    if len(peaks['frequencies']) > 0:
        snr_result = analyzer.compute_snr(frequencies, magnitudes, 
                                         peaks['frequencies'][0])
        print(f"\nSignal-to-Noise Ratio: {snr_result['snr_db']:.1f} dB")
    
    # Plot if requested
    if plot:
        # Spectrum plot
        fig1 = analyzer.plot_spectrum(frequencies, magnitudes, peaks=peaks,
                                     max_freq=sample_rate/4)
        
        # Spectrogram
        if len(time_data) > 1024:
            fig2 = analyzer.plot_spectrogram(time_data, voltage_data)
        
        plt.show()
    
    return {
        'frequencies': frequencies,
        'magnitudes': magnitudes,
        'phases': phases,
        'sample_rate': sample_rate,
        'peaks': peaks,
        'thd': thd_result if 'thd_result' in locals() else None,
        'snr': snr_result if 'snr_result' in locals() else None
    }


if __name__ == "__main__":
    # Example with test signal
    import numpy as np
    
    # Generate test signal: 1 kHz sine with harmonics and noise
    fs = 100000  # 100 kHz sample rate
    t = np.linspace(0, 1, fs)
    
    # Fundamental + harmonics + noise
    signal_clean = (np.sin(2*np.pi*1000*t) +           # 1 kHz fundamental
                   0.3*np.sin(2*np.pi*2000*t) +       # 2nd harmonic
                   0.1*np.sin(2*np.pi*3000*t))        # 3rd harmonic
    
    signal_noise = signal_clean + 0.05*np.random.randn(len(t))
    
    # Analyze
    results = analyze_waveform(t, signal_noise, plot=True)