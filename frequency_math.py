#!/usr/bin/env python3
"""
Frequency Mathematics and Musical Interval Analysis
Advanced mathematical calculations for frequency relationships and musical intervals
"""

import numpy as np
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass
from fractions import Fraction
import math


@dataclass
class FrequencyRatio:
    """Represents a frequency ratio with musical context"""
    numerator: int
    denominator: int
    cents: float  # Deviation in cents from equal temperament
    interval_name: str
    consonance_rating: float  # 0-1, higher is more consonant
    
    @property
    def ratio(self) -> float:
        return self.numerator / self.denominator if self.denominator != 0 else 0
    
    @property
    def simplified(self) -> Tuple[int, int]:
        """Return simplified fraction"""
        from math import gcd
        g = gcd(self.numerator, self.denominator)
        return (self.numerator // g, self.denominator // g)
    
    def to_fraction(self) -> Fraction:
        """Convert to Python Fraction object"""
        return Fraction(self.numerator, self.denominator)


class MusicalIntervals:
    """Musical interval calculations and relationships"""
    
    # Standard musical intervals (just intonation)
    INTERVALS = {
        'Unison': (1, 1),
        'Minor Second': (16, 15),
        'Major Second': (9, 8),
        'Minor Third': (6, 5),
        'Major Third': (5, 4),
        'Perfect Fourth': (4, 3),
        'Tritone': (45, 32),
        'Perfect Fifth': (3, 2),
        'Minor Sixth': (8, 5),
        'Major Sixth': (5, 3),
        'Minor Seventh': (16, 9),
        'Major Seventh': (15, 8),
        'Octave': (2, 1),
        'Perfect Twelfth': (3, 1),
        'Two Octaves': (4, 1),
    }
    
    # Harmonic series ratios
    HARMONICS = {
        1: (1, 1),   # Fundamental
        2: (2, 1),   # Octave
        3: (3, 1),   # Octave + Fifth
        4: (4, 1),   # Two octaves
        5: (5, 1),   # Two octaves + Major third
        6: (6, 1),   # Two octaves + Fifth
        7: (7, 1),   # Two octaves + Minor seventh
        8: (8, 1),   # Three octaves
        9: (9, 1),   # Three octaves + Major second
        10: (10, 1), # Three octaves + Major third
        11: (11, 1), # Three octaves + Tritone
        12: (12, 1), # Three octaves + Fifth
        13: (13, 1), # Three octaves + Minor sixth
        14: (14, 1), # Three octaves + Minor seventh
        15: (15, 1), # Three octaves + Major seventh
        16: (16, 1), # Four octaves
    }
    
    @staticmethod
    def frequency_to_cents(freq1: float, freq2: float) -> float:
        """Calculate cent difference between two frequencies"""
        if freq2 == 0:
            return 0
        return 1200 * np.log2(freq1 / freq2)
    
    @staticmethod
    def cents_to_ratio(cents: float) -> float:
        """Convert cents to frequency ratio"""
        return 2 ** (cents / 1200)
    
    @staticmethod
    def find_closest_interval(ratio: float, tolerance: float = 50) -> Optional[FrequencyRatio]:
        """Find closest musical interval to given ratio"""
        min_diff = float('inf')
        closest = None
        
        for name, (num, den) in MusicalIntervals.INTERVALS.items():
            interval_ratio = num / den
            cents_diff = abs(MusicalIntervals.frequency_to_cents(ratio, interval_ratio))
            
            if cents_diff < min_diff and cents_diff < tolerance:
                min_diff = cents_diff
                consonance = MusicalIntervals.calculate_consonance(num, den)
                closest = FrequencyRatio(
                    numerator=num,
                    denominator=den,
                    cents=min_diff if ratio > interval_ratio else -min_diff,
                    interval_name=name,
                    consonance_rating=consonance
                )
        
        return closest
    
    @staticmethod
    def calculate_consonance(num: int, den: int) -> float:
        """Calculate consonance rating using various methods"""
        # Euler's gradus suavitatis (simplified)
        euler = 1.0 / (num + den)
        
        # Tenney height (log of product)
        tenney = 1.0 / np.log2(num * den + 1)
        
        # Harmonic complexity
        complexity = 1.0 / max(num, den)
        
        # Combine metrics
        consonance = (euler + tenney + complexity) / 3
        
        # Special cases for perfect intervals
        ratio = num / den
        if ratio == 1.0:  # Unison
            consonance = 1.0
        elif ratio == 2.0:  # Octave
            consonance = 0.95
        elif ratio == 1.5:  # Perfect fifth
            consonance = 0.9
        elif ratio == 4/3:  # Perfect fourth
            consonance = 0.85
        
        return min(1.0, consonance)


class FrequencyAnalyzer:
    """Advanced frequency analysis tools"""
    
    @staticmethod
    def find_fundamental(frequencies: List[float], tolerance: float = 0.01) -> float:
        """Find fundamental frequency from list of partials"""
        if not frequencies:
            return 0
        
        # Sort frequencies
        freqs = sorted(frequencies)
        
        # Try different fundamental candidates
        candidates = []
        
        for i in range(len(freqs)):
            fundamental = freqs[i]
            score = 0
            
            # Check if other frequencies are harmonics
            for freq in freqs:
                ratio = freq / fundamental
                nearest_int = round(ratio)
                if abs(ratio - nearest_int) < tolerance:
                    score += 1 / nearest_int  # Weight lower harmonics more
            
            candidates.append((fundamental, score))
        
        # Return candidate with highest score
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        return freqs[0]
    
    @staticmethod
    def decompose_complex_ratio(ratio: float, max_terms: int = 10) -> List[Tuple[int, int]]:
        """Decompose complex ratio into simpler frequency relationships"""
        # Use continued fractions
        continued_fraction = []
        x = ratio
        
        for _ in range(max_terms):
            if x == 0:
                break
            
            integer_part = int(x)
            continued_fraction.append(integer_part)
            
            fractional_part = x - integer_part
            if abs(fractional_part) < 1e-10:
                break
            
            x = 1 / fractional_part
        
        # Convert back to fractions
        convergents = []
        for i in range(len(continued_fraction)):
            cf_slice = continued_fraction[:i+1]
            frac = Fraction(cf_slice[-1])
            
            for j in range(len(cf_slice) - 2, -1, -1):
                frac = cf_slice[j] + 1 / frac
            
            convergents.append((frac.numerator, frac.denominator))
        
        return convergents
    
    @staticmethod
    def calculate_beating_frequency(freq1: float, freq2: float) -> float:
        """Calculate beating frequency between two frequencies"""
        return abs(freq1 - freq2)
    
    @staticmethod
    def temperament_comparison(frequency: float, base_freq: float = 440.0) -> Dict[str, float]:
        """Compare frequency in different temperament systems"""
        
        # Calculate note number (semitones from A4)
        semitones = 12 * np.log2(frequency / base_freq)
        
        results = {}
        
        # Equal temperament
        results['equal_temperament'] = frequency
        
        # Just intonation (assuming C as root)
        # This is simplified - actual just intonation depends on key
        note_in_octave = int(round(semitones)) % 12
        just_ratios = [1, 16/15, 9/8, 6/5, 5/4, 4/3, 45/32, 3/2, 8/5, 5/3, 16/9, 15/8]
        octave_multiplier = 2 ** (int(semitones / 12))
        results['just_intonation'] = base_freq * just_ratios[note_in_octave] * octave_multiplier
        
        # Pythagorean tuning
        fifth_power = (note_in_octave * 7) % 12
        pythagorean = base_freq * (3/2) ** fifth_power * 2 ** (-int(fifth_power * 7 / 12))
        results['pythagorean'] = pythagorean * octave_multiplier
        
        # Well temperament (simplified Werckmeister III)
        # This is a simplification
        results['well_tempered'] = frequency * 0.998  # Slight adjustment
        
        return results


class LissajousFrequencyMath:
    """Mathematical analysis specific to Lissajous patterns"""
    
    @staticmethod
    def pattern_period(freq_x: float, freq_y: float) -> float:
        """Calculate the period of a Lissajous pattern"""
        if freq_x == 0 or freq_y == 0:
            return 0
        
        # Find LCM of frequencies (as rational approximation)
        from fractions import Fraction
        
        # Convert to fractions
        frac_x = Fraction(freq_x).limit_denominator(1000)
        frac_y = Fraction(freq_y).limit_denominator(1000)
        
        # LCM of numerators, GCD of denominators
        from math import gcd
        
        lcm_num = (frac_x.numerator * frac_y.numerator) // gcd(frac_x.numerator, frac_y.numerator)
        gcd_den = gcd(frac_x.denominator, frac_y.denominator)
        
        period_x = lcm_num / (frac_x.numerator * gcd_den)
        period_y = lcm_num / (frac_y.numerator * gcd_den)
        
        return max(period_x, period_y)
    
    @staticmethod
    def crossing_points(ratio_x: int, ratio_y: int, phase: float = 0) -> int:
        """Calculate number of crossing points in a Lissajous figure"""
        from math import gcd
        
        g = gcd(ratio_x, ratio_y)
        
        # Basic formula for crossings
        if phase == 0:
            crossings = 2 * ratio_x * ratio_y // g
        else:
            # Phase affects crossing count
            crossings = 2 * ratio_x * ratio_y // g
            
            # Adjust for phase (simplified)
            if abs(phase - np.pi/2) < 0.1:
                crossings = ratio_x * ratio_y
        
        return crossings
    
    @staticmethod
    def pattern_complexity(ratio_x: int, ratio_y: int) -> float:
        """Calculate complexity metric for Lissajous pattern"""
        from math import gcd
        
        g = gcd(ratio_x, ratio_y)
        
        # Normalize ratios
        norm_x = ratio_x // g
        norm_y = ratio_y // g
        
        # Complexity based on normalized sum and product
        complexity = np.log2(norm_x + norm_y) * np.log2(norm_x * norm_y)
        
        return complexity
    
    @staticmethod
    def find_generator_frequencies(target_freq: float, 
                                  ratio_x: int, ratio_y: int) -> Tuple[float, float]:
        """Find X and Y frequencies to generate pattern at target frequency"""
        from math import gcd
        
        g = gcd(ratio_x, ratio_y)
        
        # The pattern repeats at the LCM of the periods
        # Target frequency is the pattern repetition rate
        freq_x = target_freq * ratio_x / g
        freq_y = target_freq * ratio_y / g
        
        return freq_x, freq_y
    
    @staticmethod
    def phase_from_ellipse(a: float, b: float) -> float:
        """Calculate phase difference from ellipse parameters"""
        # For an ellipse with semi-major axis a and semi-minor axis b
        # tan(2θ) = 2ab/(a² - b²) where θ is the tilt angle
        
        if a == b:
            # Circle - phase is π/2
            return np.pi / 2
        
        theta = 0.5 * np.arctan(2 * a * b / (a**2 - b**2))
        
        # Convert tilt to phase
        phase = 2 * theta
        
        return phase
    
    @staticmethod
    def stability_analysis(freq_x: float, freq_y: float, 
                         tolerance: float = 0.001) -> Dict[str, any]:
        """Analyze pattern stability under frequency variations"""
        
        ratio = freq_x / freq_y
        
        # Find closest rational approximation
        frac = Fraction(ratio).limit_denominator(100)
        
        # Calculate detuning sensitivity
        delta_ratio = abs(ratio - float(frac))
        
        # Pattern will drift if frequencies aren't locked
        drift_rate = abs(freq_x - freq_y * float(frac))
        
        # Locking range (simplified)
        lock_range = min(freq_x, freq_y) * 0.01  # 1% typical for PLL
        
        is_stable = drift_rate < lock_range
        
        return {
            'ratio': ratio,
            'closest_rational': (frac.numerator, frac.denominator),
            'detuning': delta_ratio,
            'drift_rate_hz': drift_rate,
            'lock_range_hz': lock_range,
            'is_stable': is_stable,
            'pattern_period': LissajousFrequencyMath.pattern_period(freq_x, freq_y)
        }


class FrequencyGenerator:
    """Generate frequency sets for interesting Lissajous patterns"""
    
    @staticmethod
    def harmonic_series(fundamental: float, n_harmonics: int = 8) -> List[float]:
        """Generate harmonic series"""
        return [fundamental * i for i in range(1, n_harmonics + 1)]
    
    @staticmethod
    def subharmonic_series(fundamental: float, n_subharmonics: int = 8) -> List[float]:
        """Generate subharmonic series"""
        return [fundamental / i for i in range(1, n_subharmonics + 1)]
    
    @staticmethod
    def fibonacci_frequencies(base_freq: float, n_terms: int = 8) -> List[float]:
        """Generate frequencies based on Fibonacci ratios"""
        fib = [1, 1]
        for _ in range(n_terms - 2):
            fib.append(fib[-1] + fib[-2])
        
        return [base_freq * f for f in fib]
    
    @staticmethod
    def golden_ratio_frequencies(base_freq: float, n_terms: int = 5) -> List[float]:
        """Generate frequencies based on golden ratio"""
        phi = (1 + np.sqrt(5)) / 2
        return [base_freq * (phi ** i) for i in range(n_terms)]
    
    @staticmethod
    def musical_scale_frequencies(root_freq: float, scale_type: str = 'major') -> List[float]:
        """Generate frequencies for musical scales"""
        
        scales = {
            'major': [1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8, 2],
            'minor': [1, 9/8, 6/5, 4/3, 3/2, 8/5, 9/5, 2],
            'pentatonic': [1, 9/8, 5/4, 3/2, 5/3, 2],
            'blues': [1, 6/5, 4/3, 45/32, 3/2, 9/5, 2],
            'chromatic': [1, 16/15, 9/8, 6/5, 5/4, 4/3, 45/32, 3/2, 8/5, 5/3, 16/9, 15/8, 2]
        }
        
        if scale_type not in scales:
            scale_type = 'major'
        
        return [root_freq * ratio for ratio in scales[scale_type]]
    
    @staticmethod
    def prime_frequencies(base_freq: float, n_primes: int = 8) -> List[float]:
        """Generate frequencies based on prime numbers"""
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(np.sqrt(n)) + 1):
                if n % i == 0:
                    return False
            return True
        
        primes = []
        n = 2
        while len(primes) < n_primes:
            if is_prime(n):
                primes.append(n)
            n += 1
        
        return [base_freq * p for p in primes]


def demonstrate_frequency_math():
    """Demonstration of frequency mathematics"""
    
    print("🎵 FREQUENCY MATHEMATICS DEMONSTRATION")
    print("="*50)
    
    # Musical interval analysis
    print("\n1. Musical Interval Analysis:")
    test_ratio = 1.498  # Close to perfect fifth
    interval = MusicalIntervals.find_closest_interval(test_ratio)
    if interval:
        print(f"   Ratio {test_ratio:.3f} → {interval.interval_name}")
        print(f"   Exact ratio: {interval.numerator}:{interval.denominator}")
        print(f"   Cents deviation: {interval.cents:.1f}")
        print(f"   Consonance: {interval.consonance_rating:.2f}")
    
    # Lissajous period calculation
    print("\n2. Lissajous Pattern Period:")
    freq_x, freq_y = 440, 660  # A4 and E5
    period = LissajousFrequencyMath.pattern_period(freq_x, freq_y)
    print(f"   Frequencies: {freq_x}Hz, {freq_y}Hz")
    print(f"   Pattern period: {period:.4f} seconds")
    print(f"   Crossing points: {LissajousFrequencyMath.crossing_points(2, 3)}")
    
    # Stability analysis
    print("\n3. Pattern Stability:")
    stability = LissajousFrequencyMath.stability_analysis(440.0, 659.8)
    print(f"   Frequency ratio: {stability['ratio']:.4f}")
    print(f"   Closest rational: {stability['closest_rational']}")
    print(f"   Drift rate: {stability['drift_rate_hz']:.2f} Hz")
    print(f"   Stable: {stability['is_stable']}")
    
    # Harmonic generation
    print("\n4. Harmonic Series (220Hz fundamental):")
    harmonics = FrequencyGenerator.harmonic_series(220, 5)
    for i, freq in enumerate(harmonics, 1):
        interval = MusicalIntervals.find_closest_interval(freq/220)
        if interval:
            print(f"   H{i}: {freq:.0f}Hz - {interval.interval_name}")
    
    # Musical scale
    print("\n5. C Major Scale (261.63Hz = C4):")
    scale = FrequencyGenerator.musical_scale_frequencies(261.63, 'major')
    notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']
    for note, freq in zip(notes, scale):
        print(f"   {note}: {freq:.1f}Hz")


if __name__ == "__main__":
    demonstrate_frequency_math()