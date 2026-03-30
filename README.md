# PEA - Power Electronics AI Agent

An AI assistant for power electronics design: topology selection, parameter calculation, efficiency estimation, and component guidance.

## Features

- **Topology recommendation**: Suggests the best converter topology based on your specs
- **8 converter calculators**: Buck, Boost, Buck-Boost, SEPIC, Cuk, Forward, Flyback, LLC Resonant
- **Efficiency estimation**: First-order loss breakdown (conduction + switching) with component parameters
- **RAG knowledge base**: Answers questions using curated power electronics knowledge (Erickson & Maksimovic)
- **Multi-turn AI chat**: Conversational agent that remembers context across messages
- **CLI & Web UI**: Terminal (`pea`) or Streamlit (`app.py`)
- **Static UI (`index.html`)**: Full layout in the browser—converter taxonomy (**DC-DC / DC-AC / AC-DC / AC-AC**), design calculators where implemented, SPICE/components/magnetics panels, and a **Cursor-style PEA Agent** panel (model picker, optional OpenAI API in ⚙; rule-based fallback without key). Some entries are browse-only until calculators exist in Python.
- **Desktop app**: Native window (no separate browser tab) via **pywebview**—double-click `run_pea_desktop.bat` (Windows) or run `python -m pea.desktop` / `pea-desktop` after `pip install -e ".[desktop]"`.

## Quick Start

### 1. Install

```bash
cd PEA
pip install -e .
```

Or install dependencies only:

```bash
pip install -r requirements.txt
```

### 2. Run design tools (no API key)

```bash
# List available tools
pea tools

# Topology recommendation
pea tool recommend --v-in 12 --v-out 5 --i-out 2

# Buck converter design
pea tool buck --v-in 12 --v-out 5 --i-out 2 --f-sw 100

# Boost converter design
pea tool boost --v-in 5 --v-out 12 --i-out 1

# SEPIC converter design
pea tool sepic --v-in 12 --v-out 5 --i-out 2

# LLC resonant converter
pea tool llc --v-in 400 --v-out 12 --i-out 20

# Efficiency estimate
pea tool efficiency --v-in 12 --v-out 5 --i-out 2 --rds-on 50 --dcr 30
```

### 3. AI chat (requires OpenAI API key)

```bash
# Set your API key
export OPENAI_API_KEY=sk-your-key-here

# Chat with PEA
pea chat "Design a 12V to 5V 2A Buck converter"
```

### 4. Web interface (Streamlit — full Python stack)

```bash
streamlit run app.py
```

Open http://localhost:8501. Use the sidebar for direct calculations, or enter your API key for AI chat.

### 5. Static page or desktop window (`index.html`)

Open `index.html` in a browser, or run the desktop shell (loads the same UI):

```bash
# Optional: install webview extra
pip install -e ".[desktop]"

# From repo root
python -m pea.desktop
# or, after editable install:
pea-desktop
```

**Windows:** double-click `run_pea_desktop.bat` (installs `pywebview` if missing, sets `PYTHONPATH` to the repo root).

Requires **Edge WebView2** on Windows (usually preinstalled). To build a single-file `.exe`, see the PyInstaller notes in `pea/desktop.py`.

### 6. Run tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Project Structure

```
PEA/
├── pea/
│   ├── agent/            # AI agent with LangChain tool calling + conversation memory
│   ├── knowledge/        # RAG documents and ChromaDB retriever
│   ├── tools/
│   │   ├── calculator.py       # Core design equations (8 topologies + efficiency)
│   │   └── langchain_tools.py  # @tool wrappers for LLM function calling
│   ├── cli.py            # Command-line interface
│   └── desktop.py        # Native window for index.html (pywebview)
├── tests/                # Pytest test suite
├── data/                 # Extracted textbook data for knowledge base
├── scripts/              # Utility scripts (PDF extraction)
├── app.py                # Streamlit web app
├── index.html            # Standalone static UI + taxonomy + agent panel
├── run_pea_desktop.bat   # Windows launcher for desktop UI
├── requirements.txt
├── pyproject.toml
├── CONTRIBUTING.md
└── README.md
```

## Supported Topologies

| Topology | Type | Use when |
|----------|------|----------|
| Buck | Non-isolated | V_out < V_in (step-down) |
| Boost | Non-isolated | V_out > V_in (step-up) |
| Buck-Boost | Non-isolated | Inverting or wide input range |
| SEPIC | Non-isolated | Non-inverting buck-boost, common ground |
| Cuk | Non-isolated | Inverting, continuous input & output current |
| Forward | Isolated | 50-300 W, single-ended |
| Flyback | Isolated | Low-medium power, galvanic isolation |
| LLC Resonant | Isolated | High efficiency, >200 W, ZVS operation |

## Environment Variables

- `OPENAI_API_KEY`: Required for AI chat (get from [OpenAI](https://platform.openai.com))

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, tests, code layout, PR expectations, and **keeping README + CONTRIBUTING updated** when user-facing behavior changes.

## License

MIT
