# Contributing to PEA

**Last updated:** 2026-03-31

Thank you for helping improve PEA (Power Electronics AI Agent). This document is for anyone who will maintain or extend the project.

## Project overview

PEA assists with power electronics design: topology recommendation, DC-DC parameter calculations, efficiency estimation, optional RAG over curated knowledge, and multi-turn chat via LangChain + OpenAI.

- **Core logic** lives in Python under `pea/`; the **single source of truth** for design equations is `pea/tools/calculator.py`.
- **`app.py`** is the Streamlit UI; it calls the same calculator tools as the CLI.
- **`index.html`** is a **standalone** UI (browser or **`pea/desktop.py`**). **User-visible copy is English.** The sidebar **pins** **Topology Advisor** (auto topology recommendation) and **Efficiency estimate** above the DC-DC / DC-AC / AC-DC / AC-AC tabs so they are always visible. Also: SPICE / components / magnetics and a **Cursor-style agent** (model picker, optional OpenAI in ⚙, rules fallback). It does **not** call Python for calculators. Some rows are browse-only stubs; **DAB** and others may exist only here until ported to `calculator.py`—keep both sides aligned when you extend features.

### Desktop app and static UI behavior

- **`pea/desktop.py`** + **`run_pea_desktop.bat`**: native **pywebview** window (`pip install -e ".[desktop]"` or the `.bat` auto-install).
- The desktop shell **does not** open `index.html` as `file://`. It starts a small **HTTP server on 127.0.0.1** (random port) rooted at the repo so the **SPICE** tab can `fetch()` under `data/spice_models_json/` (device index + per-part JSON).
- **LTspice (Windows)**: the SPICE tab can call **`pywebview.api.ltspice_launch`** to write a temp `.lib` + `PEA_sim.cir` and start **LTspice.exe**. Auto-detect may fail; set **`LTSPICE_EXE`** to the full path of `LTspice.exe` if needed.
- **Browser-only preview**: from the repo root, `python -m http.server <port>` then open `/index.html`—the SPICE library and catalog load, but **Open in LTspice** requires the desktop app.

### Vendor SPICE data (`data/spice_models_json/`)

- The repo stores vendor models as **JSON** (`raw_spice` / `raw_text`, parsed `.subckt` index, `.model` lines). The original vendor directory tree is **not** kept in git.
- **`ui_catalog.json`** powers the SPICE tab device picker; refresh it after bulk edits to JSON:

  ```bash
  python scripts/spice_to_json.py build-ui-catalog
  ```

- To **re-import** from a local vendor folder you have on disk:

  ```bash
  python scripts/spice_to_json.py export --source "path/to/vendor_libs" --out data/spice_models_json
  ```

  Optional: `--include-asy`, `--full-subckt-body` (see `scripts/spice_to_json.py --help`).

- To **emit** a single `.lib` from one JSON file:

  ```bash
  python scripts/spice_to_json.py write-spice path/to/file.lib.json --dest out.lib
  ```

- Details and licensing reminders: [`data/spice_models_json/README.md`](data/spice_models_json/README.md) and [`data/README.md`](data/README.md).

## Development setup

Requirements: **Python 3.9+** (3.11 or 3.12 recommended if you hit wheel issues on very new Python releases).

```bash
cd PEA
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -e ".[dev]"
```

For desktop / SPICE-LTspice work, also install the desktop extra:

```bash
pip install -e ".[desktop]"
```

Copy `.env.example` to `.env` and set `OPENAI_API_KEY` when working on the agent, Streamlit chat, or `scripts/agent_smoke_test.py`.

## Running tests

```bash
pytest tests/ -v
```

`tests/test_calculator.py` covers calculators and `execute_tool`. There are currently **no** automated tests for `PEAAgent`, RAG, or Streamlit; use `python scripts/agent_smoke_test.py "your prompt"` for manual agent checks (requires API key).

For broader manual checks, see `TESTING.md` and `README.md`.

## Optional linting

The `dev` extra includes Ruff:

```bash
ruff check .
ruff format .
```

## Where to change what

| Area | Primary files |
|------|----------------|
| Design equations & tool dispatch | `pea/tools/calculator.py` |
| LangChain tools exposed to the LLM | `pea/tools/langchain_tools.py` |
| Agent behavior, prompts, chat loop | `pea/agent/runner.py` |
| RAG documents | `pea/knowledge/documents.py` |
| Vector / keyword retrieval | `pea/knowledge/retriever.py` |
| CLI (`pea` command) | `pea/cli.py` |
| Streamlit UI | `app.py` |
| Static web UI (Design / SPICE / Components / …) | `index.html` (CSS/JS inline) |
| Desktop: HTTP server, LTspice bridge | `pea/desktop.py`, `run_pea_desktop.bat`; optional `[desktop]` → `pywebview` |
| Vendor SPICE → JSON, UI catalog | `scripts/spice_to_json.py`; data under `data/spice_models_json/` |
| PDF extraction (not in default deps) | `scripts/extract_pdf.py` — requires `pypdf`; outputs under `data/raw/` |
| Manual agent smoke test (OpenAI) | `scripts/agent_smoke_test.py` |
| Streamlit first-run / project defaults | `.streamlit/config.toml` (tracked; see `.gitignore` rules) |

## RAG and local data

- With ChromaDB + Sentence Transformers available, embeddings persist under the user profile (default `~/.pea/chroma_db`). First run may download models.
- If vector setup fails, the retriever falls back to simple keyword matching over `KNOWLEDGE_DOCUMENTS`.

## Documentation maintenance (README + CONTRIBUTING)

Whenever a change affects **how users install, run, or understand** the project, **update both** [`README.md`](README.md) and this file in the **same PR / commit** (or same release), for example:

- New scripts, entry points (`pea-desktop`), optional dependencies (`[desktop]`, `[dev]`), or run commands.
- New or renamed UI surfaces (`index.html`, Streamlit, desktop).
- Data layout (`data/spice_models_json/`, export scripts).
- Behavior that contradicts what the docs claim.

After you **materially edit** `CONTRIBUTING.md`, bump the **Last updated** date at the top. Keep `README.md` and `CONTRIBUTING.md` free of drift (one source of truth per topic; cross-link where useful).

## Guidelines for pull requests

- Keep changes **focused** on the issue or feature; avoid unrelated refactors.
- **Match existing style** in the files you touch (imports, naming, typing).
- Add or extend **pytest** coverage when you change `calculator.py` or `execute_tool` behavior.
- Follow **Documentation maintenance** above: sync **README.md** and **CONTRIBUTING.md** with user-facing changes.
- If you add or redistribute **vendor SPICE models**, respect the vendor’s license and keep disclaimers in `raw_spice`; prefer documenting re-import steps over committing huge proprietary drops unless the project explicitly allows it.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT). See `LICENSE`.
