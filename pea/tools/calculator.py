"""
Power electronics design calculator.

Implements design equations for common converter topologies:
- Buck (step-down)
- Boost (step-up)
- Buck-Boost
- Flyback (isolated)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class DesignResult:
    """Result of a converter design calculation."""

    topology: str
    inductance_uH: float
    capacitance_uF: float
    switching_frequency_kHz: float
    duty_cycle: float
    ripple_current_A: Optional[float] = None
    ripple_voltage_V: Optional[float] = None
    notes: str = ""


def buck_converter_design(
    v_in: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    ripple_current_pct: float = 0.3,
    ripple_voltage_pct: float = 0.01,
) -> dict:
    """
    Design a Buck (step-down) converter.

    Args:
        v_in: Input voltage (V)
        v_out: Output voltage (V)
        i_out: Output current (A)
        f_sw_khz: Switching frequency (kHz)
        ripple_current_pct: Inductor current ripple as fraction of I_out (0.2-0.4 typical)
        ripple_voltage_pct: Output voltage ripple as fraction of V_out (0.01 typical)

    Returns:
        Design parameters as dict
    """
    if v_out >= v_in:
        return {"error": "Buck converter requires V_out < V_in (step-down)"}

    duty = v_out / v_in
    f_sw_hz = f_sw_khz * 1000

    # Inductor: L = V_out * (1 - D) / (f_sw * delta_I)
    delta_i = i_out * ripple_current_pct
    l_uH = (v_out * (1 - duty) / (f_sw_hz * delta_i)) * 1e6

    # Output capacitor: C = delta_I / (8 * f_sw * delta_V)
    delta_v = v_out * ripple_voltage_pct
    c_uF = (delta_i / (8 * f_sw_hz * delta_v)) * 1e6

    return {
        "topology": "Buck",
        "duty_cycle": round(duty, 3),
        "inductance_uH": round(l_uH, 2),
        "capacitance_uF": round(c_uF, 2),
        "switching_frequency_kHz": f_sw_khz,
        "ripple_current_A": round(delta_i, 3),
        "ripple_voltage_V": round(delta_v, 4),
        "notes": "Step-down converter. Use synchronous rectification for high efficiency.",
    }


def boost_converter_design(
    v_in: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    ripple_current_pct: float = 0.3,
    ripple_voltage_pct: float = 0.01,
) -> dict:
    """
    Design a Boost (step-up) converter.

    Args:
        v_in: Input voltage (V)
        v_out: Output voltage (V)
        i_out: Output current (A)
        f_sw_khz: Switching frequency (kHz)
        ripple_current_pct: Inductor current ripple as fraction of I_in
        ripple_voltage_pct: Output voltage ripple as fraction of V_out

    Returns:
        Design parameters as dict
    """
    if v_out <= v_in:
        return {"error": "Boost converter requires V_out > V_in (step-up)"}

    duty = 1 - (v_in / v_out)
    f_sw_hz = f_sw_khz * 1000
    i_in = i_out * (v_out / v_in)  # Power balance

    # Inductor: L = V_in * D / (f_sw * delta_I)
    delta_i = i_in * ripple_current_pct
    l_uH = (v_in * duty / (f_sw_hz * delta_i)) * 1e6

    # Output capacitor: C = I_out * D / (f_sw * delta_V)
    delta_v = v_out * ripple_voltage_pct
    c_uF = (i_out * duty / (f_sw_hz * delta_v)) * 1e6

    return {
        "topology": "Boost",
        "duty_cycle": round(duty, 3),
        "inductance_uH": round(l_uH, 2),
        "capacitance_uF": round(c_uF, 2),
        "switching_frequency_kHz": f_sw_khz,
        "ripple_current_A": round(delta_i, 3),
        "ripple_voltage_V": round(delta_v, 4),
        "notes": "Step-up converter. Watch for right-half-plane zero at high duty cycle.",
    }


def buck_boost_design(
    v_in: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    ripple_current_pct: float = 0.3,
    ripple_voltage_pct: float = 0.01,
) -> dict:
    """
    Design a Buck-Boost (inverting) converter.

    Args:
        v_in: Input voltage (V)
        v_out: Output voltage magnitude (V), output is negative
        i_out: Output current (A)
        f_sw_khz: Switching frequency (kHz)
        ripple_current_pct: Inductor current ripple
        ripple_voltage_pct: Output voltage ripple

    Returns:
        Design parameters as dict
    """
    duty = abs(v_out) / (v_in + abs(v_out))
    f_sw_hz = f_sw_khz * 1000
    i_in = i_out * (abs(v_out) / v_in)

    delta_i = i_in * ripple_current_pct
    l_uH = (v_in * duty / (f_sw_hz * delta_i)) * 1e6

    delta_v = abs(v_out) * ripple_voltage_pct
    c_uF = (i_out * duty / (f_sw_hz * delta_v)) * 1e6

    return {
        "topology": "Buck-Boost",
        "duty_cycle": round(duty, 3),
        "inductance_uH": round(l_uH, 2),
        "capacitance_uF": round(c_uF, 2),
        "switching_frequency_kHz": f_sw_khz,
        "ripple_current_A": round(delta_i, 3),
        "ripple_voltage_V": round(delta_v, 4),
        "notes": "Inverting topology. Output polarity is reversed. Good for wide input range.",
    }


def flyback_design(
    v_in_min: float,
    v_in_max: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    n_ratio: Optional[float] = None,
) -> dict:
    """
    Design a Flyback (isolated) converter - simplified first-pass design.

    Args:
        v_in_min: Minimum input voltage (V)
        v_in_max: Maximum input voltage (V)
        v_out: Output voltage (V)
        i_out: Output current (A)
        f_sw_khz: Switching frequency (kHz)
        n_ratio: Turns ratio Ns/Np (optional, will be calculated if not given)

    Returns:
        Design parameters as dict
    """
    f_sw_hz = f_sw_khz * 1000
    v_in_nom = (v_in_min + v_in_max) / 2

    # Typical duty cycle 0.4-0.5 for DCM/BCM
    duty = 0.45
    if n_ratio is None:
        n_ratio = (v_out / v_in_nom) * (1 - duty) / duty

    # Primary inductance (simplified): Lp = V_in^2 * D^2 / (2 * P_out * f_sw) for DCM
    p_out = v_out * i_out
    l_primary_uH = (v_in_min**2 * duty**2 / (2 * p_out * f_sw_hz)) * 1e6

    return {
        "topology": "Flyback",
        "duty_cycle": round(duty, 3),
        "turns_ratio_Ns_Np": round(n_ratio, 2),
        "primary_inductance_uH": round(l_primary_uH, 2),
        "switching_frequency_kHz": f_sw_khz,
        "notes": "Isolated converter. Add snubber for MOSFET protection. Consider LLC for higher power.",
    }


def topology_recommendation(v_in: float, v_out: float, i_out: float, isolated: bool = False) -> dict:
    """
    Recommend suitable converter topology based on specifications.

    Args:
        v_in: Input voltage (V)
        v_out: Output voltage (V)
        i_out: Output current (A)
        isolated: Whether galvanic isolation is required

    Returns:
        Recommendation with topology and rationale
    """
    v_ratio = v_out / v_in
    p_out = v_out * i_out

    if isolated:
        if p_out < 50:
            return {
                "recommended": "Flyback",
                "alternatives": ["Forward"],
                "rationale": "Flyback is cost-effective for low-power isolated applications.",
            }
        elif p_out < 200:
            return {
                "recommended": "Flyback",
                "alternatives": ["Forward", "Push-Pull"],
                "rationale": "Flyback or Forward suitable for medium power. Flyback simpler.",
            }
        else:
            return {
                "recommended": "LLC or Forward",
                "alternatives": ["Phase-shifted Full Bridge"],
                "rationale": "LLC offers high efficiency at higher power. Forward for moderate complexity.",
            }

    # Non-isolated
    if v_ratio < 0.9:
        return {
            "recommended": "Buck",
            "alternatives": ["Buck-Boost"],
            "rationale": "Buck is optimal for step-down (V_out < V_in). Highest efficiency.",
        }
    elif v_ratio > 1.1:
        return {
            "recommended": "Boost",
            "alternatives": ["Buck-Boost", "SEPIC"],
            "rationale": "Boost is optimal for step-up (V_out > V_in).",
        }
    else:
        return {
            "recommended": "Buck-Boost or SEPIC",
            "alternatives": ["Buck + Boost cascade"],
            "rationale": "Input and output voltages are close. Buck-Boost or SEPIC handle overlap.",
        }


def execute_tool(tool_name: str, **kwargs) -> str:
    """Execute a design tool and return result as JSON string."""
    import json

    tools = {
        "buck_converter_design": buck_converter_design,
        "boost_converter_design": boost_converter_design,
        "buck_boost_design": buck_boost_design,
        "flyback_design": flyback_design,
        "topology_recommendation": topology_recommendation,
    }
    if tool_name not in tools:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    try:
        result = tools[tool_name](**kwargs)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_available_tools() -> list[dict]:
    """Return list of available calculation tools for the agent."""
    return [
        {
            "name": "buck_converter_design",
            "description": "Design a Buck (step-down) converter. Use when V_out < V_in.",
            "parameters": ["v_in", "v_out", "i_out", "f_sw_khz", "ripple_current_pct", "ripple_voltage_pct"],
        },
        {
            "name": "boost_converter_design",
            "description": "Design a Boost (step-up) converter. Use when V_out > V_in.",
            "parameters": ["v_in", "v_out", "i_out", "f_sw_khz", "ripple_current_pct", "ripple_voltage_pct"],
        },
        {
            "name": "buck_boost_design",
            "description": "Design a Buck-Boost converter. Use for inverting or wide input range.",
            "parameters": ["v_in", "v_out", "i_out", "f_sw_khz", "ripple_current_pct", "ripple_voltage_pct"],
        },
        {
            "name": "flyback_design",
            "description": "Design a Flyback isolated converter. Use when isolation is required.",
            "parameters": ["v_in_min", "v_in_max", "v_out", "i_out", "f_sw_khz", "n_ratio"],
        },
        {
            "name": "topology_recommendation",
            "description": "Recommend suitable converter topology based on specs.",
            "parameters": ["v_in", "v_out", "i_out", "isolated"],
        },
    ]
