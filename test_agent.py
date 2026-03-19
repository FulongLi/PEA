"""
Test script for PEA (Power Electronics AI) Agent.

Usage:
    python test_agent.py
    python test_agent.py "Design a 12V to 5V 2A Buck converter"

Requires OPENAI_API_KEY in environment or .env file.
"""

import os
import sys

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def main():
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Design a 12V to 5V 2A Buck converter"

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: Set OPENAI_API_KEY environment variable or add to .env")
        print("Example: export OPENAI_API_KEY=sk-your-key")
        sys.exit(1)

    print("PEA Agent Test")
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
