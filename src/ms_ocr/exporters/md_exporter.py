"""Export to Markdown format."""

from pathlib import Path
from typing import Dict, List, Optional

from ms_ocr.layout.rules import LayoutElement
from ms_ocr.tables.tables_extractor import Table


class MarkdownExporter:
    """Export document to Markdown."""

    def __init__(
        self,
        include_frontmatter: bool = True,
        include_page_numbers: bool = False,
    ):
        """Initialize Markdown exporter.

        Args:
            include_frontmatter: Include YAML frontmatter
            include_page_numbers: Include page number comments
        """
        self.include_frontmatter = include_frontmatter
        self.include_page_numbers = include_page_numbers

    def export(
        self,
        elements: List[LayoutElement],
        tables: List[Table],
        output_path: Path,
        metadata: Optional[Dict] = None,
    ):
        """Export to Markdown file.

        Args:
            elements: Layout elements
            tables: Extracted tables
            output_path: Output file path
            metadata: Optional metadata for frontmatter
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            # Write frontmatter
            if self.include_frontmatter and metadata:
                f.write(self._generate_frontmatter(metadata))
                f.write("\n\n")

            # Write content
            current_page = -1

            for element in elements:
                # Page marker
                if self.include_page_numbers and element.page_num != current_page:
                    current_page = element.page_num
                    f.write(f"\n<!-- Page {current_page + 1} -->\n\n")

                # Write element
                md = self._element_to_markdown(element)
                if md:
                    f.write(md)
                    f.write("\n\n")

            # Write tables
            if tables:
                f.write("\n## Tables\n\n")
                for i, table in enumerate(tables):
                    f.write(f"### Table {i + 1} (Page {table.page_num + 1})\n\n")
                    f.write(table.to_markdown())
                    f.write("\n\n")

    def _generate_frontmatter(self, metadata: Dict) -> str:
        """Generate YAML frontmatter.

        Args:
            metadata: Metadata dictionary

        Returns:
            YAML frontmatter string
        """
        lines = ["---"]

        for key, value in metadata.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: {value}")

        lines.append("---")
        return "\n".join(lines)

    def _element_to_markdown(self, element: LayoutElement) -> str:
        """Convert layout element to Markdown.

        Args:
            element: Layout element

        Returns:
            Markdown string
        """
        if element.type == "title":
            return f"# {element.text}"

        elif element.type == "heading":
            level = element.level or 2
            prefix = "#" * min(level, 6)
            return f"{prefix} {element.text}"

        elif element.type == "paragraph":
            return element.text

        elif element.type == "list_item":
            indent = "  " * ((element.level or 1) - 1)
            # Check if it's a numbered list
            if element.text.strip()[0].isdigit():
                return f"{indent}{element.text}"
            else:
                # Convert to dash bullet
                text = element.text.lstrip("•●○■□▪▫-* \t")
                return f"{indent}- {text}"

        elif element.type == "table":
            return element.text  # Tables handled separately

        elif element.type == "figure":
            return f"![Figure]({element.metadata.get('image_path', '')})"

        else:
            return element.text

    def elements_to_string(self, elements: List[LayoutElement]) -> str:
        """Convert elements to Markdown string.

        Args:
            elements: Layout elements

        Returns:
            Markdown string
        """
        parts = []

        for element in elements:
            md = self._element_to_markdown(element)
            if md:
                parts.append(md)

        return "\n\n".join(parts)
