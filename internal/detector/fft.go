package detector

import (
	"math"

	"gonum.org/v1/gonum/dsp/fourier"
	"sinusoidal-noise-detector/pkg/utils"
)

// FFTAnalyzer handles FFT analysis for sinusoidal detection
type FFTAnalyzer struct {
	fft *fourier.FFT
}

// NewFFTAnalyzer creates a new FFT analyzer
func NewFFTAnalyzer() *FFTAnalyzer {
	return &FFTAnalyzer{}
}

// AnalyzeSegment performs FFT analysis on a data segment and returns detection information
func (fa *FFTAnalyzer) AnalyzeSegment(segment []float64, samplingRate float64, powerThreshold, amplitudeThreshold float64) (bool, float64, float64, float64) {
	if len(segment) == 0 {
		return false, 0, 0, 0
	}

	windowSize := len(segment)

	// Initialize FFT if needed or if window size changed
	if fa.fft == nil {
		fa.fft = fourier.NewFFT(windowSize)
	}

	// Convert to complex128 for FFT
	complexSegment := make([]complex128, windowSize)
	for i, val := range segment {
		complexSegment[i] = complex(val, 0)
	}

	// Perform FFT
	fftResult := fa.fft.Coefficients(nil, complexSegment)

	// Convert to power spectrum
	powerSpectrum := utils.PowerSpectrum(fftResult, windowSize)

	// Convert to one-sided spectrum
	oneSidedSpectrum := utils.OneSidedPowerSpectrum(powerSpectrum)

	// Remove DC component
	spectrumNoDC := utils.RemoveDC(oneSidedSpectrum)

	// Find peak and calculate power ratio
	powerRatio, peakIndex := utils.PowerRatio(spectrumNoDC)
	maxAmplitude := spectrumNoDC[peakIndex]

	// Check detection criteria
	if powerRatio > powerThreshold && maxAmplitude > amplitudeThreshold {
		// Convert bin index to frequency
		frequency := utils.FrequencyBin(peakIndex, samplingRate, windowSize)

		// Get phase at peak frequency from original FFT result
		phase := utils.ComplexAngle(fftResult[peakIndex])

		return true, frequency, phase, powerRatio
	}

	return false, 0, 0, 0
}

// SlidingWindowAnalysis performs sliding window FFT analysis on a complete signal
func (fa *FFTAnalyzer) SlidingWindowAnalysis(signal []float64, samplingRate float64, windowSize int, powerThreshold, amplitudeThreshold float64, minGapSamples int) []DetectionPoint {
	var detections []DetectionPoint
	halfWindow := windowSize / 2
	signalLength := len(signal)

	lastDetectionIndex := -1000000 // Initialize to very negative value

	// Sliding window loop
	for i := halfWindow; i < signalLength-halfWindow; i++ {
		// Skip if too close to previous detection
		if lastDetectionIndex >= 0 && (i-lastDetectionIndex) < minGapSamples {
			continue
		}

		// Extract segment
		segment := signal[i-halfWindow : i+halfWindow+1]

		// Analyze segment
		detected, frequency, phase, powerRatio := fa.AnalyzeSegment(segment, samplingRate, powerThreshold, amplitudeThreshold)

		if detected {
			detections = append(detections, DetectionPoint{
				Index:      i,
				Frequency:  frequency,
				Phase:      phase,
				PowerRatio: powerRatio,
			})
			lastDetectionIndex = i
		}
	}

	return detections
}

// DetectionPoint represents a single detection from FFT analysis
type DetectionPoint struct {
	Index      int     // Sample index
	Frequency  float64 // Dominant frequency in Hz
	Phase      float64 // Phase angle in radians
	PowerRatio float64 // Power ratio (peak/total)
}

// WindowedFFT performs FFT analysis on a windowed signal segment
func WindowedFFT(signal []float64, windowFunc func(int) []float64) []complex128 {
	if len(signal) == 0 {
		return nil
	}

	windowSize := len(signal)
	
	// Apply window function if provided
	windowedSignal := make([]float64, windowSize)
	copy(windowedSignal, signal)
	
	if windowFunc != nil {
		window := windowFunc(windowSize)
		for i := 0; i < windowSize; i++ {
			windowedSignal[i] *= window[i]
		}
	}

	// Convert to complex for FFT
	complexSignal := make([]complex128, windowSize)
	for i, val := range windowedSignal {
		complexSignal[i] = complex(val, 0)
	}

	// Perform FFT
	fft := fourier.NewFFT(windowSize)
	return fft.Coefficients(nil, complexSignal)
}

// HannWindow creates a Hann window function
func HannWindow(size int) []float64 {
	window := make([]float64, size)
	for i := 0; i < size; i++ {
		window[i] = 0.5 * (1 - math.Cos(2*math.Pi*float64(i)/float64(size-1)))
	}
	return window
}

// HammingWindow creates a Hamming window function
func HammingWindow(size int) []float64 {
	window := make([]float64, size)
	for i := 0; i < size; i++ {
		window[i] = 0.54 - 0.46*math.Cos(2*math.Pi*float64(i)/float64(size-1))
	}
	return window
}

// RectangularWindow creates a rectangular (no) window function
func RectangularWindow(size int) []float64 {
	window := make([]float64, size)
	for i := 0; i < size; i++ {
		window[i] = 1.0
	}
	return window
}