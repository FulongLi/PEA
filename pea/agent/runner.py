"""
Power Electronics AI Agent - main agent logic with tool calling and RAG.

Uses LangChain structured tools for reliable tool calling with OpenAI.
"""
from __future__ import annotations

import os
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from pea.knowledge.retriever import KnowledgeRetriever
from pea.tools.langchain_tools import get_pea_tools


# Map LLM tool names to LangChain tool invokables
_TOOL_MAP: dict[str, Any] = {t.name: t for t in get_pea_tools()}


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
        """Lazy load LLM with structured tools bound."""
        if self._llm is not None:
            return self._llm

        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key."
            )

        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            temperature=0.2,
        )
        self._llm = llm.bind_tools(get_pea_tools())
        return self._llm

    def _build_system_prompt(self, context: str | None) -> str:
        """Build system prompt with RAG context."""
        base = """You are PEA (Power Electronics AI), an expert assistant for power electronics design.

Your capabilities:
1. Recommend converter topologies (Buck, Boost, Buck-Boost, Flyback, etc.) based on specs
2. Calculate design parameters (inductance, capacitance, duty cycle) using your tools
3. Answer questions about power electronics theory and design best practices

When the user provides specifications (V_in, V_out, I_out, etc.):
- First use recommend_topology to suggest a suitable topology
- Then use the appropriate design tool (design_buck, design_boost, etc.) to calculate parameters
- Present results clearly with units and brief design notes

Use SI units: V for voltage, A for current, kHz for frequency.
"""

        if context:
            base += f"\n\nRelevant knowledge from database:\n{context}\n"

        return base

    def chat(self, user_message: str, max_tool_calls: int = 5) -> str:
        """
        Process user message and return agent response.

        Uses LangChain structured tool calling: agent invokes design tools
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
        tool_rounds = 0

        while tool_rounds < max_tool_calls:
            response_msg = llm.invoke(messages)
            tool_calls = getattr(response_msg, "tool_calls", None) or []

            if not tool_calls:
                return response_msg.content or str(response_msg)

            # Append assistant message with tool calls
            messages.append(response_msg)

            # Execute each tool call and append ToolMessage
            for tc in tool_calls:
                name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                args = tc.get("args") if isinstance(tc, dict) else getattr(tc, "args", {})
                tc_id = tc.get("id") if isinstance(tc, dict) else getattr(tc, "id", "")

                tool_fn = _TOOL_MAP.get(name) if name else None
                if tool_fn:
                    try:
                        result = tool_fn.invoke(args)
                    except Exception as e:
                        result = f"Error: {e}"
                else:
                    result = f"Unknown tool: {name}"

                messages.append(
                    ToolMessage(content=str(result), tool_call_id=tc_id or "")
                )

            tool_rounds += 1

        # Max tool rounds reached; get final response
        final_msg = llm.invoke(messages)
        return final_msg.content or str(final_msg)
