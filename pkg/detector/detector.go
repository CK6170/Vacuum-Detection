package detector

import (
	"encoding/csv"
	"errors"
	"fmt"
	"math"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/xuri/excelize/v2"
	"gonum.org/v1/gonum/dsp/fourier"
	"gonum.org/v1/plot"
	"gonum.org/v1/plot/plotter"
	"gonum.org/v1/plot/plotutil"
	"gonum.org/v1/plot/vg"
)

type DetectionResult struct {
	SinusoidTimes   [][]time.Time
	SinusoidIndices [][]int
	DomFreqs        [][]float64
	DomPhases       [][]float64
	VacuumTimes     []time.Time
	OutDir          string
	PNGPath         string
	CSVPath         string
}

func DetectFile(filename string, winSizeSec, powerRatioThresh, coDetectionWindowSec float64) (*DetectionResult, error) {
	fmt.Printf("Processing file: %s\n", filename)

	// Read data
	times, weights, err := readExcelWeights(filename)
	if err != nil {
		return nil, fmt.Errorf("read excel: %w", err)
	}
	N := len(times)
	if N < 2 {
		return nil, errors.New("not enough samples to determine sampling frequency")
	}

	// Estimate sampling frequency
	var dts []float64
	for i := 1; i < N; i++ {
		dts = append(dts, times[i].Sub(times[i-1]).Seconds())
	}
	fs := 1.0 / median(dts)
	fmt.Printf("Estimated fs: %.3f Hz\n", fs)

	// Window sizes
	winSize := int(math.Round(winSizeSec * fs))
	if winSize < 3 {
		winSize = 3
	}
	if winSize%2 == 0 { // ensure odd so center sample exists
		winSize++
	}
	halfWin := winSize / 2
	fmt.Printf("FFT window: %d samples (%.2f s)\n", winSize, winSizeSec)

	// Preprocess weights: zeroing and spike correction
	const nChan = 4
	zeroingSamples := minInt(20, N)
	weightsCorr := make([][]float64, nChan)
	totalWeight := make([]float64, N)
	for ch := 0; ch < nChan; ch++ {
		w := make([]float64, N)
		copy(w, weights[ch])
		var zsum float64
		for i := 0; i < zeroingSamples; i++ {
			zsum += w[i]
		}
		zeroRef := zsum / float64(zeroingSamples)
		for i := 0; i < N; i++ {
			w[i] -= zeroRef
		}
		wCorr := make([]float64, N)
		copy(wCorr, w)
		for i := 1; i < N-1; i++ {
			pre, post, center := w[i-1], w[i+1], w[i]
			if math.Abs(pre-post) < 10 {
				neighborAvg := 0.5 * (pre + post)
				if math.Abs(center-neighborAvg) > 200 {
					wCorr[i] = neighborAvg
				}
			}
		}
		weightsCorr[ch] = wCorr
	}
	for i := 0; i < N; i++ {
		var s float64
		for ch := 0; ch < nChan; ch++ {
			s += weightsCorr[ch][i]
		}
		totalWeight[i] = s
	}

	// Sinusoidal detection per channel
	sinusoidTimes := make([][]time.Time, nChan)
	sinusoidIndices := make([][]int, nChan)
	domFreqs := make([][]float64, nChan)
	domPhases := make([][]float64, nChan)

	minGapSamples := int(math.Round(coDetectionWindowSec * fs))
	fft := fourier.NewFFT(winSize)

	for ch := 0; ch < nChan; ch++ {
		sig := weightsCorr[ch]
		var sIdx []int
		var sFreq []float64
		var sPhase []float64
		lastDetection := -1_000_000_000

		for i := halfWin; i < N-halfWin; i++ {
			if len(sIdx) > 0 && (i-lastDetection) < minGapSamples {
				continue
			}
			segment := make([]float64, winSize)
			copy(segment, sig[i-halfWin:i+halfWin+1])
			Y := fft.Coefficients(nil, segment)
			P2 := make([]float64, winSize)
			for k := 0; k < winSize; k++ {
				P2[k] = cmplxAbs(Y[k]) / float64(winSize)
			}
			m := winSize/2 + 1
			P1 := make([]float64, m)
			copy(P1, P2[:m])
			for k := 1; k < m-1; k++ {
				P1[k] *= 2
			}
			P1[0] = 0
			maxVal := 0.0
			idxPeak := 0
			sumPow := 1e-12
			for k := 0; k < m; k++ {
				sumPow += P1[k]
				if P1[k] > maxVal {
					maxVal = P1[k]
					idxPeak = k
				}
			}
			ratio := maxVal / sumPow
			if ratio > powerRatioThresh && maxVal > 10 {
				sIdx = append(sIdx, i)
				freq := float64(idxPeak) * fs / float64(winSize)
				sFreq = append(sFreq, freq)
				phase := math.Atan2(imag(Y[idxPeak]), real(Y[idxPeak]))
				sPhase = append(sPhase, phase)
				lastDetection = i
			}
		}

		sinusoidIndices[ch] = sIdx
		st := make([]time.Time, len(sIdx))
		for ii := range sIdx {
			st[ii] = times[sIdx[ii]]
		}
		sinusoidTimes[ch] = st
		domFreqs[ch] = sFreq
		domPhases[ch] = sPhase
	}

	// Build master list of detections
	var allTimes []time.Time
	var chanForTime []int
	var detIdxForTime []int
	for ch := 0; ch < nChan; ch++ {
		for i := range sinusoidTimes[ch] {
			allTimes = append(allTimes, sinusoidTimes[ch][i])
			chanForTime = append(chanForTime, ch)
			detIdxForTime = append(detIdxForTime, i)
		}
	}
	idx := make([]int, len(allTimes))
	for i := range idx { idx[i] = i }
	sort.Slice(idx, func(i, j int) bool { return allTimes[idx[i]].Before(allTimes[idx[j]]) })
	var allTimesSorted []time.Time
	var chanSorted []int
	var detIdxSorted []int
	for _, k := range idx {
		allTimesSorted = append(allTimesSorted, allTimes[k])
		chanSorted = append(chanSorted, chanForTime[k])
		detIdxSorted = append(detIdxSorted, detIdxForTime[k])
	}

	phaseDiffThresh := math.Pi / 1.1
	freqTol := 0.1
	var vacuumTimes []time.Time

	for i := 0; i < len(allTimesSorted); i++ {
		ref := allTimesSorted[i]
		var closeIdx []int
		for j := 0; j < len(allTimesSorted); j++ {
			if math.Abs(allTimesSorted[j].Sub(ref).Seconds()) <= coDetectionWindowSec/2.0 {
				closeIdx = append(closeIdx, j)
			}
		}
		chanInfoDet := make([]struct{ det bool; freq, phase float64 }, nChan)
		for ch := 0; ch < nChan; ch++ {
			for _, ci := range closeIdx {
				if chanSorted[ci] == ch {
					idxDet := detIdxSorted[ci]
					chanInfoDet[ch] = struct{ det bool; freq, phase float64 }{true, domFreqs[ch][idxDet], domPhases[ch][idxDet]}
					break
				}
			}
		}
		found14 := false
		if chanInfoDet[0].det && chanInfoDet[3].det && math.Abs(chanInfoDet[0].freq-chanInfoDet[3].freq) < freqTol {
			pdiff := math.Abs(angleDiff(chanInfoDet[0].phase, chanInfoDet[3].phase))
			if math.Abs(pdiff-math.Pi) < phaseDiffThresh { found14 = true }
		}
		found23 := false
		if chanInfoDet[1].det && chanInfoDet[2].det && math.Abs(chanInfoDet[1].freq-chanInfoDet[2].freq) < freqTol {
			pdiff := math.Abs(angleDiff(chanInfoDet[1].phase, chanInfoDet[2].phase))
			if math.Abs(pdiff-math.Pi) < phaseDiffThresh { found23 = true }
		}
		if found14 && found23 {
			if len(vacuumTimes) == 0 || math.Abs(ref.Sub(vacuumTimes[len(vacuumTimes)-1]).Seconds()) > 0.1 {
				vacuumTimes = append(vacuumTimes, ref)
				fmt.Printf("Antiphase (same freq) at %s: W1/W4 and W2/W3\n", ref.Format(time.RFC3339Nano))
			}
		}
	}

	// Create output directory and save plot/csv
	filepathDir, base := filepath.Split(filename)
	name := strings.TrimSuffix(base, filepath.Ext(base))
	outdir := filepath.Join(filepathDir, name)
	if err := os.MkdirAll(outdir, 0o755); err != nil {
		return nil, fmt.Errorf("mkdir outdir: %w", err)
	}
	paramStr := fmt.Sprintf("win_size_sec=%.2f_thr=%.2f_codet=%.2f", winSizeSec, powerRatioThresh, coDetectionWindowSec)
	paramStrFilename := sanitizeParam(paramStr)
	pngPath := filepath.Join(outdir, fmt.Sprintf("%s_graph.png", paramStrFilename))
	if err := savePlot(times, weightsCorr, totalWeight, sinusoidIndices, vacuumTimes, pngPath); err != nil {
		return nil, fmt.Errorf("save plot: %w", err)
	}
	csvPath := filepath.Join(outdir, fmt.Sprintf("%s_detections.csv", paramStrFilename))
	if err := saveCSV(csvPath, vacuumTimes, sinusoidTimes, domFreqs, domPhases); err != nil {
		return nil, fmt.Errorf("save csv: %w", err)
	}
	fmt.Printf("Saved figure as PNG to: %s\n", pngPath)
	fmt.Printf("Saved enhanced detection summary to: %s\n", csvPath)

	return &DetectionResult{
		SinusoidTimes:   sinusoidTimes,
		SinusoidIndices: sinusoidIndices,
		DomFreqs:        domFreqs,
		DomPhases:       domPhases,
		VacuumTimes:     vacuumTimes,
		OutDir:          outdir,
		PNGPath:         pngPath,
		CSVPath:         csvPath,
	}, nil
}

func saveCSV(csvPath string, vacuumTimes []time.Time, sinusoidTimes [][]time.Time, domFreqs [][]float64, domPhases [][]float64) error {
	f, err := os.Create(csvPath)
	if err != nil { return err }
	defer f.Close()
	w := csv.NewWriter(f)
	defer w.Flush()
	header := []string{"detection_type","timestamp","weight_1_detection","weight_2_detection","weight_3_detection","weight_4_detection","frequency_hz","phase_radians","phase_degrees"}
	if err := w.Write(header); err != nil { return err }
	for _, vt := range vacuumTimes {
		row := []string{"vacuum_event", vt.Format(time.RFC3339Nano), "", "", "", "", "", "", ""}
		if err := w.Write(row); err != nil { return err }
	}
	for ch := 0; ch < 4; ch++ {
		if len(sinusoidTimes[ch]) == 0 { continue }
		for i := range sinusoidTimes[ch] {
			row := make([]string, len(header))
			row[0] = fmt.Sprintf("sinusoidal_weight_%d", ch+1)
			row[1] = sinusoidTimes[ch][i].Format(time.RFC3339Nano)
			for k := 0; k < 4; k++ { if k == ch { row[2+k] = row[1] } else { row[2+k] = "" } }
			row[6] = fmt.Sprintf("%.3f", domFreqs[ch][i])
			row[7] = fmt.Sprintf("%.3f", domPhases[ch][i])
			row[8] = fmt.Sprintf("%.1f", domPhases[ch][i]*180/math.Pi)
			if err := w.Write(row); err != nil { return err }
		}
	}
	return nil
}

func savePlot(times []time.Time, weightsCorr [][]float64, totalWeight []float64, sinusoidIndices [][]int, vacuumTimes []time.Time, pngPath string) error {
	p := plot.New()
	p.Title.Text = filepath.Base(pngPath)
	p.X.Label.Text = "Timestamp"
	p.Y.Label.Text = "Weight (g)"
	// Use time ticks on X
	p.X.Tick.Marker = plot.TimeTicks{Format: "15:04:05"}

	minY, maxY := math.Inf(1), math.Inf(-1)
	for ch := 0; ch < 4; ch++ {
		for _, v := range weightsCorr[ch] {
			if v < minY { minY = v }
			if v > maxY { maxY = v }
		}
	}
	for _, v := range totalWeight { if v < minY { minY = v }; if v > maxY { maxY = v } }
	if !isFinite(minY) || !isFinite(maxY) || minY == maxY {
		minY, maxY = -1, 1
	}

	// Plot channel lines
	colors := plotutil.SoftColors
	for ch := 0; ch < 4; ch++ {
		pts := make(plotter.XYs, len(times))
		for i := range times {
			pts[i].X = float64(times[i].UnixNano()) / 1e9
			pts[i].Y = weightsCorr[ch][i]
		}
		l, err := plotter.NewLine(pts)
		if err != nil { return err }
		l.LineStyle.Width = vg.Points(1)
		l.LineStyle.Color = colors[ch%len(colors)]
		p.Add(l)
		label := fmt.Sprintf("Weight %d", ch+1)
		p.Legend.Add(label, l)

		// Detection markers
		if len(sinusoidIndices[ch]) > 0 {
			mpts := make(plotter.XYs, len(sinusoidIndices[ch]))
			for j, idx := range sinusoidIndices[ch] {
				mpts[j].X = float64(times[idx].UnixNano()) / 1e9
				mpts[j].Y = weightsCorr[ch][idx]
			}
			s, err := plotter.NewScatter(mpts)
			if err != nil { return err }
			s.GlyphStyle.Color = colors[ch%len(colors)]
			s.GlyphStyle.Radius = vg.Points(2.5)
			p.Add(s)

			// Vertical lines at detection times
			for _, idx := range sinusoidIndices[ch] {
				vpts := plotter.XYs{{X: float64(times[idx].UnixNano()) / 1e9, Y: minY}, {X: float64(times[idx].UnixNano()) / 1e9, Y: maxY}}
				vl, err := plotter.NewLine(vpts)
				if err != nil { return err }
				vl.LineStyle.Width = vg.Points(0.5)
				vl.LineStyle.Color = colors[ch%len(colors)]
				vl.LineStyle.Dashes = []vg.Length{vg.Points(2), vg.Points(2)}
				p.Add(vl)
			}
		}
	}

	// Total weight line
	ptsTW := make(plotter.XYs, len(times))
	for i := range times {
		ptsTW[i].X = float64(times[i].UnixNano()) / 1e9
		ptsTW[i].Y = totalWeight[i]
	}
	tl, err := plotter.NewLine(ptsTW)
	if err != nil { return err }
	tl.LineStyle.Width = vg.Points(1.5)
	tl.LineStyle.Color = colorBlack()
	p.Add(tl)
	p.Legend.Add("Total weight", tl)

	// Vacuum event lines (red)
	for _, vt := range vacuumTimes {
		vpts := plotter.XYs{{X: float64(vt.UnixNano()) / 1e9, Y: minY}, {X: float64(vt.UnixNano()) / 1e9, Y: maxY}}
		vl, err := plotter.NewLine(vpts)
		if err != nil { return err }
		vl.LineStyle.Width = vg.Points(2)
		vl.LineStyle.Color = colorRed()
		p.Add(vl)
	}

	p.Add(plotter.NewGrid())
	if err := p.Save(14*vg.Inch, 7*vg.Inch, pngPath); err != nil { return err }
	return nil
}

func sanitizeParam(s string) string {
	s = strings.ReplaceAll(s, ".", "")
	s = strings.ReplaceAll(s, "=", "_")
	s = strings.ReplaceAll(s, " ", "")
	return s
}

func readExcelWeights(filename string) ([]time.Time, [][]float64, error) {
	f, err := excelize.OpenFile(filename)
	if err != nil { return nil, nil, err }
	defer f.Close()
	sheets := f.GetSheetList()
	if len(sheets) == 0 { return nil, nil, errors.New("no sheets in workbook") }
	sheet := sheets[0]
	rows, err := f.GetRows(sheet)
	if err != nil { return nil, nil, err }
	if len(rows) < 2 { return nil, nil, errors.New("no data rows") }
	// Header map
	colIdx := map[string]int{}
	for j, v := range rows[0] {
		colIdx[strings.ToLower(strings.TrimSpace(v))] = j
	}
	reqCols := []string{"timestamp", "weight_1", "weight_2", "weight_3", "weight_4"}
	for _, c := range reqCols {
		if _, ok := colIdx[c]; !ok { return nil, nil, fmt.Errorf("missing column %q", c) }
	}
	var times []time.Time
	weights := make([][]float64, 4)
	for i := range weights { weights[i] = make([]float64, 0, len(rows)-1) }
	for r := 1; r < len(rows); r++ {
		row := rows[r]
		if len(row) == 0 { continue }
		// Timestamp
		tsStr := ""
		if colIdx["timestamp"] < len(row) { tsStr = row[colIdx["timestamp"]] }
		ts, err := parseExcelTimestamp(tsStr)
		if err != nil { continue }
		times = append(times, ts)
		// Weights
		for ch := 0; ch < 4; ch++ {
			val := 0.0
			idx := colIdx[fmt.Sprintf("weight_%d", ch+1)]
			if idx < len(row) {
				if v, err := strconv.ParseFloat(strings.TrimSpace(row[idx]), 64); err == nil { val = v }
			}
			weights[ch] = append(weights[ch], val)
		}
	}
	if len(times) < 2 { return nil, nil, errors.New("insufficient parsed rows") }
	return times, weights, nil
}

func parseExcelTimestamp(s string) (time.Time, error) {
	s = strings.TrimSpace(s)
	if s == "" { return time.Time{}, errors.New("empty") }
	layouts := []string{time.RFC3339Nano, "2006-01-02 15:04:05.000", "2006-01-02 15:04:05", "01/02/2006 15:04:05", "1/2/2006 15:04:05"}
	for _, layout := range layouts {
		if t, err := time.Parse(layout, s); err == nil { return t, nil }
	}
	if f, err := strconv.ParseFloat(s, 64); err == nil {
		return excelSerialToTime(f, false), nil
	}
	return time.Time{}, fmt.Errorf("unparsed timestamp: %q", s)
}

func excelSerialToTime(serial float64, date1904 bool) time.Time {
	// Excel serial date: days since 1899-12-30 for 1900 system; since 1904-01-01 if date1904
	var base time.Time
	if date1904 {
		base = time.Date(1904, 1, 1, 0, 0, 0, 0, time.UTC)
	} else {
		base = time.Date(1899, 12, 30, 0, 0, 0, 0, time.UTC)
	}
	days := int64(math.Floor(serial))
	frac := serial - math.Floor(serial)
	sec := int64(math.Round(frac * 86400))
	return base.Add(time.Duration(days)*24*time.Hour + time.Duration(sec)*time.Second)
}

func angleDiff(a, b float64) float64 {
	// Normalize angle difference to [-pi, pi]
	d := a - b
	for d > math.Pi { d -= 2 * math.Pi }
	for d < -math.Pi { d += 2 * math.Pi }
	return d
}

func median(xs []float64) float64 {
	if len(xs) == 0 { return math.NaN() }
	c := append([]float64(nil), xs...)
	sort.Float64s(c)
	n := len(c)
	if n%2 == 1 { return c[n/2] }
	return 0.5 * (c[n/2-1] + c[n/2])
}

func isFinite(x float64) bool { return !math.IsNaN(x) && !math.IsInf(x, 0) }

func minInt(a, b int) int { if a < b { return a }; return b }

// simple helpers for colors without pulling extra deps
func colorBlack() colorRGBA { return colorRGBA{0, 0, 0, 255} }
func colorRed() colorRGBA   { return colorRGBA{255, 0, 0, 255} }

type colorRGBA struct{ R, G, B, A uint8 }

func (c colorRGBA) RGBA() (r, g, b, a uint32) {
	return uint32(c.R) * 0x101, uint32(c.G) * 0x101, uint32(c.B) * 0x101, uint32(c.A) * 0x101
}

// local helpers to avoid import of cmplx
func cmplxAbs(z complex128) float64 { return math.Hypot(real(z), imag(z)) }

