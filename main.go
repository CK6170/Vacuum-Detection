package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"

	"weightsinus/pkg/detector"
)

func main() {
	folder := flag.String("folder", ".", "Folder containing .xlsx files")
	winSizeSec := flag.Float64("win", 0.5, "FFT window size in seconds")
	powerRatio := flag.Float64("thr", 0.5, "Dominant power ratio threshold")
	coDetectSec := flag.Float64("codet", 0.5, "Co-detection window in seconds")
	flag.Parse()

	files, err := filepath.Glob(filepath.Join(*folder, "*.xlsx"))
	if err != nil {
		log.Fatalf("failed to list files: %v", err)
	}

	fmt.Printf("Found %d files in %s\n", len(files), *folder)

	var filesWithVacuum []string
	var filesWithoutVacuum []string

	for i, f := range files {
		fmt.Printf("Processing file %d/%d: %s\n", i+1, len(files), filepath.Base(f))
		res, err := detector.DetectFile(f, *winSizeSec, *powerRatio, *coDetectSec)
		if err != nil {
			fmt.Printf("Error processing %s: %v\n", filepath.Base(f), err)
			filesWithoutVacuum = append(filesWithoutVacuum, f)
			continue
		}
		if len(res.VacuumTimes) > 0 {
			filesWithVacuum = append(filesWithVacuum, f)
		} else {
			filesWithoutVacuum = append(filesWithoutVacuum, f)
		}
	}

	if len(files) == 0 {
		fmt.Println("No files processed. Provide a folder with .xlsx files via -folder")
		os.Exit(0)
	}

	fmt.Println()
	fmt.Println("============================================================")
	fmt.Println("SUMMARY OF VACUUM EFFECT DETECTION")
	fmt.Println("============================================================")
	fmt.Printf("\n• Window size: %.2f s\n", *winSizeSec)
	fmt.Printf("• Power ratio threshold: %.2f\n", *powerRatio)
	fmt.Printf("• Co-detection window: %.2f s\n", *coDetectSec)
	fmt.Printf("\n• Files WITH vacuum effects: %d\n", len(filesWithVacuum))
	fmt.Printf("• Files WITHOUT vacuum effects: %d\n", len(filesWithoutVacuum))
	fmt.Printf("• Total files processed: %d\n", len(files))
}

