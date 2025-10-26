"""Metrics collection and reporting."""

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class PageMetrics:
    """Metrics for a single page."""

    page_num: int
    native_text_ratio: float  # 0.0 to 1.0
    ocr_confidence: Optional[float]  # 0 to 100
    words_corrected: int
    tables_detected: int
    processing_time: float  # seconds
    stages: Dict[str, float] = field(default_factory=dict)  # stage -> time


@dataclass
class DocumentMetrics:
    """Metrics for entire document."""

    source_file: str
    total_pages: int
    pages_ocr: int
    pages_native: int
    avg_ocr_confidence: Optional[float]
    total_words_corrected: int
    total_tables: int
    total_time: float
    languages: List[str]
    page_metrics: List[PageMetrics] = field(default_factory=list)


class MetricsCollector:
    """Collect and aggregate metrics during processing."""

    def __init__(self, source_file: str):
        """Initialize metrics collector.

        Args:
            source_file: Source PDF filename
        """
        self.source_file = source_file
        self.page_metrics: List[PageMetrics] = []
        self.start_time = time.time()
        self.languages: List[str] = []

    def add_page(self, metrics: PageMetrics) -> None:
        """Add page metrics.

        Args:
            metrics: Page metrics
        """
        self.page_metrics.append(metrics)

    def set_languages(self, languages: List[str]) -> None:
        """Set detected languages.

        Args:
            languages: List of language codes
        """
        self.languages = languages

    def finalize(self) -> DocumentMetrics:
        """Finalize and compute document metrics.

        Returns:
            Document metrics
        """
        total_time = time.time() - self.start_time

        pages_ocr = sum(1 for p in self.page_metrics if p.ocr_confidence is not None)
        pages_native = len(self.page_metrics) - pages_ocr

        # Compute average OCR confidence
        ocr_confidences = [p.ocr_confidence for p in self.page_metrics if p.ocr_confidence]
        avg_ocr_confidence = (
            sum(ocr_confidences) / len(ocr_confidences) if ocr_confidences else None
        )

        total_words_corrected = sum(p.words_corrected for p in self.page_metrics)
        total_tables = sum(p.tables_detected for p in self.page_metrics)

        return DocumentMetrics(
            source_file=self.source_file,
            total_pages=len(self.page_metrics),
            pages_ocr=pages_ocr,
            pages_native=pages_native,
            avg_ocr_confidence=avg_ocr_confidence,
            total_words_corrected=total_words_corrected,
            total_tables=total_tables,
            total_time=total_time,
            languages=self.languages,
            page_metrics=self.page_metrics,
        )

    def save(self, output_path: Path) -> None:
        """Save metrics to JSON file.

        Args:
            output_path: Output JSON path
        """
        metrics = self.finalize()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(asdict(metrics), f, indent=2, ensure_ascii=False)


class Timer:
    """Context manager for timing operations."""

    def __init__(self):
        """Initialize timer."""
        self.start: float = 0.0
        self.elapsed: float = 0.0

    def __enter__(self):
        """Start timer."""
        self.start = time.time()
        return self

    def __exit__(self, *args):
        """Stop timer."""
        self.elapsed = time.time() - self.start
