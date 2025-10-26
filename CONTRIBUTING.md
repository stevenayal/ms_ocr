# Contributing to ms-ocr

Thank you for your interest in contributing to ms-ocr! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a welcoming and inclusive community.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/stevenayal/ms_ocr/issues)
2. Use the **Bug Report** template
3. Include as much detail as possible:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Sample PDF (if possible)
   - Error messages and logs

### Suggesting Features

1. Check if the feature has already been requested
2. Use the **Feature Request** template
3. Describe your use case clearly
4. Explain why this would be useful to others

### Submitting Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/my-awesome-feature
   ```
3. **Make your changes**:
   - Follow the coding style (see below)
   - Add tests for new functionality
   - Update documentation as needed
4. **Test your changes**:
   ```bash
   make test
   make lint
   ```
5. **Commit** with clear messages:
   ```bash
   git commit -m "Add feature: detailed description"
   ```
6. **Push** to your fork:
   ```bash
   git push origin feature/my-awesome-feature
   ```
7. **Open a Pull Request** using the PR template

## Development Setup

### Prerequisites

- Python 3.11+
- Tesseract OCR
- Java (for Tabula)
- Git

### Setup Instructions

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ms_ocr.git
cd ms_ocr

# Add upstream remote
git remote add upstream https://github.com/stevenayal/ms_ocr.git

# Create virtual environment
make setup

# Or manually:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_postprocess.py -v

# Run with coverage
pytest tests/ --cov=src/ms_ocr --cov-report=html
```

### Code Style

We use:
- **ruff** for linting
- **black** for code formatting
- **isort** for import sorting
- **mypy** for type checking

```bash
# Format code
make fmt

# Run linters
make lint

# Or manually:
black src/ tests/
isort src/ tests/
ruff check src/ tests/
mypy src/
```

**Style guidelines:**
- Line length: 100 characters
- Use type hints where possible
- Write docstrings for public functions
- Follow PEP 8

## Project Structure

```
ms_ocr/
├── src/ms_ocr/          # Main package
│   ├── readers/         # PDF and image readers
│   ├── ocr/             # OCR engine and processing
│   ├── layout/          # Layout detection
│   ├── tables/          # Table extraction
│   ├── exporters/       # Export to various formats
│   ├── utils/           # Utilities
│   ├── pipeline.py      # Main processing pipeline
│   └── cli.py           # Command-line interface
├── tests/               # Unit tests
├── assets/              # Brand assets
├── examples/            # Example files
└── docs/                # Documentation
```

## Adding New Features

### Adding a New Exporter

1. Create a new file in `src/ms_ocr/exporters/`
2. Implement the exporter class with an `export()` method
3. Add tests in `tests/test_exporters.py`
4. Update `pipeline.py` to support the new format
5. Add CLI option in `cli.py`
6. Update README with examples

### Adding New Layout Rules

1. Edit `src/ms_ocr/layout/rules.py`
2. Add new classification methods to `LayoutRules` class
3. Add tests in `tests/test_layout.py`
4. Document the new rules

### Adding OCR Languages

1. Ensure Tesseract language pack is installed
2. Update language mapping in `src/ms_ocr/utils/lang.py`
3. Test with sample PDFs in that language
4. Update documentation

## Testing Guidelines

- Write tests for all new functionality
- Aim for >80% code coverage
- Test edge cases and error conditions
- Use fixtures for common test data
- Mock external dependencies (Tesseract, file I/O)

**Test structure:**
```python
class TestMyFeature:
    """Test description."""

    def test_basic_case(self):
        """Test basic functionality."""
        # Arrange
        input_data = ...

        # Act
        result = my_function(input_data)

        # Assert
        assert result == expected
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all public functions
- Include type hints
- Provide usage examples

**Docstring format:**
```python
def my_function(param1: str, param2: int) -> bool:
    """Brief description.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When something is wrong
    """
    pass
```

## Commit Message Guidelines

Use clear, descriptive commit messages:

```
Add feature: Support for PowerPoint export

- Implement PPT exporter class
- Add tests for PPT generation
- Update CLI with --export ppt option
- Add documentation

Closes #123
```

**Format:**
- First line: Brief summary (imperative mood)
- Blank line
- Detailed description (bullet points)
- Reference related issues

## Review Process

1. Automated checks must pass (CI/CD)
2. Code review by maintainers
3. Address feedback
4. Squash commits if needed
5. Merge when approved

## Release Process

Releases are managed by maintainers:

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create Git tag
4. Build and publish to PyPI
5. Create GitHub release

## Questions?

- Open a [Discussion](https://github.com/stevenayal/ms_ocr/discussions)
- Check existing [Issues](https://github.com/stevenayal/ms_ocr/issues)
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
