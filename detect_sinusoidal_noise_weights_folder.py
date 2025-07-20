import os
import glob
from detect_sinusoidal_noise_weights import detect_sinusoidal_noise_weights

def detect_sinusoidal_noise_weights_folder(folder_path, win_size, fs, power_ratio_thresh=0.5, zeroing_samples=10, co_detection_window_sec=0.5):
    """
    Run detect_sinusoidal_noise_weights on all .xlsx files in the folder.
    Returns a list of results for each file.
    """
    # Find all .xlsx files
    files = glob.glob(os.path.join(folder_path, '*.xlsx'))
    
    if not files:
        print('No .xlsx files found in the specified folder.')
        return []

    results = []
    for filename in files:
        print(f'\nRunning sinusoidal noise detection on {os.path.basename(filename)}')
        # Call with all parameters
        result = detect_sinusoidal_noise_weights(
            filename, win_size, fs, power_ratio_thresh, zeroing_samples, co_detection_window_sec)
        results.append([filename] + list(result))
    
    return results
