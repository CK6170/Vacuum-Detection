package utils

import (
	"math"
	"math/cmplx"
)

// Mean calculates the arithmetic mean of a slice of float64 values
func Mean(values []float64) float64 {
	if len(values) == 0 {
		return 0
	}
	sum := 0.0
	for _, v := range values {
		sum += v
	}
	return sum / float64(len(values))
}

// Median calculates the median of a slice of float64 values
func Median(values []float64) float64 {
	if len(values) == 0 {
		return 0
	}
	
	// Create a copy and sort it
	sorted := make([]float64, len(values))
	copy(sorted, values)
	
	// Simple bubble sort for small arrays (efficient enough for our use case)
	for i := 0; i < len(sorted); i++ {
		for j := i + 1; j < len(sorted); j++ {
			if sorted[i] > sorted[j] {
				sorted[i], sorted[j] = sorted[j], sorted[i]
			}
		}
	}
	
	n := len(sorted)
	if n%2 == 1 {
		return sorted[n/2]
	}
	return (sorted[n/2-1] + sorted[n/2]) / 2
}

// Max returns the maximum value in a slice of float64 values
func Max(values []float64) float64 {
	if len(values) == 0 {
		return 0
	}
	max := values[0]
	for _, v := range values[1:] {
		if v > max {
			max = v
		}
	}
	return max
}

// MaxIndex returns the index of the maximum value in a slice of float64 values
func MaxIndex(values []float64) int {
	if len(values) == 0 {
		return -1
	}
	maxIdx := 0
	maxVal := values[0]
	for i, v := range values[1:] {
		if v > maxVal {
			maxVal = v
			maxIdx = i + 1
		}
	}
	return maxIdx
}

// Sum calculates the sum of a slice of float64 values
func Sum(values []float64) float64 {
	sum := 0.0
	for _, v := range values {
		sum += v
	}
	return sum
}

// Abs returns the absolute value of a float64
func Abs(x float64) float64 {
	if x < 0 {
		return -x
	}
	return x
}

// NormalizeAngle normalizes an angle to the range [0, 2π)
func NormalizeAngle(angle float64) float64 {
	for angle < 0 {
		angle += 2 * math.Pi
	}
	for angle >= 2*math.Pi {
		angle -= 2 * math.Pi
	}
	return angle
}

// AngleDifference calculates the absolute difference between two angles
// considering the circular nature of angles
func AngleDifference(angle1, angle2 float64) float64 {
	diff := math.Abs(angle1 - angle2)
	if diff > math.Pi {
		diff = 2*math.Pi - diff
	}
	return diff
}

// IsAntiPhase checks if two angles are approximately anti-phase (differ by ~π)
func IsAntiPhase(angle1, angle2, threshold float64) bool {
	phaseDiff := AngleDifference(angle1, angle2)
	return math.Abs(phaseDiff-math.Pi) < threshold
}

// ComplexAngle returns the angle of a complex number
func ComplexAngle(c complex128) float64 {
	return cmplx.Phase(c)
}

// PowerSpectrum converts a complex FFT result to a power spectrum
func PowerSpectrum(fft []complex128, windowSize int) []float64 {
	n := len(fft)
	power := make([]float64, n)
	
	for i := 0; i < n; i++ {
		power[i] = cmplx.Abs(fft[i]) / float64(windowSize)
	}
	
	return power
}

// OneSidedPowerSpectrum converts a two-sided power spectrum to one-sided
func OneSidedPowerSpectrum(twoSided []float64) []float64 {
	n := len(twoSided)
	oneSided := make([]float64, n/2+1)
	
	oneSided[0] = twoSided[0] // DC component
	for i := 1; i < len(oneSided)-1; i++ {
		oneSided[i] = 2 * twoSided[i] // Double the magnitude (except DC and Nyquist)
	}
	if len(oneSided) > 1 {
		oneSided[len(oneSided)-1] = twoSided[len(oneSided)-1] // Nyquist frequency
	}
	
	return oneSided
}

// RemoveDC removes the DC component (index 0) from a power spectrum
func RemoveDC(spectrum []float64) []float64 {
	result := make([]float64, len(spectrum))
	copy(result, spectrum)
	if len(result) > 0 {
		result[0] = 0
	}
	return result
}

// FrequencyBin converts a frequency bin index to actual frequency
func FrequencyBin(bin int, samplingRate float64, windowSize int) float64 {
	return float64(bin) * samplingRate / float64(windowSize)
}

// PowerRatio calculates the ratio of peak power to total power
func PowerRatio(spectrum []float64) (float64, int) {
	if len(spectrum) == 0 {
		return 0, -1
	}
	
	maxVal := spectrum[0]
	maxIdx := 0
	total := spectrum[0]
	
	for i := 1; i < len(spectrum); i++ {
		if spectrum[i] > maxVal {
			maxVal = spectrum[i]
			maxIdx = i
		}
		total += spectrum[i]
	}
	
	if total == 0 {
		return 0, maxIdx
	}
	
	return maxVal / total, maxIdx
}

// SpikeCorrection corrects measurement spikes in weight data
// If neighbors are stable (difference < threshold) but center point deviates significantly,
// replace the spike with average of neighbors
func SpikeCorrection(data []float64, neighborThreshold, spikeThreshold float64) []float64 {
	if len(data) < 3 {
		return data
	}
	
	corrected := make([]float64, len(data))
	copy(corrected, data)
	
	for i := 1; i < len(data)-1; i++ {
		prev, next, center := data[i-1], data[i+1], data[i]
		
		// Check if neighboring points are stable
		if math.Abs(prev-next) < neighborThreshold {
			neighborAvg := (prev + next) / 2
			
			// If center point is a spike
			if math.Abs(center-neighborAvg) > spikeThreshold {
				corrected[i] = neighborAvg
			}
		}
	}
	
	return corrected
}