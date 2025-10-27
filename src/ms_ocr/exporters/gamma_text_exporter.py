"""Export to Gamma text format with slide separators."""

from pathlib import Path
from typing import Dict, List, Optional

from ms_ocr.layout.rules import LayoutElement
from ms_ocr.tables.tables_extractor import Table


class GammaTextExporter:
    """Export document to Gamma text format with --- separators."""

    def __init__(self, brand_name: str = "AIQUAA"):
        """Initialize Gamma text exporter.

        Args:
            brand_name: Brand name for cover
        """
        self.brand_name = brand_name

    def export(
        self,
        elements: List[LayoutElement],
        tables: List[Table],
        output_path: Path,
        title: str = "Presentation",
    ):
        """Export to Gamma text file.

        Args:
            elements: Layout elements
            tables: Extracted tables
            output_path: Output file path
            title: Presentation title
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            # Write cover slide
            f.write(f"# {title}\n\n")
            f.write(f"**{self.brand_name}**\n\n")
            f.write("---\n\n")

            # Process elements into slides
            current_slide_title = None
            current_content = []
            slide_count = 0

            for element in elements:
                if element.type == "title":
                    # Skip main title (already in cover)
                    continue

                elif element.type == "heading":
                    # Flush previous slide
                    if current_slide_title and current_content:
                        self._write_slide(f, current_slide_title, current_content)
                        slide_count += 1
                        current_content = []

                    # Start new slide
                    if element.level == 1:
                        # Section divider
                        f.write(f"# {element.text}\n\n")
                        f.write("---\n\n")
                        slide_count += 1
                        current_slide_title = None
                    elif element.level <= 3:
                        # New slide title
                        current_slide_title = element.text

                elif element.type == "list_item":
                    # Add bullet
                    text = element.text.lstrip("•●○■□▪▫-*0123456789. \t")
                    if text and len(text) > 2:
                        current_content.append(f"- {text}")

                elif element.type == "paragraph":
                    text = element.text.strip()
                    if text and len(text) > 20:
                        # Add paragraph as bullet or text
                        if len(text) < 200:
                            current_content.append(f"- {text}")
                        else:
                            # Long paragraph - add as note
                            current_content.append(f"\n{text}\n")

                # Auto-flush if too much content
                if len(current_content) >= 8:
                    if current_slide_title:
                        self._write_slide(f, current_slide_title, current_content[:8])
                        slide_count += 1
                        current_content = current_content[8:]

            # Flush remaining content
            if current_slide_title and current_content:
                self._write_slide(f, current_slide_title, current_content)
                slide_count += 1

            # Add tables
            for i, table in enumerate(tables):
                f.write(f"## Tabla {i + 1}\n\n")
                f.write(table.to_markdown())
                f.write("\n\n---\n\n")
                slide_count += 1

            # Final slide
            f.write(f"# Gracias\n\n")
            f.write(f"**{self.brand_name}**\n\n")
            f.write(f"Total de slides: {slide_count}\n")

    def _write_slide(self, f, title: str, content: List[str]):
        """Write a single slide.

        Args:
            f: File handle
            title: Slide title
            content: List of content items
        """
        f.write(f"## {title}\n\n")
        for item in content:
            f.write(f"{item}\n")
        f.write("\n---\n\n")
