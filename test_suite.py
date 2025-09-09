#!/usr/bin/env python3
"""
Comprehensive Test Suite for Anthroscilloscope
Tests all modules and functionality
"""

import sys
import time
import numpy as np
import pyvisa
from datetime import datetime


class AnthroscilloscopeTestSuite:
    """Test suite for all Anthroscilloscope features"""
    
    def __init__(self, ip_address="192.168.68.73"):
        self.ip_address = ip_address
        self.rm = None
        self.scope = None
        self.test_results = []
        self.tests_passed = 0
        self.tests_failed = 0
    
    def setup(self):
        """Setup test environment"""
        try:
            self.rm = pyvisa.ResourceManager('@py')
            self.scope = self.rm.open_resource(f'TCPIP::{self.ip_address}::INSTR')
            self.scope.timeout = 5000
            return True
        except Exception as e:
            print(f"Setup failed: {e}")
            return False
    
    def teardown(self):
        """Cleanup test environment"""
        if self.scope:
            self.scope.close()
        if self.rm:
            self.rm.close()
    
    def run_test(self, test_name, test_func):
        """Run a single test and record results"""
        print(f"\n🧪 Testing: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            if result:
                print(f"✅ PASS: {test_name}")
                self.tests_passed += 1
                self.test_results.append((test_name, "PASS", None))
            else:
                print(f"❌ FAIL: {test_name}")
                self.tests_failed += 1
                self.test_results.append((test_name, "FAIL", "Test returned False"))
        except Exception as e:
            print(f"❌ ERROR: {test_name} - {e}")
            self.tests_failed += 1
            self.test_results.append((test_name, "ERROR", str(e)))
    
    def test_connection(self):
        """Test basic connection"""
        idn = self.scope.query('*IDN?').strip()
        print(f"Connected to: {idn}")
        return 'RIGOL' in idn.upper()
    
    def test_waveform_capture(self):
        """Test waveform data capture"""
        from rigol_oscilloscope_control import RigolDS1104Z
        
        scope_ctrl = RigolDS1104Z(self.ip_address)
        if not scope_ctrl.connect():
            return False
        
        time_data, voltage_data = scope_ctrl.get_waveform_data(channel=1)
        scope_ctrl.close()
        
        if time_data is not None and voltage_data is not None:
            print(f"Captured {len(voltage_data)} points")
            return len(voltage_data) > 0
        return False
    
    def test_screenshot_capture(self):
        """Test screenshot capture"""
        from rigol_oscilloscope_control import RigolDS1104Z
        
        scope_ctrl = RigolDS1104Z(self.ip_address)
        if not scope_ctrl.connect():
            return False
        
        filename = f"test_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        result = scope_ctrl.save_screenshot(filename)
        scope_ctrl.close()
        
        if result:
            import os
            exists = os.path.exists(filename)
            if exists:
                os.remove(filename)  # Clean up test file
                print(f"Screenshot saved and verified")
            return exists
        return False
    
    def test_measurements(self):
        """Test measurement functions"""
        from rigol_oscilloscope_control import RigolDS1104Z
        
        scope_ctrl = RigolDS1104Z(self.ip_address)
        if not scope_ctrl.connect():
            return False
        
        vpp = scope_ctrl.get_measurement(1, 'VPP')
        scope_ctrl.close()
        
        if vpp is not None:
            print(f"Vpp measurement: {vpp:.3f}V")
            return True
        return False
    
    def test_device_discovery(self):
        """Test device discovery"""
        from device_discovery import RigolDiscovery
        
        discovery = RigolDiscovery()
        device = discovery.quick_discover([self.ip_address])
        
        if device:
            print(f"Device discovered: {device['ip']}")
            return True
        return False
    
    def test_trigger_control(self):
        """Test trigger control"""
        from trigger_control import TriggerControl
        
        trigger = TriggerControl(self.scope)
        
        # Test edge trigger setup
        result = trigger.setup_edge_trigger(
            source='CHANnel1',
            level=0.0,
            slope='POSitive'
        )
        
        if result:
            # Verify settings
            info = trigger.get_trigger_info()
            print(f"Trigger mode: {info.get('mode', 'Unknown')}")
            return info.get('mode') == 'EDGE'
        return False
    
    def test_acquisition_control(self):
        """Test acquisition control"""
        from acquisition_control import AcquisitionControl
        
        acq = AcquisitionControl(self.scope)
        
        # Test setting acquisition type
        result = acq.set_acquisition_type('NORM')
        
        if result:
            # Verify settings
            info = acq.get_acquisition_info()
            print(f"Acquisition type: {info.get('type', 'Unknown')}")
            return info.get('type') == 'NORM'
        return False
    
    def test_long_memory_capture(self):
        """Test long memory capture"""
        from long_memory_capture import LongMemoryCapture
        
        capture = LongMemoryCapture(self.ip_address)
        if not capture.connect():
            return False
        
        # Set to smallest memory depth for quick test
        capture.set_memory_depth('12k')
        
        # Capture data
        time_data, voltage_data, sample_rate, depth = capture.capture_long_memory(
            channel=1,
            points=1000
        )
        capture.close()
        
        if time_data is not None:
            print(f"Long memory: {len(voltage_data)} points at {sample_rate/1e6:.1f} MSa/s")
            return len(voltage_data) > 0
        return False
    
    def test_data_export(self):
        """Test data export functionality"""
        from data_export import DataExporter
        import os
        
        # Generate test data
        time_data = np.linspace(0, 1, 1000)
        voltage_data = np.sin(2 * np.pi * 5 * time_data)
        
        exporter = DataExporter()
        
        # Test CSV export
        filename = "test_export.csv"
        result = exporter.export_csv(filename, time_data, voltage_data)
        
        if result and os.path.exists(filename):
            os.remove(filename)  # Clean up
            print("CSV export verified")
            return True
        return False
    
    def test_spectrum_analyzer(self):
        """Test FFT spectrum analyzer"""
        from spectrum_analyzer import SpectrumAnalyzer
        
        # Generate test signal
        fs = 10000
        t = np.linspace(0, 1, fs)
        signal = np.sin(2 * np.pi * 100 * t) + 0.5 * np.sin(2 * np.pi * 200 * t)
        
        analyzer = SpectrumAnalyzer()
        frequencies, magnitudes, phases, sample_rate = analyzer.compute_fft(
            t, signal, window='hann'
        )
        
        # Find peaks
        peaks = analyzer.find_peaks(frequencies, magnitudes, num_peaks=2)
        
        if len(peaks['frequencies']) >= 2:
            print(f"Found peaks at: {peaks['frequencies'][0]:.1f}Hz, {peaks['frequencies'][1]:.1f}Hz")
            # Check if peaks are close to expected frequencies
            expected = [100, 200]
            found = sorted(peaks['frequencies'][:2])
            
            tolerance = 5  # Hz
            match1 = abs(found[0] - expected[0]) < tolerance
            match2 = abs(found[1] - expected[1]) < tolerance
            
            return match1 and match2
        return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*60)
        print("ANTHROSCILLOSCOPE TEST SUITE")
        print("="*60)
        print(f"Testing oscilloscope at: {self.ip_address}")
        
        if not self.setup():
            print("❌ Failed to connect to oscilloscope")
            return False
        
        # Run all tests
        tests = [
            ("Connection", self.test_connection),
            ("Waveform Capture", self.test_waveform_capture),
            ("Screenshot Capture", self.test_screenshot_capture),
            ("Measurements", self.test_measurements),
            ("Device Discovery", self.test_device_discovery),
            ("Trigger Control", self.test_trigger_control),
            ("Acquisition Control", self.test_acquisition_control),
            ("Long Memory Capture", self.test_long_memory_capture),
            ("Data Export", self.test_data_export),
            ("Spectrum Analyzer", self.test_spectrum_analyzer),
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
            time.sleep(0.5)  # Small delay between tests
        
        # Print summary
        self.print_summary()
        
        self.teardown()
        
        return self.tests_failed == 0
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        
        total_tests = self.tests_passed + self.tests_failed
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        
        if self.tests_failed == 0:
            print("\n🎉 ALL TESTS PASSED! 🎉")
        else:
            print("\n⚠️ Some tests failed. Details:")
            for name, status, error in self.test_results:
                if status != "PASS":
                    print(f"  - {name}: {status}")
                    if error:
                        print(f"    Error: {error}")
        
        # Calculate success rate
        if total_tests > 0:
            success_rate = (self.tests_passed / total_tests) * 100
            print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    def quick_test(self):
        """Run quick connectivity test"""
        print("\n🚀 QUICK TEST")
        print("-"*40)
        
        if not self.setup():
            print("❌ Connection failed")
            return False
        
        # Just test connection and basic functionality
        self.run_test("Connection", self.test_connection)
        self.run_test("Basic Waveform", self.test_waveform_capture)
        
        self.print_summary()
        self.teardown()
        
        return self.tests_failed == 0


def main():
    """Main test entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Anthroscilloscope Test Suite')
    parser.add_argument('--ip', default='192.168.68.73', 
                       help='Oscilloscope IP address')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick test only')
    
    args = parser.parse_args()
    
    test_suite = AnthroscilloscopeTestSuite(args.ip)
    
    if args.quick:
        success = test_suite.quick_test()
    else:
        success = test_suite.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()