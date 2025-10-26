"""JSON schemas for Gamma export."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BrandConfig(BaseModel):
    """Brand configuration for Gamma."""

    name: str = Field(description="Brand name")
    logo: Optional[str] = Field(None, description="Logo file path")
    primary: str = Field("#0F172A", description="Primary color (hex)")
    secondary: str = Field("#22C55E", description="Secondary color (hex)")
    accent: str = Field("#06B6D4", description="Accent color (hex)")
    footer: Optional[str] = Field(None, description="Footer text")


class GammaSlide(BaseModel):
    """Single Gamma slide."""

    type: str = Field(description="Slide type: cover, section, bullets, table, image")
    title: str = Field(description="Slide title")
    subtitle: Optional[str] = Field(None, description="Subtitle (for cover slides)")
    items: Optional[List[str]] = Field(None, description="Bullet items")
    md: Optional[str] = Field(None, description="Markdown content (for tables)")
    image: Optional[str] = Field(None, description="Image path")
    notes: Optional[str] = Field(None, description="Speaker notes")
    logo: Optional[str] = Field(None, description="Logo for this slide")


class GammaMeta(BaseModel):
    """Metadata for Gamma presentation."""

    pages: int = Field(description="Number of source pages")
    lang: List[str] = Field(description="Languages detected")
    generated_by: str = Field("ms-ocr", description="Generator")
    version: str = Field("0.1.0", description="Version")


class GammaPresentation(BaseModel):
    """Complete Gamma presentation structure."""

    brand: BrandConfig = Field(description="Brand configuration")
    title: str = Field(description="Presentation title")
    slides: List[GammaSlide] = Field(description="List of slides")
    source: str = Field(description="Source PDF file")
    meta: GammaMeta = Field(description="Metadata")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return self.model_dump(exclude_none=True)


def create_cover_slide(
    title: str, subtitle: Optional[str] = None, logo: Optional[str] = None
) -> GammaSlide:
    """Create a cover slide.

    Args:
        title: Presentation title
        subtitle: Optional subtitle
        logo: Optional logo path

    Returns:
        Cover slide
    """
    return GammaSlide(type="cover", title=title, subtitle=subtitle, logo=logo)


def create_section_slide(title: str) -> GammaSlide:
    """Create a section divider slide.

    Args:
        title: Section title

    Returns:
        Section slide
    """
    return GammaSlide(type="section", title=title)


def create_bullets_slide(
    title: str, items: List[str], notes: Optional[str] = None
) -> GammaSlide:
    """Create a bullet points slide.

    Args:
        title: Slide title
        items: List of bullet points
        notes: Optional speaker notes

    Returns:
        Bullets slide
    """
    return GammaSlide(type="bullets", title=title, items=items, notes=notes)


def create_table_slide(title: str, markdown_table: str) -> GammaSlide:
    """Create a table slide.

    Args:
        title: Slide title
        markdown_table: Table in markdown format

    Returns:
        Table slide
    """
    return GammaSlide(type="table", title=title, md=markdown_table)


def create_image_slide(title: str, image_path: str) -> GammaSlide:
    """Create an image slide.

    Args:
        title: Slide title
        image_path: Path to image

    Returns:
        Image slide
    """
    return GammaSlide(type="image", title=title, image=image_path)
