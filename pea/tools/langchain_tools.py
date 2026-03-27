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
    cuk_design as _cuk_design,
    efficiency_estimate as _efficiency_estimate,
    flyback_design,
    forward_design as _forward_design,
    llc_design as _llc_design,
    sepic_design as _sepic_design,
    topology_recommendation,
)


def _fmt(result: dict) -> str:
    return json.dumps(result, indent=2)


# ── Topology recommendation ──────────────────────────────────────────────


@tool
def recommend_topology(
    v_in: float,
    v_out: float,
    i_out: float,
    isolated: bool = False,
) -> str:
    """Recommend a converter topology (Buck, Boost, SEPIC, Cuk, Forward, Flyback, LLC) based on input/output voltage, current, and whether galvanic isolation is required."""
    return _fmt(topology_recommendation(v_in=v_in, v_out=v_out, i_out=i_out, isolated=isolated))


# ── Non-isolated designs ─────────────────────────────────────────────────


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
    return _fmt(buck_converter_design(
        v_in=v_in, v_out=v_out, i_out=i_out,
        f_sw_khz=f_sw_khz, ripple_current_pct=ripple_current_pct,
        ripple_voltage_pct=ripple_voltage_pct,
    ))


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
    return _fmt(boost_converter_design(
        v_in=v_in, v_out=v_out, i_out=i_out,
        f_sw_khz=f_sw_khz, ripple_current_pct=ripple_current_pct,
        ripple_voltage_pct=ripple_voltage_pct,
    ))


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
    return _fmt(buck_boost_design(
        v_in=v_in, v_out=-abs(v_out), i_out=i_out,
        f_sw_khz=f_sw_khz, ripple_current_pct=ripple_current_pct,
        ripple_voltage_pct=ripple_voltage_pct,
    ))


@tool
def design_sepic(
    v_in: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    ripple_current_pct: float = 0.3,
    ripple_voltage_pct: float = 0.01,
) -> str:
    """Design a SEPIC converter (non-inverting buck-boost). Can step up or step down with common ground and positive output."""
    return _fmt(_sepic_design(
        v_in=v_in, v_out=v_out, i_out=i_out,
        f_sw_khz=f_sw_khz, ripple_current_pct=ripple_current_pct,
        ripple_voltage_pct=ripple_voltage_pct,
    ))


@tool
def design_cuk(
    v_in: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    ripple_current_pct: float = 0.3,
    ripple_voltage_pct: float = 0.01,
) -> str:
    """Design a Cuk converter (inverting, continuous input & output current). Low input/output ripple current."""
    return _fmt(_cuk_design(
        v_in=v_in, v_out=v_out, i_out=i_out,
        f_sw_khz=f_sw_khz, ripple_current_pct=ripple_current_pct,
        ripple_voltage_pct=ripple_voltage_pct,
    ))


# ── Isolated designs ─────────────────────────────────────────────────────


@tool
def design_forward(
    v_in_min: float,
    v_in_max: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    n_ratio: Optional[float] = None,
) -> str:
    """Design a Forward converter (isolated single-ended). Good for 50-300 W. v_in_min/v_in_max define input voltage range."""
    return _fmt(_forward_design(
        v_in_min=v_in_min, v_in_max=v_in_max, v_out=v_out, i_out=i_out,
        f_sw_khz=f_sw_khz, n_ratio=n_ratio,
    ))


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
    return _fmt(flyback_design(
        v_in_min=v_in_min, v_in_max=v_in_max, v_out=v_out, i_out=i_out,
        f_sw_khz=f_sw_khz, n_ratio=n_ratio,
    ))


@tool
def design_llc(
    v_in: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    q_factor: float = 0.5,
    n_ratio: Optional[float] = None,
) -> str:
    """Design an LLC resonant converter. High-efficiency isolated topology with ZVS. Good for >200 W."""
    return _fmt(_llc_design(
        v_in=v_in, v_out=v_out, i_out=i_out,
        f_sw_khz=f_sw_khz, q_factor=q_factor, n_ratio=n_ratio,
    ))


# ── Efficiency estimation ────────────────────────────────────────────────


@tool
def estimate_efficiency(
    v_in: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    rds_on_mohm: float = 50.0,
    dcr_mohm: float = 30.0,
    vf_diode: float = 0.5,
    t_rise_ns: float = 20.0,
    t_fall_ns: float = 20.0,
    sync_rect: bool = False,
) -> str:
    """Estimate converter efficiency and loss breakdown given component parameters (MOSFET Rds_on, inductor DCR, diode Vf, switching times)."""
    return _fmt(_efficiency_estimate(
        v_in=v_in, v_out=v_out, i_out=i_out, f_sw_khz=f_sw_khz,
        rds_on_mohm=rds_on_mohm, dcr_mohm=dcr_mohm, vf_diode=vf_diode,
        t_rise_ns=t_rise_ns, t_fall_ns=t_fall_ns, sync_rect=sync_rect,
    ))


# ── Tool list ────────────────────────────────────────────────────────────


def get_pea_tools() -> list:
    """Return list of LangChain tools for PEA agent."""
    return [
        recommend_topology,
        design_buck,
        design_boost,
        design_buck_boost,
        design_sepic,
        design_cuk,
        design_forward,
        design_flyback,
        design_llc,
        estimate_efficiency,
    ]
