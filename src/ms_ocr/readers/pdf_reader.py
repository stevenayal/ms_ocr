"""PDF reading and text extraction."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import fitz  # PyMuPDF


@dataclass
class TextBlock:
    """Text block with metadata."""

    text: str
    bbox: tuple  # (x0, y0, x1, y1)
    font_size: float
    font_name: str
    is_bold: bool
    is_italic: bool
    page_num: int


@dataclass
class PageInfo:
    """Information about a PDF page."""

    page_num: int
    width: float
    height: float
    text_blocks: List[TextBlock]
    raw_text: str
    text_density: float  # Ratio of text area to page area
    image_count: int
    has_native_text: bool


class PDFReader:
    """Read and extract information from PDF files."""

    def __init__(self, pdf_path: Path):
        """Initialize PDF reader.

        Args:
            pdf_path: Path to PDF file
        """
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.metadata = self._extract_metadata()

    def _extract_metadata(self) -> Dict:
        """Extract PDF metadata.

        Returns:
            Dictionary with metadata
        """
        return {
            "title": self.doc.metadata.get("title", ""),
            "author": self.doc.metadata.get("author", ""),
            "subject": self.doc.metadata.get("subject", ""),
            "creator": self.doc.metadata.get("creator", ""),
            "producer": self.doc.metadata.get("producer", ""),
            "creation_date": self.doc.metadata.get("creationDate", ""),
            "page_count": len(self.doc),
        }

    def get_page_info(self, page_num: int) -> PageInfo:
        """Get information about a specific page.

        Args:
            page_num: Page number (0-indexed)

        Returns:
            Page information
        """
        page = self.doc[page_num]
        rect = page.rect

        # Extract text blocks with formatting
        blocks = page.get_text("dict")["blocks"]
        text_blocks = []
        raw_text_parts = []

        for block in blocks:
            if block["type"] == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span["text"].strip()
                        if text:
                            text_blocks.append(
                                TextBlock(
                                    text=text,
                                    bbox=tuple(span["bbox"]),
                                    font_size=span["size"],
                                    font_name=span["font"],
                                    is_bold="bold" in span["font"].lower(),
                                    is_italic="italic" in span["font"].lower(),
                                    page_num=page_num,
                                )
                            )
                            raw_text_parts.append(text)

        # Calculate text density
        text_area = sum((b.bbox[2] - b.bbox[0]) * (b.bbox[3] - b.bbox[1]) for b in text_blocks)
        page_area = rect.width * rect.height
        text_density = text_area / page_area if page_area > 0 else 0

        # Get image count
        image_list = page.get_images()
        image_count = len(image_list)

        # Raw text
        raw_text = "\n".join(raw_text_parts)

        return PageInfo(
            page_num=page_num,
            width=rect.width,
            height=rect.height,
            text_blocks=text_blocks,
            raw_text=raw_text,
            text_density=text_density,
            image_count=image_count,
            has_native_text=len(text_blocks) > 0,
        )

    def needs_ocr(self, page_num: int, threshold: float = 0.01) -> bool:
        """Determine if a page needs OCR.

        Args:
            page_num: Page number
            threshold: Text density threshold

        Returns:
            True if OCR is needed
        """
        page_info = self.get_page_info(page_num)
        return page_info.text_density < threshold or not page_info.has_native_text

    def extract_page_as_image(self, page_num: int, dpi: int = 300):
        """Extract page as image.

        Args:
            page_num: Page number
            dpi: Resolution in DPI

        Returns:
            PIL Image
        """
        from PIL import Image

        page = self.doc[page_num]
        zoom = dpi / 72  # PDF default is 72 DPI
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return img

    def get_text_by_page(self, page_num: int) -> str:
        """Get raw text from a page.

        Args:
            page_num: Page number

        Returns:
            Raw text
        """
        page = self.doc[page_num]
        return page.get_text()

    def close(self):
        """Close the PDF document."""
        self.doc.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
