"""
Native window for the static PEA UI (index.html) using pywebview.

- Serves the repo root over http://127.0.0.1:<port>/ so ``fetch()`` can load
  ``data/spice_models_json/*.json`` (file:// would block this in the WebView).
- Exposes a small JS API to launch LTspice with a netlist + vendor model text
  written to a temp folder.

Install: pip install pywebview  OR  pip install -e ".[desktop]"
Run:     python -m pea.desktop  OR  pea-desktop (after editable install)

Environment:
  LTSPICE_EXE — full path to LTspice.exe if auto-detect fails (Windows).

Single-file .exe (needs pip install pyinstaller), from repo root:
  pyinstaller --onefile --windowed --name PEA-Desktop ^
    --collect-all webview --add-data "index.html;." --add-data "data;data" pea/desktop.py
Output: dist/PEA-Desktop.exe. Requires Edge WebView2 runtime (usually on Win10/11).
"""

from __future__ import annotations

import os
import re
import socket
import subprocess
import sys
import tempfile
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def _root_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def _pick_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    _, port = s.getsockname()
    s.close()
    return port


def _start_http_server(root: Path) -> tuple[ThreadingHTTPServer, int]:
    last_err: OSError | None = None
    for _ in range(32):
        port = _pick_port()
        try:

            def handler(*args, **kwargs):
                return SimpleHTTPRequestHandler(*args, directory=str(root), **kwargs)

            httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
            break
        except OSError as e:
            last_err = e
            httpd = None
    else:
        raise RuntimeError(f"Could not bind HTTP server: {last_err}") from last_err

    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, port


def _find_ltspice_exe() -> Path | None:
    env = os.environ.get("LTSPICE_EXE", "").strip()
    if env:
        p = Path(env)
        if p.is_file():
            return p
    if sys.platform != "win32":
        return None
    pf = os.environ.get("ProgramFiles", r"C:\Program Files")
    pfx86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    local = os.environ.get("LOCALAPPDATA", "")
    candidates = [
        Path(pf) / "ADI" / "LTspice" / "LTspice.exe",
        Path(pfx86) / "LTspice" / "LTspice.exe",
        Path(local) / "Programs" / "ADI" / "LTspice" / "LTspice.exe",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def _safe_lib_basename(name: str) -> str:
    base = Path(name).name.strip() or "pea_model.lib"
    if not base.lower().endswith((".lib", ".cir", ".mod", ".sp")):
        base += ".lib"
    safe = re.sub(r"[^A-Za-z0-9._\-]+", "_", base)
    return safe[:120] if len(safe) > 120 else safe


class PeaDesktopApi:
    """Methods are exposed to JS as ``pywebview.api.<name>()``."""

    def __init__(self, ltspice: Path | None) -> None:
        self._ltspice = ltspice

    def ltspice_status(self) -> dict:
        return {
            "available": self._ltspice is not None,
            "path": str(self._ltspice) if self._ltspice else "",
        }

    def ltspice_launch(self, netlist_text: str, lib_basename: str, lib_text: str) -> dict:
        """Write ``lib_text`` and netlist (with .include) to a temp dir and open LTspice."""
        if not self._ltspice:
            return {
                "ok": False,
                "error": "LTspice not found. Install ADI LTspice or set LTSPICE_EXE.",
            }
        lib_name = _safe_lib_basename(lib_basename)
        text = (lib_text or "").replace("\r\n", "\n")
        nl = (netlist_text or "").replace("\r\n", "\n")
        d = Path(tempfile.mkdtemp(prefix="pea_ltspice_"))
        lib_path = d / lib_name
        try:
            lib_path.write_text(text, encoding="utf-8", newline="\n")
        except OSError as e:
            return {"ok": False, "error": f"Could not write model file: {e}"}
        cir = d / "PEA_sim.cir"
        header = (
            f"* PEA — auto wrapper (temp dir)\n"
            f'.include "{lib_name}"\n\n'
        )
        try:
            cir.write_text(header + nl, encoding="utf-8", newline="\n")
        except OSError as e:
            return {"ok": False, "error": f"Could not write netlist: {e}"}
        try:
            subprocess.Popen(
                [str(self._ltspice), str(cir)],
                cwd=str(d),
                shell=False,
            )
        except OSError as e:
            return {"ok": False, "error": str(e)}
        return {"ok": True, "workdir": str(d), "cir": str(cir), "lib": str(lib_path)}


def main() -> None:
    try:
        import webview
    except ImportError as e:
        raise SystemExit(
            "Install pywebview: python -m pip install pywebview\n"
            'Or: pip install -e ".[desktop]"'
        ) from e

    root = _root_dir()
    index = root / "index.html"
    if not index.is_file():
        raise SystemExit(f"index.html not found: {index}")

    httpd, port = _start_http_server(root)
    url = f"http://127.0.0.1:{port}/index.html"
    lt = _find_ltspice_exe()
    api = PeaDesktopApi(lt)

    webview.create_window(
        "PEA — Power Electronics Agent",
        url,
        width=1400,
        height=900,
        min_size=(900, 600),
        js_api=api,
    )
    try:
        webview.start(debug=False)
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    main()
