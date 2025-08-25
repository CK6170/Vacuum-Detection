package types

import (
	"time"
)

// WeightData represents a single row of weight sensor data
type WeightData struct {
	Timestamp time.Time
	Weight1   float64
	Weight2   float64
	Weight3   float64
	Weight4   float64
}

// WeightDataSet represents the complete dataset from an Excel file
type WeightDataSet struct {
	Data           []WeightData
	SamplingRate   float64
	TotalSamples   int
	ZeroReferences [4]float64 // Zero reference for each weight channel
}

// SinusoidalDetection represents a single sinusoidal pattern detection
type SinusoidalDetection struct {
	Index           int       // Sample index where detection occurred
	Timestamp       time.Time // Timestamp of detection
	Frequency       float64   // Dominant frequency in Hz
	Phase           float64   // Phase angle in radians
	PowerRatio      float64   // Ratio of peak power to total power
	Channel         int       // Weight channel (0-3)
}

// VacuumEvent represents a detected vacuum event with anti-phase behavior
type VacuumEvent struct {
	Timestamp       time.Time                 // Time when vacuum event was detected
	Pairs           [][2]int                  // Sensor pairs involved (e.g., [[0,3], [1,2]])
	Detections      []SinusoidalDetection     // Contributing sinusoidal detections
}

// DetectionResult contains all analysis results for a single file
type DetectionResult struct {
	Filename                string                   // Input filename
	SinusoidalDetections    [][]SinusoidalDetection  // Detections per channel [4][]
	VacuumTimes             []time.Time              // Timestamps of vacuum events
	VacuumEvents            []VacuumEvent            // Detailed vacuum event information
	Parameters              DetectionParameters      // Parameters used for detection
	ProcessingTime          time.Duration            // Time taken to process
	Error                   error                    // Any error that occurred
}

// DetectionParameters holds the configuration for detection algorithm
type DetectionParameters struct {
	WindowSizeSec           float64  // FFT window size in seconds
	PowerRatioThreshold     float64  // Minimum power ratio for detection
	CoDetectionWindowSec    float64  // Time window for considering detections simultaneous
	PhaseDifferenceThresh   float64  // Threshold for anti-phase detection (radians)
	FrequencyTolerance      float64  // Frequency matching tolerance (Hz)
	MinimumAmplitude        float64  // Minimum amplitude threshold
	ZeroingSamples          int      // Number of samples for zero reference calculation
	MinGapSamples           int      // Minimum gap between detections to prevent clustering
}

// DefaultDetectionParameters returns the default detection parameters
func DefaultDetectionParameters() DetectionParameters {
	return DetectionParameters{
		WindowSizeSec:           0.5,
		PowerRatioThreshold:     0.5,
		CoDetectionWindowSec:    0.5,
		PhaseDifferenceThresh:   3.14159 / 1.1, // ~163°
		FrequencyTolerance:      0.1,
		MinimumAmplitude:        10.0,
		ZeroingSamples:          20,
		MinGapSamples:           0, // Will be calculated based on CoDetectionWindowSec
	}
}

// TotalSinusoidalDetections returns the total number of sinusoidal detections across all channels
func (dr *DetectionResult) TotalSinusoidalDetections() int {
	total := 0
	for _, channelDetections := range dr.SinusoidalDetections {
		total += len(channelDetections)
	}
	return total
}

// HasVacuumEvents returns true if any vacuum events were detected
func (dr *DetectionResult) HasVacuumEvents() bool {
	return len(dr.VacuumEvents) > 0
}

// BatchResult contains results from processing multiple files
type BatchResult struct {
	TotalFiles          int
	SuccessfulFiles     int
	FilesWithVacuum     int
	FilesWithoutVacuum  int
	Results             []DetectionResult
	Errors              []FileError
	ProcessingTime      time.Duration
}

// FileError represents an error that occurred while processing a specific file
type FileError struct {
	Filename    string
	FilePath    string
	Error       error
	ErrorType   string
}

// WeightChannelNames provides human-readable names for weight channels
var WeightChannelNames = [4]string{"Weight 1", "Weight 2", "Weight 3", "Weight 4"}

// GetWeights returns the weight values for all 4 channels at a given index
func (wd *WeightData) GetWeights() [4]float64 {
	return [4]float64{wd.Weight1, wd.Weight2, wd.Weight3, wd.Weight4}
}

// TotalWeight returns the sum of all weight measurements
func (wd *WeightData) TotalWeight() float64 {
	return wd.Weight1 + wd.Weight2 + wd.Weight3 + wd.Weight4
}

// GetWeight returns the weight value for a specific channel (0-3)
func (wd *WeightData) GetWeight(channel int) float64 {
	switch channel {
	case 0:
		return wd.Weight1
	case 1:
		return wd.Weight2
	case 2:
		return wd.Weight3
	case 3:
		return wd.Weight4
	default:
		return 0.0
	}
}

// SetWeight sets the weight value for a specific channel (0-3)
func (wd *WeightData) SetWeight(channel int, value float64) {
	switch channel {
	case 0:
		wd.Weight1 = value
	case 1:
		wd.Weight2 = value
	case 2:
		wd.Weight3 = value
	case 3:
		wd.Weight4 = value
	}
}