# ms-ocr

High-quality PDF text extraction with OCR, focused on Spanish content. Extract structured Markdown, generate Gamma presentations, and export to multiple formats.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Tests](https://github.com/stevenayal/ms_ocr/workflows/CI/badge.svg)

## Features

- **Intelligent Text Extraction**: Automatically detects whether to use native PDF text or OCR
- **Multi-language OCR**: Optimized for Spanish with support for multiple languages
- **Layout Detection**: Preserves document structure (headings, lists, tables, sections)
- **Table Extraction**: Extracts tables using Camelot and Tabula
- **Multiple Export Formats**:
  - Markdown with YAML frontmatter
  - Gamma JSON for presentations
  - DOCX with proper formatting
- **Advanced OCR Preprocessing**: Deskewing, denoising, binarization, and contrast enhancement
- **Text Post-processing**: Fixes hyphenation, spacing, and common OCR errors
- **Brand Integration**: Custom branding for Gamma presentations (logos, colors)
- **Metrics & Logging**: Detailed processing metrics and structured logging
- **Batch Processing**: Process multiple PDFs in parallel
- **Docker Support**: Easy deployment with Docker

## Installation

### Local Installation

**Requirements:**
- Python 3.11+
- Tesseract OCR
- Java (for Tabula)

#### Install Tesseract

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
Download from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

#### Install ms-ocr

```bash
# Clone repository
git clone https://github.com/stevenayal/ms_ocr.git
cd ms_ocr

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

Or use Make:

```bash
make setup
```

### Docker Installation

```bash
# Build image
docker build -t ms-ocr .

# Or use Make
make docker-build
```

## Quick Start

### Basic Usage

```bash
ms-ocr extract --input document.pdf --out output/ --lang spa,eng
```

### Generate Gamma Presentation

```bash
ms-ocr extract \
  --input ISTQB.pdf \
  --out output/ \
  --lang spa,eng \
  --gamma \
  --brand assets/brand.json \
  --logo assets/logo.png
```

### Process Multiple PDFs

```bash
ms-ocr extract \
  --input pdfs/ \
  --out output/ \
  --lang spa,eng \
  --workers 4
```

### Docker Usage

```bash
docker run --rm \
  -v $(pwd)/examples:/data/input \
  -v $(pwd)/output:/data/output \
  -v $(pwd)/assets:/app/assets \
  ms-ocr extract \
  --input /data/input/document.pdf \
  --out /data/output \
  --lang spa,eng \
  --gamma \
  --brand /app/assets/brand.json \
  --logo /app/assets/logo.png
```

## CLI Reference

### `ms-ocr extract`

Extract text from PDF files.

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--input, -i` | Path | Required | Input PDF file or directory |
| `--out, -o` | Path | Required | Output directory |
| `--lang` | String | `spa,eng` | OCR languages (comma-separated) |
| `--gamma` | Flag | False | Generate Gamma JSON output |
| `--brand` | Path | None | Brand configuration JSON file |
| `--logo` | Path | None | Logo file path |
| `--dpi` | Integer | 300 | Image resolution for OCR |
| `--deskew` | Flag | True | Apply deskewing |
| `--denoise` | Flag | True | Apply denoising |
| `--binarize` | Flag | True | Apply binarization |
| `--min-conf` | Integer | 0 | Minimum OCR confidence (0-100) |
| `--pages` | String | None | Page numbers (e.g., `1,3-10`) |
| `--export` | String | `md,json` | Export formats (md,json,docx) |
| `--workers` | Integer | 1 | Number of parallel workers |
| `--log-level` | Choice | INFO | Logging level |
| `--log-file` | Path | None | Log file path |

**Examples:**

```bash
# Basic extraction
ms-ocr extract -i document.pdf -o output/

# High-quality OCR with preprocessing
ms-ocr extract -i scanned.pdf -o output/ --dpi 600 --deskew --denoise

# Process specific pages
ms-ocr extract -i book.pdf -o output/ --pages 1,5-10,20

# Generate all formats
ms-ocr extract -i doc.pdf -o output/ --export md,json,docx

# Batch processing with 4 workers
ms-ocr extract -i pdfs/ -o output/ --workers 4
```

## Brand Configuration

Create a `brand.json` file to customize Gamma presentations:

```json
{
  "name": "AIQUAA",
  "primary": "#0F172A",
  "secondary": "#22C55E",
  "accent": "#06B6D4",
  "logo": "assets/logo.png",
  "footer": "AI al servicio del QA"
}
```

**Fields:**
- `name`: Brand name (appears in presentation)
- `primary`: Primary color (hex)
- `secondary`: Secondary color (hex)
- `accent`: Accent color (hex)
- `logo`: Path to logo file (PNG, JPG)
- `footer`: Footer text

## Output Formats

### Markdown

Structured Markdown with:
- YAML frontmatter (title, source, languages)
- Hierarchical headings (`#`, `##`, `###`)
- Preserved lists (bullets and numbered)
- Tables in pipe format
- Optional page number comments

**Example:**

```markdown
---
title: ISTQB Syllabus
source: ISTQB.pdf
languages:
  - spa
  - eng
generated_by: ms-ocr
---

# CAPÍTULO 1. Fundamentos de las Pruebas

## 1.1 ¿Qué es probar?

El objetivo principal de las pruebas es...

- Detectar defectos
- Validar funcionalidad
- Verificar calidad

## 1.2 Objetivos de las pruebas

1. Prevenir defectos
2. Verificar requisitos
3. Generar confianza
```

### Gamma JSON

Presentation-ready JSON format:

```json
{
  "brand": {
    "name": "AIQUAA",
    "logo": "assets/logo.png",
    "primary": "#0F172A",
    "secondary": "#22C55E"
  },
  "title": "ISTQB Syllabus",
  "slides": [
    {
      "type": "cover",
      "title": "CAPÍTULO 1",
      "subtitle": "Fundamentos de las Pruebas",
      "logo": "assets/logo.png"
    },
    {
      "type": "section",
      "title": "1.1 ¿Qué es probar?"
    },
    {
      "type": "bullets",
      "title": "Objetivos",
      "items": [
        "Detectar defectos",
        "Validar funcionalidad",
        "Verificar calidad"
      ]
    }
  ],
  "source": "ISTQB.pdf",
  "meta": {
    "pages": 50,
    "lang": ["spa", "eng"]
  }
}
```

### DOCX

Word document with:
- Proper heading styles (Heading 1-6)
- List formatting
- Table extraction
- Paragraph styles

## Processing Pipeline

The pipeline automatically:

1. **Detects Text Type**: Checks if PDF has native text or needs OCR
2. **Preprocesses Images** (if OCR needed):
   - Converts to grayscale
   - Applies denoising
   - Enhances contrast (CLAHE)
   - Binarizes (Otsu's method)
   - Deskews using Hough transform
3. **Extracts Text**:
   - Native text: Uses PyMuPDF
   - Scanned: Uses Tesseract OCR
4. **Detects Layout**:
   - Identifies titles, headings, paragraphs
   - Detects section numbers (1.1, 2.3.4)
   - Classifies list items
   - Removes headers/footers
5. **Extracts Tables**:
   - Attempts Camelot (lattice and stream modes)
   - Falls back to Tabula
   - Converts to Markdown tables
6. **Post-processes Text**:
   - Fixes hyphenation at line breaks
   - Corrects spacing issues
   - Normalizes lists
   - Preserves section numbering
7. **Exports**:
   - Generates Markdown, Gamma JSON, and/or DOCX
   - Saves processing metrics

## Metrics

Each processed PDF generates a metrics file (`document.metrics.json`):

```json
{
  "source_file": "ISTQB.pdf",
  "total_pages": 50,
  "pages_ocr": 12,
  "pages_native": 38,
  "avg_ocr_confidence": 87.5,
  "total_words_corrected": 23,
  "total_tables": 5,
  "total_time": 124.5,
  "languages": ["spa", "eng"],
  "page_metrics": [
    {
      "page_num": 0,
      "native_text_ratio": 0.85,
      "ocr_confidence": null,
      "words_corrected": 0,
      "tables_detected": 1,
      "processing_time": 2.3,
      "stages": {
        "page_info": 0.1,
        "layout": 1.2,
        "tables": 1.0
      }
    }
  ]
}
```

## Development

### Run Tests

```bash
make test
```

Or:

```bash
pytest tests/ -v --cov=src/ms_ocr
```

### Format Code

```bash
make fmt
```

### Lint Code

```bash
make lint
```

### Run Example

```bash
make run PDF=examples/sample.pdf OUT=examples/output
```

## Known Limitations

- **Handwritten Text**: Not supported (requires specialized OCR)
- **Low-Resolution Scans**: OCR quality degrades below 150 DPI
- **Complex Multi-Column Layouts**: May require manual adjustment
- **Non-Latin Scripts**: Limited support (Arabic, Chinese, etc.)
- **Image-Based Tables**: Extraction accuracy depends on table structure

## Roadmap

- [ ] Support for multi-column layouts
- [ ] Distributed batch processing
- [ ] PowerPoint export
- [ ] Web interface
- [ ] Cloud deployment (AWS Lambda, Azure Functions)
- [ ] Enhanced table detection using deep learning
- [ ] Handwriting recognition (using specialized models)
- [ ] REST API

## Performance

**Benchmark** (4-core, 8GB RAM, SSD):

| PDF Type | Pages | Time | Speed |
|----------|-------|------|-------|
| Native text | 100 | ~2 min | 50 pages/min |
| Scanned (300 DPI) | 100 | ~8 min | 12.5 pages/min |
| Mixed | 100 | ~5 min | 20 pages/min |

**Docker overhead**: ~10-15% slower than native installation

## Troubleshooting

### Tesseract not found

**Error:** `pytesseract.pytesseract.TesseractNotFoundError`

**Solution:** Install Tesseract and ensure it's in PATH

### Java not found (Tabula)

**Error:** `java: command not found`

**Solution:** Install Java JRE:
```bash
sudo apt-get install default-jre
```

### Out of memory

**Solution:** Reduce DPI or use `--workers 1`

### Poor OCR quality

**Solutions:**
- Increase DPI: `--dpi 600`
- Enable preprocessing: `--deskew --denoise --binarize`
- Check input image quality

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Issue Templates

- Bug Report
- Feature Request
- Documentation Improvement

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) for PDF processing
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for optical character recognition
- [Camelot](https://github.com/camelot-dev/camelot) and [Tabula](https://github.com/chezou/tabula-py) for table extraction
- [LayoutParser](https://github.com/Layout-Parser/layout-parser) for layout detection

## Contact

**Steven Ayal** - [GitHub](https://github.com/stevenayal)

**Project Link:** https://github.com/stevenayal/ms_ocr

---

**Made with ❤️ for the QA community**
