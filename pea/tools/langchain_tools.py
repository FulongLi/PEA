"""
LangChain structured tools for PEA design calculations.

Uses @tool decorator for reliable tool calling with OpenAI and other LLMs.
"""

from __future__ import annotations

import json
from typing import Optional

from langchain_core.tools import tool

from pea.tools.calculator import (
    buck_boost_design,
    buck_converter_design,
    boost_converter_design,
    flyback_design,
    topology_recommendation,
)


def _format_result(result: dict) -> str:
    """Format design result as readable string for LLM."""
    return json.dumps(result, indent=2)


@tool
def recommend_topology(
    v_in: float,
    v_out: float,
    i_out: float,
    isolated: bool = False,
) -> str:
    """Recommend suitable converter topology (Buck, Boost, Buck-Boost, Flyback, LLC) based on input/output voltage, current, and whether galvanic isolation is required."""
    result = topology_recommendation(v_in=v_in, v_out=v_out, i_out=i_out, isolated=isolated)
    return _format_result(result)


@tool
def design_buck(
    v_in: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    ripple_current_pct: float = 0.3,
    ripple_voltage_pct: float = 0.01,
) -> str:
    """Design a Buck (step-down) converter. Use when V_out < V_in. Returns inductance, capacitance, duty cycle, and design notes."""
    result = buck_converter_design(
        v_in=v_in,
        v_out=v_out,
        i_out=i_out,
        f_sw_khz=f_sw_khz,
        ripple_current_pct=ripple_current_pct,
        ripple_voltage_pct=ripple_voltage_pct,
    )
    return _format_result(result)


@tool
def design_boost(
    v_in: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    ripple_current_pct: float = 0.3,
    ripple_voltage_pct: float = 0.01,
) -> str:
    """Design a Boost (step-up) converter. Use when V_out > V_in. Returns inductance, capacitance, duty cycle, and design notes."""
    result = boost_converter_design(
        v_in=v_in,
        v_out=v_out,
        i_out=i_out,
        f_sw_khz=f_sw_khz,
        ripple_current_pct=ripple_current_pct,
        ripple_voltage_pct=ripple_voltage_pct,
    )
    return _format_result(result)


@tool
def design_buck_boost(
    v_in: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    ripple_current_pct: float = 0.3,
    ripple_voltage_pct: float = 0.01,
) -> str:
    """Design a Buck-Boost (inverting) converter. Pass v_out as positive magnitude; output polarity is negative. Good for wide input range."""
    result = buck_boost_design(
        v_in=v_in,
        v_out=-abs(v_out),  # Calculator expects negative for inverting
        i_out=i_out,
        f_sw_khz=f_sw_khz,
        ripple_current_pct=ripple_current_pct,
        ripple_voltage_pct=ripple_voltage_pct,
    )
    return _format_result(result)


@tool
def design_flyback(
    v_in_min: float,
    v_in_max: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    n_ratio: Optional[float] = None,
) -> str:
    """Design a Flyback isolated converter. Use when galvanic isolation is required. v_in_min and v_in_max define input voltage range."""
    result = flyback_design(
        v_in_min=v_in_min,
        v_in_max=v_in_max,
        v_out=v_out,
        i_out=i_out,
        f_sw_khz=f_sw_khz,
        n_ratio=n_ratio,
    )
    return _format_result(result)


def get_pea_tools() -> list:
    """Return list of LangChain tools for PEA agent."""
    return [
        recommend_topology,
        design_buck,
        design_boost,
        design_buck_boost,
        design_flyback,
    ]
