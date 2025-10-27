#!/usr/bin/env python3
"""Smart converter from Markdown to Gamma - uses section numbers and groups content."""

import re
from pathlib import Path
from collections import defaultdict


def create_gamma_smart(md_path: Path, output_path: Path, brand="AIQUAA"):
    """Create Gamma presentation from markdown using smart grouping.

    Args:
        md_path: Input markdown path
        output_path: Output gamma text path
        brand: Brand name
    """
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Remove frontmatter
    in_frontmatter = False
    content_lines = []
    for line in lines:
        if line.strip() == '---':
            in_frontmatter = not in_frontmatter
            continue
        if not in_frontmatter:
            content_lines.append(line)

    # Group content by section numbers (1.1, 1.2, etc.)
    sections = defaultdict(list)
    current_section = None
    current_title = None

    for line in content_lines:
        line_stripped = line.strip()

        # Skip page markers and copyright
        if not line_stripped or '<!--' in line_stripped or 'Testing IT Consulting' in line_stripped:
            continue
        if 'prohibida su reproducción' in line_stripped or line_stripped.startswith('####'):
            continue

        # Detect section numbers
        match = re.match(r'^#+ (\d+(?:\.\d+)*)\s+(.+)$', line_stripped)
        if match:
            section_num = match.group(1)
            section_title = match.group(2)
            current_section = f"{section_num} {section_title}"
            current_title = section_title
            sections[current_section] = []
            continue

        # Add content to current section
        if current_section and line_stripped:
            # Remove # from lines that aren't section headers
            cleaned = line_stripped.lstrip('#').strip()
            if cleaned and len(cleaned) > 3:
                sections[current_section].append(cleaned)

    # Write Gamma format
    with open(output_path, "w", encoding="utf-8") as f:
        # Cover
        doc_name = Path(md_path).stem.replace('ISTQB CTFL_v4.0_Syll2023-C', 'Capítulo ')
        f.write(f"# ISTQB CTFL v4.0\n\n")
        f.write(f"## {doc_name}\n\n")
        f.write(f"**{brand}**\n\n")
        f.write("---\n\n")

        # Content slides
        slide_count = 0
        for section, content in sorted(sections.items()):
            if not content:
                continue

            # Section divider for main sections (1.1, 1.2, not 1.1.1)
            if re.match(r'^\d+\.\d+\s', section) and section.count('.') == 1:
                f.write(f"# {section}\n\n")
                f.write("---\n\n")
                slide_count += 1

            # Content slide
            f.write(f"## {section}\n\n")

            # Group content into bullets (max 8 per slide)
            bullets = []
            for item in content:
                if len(item) < 500:  # Skip very long items
                    bullets.append(item)

            # Write bullets in chunks
            for i in range(0, len(bullets), 8):
                if i > 0:
                    f.write(f"## {section} (cont.)\n\n")

                for bullet in bullets[i:i+8]:
                    f.write(f"- {bullet}\n")

                f.write("\n---\n\n")
                slide_count += 1

        # Closing
        f.write("# Gracias\n\n")
        f.write(f"**{brand}**\n\n")
        f.write(f"\nTotal: {slide_count} slides\n")

    return slide_count


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python create_gamma_smart.py <markdown_file>")
        sys.exit(1)

    md_file = Path(sys.argv[1])
    output_file = md_file.parent / f"{md_file.stem}.gamma.txt"

    slides = create_gamma_smart(md_file, output_file)
    print(f"OK - Created: {output_file}")
    print(f"     {slides} slides")
