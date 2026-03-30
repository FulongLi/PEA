# Contributing to PEA

**Last updated:** 2026-03-30

Thank you for helping improve PEA (Power Electronics AI Agent). This document is for anyone who will maintain or extend the project.

## Project overview

PEA assists with power electronics design: topology recommendation, DC-DC parameter calculations, efficiency estimation, optional RAG over curated knowledge, and multi-turn chat via LangChain + OpenAI.

- **Core logic** lives in Python under `pea/`; the **single source of truth** for design equations is `pea/tools/calculator.py`.
- **`app.py`** is the Streamlit UI; it calls the same calculator tools as the CLI.
- **`index.html`** is a **standalone** in-browser demo (calculators, SPICE snippets, components, magnetics, rule-based chat). It does **not** call the Python backend. Some features there (e.g. DAB) may not exist in the Python package yet—keep implementations aligned deliberately if you add features on both sides.

## Development setup

Requirements: **Python 3.9+** (3.11 or 3.12 recommended if you hit wheel issues on very new Python releases).

```bash
cd PEA
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -e ".[dev]"
```

Copy `.env.example` to `.env` and set `OPENAI_API_KEY` when working on the agent, Streamlit chat, or `test_agent.py`.

## Running tests

```bash
pytest tests/ -v
```

`tests/test_calculator.py` covers calculators and `execute_tool`. There are currently **no** automated tests for `PEAAgent`, RAG, or Streamlit; use `python test_agent.py "your prompt"` for manual agent checks (requires API key).

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
| Static web UI | `index.html` (CSS/JS inline) |
| PDF extraction (not in default deps) | `scripts/extract_pdf.py` — requires `pypdf` |

## RAG and local data

- With ChromaDB + Sentence Transformers available, embeddings persist under the user profile (default `~/.pea/chroma_db`). First run may download models.
- If vector setup fails, the retriever falls back to simple keyword matching over `KNOWLEDGE_DOCUMENTS`.

## Guidelines for pull requests

- Keep changes **focused** on the issue or feature; avoid unrelated refactors.
- **Match existing style** in the files you touch (imports, naming, typing).
- Add or extend **pytest** coverage when you change `calculator.py` or `execute_tool` behavior.
- If you change user-visible behavior, update `README.md` when appropriate.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT). See `LICENSE`.
