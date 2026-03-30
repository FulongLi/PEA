"""
Extract text from a power-electronics PDF (e.g. Erickson & Maksimović).

Writes ``erickson_extracted.txt`` under ``data/raw/`` when invoked as a script.
Requires: ``pip install pypdf``. Runtime RAG uses ``pea/knowledge/documents.py``,
not this file — use the extract for manual curation only.
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
    argv = [a for a in sys.argv[1:] if a != "--append"]
    append = "--append" in sys.argv
    if not argv:
        print(
            "Usage: python scripts/extract_pdf.py <pdf_path> [start_page] [end_page] [--append]\n"
            "  start_page / end_page: 0-based; end_page is exclusive (same as slice).\n"
            "  Output: data/raw/erickson_extracted.txt (created under repo root)."
        )
        sys.exit(1)
    pdf = argv[0]
    start = int(argv[1]) if len(argv) > 1 else 0
    end = int(argv[2]) if len(argv) > 2 else None
    out = Path(__file__).resolve().parent.parent / "data" / "raw"
    out.mkdir(parents=True, exist_ok=True)
    extract_pdf(pdf, str(out), start, end, append)
