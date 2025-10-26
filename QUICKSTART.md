# Quick Start Guide

Get started with ms-ocr in 5 minutes!

## Prerequisites

Before you begin, ensure you have:
- Python 3.11 or higher
- Tesseract OCR installed
- Java (for Tabula table extraction)

## Installation

### Option 1: Local Installation (Recommended for Development)

```bash
# 1. Clone the repository
git clone https://github.com/stevenayal/ms_ocr.git
cd ms_ocr

# 2. Set up the environment (creates venv and installs dependencies)
make setup

# 3. Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# 4. Verify installation
ms-ocr --version
```

### Option 2: Docker (Easiest, No Dependencies)

```bash
# 1. Clone the repository
git clone https://github.com/stevenayal/ms_ocr.git
cd ms_ocr

# 2. Build the Docker image
make docker-build

# 3. Run (no need to activate anything)
# See Docker examples below
```

## Your First Extraction

### Example 1: Basic PDF to Markdown

```bash
# Add your PDF to the examples folder
cp /path/to/your/document.pdf examples/

# Process it
ms-ocr extract \
  --input examples/document.pdf \
  --out examples/output \
  --lang spa,eng

# Check the output
ls examples/output/
# You should see: document.md, document.metrics.json
```

### Example 2: Generate Gamma Presentation

```bash
ms-ocr extract \
  --input examples/document.pdf \
  --out examples/output \
  --lang spa,eng \
  --gamma \
  --brand assets/brand.json \
  --logo assets/logo.png

# Check the output
ls examples/output/
# You should see: document.md, document.gamma.json, document.metrics.json
```

### Example 3: Docker Version

```bash
# Place your PDF in examples/
cp /path/to/your/document.pdf examples/

# Run with Docker
docker run --rm \
  -v $(pwd)/examples:/data/input \
  -v $(pwd)/examples/output:/data/output \
  -v $(pwd)/assets:/app/assets \
  ms-ocr extract \
  --input /data/input/document.pdf \
  --out /data/output \
  --lang spa,eng \
  --gamma \
  --brand /app/assets/brand.json \
  --logo /app/assets/logo.png

# Check the output
ls examples/output/
```

## Common Use Cases

### High-Quality OCR (Scanned Documents)

```bash
ms-ocr extract \
  --input scanned.pdf \
  --out output/ \
  --dpi 600 \
  --deskew \
  --denoise \
  --binarize \
  --lang spa,eng
```

### Process Specific Pages

```bash
ms-ocr extract \
  --input largebook.pdf \
  --out output/ \
  --pages 1,5-10,20-25 \
  --lang spa,eng
```

### Batch Processing (Multiple PDFs)

```bash
# Put all PDFs in a folder
mkdir pdfs/
cp *.pdf pdfs/

# Process with 4 parallel workers
ms-ocr extract \
  --input pdfs/ \
  --out output/ \
  --workers 4 \
  --lang spa,eng
```

### Export All Formats

```bash
ms-ocr extract \
  --input document.pdf \
  --out output/ \
  --export md,json,docx \
  --gamma \
  --brand assets/brand.json \
  --logo assets/logo.png \
  --lang spa,eng
```

## Customizing Brand (for Gamma)

Edit `assets/brand.json`:

```json
{
  "name": "Your Company",
  "primary": "#FF5733",
  "secondary": "#33FF57",
  "accent": "#3357FF",
  "logo": "assets/your-logo.png",
  "footer": "Your tagline here"
}
```

Add your logo:

```bash
cp /path/to/your-logo.png assets/logo.png
```

## Verifying Output

### Check Markdown

```bash
cat examples/output/document.md
```

### Check Gamma JSON

```bash
cat examples/output/document.gamma.json | python -m json.tool
```

### Check Metrics

```bash
cat examples/output/document.metrics.json | python -m json.tool
```

## Troubleshooting

### "Tesseract not found"

**Install Tesseract:**

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng

# macOS
brew install tesseract tesseract-lang

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### "Java not found" (for tables)

```bash
# Ubuntu/Debian
sudo apt-get install default-jre

# macOS
brew install openjdk

# Windows
# Download from: https://www.oracle.com/java/technologies/downloads/
```

### Poor OCR Quality

Try these options:
- Increase DPI: `--dpi 600`
- Enable all preprocessing: `--deskew --denoise --binarize`
- Check input quality (should be at least 300 DPI)

### Out of Memory

- Reduce DPI: `--dpi 200`
- Process fewer workers: `--workers 1`
- Process pages in batches: `--pages 1-10` then `--pages 11-20`

## Next Steps

1. **Read the full documentation**: [README.md](README.md)
2. **Customize layout rules**: `src/ms_ocr/layout/rules.py`
3. **Add new exporters**: `src/ms_ocr/exporters/`
4. **Contribute**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## Getting Help

- **Documentation**: [README.md](README.md)
- **Issues**: https://github.com/stevenayal/ms_ocr/issues
- **Discussions**: https://github.com/stevenayal/ms_ocr/discussions

## Summary of Commands

```bash
# Setup
make setup                    # Install dependencies
make test                     # Run tests
make lint                     # Check code quality
make fmt                      # Format code

# Basic usage
ms-ocr extract -i input.pdf -o output/

# Advanced usage
ms-ocr extract -i input.pdf -o output/ --gamma --brand assets/brand.json

# Docker
make docker-build             # Build image
make docker-run PDF=file.pdf  # Run extraction

# Development
make run PDF=file.pdf         # Quick test run
make clean                    # Clean build artifacts
```

Happy extracting! 🎉
