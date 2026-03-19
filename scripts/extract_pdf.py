"""
Extract text from Erickson's Fundamentals of Power Electronics PDF.
Outputs structured text for knowledge base processing.
"""

import sys
from pathlib import Path

def extract_pdf(
    pdf_path: str,
    output_dir: str = None,
    start_page: int = 0,
    end_page: int = None,
    append: bool = False,
):
    """Extract text from PDF by page range.
    Args:
        pdf_path: Path to PDF
        output_dir: Output directory
        start_page: First page (0-indexed)
        end_page: Last page (exclusive). None = full book.
        append: If True, append to existing file; else overwrite.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        print("Install pypdf: pip install pypdf")
        return

    reader = PdfReader(pdf_path)
    total = len(reader.pages)
    end_page = end_page if end_page is not None else total
    end_page = min(end_page, total)
    print(f"Extracting pages {start_page+1}-{end_page} of {total}")

    output_path = Path(output_dir or ".") / "erickson_extracted.txt"
    mode = "a" if append else "w"

    with open(output_path, mode, encoding="utf-8") as f:
        for i in range(start_page, end_page):
            page = reader.pages[i]
            text = page.extract_text()
            if text:
                f.write(f"\n\n--- PAGE {i+1} ---\n\n")
                f.write(text)
            if (i - start_page + 1) % 50 == 0:
                print(f"Extracted {i - start_page + 1}/{end_page - start_page} pages...")

    print(f"Saved to {output_path}")
    return str(output_path)


if __name__ == "__main__":
    args = [a for a in sys.argv if a != "--append"]
    pdf = args[1] if len(args) > 1 else r"d:\books\Robert_Erikson_fundamentals-of-power-electronics-3n_2020.pdf"
    start = int(args[2]) if len(args) > 2 else 0
    end = int(args[3]) if len(args) > 3 else None
    append = "--append" in sys.argv
    out = Path(__file__).parent.parent / "data" / "raw"
    out.mkdir(parents=True, exist_ok=True)
    extract_pdf(pdf, str(out), start, end, append)
