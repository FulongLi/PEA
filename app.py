"""
Streamlit web interface for PEA (Power Electronics AI Agent).
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

# Sidebar: Quick tools (no API key)
with st.sidebar:
    st.header("Quick Tools")
    st.caption("Direct calculations (no API key needed)")

    tool_choice = st.selectbox(
        "Select tool",
        ["Topology Recommendation", "Buck", "Boost", "Buck-Boost", "Flyback"],
    )

    col1, col2 = st.columns(2)
    with col1:
        v_in = st.number_input("V_in (V)", min_value=0.1, value=12.0, step=0.1)
        v_out = st.number_input("V_out (V)", min_value=0.1, value=5.0, step=0.1)
    with col2:
        i_out = st.number_input("I_out (A)", min_value=0.01, value=2.0, step=0.1)
        f_sw = st.number_input("f_sw (kHz)", min_value=10, value=100, step=10)

    if "Flyback" in tool_choice:
        v_in_min = st.number_input("V_in_min (V)", min_value=0.1, value=9.0, step=0.1)
        v_in_max = st.number_input("V_in_max (V)", min_value=0.1, value=18.0, step=0.1)
    else:
        v_in_min, v_in_max = 9.0, 18.0

    isolated = st.checkbox("Require isolation", value=False) if "Recommendation" in tool_choice else False

    if st.button("Calculate"):
        if "Recommendation" in tool_choice:
            result = execute_tool("topology_recommendation", v_in=v_in, v_out=v_out, i_out=i_out, isolated=isolated)
        elif "Buck" == tool_choice:
            result = execute_tool("buck_converter_design", v_in=v_in, v_out=v_out, i_out=i_out, f_sw_khz=f_sw)
        elif "Boost" == tool_choice:
            result = execute_tool("boost_converter_design", v_in=v_in, v_out=v_out, i_out=i_out, f_sw_khz=f_sw)
        elif "Buck-Boost" in tool_choice:
            result = execute_tool("buck_boost_design", v_in=v_in, v_out=-v_out, i_out=i_out, f_sw_khz=f_sw)
        elif "Flyback" in tool_choice:
            result = execute_tool("flyback_design", v_in_min=v_in_min, v_in_max=v_in_max,
                                 v_out=v_out, i_out=i_out, f_sw_khz=f_sw)
        else:
            result = "{}"

        try:
            st.json(json.loads(result))
        except json.JSONDecodeError:
            st.code(result)

# Main area: AI Chat
st.header("AI Chat")
st.caption("Ask design questions or provide specs for full AI-assisted design (requires OpenAI API key)")

api_key = os.getenv("OPENAI_API_KEY") or st.text_input("OpenAI API Key", type="password", placeholder="sk-...")

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("e.g., Design a 12V to 5V 2A Buck converter"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                agent = PEAAgent(api_key=api_key)
                response = agent.chat(prompt)
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.info("Enter your OpenAI API key above to use the AI chat. Use the sidebar for direct calculations.")
