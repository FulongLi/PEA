"""
Power electronics design calculator.

Implements design equations for common converter topologies:
- Buck (step-down)
- Boost (step-up)
- Buck-Boost (inverting)
- SEPIC (non-inverting buck-boost)
- Cuk (inverting, continuous input/output current)
- Forward (isolated, single-ended)
- Flyback (isolated, coupled inductor)
- LLC resonant (isolated, high efficiency)

Also provides topology recommendation and efficiency estimation.
"""
from __future__ import annotations

import math
from typing import Optional


# ── Basic Topologies ─────────────────────────────────────────────────────


def buck_converter_design(
    v_in: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    ripple_current_pct: float = 0.3,
    ripple_voltage_pct: float = 0.01,
) -> dict:
    """Design a Buck (step-down) converter."""
    if v_out >= v_in:
        return {"error": "Buck converter requires V_out < V_in (step-down)"}

    duty = v_out / v_in
    f_sw_hz = f_sw_khz * 1000

    delta_i = i_out * ripple_current_pct
    l_uH = (v_out * (1 - duty) / (f_sw_hz * delta_i)) * 1e6

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
    """Design a Boost (step-up) converter."""
    if v_out <= v_in:
        return {"error": "Boost converter requires V_out > V_in (step-up)"}

    duty = 1 - (v_in / v_out)
    f_sw_hz = f_sw_khz * 1000
    i_in = i_out * (v_out / v_in)

    delta_i = i_in * ripple_current_pct
    l_uH = (v_in * duty / (f_sw_hz * delta_i)) * 1e6

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
    """Design a Buck-Boost (inverting) converter. v_out is treated as magnitude."""
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


# ── New Topologies ───────────────────────────────────────────────────────


def sepic_design(
    v_in: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    ripple_current_pct: float = 0.3,
    ripple_voltage_pct: float = 0.01,
) -> dict:
    """
    Design a SEPIC (Single-Ended Primary-Inductor Converter).

    Non-inverting topology that can step up or step down.
    Requires two inductors (or a coupled inductor) and a coupling capacitor.
    """
    duty = v_out / (v_in + v_out)
    f_sw_hz = f_sw_khz * 1000
    i_in = i_out * v_out / v_in

    delta_i = i_in * ripple_current_pct
    # Each inductor carries the input or output current respectively
    l1_uH = (v_in * duty / (f_sw_hz * delta_i)) * 1e6
    l2_uH = l1_uH  # Matched inductors for coupled-inductor designs

    delta_v = v_out * ripple_voltage_pct
    # Output capacitor sized for charge delivered during switch-on interval
    c_out_uF = (i_out * duty / (f_sw_hz * delta_v)) * 1e6
    # Coupling capacitor carries full load current; size for ~5% V_in ripple
    c_couple_uF = (i_out * duty / (f_sw_hz * v_in * 0.05)) * 1e6

    return {
        "topology": "SEPIC",
        "duty_cycle": round(duty, 3),
        "L1_inductance_uH": round(l1_uH, 2),
        "L2_inductance_uH": round(l2_uH, 2),
        "output_capacitance_uF": round(c_out_uF, 2),
        "coupling_capacitance_uF": round(c_couple_uF, 2),
        "switching_frequency_kHz": f_sw_khz,
        "ripple_current_A": round(delta_i, 3),
        "ripple_voltage_V": round(delta_v, 4),
        "notes": (
            "Non-inverting buck-boost. Same ground for input and output. "
            "L1 and L2 can be wound on the same core (coupled inductor). "
            "Higher component count than Buck or Boost alone."
        ),
    }


def cuk_design(
    v_in: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    ripple_current_pct: float = 0.3,
    ripple_voltage_pct: float = 0.01,
) -> dict:
    """
    Design a Cuk converter.

    Inverting topology with continuous input and output currents.
    Requires two inductors and a coupling capacitor.
    """
    vo_mag = abs(v_out)
    duty = vo_mag / (v_in + vo_mag)
    f_sw_hz = f_sw_khz * 1000
    i_in = i_out * vo_mag / v_in

    delta_i_in = i_in * ripple_current_pct
    delta_i_out = i_out * ripple_current_pct

    l1_uH = (v_in * duty / (f_sw_hz * delta_i_in)) * 1e6
    l2_uH = (vo_mag * (1 - duty) / (f_sw_hz * delta_i_out)) * 1e6

    delta_v = vo_mag * ripple_voltage_pct
    c_out_uF = (delta_i_out / (8 * f_sw_hz * delta_v)) * 1e6
    # Coupling cap carries full load; size for ~5% ripple on V_in + V_out
    c_couple_uF = (i_out * duty / (f_sw_hz * (v_in + vo_mag) * 0.05)) * 1e6

    return {
        "topology": "Cuk",
        "duty_cycle": round(duty, 3),
        "L1_input_inductance_uH": round(l1_uH, 2),
        "L2_output_inductance_uH": round(l2_uH, 2),
        "output_capacitance_uF": round(c_out_uF, 2),
        "coupling_capacitance_uF": round(c_couple_uF, 2),
        "switching_frequency_kHz": f_sw_khz,
        "ripple_current_input_A": round(delta_i_in, 3),
        "ripple_current_output_A": round(delta_i_out, 3),
        "ripple_voltage_V": round(delta_v, 4),
        "notes": (
            "Inverting topology with continuous input and output currents (low EMI). "
            "Output polarity is negative. L1/L2 can share a coupled core. "
            "Coupling capacitor must handle high ripple current."
        ),
    }


def forward_design(
    v_in_min: float,
    v_in_max: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    n_ratio: Optional[float] = None,
) -> dict:
    """
    Design a Forward converter (isolated single-ended).

    Suitable for ~50-300 W. Requires a reset winding or active clamp.
    """
    f_sw_hz = f_sw_khz * 1000
    v_in_nom = (v_in_min + v_in_max) / 2

    # Max duty limited to 0.5 for voltage-second reset with 1:1 reset winding
    d_max = 0.5
    if n_ratio is None:
        n_ratio = v_out / (v_in_min * d_max)

    duty_nom = v_out / (n_ratio * v_in_nom)
    duty_nom = min(duty_nom, d_max)

    # Output inductor (same as Buck post-rectifier)
    delta_i = i_out * 0.3
    v_sec = n_ratio * v_in_nom
    l_uH = ((v_sec * duty_nom - v_out) / (f_sw_hz * delta_i)) * 1e6
    l_uH = max(l_uH, 0.1)

    delta_v = v_out * 0.01
    c_uF = (delta_i / (8 * f_sw_hz * delta_v)) * 1e6

    # Peak switch voltage = V_in + V_reset ≈ 2*V_in for 1:1 reset
    v_switch_peak = 2 * v_in_max

    return {
        "topology": "Forward",
        "duty_cycle": round(duty_nom, 3),
        "turns_ratio_Ns_Np": round(n_ratio, 3),
        "output_inductance_uH": round(l_uH, 2),
        "output_capacitance_uF": round(c_uF, 2),
        "switching_frequency_kHz": f_sw_khz,
        "peak_switch_voltage_V": round(v_switch_peak, 1),
        "ripple_current_A": round(delta_i, 3),
        "notes": (
            "Isolated single-ended topology. Max D ≈ 0.5 with 1:1 reset winding. "
            "Good for 50-300 W. MOSFET sees ~2x V_in. "
            "Active clamp allows D > 0.5 and recovers leakage energy."
        ),
    }


def flyback_design(
    v_in_min: float,
    v_in_max: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    n_ratio: Optional[float] = None,
) -> dict:
    """Design a Flyback (isolated) converter - simplified first-pass design."""
    f_sw_hz = f_sw_khz * 1000
    v_in_nom = (v_in_min + v_in_max) / 2

    duty = 0.45
    if n_ratio is None:
        n_ratio = (v_out / v_in_nom) * (1 - duty) / duty

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


def llc_design(
    v_in: float,
    v_out: float,
    i_out: float,
    f_sw_khz: float = 100,
    q_factor: float = 0.5,
    n_ratio: Optional[float] = None,
) -> dict:
    """
    Design an LLC resonant converter - first-pass resonant tank sizing.

    The LLC uses a series resonant inductor (Lr), magnetizing inductor (Lm),
    and resonant capacitor (Cr).  Frequency modulation around the resonant
    frequency controls the output.

    Args:
        v_in: DC input voltage (V) — typically from a PFC front-end
        v_out: Output voltage (V)
        i_out: Output current (A)
        f_sw_khz: Nominal switching frequency ≈ resonant frequency (kHz)
        q_factor: Loaded quality factor (0.3-0.8 typical; lower = wider gain range)
        n_ratio: Transformer turns ratio Ns/Np (auto-calculated if None)
    """
    f_r_hz = f_sw_khz * 1000
    p_out = v_out * i_out
    if p_out <= 0:
        return {"error": "Output power must be positive"}

    if n_ratio is None:
        # At resonance, gain = 1 → V_out = n * V_in / 2  (full-bridge)
        n_ratio = 2 * v_out / v_in

    r_ac = 8 * (n_ratio ** 2) * (v_out ** 2) / (math.pi ** 2 * p_out)

    # Cr from Q = 1/(2*pi*fr*Cr*R_ac)  →  Cr = 1/(2*pi*fr*Q*R_ac)
    c_r_nF = 1e9 / (2 * math.pi * f_r_hz * q_factor * r_ac)

    # Lr from fr = 1/(2*pi*sqrt(Lr*Cr))
    c_r_f = c_r_nF * 1e-9
    l_r_uH = (1 / ((2 * math.pi * f_r_hz) ** 2 * c_r_f)) * 1e6

    # Lm typically 3-7x Lr for good gain range; use 5x as starting point
    lm_ratio = 5.0
    l_m_uH = l_r_uH * lm_ratio

    return {
        "topology": "LLC Resonant",
        "turns_ratio_Ns_Np": round(n_ratio, 3),
        # High-power / low-gain designs can yield sub-0.01 µH Lr; keep extra digits.
        "resonant_inductance_Lr_uH": round(l_r_uH, 4),
        "magnetizing_inductance_Lm_uH": round(l_m_uH, 4),
        "resonant_capacitance_Cr_nF": round(c_r_nF, 2),
        "Lm_Lr_ratio": lm_ratio,
        "resonant_frequency_kHz": f_sw_khz,
        "Q_factor": q_factor,
        "equivalent_ac_resistance_ohm": round(r_ac, 2),
        "notes": (
            "LLC resonant converter (full-bridge primary, center-tap secondary assumed). "
            "Achieves ZVS over full load range when operated near or above resonance. "
            "Lm/Lr ratio of 5 is a starting point — decrease for wider gain range, "
            "increase for lower circulating current. Verify gain curves for V_in range."
        ),
    }


# ── Efficiency Estimation ────────────────────────────────────────────────


def efficiency_estimate(
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
) -> dict:
    """
    Estimate converter efficiency from component-level loss parameters.

    Provides a first-order breakdown of conduction and switching losses
    for a generic non-isolated converter (Buck-like model).  The estimate
    is conservative and intended for initial component selection.

    Args:
        v_in: Input voltage (V)
        v_out: Output voltage (V)
        i_out: Output current (A)
        f_sw_khz: Switching frequency (kHz)
        rds_on_mohm: High-side MOSFET Rds(on) in milliohms
        dcr_mohm: Inductor DC resistance in milliohms
        vf_diode: Freewheeling diode forward voltage (V); ignored if sync_rect
        t_rise_ns: MOSFET turn-on rise time (ns)
        t_fall_ns: MOSFET turn-off fall time (ns)
        sync_rect: True if using synchronous rectification (MOSFET instead of diode)
    """
    p_out = v_out * i_out
    if p_out <= 0:
        return {"error": "Output power must be positive"}

    f_sw_hz = f_sw_khz * 1000
    rds = rds_on_mohm / 1000
    dcr = dcr_mohm / 1000
    duty = min(v_out / v_in, 0.99) if v_out < v_in else max(1 - v_in / v_out, 0.01)

    i_rms_sw = i_out * math.sqrt(duty)

    # Conduction losses
    p_cond_fet = i_rms_sw ** 2 * rds
    p_cond_inductor = i_out ** 2 * dcr

    if sync_rect:
        p_cond_diode = i_out ** 2 * (1 - duty) * rds  # low-side FET
    else:
        p_cond_diode = vf_diode * i_out * (1 - duty)

    p_conduction = p_cond_fet + p_cond_inductor + p_cond_diode

    # Switching losses (overlap model)
    t_rise = t_rise_ns * 1e-9
    t_fall = t_fall_ns * 1e-9
    p_sw_on = 0.5 * v_in * i_out * t_rise * f_sw_hz
    p_sw_off = 0.5 * v_in * i_out * t_fall * f_sw_hz
    p_switching = p_sw_on + p_sw_off

    p_total_loss = p_conduction + p_switching
    p_in = p_out + p_total_loss
    eta = p_out / p_in if p_in > 0 else 0

    return {
        "output_power_W": round(p_out, 2),
        "estimated_efficiency_pct": round(eta * 100, 1),
        "total_loss_W": round(p_total_loss, 3),
        "conduction_loss_W": round(p_conduction, 3),
        "switching_loss_W": round(p_switching, 3),
        "breakdown": {
            "MOSFET_conduction_W": round(p_cond_fet, 3),
            "inductor_DCR_W": round(p_cond_inductor, 3),
            "diode_or_SR_conduction_W": round(p_cond_diode, 3),
            "turn_on_loss_W": round(p_sw_on, 3),
            "turn_off_loss_W": round(p_sw_off, 3),
        },
        "notes": (
            f"{'Synchronous rectification' if sync_rect else 'Diode rectification'}. "
            "First-order estimate; does not include gate-drive, quiescent, or core losses. "
            "Actual efficiency may differ by 1-3%."
        ),
    }


# ── Topology Recommendation ─────────────────────────────────────────────


def topology_recommendation(v_in: float, v_out: float, i_out: float, isolated: bool = False) -> dict:
    """Recommend suitable converter topology based on specifications."""
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
                "recommended": "LLC Resonant",
                "alternatives": ["Forward", "Phase-shifted Full Bridge"],
                "rationale": (
                    "LLC resonant offers highest efficiency at higher power with ZVS. "
                    "Forward converter is simpler but less efficient."
                ),
            }

    if v_ratio < 0.9:
        rec = {
            "recommended": "Buck",
            "alternatives": ["Buck-Boost"],
            "rationale": "Buck is optimal for step-down (V_out < V_in). Highest efficiency.",
        }
    elif v_ratio > 1.1:
        rec = {
            "recommended": "Boost",
            "alternatives": ["SEPIC", "Buck-Boost"],
            "rationale": "Boost is optimal for step-up (V_out > V_in).",
        }
    else:
        rec = {
            "recommended": "SEPIC",
            "alternatives": ["Cuk", "Buck-Boost", "Buck + Boost cascade"],
            "rationale": (
                "Input and output voltages are close. SEPIC provides non-inverting "
                "buck-boost capability with common ground. Cuk alternative if "
                "continuous I/O current is needed."
            ),
        }

    rec["output_power_W"] = round(p_out, 1)
    return rec


# ── Tool dispatch ────────────────────────────────────────────────────────


_TOOL_REGISTRY: dict[str, callable] = {
    "buck_converter_design": buck_converter_design,
    "boost_converter_design": boost_converter_design,
    "buck_boost_design": buck_boost_design,
    "sepic_design": sepic_design,
    "cuk_design": cuk_design,
    "forward_design": forward_design,
    "flyback_design": flyback_design,
    "llc_design": llc_design,
    "topology_recommendation": topology_recommendation,
    "efficiency_estimate": efficiency_estimate,
}


def execute_tool(tool_name: str, **kwargs) -> str:
    """Execute a design tool and return result as JSON string."""
    import json

    fn = _TOOL_REGISTRY.get(tool_name)
    if fn is None:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    try:
        result = fn(**kwargs)
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
            "name": "sepic_design",
            "description": "Design a SEPIC converter. Non-inverting buck-boost with common ground.",
            "parameters": ["v_in", "v_out", "i_out", "f_sw_khz", "ripple_current_pct", "ripple_voltage_pct"],
        },
        {
            "name": "cuk_design",
            "description": "Design a Cuk converter. Inverting with continuous input/output currents.",
            "parameters": ["v_in", "v_out", "i_out", "f_sw_khz", "ripple_current_pct", "ripple_voltage_pct"],
        },
        {
            "name": "forward_design",
            "description": "Design a Forward isolated converter. Good for 50-300 W.",
            "parameters": ["v_in_min", "v_in_max", "v_out", "i_out", "f_sw_khz", "n_ratio"],
        },
        {
            "name": "flyback_design",
            "description": "Design a Flyback isolated converter. Use when isolation is required.",
            "parameters": ["v_in_min", "v_in_max", "v_out", "i_out", "f_sw_khz", "n_ratio"],
        },
        {
            "name": "llc_design",
            "description": "Design an LLC resonant converter. High efficiency isolated topology with ZVS.",
            "parameters": ["v_in", "v_out", "i_out", "f_sw_khz", "q_factor", "n_ratio"],
        },
        {
            "name": "topology_recommendation",
            "description": "Recommend suitable converter topology based on specs.",
            "parameters": ["v_in", "v_out", "i_out", "isolated"],
        },
        {
            "name": "efficiency_estimate",
            "description": "Estimate converter efficiency and loss breakdown.",
            "parameters": [
                "v_in", "v_out", "i_out", "f_sw_khz",
                "rds_on_mohm", "dcr_mohm", "vf_diode",
                "t_rise_ns", "t_fall_ns", "sync_rect",
            ],
        },
    ]
