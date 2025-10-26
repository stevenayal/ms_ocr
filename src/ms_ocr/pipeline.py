"""Main processing pipeline."""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from ms_ocr.exporters.docx_exporter import DocxExporter
from ms_ocr.exporters.gamma_exporter import GammaExporter
from ms_ocr.exporters.md_exporter import MarkdownExporter
from ms_ocr.layout.detector import LayoutDetector
from ms_ocr.layout.rules import LayoutElement
from ms_ocr.ocr.ocr_engine import OCREngine
from ms_ocr.ocr.postprocess import TextPostProcessor, normalize_lists
from ms_ocr.readers.pdf_reader import PDFReader
from ms_ocr.tables.tables_extractor import TablesExtractor
from ms_ocr.utils.fs import ensure_dir, get_output_paths
from ms_ocr.utils.lang import detect_languages_multi
from ms_ocr.utils.logger import get_logger
from ms_ocr.utils.metrics import MetricsCollector, PageMetrics, Timer

logger = get_logger(__name__)


class ProcessingPipeline:
    """Main OCR processing pipeline."""

    def __init__(
        self,
        languages: List[str] = None,
        dpi: int = 300,
        min_confidence: int = 0,
        deskew: bool = True,
        denoise: bool = True,
        binarize: bool = True,
        use_layout_ml: bool = False,
        extract_tables: bool = True,
    ):
        """Initialize processing pipeline.

        Args:
            languages: OCR languages
            dpi: Image resolution for OCR
            min_confidence: Minimum OCR confidence
            deskew: Apply deskewing
            denoise: Apply denoising
            binarize: Apply binarization
            use_layout_ml: Use ML-based layout detection
            extract_tables: Extract tables
        """
        self.languages = languages or ["spa", "eng"]
        self.dpi = dpi
        self.min_confidence = min_confidence

        # Initialize components
        self.ocr_engine = OCREngine(
            languages=self.languages,
            min_confidence=min_confidence,
            preprocess=True,
            dpi=dpi,
            deskew=deskew,
            denoise=denoise,
            binarize=binarize,
        )

        self.layout_detector = LayoutDetector(use_ml=use_layout_ml)
        self.text_processor = TextPostProcessor()

        if extract_tables:
            self.table_extractor = TablesExtractor()
        else:
            self.table_extractor = None

    def process_pdf(
        self,
        pdf_path: Path,
        output_dir: Path,
        export_formats: List[str] = None,
        gamma_config: Optional[Dict] = None,
        logo_path: Optional[str] = None,
        page_filter: Optional[List[int]] = None,
    ) -> Dict:
        """Process a PDF file.

        Args:
            pdf_path: Input PDF path
            output_dir: Output directory
            export_formats: List of formats to export (md, json, docx)
            gamma_config: Gamma brand configuration
            logo_path: Logo file path
            page_filter: Optional list of page numbers to process

        Returns:
            Processing results dictionary
        """
        logger.info(f"Processing PDF: {pdf_path}")
        ensure_dir(output_dir)

        export_formats = export_formats or ["md"]
        metrics_collector = MetricsCollector(source_file=str(pdf_path))

        all_elements = []
        all_tables = []

        with PDFReader(pdf_path) as reader:
            total_pages = len(reader.doc)

            # Determine pages to process
            if page_filter:
                pages = [p for p in page_filter if 0 <= p < total_pages]
            else:
                pages = list(range(total_pages))

            logger.info(f"Processing {len(pages)} pages")

            # First pass: detect headers/footers
            blocks_by_page = []
            for page_num in pages:
                page_info = reader.get_page_info(page_num)
                blocks_by_page.append(page_info.text_blocks)

            headers, footers = self.layout_detector.rules.detect_headers_footers(blocks_by_page)

            # Process each page
            for page_num in pages:
                logger.info(f"Processing page {page_num + 1}/{total_pages}")

                with Timer() as page_timer:
                    page_metrics = self._process_page(
                        reader,
                        page_num,
                        (headers, footers),
                        all_elements,
                        all_tables,
                    )

                page_metrics.processing_time = page_timer.elapsed
                metrics_collector.add_page(page_metrics)

        # Detect languages
        all_text = " ".join([e.text for e in all_elements])
        detected_langs = detect_languages_multi(all_text)
        metrics_collector.set_languages(detected_langs)

        # Merge elements
        all_elements = self.layout_detector.merge_elements(all_elements)

        # Export
        output_paths = get_output_paths(pdf_path, output_dir, export_formats)

        if "md" in export_formats:
            self._export_markdown(
                all_elements, all_tables, output_paths["md"], pdf_path, detected_langs
            )

        if "json" in export_formats:
            self._export_gamma(
                all_elements,
                all_tables,
                output_paths["json"],
                pdf_path,
                detected_langs,
                gamma_config,
                logo_path,
            )

        if "docx" in export_formats:
            self._export_docx(all_elements, all_tables, output_paths["docx"], pdf_path)

        # Save metrics
        metrics_path = output_dir / f"{pdf_path.stem}.metrics.json"
        metrics_collector.save(metrics_path)

        logger.info(f"Processing complete: {pdf_path}")

        return {
            "source": str(pdf_path),
            "output_dir": str(output_dir),
            "pages_processed": len(pages),
            "elements": len(all_elements),
            "tables": len(all_tables),
            "languages": detected_langs,
            "outputs": {k: str(v) for k, v in output_paths.items()},
            "metrics": str(metrics_path),
        }

    def _process_page(
        self,
        reader: PDFReader,
        page_num: int,
        exclude_headers_footers: tuple,
        all_elements: List[LayoutElement],
        all_tables: List,
    ) -> PageMetrics:
        """Process a single page.

        Args:
            reader: PDF reader
            page_num: Page number
            exclude_headers_footers: Tuple of (headers, footers) to exclude
            all_elements: List to append elements to
            all_tables: List to append tables to

        Returns:
            Page metrics
        """
        stage_times = {}

        # Get page info
        with Timer() as t:
            page_info = reader.get_page_info(page_num)
        stage_times["page_info"] = t.elapsed

        # Determine if OCR is needed
        needs_ocr = reader.needs_ocr(page_num)
        ocr_confidence = None

        if needs_ocr:
            # Extract as image and OCR
            with Timer() as t:
                image = reader.extract_page_as_image(page_num, dpi=self.dpi)
                ocr_result = self.ocr_engine.extract_text(image)
            stage_times["ocr"] = t.elapsed

            ocr_confidence = ocr_result.confidence

            # Post-process text
            with Timer() as t:
                processed_text = self.text_processor.process(ocr_result.text)
                processed_text = normalize_lists(processed_text)
            stage_times["postprocess"] = t.elapsed

            # Create synthetic layout elements from OCR text
            # (Simplified - in reality, would use word positions)
            lines = processed_text.split("\n")
            for line in lines:
                if line.strip():
                    # Simple heuristic classification
                    element = self._classify_ocr_line(line, page_num)
                    all_elements.append(element)

        else:
            # Use native text with layout detection
            with Timer() as t:
                elements = self.layout_detector.detect(page_info, exclude_headers_footers)
                all_elements.extend(elements)
            stage_times["layout"] = t.elapsed

        # Extract tables
        tables_count = 0
        if self.table_extractor:
            with Timer() as t:
                tables = self.table_extractor.extract_from_pdf(reader.pdf_path, page_num)
                all_tables.extend(tables)
                tables_count = len(tables)
            stage_times["tables"] = t.elapsed

        # Calculate text density
        text_density = page_info.text_density if not needs_ocr else 0.0

        return PageMetrics(
            page_num=page_num,
            native_text_ratio=1.0 - text_density if needs_ocr else text_density,
            ocr_confidence=ocr_confidence,
            words_corrected=self.text_processor.words_corrected,
            tables_detected=tables_count,
            processing_time=0,  # Set by caller
            stages=stage_times,
        )

    def _classify_ocr_line(self, line: str, page_num: int) -> LayoutElement:
        """Classify an OCR text line into a layout element.

        Args:
            line: Text line
            page_num: Page number

        Returns:
            Layout element
        """
        import re

        text = line.strip()

        # Check for section numbers
        if re.match(r"^\d+(?:\.\d+)*\s+", text):
            section_match = re.match(r"^(\d+(?:\.\d+)*)\s+(.+)$", text)
            section_num = section_match.group(1)
            level = len(section_num.split("."))
            return LayoutElement(type="heading", text=text, level=level, page_num=page_num)

        # Check for list items
        if re.match(r"^[•●○■□▪▫\-\*]\s+", text) or re.match(r"^\d+[\.)]\s+", text):
            return LayoutElement(type="list_item", text=text, page_num=page_num)

        # Check for all caps (potential heading)
        if text.isupper() and len(text) > 5 and len(text) < 100:
            return LayoutElement(type="heading", text=text, level=2, page_num=page_num)

        # Default: paragraph
        return LayoutElement(type="paragraph", text=text, page_num=page_num)

    def _export_markdown(
        self,
        elements: List[LayoutElement],
        tables: List,
        output_path: Path,
        pdf_path: Path,
        languages: List[str],
    ):
        """Export to Markdown.

        Args:
            elements: Layout elements
            tables: Tables
            output_path: Output path
            pdf_path: Source PDF path
            languages: Detected languages
        """
        logger.info(f"Exporting to Markdown: {output_path}")

        metadata = {
            "title": pdf_path.stem,
            "source": str(pdf_path),
            "languages": languages,
            "generated_by": "ms-ocr",
        }

        exporter = MarkdownExporter()
        exporter.export(elements, tables, output_path, metadata)

    def _export_gamma(
        self,
        elements: List[LayoutElement],
        tables: List,
        output_path: Path,
        pdf_path: Path,
        languages: List[str],
        gamma_config: Optional[Dict],
        logo_path: Optional[str],
    ):
        """Export to Gamma JSON.

        Args:
            elements: Layout elements
            tables: Tables
            output_path: Output path
            pdf_path: Source PDF path
            languages: Detected languages
            gamma_config: Brand configuration
            logo_path: Logo path
        """
        logger.info(f"Exporting to Gamma JSON: {output_path}")

        exporter = GammaExporter(brand_config=gamma_config, logo_path=logo_path)

        metadata = {"pages": len(set(e.page_num for e in elements)), "languages": languages}

        exporter.export(elements, tables, output_path, str(pdf_path), metadata)

    def _export_docx(
        self, elements: List[LayoutElement], tables: List, output_path: Path, pdf_path: Path
    ):
        """Export to DOCX.

        Args:
            elements: Layout elements
            tables: Tables
            output_path: Output path
            pdf_path: Source PDF path
        """
        logger.info(f"Exporting to DOCX: {output_path}")

        exporter = DocxExporter()
        exporter.export(elements, tables, output_path, title=pdf_path.stem)
