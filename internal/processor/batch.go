package processor

import (
	"fmt"
	"path/filepath"
	"time"

	"sinusoidal-noise-detector/internal/detector"
	"sinusoidal-noise-detector/internal/types"
)

// BatchProcessor handles processing multiple files
type BatchProcessor struct {
	WinSizeSec           float64
	PowerRatioThresh     float64
	CoDetectionWindowSec float64
}

// NewBatchProcessor creates a new batch processor with specified parameters
func NewBatchProcessor(winSizeSec, powerRatioThresh, coDetectionWindowSec float64) *BatchProcessor {
	return &BatchProcessor{
		WinSizeSec:           winSizeSec,
		PowerRatioThresh:     powerRatioThresh,
		CoDetectionWindowSec: coDetectionWindowSec,
	}
}

// ProcessFiles processes multiple Excel files and returns batch results
func (bp *BatchProcessor) ProcessFiles(files []string) (*types.BatchResult, error) {
	startTime := time.Now()

	result := &types.BatchResult{
		TotalFiles: len(files),
		Results:    make([]types.DetectionResult, 0, len(files)),
		Errors:     make([]types.FileError, 0),
	}

	for i, file := range files {
		fmt.Printf("Processing file %d/%d: %s\n", i+1, len(files), filepath.Base(file))

		// Process single file
		detectionResult, err := detector.DetectSinusoidalNoiseWeights(
			file, bp.WinSizeSec, bp.PowerRatioThresh, bp.CoDetectionWindowSec)

		if err != nil {
			// Handle error
			fmt.Printf("❌ Error processing file %d/%d: %s - %v\n", i+1, len(files), filepath.Base(file), err)
			
			fileError := types.FileError{
				Filename: filepath.Base(file),
				FilePath: file,
				Error:    err,
				ErrorType: fmt.Sprintf("%T", err),
			}
			result.Errors = append(result.Errors, fileError)

			// Add failed result
			failedResult := types.DetectionResult{
				Filename:             filepath.Base(file),
				SinusoidalDetections: make([][]types.SinusoidalDetection, 4),
				VacuumTimes:          []time.Time{},
				VacuumEvents:         []types.VacuumEvent{},
				Error:                err,
			}
			result.Results = append(result.Results, failedResult)
		} else {
			// Success
			fmt.Printf("  📊 Detections: %d vacuum events, %d total sinusoidal detections\n",
				len(detectionResult.VacuumEvents), detectionResult.TotalSinusoidalDetections())
			
			result.Results = append(result.Results, *detectionResult)
			result.SuccessfulFiles++

			if detectionResult.HasVacuumEvents() {
				result.FilesWithVacuum++
			} else {
				result.FilesWithoutVacuum++
			}
		}
	}

	result.ProcessingTime = time.Since(startTime)
	return result, nil
}

// PrintSummary prints a comprehensive summary of batch processing results
func (bp *BatchProcessor) PrintSummary(result *types.BatchResult) {
	fmt.Println("\n" + "="*60)
	fmt.Println("SUMMARY OF VACUUM EFFECT DETECTION")
	fmt.Println("="*60)

	fmt.Printf("\n📊 DETECTION PARAMETERS:\n")
	fmt.Printf("  • Window size: %.1f seconds\n", bp.WinSizeSec)
	fmt.Printf("  • Power ratio threshold: %.1f\n", bp.PowerRatioThresh)
	fmt.Printf("  • Co-detection window: %.2f seconds\n", bp.CoDetectionWindowSec)

	fmt.Printf("\n📁 FILES PROCESSED:\n")
	fmt.Printf("  • Files WITH vacuum effects: %d\n", result.FilesWithVacuum)
	fmt.Printf("  • Files WITHOUT vacuum effects: %d\n", result.FilesWithoutVacuum)
	fmt.Printf("  • Total files processed: %d\n", result.TotalFiles)
	fmt.Printf("  • Files with vacuum effects: %d (%.1f%%)\n", 
		result.FilesWithVacuum, float64(result.FilesWithVacuum)/float64(result.TotalFiles)*100)
	fmt.Printf("  • Files without vacuum effects: %d (%.1f%%)\n", 
		result.FilesWithoutVacuum, float64(result.FilesWithoutVacuum)/float64(result.TotalFiles)*100)

	// Error summary
	bp.printErrorSummary(result)

	// Processing summary
	fmt.Printf("\n📊 PROCESSING SUMMARY:\n")
	fmt.Printf("  • Total files processed: %d\n", result.TotalFiles)
	fmt.Printf("  • Successfully processed: %d\n", result.SuccessfulFiles)
	fmt.Printf("  • Failed to process: %d\n", len(result.Errors))
	fmt.Printf("  • Processing time: %v\n", result.ProcessingTime)

	// Sinusoidal detection summary
	totalSinusoidalDetections := 0
	for _, res := range result.Results {
		if res.Error == nil {
			totalSinusoidalDetections += res.TotalSinusoidalDetections()
		}
	}

	fmt.Printf("  • Total sinusoidal detections across all files: %d\n", totalSinusoidalDetections)
	fmt.Printf("  • Detection CSV files saved in individual subdirectories\n")
	fmt.Printf("  • Each CSV contains vacuum events and sinusoidal detections per weight channel\n")

	fmt.Println("\nAll files processed. CSVs saved in their respective subfolders.")
}

// printErrorSummary prints detailed error analysis
func (bp *BatchProcessor) printErrorSummary(result *types.BatchResult) {
	fmt.Println("\n" + "="*60)
	fmt.Println("COMPREHENSIVE ERROR SUMMARY")
	fmt.Println("="*60)

	if len(result.Errors) == 0 {
		fmt.Printf("\n✅ NO ERRORS: All %d files processed successfully!\n", result.TotalFiles)
		return
	}

	fmt.Printf("\n❌ ERRORS FOUND: %d files failed to process\n", len(result.Errors))

	// Group errors by type
	errorTypes := make(map[string][]string)
	for _, fileError := range result.Errors {
		errorType := fileError.ErrorType
		if _, exists := errorTypes[errorType]; !exists {
			errorTypes[errorType] = make([]string, 0)
		}
		errorTypes[errorType] = append(errorTypes[errorType], fileError.Filename)
	}

	fmt.Printf("\n📊 ERROR BREAKDOWN BY TYPE:\n")
	for errorType, filenames := range errorTypes {
		fmt.Printf("  %s: %d files\n", errorType, len(filenames))
	}

	// Common error patterns
	fmt.Printf("\n🔍 COMMON ERROR PATTERNS:\n")
	commonErrors := make(map[string]int)
	for _, fileError := range result.Errors {
		errorMsg := fileError.Error.Error()
		
		// Categorize errors
		if containsAnyIgnoreCase(errorMsg, []string{"memory", "out of memory"}) {
			commonErrors["Memory Issues"]++
		} else if containsAnyIgnoreCase(errorMsg, []string{"file", "not found", "does not exist"}) {
			commonErrors["File Not Found"]++
		} else if containsAnyIgnoreCase(errorMsg, []string{"permission", "access denied"}) {
			commonErrors["Permission Issues"]++
		} else if containsAnyIgnoreCase(errorMsg, []string{"value", "index", "parse"}) {
			commonErrors["Data/Value Errors"]++
		} else if containsAnyIgnoreCase(errorMsg, []string{"excel", "xlsx", "column"}) {
			commonErrors["Excel Format Errors"]++
		} else {
			commonErrors["Other Errors"]++
		}
	}

	for errorCategory, count := range commonErrors {
		fmt.Printf("  %s: %d occurrences\n", errorCategory, count)
	}

	fmt.Printf("\n💡 TROUBLESHOOTING RECOMMENDATIONS:\n")
	if commonErrors["Memory Issues"] > 0 {
		fmt.Println("  • Memory Issues: Close other applications, reduce data size, or process files in smaller batches")
	}
	if commonErrors["File Not Found"] > 0 {
		fmt.Println("  • File Not Found: Check file paths and ensure Excel files are accessible")
	}
	if commonErrors["Permission Issues"] > 0 {
		fmt.Println("  • Permission Issues: Run with appropriate permissions or check folder access")
	}
	if commonErrors["Data/Value Errors"] > 0 {
		fmt.Println("  • Data Errors: Check Excel file format and data integrity")
	}
	if commonErrors["Excel Format Errors"] > 0 {
		fmt.Println("  • Excel Format Errors: Ensure files have proper column names (timestamp, weight_1, weight_2, weight_3, weight_4)")
	}
}

// containsAnyIgnoreCase checks if a string contains any of the given substrings (case insensitive)
func containsAnyIgnoreCase(str string, substrings []string) bool {
	strLower := toLower(str)
	for _, substr := range substrings {
		if contains(strLower, toLower(substr)) {
			return true
		}
	}
	return false
}

// Simple case conversion (basic implementation)
func toLower(s string) string {
	result := make([]rune, len(s))
	for i, r := range s {
		if r >= 'A' && r <= 'Z' {
			result[i] = r + 32
		} else {
			result[i] = r
		}
	}
	return string(result)
}

// Simple substring check
func contains(s, substr string) bool {
	return len(s) >= len(substr) && indexOf(s, substr) >= 0
}

// Simple indexOf implementation
func indexOf(s, substr string) int {
	if len(substr) == 0 {
		return 0
	}
	if len(substr) > len(s) {
		return -1
	}
	
	for i := 0; i <= len(s)-len(substr); i++ {
		match := true
		for j := 0; j < len(substr); j++ {
			if s[i+j] != substr[j] {
				match = false
				break
			}
		}
		if match {
			return i
		}
	}
	return -1
}