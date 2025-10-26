# Examples

This directory contains example PDFs and usage scripts.

## Directory Structure

```
examples/
├── sample.pdf          # Example PDF (add your own)
├── output/             # Output directory (generated files)
└── README.md          # This file
```

## Quick Start

### Basic Usage

```bash
# From project root
ms-ocr extract --input examples/sample.pdf --out examples/output/ --lang spa,eng
```

### Generate Gamma Presentation

```bash
ms-ocr extract \
  --input examples/sample.pdf \
  --out examples/output/ \
  --lang spa,eng \
  --gamma \
  --brand assets/brand.json \
  --logo assets/logo.png
```

### Using Makefile

```bash
# From project root
make run PDF=examples/sample.pdf OUT=examples/output
```

### Docker

```bash
# From project root
docker run --rm \
  -v $(pwd)/examples:/data/input \
  -v $(pwd)/examples/output:/data/output \
  -v $(pwd)/assets:/app/assets \
  ms-ocr extract \
  --input /data/input/sample.pdf \
  --out /data/output \
  --lang spa,eng \
  --gamma \
  --brand /app/assets/brand.json \
  --logo /app/assets/logo.png
```

## Expected Output

After processing, you should see:

```
examples/output/
├── sample.md              # Markdown output
├── sample.gamma.json      # Gamma presentation JSON
├── sample.docx            # Word document (if --export includes docx)
└── sample.metrics.json    # Processing metrics
```

## Sample PDFs

Add your own PDF files to this directory for testing. Good test cases:

- **Native Text PDF**: Digital-born document (e.g., exported from Word)
- **Scanned PDF**: Image-based document from scanner
- **Mixed PDF**: Contains both native text and scanned images
- **Table-Heavy PDF**: Document with multiple tables
- **Multi-Language PDF**: Document with Spanish and English text
- **Complex Layout**: Document with columns, figures, and varied formatting

## Tips

1. **For best OCR results**:
   - Use high-quality scans (300+ DPI)
   - Enable preprocessing: `--deskew --denoise --binarize`
   - Adjust DPI if needed: `--dpi 600`

2. **For large PDFs**:
   - Process specific pages: `--pages 1,5-10`
   - Use parallel workers: `--workers 4`

3. **For debugging**:
   - Enable verbose logging: `--log-level DEBUG`
   - Save logs to file: `--log-file output.log`

## Troubleshooting

### No output generated

- Check input PDF exists
- Verify output directory permissions
- Check logs for errors

### Poor OCR quality

- Increase DPI: `--dpi 600`
- Verify Tesseract is installed: `tesseract --version`
- Check Tesseract language packs: `tesseract --list-langs`

### Tables not extracted

- Try different table extraction methods (Camelot/Tabula)
- Check if PDF has actual table structure or just text
- Some complex tables may require manual formatting

## Integration with Gamma

To use the generated Gamma JSON:

1. Open [Gamma.app](https://gamma.app)
2. Create new presentation
3. Import JSON file
4. Customize as needed

## Contributing Examples

If you have interesting example PDFs (with permission to share), please contribute them via Pull Request. Ensure:

- No sensitive information
- Properly licensed/public domain
- Representative of common use cases
- Documented in this README
