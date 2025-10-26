"""File system utilities."""

import shutil
from pathlib import Path
from typing import List, Union


def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if not.

    Args:
        path: Directory path

    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_pdf_files(path: Union[str, Path]) -> List[Path]:
    """Get all PDF files from a path (file or directory).

    Args:
        path: File or directory path

    Returns:
        List of PDF file paths
    """
    path = Path(path)

    if path.is_file():
        if path.suffix.lower() == ".pdf":
            return [path]
        else:
            raise ValueError(f"File {path} is not a PDF")

    if path.is_dir():
        return sorted(path.glob("*.pdf"))

    raise ValueError(f"Path {path} does not exist")


def clean_filename(filename: str) -> str:
    """Clean filename for safe file system usage.

    Args:
        filename: Original filename

    Returns:
        Cleaned filename
    """
    # Remove or replace problematic characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")

    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:195] + (f".{ext}" if ext else "")

    return filename


def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> Path:
    """Copy file to destination.

    Args:
        src: Source file path
        dst: Destination file path

    Returns:
        Destination path
    """
    src = Path(src)
    dst = Path(dst)

    if not src.exists():
        raise FileNotFoundError(f"Source file {src} not found")

    ensure_dir(dst.parent)
    shutil.copy2(src, dst)

    return dst


def get_output_paths(input_path: Path, output_dir: Path, formats: List[str]) -> dict:
    """Generate output file paths for different formats.

    Args:
        input_path: Input PDF path
        output_dir: Output directory
        formats: List of output formats (md, json, docx)

    Returns:
        Dictionary mapping format to output path
    """
    stem = input_path.stem
    paths = {}

    for fmt in formats:
        if fmt == "md":
            paths["md"] = output_dir / f"{stem}.md"
        elif fmt == "json":
            paths["json"] = output_dir / f"{stem}.gamma.json"
        elif fmt == "docx":
            paths["docx"] = output_dir / f"{stem}.docx"

    return paths
