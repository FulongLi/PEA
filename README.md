# PEA - Power Electronics AI Agent

An AI assistant for power electronics design: topology selection, parameter calculation, and component guidance.

## Features

- **Topology recommendation**: Suggests Buck, Boost, Buck-Boost, Flyback, or LLC based on your specs
- **Design calculations**: Computes inductance, capacitance, duty cycle for common converters
- **RAG knowledge base**: Answers questions using curated power electronics knowledge
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

## Project Structure

```
PEA/
├── pea/
│   ├── agent/          # AI agent with tool calling
│   ├── knowledge/      # RAG documents and retriever
│   ├── tools/          # Design calculators (Buck, Boost, etc.)
│   └── cli.py          # Command-line interface
├── app.py              # Streamlit web app
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Supported Topologies

| Topology | Use when |
|----------|----------|
| Buck | V_out < V_in (step-down) |
| Boost | V_out > V_in (step-up) |
| Buck-Boost | Inverting or wide input range |
| Flyback | Galvanic isolation required |

## Environment Variables

- `OPENAI_API_KEY`: Required for AI chat (get from [OpenAI](https://platform.openai.com))

## License

MIT
