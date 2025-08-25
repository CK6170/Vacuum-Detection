package detector

import (
	"fmt"
	"image/color"
	"os"
	"path/filepath"
	"time"

	"github.com/wcharczuk/go-chart/v2"
	"github.com/wcharczuk/go-chart/v2/drawing"
	"sinusoidal-noise-detector/internal/types"
)

// PlotResults creates and saves a visualization of the weight data and detection results
func PlotResults(result *types.DetectionResult, dataset *types.WeightDataSet, outputPath string) error {
	// Prepare time series data
	timestamps := make([]time.Time, len(dataset.Data))
	weight1 := make([]float64, len(dataset.Data))
	weight2 := make([]float64, len(dataset.Data))
	weight3 := make([]float64, len(dataset.Data))
	weight4 := make([]float64, len(dataset.Data))
	totalWeight := make([]float64, len(dataset.Data))

	for i, data := range dataset.Data {
		timestamps[i] = data.Timestamp
		weight1[i] = data.Weight1
		weight2[i] = data.Weight2
		weight3[i] = data.Weight3
		weight4[i] = data.Weight4
		totalWeight[i] = data.TotalWeight()
	}

	// Create chart
	graph := chart.Chart{
		Title: fmt.Sprintf("Weight Sensor Data - %s", result.Filename),
		TitleStyle: chart.Style{
			FontSize: 14,
		},
		Width:  1400,
		Height: 700,
		Background: chart.Style{
			Padding: chart.Box{
				Top:    40,
				Left:   40,
				Right:  40,
				Bottom: 40,
			},
		},
		XAxis: chart.XAxis{
			Name: "Time",
			Style: chart.Style{
				TextRotationDegrees: 45.0,
			},
			ValueFormatter: chart.TimeValueFormatterWithFormat("15:04:05"),
		},
		YAxis: chart.YAxis{
			Name: "Weight (g)",
		},
	}

	// Define colors for each channel
	colors := []color.RGBA{
		{255, 0, 0, 255},   // Red for Weight 1
		{0, 255, 0, 255},   // Green for Weight 2
		{0, 0, 255, 255},   // Blue for Weight 3
		{255, 165, 0, 255}, // Orange for Weight 4
		{0, 0, 0, 255},     // Black for Total Weight
	}

	// Add weight data series
	series := []chart.Series{
		chart.TimeSeries{
			Name:    "Weight 1",
			XValues: timestamps,
			YValues: weight1,
			Style: chart.Style{
				StrokeColor: colors[0],
				StrokeWidth: 1,
			},
		},
		chart.TimeSeries{
			Name:    "Weight 2",
			XValues: timestamps,
			YValues: weight2,
			Style: chart.Style{
				StrokeColor: colors[1],
				StrokeWidth: 1,
			},
		},
		chart.TimeSeries{
			Name:    "Weight 3",
			XValues: timestamps,
			YValues: weight3,
			Style: chart.Style{
				StrokeColor: colors[2],
				StrokeWidth: 1,
			},
		},
		chart.TimeSeries{
			Name:    "Weight 4",
			XValues: timestamps,
			YValues: weight4,
			Style: chart.Style{
				StrokeColor: colors[3],
				StrokeWidth: 1,
			},
		},
		chart.TimeSeries{
			Name:    "Total Weight",
			XValues: timestamps,
			YValues: totalWeight,
			Style: chart.Style{
				StrokeColor: colors[4],
				StrokeWidth: 2,
			},
		},
	}

	// Add detection points as scatter series
	for channel, detections := range result.SinusoidalDetections {
		if len(detections) > 0 {
			detectionTimes := make([]time.Time, len(detections))
			detectionWeights := make([]float64, len(detections))

			for i, detection := range detections {
				detectionTimes[i] = detection.Timestamp
				// Find the weight value at this timestamp
				for j, data := range dataset.Data {
					if data.Timestamp.Equal(detection.Timestamp) {
						detectionWeights[i] = data.GetWeight(channel)
						break
					}
					// If exact match not found, use index-based lookup
					if j == detection.Index && detection.Index < len(dataset.Data) {
						detectionWeights[i] = data.GetWeight(channel)
						break
					}
				}
			}

			// Add detection points series
			series = append(series, chart.TimeSeries{
				Name:    fmt.Sprintf("Detections Ch%d", channel+1),
				XValues: detectionTimes,
				YValues: detectionWeights,
				Style: chart.Style{
					StrokeColor: colors[channel],
					DotColor:    colors[channel],
					DotWidth:    5,
					Show:        true,
				},
			})
		}
	}

	// Add vacuum event markers as annotation series
	if len(result.VacuumEvents) > 0 {
		vacuumTimes := make([]time.Time, len(result.VacuumEvents))
		vacuumMarkers := make([]float64, len(result.VacuumEvents))

		// Find Y range for placing markers
		minY, maxY := findYRange([][]float64{weight1, weight2, weight3, weight4, totalWeight})
		markerY := minY + (maxY-minY)*0.9 // Place markers at 90% of the range

		for i, event := range result.VacuumEvents {
			vacuumTimes[i] = event.Timestamp
			vacuumMarkers[i] = markerY
		}

		series = append(series, chart.TimeSeries{
			Name:    "Vacuum Events",
			XValues: vacuumTimes,
			YValues: vacuumMarkers,
			Style: chart.Style{
				StrokeColor: color.RGBA{255, 0, 0, 255}, // Red
				DotColor:    color.RGBA{255, 0, 0, 255},
				DotWidth:    8,
				Show:        true,
			},
		})
	}

	graph.Series = series

	// Enable legend
	graph.Elements = []chart.Renderable{
		chart.LegendThin(&graph),
	}

	// Save the chart
	file, err := os.Create(outputPath)
	if err != nil {
		return fmt.Errorf("failed to create output file: %w", err)
	}
	defer file.Close()

	err = graph.Render(chart.PNG, file)
	if err != nil {
		return fmt.Errorf("failed to render chart: %w", err)
	}

	fmt.Printf("Saved figure as PNG to: %s\n", outputPath)
	return nil
}

// findYRange finds the minimum and maximum Y values across multiple series
func findYRange(series [][]float64) (float64, float64) {
	if len(series) == 0 {
		return 0, 0
	}

	minY := series[0][0]
	maxY := series[0][0]

	for _, s := range series {
		for _, val := range s {
			if val < minY {
				minY = val
			}
			if val > maxY {
				maxY = val
			}
		}
	}

	return minY, maxY
}

// SaveResultsWithVisualization saves both CSV and visualization for detection results
func SaveResultsWithVisualization(result *types.DetectionResult, dataset *types.WeightDataSet, inputFilename string) error {
	// Create output directory
	dir, basename := filepath.Split(inputFilename)
	name := basename[:len(basename)-len(filepath.Ext(basename))]
	outdir := filepath.Join(dir, name)

	err := os.MkdirAll(outdir, 0755)
	if err != nil {
		return fmt.Errorf("failed to create output directory: %w", err)
	}

	// Create parameter string for filename
	params := result.Parameters
	paramStr := fmt.Sprintf("win_size_sec%.1f_thr%.2f_codet%.2f",
		params.WindowSizeSec, params.PowerRatioThreshold, params.CoDetectionWindowSec)

	// Replace dots with underscores for filename compatibility
	paramStr = replaceChars(paramStr, ".", "")
	paramStr = replaceChars(paramStr, "=", "_")

	// Save visualization
	pngFilename := fmt.Sprintf("%s_graph.png", paramStr)
	pngPath := filepath.Join(outdir, pngFilename)

	err = PlotResults(result, dataset, pngPath)
	if err != nil {
		return fmt.Errorf("failed to save visualization: %w", err)
	}

	return nil
}

// replaceChars replaces all occurrences of old with new in string s
func replaceChars(s, old, new string) string {
	result := ""
	for i := 0; i < len(s); i++ {
		if i <= len(s)-len(old) && s[i:i+len(old)] == old {
			result += new
			i += len(old) - 1
		} else {
			result += string(s[i])
		}
	}
	return result
}

// CreateVerticalLineAnnotation creates a vertical line annotation for vacuum events
func CreateVerticalLineAnnotation(timestamp time.Time, label string) chart.Annotation {
	return chart.Annotation{
		X:     chart.TimeToFloat64(timestamp),
		Style: chart.Style{
			StrokeColor: color.RGBA{255, 0, 0, 255}, // Red
			StrokeWidth: 2,
		},
	}
}

// AddVacuumEventLines adds vertical lines for vacuum events to the chart
func AddVacuumEventLines(graph *chart.Chart, vacuumEvents []types.VacuumEvent) {
	annotations := make([]chart.Annotation, len(vacuumEvents))
	
	for i, event := range vacuumEvents {
		annotations[i] = CreateVerticalLineAnnotation(event.Timestamp, "Vacuum")
	}
	
	graph.Elements = append(graph.Elements, chart.AnnotationSeries{
		Annotations: annotations,
	})
}

// CreateDetectionScatterPoints creates scatter points for detections
func CreateDetectionScatterPoints(detections []types.SinusoidalDetection, weights []float64, channelColor color.RGBA) chart.ContinuousSeries {
	if len(detections) == 0 {
		return chart.ContinuousSeries{}
	}

	xValues := make([]float64, len(detections))
	yValues := make([]float64, len(detections))

	for i, detection := range detections {
		xValues[i] = chart.TimeToFloat64(detection.Timestamp)
		if detection.Index < len(weights) {
			yValues[i] = weights[detection.Index]
		}
	}

	return chart.ContinuousSeries{
		XValues: xValues,
		YValues: yValues,
		Style: chart.Style{
			StrokeColor: channelColor,
			DotColor:    channelColor,
			DotWidth:    5,
			Show:        true,
		},
	}
}