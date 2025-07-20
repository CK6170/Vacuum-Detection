import os
import matplotlib.pyplot as plt
import pickle


def save_analysis_results(
    fig, summary_text, filename, win_size, fs, power_ratio_thresh, zeroing_samples, co_detection_window_sec):
    """
    Save analysis results in a subdirectory with PDF (2 pages), .fig (pickle), and .txt summary.

    - fig: matplotlib Figure handle (main plot)
    - summary_text: string with summary (can include newlines)
    - filename: original input filename (with path)
    - win_size, fs, power_ratio_thresh, zeroing_samples, co_detection_window_sec: analysis parameters
    """
    # Extract folder and base file name (no extension)
    filepath, basename = os.path.split(filename)
    name, _ = os.path.splitext(basename)
    outdir = os.path.join(filepath, name)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    # Prepare parameter string for file names
    param_str = f'win_size={win_size}_fs={fs:.2f}Hz_thr={power_ratio_thresh:.2f}_zero={zeroing_samples}_codet={co_detection_window_sec:.2f}'
    param_str_filename = param_str.replace('.', '')

    pdfname = f'{param_str_filename}_analysis.pdf'
    figname = f'{param_str_filename}_graph.pkl'
    txtname = f'{param_str_filename}_summary.txt'

    pdfpathname = os.path.join(outdir, pdfname)
    figpathname = os.path.join(outdir, figname)
    txtpathname = os.path.join(outdir, txtname)
    # Save the main figure as PDF (first page)
    fig.savefig(pdfpathname)
    # Save the matplotlib figure as a pickle (Python's version of .fig)
    with open(figpathname, 'wb') as f:
        pickle.dump(fig, f)
    # Create summary as page 2 (new figure with text)
    fig2 = plt.figure(figsize=(8.27, 11.7))  # A4 size in inches
    plt.axis('off')
    if isinstance(summary_text, str):
        summary_lines = summary_text.split('\n')
    else:
        summary_lines = summary_text
    # Place text at top left
    plt.text(0.01, 0.98, '\n'.join(summary_lines), fontsize=10, va='top', ha='left', transform=plt.gca().transAxes)
    # Append as second page
    from PyPDF2 import PdfMerger
    import tempfile
    # Save fig2 as temp PDF, then merge
    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    fig2.set_size_inches(16, 9, forward=True)  # Large, wide screen shape
    for ax in fig.get_axes():
        ax.relim()
        ax.autoscale(enable=True)
        ax.autoscale_view(True, True, True)
    
    fig2.tight_layout()
    fig2.canvas.draw()
    fig2.savefig(tmp_pdf.name)
    tmp_pdf.close()
    plt.close(fig2)
    # Merge PDFs
    merger = PdfMerger()
    merger.append(pdfpathname)
    merger.append(tmp_pdf.name)
    merger.write(pdfpathname)
    merger.close()
    os.unlink(tmp_pdf.name)
    # Save summary as .txt file
    with open(txtpathname, 'w', encoding='utf-8') as f:
        if isinstance(summary_text, list):
            f.write('\n'.join(summary_text))
        else:
            f.write(summary_text)

    print(f'\nFiles saved in: {outdir}')
    print(f'   PDF: {pdfname}')
    print(f'   FIG: {figname}')
    print(f'   TXT: {txtname}')

