"""Layout detection using rules and optional ML models."""

from typing import List, Optional

from ms_ocr.layout.rules import LayoutElement, LayoutRules
from ms_ocr.readers.pdf_reader import PageInfo, TextBlock

# Try to import layoutparser, but make it optional
try:
    import layoutparser as lp
    LAYOUTPARSER_AVAILABLE = True
except ImportError:
    LAYOUTPARSER_AVAILABLE = False


class LayoutDetector:
    """Detect layout elements in pages."""

    def __init__(self, use_ml: bool = False):
        """Initialize layout detector.

        Args:
            use_ml: Whether to use ML-based detection (layoutparser)
        """
        self.use_ml = use_ml
        self.rules = LayoutRules()

        if use_ml and LAYOUTPARSER_AVAILABLE:
            try:
                # Load a pre-trained model (CPU version)
                self.model = lp.Detectron2LayoutModel(
                    "lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config",
                    extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
                    label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
                )
            except Exception as e:
                # Fallback to rules-based if ML fails
                self.use_ml = False
                self.model = None
        else:
            self.use_ml = False
            self.model = None

    def detect(
        self, page_info: PageInfo, exclude_headers_footers: Optional[tuple] = None
    ) -> List[LayoutElement]:
        """Detect layout elements in a page.

        Args:
            page_info: Page information
            exclude_headers_footers: Tuple of (header_texts, footer_texts) to exclude

        Returns:
            List of layout elements
        """
        if self.use_ml and self.model:
            return self._detect_ml(page_info, exclude_headers_footers)
        else:
            return self._detect_rules(page_info, exclude_headers_footers)

    def _detect_rules(
        self, page_info: PageInfo, exclude_headers_footers: Optional[tuple] = None
    ) -> List[LayoutElement]:
        """Detect layout using rules.

        Args:
            page_info: Page information
            exclude_headers_footers: Tuple of (header_texts, footer_texts) to exclude

        Returns:
            List of layout elements
        """
        elements = []
        headers, footers = exclude_headers_footers or (set(), set())

        for block in page_info.text_blocks:
            # Skip headers/footers
            if block.text.strip() in headers or block.text.strip() in footers:
                continue

            element = self.rules.classify_block(block)
            elements.append(element)

        return elements

    def _detect_ml(
        self, page_info: PageInfo, exclude_headers_footers: Optional[tuple] = None
    ) -> List[LayoutElement]:
        """Detect layout using ML model.

        Args:
            page_info: Page information
            exclude_headers_footers: Tuple of (header_texts, footer_texts) to exclude

        Returns:
            List of layout elements
        """
        # This is a simplified implementation
        # In practice, you'd render the page as image and run detection
        # For now, fallback to rules
        return self._detect_rules(page_info, exclude_headers_footers)

    def merge_elements(self, elements: List[LayoutElement]) -> List[LayoutElement]:
        """Merge adjacent elements of same type.

        Args:
            elements: List of layout elements

        Returns:
            Merged list
        """
        if not elements:
            return []

        merged = []
        current = elements[0]

        for element in elements[1:]:
            # Merge consecutive paragraphs
            if (
                current.type == "paragraph"
                and element.type == "paragraph"
                and element.page_num == current.page_num
            ):
                current.text += " " + element.text
            else:
                merged.append(current)
                current = element

        merged.append(current)
        return merged
