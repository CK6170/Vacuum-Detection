import os
import glob
import itertools
import pandas as pd
from detect_sinusoidal_noise_weights import detect_sinusoidal_noise_weights

def optimize_parameters(folder, test_file=None):
    """
    Systematically test different parameter combinations to find optimal settings
    for vacuum effect detection.
    
    Parameters:
    -----------
    folder : str
        Path to folder containing Excel files
    test_file : str, optional
        Specific file to test (if None, uses first available file)
    """
    
    # Get test file
    if test_file is None:
        files = sorted(glob.glob(os.path.join(folder, '*.xlsx')))
        if not files:
            print("No Excel files found in the specified folder!")
            return
        test_file = files[0]
    
    print(f"Testing parameters on file: {os.path.basename(test_file)}")
    print("="*70)
    
    # Parameter ranges to test
    win_size_sec_values = [0.1, 0.25, 0.5, 1.0, 2.0]
    power_ratio_thresh_values = [0.1, 0.25, 0.5, 0.75, 0.9]
    co_detection_window_sec_values = [0.02, 0.05, 0.1, 0.25, 0.5]
    
    # Store results
    results = []
    
    # Test all combinations
    total_combinations = len(win_size_sec_values) * len(power_ratio_thresh_values) * len(co_detection_window_sec_values)
    current = 0
    
    print(f"Testing {total_combinations} parameter combinations...")
    print()
    
    for win_size_sec in win_size_sec_values:
        for power_ratio_thresh in power_ratio_thresh_values:
            for co_detection_window_sec in co_detection_window_sec_values:
                current += 1
                print(f"Progress: {current}/{total_combinations} - Testing: win={win_size_sec}s, thr={power_ratio_thresh}, codet={co_detection_window_sec}s")
                
                try:
                    # Run detection with current parameters
                    sinusoid_times, sinusoid_indices, dom_freqs, dom_phases, vacuum_times = detect_sinusoidal_noise_weights(
                        test_file, win_size_sec, power_ratio_thresh, co_detection_window_sec
                    )
                    
                    # Store results
                    result = {
                        'win_size_sec': win_size_sec,
                        'power_ratio_thresh': power_ratio_thresh,
                        'co_detection_window_sec': co_detection_window_sec,
                        'num_vacuum_events': len(vacuum_times),
                        'num_sinusoid_detections': sum(len(times) for times in sinusoid_times),
                        'success': True
                    }
                    
                    if vacuum_times:
                        result['vacuum_detected'] = True
                        result['first_vacuum_time'] = str(vacuum_times[0])
                    else:
                        result['vacuum_detected'] = False
                        result['first_vacuum_time'] = None
                        
                except Exception as e:
                    print(f"  Error: {str(e)}")
                    result = {
                        'win_size_sec': win_size_sec,
                        'power_ratio_thresh': power_ratio_thresh,
                        'co_detection_window_sec': co_detection_window_sec,
                        'num_vacuum_events': 0,
                        'num_sinusoid_detections': 0,
                        'success': False,
                        'vacuum_detected': False,
                        'first_vacuum_time': None,
                        'error': str(e)
                    }
                
                results.append(result)
                print(f"  Result: {result['num_vacuum_events']} vacuum events, {result['num_sinusoid_detections']} sinusoid detections")
                print()
    
    # Convert to DataFrame for analysis
    df_results = pd.DataFrame(results)
    
    # Save detailed results
    output_file = os.path.join(folder, 'parameter_optimization_results.csv')
    df_results.to_csv(output_file, index=False)
    print(f"Detailed results saved to: {output_file}")
    
    # Analyze results
    print("\n" + "="*70)
    print("PARAMETER OPTIMIZATION ANALYSIS")
    print("="*70)
    
    # Filter successful runs
    successful_runs = df_results[df_results['success'] == True]
    
    if len(successful_runs) == 0:
        print("No successful parameter combinations found!")
        return
    
    # Find best parameters for different criteria
    print(f"\nSuccessful parameter combinations: {len(successful_runs)}")
    
    # 1. Most vacuum events detected
    if successful_runs['vacuum_detected'].any():
        best_vacuum = successful_runs.loc[successful_runs['num_vacuum_events'].idxmax()]
        print(f"\nBest for MAXIMUM vacuum events:")
        print(f"  win_size_sec: {best_vacuum['win_size_sec']}")
        print(f"  power_ratio_thresh: {best_vacuum['power_ratio_thresh']}")
        print(f"  co_detection_window_sec: {best_vacuum['co_detection_window_sec']}")
        print(f"  Vacuum events: {best_vacuum['num_vacuum_events']}")
    
    # 2. Balanced detection (some vacuum events but not too many)
    balanced_runs = successful_runs[
        (successful_runs['num_vacuum_events'] > 0) & 
        (successful_runs['num_vacuum_events'] <= 5)
    ]
    
    if len(balanced_runs) > 0:
        # Find the most balanced (closest to 2-3 events)
        balanced_runs['balance_score'] = abs(balanced_runs['num_vacuum_events'] - 2.5)
        best_balanced = balanced_runs.loc[balanced_runs['balance_score'].idxmin()]
        
        print(f"\nBest for BALANCED detection (2-3 events):")
        print(f"  win_size_sec: {best_balanced['win_size_sec']}")
        print(f"  power_ratio_thresh: {best_balanced['power_ratio_thresh']}")
        print(f"  co_detection_window_sec: {best_balanced['co_detection_window_sec']}")
        print(f"  Vacuum events: {best_balanced['num_vacuum_events']}")
    
    # 3. Parameter sensitivity analysis
    print(f"\nPARAMETER SENSITIVITY ANALYSIS:")
    
    # Window size sensitivity
    win_size_analysis = successful_runs.groupby('win_size_sec')['num_vacuum_events'].agg(['mean', 'std', 'count'])
    print(f"\nWindow size sensitivity:")
    for win_size, stats in win_size_analysis.iterrows():
        print(f"  {win_size}s: avg={stats['mean']:.1f}±{stats['std']:.1f} events (n={stats['count']})")
    
    # Power ratio threshold sensitivity
    power_analysis = successful_runs.groupby('power_ratio_thresh')['num_vacuum_events'].agg(['mean', 'std', 'count'])
    print(f"\nPower ratio threshold sensitivity:")
    for threshold, stats in power_analysis.iterrows():
        print(f"  {threshold}: avg={stats['mean']:.1f}±{stats['std']:.1f} events (n={stats['count']})")
    
    # Co-detection window sensitivity
    codet_analysis = successful_runs.groupby('co_detection_window_sec')['num_vacuum_events'].agg(['mean', 'std', 'count'])
    print(f"\nCo-detection window sensitivity:")
    for window, stats in codet_analysis.iterrows():
        print(f"  {window}s: avg={stats['mean']:.1f}±{stats['std']:.1f} events (n={stats['count']})")
    
    # 4. Recommended parameter sets
    print(f"\nRECOMMENDED PARAMETER SETS:")
    
    # Conservative (fewer false positives)
    conservative = successful_runs[successful_runs['power_ratio_thresh'] >= 0.5].loc[
        successful_runs[successful_runs['power_ratio_thresh'] >= 0.5]['num_vacuum_events'].idxmin()
    ]
    print(f"\nConservative (fewer false positives):")
    print(f"  win_size_sec: {conservative['win_size_sec']}")
    print(f"  power_ratio_thresh: {conservative['power_ratio_thresh']}")
    print(f"  co_detection_window_sec: {conservative['co_detection_window_sec']}")
    
    # Sensitive (more detections)
    sensitive = successful_runs[successful_runs['power_ratio_thresh'] <= 0.3].loc[
        successful_runs[successful_runs['power_ratio_thresh'] <= 0.3]['num_vacuum_events'].idxmax()
    ]
    print(f"\nSensitive (more detections):")
    print(f"  win_size_sec: {sensitive['win_size_sec']}")
    print(f"  power_ratio_thresh: {sensitive['power_ratio_thresh']}")
    print(f"  co_detection_window_sec: {sensitive['co_detection_window_sec']}")
    
    return df_results

if __name__ == "__main__":
    # Set your folder path here
    folder = r'D:\Coolers\Phyton\excel_files'
    
    # Run optimization
    results = optimize_parameters(folder)
    
    print(f"\nOptimization complete! Check the CSV file for detailed results.")
