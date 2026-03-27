"""
Design calculation tools for power electronics.
"""

from pea.tools.calculator import (
    buck_boost_design,
    buck_converter_design,
    boost_converter_design,
    cuk_design,
    efficiency_estimate,
    execute_tool,
    flyback_design,
    forward_design,
    get_available_tools,
    llc_design,
    sepic_design,
    topology_recommendation,
)

__all__ = [
    "buck_converter_design",
    "boost_converter_design",
    "buck_boost_design",
    "sepic_design",
    "cuk_design",
    "forward_design",
    "flyback_design",
    "llc_design",
    "topology_recommendation",
    "efficiency_estimate",
    "execute_tool",
    "get_available_tools",
]
