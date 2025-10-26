"""Extract and process images from PDFs."""

from pathlib import Path
from typing import List, Optional

import fitz  # PyMuPDF
from PIL import Image


class ImageExtractor:
    """Extract images from PDF pages."""

    def __init__(self, pdf_path: Path):
        """Initialize image extractor.

        Args:
            pdf_path: Path to PDF file
        """
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)

    def extract_images(
        self, page_num: int, output_dir: Optional[Path] = None
    ) -> List[Path]:
        """Extract all images from a page.

        Args:
            page_num: Page number
            output_dir: Directory to save images (optional)

        Returns:
            List of image paths
        """
        page = self.doc[page_num]
        image_list = page.get_images()
        extracted = []

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = self.doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            # Convert to PIL Image
            from io import BytesIO

            image = Image.open(BytesIO(image_bytes))

            if output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                img_path = output_dir / f"page_{page_num}_img_{img_index}.{image_ext}"
                image.save(img_path)
                extracted.append(img_path)

        return extracted

    def get_page_as_image(self, page_num: int, dpi: int = 300) -> Image.Image:
        """Render page as image.

        Args:
            page_num: Page number
            dpi: Resolution

        Returns:
            PIL Image
        """
        page = self.doc[page_num]
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return img

    def save_page_as_image(self, page_num: int, output_path: Path, dpi: int = 300):
        """Save page as image file.

        Args:
            page_num: Page number
            output_path: Output file path
            dpi: Resolution
        """
        img = self.get_page_as_image(page_num, dpi)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)

    def close(self):
        """Close the PDF document."""
        self.doc.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
