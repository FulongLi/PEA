# PEA Agent 测试步骤

## 环境要求

- Python 3.9+
- 已安装项目依赖：`pip install -r requirements.txt`
- AI 聊天需 OpenAI API Key

---

## 步骤 1：测试直接计算工具（无需 API Key）

这些命令不调用 LLM，仅使用本地计算公式。

### 1.1 列出可用工具

```powershell
cd C:\Users\User\Documents\GitHub\PEA
python -m pea.cli tools
```

**预期输出**：列出 5 个设计工具及参数说明。

### 1.2 拓扑推荐

```powershell
python -m pea.cli tool recommend --v-in 12 --v-out 5 --i-out 2
```

**预期输出**：
```json
{
  "recommended": "Buck",
  "alternatives": ["Buck-Boost"],
  "rationale": "Buck is optimal for step-down (V_out < V_in). Highest efficiency."
}
```

### 1.3 Buck 设计计算

```powershell
python -m pea.cli tool buck --v-in 12 --v-out 5 --i-out 2
```

**预期输出**：
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

### 1.4 其他工具示例

```powershell
# Boost
python -m pea.cli tool boost --v-in 5 --v-out 12 --i-out 1

# Flyback (需输入电压范围)
python -m pea.cli tool flyback --v-in-min 9 --v-in-max 18 --v-out 24 --i-out 0.5
```

---

## 步骤 2：测试 AI Agent（需 API Key）

### 2.1 设置 API Key

**PowerShell：**
```powershell
$env:OPENAI_API_KEY = "sk-your-actual-openai-api-key"
```

**或创建 `.env` 文件：**
```
OPENAI_API_KEY=sk-your-actual-openai-api-key
```

### 2.2 运行测试脚本

```powershell
cd C:\Users\User\Documents\GitHub\PEA
python test_agent.py "Design a 12V to 5V 2A Buck converter"
```

**预期行为**：Agent 调用 `recommend_topology` 和 `design_buck`，返回完整设计说明。

### 2.3 使用默认提示词

```powershell
python test_agent.py
```

默认提示词：`Design a 12V to 5V 2A Buck converter`

### 2.4 使用 CLI 聊天

```powershell
pea chat "Design a 12V to 5V 2A Buck converter"
```

### 2.5 使用 Streamlit 网页

```powershell
streamlit run app.py
```

浏览器打开 http://localhost:8501，输入 API Key 后即可对话。

---

## 步骤 3：常见问题排查

### 问题 A：`ModuleNotFoundError: langchain_core`

**解决**：
```powershell
pip install langchain-core langchain-openai
```

### 问题 B：`Error: Set OPENAI_API_KEY environment variable`

**解决**：按步骤 2.1 设置 API Key。

### 问题 C：`ImportError: DLL load failed while importing _uuid_utils`

**原因**：`uuid-utils`（langchain-core 依赖）在部分 Windows/Python 环境下存在兼容性问题。

**尝试方案**：

1. **安装 Visual C++ Redistributable**
   - 下载：https://aka.ms/vs/17/release/vc_redist.x64.exe
   - 安装后重启终端再试

2. **升级 Python 到 3.10+**
   ```powershell
   # 使用 pyenv 或从 python.org 安装 3.10+
   ```

3. **使用虚拟环境**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python test_agent.py
   ```

### 问题 D：`pea` 命令找不到

**解决**：确保已安装项目：
```powershell
pip install -e .
```

或使用模块方式运行：
```powershell
python -m pea.cli chat "Design a 12V to 5V 2A Buck converter"
```

---

## 测试结果记录（复现用）

| 步骤 | 命令 | 结果 |
|------|------|------|
| 1.1 | `python -m pea.cli tools` | ✅ 通过 |
| 1.2 | `python -m pea.cli tool recommend --v-in 12 --v-out 5 --i-out 2` | ✅ 通过 |
| 1.3 | `python -m pea.cli tool buck --v-in 12 --v-out 5 --i-out 2` | ✅ 通过 |
| 2.2 | `python test_agent.py "Design a 12V to 5V 2A Buck converter"` | 需有效 API Key；若遇 uuid_utils 错误见问题 C |
