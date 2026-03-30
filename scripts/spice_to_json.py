"""
Convert vendor SPICE text files to JSON under ``data/spice_models_json/``.

Each output file includes:
  - ``raw_spice`` (or ``raw_text`` for .asy): lossless round-trip source
  - ``parsed``: best-effort index of ``.subckt`` blocks and ``.model`` lines

Usage (from repo root):
  python scripts/spice_to_json.py export --source path/to/vendor_libs --out data/spice_models_json
  python scripts/spice_to_json.py build-ui-catalog [--root data/spice_models_json]
  python scripts/spice_to_json.py write-spice path/to/file.json [--dest out.lib]

``build-ui-catalog`` refreshes ``ui_catalog.json`` for the PEA UI (after JSON-only workflow).

No third-party dependencies (stdlib only).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


PEA_SPICE_JSON_VERSION = 1
SPICE_EXTENSIONS = {".lib", ".cir", ".mod", ".sp"}
ASY_EXTENSION = ".asy"


def _decode_bytes(raw: bytes) -> tuple[str, str]:
    """Return (text, encoding_used). Tries utf-8 then latin-1."""
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace"), "latin-1+replace"


def _read_text(path: Path) -> tuple[str, str, bytes]:
    """Return (text, encoding_used, raw_bytes)."""
    raw = path.read_bytes()
    text, enc = _decode_bytes(raw)
    return text, enc, raw


def parse_subcircuits(text: str) -> list[dict]:
    """Extract .subckt ... .ends blocks (line-preserving body, nested-safe)."""
    lines = text.splitlines()
    blocks: list[dict] = []
    i, n = 0, len(lines)
    subckt_re = re.compile(r"^\s*\.subckt\s+(\S+)(.*)$", re.I)
    ends_re = re.compile(r"^\s*\.ends\b", re.I)

    while i < n:
        m = subckt_re.match(lines[i])
        if m:
            name = m.group(1)
            rest = m.group(2).strip()
            if "*" in rest:
                rest = rest.split("*", 1)[0].strip()
            ports = rest.split() if rest else []
            body_lines = [lines[i]]
            depth = 1
            i += 1
            while i < n and depth > 0:
                body_lines.append(lines[i])
                if subckt_re.match(lines[i]):
                    depth += 1
                elif ends_re.match(lines[i]):
                    depth -= 1
                i += 1
            blocks.append(
                {
                    "name": name,
                    "ports": ports,
                    "line_count": len(body_lines),
                    "body": "\n".join(body_lines),
                }
            )
            continue
        i += 1
    return blocks


def parse_dot_models(text: str) -> list[str]:
    out: list[str] = []
    model_re = re.compile(r"^\s*\.model\s+", re.I)
    for line in text.splitlines():
        if model_re.match(line):
            out.append(line.rstrip())
    return out


def parse_asy_meta(text: str) -> dict:
    """LTspice symbol file: capture Value / Prefix and pin names."""
    meta: dict = {"symattr_value": None, "symattr_prefix": None, "pins": []}
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("SYMATTR Value "):
            meta["symattr_value"] = s[len("SYMATTR Value ") :].strip()
        elif s.startswith("SYMATTR Prefix "):
            meta["symattr_prefix"] = s[len("SYMATTR Prefix ") :].strip()
        elif s.startswith("PINATTR PinName "):
            meta["pins"].append(s[len("PINATTR PinName ") :].strip())
    return meta


def json_rel_path_for_source(rel: str) -> str:
    """Stable relative path for JSON mirror (always POSIX slashes)."""
    rel_posix = rel.replace("\\", "/")
    p = Path(rel_posix)
    return p.with_suffix(p.suffix + ".json").as_posix()


def export_one(
    source_root: Path,
    spice_path: Path,
    out_root: Path,
    *,
    full_subckt_body: bool,
) -> dict:
    rel = str(spice_path.relative_to(source_root)).replace("\\", "/")
    text, enc, raw_bytes = _read_text(spice_path)
    suffix = spice_path.suffix.lower()

    if suffix == ASY_EXTENSION:
        record = {
            "pea_spice_json_version": PEA_SPICE_JSON_VERSION,
            "source_relative": rel,
            "file_type": "ltspice_asy",
            "encoding_used": enc,
            "raw_text": text,
            "parsed": {"ltspice_symbol": parse_asy_meta(text)},
        }
    else:
        sub_raw = parse_subcircuits(text)
        sub_out: list[dict] = []
        for b in sub_raw:
            e: dict = {
                "name": b["name"],
                "ports": b["ports"],
                "line_count": b["line_count"],
            }
            if full_subckt_body:
                e["body"] = b["body"]
            sub_out.append(e)
        record = {
            "pea_spice_json_version": PEA_SPICE_JSON_VERSION,
            "source_relative": rel,
            "file_type": suffix.lstrip(".") or "spice",
            "encoding_used": enc,
            "raw_spice": text,
            "parsed": {
                "subcircuits": sub_out,
                "dot_models": parse_dot_models(text),
            },
        }

    json_rel = json_rel_path_for_source(rel)
    out_path = out_root / "files" / json_rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    sc = len(record.get("parsed", {}).get("subcircuits") or [])
    dm = len(record.get("parsed", {}).get("dot_models") or [])
    return {
        "relative": rel,
        "json_relative": json_rel,
        "sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "bytes": len(raw_bytes),
        "subckt_count": sc,
        "dot_model_count": dm,
    }


def cmd_export(args: argparse.Namespace) -> int:
    source = Path(args.source).resolve()
    out_root = Path(args.out).resolve()
    if not source.is_dir():
        print(f"Source not a directory: {source}", file=sys.stderr)
        print("Tip: vendor tree removed? Refresh UI index with:", file=sys.stderr)
        print("  python scripts/spice_to_json.py build-ui-catalog", file=sys.stderr)
        return 1

    out_root.mkdir(parents=True, exist_ok=True)

    exts = set(SPICE_EXTENSIONS)
    if args.include_asy:
        exts.add(ASY_EXTENSION)

    entries: list[dict] = []
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in exts:
            continue
        try:
            meta = export_one(
                source,
                path,
                out_root,
                full_subckt_body=args.full_subckt_body,
            )
            entries.append(meta)
        except OSError as e:
            print(f"Skip {path}: {e}", file=sys.stderr)

    try:
        src_display = str(source.relative_to(Path.cwd()))
    except ValueError:
        src_display = str(source)
    catalog = {
        "catalog_version": 1,
        "pea_spice_json_version": PEA_SPICE_JSON_VERSION,
        "source_root": src_display.replace("\\", "/"),
        "file_count": len(entries),
        "files": entries,
    }
    (out_root / "catalog.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    build_ui_catalog(out_root)
    print(f"Wrote {len(entries)} JSON files under {out_root / 'files'}")
    print(f"Catalog: {out_root / 'catalog.json'}")
    return 0


def build_ui_catalog(out_root: Path) -> int:
    """Build ``ui_catalog.json`` for the web UI (device picker)."""
    files_dir = out_root / "files"
    if not files_dir.is_dir():
        return 0
    items: list[dict] = []
    for p in sorted(files_dir.rglob("*.json")):
        rel = p.relative_to(out_root).as_posix()
        if rel == "catalog.json":
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        sr = data.get("source_relative", rel)
        subckts = [s["name"] for s in data.get("parsed", {}).get("subcircuits", [])]
        cat = sr.split("/")[0] if "/" in sr else "(root)"
        items.append(
            {
                "json_relative": rel,
                "source_relative": sr,
                "category": cat,
                "basename": Path(sr).name,
                "file_type": data.get("file_type", ""),
                "subckts": subckts,
                "subckt_count": len(subckts),
                "dot_model_count": len(data.get("parsed", {}).get("dot_models", [])),
            }
        )
    payload = {"version": 1, "count": len(items), "items": items}
    (out_root / "ui_catalog.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return len(items)


def cmd_build_ui_catalog(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    n = build_ui_catalog(root)
    print(f"Wrote {root / 'ui_catalog.json'} ({n} items)")
    return 0


def cmd_write_spice(args: argparse.Namespace) -> int:
    jp = Path(args.json_file).resolve()
    data = json.loads(jp.read_text(encoding="utf-8"))
    ver = data.get("pea_spice_json_version")
    if ver != PEA_SPICE_JSON_VERSION:
        print(f"Warning: json version {ver!r} != {PEA_SPICE_JSON_VERSION}", file=sys.stderr)

    if "raw_spice" in data:
        text = data["raw_spice"]
        default_suffix = "." + str(data.get("file_type", "lib"))
    elif "raw_text" in data:
        text = data["raw_text"]
        default_suffix = ".asy"
    else:
        print("JSON missing raw_spice / raw_text", file=sys.stderr)
        return 1

    if args.dest:
        dest = Path(args.dest)
    else:
        src_rel = data.get("source_relative", "out" + default_suffix)
        dest = jp.parent / Path(src_rel).name

    dest = dest.resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    enc = data.get("encoding_used", "utf-8")
    if enc.startswith("latin-1"):
        dest.write_bytes(text.encode("latin-1", errors="replace"))
    else:
        dest.write_text(text, encoding="utf-8", newline="\n")
    print(f"Wrote {dest}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="PEA: SPICE library files ↔ JSON")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_exp = sub.add_parser("export", help="Scan source tree and emit JSON + catalog.json")
    p_exp.add_argument(
        "--source",
        default="data/All SPICE Models",
        help="Vendor library root (.lib / .cir / …). If missing, use build-ui-catalog only.",
    )
    p_exp.add_argument(
        "--out",
        default="data/spice_models_json",
        help="Output directory for catalog.json and files/",
    )
    p_exp.add_argument(
        "--include-asy",
        action="store_true",
        help="Also convert LTspice .asy symbol files (raw_text + pin metadata)",
    )
    p_exp.add_argument(
        "--full-subckt-body",
        action="store_true",
        help="Store each .subckt body again under parsed (large); default is index only — use raw_spice to regenerate",
    )
    p_exp.set_defaults(func=cmd_export)

    p_wr = sub.add_parser("write-spice", help="Write raw_spice from a JSON file back to disk")
    p_wr.add_argument("json_file", help="Path to one exported .json")
    p_wr.add_argument(
        "--dest",
        default=None,
        help="Output path (default: basename of source_relative next to json)",
    )
    p_wr.set_defaults(func=cmd_write_spice)

    p_ui = sub.add_parser(
        "build-ui-catalog",
        help="Scan data/spice_models_json/files/*.json and write ui_catalog.json",
    )
    p_ui.add_argument(
        "--root",
        default="data/spice_models_json",
        help="Folder containing files/ and catalog.json",
    )
    p_ui.set_defaults(func=cmd_build_ui_catalog)

    args = ap.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
