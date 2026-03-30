"""
Native window for the static PEA UI (index.html) via pywebview.
No browser tab — double-click friendly when paired with a .bat or frozen .exe.

Install: pip install pywebview   或   pip install -e ".[desktop]"
Run:     python -m pea.desktop   或   pea-desktop（editable 安装后）

打包单文件 exe（需 pip install pyinstaller），在仓库根目录执行:
  pyinstaller --onefile --windowed --name PEA-Desktop ^
    --collect-all webview --add-data "index.html;." pea/desktop.py
生成 dist/PEA-Desktop.exe；首次运行需本机已装 Edge WebView2 运行时（Win10/11 通常已有）。
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
            "需要安装 pywebview：python -m pip install pywebview\n"
            "或：pip install -e \".[desktop]\""
        ) from e

    index = _root_dir() / "index.html"
    if not index.is_file():
        raise SystemExit(f"未找到 index.html：{index}")

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
