import os
import glob
from detect_sinusoidal_noise_weights import detect_sinusoidal_noise_weights

def quick_test_parameters(folder, test_file=None, custom_params=None):
    """
    Quick test of specific parameter combinations on a single file.
    
    Parameters:
    -----------
    folder : str
        Path to folder containing Excel files
    test_file : str, optional
        Specific file to test (if None, uses first available file)
    custom_params : dict, optional
        Custom parameters to test. If None, tests default combinations.
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
    
    # Default parameter combinations to test
    if custom_params is None:
        param_sets = [
            # Current parameters
            {"name": "Current", "win_size_sec": 0.25, "power_ratio_thresh": 0.25, "co_detection_window_sec": 0.05},
            
            # More sensitive (lower thresholds)
            {"name": "Sensitive", "win_size_sec": 0.25, "power_ratio_thresh": 0.1, "co_detection_window_sec": 0.02},
            
            # More conservative (higher thresholds)
            {"name": "Conservative", "win_size_sec": 0.5, "power_ratio_thresh": 0.5, "co_detection_window_sec": 0.1},
            
            # Larger window for better frequency resolution
            {"name": "Large Window", "win_size_sec": 1.0, "power_ratio_thresh": 0.25, "co_detection_window_sec": 0.05},
            
            # Smaller window for better time resolution
            {"name": "Small Window", "win_size_sec": 0.1, "power_ratio_thresh": 0.25, "co_detection_window_sec": 0.05},
            
            # Tight co-detection window
            {"name": "Tight Co-detection", "win_size_sec": 0.25, "power_ratio_thresh": 0.25, "co_detection_window_sec": 0.02},
            
            # Loose co-detection window
            {"name": "Loose Co-detection", "win_size_sec": 0.25, "power_ratio_thresh": 0.25, "co_detection_window_sec": 0.25},
        ]
    else:
        param_sets = [custom_params]
    
    results = []
    
    for params in param_sets:
        print(f"\nTesting: {params['name']}")
        print(f"  win_size_sec: {params['win_size_sec']}")
        print(f"  power_ratio_thresh: {params['power_ratio_thresh']}")
        print(f"  co_detection_window_sec: {params['co_detection_window_sec']}")
        
        try:
            # Run detection with current parameters
            sinusoid_times, sinusoid_indices, dom_freqs, dom_phases, vacuum_times = detect_sinusoidal_noise_weights(
                test_file, 
                params['win_size_sec'], 
                params['power_ratio_thresh'], 
                params['co_detection_window_sec']
            )
            
            # Count total sinusoid detections across all channels
            total_sinusoids = sum(len(times) for times in sinusoid_times)
            
            print(f"  Result: {len(vacuum_times)} vacuum events, {total_sinusoids} sinusoid detections")
            
            if vacuum_times:
                print(f"  ✓ Vacuum effect detected!")
                for i, vt in enumerate(vacuum_times):
                    print(f"    Event {i+1}: {vt}")
            else:
                print(f"  ✗ No vacuum effect detected")
            
            # Store results
            result = {
                'name': params['name'],
                'win_size_sec': params['win_size_sec'],
                'power_ratio_thresh': params['power_ratio_thresh'],
                'co_detection_window_sec': params['co_detection_window_sec'],
                'num_vacuum_events': len(vacuum_times),
                'num_sinusoid_detections': total_sinusoids,
                'success': True
            }
            
        except Exception as e:
            print(f"  Error: {str(e)}")
            result = {
                'name': params['name'],
                'win_size_sec': params['win_size_sec'],
                'power_ratio_thresh': params['power_ratio_thresh'],
                'co_detection_window_sec': params['co_detection_window_sec'],
                'num_vacuum_events': 0,
                'num_sinusoid_detections': 0,
                'success': False,
                'error': str(e)
            }
        
        results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("QUICK TEST SUMMARY")
    print("="*70)
    
    successful_tests = [r for r in results if r['success']]
    vacuum_detected = [r for r in successful_tests if r['num_vacuum_events'] > 0]
    
    print(f"\nSuccessful tests: {len(successful_tests)}/{len(param_sets)}")
    print(f"Tests with vacuum detection: {len(vacuum_detected)}")
    
    if vacuum_detected:
        print(f"\nBest parameter sets for vacuum detection:")
        for result in sorted(vacuum_detected, key=lambda x: x['num_vacuum_events'], reverse=True):
            print(f"  {result['name']}: {result['num_vacuum_events']} events")
            print(f"    Parameters: win={result['win_size_sec']}s, thr={result['power_ratio_thresh']}, codet={result['co_detection_window_sec']}s")
    
    return results

if __name__ == "__main__":
    # Set your folder path here
    folder = r'D:\Coolers\Phyton\excel_files'
    
    # Test default parameter combinations
    results = quick_test_parameters(folder)
    
    # Or test custom parameters
    # custom_params = {
    #     "name": "Custom Test",
    #     "win_size_sec": 0.3,
    #     "power_ratio_thresh": 0.2,
    #     "co_detection_window_sec": 0.03
    # }
    # results = quick_test_parameters(folder, custom_params=custom_params)
