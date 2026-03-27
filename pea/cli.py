"""
Command-line interface for PEA (Power Electronics AI Agent).
"""

import argparse
import sys

from pea.tools.calculator import get_available_tools

_TOOL_CHOICES = [
    "buck", "boost", "buck_boost",
    "sepic", "cuk",
    "forward", "flyback", "llc",
    "recommend", "efficiency",
]

_CLI_TO_CALC = {
    "buck": "buck_converter_design",
    "boost": "boost_converter_design",
    "buck_boost": "buck_boost_design",
    "sepic": "sepic_design",
    "cuk": "cuk_design",
    "forward": "forward_design",
    "flyback": "flyback_design",
    "llc": "llc_design",
    "recommend": "topology_recommendation",
    "efficiency": "efficiency_estimate",
}

_ISOLATED_TOOLS = {"flyback", "forward"}


def run_cli():
    """Run the PEA CLI."""
    parser = argparse.ArgumentParser(
        description="PEA - Power Electronics AI Agent. Design assistant for DC-DC converters."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Chat
    chat_parser = subparsers.add_parser("chat", help="Chat with PEA AI agent (requires OPENAI_API_KEY)")
    chat_parser.add_argument(
        "message", nargs="?", default=None,
        help="Your question or design specs",
    )
    chat_parser.add_argument("-m", "--model", default="gpt-4o-mini", help="OpenAI model")

    # Tool
    tool_parser = subparsers.add_parser("tool", help="Run design tool directly (no API key needed)")
    tool_parser.add_argument("tool_name", choices=_TOOL_CHOICES, help="Design tool to run")
    tool_parser.add_argument("--v-in", type=float, help="Input voltage (V)")
    tool_parser.add_argument("--v-out", type=float, help="Output voltage (V)")
    tool_parser.add_argument("--i-out", type=float, help="Output current (A)")
    tool_parser.add_argument("--v-in-min", type=float, help="Min input voltage (isolated converters)")
    tool_parser.add_argument("--v-in-max", type=float, help="Max input voltage (isolated converters)")
    tool_parser.add_argument("--f-sw", type=float, default=100, help="Switching freq (kHz)")
    tool_parser.add_argument("--isolated", action="store_true", help="Require isolation (recommend)")
    tool_parser.add_argument("--q-factor", type=float, default=0.5, help="Q factor (LLC)")
    tool_parser.add_argument("--rds-on", type=float, default=50, help="MOSFET Rds(on) mΩ (efficiency)")
    tool_parser.add_argument("--dcr", type=float, default=30, help="Inductor DCR mΩ (efficiency)")
    tool_parser.add_argument("--vf-diode", type=float, default=0.5, help="Diode Vf V (efficiency)")

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

        calc_name = _CLI_TO_CALC[args.tool_name]

        if args.tool_name in _ISOLATED_TOOLS:
            if not all([args.v_in_min, args.v_in_max, args.v_out, args.i_out]):
                print(f"Error: {args.tool_name} requires --v-in-min, --v-in-max, --v-out, --i-out", file=sys.stderr)
                return 1
            result = execute_tool(calc_name, v_in_min=args.v_in_min, v_in_max=args.v_in_max,
                                  v_out=args.v_out, i_out=args.i_out, f_sw_khz=args.f_sw)
        elif args.tool_name == "recommend":
            if not all([args.v_in, args.v_out, args.i_out]):
                print("Error: recommend requires --v-in, --v-out, --i-out", file=sys.stderr)
                return 1
            result = execute_tool(calc_name, v_in=args.v_in, v_out=args.v_out,
                                  i_out=args.i_out, isolated=args.isolated)
        elif args.tool_name == "llc":
            if not all([args.v_in, args.v_out, args.i_out]):
                print("Error: llc requires --v-in, --v-out, --i-out", file=sys.stderr)
                return 1
            result = execute_tool(calc_name, v_in=args.v_in, v_out=args.v_out,
                                  i_out=args.i_out, f_sw_khz=args.f_sw, q_factor=args.q_factor)
        elif args.tool_name == "efficiency":
            if not all([args.v_in, args.v_out, args.i_out]):
                print("Error: efficiency requires --v-in, --v-out, --i-out", file=sys.stderr)
                return 1
            result = execute_tool(calc_name, v_in=args.v_in, v_out=args.v_out, i_out=args.i_out,
                                  f_sw_khz=args.f_sw, rds_on_mohm=args.rds_on,
                                  dcr_mohm=args.dcr, vf_diode=args.vf_diode)
        else:
            if not all([args.v_in, args.v_out, args.i_out]):
                print("Error: requires --v-in, --v-out, --i-out", file=sys.stderr)
                return 1
            result = execute_tool(calc_name, v_in=args.v_in, v_out=args.v_out,
                                  i_out=args.i_out, f_sw_khz=args.f_sw)

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
