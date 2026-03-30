# PEA — manual test checklist

## Requirements

- Python 3.9+
- Dependencies: `pip install -r requirements.txt` (or `pip install -e .`)
- OpenAI API key for AI chat tests

---

## Step 1 — Calculator tools (no API key)

These use local math only (no LLM).

### 1.1 List tools

```powershell
cd E:\path\to\PEA
python -m pea.cli tools
```

**Expected:** List of design tools and parameter hints.

### 1.2 Topology recommendation

```powershell
python -m pea.cli tool recommend --v-in 12 --v-out 5 --i-out 2
```

**Expected (example):**
```json
{
  "recommended": "Buck",
  "alternatives": ["Buck-Boost"],
  "rationale": "Buck is optimal for step-down (V_out < V_in). Highest efficiency."
}
```

### 1.3 Buck design

```powershell
python -m pea.cli tool buck --v-in 12 --v-out 5 --i-out 2
```

**Expected (example):**
```json
{
  "topology": "Buck",
  "duty_cycle": 0.417,
  "inductance_uH": 48.61,
  "capacitance_uF": 15.0,
  "switching_frequency_kHz": 100,
  "ripple_current_A": 0.6,
  "ripple_voltage_V": 0.05,
  "notes": "Step-down converter. Use synchronous rectification for high efficiency."
}
```

### 1.4 Other tools (examples)

```powershell
python -m pea.cli tool boost --v-in 5 --v-out 12 --i-out 1
python -m pea.cli tool flyback --v-in-min 9 --v-in-max 18 --v-out 24 --i-out 0.5
```

---

## Step 2 — AI agent (API key required)

### 2.1 Set API key

**PowerShell:**
```powershell
$env:OPENAI_API_KEY = "sk-your-key"
```

**Or** copy `.env.example` to `.env` and set `OPENAI_API_KEY`.

### 2.2 Test script

```powershell
python scripts/agent_smoke_test.py "Design a 12V to 5V 2A Buck converter"
```

**Expected:** Agent uses tools and returns a design narrative.

### 2.3 Default prompt

```powershell
python scripts/agent_smoke_test.py
```

Default: `Design a 12V to 5V 2A Buck converter`

### 2.4 CLI chat

```powershell
pea chat "Design a 12V to 5V 2A Buck converter"
```

### 2.5 Streamlit

```powershell
streamlit run app.py
```

Open http://localhost:8501 and enter the API key in the UI if needed.

### 2.6 Static / desktop UI

- Open `index.html` in a browser, or run `python -m pea.desktop` / `run_pea_desktop.bat`.
- **Topology Advisor** and **Efficiency estimate** are pinned at the top of the sidebar (always visible). Tabs below list DC-DC / DC-AC / AC-DC / AC-AC.

---

## Step 3 — Troubleshooting

### A: `ModuleNotFoundError: langchain_core`

```powershell
pip install langchain-core langchain-openai
```

### B: `Error: Set OPENAI_API_KEY...`

Set the key as in §2.1.

### C: `ImportError: DLL load failed` (uuid / Windows)

Try: install [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe), use Python 3.10+, or a clean venv with `pip install -r requirements.txt`.

### D: `pea` command not found

```powershell
pip install -e .
```

Or: `python -m pea.cli chat "..."`

---

## Result log (optional)

| Step | Command | Notes |
|------|---------|--------|
| 1.1 | `python -m pea.cli tools` | |
| 1.2 | `python -m pea.cli tool recommend ...` | |
| 1.3 | `python -m pea.cli tool buck ...` | |
| 2.2 | `python scripts/agent_smoke_test.py "..."` | Needs valid key |
