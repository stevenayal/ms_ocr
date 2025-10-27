#!/usr/bin/env python3
"""Convert Markdown to Gamma text format with slide separators."""

import re
import sys
from pathlib import Path


def convert_md_to_gamma(md_path: Path, output_path: Path, brand_name: str = "AIQUAA"):
    """Convert markdown to Gamma format.

    Args:
        md_path: Input markdown file
        output_path: Output gamma text file
        brand_name: Brand name for cover
    """
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove frontmatter
    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

    lines = content.split('\n')
    slides = []
    current_slide = []
    current_title = None
    slide_content = []

    for line in lines:
        line = line.strip()

        # Skip empty lines at start
        if not line and not current_slide and not slide_content:
            continue

        # Skip page markers
        if line.startswith('<!--') and 'Page' in line:
            continue

        # Skip copyright notices
        if 'Testing IT Consulting' in line or 'prohibida su reproducción' in line:
            continue

        # Detect headings
        if line.startswith('# '):
            # H1 - Major section or title
            text = line[2:].strip()
            if text and len(text) > 3:
                # Flush previous slide
                if current_title and slide_content:
                    slides.append((current_title, slide_content[:]))
                    slide_content = []

                # Check if it's a section number
                if re.match(r'^\d+\.', text):
                    # It's a numbered section - make it a divider
                    slides.append(('SECTION', [text]))
                    current_title = None
                else:
                    current_title = text

        elif line.startswith('## '):
            # H2 - Subsection
            text = line[3:].strip()
            if text and len(text) > 3:
                # Flush previous slide
                if current_title and slide_content:
                    slides.append((current_title, slide_content[:]))
                    slide_content = []
                current_title = text

        elif line.startswith('### ') or line.startswith('#### '):
            # H3/H4 - Sub-subsection
            text = line.lstrip('#').strip()
            if text and len(text) > 3:
                # Flush previous slide
                if current_title and slide_content:
                    slides.append((current_title, slide_content[:]))
                    slide_content = []
                current_title = text

        elif line.startswith('- ') or line.startswith('* '):
            # Bullet point
            text = line[2:].strip()
            if text and len(text) > 2:
                slide_content.append(f"- {text}")

                # Auto-flush if too many bullets
                if len(slide_content) >= 6:
                    if current_title:
                        slides.append((current_title, slide_content[:]))
                        slide_content = []

        elif re.match(r'^\d+\. ', line):
            # Numbered list
            text = re.sub(r'^\d+\. ', '', line).strip()
            if text and len(text) > 2:
                slide_content.append(f"- {text}")

        elif line and not line.startswith('|') and not line.startswith('---'):
            # Regular paragraph
            if len(line) > 20:
                # Only add substantial paragraphs
                if len(line) < 300:
                    slide_content.append(f"- {line}")
                else:
                    # Long paragraph - split or summarize
                    words = line.split()
                    if len(words) > 30:
                        # Take first sentence or 30 words
                        short = ' '.join(words[:30]) + '...'
                        slide_content.append(f"- {short}")

                # Auto-flush if too much content
                if len(slide_content) >= 5:
                    if current_title:
                        slides.append((current_title, slide_content[:]))
                        slide_content = []

    # Flush last slide
    if current_title and slide_content:
        slides.append((current_title, slide_content))

    # Merge consecutive slides with same title
    merged_slides = []
    i = 0
    while i < len(slides):
        title, content = slides[i]
        # Collect all consecutive slides with same title
        while i + 1 < len(slides) and slides[i + 1][0] == title:
            content.extend(slides[i + 1][1])
            i += 1
        merged_slides.append((title, content))
        i += 1

    # Write Gamma format
    with open(output_path, "w", encoding="utf-8") as f:
        # Cover slide
        doc_title = Path(md_path).stem.replace('ISTQB CTFL_v4.0_Syll2023-C', 'ISTQB CTFL Capítulo ').replace('-v1.0', '')
        f.write(f"# {doc_title}\n\n")
        f.write(f"**{brand_name}**\n\n")
        f.write("Fundamentos de Testing de Software\n\n")
        f.write("---\n\n")

        # Content slides
        for i, (title, content) in enumerate(merged_slides):
            if title == 'SECTION':
                # Section divider
                f.write(f"# {content[0]}\n\n")
                f.write("---\n\n")
            elif content:  # Only write if has content
                # Regular slide
                f.write(f"## {title}\n\n")
                # Limit bullets per slide
                for item in content[:8]:
                    f.write(f"{item}\n")
                f.write("\n---\n\n")

                # If too many bullets, create continuation slides
                if len(content) > 8:
                    remaining = content[8:]
                    chunk_size = 8
                    for j in range(0, len(remaining), chunk_size):
                        f.write(f"## {title} (cont.)\n\n")
                        for item in remaining[j:j+chunk_size]:
                            f.write(f"{item}\n")
                        f.write("\n---\n\n")

        # Closing slide
        f.write("# Gracias\n\n")
        f.write(f"**{brand_name}**\n\n")
        f.write(f"Total: {len(merged_slides)} slides principales\n")

    return len(merged_slides)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_md_to_gamma.py <markdown_file>")
        sys.exit(1)

    md_file = Path(sys.argv[1])
    output_file = md_file.with_suffix('.gamma.txt')

    num_slides = convert_md_to_gamma(md_file, output_file)
    print(f"OK - Created {output_file}")
    print(f"     {num_slides} slides generated")
