# PEA - Power Electronics AI Agent

An AI assistant for power electronics design: topology selection, parameter calculation, efficiency estimation, and component guidance.

## Features

- **Topology recommendation**: Suggests the best converter topology based on your specs
- **8 converter calculators**: Buck, Boost, Buck-Boost, SEPIC, Cuk, Forward, Flyback, LLC Resonant
- **Efficiency estimation**: First-order loss breakdown (conduction + switching) with component parameters
- **RAG knowledge base**: Answers questions using curated power electronics knowledge (Erickson & Maksimovic)
- **Multi-turn AI chat**: Conversational agent that remembers context across messages
- **CLI & Web UI**: Use from terminal or Streamlit web interface

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

### 4. Web interface

```bash
streamlit run app.py
```

Open http://localhost:8501. Use the sidebar for direct calculations, or enter your API key for AI chat.

### 5. Run tests

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
│   └── cli.py            # Command-line interface
├── tests/                # Pytest test suite
├── data/                 # Extracted textbook data for knowledge base
├── scripts/              # Utility scripts (PDF extraction)
├── app.py                # Streamlit web app
├── requirements.txt
├── pyproject.toml
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

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, tests, code layout, and PR expectations.

## License

MIT
