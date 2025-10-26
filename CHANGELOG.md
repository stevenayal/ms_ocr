# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Multi-column layout support
- PowerPoint export
- Web interface
- REST API
- Cloud deployment support
- Enhanced table detection with deep learning

## [0.1.0] - 2025-01-26

### Added
- Initial release
- PDF text extraction with intelligent native/OCR detection
- Multi-language OCR support (optimized for Spanish)
- Layout detection (titles, headings, lists, paragraphs)
- Table extraction using Camelot and Tabula
- Export to Markdown with YAML frontmatter
- Export to Gamma JSON for presentations
- Export to DOCX with formatting
- Advanced OCR preprocessing (deskewing, denoising, binarization)
- Text post-processing (hyphenation fixes, spacing corrections)
- Brand integration for Gamma presentations
- Detailed metrics and logging
- Batch processing with parallel workers
- Docker support
- Comprehensive CLI
- Unit tests and CI/CD
- Complete documentation

### Features
- Automatic text density detection
- Header/footer removal
- Section number preservation (1.1, 2.3.4)
- List normalization (bullets and numbered)
- Language detection
- Page filtering
- Configurable OCR parameters
- Metrics export

### Dependencies
- Python 3.11+
- PyMuPDF 1.23.8
- pytesseract 0.3.10
- opencv-python 4.9.0
- camelot-py 0.11.0
- tabula-py 2.9.0
- layoutparser 0.3.4
- And more (see requirements.txt)

[Unreleased]: https://github.com/stevenayal/ms_ocr/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/stevenayal/ms_ocr/releases/tag/v0.1.0
