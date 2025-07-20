import os
import glob
import sys
from detect_sinusoidal_noise_weights import detect_sinusoidal_noise_weights

folder = r'D:\Coolers\vacuum_examples'
win_size_sec = 0.25
power_ratio_thresh = 0.25
co_detection_window_sec = 0.05


files = sorted(glob.glob(os.path.join(folder, '*.xlsx')))

print(f"Found {len(files)} files in {folder}")

for file in files:
    print(f'\nProcessing: {file}')
    detect_sinusoidal_noise_weights(
        file, win_size_sec, power_ratio_thresh, co_detection_window_sec
    )
print("All files processed. PNGs and CSVs saved in their respective subfolders.")

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
