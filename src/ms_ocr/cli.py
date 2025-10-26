"""Command-line interface for ms-ocr."""

import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from tqdm import tqdm

from ms_ocr.pipeline import ProcessingPipeline
from ms_ocr.utils.fs import get_pdf_files
from ms_ocr.utils.logger import setup_logger

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """ms-ocr - High-quality PDF text extraction with OCR."""
    pass


@cli.command()
@click.option(
    "--input",
    "-i",
    "input_path",
    required=True,
    type=click.Path(exists=True),
    help="Input PDF file or directory",
)
@click.option(
    "--out",
    "-o",
    "output_dir",
    required=True,
    type=click.Path(),
    help="Output directory",
)
@click.option(
    "--lang",
    default="spa,eng",
    help="OCR languages (comma-separated, e.g., spa,eng)",
)
@click.option(
    "--gamma",
    is_flag=True,
    help="Generate Gamma JSON output",
)
@click.option(
    "--brand",
    type=click.Path(exists=True),
    help="Brand configuration JSON file",
)
@click.option(
    "--logo",
    type=click.Path(exists=True),
    help="Logo file path",
)
@click.option(
    "--dpi",
    default=300,
    type=int,
    help="Image resolution for OCR (default: 300)",
)
@click.option(
    "--deskew/--no-deskew",
    default=True,
    help="Apply deskewing (default: enabled)",
)
@click.option(
    "--denoise/--no-denoise",
    default=True,
    help="Apply denoising (default: enabled)",
)
@click.option(
    "--binarize/--no-binarize",
    default=True,
    help="Apply binarization (default: enabled)",
)
@click.option(
    "--keep-layout",
    is_flag=True,
    help="Preserve layout and line breaks",
)
@click.option(
    "--min-conf",
    default=0,
    type=int,
    help="Minimum OCR confidence threshold (0-100)",
)
@click.option(
    "--pages",
    help="Page numbers to process (e.g., 1,3-10)",
)
@click.option(
    "--merge",
    is_flag=True,
    help="Merge multiple PDFs into single output",
)
@click.option(
    "--export",
    default="md,json",
    help="Export formats (comma-separated: md,json,docx)",
)
@click.option(
    "--workers",
    default=1,
    type=int,
    help="Number of parallel workers (default: 1)",
)
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    help="Logging level",
)
@click.option(
    "--log-file",
    type=click.Path(),
    help="Log file path",
)
def extract(
    input_path: str,
    output_dir: str,
    lang: str,
    gamma: bool,
    brand: Optional[str],
    logo: Optional[str],
    dpi: int,
    deskew: bool,
    denoise: bool,
    binarize: bool,
    keep_layout: bool,
    min_conf: int,
    pages: Optional[str],
    merge: bool,
    export: str,
    workers: int,
    log_level: str,
    log_file: Optional[str],
):
    """Extract text from PDF files using OCR."""
    # Setup logging
    log_path = Path(log_file) if log_file else None
    setup_logger(log_path, level=log_level)

    # Parse parameters
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    languages = [l.strip() for l in lang.split(",")]

    export_formats = [f.strip() for f in export.split(",")]
    if gamma and "json" not in export_formats:
        export_formats.append("json")

    # Load brand config
    brand_config = None
    if brand:
        with open(brand, "r") as f:
            brand_config = json.load(f)

    # Parse page filter
    page_filter = _parse_page_range(pages) if pages else None

    # Get PDF files
    try:
        pdf_files = get_pdf_files(input_path)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    if not pdf_files:
        console.print("[yellow]No PDF files found.[/yellow]")
        sys.exit(0)

    console.print(f"[green]Found {len(pdf_files)} PDF file(s)[/green]")

    # Initialize pipeline
    pipeline = ProcessingPipeline(
        languages=languages,
        dpi=dpi,
        min_confidence=min_conf,
        deskew=deskew,
        denoise=denoise,
        binarize=binarize,
        use_layout_ml=False,  # Can be made configurable
        extract_tables=True,
    )

    # Process files
    if workers > 1 and len(pdf_files) > 1:
        _process_parallel(
            pdf_files,
            output_dir,
            pipeline,
            export_formats,
            brand_config,
            logo,
            page_filter,
            workers,
        )
    else:
        _process_sequential(
            pdf_files,
            output_dir,
            pipeline,
            export_formats,
            brand_config,
            logo,
            page_filter,
        )

    console.print(f"\n[bold green]✓ Processing complete![/bold green]")
    console.print(f"Output directory: {output_dir}")


def _process_sequential(
    pdf_files: List[Path],
    output_dir: Path,
    pipeline: ProcessingPipeline,
    export_formats: List[str],
    brand_config: Optional[dict],
    logo: Optional[str],
    page_filter: Optional[List[int]],
):
    """Process PDF files sequentially.

    Args:
        pdf_files: List of PDF paths
        output_dir: Output directory
        pipeline: Processing pipeline
        export_formats: Export formats
        brand_config: Brand configuration
        logo: Logo path
        page_filter: Page filter
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for pdf_file in pdf_files:
            task = progress.add_task(f"Processing {pdf_file.name}...", total=None)

            try:
                result = pipeline.process_pdf(
                    pdf_path=pdf_file,
                    output_dir=output_dir,
                    export_formats=export_formats,
                    gamma_config=brand_config,
                    logo_path=logo,
                    page_filter=page_filter,
                )

                progress.update(
                    task,
                    description=f"✓ {pdf_file.name} ({result['pages_processed']} pages)",
                )
            except Exception as e:
                progress.update(task, description=f"✗ {pdf_file.name} - Error: {e}")
                console.print(f"[red]Error processing {pdf_file}: {e}[/red]")


def _process_parallel(
    pdf_files: List[Path],
    output_dir: Path,
    pipeline: ProcessingPipeline,
    export_formats: List[str],
    brand_config: Optional[dict],
    logo: Optional[str],
    page_filter: Optional[List[int]],
    workers: int,
):
    """Process PDF files in parallel.

    Args:
        pdf_files: List of PDF paths
        output_dir: Output directory
        pipeline: Processing pipeline
        export_formats: Export formats
        brand_config: Brand configuration
        logo: Logo path
        page_filter: Page filter
        workers: Number of workers
    """
    console.print(f"Processing {len(pdf_files)} files with {workers} workers...")

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                pipeline.process_pdf,
                pdf_file,
                output_dir,
                export_formats,
                brand_config,
                logo,
                page_filter,
            ): pdf_file
            for pdf_file in pdf_files
        }

        with tqdm(total=len(pdf_files), desc="Processing PDFs") as pbar:
            for future in as_completed(futures):
                pdf_file = futures[future]
                try:
                    result = future.result()
                    pbar.set_postfix_str(f"✓ {pdf_file.name}")
                except Exception as e:
                    console.print(f"[red]Error processing {pdf_file}: {e}[/red]")
                finally:
                    pbar.update(1)


def _parse_page_range(page_str: str) -> List[int]:
    """Parse page range string.

    Args:
        page_str: Page range string (e.g., "1,3-5,7")

    Returns:
        List of page numbers (0-indexed)
    """
    pages = set()

    for part in page_str.split(","):
        if "-" in part:
            start, end = part.split("-")
            pages.update(range(int(start) - 1, int(end)))
        else:
            pages.add(int(part) - 1)

    return sorted(pages)


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
