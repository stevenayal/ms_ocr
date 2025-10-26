"""Layout detection rules and heuristics."""

import re
from dataclasses import dataclass
from typing import List, Optional

from ms_ocr.readers.pdf_reader import TextBlock


@dataclass
class LayoutElement:
    """Detected layout element."""

    type: str  # title, heading, paragraph, list_item, table, figure, header, footer
    text: str
    level: Optional[int] = None  # For headings: 1, 2, 3, etc.
    page_num: int = 0
    bbox: Optional[tuple] = None
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LayoutRules:
    """Rules for detecting layout elements."""

    def __init__(
        self,
        title_min_size: float = 16.0,
        heading_min_size: float = 12.0,
        body_size: float = 10.0,
    ):
        """Initialize layout rules.

        Args:
            title_min_size: Minimum font size for titles
            heading_min_size: Minimum font size for headings
            body_size: Expected body text size
        """
        self.title_min_size = title_min_size
        self.heading_min_size = heading_min_size
        self.body_size = body_size

    def classify_block(self, block: TextBlock) -> LayoutElement:
        """Classify a text block.

        Args:
            block: Text block to classify

        Returns:
            Layout element
        """
        text = block.text.strip()

        # Check for section numbers (e.g., "1.1", "2.3.4")
        section_match = re.match(r"^(\d+(?:\.\d+)*)\s+(.+)$", text)

        # Check for list items
        if self._is_list_item(text):
            level = self._get_list_level(text)
            return LayoutElement(
                type="list_item",
                text=text,
                level=level,
                page_num=block.page_num,
                bbox=block.bbox,
                metadata={"font_size": block.font_size},
            )

        # Check for titles (large, bold, or uppercase)
        if self._is_title(block):
            return LayoutElement(
                type="title",
                text=text,
                level=1,
                page_num=block.page_num,
                bbox=block.bbox,
                metadata={"font_size": block.font_size, "bold": block.is_bold},
            )

        # Check for headings with section numbers
        if section_match:
            section_num = section_match.group(1)
            heading_text = section_match.group(2)
            level = self._get_heading_level_from_number(section_num)

            return LayoutElement(
                type="heading",
                text=text,
                level=level,
                page_num=block.page_num,
                bbox=block.bbox,
                metadata={
                    "font_size": block.font_size,
                    "section_number": section_num,
                    "bold": block.is_bold,
                },
            )

        # Check for headings by size/style
        if self._is_heading(block):
            level = self._get_heading_level_from_size(block.font_size)
            return LayoutElement(
                type="heading",
                text=text,
                level=level,
                page_num=block.page_num,
                bbox=block.bbox,
                metadata={"font_size": block.font_size, "bold": block.is_bold},
            )

        # Default: paragraph
        return LayoutElement(
            type="paragraph",
            text=text,
            page_num=block.page_num,
            bbox=block.bbox,
            metadata={"font_size": block.font_size},
        )

    def _is_title(self, block: TextBlock) -> bool:
        """Check if block is a title.

        Args:
            block: Text block

        Returns:
            True if title
        """
        text = block.text.strip()

        # Large font size
        if block.font_size >= self.title_min_size:
            return True

        # All uppercase and bold
        if text.isupper() and block.is_bold and len(text) > 5:
            return True

        # Centered and bold (heuristic based on bbox)
        # This is a simplified check; real implementation would compare to page width
        if block.is_bold and len(text) < 100:
            return True

        return False

    def _is_heading(self, block: TextBlock) -> bool:
        """Check if block is a heading.

        Args:
            block: Text block

        Returns:
            True if heading
        """
        # Font size larger than body
        if block.font_size >= self.heading_min_size and block.font_size > self.body_size:
            return True

        # Bold and reasonable length
        if block.is_bold and 5 < len(block.text.strip()) < 100:
            return True

        return False

    def _is_list_item(self, text: str) -> bool:
        """Check if text is a list item.

        Args:
            text: Text to check

        Returns:
            True if list item
        """
        # Bullet points
        if re.match(r"^[•●○■□▪▫\-\*]\s+", text):
            return True

        # Numbered lists
        if re.match(r"^\d+[\.)]\s+", text):
            return True

        # Lettered lists
        if re.match(r"^[a-z][\.)]\s+", text, re.IGNORECASE):
            return True

        return False

    def _get_list_level(self, text: str) -> int:
        """Get list indentation level.

        Args:
            text: List item text

        Returns:
            Indentation level (1-based)
        """
        # Count leading whitespace (simplified)
        match = re.match(r"^(\s*)", text)
        if match:
            spaces = len(match.group(1))
            return (spaces // 2) + 1 if spaces > 0 else 1

        return 1

    def _get_heading_level_from_number(self, section_num: str) -> int:
        """Get heading level from section number.

        Args:
            section_num: Section number (e.g., "1.2.3")

        Returns:
            Heading level (1-6)
        """
        parts = section_num.split(".")
        level = len(parts)
        return min(level, 6)  # Cap at h6

    def _get_heading_level_from_size(self, font_size: float) -> int:
        """Get heading level from font size.

        Args:
            font_size: Font size

        Returns:
            Heading level (1-6)
        """
        if font_size >= self.title_min_size:
            return 1
        elif font_size >= self.heading_min_size + 4:
            return 2
        elif font_size >= self.heading_min_size + 2:
            return 3
        elif font_size >= self.heading_min_size:
            return 4
        else:
            return 5

    def detect_headers_footers(
        self, blocks_by_page: List[List[TextBlock]], threshold: float = 0.6
    ) -> tuple:
        """Detect repeated headers and footers.

        Args:
            blocks_by_page: List of text blocks for each page
            threshold: Minimum repetition ratio to consider as header/footer

        Returns:
            Tuple of (header_texts, footer_texts) to exclude
        """
        if not blocks_by_page or len(blocks_by_page) < 3:
            return set(), set()

        # Collect top and bottom blocks from each page
        top_blocks = []
        bottom_blocks = []

        for blocks in blocks_by_page:
            if not blocks:
                continue

            sorted_blocks = sorted(blocks, key=lambda b: b.bbox[1])  # Sort by y position

            if len(sorted_blocks) > 0:
                top_blocks.append(sorted_blocks[0].text.strip())

            if len(sorted_blocks) > 1:
                bottom_blocks.append(sorted_blocks[-1].text.strip())

        # Find repeated texts
        headers = self._find_repeated_texts(top_blocks, threshold)
        footers = self._find_repeated_texts(bottom_blocks, threshold)

        return headers, footers

    def _find_repeated_texts(self, texts: List[str], threshold: float) -> set:
        """Find texts that appear frequently.

        Args:
            texts: List of texts
            threshold: Minimum frequency ratio

        Returns:
            Set of repeated texts
        """
        if not texts:
            return set()

        from collections import Counter

        counts = Counter(texts)
        total = len(texts)
        repeated = set()

        for text, count in counts.items():
            if count / total >= threshold:
                repeated.add(text)

        return repeated
