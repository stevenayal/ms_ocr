"""Tests for exporters."""

import json
import tempfile
from pathlib import Path

import pytest

from ms_ocr.exporters.gamma_exporter import GammaExporter
from ms_ocr.exporters.json_schemas import (
    BrandConfig,
    create_bullets_slide,
    create_cover_slide,
    create_section_slide,
)
from ms_ocr.exporters.md_exporter import MarkdownExporter
from ms_ocr.layout.rules import LayoutElement


class TestMarkdownExporter:
    """Test Markdown exporter."""

    def test_export_basic(self):
        """Test basic Markdown export."""
        elements = [
            LayoutElement(type="title", text="Test Document", level=1, page_num=0),
            LayoutElement(type="heading", text="Section 1", level=2, page_num=0),
            LayoutElement(type="paragraph", text="This is a paragraph.", page_num=0),
            LayoutElement(type="list_item", text="- Item 1", level=1, page_num=0),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.md"
            exporter = MarkdownExporter()
            exporter.export(elements, [], output_path)

            assert output_path.exists()

            content = output_path.read_text(encoding="utf-8")
            assert "# Test Document" in content
            assert "## Section 1" in content
            assert "This is a paragraph." in content

    def test_export_with_frontmatter(self):
        """Test Markdown export with frontmatter."""
        elements = [
            LayoutElement(type="title", text="Test", level=1, page_num=0),
        ]

        metadata = {"title": "Test Document", "author": "Test Author"}

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.md"
            exporter = MarkdownExporter(include_frontmatter=True)
            exporter.export(elements, [], output_path, metadata)

            content = output_path.read_text(encoding="utf-8")
            assert "---" in content
            assert "title: Test Document" in content


class TestGammaExporter:
    """Test Gamma JSON exporter."""

    def test_export_basic(self):
        """Test basic Gamma export."""
        elements = [
            LayoutElement(type="title", text="Test Presentation", level=1, page_num=0),
            LayoutElement(type="heading", text="Section 1", level=1, page_num=0),
            LayoutElement(type="heading", text="Topic 1", level=2, page_num=0),
            LayoutElement(type="list_item", text="- Point 1", level=1, page_num=0),
            LayoutElement(type="list_item", text="- Point 2", level=1, page_num=0),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gamma.json"
            exporter = GammaExporter()
            exporter.export(elements, [], output_path, "test.pdf")

            assert output_path.exists()

            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert "brand" in data
            assert "title" in data
            assert "slides" in data
            assert len(data["slides"]) > 0

    def test_export_with_brand(self):
        """Test Gamma export with brand configuration."""
        brand_config = {
            "name": "AIQUAA",
            "primary": "#0F172A",
            "secondary": "#22C55E",
        }

        elements = [
            LayoutElement(type="title", text="Test", level=1, page_num=0),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gamma.json"
            exporter = GammaExporter(brand_config=brand_config)
            exporter.export(elements, [], output_path, "test.pdf")

            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert data["brand"]["name"] == "AIQUAA"
            assert data["brand"]["primary"] == "#0F172A"


class TestJsonSchemas:
    """Test JSON schema utilities."""

    def test_create_cover_slide(self):
        """Test cover slide creation."""
        slide = create_cover_slide("My Presentation", "A subtitle", "logo.png")

        assert slide.type == "cover"
        assert slide.title == "My Presentation"
        assert slide.subtitle == "A subtitle"
        assert slide.logo == "logo.png"

    def test_create_section_slide(self):
        """Test section slide creation."""
        slide = create_section_slide("Chapter 1")

        assert slide.type == "section"
        assert slide.title == "Chapter 1"

    def test_create_bullets_slide(self):
        """Test bullets slide creation."""
        items = ["Point 1", "Point 2", "Point 3"]
        slide = create_bullets_slide("Key Points", items)

        assert slide.type == "bullets"
        assert slide.title == "Key Points"
        assert len(slide.items) == 3

    def test_brand_config(self):
        """Test brand configuration."""
        brand = BrandConfig(
            name="Test Brand", primary="#FF0000", secondary="#00FF00", accent="#0000FF"
        )

        assert brand.name == "Test Brand"
        assert brand.primary == "#FF0000"
