#!/usr/bin/env python3
"""
Lissajous Text Generation System - Dependency Verification
Run after installation to verify all components work correctly
"""

def verify_dependencies():
    print("=" * 70)
    print("LISSAJOUS TEXT GENERATION SYSTEM - DEPENDENCY CHECK")
    print("=" * 70)

    critical = [
        ('numpy', 'NumPy'),
        ('scipy', 'SciPy'),
        ('matplotlib', 'Matplotlib'),
        ('pyvisa', 'PyVISA'),
        ('sounddevice', 'SoundDevice'),
    ]

    recommended = [
        ('fontTools', 'FontTools'),
        ('freetype', 'FreeType-Py'),
        ('tkinter', 'Tkinter'),
    ]

    optional = [
        ('shapely', 'Shapely'),
        ('h5py', 'HDF5'),
        ('pytest', 'PyTest'),
        ('PyQt5', 'PyQt5'),
    ]

    def check_packages(packages, category):
        print(f"\n{category}:")
        status = {'installed': 0, 'missing': 0}
        details = []

        for module, name in packages:
            try:
                mod = __import__(module)
                ver = getattr(mod, '__version__', 'unknown')

                # Special handling for tkinter
                if module == 'tkinter':
                    ver = f"{mod.TkVersion}"

                print(f"  ✓ {name:20} v{ver}")
                status['installed'] += 1
                details.append((name, ver, True))
            except ImportError:
                print(f"  ✗ {name:20} MISSING")
                status['missing'] += 1
                details.append((name, None, False))

        return status, details

    print("\n" + "=" * 70)
    crit_status, crit_details = check_packages(critical, "CRITICAL Dependencies")

    print("\n" + "-" * 70)
    rec_status, rec_details = check_packages(recommended, "RECOMMENDED Dependencies")

    print("\n" + "-" * 70)
    opt_status, opt_details = check_packages(optional, "OPTIONAL Dependencies")

    print("\n" + "=" * 70)
    print("SUMMARY:")
    print(f"  Critical:    {crit_status['installed']}/{len(critical)} installed")
    print(f"  Recommended: {rec_status['installed']}/{len(recommended)} installed")
    print(f"  Optional:    {opt_status['installed']}/{len(optional)} installed")

    total_installed = (crit_status['installed'] +
                      rec_status['installed'] +
                      opt_status['installed'])
    total_packages = len(critical) + len(recommended) + len(optional)

    print(f"  Total:       {total_installed}/{total_packages} installed "
          f"({100*total_installed//total_packages}%)")

    print("\n" + "=" * 70)

    if crit_status['missing'] == 0:
        print("✓ STATUS: All critical dependencies installed")
        print("          Ready to proceed with development!")

        if rec_status['missing'] > 0:
            print("\n  Note: Some recommended packages missing.")
            print("        Install with: ./install_dependencies_recommended.sh")
    else:
        print("✗ STATUS: Missing critical dependencies")
        print(f"          {crit_status['missing']} critical package(s) not found")
        print("\n  Install with: ./install_dependencies_critical.sh")

        missing_crit = [name for name, ver, installed in crit_details if not installed]
        print(f"\n  Missing critical: {', '.join(missing_crit)}")

    print("=" * 70)

    # Additional tests for audio and oscilloscope
    if crit_status['missing'] == 0:
        print("\n" + "=" * 70)
        print("ADDITIONAL CHECKS:")
        print("=" * 70)

        # Test SoundDevice
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            print(f"\n  Audio Devices: {len(devices)} found")
            default_out = sd.default.device[1]
            if default_out is not None:
                print(f"  Default Output: {devices[default_out]['name']}")
            else:
                print("  Default Output: None configured")
        except Exception as e:
            print(f"\n  ✗ Audio system check failed: {e}")

        # Test PyVISA
        try:
            import pyvisa
            rm = pyvisa.ResourceManager('@py')
            resources = rm.list_resources()
            print(f"\n  VISA Resources: {len(resources)} found")
            if resources:
                for res in resources:
                    print(f"    - {res}")
            else:
                print("    (No instruments detected - this is normal if not connected)")
        except Exception as e:
            print(f"\n  ✗ PyVISA check failed: {e}")

        print("\n" + "=" * 70)

    return crit_status['missing'] == 0

if __name__ == '__main__':
    import sys
    success = verify_dependencies()
    sys.exit(0 if success else 1)
