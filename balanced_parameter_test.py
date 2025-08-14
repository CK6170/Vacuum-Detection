import os
import glob
from detect_sinusoidal_noise_weights import detect_sinusoidal_noise_weights

def test_balanced_parameters(folder, test_file=None):
    """
    Test parameter combinations that are balanced - not too sensitive, not too aggressive.
    Focuses on finding parameters that detect vacuum effects in multiple files.
    """
    
    # Get test file
    if test_file is None:
        files = sorted(glob.glob(os.path.join(folder, '*.xlsx')))
        if not files:
            print("No Excel files found in the specified folder!")
            return
        test_file = files[0]
    
    print(f"Testing balanced parameters on file: {os.path.basename(test_file)}")
    print("="*70)
    
    # Balanced parameter combinations - less sensitive than current (0.1, 0.75, 0.02)
    # but more sensitive than very conservative ones
    param_sets = [
        # Current parameters (too aggressive - only 1 file)
        {"name": "Current (Too Aggressive)", "win_size_sec": 0.1, "power_ratio_thresh": 0.75, "co_detection_window_sec": 0.02},
        
        # Balanced approach 1: Larger window, moderate threshold, moderate timing
        {"name": "Balanced 1", "win_size_sec": 0.5, "power_ratio_thresh": 0.5, "co_detection_window_sec": 0.1},
        
        # Balanced approach 2: Medium window, lower threshold, moderate timing
        {"name": "Balanced 2", "win_size_sec": 0.25, "power_ratio_thresh": 0.4, "co_detection_window_sec": 0.1},
        
        # Balanced approach 3: Medium window, moderate threshold, looser timing
        {"name": "Balanced 3", "win_size_sec": 0.25, "power_ratio_thresh": 0.5, "co_detection_window_sec": 0.15},
        
        # Balanced approach 4: Larger window, lower threshold, moderate timing
        {"name": "Balanced 4", "win_size_sec": 0.75, "power_ratio_thresh": 0.4, "co_detection_window_sec": 0.1},
        
        # Balanced approach 5: Medium window, balanced threshold, balanced timing
        {"name": "Balanced 5", "win_size_sec": 0.3, "power_ratio_thresh": 0.45, "co_detection_window_sec": 0.08},
        
        # Conservative but not too much
        {"name": "Moderately Conservative", "win_size_sec": 0.6, "power_ratio_thresh": 0.6, "co_detection_window_sec": 0.12},
        
        # Sensitive but not too much
        {"name": "Moderately Sensitive", "win_size_sec": 0.2, "power_ratio_thresh": 0.35, "co_detection_window_sec": 0.06},
    ]
    
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
    
    # Summary and recommendations
    print("\n" + "="*70)
    print("BALANCED PARAMETER RECOMMENDATIONS")
    print("="*70)
    
    successful_tests = [r for r in results if r['success']]
    vacuum_detected = [r for r in successful_tests if r['num_vacuum_events'] > 0]
    
    print(f"\nSuccessful tests: {len(successful_tests)}/{len(param_sets)}")
    print(f"Tests with vacuum detection: {len(vacuum_detected)}")
    
    if vacuum_detected:
        print(f"\nParameter sets that detected vacuum effects:")
        for result in sorted(vacuum_detected, key=lambda x: x['num_vacuum_events'], reverse=True):
            print(f"  {result['name']}: {result['num_vacuum_events']} events")
            print(f"    Parameters: win={result['win_size_sec']}s, thr={result['power_ratio_thresh']}, codet={result['co_detection_window_sec']}s")
    
    # Find the most balanced parameters (not too many events, not too few)
    if vacuum_detected:
        print(f"\nRECOMMENDED BALANCED PARAMETERS:")
        
        # Look for parameters that give 2-4 vacuum events (balanced)
        balanced_options = [r for r in vacuum_detected if 2 <= r['num_vacuum_events'] <= 4]
        
        if balanced_options:
            # Sort by how close to 3 events (ideal balance)
            for result in balanced_options:
                result['balance_score'] = abs(result['num_vacuum_events'] - 3)
            
            best_balanced = min(balanced_options, key=lambda x: x['balance_score'])
            print(f"\nBest balanced option (closest to 3 events):")
            print(f"  {best_balanced['name']}")
            print(f"  win_size_sec: {best_balanced['win_size_sec']}")
            print(f"  power_ratio_thresh: {best_balanced['power_ratio_thresh']}")
            print(f"  co_detection_window_sec: {best_balanced['co_detection_window_sec']}")
            print(f"  Vacuum events: {best_balanced['num_vacuum_events']}")
        else:
            # If no balanced options, recommend the one with moderate events
            moderate_options = [r for r in vacuum_detected if r['num_vacuum_events'] <= 5]
            if moderate_options:
                best_moderate = min(moderate_options, key=lambda x: x['num_vacuum_events'])
                print(f"\nBest moderate option (not too aggressive):")
                print(f"  {best_moderate['name']}")
                print(f"  win_size_sec: {best_moderate['win_size_sec']}")
                print(f"  power_ratio_thresh: {best_moderate['power_ratio_thresh']}")
                print(f"  co_detection_window_sec: {best_moderate['co_detection_window_sec']}")
                print(f"  Vacuum events: {best_moderate['num_vacuum_events']}")
    
    # Parameter adjustment suggestions
    print(f"\nPARAMETER ADJUSTMENT STRATEGY:")
    print(f"  Current issue: win_size_sec=0.1 is too small (too time-sensitive)")
    print(f"  Recommendation: Increase win_size_sec to 0.25-0.75 for better pattern detection")
    print(f"  Current issue: co_detection_window_sec=0.02 is too tight")
    print(f"  Recommendation: Increase to 0.08-0.15 for more flexible timing")
    print(f"  Current issue: power_ratio_thresh=0.75 might be too high")
    print(f"  Recommendation: Try 0.4-0.6 for balanced sensitivity")
    
    return results

if __name__ == "__main__":
    # Set your folder path here
    folder = r'D:\Coolers\Phyton\excel_files'
    
    # Test balanced parameters
    results = test_balanced_parameters(folder)
    
    print(f"\nBalanced parameter testing complete!")
    print(f"Use the recommended parameters in your run_all.py script.")
