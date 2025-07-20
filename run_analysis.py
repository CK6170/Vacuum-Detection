import os
from detect_sinusoidal_noise_weights import detect_sinusoidal_noise_weights
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

file = r'D:\Coolers\vacuum_examples\e33eab74-84ae-4ae4-8265-bcdbbe2f5bfa_lc_data.xlsx'
# file = r'D:\Coolers\non_vacuum_examples\50514d5a-3e9f-460c-8bf7-ca3ddc7c85d0_lc_data.xlsx'
win_size_sec = 0.5
power_ratio_thresh = 0.25
co_detection_window_sec = 0.05

# Call the function with all parameters
result = detect_sinusoidal_noise_weights(
    file, win_size_sec, power_ratio_thresh, co_detection_window_sec)

filepath, basename = os.path.split(file)
name, _ = os.path.splitext(basename)
outdir = os.path.join(filepath, name)

# Prepare parameter string for file names
param_str = f'win_size_sec={win_size_sec}_thr={power_ratio_thresh:.2f}_codet={co_detection_window_sec:.2f}'
param_str_filename = param_str.replace('.', '').replace('=', '_').replace(' ', '')

pngname = f'{param_str_filename}_graph.png'
pngpathname = os.path.join(outdir, pngname)

# Open the PNG and show it
img = mpimg.imread(pngpathname)
plt.figure(figsize=(10, 6))
plt.imshow(img)
plt.axis('off')
plt.title('Vacuum Detection Result')
plt.show()
