#!/usr/bin/env python3
"""
Data Export Module for Anthroscilloscope
Exports waveform data to CSV, HDF5, and other formats
"""

import csv
import json
import numpy as np
from datetime import datetime
import os

try:
    import h5py
    HAS_HDF5 = True
except ImportError:
    HAS_HDF5 = False
    print("Warning: h5py not installed. HDF5 export disabled.")
    print("Install with: pip3 install h5py")

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class DataExporter:
    """Export oscilloscope data to various formats"""
    
    @staticmethod
    def export_csv(filename, time_data, voltage_data, channel_info=None, metadata=None):
        """
        Export waveform data to CSV file
        
        Args:
            filename: Output filename (will add .csv if not present)
            time_data: Time axis data (numpy array or list)
            voltage_data: Voltage data (numpy array or list, or dict for multiple channels)
            channel_info: Dictionary with channel information
            metadata: Additional metadata to include
        """
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write metadata as comments
                if metadata:
                    for key, value in metadata.items():
                        writer.writerow([f'# {key}: {value}'])
                
                # Handle single channel or multiple channels
                if isinstance(voltage_data, dict):
                    # Multiple channels
                    headers = ['Time (s)'] + [f'Channel {ch} (V)' for ch in voltage_data.keys()]
                    writer.writerow(headers)
                    
                    # Assume all channels have same time base
                    first_channel = list(voltage_data.keys())[0]
                    time = voltage_data[first_channel].get('time', time_data)
                    
                    for i in range(len(time)):
                        row = [time[i]]
                        for ch in voltage_data.keys():
                            volts = voltage_data[ch].get('voltage', voltage_data[ch])
                            row.append(volts[i] if i < len(volts) else 0)
                        writer.writerow(row)
                else:
                    # Single channel
                    writer.writerow(['Time (s)', 'Voltage (V)'])
                    for t, v in zip(time_data, voltage_data):
                        writer.writerow([t, v])
            
            print(f"Data exported to {filename}")
            return True
            
        except Exception as e:
            print(f"CSV export failed: {e}")
            return False
    
    @staticmethod
    def export_hdf5(filename, time_data, voltage_data, channel_info=None, metadata=None):
        """
        Export waveform data to HDF5 file (efficient for large datasets)
        
        Args:
            filename: Output filename (will add .h5 if not present)
            time_data: Time axis data
            voltage_data: Voltage data (single channel or dict of channels)
            channel_info: Dictionary with channel settings
            metadata: Additional metadata
        """
        if not HAS_HDF5:
            print("HDF5 export not available. Install h5py first.")
            return False
        
        if not filename.endswith(('.h5', '.hdf5')):
            filename += '.h5'
        
        try:
            with h5py.File(filename, 'w') as f:
                # Create main group
                waveform_group = f.create_group('waveform')
                
                # Handle single or multiple channels
                if isinstance(voltage_data, dict):
                    # Multiple channels
                    for ch_name, ch_data in voltage_data.items():
                        ch_group = waveform_group.create_group(ch_name)
                        
                        # Store time and voltage data
                        if 'time' in ch_data:
                            ch_group.create_dataset('time', data=ch_data['time'], compression='gzip')
                        else:
                            ch_group.create_dataset('time', data=time_data, compression='gzip')
                        
                        if 'voltage' in ch_data:
                            ch_group.create_dataset('voltage', data=ch_data['voltage'], compression='gzip')
                        else:
                            ch_group.create_dataset('voltage', data=ch_data, compression='gzip')
                        
                        # Add channel-specific metadata
                        if 'sample_rate' in ch_data:
                            ch_group.attrs['sample_rate'] = ch_data['sample_rate']
                        if 'memory_depth' in ch_data:
                            ch_group.attrs['memory_depth'] = ch_data['memory_depth']
                else:
                    # Single channel
                    ch_group = waveform_group.create_group('CH1')
                    ch_group.create_dataset('time', data=time_data, compression='gzip')
                    ch_group.create_dataset('voltage', data=voltage_data, compression='gzip')
                
                # Add metadata
                if metadata:
                    meta_group = f.create_group('metadata')
                    for key, value in metadata.items():
                        if value is not None:
                            meta_group.attrs[key] = str(value)
                
                # Add channel info
                if channel_info:
                    info_group = f.create_group('channel_info')
                    for key, value in channel_info.items():
                        if value is not None:
                            info_group.attrs[key] = str(value)
                
                # Add file metadata
                f.attrs['created'] = datetime.now().isoformat()
                f.attrs['format_version'] = '1.0'
                f.attrs['software'] = 'Anthroscilloscope'
            
            print(f"Data exported to {filename}")
            file_size = os.path.getsize(filename) / (1024 * 1024)
            print(f"File size: {file_size:.2f} MB")
            return True
            
        except Exception as e:
            print(f"HDF5 export failed: {e}")
            return False
    
    @staticmethod
    def export_numpy(filename, time_data, voltage_data, metadata=None):
        """
        Export data as NumPy binary files (.npz)
        
        Args:
            filename: Output filename (will add .npz if not present)
            time_data: Time axis data
            voltage_data: Voltage data
            metadata: Additional metadata
        """
        if not filename.endswith('.npz'):
            filename += '.npz'
        
        try:
            save_dict = {}
            
            if isinstance(voltage_data, dict):
                # Multiple channels
                for ch_name, ch_data in voltage_data.items():
                    if 'time' in ch_data:
                        save_dict[f'{ch_name}_time'] = ch_data['time']
                    else:
                        save_dict[f'{ch_name}_time'] = time_data
                    
                    if 'voltage' in ch_data:
                        save_dict[f'{ch_name}_voltage'] = ch_data['voltage']
                    else:
                        save_dict[f'{ch_name}_voltage'] = ch_data
            else:
                # Single channel
                save_dict['time'] = time_data
                save_dict['voltage'] = voltage_data
            
            # Add metadata as arrays
            if metadata:
                save_dict['metadata'] = np.array(str(metadata))
            
            np.savez_compressed(filename, **save_dict)
            print(f"Data exported to {filename}")
            return True
            
        except Exception as e:
            print(f"NumPy export failed: {e}")
            return False
    
    @staticmethod
    def export_wav(filename, voltage_data, sample_rate, normalize=True):
        """
        Export waveform as audio WAV file (useful for audio analysis)
        
        Args:
            filename: Output filename
            voltage_data: Voltage data to convert to audio
            sample_rate: Sample rate in Hz
            normalize: Normalize to [-1, 1] range
        """
        try:
            from scipy.io import wavfile
        except ImportError:
            print("WAV export requires scipy. Install with: pip3 install scipy")
            return False
        
        if not filename.endswith('.wav'):
            filename += '.wav'
        
        try:
            # Handle dict input
            if isinstance(voltage_data, dict):
                # Use first channel
                first_ch = list(voltage_data.keys())[0]
                if 'voltage' in voltage_data[first_ch]:
                    audio_data = voltage_data[first_ch]['voltage']
                else:
                    audio_data = voltage_data[first_ch]
            else:
                audio_data = voltage_data
            
            # Convert to numpy array
            audio_data = np.array(audio_data)
            
            # Normalize if requested
            if normalize:
                max_val = np.max(np.abs(audio_data))
                if max_val > 0:
                    audio_data = audio_data / max_val
            
            # Convert to 16-bit PCM
            audio_data = (audio_data * 32767).astype(np.int16)
            
            # Write WAV file
            wavfile.write(filename, int(sample_rate), audio_data)
            print(f"Audio exported to {filename}")
            print(f"Sample rate: {sample_rate/1000:.1f} kHz")
            print(f"Duration: {len(audio_data)/sample_rate:.3f} seconds")
            return True
            
        except Exception as e:
            print(f"WAV export failed: {e}")
            return False
    
    @staticmethod
    def export_json(filename, time_data, voltage_data, metadata=None):
        """
        Export data as JSON (human-readable but larger files)
        
        Args:
            filename: Output filename
            time_data: Time axis data
            voltage_data: Voltage data
            metadata: Additional metadata
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        try:
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'software': 'Anthroscilloscope',
                'data': {}
            }
            
            if isinstance(voltage_data, dict):
                # Multiple channels
                for ch_name, ch_data in voltage_data.items():
                    if isinstance(ch_data, dict):
                        export_data['data'][ch_name] = {
                            'time': ch_data.get('time', time_data).tolist(),
                            'voltage': ch_data.get('voltage', ch_data).tolist()
                        }
                    else:
                        export_data['data'][ch_name] = {
                            'time': time_data.tolist() if hasattr(time_data, 'tolist') else list(time_data),
                            'voltage': ch_data.tolist() if hasattr(ch_data, 'tolist') else list(ch_data)
                        }
            else:
                # Single channel
                export_data['data']['CH1'] = {
                    'time': time_data.tolist() if hasattr(time_data, 'tolist') else list(time_data),
                    'voltage': voltage_data.tolist() if hasattr(voltage_data, 'tolist') else list(voltage_data)
                }
            
            if metadata:
                export_data['metadata'] = metadata
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"Data exported to {filename}")
            return True
            
        except Exception as e:
            print(f"JSON export failed: {e}")
            return False
    
    @staticmethod
    def export_matlab(filename, time_data, voltage_data, metadata=None):
        """
        Export data in MATLAB format (.mat)
        
        Args:
            filename: Output filename
            time_data: Time axis data
            voltage_data: Voltage data
            metadata: Additional metadata
        """
        try:
            from scipy.io import savemat
        except ImportError:
            print("MATLAB export requires scipy. Install with: pip3 install scipy")
            return False
        
        if not filename.endswith('.mat'):
            filename += '.mat'
        
        try:
            mat_dict = {}
            
            if isinstance(voltage_data, dict):
                # Multiple channels
                for ch_name, ch_data in voltage_data.items():
                    clean_name = ch_name.replace('CH', 'channel')
                    if isinstance(ch_data, dict):
                        mat_dict[f'{clean_name}_time'] = ch_data.get('time', time_data)
                        mat_dict[f'{clean_name}_voltage'] = ch_data.get('voltage', ch_data)
                    else:
                        mat_dict[f'{clean_name}_time'] = time_data
                        mat_dict[f'{clean_name}_voltage'] = ch_data
            else:
                # Single channel
                mat_dict['time'] = time_data
                mat_dict['voltage'] = voltage_data
            
            # Add metadata
            if metadata:
                for key, value in metadata.items():
                    if isinstance(value, (int, float, str, np.ndarray)):
                        mat_dict[f'meta_{key}'] = value
            
            savemat(filename, mat_dict)
            print(f"Data exported to {filename}")
            return True
            
        except Exception as e:
            print(f"MATLAB export failed: {e}")
            return False


def export_suite(time_data, voltage_data, base_filename, formats=['csv', 'hdf5'], metadata=None):
    """
    Export data to multiple formats at once
    
    Args:
        time_data: Time axis data
        voltage_data: Voltage data
        base_filename: Base filename (without extension)
        formats: List of formats to export ('csv', 'hdf5', 'numpy', 'json', 'matlab')
        metadata: Metadata dictionary
    """
    exporter = DataExporter()
    results = {}
    
    for fmt in formats:
        if fmt.lower() == 'csv':
            results['csv'] = exporter.export_csv(base_filename, time_data, voltage_data, metadata=metadata)
        elif fmt.lower() == 'hdf5' and HAS_HDF5:
            results['hdf5'] = exporter.export_hdf5(base_filename, time_data, voltage_data, metadata=metadata)
        elif fmt.lower() == 'numpy':
            results['numpy'] = exporter.export_numpy(base_filename, time_data, voltage_data, metadata=metadata)
        elif fmt.lower() == 'json':
            results['json'] = exporter.export_json(base_filename, time_data, voltage_data, metadata=metadata)
        elif fmt.lower() == 'matlab':
            results['matlab'] = exporter.export_matlab(base_filename, time_data, voltage_data, metadata=metadata)
    
    return results


if __name__ == "__main__":
    # Example usage
    import numpy as np
    
    # Generate sample data
    time = np.linspace(0, 1, 1000)
    voltage = np.sin(2 * np.pi * 5 * time) + 0.5 * np.sin(2 * np.pi * 50 * time)
    
    metadata = {
        'oscilloscope': 'Rigol DS1104Z Plus',
        'channel': 1,
        'vertical_scale': '1V/div',
        'timebase': '100ms/div',
        'sample_rate': 1000
    }
    
    # Export to multiple formats
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"waveform_{timestamp}"
    
    export_suite(time, voltage, base_filename, 
                formats=['csv', 'numpy', 'json'],
                metadata=metadata)