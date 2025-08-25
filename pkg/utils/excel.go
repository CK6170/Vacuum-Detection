package utils

import (
	"fmt"
	"strconv"
	"time"

	"github.com/xuri/excelize/v2"
	"sinusoidal-noise-detector/internal/types"
)

// ReadExcelWeightData reads weight sensor data from an Excel file
func ReadExcelWeightData(filename string) (*types.WeightDataSet, error) {
	// Open Excel file
	f, err := excelize.OpenFile(filename)
	if err != nil {
		return nil, fmt.Errorf("failed to open Excel file: %w", err)
	}
	defer f.Close()

	// Get the first sheet name
	sheetName := f.GetSheetName(0)
	if sheetName == "" {
		return nil, fmt.Errorf("no sheets found in Excel file")
	}

	// Get all rows
	rows, err := f.GetRows(sheetName)
	if err != nil {
		return nil, fmt.Errorf("failed to read rows: %w", err)
	}

	if len(rows) < 2 {
		return nil, fmt.Errorf("insufficient data: need at least header + 1 data row")
	}

	// Find column indices
	header := rows[0]
	timestampCol, weight1Col, weight2Col, weight3Col, weight4Col := -1, -1, -1, -1, -1

	for i, colName := range header {
		switch colName {
		case "timestamp":
			timestampCol = i
		case "weight_1":
			weight1Col = i
		case "weight_2":
			weight2Col = i
		case "weight_3":
			weight3Col = i
		case "weight_4":
			weight4Col = i
		}
	}

	// Validate required columns
	if timestampCol == -1 {
		return nil, fmt.Errorf("column 'timestamp' not found")
	}
	if weight1Col == -1 || weight2Col == -1 || weight3Col == -1 || weight4Col == -1 {
		return nil, fmt.Errorf("one or more weight columns (weight_1, weight_2, weight_3, weight_4) not found")
	}

	// Parse data rows
	var data []types.WeightData
	var timestamps []time.Time

	for i, row := range rows[1:] { // Skip header
		if len(row) <= timestampCol || len(row) <= weight1Col || 
		   len(row) <= weight2Col || len(row) <= weight3Col || len(row) <= weight4Col {
			continue // Skip incomplete rows
		}

		// Parse timestamp
		timestampStr := row[timestampCol]
		timestamp, err := parseTimestamp(timestampStr)
		if err != nil {
			return nil, fmt.Errorf("failed to parse timestamp in row %d: %w", i+2, err)
		}

		// Parse weight values
		weight1, err := parseFloat(row[weight1Col])
		if err != nil {
			return nil, fmt.Errorf("failed to parse weight_1 in row %d: %w", i+2, err)
		}

		weight2, err := parseFloat(row[weight2Col])
		if err != nil {
			return nil, fmt.Errorf("failed to parse weight_2 in row %d: %w", i+2, err)
		}

		weight3, err := parseFloat(row[weight3Col])
		if err != nil {
			return nil, fmt.Errorf("failed to parse weight_3 in row %d: %w", i+2, err)
		}

		weight4, err := parseFloat(row[weight4Col])
		if err != nil {
			return nil, fmt.Errorf("failed to parse weight_4 in row %d: %w", i+2, err)
		}

		data = append(data, types.WeightData{
			Timestamp: timestamp,
			Weight1:   weight1,
			Weight2:   weight2,
			Weight3:   weight3,
			Weight4:   weight4,
		})
		timestamps = append(timestamps, timestamp)
	}

	if len(data) < 2 {
		return nil, fmt.Errorf("insufficient data: need at least 2 data points")
	}

	// Calculate sampling rate from timestamp differences
	timeDiffs := make([]float64, 0, len(timestamps)-1)
	for i := 1; i < len(timestamps); i++ {
		diff := timestamps[i].Sub(timestamps[i-1]).Seconds()
		if diff > 0 {
			timeDiffs = append(timeDiffs, diff)
		}
	}

	if len(timeDiffs) == 0 {
		return nil, fmt.Errorf("unable to calculate sampling rate: no valid time differences")
	}

	// Use median time difference for robust sampling rate estimation
	medianDt := Median(timeDiffs)
	samplingRate := 1.0 / medianDt

	// Calculate zero references (baseline correction) from first few samples
	const zeroingSamples = 20
	zeroRefs := [4]float64{}
	numSamples := len(data)
	samplesForZeroing := zeroingSamples
	if numSamples < zeroingSamples {
		samplesForZeroing = numSamples
	}

	for ch := 0; ch < 4; ch++ {
		sum := 0.0
		for i := 0; i < samplesForZeroing; i++ {
			sum += data[i].GetWeight(ch)
		}
		zeroRefs[ch] = sum / float64(samplesForZeroing)
	}

	// Apply zero reference correction and spike correction to all data
	for i := range data {
		for ch := 0; ch < 4; ch++ {
			originalValue := data[i].GetWeight(ch)
			correctedValue := originalValue - zeroRefs[ch]
			data[i].SetWeight(ch, correctedValue)
		}
	}

	// Apply spike correction to each channel
	for ch := 0; ch < 4; ch++ {
		// Extract channel data
		channelData := make([]float64, len(data))
		for i := range data {
			channelData[i] = data[i].GetWeight(ch)
		}

		// Apply spike correction
		correctedData := SpikeCorrection(channelData, 10.0, 200.0)

		// Put corrected data back
		for i := range data {
			data[i].SetWeight(ch, correctedData[i])
		}
	}

	return &types.WeightDataSet{
		Data:           data,
		SamplingRate:   samplingRate,
		TotalSamples:   len(data),
		ZeroReferences: zeroRefs,
	}, nil
}

// parseTimestamp attempts to parse various timestamp formats
func parseTimestamp(timestampStr string) (time.Time, error) {
	// Common timestamp formats to try
	formats := []string{
		"2006-01-02 15:04:05",
		"2006-01-02T15:04:05",
		"2006-01-02 15:04:05.000",
		"2006-01-02T15:04:05.000",
		"2006-01-02 15:04:05.000000",
		"2006-01-02T15:04:05.000000",
		"01/02/2006 15:04:05",
		"01-02-2006 15:04:05",
		"2006/01/02 15:04:05",
		time.RFC3339,
		time.RFC3339Nano,
	}

	for _, format := range formats {
		if t, err := time.Parse(format, timestampStr); err == nil {
			return t, nil
		}
	}

	return time.Time{}, fmt.Errorf("unable to parse timestamp: %s", timestampStr)
}

// parseFloat parses a string to float64, handling various number formats
func parseFloat(s string) (float64, error) {
	if s == "" {
		return 0, fmt.Errorf("empty string")
	}
	
	f, err := strconv.ParseFloat(s, 64)
	if err != nil {
		return 0, fmt.Errorf("invalid number format: %s", s)
	}
	
	return f, nil
}