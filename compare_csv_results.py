import os
import glob
import pandas as pd
import csv
from collections import defaultdict
import statistics

def parse_csv_file(csv_path):
    """Parse a CSV file and extract detection data."""
    if not os.path.exists(csv_path):
        return None
    
    results = {
        'vacuum_events': [],
        'sinusoidal_detections': defaultdict(list),
        'total_sinusoidal': 0,
        'frequencies': []
    }
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            # Skip comment lines for Go files
            lines = []
            for line in file:
                if not line.startswith('#'):
                    lines.append(line)
            
            if len(lines) <= 1:  # Only header or empty
                return results
                
            reader = csv.DictReader(lines)
            
            for row in reader:
                if not row.get('detection_type'):
                    continue
                    
                if row['detection_type'] == 'vacuum_event':
                    results['vacuum_events'].append(row['timestamp'])
                elif row['detection_type'].startswith('sinusoidal_weight_'):
                    channel = row['detection_type'].replace('sinusoidal_weight_', '')
                    detection_data = {
                        'timestamp': row['timestamp'],
                        'frequency': float(row['frequency_hz']) if row['frequency_hz'] else 0,
                        'phase': float(row['phase_radians']) if row['phase_radians'] else 0
                    }
                    results['sinusoidal_detections'][channel].append(detection_data)
                    results['total_sinusoidal'] += 1
                    if detection_data['frequency'] > 0:
                        results['frequencies'].append(detection_data['frequency'])
    
    except Exception as e:
        print(f"Error parsing {csv_path}: {e}")
        return None
    
    return results

def compare_results(py_results, go_results, filename):
    """Compare results between Python and Go implementations."""
    comparison = {
        'filename': filename,
        'vacuum_events_match': len(py_results['vacuum_events']) == len(go_results['vacuum_events']),
        'py_vacuum_count': len(py_results['vacuum_events']),
        'go_vacuum_count': len(go_results['vacuum_events']),
        'py_sinusoidal_count': py_results['total_sinusoidal'],
        'go_sinusoidal_count': go_results['total_sinusoidal'],
        'sinusoidal_diff': abs(py_results['total_sinusoidal'] - go_results['total_sinusoidal']),
        'py_avg_freq': statistics.mean(py_results['frequencies']) if py_results['frequencies'] else 0,
        'go_avg_freq': statistics.mean(go_results['frequencies']) if go_results['frequencies'] else 0,
        'freq_diff': 0,
        'both_have_detections': py_results['total_sinusoidal'] > 0 and go_results['total_sinusoidal'] > 0,
        'both_no_detections': py_results['total_sinusoidal'] == 0 and go_results['total_sinusoidal'] == 0
    }
    
    if comparison['py_avg_freq'] > 0 and comparison['go_avg_freq'] > 0:
        comparison['freq_diff'] = abs(comparison['py_avg_freq'] - comparison['go_avg_freq'])
    
    return comparison

def main():
    base_dir = r'D:\Coolers\Phyton\excel_files'
    
    print("SCANNING for directories with both Python and Go CSV files...")
    
    # Find directories with both CSV files
    valid_comparisons = []
    subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    print(f"Found {len(subdirs)} total directories, scanning for matching CSV files...")
    
    # Process with progress reporting
    for i, subdir in enumerate(subdirs, 1):
        if i % 1000 == 0:  # Progress report every 1000 directories
            print(f"  Scanned {i}/{len(subdirs)} directories...")
            
        dir_path = os.path.join(base_dir, subdir)
        
        py_csv = os.path.join(dir_path, 'win_size_sec_05_thr_050_codet_015_detections_py.csv')
        go_csv = os.path.join(dir_path, 'win_size_sec_0_5_thr_0_50_codet_0_15_detections_go.csv')
        
        if os.path.exists(py_csv) and os.path.exists(go_csv):
            valid_comparisons.append((subdir, py_csv, go_csv))
    
    print(f"FOUND {len(valid_comparisons)} directories with both CSV files (processing ALL {len(valid_comparisons)} files)")
    
    if len(valid_comparisons) == 0:
        print("ERROR: No matching CSV files found!")
        return
    
    # Compare results
    results = []
    errors = []
    
    for i, (filename, py_csv, go_csv) in enumerate(valid_comparisons, 1):
        print(f"Processing {i}/{len(valid_comparisons)}: {filename[:50]}...")
        
        py_results = parse_csv_file(py_csv)
        go_results = parse_csv_file(go_csv)
        
        if py_results is None or go_results is None:
            errors.append(filename)
            continue
        
        comparison = compare_results(py_results, go_results, filename)
        results.append(comparison)
    
    # Generate summary statistics
    print("\n" + "="*80)
    print("COMPREHENSIVE CSV COMPARISON SUMMARY")
    print("="*80)
    
    print(f"FILES ANALYZED: {len(results)} successful comparisons")
    if errors:
        print(f"ERRORS: {len(errors)} files failed to parse")
    
    # Vacuum event comparison
    vacuum_matches = sum(1 for r in results if r['vacuum_events_match'])
    total_py_vacuum = sum(r['py_vacuum_count'] for r in results)
    total_go_vacuum = sum(r['go_vacuum_count'] for r in results)
    
    print(f"\nVACUUM EVENT ANALYSIS:")
    print(f"  - Perfect vacuum matches: {vacuum_matches}/{len(results)} ({vacuum_matches/len(results)*100:.1f}%)")
    print(f"  - Total Python vacuum events: {total_py_vacuum}")
    print(f"  - Total Go vacuum events: {total_go_vacuum}")
    print(f"  - Vacuum event agreement: {total_py_vacuum == total_go_vacuum}")
    
    # Sinusoidal detection comparison
    total_py_sinusoidal = sum(r['py_sinusoidal_count'] for r in results)
    total_go_sinusoidal = sum(r['go_sinusoidal_count'] for r in results)
    sinusoidal_diffs = [r['sinusoidal_diff'] for r in results]
    
    print(f"\nSINUSOIDAL DETECTION ANALYSIS:")
    print(f"  - Total Python sinusoidal detections: {total_py_sinusoidal:,}")
    print(f"  - Total Go sinusoidal detections: {total_go_sinusoidal:,}")
    print(f"  - Difference: {abs(total_py_sinusoidal - total_go_sinusoidal):,} ({abs(total_py_sinusoidal - total_go_sinusoidal)/max(total_py_sinusoidal, total_go_sinusoidal)*100:.2f}%)")
    print(f"  - Average difference per file: {statistics.mean(sinusoidal_diffs):.1f} detections")
    print(f"  - Max difference per file: {max(sinusoidal_diffs)} detections")
    
    # Agreement analysis
    both_detect = sum(1 for r in results if r['both_have_detections'])
    both_no_detect = sum(1 for r in results if r['both_no_detections'])
    
    print(f"\nAGREEMENT ANALYSIS:")
    print(f"  - Both found detections: {both_detect}/{len(results)} files")
    print(f"  - Both found no detections: {both_no_detect}/{len(results)} files")
    print(f"  - Total agreement: {both_detect + both_no_detect}/{len(results)} files ({(both_detect + both_no_detect)/len(results)*100:.1f}%)")
    
    # Frequency analysis
    freq_comparisons = [r for r in results if r['py_avg_freq'] > 0 and r['go_avg_freq'] > 0]
    if freq_comparisons:
        freq_diffs = [r['freq_diff'] for r in freq_comparisons]
        print(f"\nFREQUENCY ANALYSIS ({len(freq_comparisons)} files with detections):")
        print(f"  - Average frequency difference: {statistics.mean(freq_diffs):.4f} Hz")
        print(f"  - Max frequency difference: {max(freq_diffs):.4f} Hz")
        print(f"  - Frequency agreement within 0.1 Hz: {sum(1 for d in freq_diffs if d < 0.1)}/{len(freq_diffs)} files")
    
    # Distribution analysis
    exact_matches = sum(1 for r in results if r['sinusoidal_diff'] == 0)
    small_diffs = sum(1 for r in results if r['sinusoidal_diff'] <= 2)
    
    print(f"\nDETECTION DIFFERENCE DISTRIBUTION:")
    print(f"  - Exact matches (0 difference): {exact_matches}/{len(results)} ({exact_matches/len(results)*100:.1f}%)")
    print(f"  - Small differences (<=2): {small_diffs}/{len(results)} ({small_diffs/len(results)*100:.1f}%)")
    print(f"  - Large differences (>5): {sum(1 for r in results if r['sinusoidal_diff'] > 5)}/{len(results)}")
    
    print("\n" + "="*80)
    print("OVERALL ASSESSMENT:")
    
    if vacuum_matches == len(results) and abs(total_py_sinusoidal - total_go_sinusoidal) / max(total_py_sinusoidal, total_go_sinusoidal) < 0.05:
        print("EXCELLENT: Both implementations show very high agreement!")
    elif vacuum_matches >= len(results) * 0.9 and abs(total_py_sinusoidal - total_go_sinusoidal) / max(total_py_sinusoidal, total_go_sinusoidal) < 0.1:
        print("GOOD: Both implementations show good agreement with minor differences")
    else:
        print("REVIEW NEEDED: Implementations show significant differences")
    
    print("="*80)

if __name__ == "__main__":
    main()
