"""Export to Gamma JSON format."""

import json
from pathlib import Path
from typing import Dict, List, Optional

from ms_ocr.exporters.json_schemas import (
    BrandConfig,
    GammaMeta,
    GammaPresentation,
    GammaSlide,
    create_bullets_slide,
    create_cover_slide,
    create_section_slide,
    create_table_slide,
)
from ms_ocr.layout.rules import LayoutElement
from ms_ocr.tables.tables_extractor import Table


class GammaExporter:
    """Export document to Gamma presentation format."""

    def __init__(self, brand_config: Optional[Dict] = None, logo_path: Optional[str] = None):
        """Initialize Gamma exporter.

        Args:
            brand_config: Brand configuration dictionary
            logo_path: Path to logo file
        """
        if brand_config:
            self.brand = BrandConfig(**brand_config)
        else:
            self.brand = BrandConfig(name="Presentation")

        if logo_path:
            self.brand.logo = logo_path

    def export(
        self,
        elements: List[LayoutElement],
        tables: List[Table],
        output_path: Path,
        source_file: str,
        metadata: Optional[Dict] = None,
    ):
        """Export to Gamma JSON file.

        Args:
            elements: Layout elements
            tables: Extracted tables
            output_path: Output file path
            source_file: Source PDF filename
            metadata: Optional metadata
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build slides
        slides = self._build_slides(elements, tables)

        # Detect title
        title = self._detect_title(elements)

        # Create meta
        meta = GammaMeta(
            pages=metadata.get("pages", 0) if metadata else 0,
            lang=metadata.get("languages", ["spa"]) if metadata else ["spa"],
        )

        # Create presentation
        presentation = GammaPresentation(
            brand=self.brand, title=title, slides=slides, source=source_file, meta=meta
        )

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(presentation.to_dict(), f, indent=2, ensure_ascii=False)

    def _build_slides(
        self, elements: List[LayoutElement], tables: List[Table]
    ) -> List[GammaSlide]:
        """Build slides from elements.

        Args:
            elements: Layout elements
            tables: Extracted tables

        Returns:
            List of slides
        """
        slides = []

        # Create cover slide
        title = self._detect_title(elements)
        subtitle = self._detect_subtitle(elements)
        slides.append(create_cover_slide(title, subtitle, self.brand.logo))

        # Group elements into slides
        current_section = None
        current_bullets = []
        current_title = None

        for element in elements:
            if element.type == "heading":
                # Flush previous bullets
                if current_bullets and current_title:
                    slides.append(create_bullets_slide(current_title, current_bullets))
                    current_bullets = []

                # Check heading level
                if element.level == 1:
                    # Major section
                    slides.append(create_section_slide(element.text))
                    current_section = element.text
                    current_title = None
                else:
                    # Subsection - becomes slide title
                    current_title = element.text

            elif element.type == "list_item":
                # Add to current bullets
                text = element.text.lstrip("•●○■□▪▫-*0123456789. \t")
                current_bullets.append(text)

            elif element.type == "paragraph":
                # Flush bullets if any
                if current_bullets and current_title:
                    slides.append(create_bullets_slide(current_title, current_bullets))
                    current_bullets = []
                    current_title = None

                # Paragraph becomes notes or new slide
                # For simplicity, add as bullets slide with single item
                if len(element.text) > 50:
                    # Long paragraph - split or skip
                    pass

        # Flush remaining bullets
        if current_bullets and current_title:
            slides.append(create_bullets_slide(current_title, current_bullets))

        # Add table slides
        for i, table in enumerate(tables):
            table_title = f"Table {i + 1}"
            slides.append(create_table_slide(table_title, table.to_markdown()))

        return slides

    def _detect_title(self, elements: List[LayoutElement]) -> str:
        """Detect presentation title.

        Args:
            elements: Layout elements

        Returns:
            Title string
        """
        for element in elements:
            if element.type == "title":
                return element.text

        # Fallback: first heading
        for element in elements:
            if element.type == "heading" and element.level == 1:
                return element.text

        return "Untitled Presentation"

    def _detect_subtitle(self, elements: List[LayoutElement]) -> Optional[str]:
        """Detect presentation subtitle.

        Args:
            elements: Layout elements

        Returns:
            Subtitle string or None
        """
        # Look for heading after title
        found_title = False
        for element in elements:
            if element.type == "title":
                found_title = True
            elif found_title and element.type == "heading" and element.level <= 2:
                return element.text

        return None

    def set_brand(self, brand_config: Dict):
        """Update brand configuration.

        Args:
            brand_config: Brand configuration dictionary
        """
        self.brand = BrandConfig(**brand_config)

    def set_logo(self, logo_path: str):
        """Update logo path.

        Args:
            logo_path: Path to logo file
        """
        self.brand.logo = logo_path
