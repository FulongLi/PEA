"""
Streamlit web interface for PEA (Power Electronics AI Agent).

Uses the same stack as ``pea chat`` and ``pea tool``: ``execute_tool`` from
``pea.tools.calculator`` for sidebar calculators, and ``PEAAgent`` for the
main chat when ``OPENAI_API_KEY`` is set.

Contrast: ``index.html`` + ``pea.desktop`` is a separate static UI; keep
user-facing behavior in sync when you change calculators or taxonomy.
"""

import json
import os
import streamlit as st

from pea.agent.runner import PEAAgent
from pea.tools.calculator import execute_tool


st.set_page_config(
    page_title="PEA - Power Electronics AI",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ PEA - Power Electronics AI Agent")
st.caption("Design assistant for DC-DC converters: topology selection, parameter calculation, component guidance")

# ── Sidebar: Quick tools (no API key) ────────────────────────────────────
with st.sidebar:
    st.header("Quick Tools")
    st.caption("Direct calculations (no API key needed)")

    tool_choice = st.selectbox(
        "Select tool",
        [
            "Topology Recommendation",
            "Buck",
            "Boost",
            "Buck-Boost",
            "SEPIC",
            "Cuk",
            "Forward",
            "Flyback",
            "LLC Resonant",
            "Efficiency Estimate",
        ],
    )

    col1, col2 = st.columns(2)
    with col1:
        v_in = st.number_input("V_in (V)", min_value=0.1, value=12.0, step=0.1)
        v_out = st.number_input("V_out (V)", min_value=0.1, value=5.0, step=0.1)
    with col2:
        i_out = st.number_input("I_out (A)", min_value=0.01, value=2.0, step=0.1)
        f_sw = st.number_input("f_sw (kHz)", min_value=10, value=100, step=10)

    if tool_choice in ("Flyback", "Forward"):
        v_in_min = st.number_input("V_in_min (V)", min_value=0.1, value=9.0, step=0.1)
        v_in_max = st.number_input("V_in_max (V)", min_value=0.1, value=18.0, step=0.1)
    else:
        v_in_min, v_in_max = 9.0, 18.0

    if tool_choice == "LLC Resonant":
        q_factor = st.number_input("Q factor", min_value=0.1, value=0.5, step=0.1)
    else:
        q_factor = 0.5

    if tool_choice == "Efficiency Estimate":
        st.markdown("**Component parameters**")
        rds_on = st.number_input("MOSFET Rds(on) (mΩ)", min_value=1.0, value=50.0, step=5.0)
        dcr = st.number_input("Inductor DCR (mΩ)", min_value=1.0, value=30.0, step=5.0)
        vf_diode = st.number_input("Diode Vf (V)", min_value=0.0, value=0.5, step=0.1)
        t_rise_ns = st.number_input("Rise time (ns)", min_value=1.0, value=20.0, step=5.0)
        t_fall_ns = st.number_input("Fall time (ns)", min_value=1.0, value=20.0, step=5.0)
    else:
        rds_on = 50.0
        dcr = 30.0
        vf_diode = 0.5
        t_rise_ns = 20.0
        t_fall_ns = 20.0

    isolated = st.checkbox("Require isolation", value=False) if tool_choice == "Topology Recommendation" else False

    if st.button("Calculate", use_container_width=True):
        tool_map = {
            "Topology Recommendation": lambda: execute_tool(
                "topology_recommendation", v_in=v_in, v_out=v_out, i_out=i_out, isolated=isolated,
            ),
            "Buck": lambda: execute_tool(
                "buck_converter_design", v_in=v_in, v_out=v_out, i_out=i_out, f_sw_khz=f_sw,
            ),
            "Boost": lambda: execute_tool(
                "boost_converter_design", v_in=v_in, v_out=v_out, i_out=i_out, f_sw_khz=f_sw,
            ),
            "Buck-Boost": lambda: execute_tool(
                "buck_boost_design", v_in=v_in, v_out=-v_out, i_out=i_out, f_sw_khz=f_sw,
            ),
            "SEPIC": lambda: execute_tool(
                "sepic_design", v_in=v_in, v_out=v_out, i_out=i_out, f_sw_khz=f_sw,
            ),
            "Cuk": lambda: execute_tool(
                "cuk_design", v_in=v_in, v_out=v_out, i_out=i_out, f_sw_khz=f_sw,
            ),
            "Forward": lambda: execute_tool(
                "forward_design", v_in_min=v_in_min, v_in_max=v_in_max,
                v_out=v_out, i_out=i_out, f_sw_khz=f_sw,
            ),
            "Flyback": lambda: execute_tool(
                "flyback_design", v_in_min=v_in_min, v_in_max=v_in_max,
                v_out=v_out, i_out=i_out, f_sw_khz=f_sw,
            ),
            "LLC Resonant": lambda: execute_tool(
                "llc_design", v_in=v_in, v_out=v_out, i_out=i_out,
                f_sw_khz=f_sw, q_factor=q_factor,
            ),
            "Efficiency Estimate": lambda: execute_tool(
                "efficiency_estimate",
                v_in=v_in, v_out=v_out, i_out=i_out, f_sw_khz=f_sw,
                rds_on_mohm=rds_on, dcr_mohm=dcr, vf_diode=vf_diode,
                t_rise_ns=t_rise_ns, t_fall_ns=t_fall_ns,
            ),
        }
        result = tool_map.get(tool_choice, lambda: "{}")()

        try:
            st.json(json.loads(result))
        except json.JSONDecodeError:
            st.code(result)

# ── Main area: AI Chat ───────────────────────────────────────────────────
st.header("AI Chat")
st.caption("Ask design questions or provide specs for full AI-assisted design (requires OpenAI API key)")

api_key = os.getenv("OPENAI_API_KEY") or st.text_input(
    "OpenAI API Key", type="password", placeholder="sk-..."
)

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

    if "agent" not in st.session_state:
        st.session_state.agent = PEAAgent(api_key=api_key)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    agent: PEAAgent = st.session_state.agent

    col_header, col_btn = st.columns([6, 1])
    with col_btn:
        if st.button("Clear chat"):
            agent.clear_history()
            st.session_state.messages = []
            st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("e.g., Design a 12V to 5V 2A Buck converter"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = agent.chat(prompt)
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.info("Enter your OpenAI API key above to use the AI chat. Use the sidebar for direct calculations.")
