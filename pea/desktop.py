"""
Native window for the static PEA UI (index.html) using pywebview.

Install: pip install pywebview  OR  pip install -e ".[desktop]"
Run:     python -m pea.desktop  OR  pea-desktop (after editable install)

Single-file .exe (needs pip install pyinstaller), from repo root:
  pyinstaller --onefile --windowed --name PEA-Desktop ^
    --collect-all webview --add-data "index.html;." pea/desktop.py
Output: dist/PEA-Desktop.exe. Requires Edge WebView2 runtime (usually on Win10/11).
"""

from __future__ import annotations

import sys
from pathlib import Path


def _root_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def main() -> None:
    try:
        import webview
    except ImportError as e:
        raise SystemExit(
            "Install pywebview: python -m pip install pywebview\n"
            "Or: pip install -e \".[desktop]\""
        ) from e

    index = _root_dir() / "index.html"
    if not index.is_file():
        raise SystemExit(f"index.html not found: {index}")

    url = index.as_uri()
    webview.create_window(
        "PEA — Power Electronics Agent",
        url,
        width=1400,
        height=900,
        min_size=(900, 600),
    )
    webview.start(debug=False)


if __name__ == "__main__":
    main()
