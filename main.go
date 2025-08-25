package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"

	"sinusoidal-noise-detector/internal/detector"
	"sinusoidal-noise-detector/internal/processor"
)

// Build information (set via ldflags during build)
var (
	Version   = "development"
	Commit    = "unknown"
	BuildTime = "unknown"
)

func main() {
	var (
		filePath              = flag.String("file", "", "Path to Excel file to process")
		folderPath            = flag.String("folder", "", "Path to folder containing Excel files to process")
		winSizeSec            = flag.Float64("win-size", 0.5, "Window size for FFT analysis in seconds")
		powerRatioThresh      = flag.Float64("power-ratio", 0.5, "Power ratio threshold for detection")
		coDetectionWindowSec  = flag.Float64("co-detection", 0.5, "Co-detection window in seconds")
		version               = flag.Bool("version", false, "Show version information")
		help                  = flag.Bool("help", false, "Show help message")
	)
	flag.Parse()

	if *version {
		fmt.Printf("Sinusoidal Noise Detector %s\n", Version)
		fmt.Printf("  Commit: %s\n", Commit)
		fmt.Printf("  Built: %s\n", BuildTime)
		return
	}

	if *help || (*filePath == "" && *folderPath == "") {
		fmt.Println("Sinusoidal Noise Detection in Weight Sensor Data")
		fmt.Println("================================================")
		fmt.Printf("Version: %s\n", Version)
		fmt.Println()
		fmt.Println("This program analyzes weight sensor data to detect sinusoidal noise patterns")
		fmt.Println("that may indicate vacuum-related events or mechanical vibrations.")
		fmt.Println()
		fmt.Println("Usage:")
		fmt.Println("  Single file: ./sinusoidal-noise-detector -file path/to/data.xlsx")
		fmt.Println("  Batch mode:  ./sinusoidal-noise-detector -folder path/to/data/")
		fmt.Println()
		flag.PrintDefaults()
		return
	}

	if *filePath != "" {
		// Process single file
		err := processSingleFile(*filePath, *winSizeSec, *powerRatioThresh, *coDetectionWindowSec)
		if err != nil {
			log.Fatalf("Error processing file: %v", err)
		}
	} else if *folderPath != "" {
		// Process all files in folder
		err := processFolderFiles(*folderPath, *winSizeSec, *powerRatioThresh, *coDetectionWindowSec)
		if err != nil {
			log.Fatalf("Error processing folder: %v", err)
		}
	}
}

func processSingleFile(filePath string, winSizeSec, powerRatioThresh, coDetectionWindowSec float64) error {
	fmt.Printf("Processing file: %s\n", filePath)
	
	result, err := detector.DetectSinusoidalNoiseWeights(filePath, winSizeSec, powerRatioThresh, coDetectionWindowSec)
	if err != nil {
		return fmt.Errorf("detection failed: %w", err)
	}

	fmt.Printf("📊 Detections: %d vacuum events, %d total sinusoidal detections\n", 
		len(result.VacuumTimes), result.TotalSinusoidalDetections())
	
	return nil
}

func processFolderFiles(folderPath string, winSizeSec, powerRatioThresh, coDetectionWindowSec float64) error {
	files, err := filepath.Glob(filepath.Join(folderPath, "*.xlsx"))
	if err != nil {
		return fmt.Errorf("failed to find Excel files: %w", err)
	}

	if len(files) == 0 {
		return fmt.Errorf("no Excel files found in %s", folderPath)
	}

	fmt.Printf("Found %d files in %s\n", len(files), folderPath)

	batchProcessor := processor.NewBatchProcessor(winSizeSec, powerRatioThresh, coDetectionWindowSec)
	results, err := batchProcessor.ProcessFiles(files)
	if err != nil {
		return fmt.Errorf("batch processing failed: %w", err)
	}

	batchProcessor.PrintSummary(results)
	return nil
}