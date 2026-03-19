"""
Power Electronics AI Agent - main agent logic with tool calling and RAG.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from pea.knowledge.retriever import KnowledgeRetriever
from pea.tools.calculator import (
    buck_boost_design,
    buck_converter_design,
    boost_converter_design,
    flyback_design,
    topology_recommendation,
)


# Tool registry for the agent (import from tools for consistency)
from pea.tools.calculator import execute_tool


class PEAAgent:
    """
    Power Electronics AI Agent.

    Combines LLM with RAG (knowledge retrieval) and design calculation tools.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        use_rag: bool = True,
        use_vector_store: bool = True,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.use_rag = use_rag
        self.retriever = KnowledgeRetriever(use_vector_store=use_vector_store) if use_rag else None
        self._llm = None

    def _get_llm(self):
        """Lazy load LLM to avoid import errors when API key is missing."""
        if self._llm is not None:
            return self._llm

        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key."
            )

        from langchain_openai import ChatOpenAI

        self._llm = ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            temperature=0.2,
        )
        return self._llm

    def _build_system_prompt(self, context: str | None) -> str:
        """Build system prompt with RAG context and tool descriptions."""
        base = """You are PEA (Power Electronics AI), an expert assistant for power electronics design.

Your capabilities:
1. Recommend converter topologies (Buck, Boost, Buck-Boost, Flyback, etc.) based on specs
2. Calculate design parameters (inductance, capacitance, duty cycle) using built-in tools
3. Answer questions about power electronics theory and design best practices

When the user provides specifications (V_in, V_out, I_out, etc.):
- First use topology_recommendation to suggest a suitable topology
- Then use the appropriate design tool (buck_converter_design, boost_converter_design, etc.) to calculate parameters
- Present results clearly with units and brief design notes

Available tools (call with exact parameter names):
- topology_recommendation(v_in, v_out, i_out, isolated=False): Recommend topology
- buck_converter_design(v_in, v_out, i_out, f_sw_khz=100, ripple_current_pct=0.3, ripple_voltage_pct=0.01)
- boost_converter_design(v_in, v_out, i_out, f_sw_khz=100, ripple_current_pct=0.3, ripple_voltage_pct=0.01)
- buck_boost_design(v_in, v_out, i_out, f_sw_khz=100, ripple_current_pct=0.3, ripple_voltage_pct=0.01)
- flyback_design(v_in_min, v_in_max, v_out, i_out, f_sw_khz=100, n_ratio=None)

To call a tool, respond with a JSON block on its own line:
```json
{"tool": "tool_name", "params": {"param1": value1, "param2": value2}}
```

Use SI units: V for voltage, A for current, kHz for frequency.
"""

        if context:
            base += f"\n\nRelevant knowledge from database:\n{context}\n"

        return base

    def _parse_tool_call(self, response: str) -> tuple[str | None, dict | None]:
        """Extract tool call from LLM response if present."""
        match = re.search(r"```json\s*([\s\S]*?)\s*```", response)
        if match:
            try:
                data = json.loads(match.group(1).strip())
                if "tool" in data and "params" in data:
                    return data["tool"], data["params"]
            except json.JSONDecodeError:
                pass
        return None, None

    def chat(self, user_message: str, max_tool_calls: int = 3) -> str:
        """
        Process user message and return agent response.

        Supports tool calling: agent may request design calculations,
        which are executed and fed back for final answer.
        """
        # RAG: retrieve relevant context
        context = None
        if self.use_rag and self.retriever:
            docs = self.retriever.search(user_message, top_k=4)
            if docs:
                context = "\n---\n".join(docs)

        messages: list = [
            SystemMessage(content=self._build_system_prompt(context)),
            HumanMessage(content=user_message),
        ]

        llm = self._get_llm()
        tool_calls_made = 0

        while tool_calls_made < max_tool_calls:
            response_msg = llm.invoke(messages)
            response = response_msg.content if hasattr(response_msg, "content") else str(response_msg)
            tool_name, params = self._parse_tool_call(response)

            if tool_name is None or params is None:
                return response

            # Execute tool
            tool_result = execute_tool(tool_name, **params)
            tool_calls_made += 1

            # Append assistant response and tool result, get follow-up
            messages.append(AIMessage(content=response))
            messages.append(
                HumanMessage(
                    content=f"Tool result:\n{tool_result}\n\nPlease summarize the design for the user in a clear, actionable format."
                )
            )

        # Fallback if we hit max tool calls
        final_msg = llm.invoke(messages)
        return final_msg.content if hasattr(final_msg, "content") else str(final_msg)
