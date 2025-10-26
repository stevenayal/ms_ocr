"""Post-processing for OCR text."""

import re
from typing import List

from unidecode import unidecode


class TextPostProcessor:
    """Post-process OCR text to improve quality."""

    def __init__(self, fix_hyphens: bool = True, fix_spacing: bool = True):
        """Initialize post-processor.

        Args:
            fix_hyphens: Fix hyphenated words at line breaks
            fix_spacing: Fix spacing issues
        """
        self.fix_hyphens = fix_hyphens
        self.fix_spacing = fix_spacing
        self.words_corrected = 0

    def process(self, text: str) -> str:
        """Process text through pipeline.

        Args:
            text: Raw OCR text

        Returns:
            Processed text
        """
        self.words_corrected = 0

        if self.fix_hyphens:
            text = self._fix_hyphenation(text)

        if self.fix_spacing:
            text = self._fix_spacing(text)

        text = self._normalize_whitespace(text)
        text = self._fix_common_ocr_errors(text)

        return text

    def _fix_hyphenation(self, text: str) -> str:
        """Fix words broken by hyphens at line breaks.

        Args:
            text: Input text

        Returns:
            Fixed text
        """
        # Pattern: word- \n word
        pattern = r"(\w+)-\s*\n\s*(\w+)"

        def replacer(match):
            self.words_corrected += 1
            return match.group(1) + match.group(2)

        return re.sub(pattern, replacer, text)

    def _fix_spacing(self, text: str) -> str:
        """Fix spacing issues.

        Args:
            text: Input text

        Returns:
            Fixed text
        """
        # Fix multiple spaces
        text = re.sub(r" {2,}", " ", text)

        # Fix space before punctuation
        text = re.sub(r" ([.,;:!?])", r"\1", text)

        # Fix missing space after punctuation
        text = re.sub(r"([.,;:!?])([A-Za-z])", r"\1 \2", text)

        return text

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace.

        Args:
            text: Input text

        Returns:
            Normalized text
        """
        # Replace multiple newlines with double newline (paragraph break)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove trailing/leading whitespace from lines
        lines = [line.strip() for line in text.split("\n")]
        return "\n".join(lines)

    def _fix_common_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors.

        Args:
            text: Input text

        Returns:
            Fixed text
        """
        # Common substitutions for Spanish OCR
        replacements = {
            r"\bl\b": "1",  # lowercase L as 1 in numbers
            r"\bO\b": "0",  # uppercase O as 0 in numbers
            r"([0-9])l": r"\g<1>1",  # l after digit
            r"([0-9])O": r"\g<1>0",  # O after digit
        }

        for pattern, replacement in replacements.items():
            # Only apply if it makes sense in context
            text = re.sub(pattern, replacement, text)

        return text


def merge_lines(lines: List[str], preserve_breaks: bool = True) -> str:
    """Merge lines intelligently.

    Args:
        lines: List of text lines
        preserve_breaks: Whether to preserve paragraph breaks

    Returns:
        Merged text
    """
    if not lines:
        return ""

    result = []
    current_para = []

    for line in lines:
        line = line.strip()

        if not line:
            # Empty line - paragraph break
            if current_para:
                result.append(" ".join(current_para))
                current_para = []
            if preserve_breaks:
                result.append("")
        else:
            current_para.append(line)

    # Add last paragraph
    if current_para:
        result.append(" ".join(current_para))

    return "\n".join(result)


def normalize_lists(text: str) -> str:
    """Normalize list formatting.

    Args:
        text: Input text

    Returns:
        Text with normalized lists
    """
    lines = text.split("\n")
    result = []

    for line in lines:
        line = line.strip()

        # Detect bullet points
        if re.match(r"^[•●○■□▪▫-]\s+", line):
            # Normalize to dash
            line = re.sub(r"^[•●○■□▪▫-]\s+", "- ", line)

        # Detect numbered lists
        elif re.match(r"^\d+[\.)]\s+", line):
            # Normalize to dot format
            line = re.sub(r"^(\d+)[\.)]\s+", r"\1. ", line)

        result.append(line)

    return "\n".join(result)


def preserve_section_numbers(text: str) -> str:
    """Preserve hierarchical section numbering.

    Args:
        text: Input text

    Returns:
        Text with preserved section numbers
    """
    # Pattern for section numbers like "1.1.2"
    pattern = r"^(\d+(?:\.\d+)*)\s+"

    lines = text.split("\n")
    result = []

    for line in lines:
        # If line starts with section number, preserve it
        if re.match(pattern, line.strip()):
            result.append(line.strip())
        else:
            result.append(line)

    return "\n".join(result)
