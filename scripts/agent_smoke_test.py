"""
Manual smoke test for PEAAgent (OpenAI + tools + optional RAG).

Usage:
    python scripts/agent_smoke_test.py
    python scripts/agent_smoke_test.py "Design a 12V to 5V 2A Buck converter"

Requires OPENAI_API_KEY in the environment or a .env file in the repo root.
Not run by pytest; use for quick integration checks after agent changes.
"""

from __future__ import annotations

import os
import sys

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def main() -> None:
    prompt = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "Design a 12V to 5V 2A Buck converter"
    )

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: Set OPENAI_API_KEY or add it to .env")
        print("Example: set OPENAI_API_KEY=sk-...")
        sys.exit(1)

    print("PEA Agent smoke test")
    print("-" * 40)
    print(f"Prompt: {prompt}")
    print("-" * 40)

    from pea.agent.runner import PEAAgent

    agent = PEAAgent()
    response = agent.chat(prompt)

    print("\nResponse:")
    print(response)


if __name__ == "__main__":
    main()
