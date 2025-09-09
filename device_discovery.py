#!/usr/bin/env python3
"""
Device Discovery Module for Anthroscilloscope
Auto-discovers Rigol oscilloscopes on the network using multiple methods
"""

import socket
import subprocess
import time
import pyvisa
from threading import Thread
import re
import platform

try:
    from zeroconf import ServiceBrowser, Zeroconf
    HAS_ZEROCONF = True
except ImportError:
    HAS_ZEROCONF = False
    print("Note: zeroconf not installed. mDNS discovery disabled.")
    print("Install with: pip3 install zeroconf")


class RigolDiscovery:
    """Discover Rigol oscilloscopes on the network"""
    
    def __init__(self):
        self.found_devices = []
        self.rm = pyvisa.ResourceManager('@py')
    
    def discover_all(self, timeout=10):
        """
        Use all available methods to discover oscilloscopes
        
        Args:
            timeout: Maximum time to spend searching (seconds)
        
        Returns:
            List of discovered devices with their details
        """
        print("🔍 Searching for Rigol oscilloscopes on the network...")
        print("=" * 60)
        
        devices = []
        
        # Method 1: VISA resource scan
        print("Method 1: VISA resource scan...")
        visa_devices = self.discover_visa()
        devices.extend(visa_devices)
        
        # Method 2: Direct IP scan of common ranges
        print("\nMethod 2: Scanning common IP ranges...")
        ip_devices = self.discover_ip_scan(timeout=timeout//2)
        devices.extend(ip_devices)
        
        # Method 3: mDNS/Bonjour discovery
        if HAS_ZEROCONF:
            print("\nMethod 3: mDNS/Bonjour discovery...")
            mdns_devices = self.discover_mdns(timeout=timeout//2)
            devices.extend(mdns_devices)
        
        # Method 4: ARP cache check
        print("\nMethod 4: Checking ARP cache...")
        arp_devices = self.discover_arp()
        devices.extend(arp_devices)
        
        # Remove duplicates based on IP
        unique_devices = {}
        for device in devices:
            ip = device.get('ip')
            if ip and ip not in unique_devices:
                unique_devices[ip] = device
        
        self.found_devices = list(unique_devices.values())
        
        print("\n" + "=" * 60)
        print(f"✅ Discovery complete! Found {len(self.found_devices)} device(s)")
        
        return self.found_devices
    
    def discover_visa(self):
        """Discover using PyVISA resource manager"""
        devices = []
        try:
            resources = self.rm.list_resources()
            
            for resource in resources:
                if 'TCPIP' in resource:
                    # Extract IP from VISA resource string
                    ip_match = re.search(r'TCPIP[0-9]*::([0-9.]+)::', resource)
                    if ip_match:
                        ip = ip_match.group(1)
                        
                        # Try to connect and get IDN
                        try:
                            device = self.rm.open_resource(resource)
                            device.timeout = 2000
                            idn = device.query('*IDN?').strip()
                            device.close()
                            
                            if 'RIGOL' in idn.upper():
                                devices.append({
                                    'ip': ip,
                                    'resource': resource,
                                    'idn': idn,
                                    'method': 'VISA'
                                })
                                print(f"  ✓ Found: {ip} - {idn}")
                        except:
                            pass
        except Exception as e:
            print(f"  VISA scan error: {e}")
        
        return devices
    
    def discover_ip_scan(self, timeout=5):
        """Scan common IP ranges for Rigol devices"""
        devices = []
        
        # Get local IP to determine subnet
        local_ip = self._get_local_ip()
        if not local_ip:
            return devices
        
        # Extract subnet (assume /24)
        subnet = '.'.join(local_ip.split('.')[:-1])
        print(f"  Scanning subnet {subnet}.0/24...")
        
        # Quick scan of common IPs
        common_ips = [
            f"{subnet}.{i}" for i in range(1, 255)
        ]
        
        # Use threading for faster scanning
        threads = []
        for ip in common_ips[:50]:  # Limit to first 50 for speed
            thread = Thread(target=self._check_rigol_ip, args=(ip, devices))
            thread.daemon = True
            threads.append(thread)
            thread.start()
        
        # Wait for threads with timeout
        start_time = time.time()
        for thread in threads:
            remaining = timeout - (time.time() - start_time)
            if remaining > 0:
                thread.join(timeout=min(0.1, remaining))
        
        return devices
    
    def _check_rigol_ip(self, ip, devices):
        """Check if an IP address has a Rigol oscilloscope"""
        try:
            # Try to connect on SCPI port 5555
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, 5555))
            sock.close()
            
            if result == 0:
                # Port is open, try SCPI connection
                try:
                    resource = f'TCPIP::{ip}::INSTR'
                    device = self.rm.open_resource(resource)
                    device.timeout = 1000
                    idn = device.query('*IDN?').strip()
                    device.close()
                    
                    if 'RIGOL' in idn.upper():
                        devices.append({
                            'ip': ip,
                            'resource': resource,
                            'idn': idn,
                            'method': 'IP_SCAN'
                        })
                        print(f"  ✓ Found: {ip}")
                except:
                    pass
        except:
            pass
    
    def discover_mdns(self, timeout=5):
        """Discover using mDNS/Bonjour (requires zeroconf)"""
        if not HAS_ZEROCONF:
            return []
        
        devices = []
        
        class MDNSListener:
            def __init__(self, parent_devices):
                self.devices = parent_devices
            
            def add_service(self, zeroconf, service_type, name):
                info = zeroconf.get_service_info(service_type, name)
                if info:
                    ip = socket.inet_ntoa(info.addresses[0])
                    if 'rigol' in name.lower() or 'ds1' in name.lower():
                        self.devices.append({
                            'ip': ip,
                            'resource': f'TCPIP::{ip}::INSTR',
                            'name': name,
                            'method': 'mDNS'
                        })
                        print(f"  ✓ Found via mDNS: {ip} ({name})")
            
            def remove_service(self, zeroconf, service_type, name):
                pass
            
            def update_service(self, zeroconf, service_type, name):
                pass
        
        try:
            zeroconf = Zeroconf()
            listener = MDNSListener(devices)
            
            # Look for common service types
            services = [
                "_lxi._tcp.local.",
                "_scpi-raw._tcp.local.",
                "_http._tcp.local."
            ]
            
            browsers = []
            for service in services:
                browser = ServiceBrowser(zeroconf, service, listener)
                browsers.append(browser)
            
            time.sleep(timeout)
            zeroconf.close()
            
        except Exception as e:
            print(f"  mDNS error: {e}")
        
        return devices
    
    def discover_arp(self):
        """Check ARP cache for Rigol MAC addresses"""
        devices = []
        
        try:
            # Rigol MAC prefixes
            rigol_macs = ['00:19:AF', '00:0C:DC']
            
            # Get ARP table
            if platform.system() == 'Windows':
                cmd = 'arp -a'
            else:
                cmd = 'arp -n'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                for mac_prefix in rigol_macs:
                    if mac_prefix.lower() in line.lower():
                        # Extract IP from line
                        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                        if ip_match:
                            ip = ip_match.group(1)
                            devices.append({
                                'ip': ip,
                                'resource': f'TCPIP::{ip}::INSTR',
                                'method': 'ARP',
                                'mac': mac_prefix
                            })
                            print(f"  ✓ Found Rigol MAC in ARP: {ip}")
        except Exception as e:
            print(f"  ARP check error: {e}")
        
        return devices
    
    def _get_local_ip(self):
        """Get local IP address"""
        try:
            # Create a socket to external address to find local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return None
    
    def quick_discover(self, known_ips=None):
        """
        Quick discovery for known IPs or saved configurations
        
        Args:
            known_ips: List of IPs to check first
        
        Returns:
            First working device found
        """
        if known_ips is None:
            # Default common IPs
            known_ips = [
                '192.168.68.73',  # Your current oscilloscope
                '192.168.1.100',
                '192.168.0.100',
                '10.0.0.100'
            ]
        
        print("Quick discovery of known addresses...")
        
        for ip in known_ips:
            try:
                resource = f'TCPIP::{ip}::INSTR'
                device = self.rm.open_resource(resource)
                device.timeout = 1000
                idn = device.query('*IDN?').strip()
                device.close()
                
                if 'RIGOL' in idn.upper():
                    print(f"✓ Found at {ip}: {idn}")
                    return {
                        'ip': ip,
                        'resource': resource,
                        'idn': idn,
                        'method': 'QUICK'
                    }
            except:
                pass
        
        return None
    
    def save_discovered(self, filename='known_devices.txt'):
        """Save discovered devices for quick future access"""
        try:
            with open(filename, 'w') as f:
                for device in self.found_devices:
                    f.write(f"{device['ip']}|{device.get('idn', 'Unknown')}\n")
            print(f"Saved {len(self.found_devices)} devices to {filename}")
        except Exception as e:
            print(f"Error saving devices: {e}")
    
    def load_known_devices(self, filename='known_devices.txt'):
        """Load previously discovered devices"""
        known_ips = []
        try:
            with open(filename, 'r') as f:
                for line in f:
                    if '|' in line:
                        ip = line.split('|')[0].strip()
                        known_ips.append(ip)
        except:
            pass
        return known_ips


def interactive_discovery():
    """Interactive device discovery with user selection"""
    discovery = RigolDiscovery()
    
    # Try quick discovery first
    print("Attempting quick discovery...")
    device = discovery.quick_discover()
    
    if device:
        print(f"\nQuick discovery successful!")
        print(f"Device: {device['idn']}")
        print(f"IP: {device['ip']}")
        
        response = input("\nUse this device? (Y/n): ").strip().lower()
        if response != 'n':
            return device['ip']
    
    # Full discovery
    print("\nPerforming full network scan...")
    devices = discovery.discover_all(timeout=10)
    
    if not devices:
        print("No devices found!")
        manual_ip = input("Enter IP address manually (or press Enter to cancel): ").strip()
        return manual_ip if manual_ip else None
    
    # Display found devices
    print("\nFound devices:")
    for i, device in enumerate(devices, 1):
        print(f"{i}. {device['ip']} - {device.get('idn', 'Unknown')}")
    
    # Let user select
    while True:
        try:
            choice = input(f"\nSelect device (1-{len(devices)}) or 0 to cancel: ").strip()
            if choice == '0':
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(devices):
                selected = devices[idx]
                discovery.save_discovered()  # Save for future quick discovery
                return selected['ip']
        except:
            print("Invalid selection!")


if __name__ == "__main__":
    # Interactive discovery example
    ip = interactive_discovery()
    if ip:
        print(f"\nSelected oscilloscope at: {ip}")
        print("You can now connect using this IP address")
    else:
        print("\nNo device selected")