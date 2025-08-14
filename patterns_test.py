import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.signal import correlate

# Generate data
x = np.linspace(0, 2 * np.pi, 100)
wave_pattern = np.sin(x)  # Wavy pattern
diagonal_line = np.linspace(-1, 1, 100)  # Straight diagonal line

# Derivative (Rate of Change)
derivative_wave = np.gradient(wave_pattern)
derivative_diagonal = np.gradient(diagonal_line)

print(derivative_wave)
print(derivative_diagonal)


# Plotting additional metrics: Derivative (Rate of Change) and RMS

plt.figure(figsize=(12, 8))

# Plot Derivative
plt.subplot(3, 2, 1)
plt.plot(x, derivative_wave, label="Wave Derivative")
plt.title("Wave Pattern Derivative")

plt.subplot(3, 2, 2)
plt.plot(x, derivative_diagonal, label="Diagonal Derivative", color='r')
plt.title("Diagonal Line Derivative")

# # Plot RMS as a bar chart
# plt.subplot(3, 2, 3)
# plt.bar(['Wave', 'Diagonal'], [rms_wave, rms_diagonal])
# plt.title("Root Mean Square (RMS)")

# Plotting the original wave and diagonal for context
plt.subplot(3, 2, 3)
plt.plot(x, wave_pattern, label="Wave Pattern")
plt.title("Wave Pattern")

plt.subplot(3, 2, 4)
plt.plot(x, diagonal_line, label="Diagonal Line", color='r')
plt.title("Diagonal Line")

plt.tight_layout()
plt.show()




##############




# # Variance
# variance_wave = np.var(wave_pattern)
# variance_diagonal = np.var(diagonal_line)
#
# # Fourier Transform (Frequency analysis)
# fft_wave = fft(wave_pattern)
# fft_diagonal = fft(diagonal_line)
#
# # Autocorrelation
# autocorr_wave = correlate(wave_pattern, wave_pattern)
# autocorr_diagonal = correlate(diagonal_line, diagonal_line)
#
# # Root Mean Square (RMS)
# rms_wave = np.sqrt(np.mean(wave_pattern**2))
# rms_diagonal = np.sqrt(np.mean(diagonal_line**2))
#
# # Plot the patterns
# plt.figure(figsize=(12, 8))
#
# # Plot wave pattern and diagonal line
# plt.subplot(3, 2, 1)
# plt.plot(x, wave_pattern, label="Wave Pattern")
# plt.title("Wave Pattern")
#
# plt.subplot(3, 2, 2)
# plt.plot(x, diagonal_line, label="Diagonal Line", color='r')
# plt.title("Diagonal Line")
#
# # Plot variance
# plt.subplot(3, 2, 3)
# plt.bar(['Wave', 'Diagonal'], [variance_wave, variance_diagonal])
# plt.title("Variance")
#
# # Plot FFT magnitudes
# plt.subplot(3, 2, 4)
# plt.plot(np.abs(fft_wave), label="Wave FFT")
# plt.plot(np.abs(fft_diagonal), label="Diagonal FFT", color='r')
# plt.title("Fourier Transform")
#
# # Plot autocorrelation
# plt.subplot(3, 2, 5)
# plt.plot(autocorr_wave, label="Wave Autocorr")
# plt.title("Autocorrelation: Wave")
#
# plt.subplot(3, 2, 6)
# plt.plot(autocorr_diagonal, label="Diagonal Autocorr", color='r')
# plt.title("Autocorrelation: Diagonal")
#
# plt.tight_layout()
# plt.show()
#
# # Output the metrics
# {
#     "Variance": {"Wave": variance_wave, "Diagonal": variance_diagonal},
#     "RMS": {"Wave": rms_wave, "Diagonal": rms_diagonal}
# }


# # Plotting additional metrics: Derivative (Rate of Change) and RMS
#
# plt.figure(figsize=(12, 8))
#
# # Plot Derivative
# plt.subplot(3, 2, 1)
# plt.plot(x, derivative_wave, label="Wave Derivative")
# plt.title("Wave Pattern Derivative")
#
# plt.subplot(3, 2, 2)
# plt.plot(x, derivative_diagonal, label="Diagonal Derivative", color='r')
# plt.title("Diagonal Line Derivative")
#
# # Plot RMS as a bar chart
# plt.subplot(3, 2, 3)
# plt.bar(['Wave', 'Diagonal'], [rms_wave, rms_diagonal])
# plt.title("Root Mean Square (RMS)")
#
# # Plotting the original wave and diagonal for context
# plt.subplot(3, 2, 4)
# plt.plot(x, wave_pattern, label="Wave Pattern")
# plt.title("Wave Pattern")
#
# plt.subplot(3, 2, 5)
# plt.plot(x, diagonal_line, label="Diagonal Line", color='r')
# plt.title("Diagonal Line")
#
# plt.tight_layout()
# plt.show()