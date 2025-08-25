# =============================================================================
# Sinusoidal Noise Detection in Weight Sensor Data
# =============================================================================
# This script analyzes weight sensor data to detect sinusoidal noise patterns
# that may indicate vacuum-related events or mechanical vibrations.

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

def detect_sinusoidal_noise_weights(
    filename, win_size_sec=0.5, power_ratio_thresh=0.5, co_detection_window_sec=0.5):
    """
    Detects sinusoidal noise patterns in 4-channel weight sensor data.
    
    This function analyzes weight measurements from 4 sensors to identify:
    1. Sinusoidal oscillations in individual channels using FFT analysis
    2. Anti-phase oscillations between sensor pairs (1,4) and (2,3) 
    3. Vacuum events when both pairs exhibit anti-phase behavior simultaneously
    
    Parameters:
    -----------
    filename : str
        Path to Excel file containing weight data with 'timestamp' and 'weight_1' to 'weight_4' columns
    win_size_sec : float, default=0.5
        Size of sliding window for FFT analysis in seconds
    power_ratio_thresh : float, default=0.5
        Threshold for dominant frequency power ratio (peak power / total power)
    co_detection_window_sec : float, default=0.5
        Time window for considering detections as simultaneous across channels
        
    Returns:
    --------
    tuple of (sinusoid_times, sinusoid_indices, dom_freqs, dom_phases, vacuum_times)
        - sinusoid_times: List of detection timestamps per channel
        - sinusoid_indices: List of detection sample indices per channel  
        - dom_freqs: List of dominant frequencies detected per channel
        - dom_phases: List of phase values at dominant frequencies per channel
        - vacuum_times: List of timestamps where vacuum events were detected
    """

    print(f"Processing file: {filename}")

    # =============================================================================
    # DATA LOADING AND PREPROCESSING
    # =============================================================================
    
    # --- Read data from Excel file ---
    df = pd.read_excel(filename)
    assert 'timestamp' in df.columns, "No column named 'timestamp'!"
    N = len(df)  # Total number of data points
    t = pd.to_datetime(df['timestamp'])  # Convert timestamps to datetime objects

    # --- Estimate sampling frequency from timestamp differences ---
    if N < 2:
        raise ValueError("Not enough samples to determine sampling frequency!")
    
    # Calculate time differences between consecutive samples
    dt_seconds = (t.diff().dropna().dt.total_seconds()).values
    # Use median to get robust estimate of sampling period
    fs = 1 / np.median(dt_seconds)
    print(f"Estimated fs: {fs:.3f} Hz")

    # Convert window size from seconds to samples for FFT analysis
    win_size = int(round(win_size_sec * fs))
    half_win = win_size // 2
    print(f"FFT window: {win_size} samples ({win_size_sec:.2f} s)")

    # Define the 4 weight sensor channels
    weight_names = ['weight_1','weight_2','weight_3','weight_4']
    n_chan = 4
    zeroing_samples = 20  # Number of initial samples to use for zero reference

    # =============================================================================
    # WEIGHT DATA PREPROCESSING
    # =============================================================================
    
    # --- Zero reference & spike correction ---
    # Process each weight channel to remove DC offset and correct measurement spikes
    weights = np.zeros((N, n_chan))
    
    for ch, name in enumerate(weight_names):
        # Get raw weight data for this channel
        w = df[name].values
        
        # Calculate zero reference from first few samples (baseline correction)
        zero_ref = np.mean(w[:zeroing_samples])
        w_zero = w - zero_ref  # Remove DC offset
        
        # Copy for spike correction
        w_corr = w_zero.copy()
        
        # Spike detection and correction algorithm
        # If neighbors are stable (difference < 10) but center point deviates significantly (> 200),
        # replace the spike with average of neighbors
        for i in range(1, N-1):
            pre, post, center = w_zero[i-1], w_zero[i+1], w_zero[i]
            
            # Check if neighboring points are stable (small difference)
            if abs(pre - post) < 10:
                neighbor_avg = (pre + post) / 2
                
                # If center point is a spike (large deviation from neighbors)
                if abs(center - neighbor_avg) > 200:
                    w_corr[i] = neighbor_avg  # Replace spike with neighbor average
        
        # Store corrected weight data
        weights[:,ch] = w_corr

    # Calculate total weight across all sensors for reference
    total_weight = np.sum(weights, axis=1)

    # =============================================================================
    # SINUSOIDAL PATTERN DETECTION USING FFT
    # =============================================================================
    
    # --- Sinusoidal detection per channel ---
    # Initialize storage for detection results
    sinusoid_times   = [[] for _ in range(n_chan)]  # Timestamps of detections
    sinusoid_indices = [[] for _ in range(n_chan)]  # Sample indices of detections
    dom_freqs        = [[] for _ in range(n_chan)]  # Dominant frequencies detected
    dom_phases       = [[] for _ in range(n_chan)]  # Phase angles at dominant frequencies

    # Process each weight channel independently
    for ch in range(n_chan):
        sig = weights[:,ch]  # Get signal for current channel
        s_indices, s_freqs, s_phases = [], [], []  # Local storage for this channel
        
        last_detection_idx = -np.inf  # Track last detection to prevent clustering
        min_gap_samples = int(round(co_detection_window_sec * fs))  # Minimum gap between detections
        
        # Sliding window analysis across the signal
        for i in range(half_win, N-half_win):
            # Skip if too close to previous detection (avoid clustering)
            if s_indices and (i - last_detection_idx) < min_gap_samples:
                continue
            
            # Extract segment for FFT analysis
            segment = sig[i-half_win:i+half_win+1]
            
            # Perform FFT and convert to power spectrum
            Y = np.fft.fft(segment)                    # Complex FFT
            P2 = np.abs(Y) / win_size                  # Two-sided power spectrum
            P1 = P2[:win_size//2+1]                   # One-sided power spectrum
            P1[1:-1] = 2*P1[1:-1]                     # Account for negative frequencies
            
            # Remove DC component for analysis
            P1_no_dc = P1.copy()
            P1_no_dc[0] = 0
            
            # Find dominant frequency component
            maxval = np.max(P1_no_dc)                 # Peak power
            idx_peak = np.argmax(P1_no_dc)            # Index of peak frequency
            
            # Calculate power concentration ratio (how much power is in the peak)
            ratio = maxval / (np.sum(P1_no_dc) + 1e-12)  # Add small value to avoid division by zero
            
            # Detection criteria: high power ratio and sufficient amplitude
            if ratio > power_ratio_thresh and maxval > 10:
                s_indices.append(i)                   # Store sample index
                freq = idx_peak * fs / win_size       # Convert bin to frequency
                s_freqs.append(freq)                  # Store frequency
                phase = np.angle(Y[idx_peak])         # Extract phase at peak frequency
                s_phases.append(phase)                # Store phase
                last_detection_idx = i                # Update last detection position
        
        # Store results for this channel
        sinusoid_indices[ch] = s_indices
        sinusoid_times[ch] = t.iloc[s_indices].to_list()  # Convert indices to timestamps
        dom_freqs[ch] = s_freqs
        dom_phases[ch] = s_phases

    # =============================================================================
    # VISUALIZATION OF WEIGHT DATA AND DETECTIONS
    # =============================================================================
    
    # --- Plot all channels using Object-Oriented matplotlib API ---
    fig, ax = plt.subplots(figsize=(14,7))
    colors = plt.cm.tab10.colors  # Get distinct colors for each channel
    
    # Plot weight data for each channel
    for ch in range(n_chan):
        ax.plot(t, weights[:,ch], color=colors[ch], label=f'Weight {ch+1}')
    
    # Plot total weight as black line
    ax.plot(t, total_weight, 'k', lw=1.5, label='Total weight')

    # Mark detection points and add vertical lines
    for ch in range(n_chan):
        idxs = sinusoid_indices[ch]
        # Plot detection points as circles
        ax.plot(np.array(t)[idxs], weights[idxs, ch], 'o', color=colors[ch], markersize=5)
        # Add vertical dashed lines at detection times
        for i in idxs:
            ax.axvline(t.iloc[i], color=colors[ch], linestyle='--', linewidth=1, alpha=0.6)

    # =============================================================================
    # VACUUM EVENT DETECTION VIA ANTI-PHASE ANALYSIS
    # =============================================================================
    
    # --- Vacuum detection: both (1,4) AND (2,3) must match (anti-phase, same freq) ---
    # Vacuum events are characterized by anti-phase oscillations between opposing sensor pairs
    phase_diff_thresh = np.pi/1.1  # ~163° - threshold for considering phases as anti-phase
    freq_tol = 0.1                 # Frequency tolerance for matching between sensors
    vacuum_times = []              # Storage for detected vacuum event timestamps
    vacuum_pairs = []              # Storage for which sensor pairs were involved

    # =============================================================================
    # BUILD MASTER TIMELINE OF ALL DETECTIONS
    # =============================================================================
    
    # Build master list of all detections for aligning windows across channels
    all_times = []           # All detection times from all channels
    chan_for_time = []       # Which channel each detection belongs to
    det_idx_for_time = []    # Index within that channel's detection list
    
    # Collect all detection times from all channels
    for ch in range(n_chan):
        all_times.extend(sinusoid_times[ch])
        chan_for_time.extend([ch]*len(sinusoid_times[ch]))
        det_idx_for_time.extend(range(len(sinusoid_times[ch])))
    
    # Sort all detection times chronologically
    all_times_np = np.array([pd.Timestamp(tt).to_datetime64() for tt in all_times])
    idx_sort = np.argsort(all_times_np)
    all_times_np = all_times_np[idx_sort]
    chan_for_time = np.array(chan_for_time)[idx_sort]
    det_idx_for_time = np.array(det_idx_for_time)[idx_sort]

    # =============================================================================
    # ANALYZE TEMPORAL COINCIDENCE AND PHASE RELATIONSHIPS
    # =============================================================================
    
    # Detection loop - check each time point for multi-channel events
    for i in range(len(all_times_np)):
        time_i = all_times_np[i]
        
        # Find all detections within the co-detection window around this time
        close_idx = np.where(np.abs((all_times_np - time_i) / np.timedelta64(1, 's')) <= co_detection_window_sec/2)[0]
        
        # Initialize channel information structure
        chan_info = [{'det':False, 'freq':np.nan, 'phase':np.nan} for _ in range(n_chan)]
        
        # Populate channel information for channels with detections in this window
        for ch in range(n_chan):
            idx_this = close_idx[chan_for_time[close_idx] == ch]
            if len(idx_this) > 0:
                # Get the detection index for this channel
                idx_det = det_idx_for_time[idx_this[0]]
                chan_info[ch]['det'] = True
                chan_info[ch]['freq'] = dom_freqs[ch][idx_det]
                chan_info[ch]['phase'] = dom_phases[ch][idx_det]
        
        # =============================================================================
        # CHECK FOR ANTI-PHASE PATTERNS IN SENSOR PAIRS
        # =============================================================================
        
        found_14 = found_23 = False  # Flags for anti-phase detection in each pair
        
        # Check pair (1,4) - channels 0 and 3
        if chan_info[0]['det'] and chan_info[3]['det'] and \
            abs(chan_info[0]['freq'] - chan_info[3]['freq']) < freq_tol:
            # Calculate phase difference between the two channels
            pdiff_14 = np.abs(np.angle(np.exp(1j*(chan_info[0]['phase'] - chan_info[3]['phase']))))
            # Check if phases are approximately anti-phase (difference ≈ π)
            if abs(pdiff_14 - np.pi) < phase_diff_thresh:
                found_14 = True
        
        # Check pair (2,3) - channels 1 and 2  
        if chan_info[1]['det'] and chan_info[2]['det'] and \
            abs(chan_info[1]['freq'] - chan_info[2]['freq']) < freq_tol:
            # Calculate phase difference between the two channels
            pdiff_23 = np.abs(np.angle(np.exp(1j*(chan_info[1]['phase'] - chan_info[2]['phase']))))
            # Check if phases are approximately anti-phase (difference ≈ π)
            if abs(pdiff_23 - np.pi) < phase_diff_thresh:
                found_23 = True
        
        # =============================================================================
        # VACUUM EVENT CONFIRMATION AND LOGGING
        # =============================================================================
        
        # Vacuum event detected if BOTH pairs show anti-phase behavior
        if found_14 and found_23:
            time_dt = pd.to_datetime(str(time_i))
            
            # Avoid duplicate detections too close in time (< 0.1 seconds apart)
            if not vacuum_times or min([abs((time_dt - vt).total_seconds()) for vt in vacuum_times]) > 0.1:
                # Mark vacuum event on plot with red vertical line
                ax.axvline(time_dt, color='r', lw=2)
                
                # Store vacuum event information
                vacuum_times.append(time_dt)
                vacuum_pairs.append([(1,4),(2,3)])
                
                # Log the detection
                print(f'Antiphase (same freq) at {time_dt}: W1/W4 and W2/W3')

    # =============================================================================
    # FINALIZE PLOT AND SAVE RESULTS
    # =============================================================================
    
    # Configure plot appearance and labels
    ax.set_title(filename)
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Weight (g)')
    ax.legend()
    ax.grid(True)
    fig.tight_layout()

    # =============================================================================
    # FILE OUTPUT AND RESULTS STORAGE
    # =============================================================================
    
    # --- Save outputs in a subfolder ---
    # Create output directory based on input filename
    filepath, basename = os.path.split(filename)
    name, _ = os.path.splitext(basename)
    outdir = os.path.join(filepath, name)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # Create parameter string for filename identification
    param_str = f'win_size_sec={win_size_sec}_thr={power_ratio_thresh:.2f}_codet={co_detection_window_sec:.2f}'
    param_str_filename = param_str.replace('.', '').replace('=', '_').replace(' ', '')

    # Save plot as PNG file (before showing to avoid display issues)
    pngname = f'{param_str_filename}_graph.png'
    pngpathname = os.path.join(outdir, pngname)
    fig.savefig(pngpathname)
    plt.close(fig)  # Close the figure to free memory and prevent display
    print(f'Saved figure as PNG to: {pngpathname}')

    # Save enhanced detection summary as CSV file with both vacuum and sinusoidal detections
    # Create comprehensive detection data
    detection_data = []
    
    # Add vacuum events
    for vt in vacuum_times:
        detection_data.append({
            'detection_type': 'vacuum_event',
            'timestamp': str(vt),
            'weight_1_detection': '',
            'weight_2_detection': '',
            'weight_3_detection': '',
            'weight_4_detection': '',
            'frequency_hz': '',
            'phase_radians': '',
            'phase_degrees': ''
        })
    
    # Add sinusoidal detections for each weight channel
    for ch in range(n_chan):
        channel_name = f'weight_{ch+1}'
        if sinusoid_times[ch] and len(sinusoid_times[ch]) > 0:
            for i, (time_det, freq_det, phase_det) in enumerate(zip(sinusoid_times[ch], dom_freqs[ch], dom_phases[ch])):
                # Create detection entry for this channel
                detection_entry = {
                    'detection_type': f'sinusoidal_{channel_name}',
                    'timestamp': str(time_det),
                    'weight_1_detection': str(time_det) if ch == 0 else '',
                    'weight_2_detection': str(time_det) if ch == 1 else '',
                    'weight_3_detection': str(time_det) if ch == 2 else '',
                    'weight_4_detection': str(time_det) if ch == 3 else '',
                    'frequency_hz': f'{freq_det:.3f}',
                    'phase_radians': f'{phase_det:.3f}',
                    'phase_degrees': f'{np.degrees(phase_det):.1f}'
                }
                detection_data.append(detection_entry)
    
    # Create DataFrame and save
    if detection_data:
        summary_df = pd.DataFrame(detection_data)
        csvname = f'{param_str_filename}_detections.csv'
        csvpathname = os.path.join(outdir, csvname)
        summary_df.to_csv(csvpathname, index=False)
        print(f'Saved enhanced detection summary to: {csvpathname}')
        print(f'  • {len(vacuum_times)} vacuum events')
        print(f'  • {sum(len(st) if st else 0 for st in sinusoid_times)} total sinusoidal detections')
    else:
        # No detections - create empty CSV with headers
        summary_df = pd.DataFrame(columns=[
            'detection_type', 'timestamp', 'weight_1_detection', 'weight_2_detection',
            'weight_3_detection', 'weight_4_detection', 'frequency_hz', 'phase_radians', 'phase_degrees'
        ])
        csvname = f'{param_str_filename}_detections.csv'
        csvpathname = os.path.join(outdir, csvname)
        summary_df.to_csv(csvpathname, index=False)
        print(f'Saved empty detection summary to: {csvpathname} (no detections found)')

    # plt.show()  # Commented out to prevent interactive display

    # Return all analysis results
    return sinusoid_times, sinusoid_indices, dom_freqs, dom_phases, vacuum_times
