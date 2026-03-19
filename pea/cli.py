"""
Command-line interface for PEA (Power Electronics AI Agent).
"""

import argparse
import sys

from pea.tools.calculator import get_available_tools


def run_cli():
    """Run the PEA CLI."""
    parser = argparse.ArgumentParser(
        description="PEA - Power Electronics AI Agent. Design assistant for DC-DC converters."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Chat command (interactive with AI)
    chat_parser = subparsers.add_parser("chat", help="Chat with PEA AI agent (requires OPENAI_API_KEY)")
    chat_parser.add_argument(
        "message",
        nargs="?",
        default=None,
        help="Your question or design specs (e.g., 'Design a 12V to 5V 2A converter')",
    )
    chat_parser.add_argument(
        "-m", "--model",
        default="gpt-4o-mini",
        help="OpenAI model (default: gpt-4o-mini)",
    )

    # Tool command (direct calculation without AI)
    tool_parser = subparsers.add_parser("tool", help="Run design tool directly (no API key needed)")
    tool_parser.add_argument(
        "tool_name",
        choices=["buck", "boost", "buck_boost", "flyback", "recommend"],
        help="Design tool to run",
    )
    tool_parser.add_argument("--v-in", type=float, help="Input voltage (V)")
    tool_parser.add_argument("--v-out", type=float, help="Output voltage (V)")
    tool_parser.add_argument("--i-out", type=float, help="Output current (A)")
    tool_parser.add_argument("--v-in-min", type=float, help="Min input voltage (Flyback)")
    tool_parser.add_argument("--v-in-max", type=float, help="Max input voltage (Flyback)")
    tool_parser.add_argument("--f-sw", type=float, default=100, help="Switching freq (kHz)")
    tool_parser.add_argument("--isolated", action="store_true", help="Require isolation (recommend)")

    # List tools
    subparsers.add_parser("tools", help="List available design tools")

    args = parser.parse_args()

    if args.command == "tools":
        tools = get_available_tools()
        print("Available design tools:\n")
        for t in tools:
            print(f"  {t['name']}")
            print(f"    {t['description']}")
            print(f"    Params: {', '.join(t['parameters'])}\n")
        return 0

    if args.command == "tool":
        from pea.tools.calculator import execute_tool

        tool_map = {
            "buck": "buck_converter_design",
            "boost": "boost_converter_design",
            "buck_boost": "buck_boost_design",
            "flyback": "flyback_design",
            "recommend": "topology_recommendation",
        }
        name = tool_map[args.tool_name]

        if name == "flyback":
            if args.v_in_min is None or args.v_in_max is None or args.v_out is None or args.i_out is None:
                print("Error: flyback requires --v-in-min, --v-in-max, --v-out, --i-out", file=sys.stderr)
                return 1
            result = execute_tool(name, v_in_min=args.v_in_min, v_in_max=args.v_in_max,
                                 v_out=args.v_out, i_out=args.i_out, f_sw_khz=args.f_sw)
        elif name == "topology_recommendation":
            if args.v_in is None or args.v_out is None or args.i_out is None:
                print("Error: recommend requires --v-in, --v-out, --i-out", file=sys.stderr)
                return 1
            result = execute_tool(name, v_in=args.v_in, v_out=args.v_out, i_out=args.i_out,
                                 isolated=args.isolated)
        else:
            if args.v_in is None or args.v_out is None or args.i_out is None:
                print("Error: requires --v-in, --v-out, --i-out", file=sys.stderr)
                return 1
            result = execute_tool(name, v_in=args.v_in, v_out=args.v_out, i_out=args.i_out,
                                 f_sw_khz=args.f_sw)

        print(result)
        return 0

    if args.command == "chat":
        from pea.agent.runner import PEAAgent

        agent = PEAAgent(model=args.model)
        try:
            if args.message:
                msg = args.message
            else:
                print("PEA - Power Electronics AI Agent")
                print("Enter your design specs or question (Ctrl+C to exit):\n")
                msg = input("You: ").strip()
                if not msg:
                    return 0

            response = agent.chat(msg)
            print("\nPEA:", response)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            print("Set OPENAI_API_KEY or use 'pea tool' for direct calculations.", file=sys.stderr)
            return 1
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
