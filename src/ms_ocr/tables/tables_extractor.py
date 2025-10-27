"""Table extraction from PDF pages."""

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pandas as pd
from PIL import Image

from ms_ocr.utils.logger import get_logger

# Try to import camelot, but make it optional
try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False

# Try to import tabula, but make it optional
try:
    import tabula
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False

logger = get_logger(__name__)


@dataclass
class Table:
    """Extracted table data."""

    data: pd.DataFrame
    page_num: int
    bbox: Optional[tuple] = None
    confidence: float = 0.0
    method: str = "camelot"  # camelot, tabula, or ocr

    def to_markdown(self) -> str:
        """Convert table to markdown format.

        Returns:
            Markdown table string
        """
        if self.data.empty:
            return ""

        return self.data.to_markdown(index=False)

    def to_dict(self) -> dict:
        """Convert table to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "data": self.data.to_dict(orient="records"),
            "page_num": self.page_num,
            "confidence": self.confidence,
            "method": self.method,
        }


class TablesExtractor:
    """Extract tables from PDF pages."""

    def __init__(
        self,
        method: str = "auto",  # auto, camelot, tabula
        min_confidence: float = 0.5,
    ):
        """Initialize table extractor.

        Args:
            method: Extraction method
            min_confidence: Minimum confidence threshold
        """
        self.method = method
        self.min_confidence = min_confidence

    def extract_from_pdf(self, pdf_path: Path, page_num: int) -> List[Table]:
        """Extract tables from a PDF page.

        Args:
            pdf_path: PDF file path
            page_num: Page number (0-indexed, but methods use 1-indexed)

        Returns:
            List of extracted tables
        """
        tables = []

        # Convert to 1-indexed for camelot/tabula
        page_str = str(page_num + 1)

        if self.method in ("auto", "camelot") and CAMELOT_AVAILABLE:
            tables.extend(self._extract_camelot(pdf_path, page_str))

        if self.method in ("auto", "tabula") and not tables and TABULA_AVAILABLE:
            tables.extend(self._extract_tabula(pdf_path, page_str))

        # Filter by confidence
        tables = [t for t in tables if t.confidence >= self.min_confidence]

        # Set page numbers (convert back to 0-indexed)
        for table in tables:
            table.page_num = page_num

        return tables

    def _extract_camelot(self, pdf_path: Path, page_str: str) -> List[Table]:
        """Extract tables using Camelot.

        Args:
            pdf_path: PDF file path
            page_str: Page number as string (1-indexed)

        Returns:
            List of tables
        """
        tables = []

        try:
            # Try lattice mode (for tables with lines)
            camelot_tables = camelot.read_pdf(
                str(pdf_path), pages=page_str, flavor="lattice", suppress_stdout=True
            )

            if len(camelot_tables) == 0:
                # Try stream mode (for tables without lines)
                camelot_tables = camelot.read_pdf(
                    str(pdf_path), pages=page_str, flavor="stream", suppress_stdout=True
                )

            for ct in camelot_tables:
                df = ct.df

                # Clean up table
                df = self._clean_dataframe(df)

                if not df.empty:
                    tables.append(
                        Table(
                            data=df,
                            page_num=0,  # Will be set by caller
                            bbox=ct._bbox if hasattr(ct, "_bbox") else None,
                            confidence=ct.accuracy / 100 if hasattr(ct, "accuracy") else 0.8,
                            method="camelot",
                        )
                    )

        except Exception as e:
            logger.warning(f"Camelot extraction failed: {e}")

        return tables

    def _extract_tabula(self, pdf_path: Path, page_str: str) -> List[Table]:
        """Extract tables using Tabula.

        Args:
            pdf_path: PDF file path
            page_str: Page number as string (1-indexed)

        Returns:
            List of tables
        """
        tables = []

        try:
            # Tabula returns list of DataFrames
            dfs = tabula.read_pdf(
                str(pdf_path),
                pages=page_str,
                multiple_tables=True,
                pandas_options={"header": None},
            )

            for df in dfs:
                df = self._clean_dataframe(df)

                if not df.empty:
                    tables.append(
                        Table(
                            data=df,
                            page_num=0,
                            confidence=0.7,  # Tabula doesn't provide confidence
                            method="tabula",
                        )
                    )

        except Exception as e:
            logger.warning(f"Tabula extraction failed: {e}")

        return tables

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean extracted dataframe.

        Args:
            df: Raw dataframe

        Returns:
            Cleaned dataframe
        """
        if df.empty:
            return df

        # Remove completely empty rows
        df = df.dropna(how="all")

        # Remove completely empty columns
        df = df.dropna(axis=1, how="all")

        # Try to detect header row
        if len(df) > 1:
            # If first row has distinct values, use as header
            first_row = df.iloc[0]
            if first_row.notna().sum() > len(df.columns) * 0.5:
                df.columns = first_row
                df = df.iloc[1:]
                df = df.reset_index(drop=True)

        # Clean cell values
        df = df.applymap(lambda x: str(x).strip() if pd.notna(x) else "")

        return df

    def extract_from_image(self, image: Image.Image, ocr_engine=None) -> Optional[Table]:
        """Extract table from image using OCR.

        Args:
            image: PIL Image
            ocr_engine: OCR engine instance

        Returns:
            Extracted table or None
        """
        # This is a simplified implementation
        # A real implementation would:
        # 1. Detect table grid lines using OpenCV
        # 2. Segment cells
        # 3. OCR each cell
        # 4. Construct DataFrame

        logger.warning("Image-based table extraction not fully implemented")
        return None


def detect_table_regions(page_info) -> List[tuple]:
    """Detect potential table regions in a page.

    Args:
        page_info: PageInfo object

    Returns:
        List of bounding boxes
    """
    # Simplified table detection based on layout
    # Real implementation would use OpenCV or layout models
    return []
