import os
import glob
import sys
import random
import time
from detect_sinusoidal_noise_weights import detect_sinusoidal_noise_weights

folder = r'D:\Coolers\Python1\excel_files'
win_size_sec = 0.5
power_ratio_thresh = 0.5
co_detection_window_sec = 0.15


files = sorted(glob.glob(os.path.join(folder, '*.xlsx')))

print(f"Found {len(files)} files in {folder}")

# Lists to track results
files_with_vacuum = []
files_without_vacuum = []
all_results = []
all_errors = []  # Track all errors

for file_index, file in enumerate(files, 1):
    try:
        print(f"Processing file {file_index}/{len(files)}: {os.path.basename(file)}")
        
        # Get the results from the detection function
        sinusoid_times, sinusoid_indices, dom_freqs, dom_phases, vacuum_times = detect_sinusoidal_noise_weights(
            file, win_size_sec, power_ratio_thresh, co_detection_window_sec
        )
        
        # Show detection results summary
        print(f"  📊 Detections: {len(vacuum_times)} vacuum events, {sum(len(st) if st else 0 for st in sinusoid_times) if sinusoid_times else 0} total sinusoidal detections")
        
        # Store results
        file_result = {
            'filename': os.path.basename(file),
            'filepath': file,
            'vacuum_times': vacuum_times,
            'num_vacuum_events': len(vacuum_times),
            'sinusoid_times': sinusoid_times,
            'sinusoid_indices': sinusoid_indices,
            'dom_freqs': dom_freqs,
            'dom_phases': dom_phases,
            'status': 'success'
        }
        all_results.append(file_result)
        
        # Categorize file
        if vacuum_times:
            files_with_vacuum.append(file)
        else:
            files_without_vacuum.append(file)
            
    except Exception as e:
        print(f"❌ Error processing file {file_index}/{len(files)}: {os.path.basename(file)} - {str(e)}")
        error_msg = f"Error processing {os.path.basename(file)}: {str(e)}"
        all_errors.append({
            'filename': os.path.basename(file),
            'filepath': file,
            'error': str(e),
            'error_type': type(e).__name__
        })
        files_without_vacuum.append(file)
        
        # Add failed file to results
        file_result = {
            'filename': os.path.basename(file),
            'filepath': file,
            'vacuum_times': [],
            'num_vacuum_events': 0,
            'sinusoid_times': [],
            'sinusoid_indices': [],
            'dom_freqs': [],
            'dom_phases': [],
            'status': 'failed',
            'error': str(e)
        }
        all_results.append(file_result)

print("\n" + "="*60)
print("SUMMARY OF VACUUM EFFECT DETECTION")
print("="*60)

print(f"\n📊 DETECTION PARAMETERS:")
print(f"  • Window size: {win_size_sec} seconds")
print(f"  • Power ratio threshold: {power_ratio_thresh}")
print(f"  • Co-detection window: {co_detection_window_sec} seconds")

print(f"\n📁 FILES PROCESSED:")
print(f"  • Files WITH vacuum effects: {len(files_with_vacuum)}")
print(f"  • Files WITHOUT vacuum effects: {len(files_without_vacuum)}")
print(f"  • Total files processed: {len(files)}")
print(f"  • Files with vacuum effects: {len(files_with_vacuum)} ({len(files_with_vacuum)/len(files)*100:.1f}%)")
print(f"  • Files without vacuum effects: {len(files_without_vacuum)} ({len(files_without_vacuum)/len(files)*100:.1f}%)")

# COMPREHENSIVE ERROR SUMMARY
print("\n" + "="*60)
print("COMPREHENSIVE ERROR SUMMARY")
print("="*60)

if all_errors:
    print(f"\n❌ ERRORS FOUND: {len(all_errors)} files failed to process")
    
    # Group errors by type
    error_types = {}
    for error in all_errors:
        error_type = error['error_type']
        if error_type not in error_types:
            error_types[error_type] = []
        error_types[error_type].append(error['filename'])
    
    print(f"\n📊 ERROR BREAKDOWN BY TYPE:")
    for error_type, filenames in error_types.items():
        print(f"  {error_type}: {len(filenames)} files")
    
    # Common error patterns
    print(f"\n🔍 COMMON ERROR PATTERNS:")
    common_errors = {}
    for error in all_errors:
        error_msg = error['error'].lower()
        if 'memory' in error_msg or 'out of memory' in error_msg:
            common_errors['Memory Issues'] = common_errors.get('Memory Issues', 0) + 1
        elif 'file' in error_msg and ('not found' in error_msg or 'does not exist' in error_msg):
            common_errors['File Not Found'] = common_errors.get('File Not Found', 0) + 1
        elif 'permission' in error_msg or 'access denied' in error_msg:
            common_errors['Permission Issues'] = common_errors.get('Permission Issues', 0) + 1
        elif 'value' in error_msg or 'index' in error_msg:
            common_errors['Data/Value Errors'] = common_errors.get('Data/Value Errors', 0) + 1
        elif 'matplotlib' in error_msg or 'plot' in error_msg:
            common_errors['Plotting/PNG Errors'] = common_errors.get('Plotting/PNG Errors', 0) + 1
        else:
            common_errors['Other Errors'] = common_errors.get('Other Errors', 0) + 1
    
    for error_category, count in common_errors.items():
        print(f"  {error_category}: {count} occurrences")
    
    print(f"\n💡 TROUBLESHOOTING RECOMMENDATIONS:")
    if any('Memory' in k for k in common_errors.keys()):
        print("  • Memory Issues: Close other applications, reduce data size, or process files in smaller batches")
    if any('File Not Found' in k for k in common_errors.keys()):
        print("  • File Not Found: Check file paths and ensure Excel files are accessible")
    if any('Permission' in k for k in common_errors.keys()):
        print("  • Permission Issues: Run as administrator or check folder permissions")
    if any('Data/Value' in k for k in common_errors.keys()):
        print("  • Data Errors: Check Excel file format and data integrity")
    if any('Plotting/PNG' in k for k in common_errors.keys()):
        print("  • PNG Generation Errors: This explains why some PNG files are corrupted!")
        print("    - Check matplotlib backend configuration")
        print("    - Verify sufficient disk space")
        print("    - Try different image format (JPG instead of PNG)")
    
else:
    print(f"\n✅ NO ERRORS: All {len(files)} files processed successfully!")

print("\nAll files processed. PNGs and CSVs saved in their respective subfolders.")

# Note: Sinusoidal detection data is now included in individual detection CSV files
# saved in each subdirectory by the detect_sinusoidal_noise_weights function
print("\n" + "="*60)
print("SINUSOIDAL DETECTION DATA")
print("="*60)
print("✅ Sinusoidal detection data is now included in the individual detection CSV files")
print("   saved in each subdirectory alongside the PNG graphs.")
print("   Each CSV contains both vacuum events and sinusoidal detections per weight channel.")

# Show summary of what was processed
print(f"\n📊 PROCESSING SUMMARY:")
print(f"  • Total files processed: {len(files)}")
print(f"  • Files with vacuum effects: {len(files_with_vacuum)}")
print(f"  • Files without vacuum effects: {len(files_without_vacuum)}")

# Show sinusoidal detection summary
total_sinusoidal_detections = 0
for result in all_results:
    if result['status'] == 'success' and result['sinusoid_times']:
        total_sinusoidal_detections += sum(len(st) if st else 0 for st in result['sinusoid_times'])

print(f"  • Total sinusoidal detections across all files: {total_sinusoidal_detections}")
print(f"  • Detection CSV files saved in individual subdirectories")
print(f"  • Each CSV contains vacuum events and sinusoidal detections per weight channel")

# CSV files are now created individually in each subdirectory
# with enhanced detection data including sinusoidal detections per weight channel

# Function to open random graphs for visual inspection
def open_random_graphs_for_inspection():
    """Open random graphs from files with and without vacuum effects for visual inspection."""
    
    print("\n" + "="*60)
    print("OPENING RANDOM GRAPHS FOR VISUAL INSPECTION")
    print("="*60)
    
    # Create pattern for finding PNG files - use the actual pattern that works
    pattern = f'win_size_sec={win_size_sec}_thr={power_ratio_thresh:.2f}_codet={co_detection_window_sec:.2f}'
    pattern_filename = pattern.replace('.', '').replace('=', '_').replace(' ', '')
    
    print(f"Looking for PNG files with pattern: {pattern_filename}")
    
    # First, let's see what PNG files actually exist in the folder
    all_pngs_in_folder = glob.glob(os.path.join(folder, '*', '*_graph.png'))
    print(f"Total PNG files found in folder: {len(all_pngs_in_folder)}")
    
    # Filter to only show PNG files with CURRENT parameters
    current_pattern_pngs = glob.glob(os.path.join(folder, '*', f'{pattern_filename}_graph.png'))
    print(f"PNG files with CURRENT parameters ({pattern_filename}): {len(current_pattern_pngs)}")
    
    if current_pattern_pngs:
        print(f"PNG files with CURRENT parameters: {len(current_pattern_pngs)} files")
    
    # Show count of PNG files with OTHER parameters (for reference)
    other_pngs = len(all_pngs_in_folder) - len(current_pattern_pngs)
    if other_pngs > 0:
        print(f"\nNote: {other_pngs} PNG files found with OTHER parameter combinations (ignoring these)")
        print("These are from previous parameter testing runs and will not be used.")
    
    # Count subfolders
    subfolders = [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]
    print(f"Found {len(subfolders)} subfolders in {folder}")
    
    # Find PNG files for files with vacuum effects
    vacuum_pngs = []
    for filepath in files_with_vacuum:
        filename = os.path.basename(filepath)
        name, _ = os.path.splitext(filename)
        
        # Use the actual pattern that matches your generated files
        png_path = os.path.join(folder, name, f'{pattern_filename}_graph.png')
        
        if os.path.exists(png_path):
            vacuum_pngs.append(png_path)
    
    # Find PNG files for files without vacuum effects
    no_vacuum_pngs = []
    for filepath in files_without_vacuum:
        filename = os.path.basename(filepath)
        name, _ = os.path.splitext(filename)
        
        # Use the actual pattern that matches your generated files
        png_path = os.path.join(folder, name, f'{pattern_filename}_graph.png')
        
        if os.path.exists(png_path):
            no_vacuum_pngs.append(png_path)
    
    print(f"\nFound {len(vacuum_pngs)} PNG files for files WITH vacuum effects")
    print(f"Found {len(no_vacuum_pngs)} PNG files for files WITHOUT vacuum effects")
    
    # Remove duplicates from both lists
    vacuum_pngs = list(set(vacuum_pngs))
    no_vacuum_pngs = list(set(no_vacuum_pngs))
    
    # Remove any files that appear in both lists
    common_pngs = set(vacuum_pngs) & set(no_vacuum_pngs)
    if common_pngs:
        print(f"\nWarning: Found {len(common_pngs)} PNG files that appear in both categories:")
        for png in common_pngs:
            print(f"  {os.path.basename(os.path.dirname(png))}")
        # Remove common files from both lists
        vacuum_pngs = [png for png in vacuum_pngs if png not in common_pngs]
        no_vacuum_pngs = [png for png in no_vacuum_pngs if png not in common_pngs]
        print(f"Removed common files. Now have {len(vacuum_pngs)} unique files with vacuum, {len(no_vacuum_pngs)} unique files without.")
    
    # Ensure we have enough files to open
    graphs_to_open = []
    
    # Select 3 random files with vacuum effects (or all if less than 3)
    if vacuum_pngs:
        num_vacuum_to_open = min(3, len(vacuum_pngs))
        if len(vacuum_pngs) >= 3:
            selected_vacuum = random.sample(vacuum_pngs, 3)
        else:
            selected_vacuum = vacuum_pngs  # Use all available
        graphs_to_open.extend(selected_vacuum)
        print(f"\nOpening {len(selected_vacuum)} graphs from files WITH vacuum effects:")
        for png in selected_vacuum:
            print(f"  ✓ {os.path.basename(os.path.dirname(png))}")
    else:
        print("\nNo PNG files found for files WITH vacuum effects!")
    
    # Select 3 random files without vacuum effects (or all if less than 3)
    if no_vacuum_pngs:
        num_no_vacuum_to_open = min(3, len(no_vacuum_pngs))
        if len(no_vacuum_pngs) >= 3:
            selected_no_vacuum = random.sample(no_vacuum_pngs, 3)
        else:
            selected_no_vacuum = no_vacuum_pngs  # Use all available
        graphs_to_open.extend(selected_no_vacuum)
        print(f"\nOpening {len(selected_no_vacuum)} graphs from files WITHOUT vacuum effects:")
        for png in selected_no_vacuum:
            print(f"  ✗ {os.path.basename(os.path.dirname(png))}")
    else:
        print("\nNo PNG files found for files WITHOUT vacuum effects!")
    
    # If we don't have enough files, try to find more PNGs in the folder
    if len(graphs_to_open) < 6:
        print(f"\nOnly found {len(graphs_to_open)} PNG files, searching for more...")
        
        # Search for any PNG files with the pattern in the folder
        all_pngs = glob.glob(os.path.join(folder, '*', '*_graph.png'))
        print(f"Found {len(all_pngs)} total PNG files in folder")
        
        # Add any missing files to reach 6 total (avoiding duplicates)
        remaining_slots = 6 - len(graphs_to_open)
        available_pngs = [png for png in all_pngs if png not in graphs_to_open]
        
        if available_pngs and remaining_slots > 0:
            additional_pngs = random.sample(available_pngs, min(remaining_slots, len(available_pngs)))
            graphs_to_open.extend(additional_pngs)
            print(f"Added {len(additional_pngs)} additional PNG files to reach {len(graphs_to_open)} total")
        else:
            print(f"No additional PNG files available to reach 6 total.")
    
    # Remove any final duplicates and ensure unique files
    graphs_to_open = list(set(graphs_to_open))
    print(f"\nFinal unique PNG files to open: {len(graphs_to_open)}")
    
    # Open the selected graphs
    print(f"\nOpening {len(graphs_to_open)} graphs...")
    for i, pngpathname in enumerate(graphs_to_open, 1):
        try:
            if sys.platform.startswith('darwin'):
                os.system(f'open "{pngpathname}"')  # macOS
            elif os.name == 'nt':
                os.startfile(pngpathname)           # Windows
            elif os.name == 'posix':
                os.system(f'xdg-open "{pngpathname}"')  # Linux
            
            # Add delay between opening files to ensure they all open properly
            if i < len(graphs_to_open):  # Don't delay after the last file
                time.sleep(2)
                
        except Exception as e:
            print(f"Error opening graph: {str(e)}")
    
    print(f"\nOpened {len(graphs_to_open)} graphs for visual inspection!")
    if len(graphs_to_open) < 6:
        print(f"Note: Only opened {len(graphs_to_open)} graphs instead of 6 due to limited PNG files available.")
        print(f"Total PNG files in folder: {len(all_pngs_in_folder)}")
        print("This indicates that only a few files successfully generated PNGs.")
        print("\nPOSSIBLE ISSUES:")
        print("1. Most Excel files failed to process (check for errors above)")
        print("2. PNG generation failed for most files")
        print("3. Naming pattern mismatch between generation and search")
        print("4. Subfolders weren't created for most files")
        print("5. Processing stopped early due to errors")
    else:
        print("Successfully opened 6 graphs (3 with vacuum + 3 without vacuum)!")
    print("Compare the patterns to understand why some files were detected and others weren't.")

# Call the function to open random graphs
if len(files) > 0:
    open_random_graphs_for_inspection()
else:
    print("No files processed, skipping graph opening.")


""" 
pattern = f'win_size_sec={win_size_sec}_thr={power_ratio_thresh:.2f}_codet={co_detection_window_sec:.2f}'
pattern = pattern.replace('.', '').replace('=', '_').replace(' ', '')
pngs = sorted(glob.glob(os.path.join(folder, '*', f'{pattern}_graph.png')))

for pngpathname in pngs:
    if sys.platform.startswith('darwin'):
        os.system(f'open "{pngpathname}"')  # macOS
    elif os.name == 'nt':
        os.startfile(pngpathname)           # Windows
    elif os.name == 'posix':
        os.system(f'xdg-open "{pngpathname}"')  # Linux
 """