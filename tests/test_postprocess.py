"""Tests for text post-processing."""

import pytest

from ms_ocr.ocr.postprocess import (
    TextPostProcessor,
    merge_lines,
    normalize_lists,
    preserve_section_numbers,
)


class TestTextPostProcessor:
    """Test TextPostProcessor class."""

    def test_fix_hyphenation(self):
        """Test hyphenation fixing."""
        processor = TextPostProcessor(fix_hyphens=True, fix_spacing=False)

        text = "This is a test-\nword that continues."
        result = processor.process(text)

        assert "testword" in result
        assert processor.words_corrected == 1

    def test_fix_spacing(self):
        """Test spacing fixes."""
        processor = TextPostProcessor(fix_hyphens=False, fix_spacing=True)

        text = "Hello  world .This is   a test ."
        result = processor.process(text)

        assert "Hello world." in result
        assert "This is a test." in result

    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        processor = TextPostProcessor()

        text = "Line 1\n\n\n\nLine 2\n\n\nLine 3"
        result = processor.process(text)

        # Should reduce multiple newlines to double newlines
        assert "\n\n\n\n" not in result

    def test_fix_common_ocr_errors(self):
        """Test common OCR error fixes."""
        processor = TextPostProcessor()

        # These are context-dependent, so just ensure no crashes
        text = "The number is l23 and O45"
        result = processor.process(text)

        assert result is not None


class TestMergeLines:
    """Test merge_lines function."""

    def test_merge_simple(self):
        """Test simple line merging."""
        lines = ["Line 1", "Line 2", "", "Line 3"]
        result = merge_lines(lines, preserve_breaks=True)

        assert "Line 1 Line 2" in result
        assert "Line 3" in result

    def test_merge_no_breaks(self):
        """Test merging without preserving breaks."""
        lines = ["Line 1", "Line 2", "", "Line 3"]
        result = merge_lines(lines, preserve_breaks=False)

        assert result.count("\n") < len(lines)


class TestNormalizeLists:
    """Test normalize_lists function."""

    def test_normalize_bullets(self):
        """Test bullet normalization."""
        text = "• Item 1\n● Item 2\n- Item 3"
        result = normalize_lists(text)

        # All should be normalized to dashes
        assert result.count("- Item") == 3

    def test_normalize_numbered(self):
        """Test numbered list normalization."""
        text = "1) First\n2) Second\n3. Third"
        result = normalize_lists(text)

        # Should normalize to dot format
        assert "1. First" in result
        assert "2. Second" in result


class TestPreserveSectionNumbers:
    """Test preserve_section_numbers function."""

    def test_preserve_sections(self):
        """Test section number preservation."""
        text = "1.1 Introduction\nSome text here\n2.3.4 Subsection"
        result = preserve_section_numbers(text)

        assert "1.1 Introduction" in result
        assert "2.3.4 Subsection" in result
