# PEA Knowledge Base Data

**Runtime:** The app loads RAG text from `pea/knowledge/documents.py` only. Nothing in this folder is imported automatically.

## SPICE model libraries

- **`spice_models_json/`** — vendor models as JSON (`raw_spice` / `raw_text`, parsed `.subckt` / `.model` index, `ui_catalog.json` for the PEA UI). The original vendor tree is not stored in git; re-import with `python scripts/spice_to_json.py export --source <folder>` when you have files locally (see `spice_models_json/README.md`).

## Erickson Textbook Extraction

The knowledge base includes content from:
**Fundamentals of Power Electronics**, 3rd Edition (2020)  
Robert W. Erickson, Dragan Maksimović

### Extraction Script

```bash
# Extract page range (0-indexed)
python scripts/extract_pdf.py "path/to/erickson.pdf" [start_page] [end_page]

# Append to existing file
python scripts/extract_pdf.py "path/to/erickson.pdf" 500 900 --append

# Examples
python scripts/extract_pdf.py "path/to/erickson.pdf" 0 500      # pages 1-500
python scripts/extract_pdf.py "path/to/erickson.pdf" 500 900 --append
python scripts/extract_pdf.py "path/to/erickson.pdf" 900 1081 --append
```

- Output: `data/raw/erickson_extracted.txt`
- Full book: 1081 pages

### Knowledge Base Update

After adding new content to `pea/knowledge/documents.py`, rebuild the vector index:

1. Delete the ChromaDB cache: `rm -rf ~/.pea/chroma_db` (or `%USERPROFILE%\.pea\chroma_db` on Windows)
2. Restart the PEA agent – it will re-index on first use

### Current Coverage

- **Ch 1–2**: Introduction, volt-second balance, small-ripple, Buck/Boost analysis
- **Ch 3**: DC transformer model, efficiency
- **Ch 4**: Switch applications, quadrants
- **Ch 5**: DCM
- **Ch 6**: Isolated topologies
- **Ch 7–9**: AC modeling, RHP zero, compensator design
- **Ch 10–12**: Magnetics, inductor design, transformer design
- **Ch 13–14**: Feedback theorem, averaged switch modeling
- **Ch 17**: Input filter design
- **Ch 18–19**: Current-programmed control, digital control
- **Ch 20–21**: Power factor, PFC rectifiers
- **Ch 22–23**: Resonant converters, soft switching
