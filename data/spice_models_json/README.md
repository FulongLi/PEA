# SPICE models as JSON

Canonical storage for vendor models. Original vendor folders are **not** kept in-repo; regenerate from a local vendor drop when needed.

## Regenerate from vendor files (optional)

If you have a vendor library tree on disk:

```bash
python scripts/spice_to_json.py export --source "path/to/vendor_libs" --out data/spice_models_json
python scripts/spice_to_json.py export --source "path/to/vendor_libs" --include-asy
python scripts/spice_to_json.py export --source "path/to/vendor_libs" --full-subckt-body   # large
```

## Refresh UI index only

After editing JSON files by hand:

```bash
python scripts/spice_to_json.py build-ui-catalog
```

## JSON shape (`pea_spice_json_version` = 1)

| Field | Meaning |
|--------|---------|
| `source_relative` | Path under `All SPICE Models` (POSIX `/`). |
| `raw_spice` / `raw_text` | **Canonical text** for round-trip; use this to regenerate the original file. |
| `parsed.subcircuits` | Each: `name`, `ports`, `line_count`; optional `body` if exported with `--full-subckt-body`. |
| `parsed.dot_models` | Full lines starting with `.model` (single-line only). |
| `parsed.ltspice_symbol` | For `.asy`: `symattr_value`, `symattr_prefix`, `pins`. |

`catalog.json` lists every file with `sha256` and counts for quick search.

## Restore a `.lib` from JSON

```bash
python scripts/spice_to_json.py write-spice path/to/file.lib.json --dest out.lib
```

## Note on licensing

Vendor models keep their original disclaimers inside `raw_spice`. Do not redistribute outside the terms printed in each file.
