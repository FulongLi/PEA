"""
Tests for pea.tools.calculator — every topology calculator and the efficiency estimator.
"""

import json
import math

import pytest

from pea.tools.calculator import (
    boost_converter_design,
    buck_boost_design,
    buck_converter_design,
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


# ── Buck ─────────────────────────────────────────────────────────────────


class TestBuck:
    def test_basic_12v_to_5v(self):
        r = buck_converter_design(v_in=12, v_out=5, i_out=2)
        assert r["topology"] == "Buck"
        assert 0 < r["duty_cycle"] < 1
        assert pytest.approx(r["duty_cycle"], abs=0.01) == 5 / 12
        assert r["inductance_uH"] > 0
        assert r["capacitance_uF"] > 0

    def test_rejects_step_up(self):
        r = buck_converter_design(v_in=5, v_out=12, i_out=1)
        assert "error" in r

    def test_duty_cycle_formula(self):
        r = buck_converter_design(v_in=24, v_out=3.3, i_out=5)
        assert pytest.approx(r["duty_cycle"], abs=0.001) == 3.3 / 24


# ── Boost ────────────────────────────────────────────────────────────────


class TestBoost:
    def test_basic_5v_to_12v(self):
        r = boost_converter_design(v_in=5, v_out=12, i_out=1)
        assert r["topology"] == "Boost"
        assert pytest.approx(r["duty_cycle"], abs=0.01) == 1 - 5 / 12
        assert r["inductance_uH"] > 0

    def test_rejects_step_down(self):
        r = boost_converter_design(v_in=12, v_out=5, i_out=1)
        assert "error" in r


# ── Buck-Boost ───────────────────────────────────────────────────────────


class TestBuckBoost:
    def test_basic(self):
        r = buck_boost_design(v_in=12, v_out=-12, i_out=1)
        assert r["topology"] == "Buck-Boost"
        assert pytest.approx(r["duty_cycle"], abs=0.01) == 0.5

    def test_accepts_positive_magnitude(self):
        r = buck_boost_design(v_in=12, v_out=5, i_out=1)
        assert r["duty_cycle"] > 0


# ── SEPIC ────────────────────────────────────────────────────────────────


class TestSEPIC:
    def test_step_down(self):
        r = sepic_design(v_in=12, v_out=5, i_out=2)
        assert r["topology"] == "SEPIC"
        expected_d = 5 / (12 + 5)
        assert pytest.approx(r["duty_cycle"], abs=0.01) == expected_d
        assert r["L1_inductance_uH"] > 0
        assert r["output_capacitance_uF"] > 0
        assert r["coupling_capacitance_uF"] > 0

    def test_step_up(self):
        r = sepic_design(v_in=5, v_out=12, i_out=1)
        assert r["topology"] == "SEPIC"
        assert r["duty_cycle"] > 0.5


# ── Cuk ──────────────────────────────────────────────────────────────────


class TestCuk:
    def test_basic(self):
        r = cuk_design(v_in=12, v_out=5, i_out=2)
        assert r["topology"] == "Cuk"
        assert r["L1_input_inductance_uH"] > 0
        assert r["L2_output_inductance_uH"] > 0

    def test_duty_cycle(self):
        r = cuk_design(v_in=12, v_out=-5, i_out=2)
        expected_d = 5 / (12 + 5)
        assert pytest.approx(r["duty_cycle"], abs=0.01) == expected_d


# ── Forward ──────────────────────────────────────────────────────────────


class TestForward:
    def test_basic(self):
        r = forward_design(v_in_min=36, v_in_max=72, v_out=5, i_out=10)
        assert r["topology"] == "Forward"
        assert r["turns_ratio_Ns_Np"] > 0
        assert r["output_inductance_uH"] > 0
        assert r["duty_cycle"] <= 0.5

    def test_peak_switch_voltage(self):
        r = forward_design(v_in_min=36, v_in_max=72, v_out=5, i_out=10)
        assert r["peak_switch_voltage_V"] == pytest.approx(144.0)


# ── Flyback ──────────────────────────────────────────────────────────────


class TestFlyback:
    def test_basic(self):
        r = flyback_design(v_in_min=90, v_in_max=265, v_out=12, i_out=2)
        assert r["topology"] == "Flyback"
        assert r["turns_ratio_Ns_Np"] > 0
        assert r["primary_inductance_uH"] > 0

    def test_custom_turns_ratio(self):
        r = flyback_design(v_in_min=9, v_in_max=18, v_out=5, i_out=1, n_ratio=0.5)
        assert r["turns_ratio_Ns_Np"] == 0.5


# ── LLC ──────────────────────────────────────────────────────────────────


class TestLLC:
    def test_basic(self):
        r = llc_design(v_in=400, v_out=12, i_out=20)
        assert r["topology"] == "LLC Resonant"
        assert r["resonant_inductance_Lr_uH"] > 0
        assert r["magnetizing_inductance_Lm_uH"] > r["resonant_inductance_Lr_uH"]
        assert r["resonant_capacitance_Cr_nF"] > 0

    def test_turns_ratio_auto(self):
        r = llc_design(v_in=400, v_out=12, i_out=20)
        expected_n = 2 * 12 / 400
        assert pytest.approx(r["turns_ratio_Ns_Np"], abs=0.001) == expected_n

    def test_rejects_zero_power(self):
        r = llc_design(v_in=400, v_out=0, i_out=20)
        assert "error" in r


# ── Topology Recommendation ──────────────────────────────────────────────


class TestTopologyRecommendation:
    def test_step_down_recommends_buck(self):
        r = topology_recommendation(v_in=12, v_out=5, i_out=2)
        assert r["recommended"] == "Buck"

    def test_step_up_recommends_boost(self):
        r = topology_recommendation(v_in=5, v_out=12, i_out=1)
        assert r["recommended"] == "Boost"

    def test_close_voltages_recommends_sepic(self):
        r = topology_recommendation(v_in=12, v_out=12, i_out=1)
        assert "SEPIC" in r["recommended"]

    def test_isolated_low_power(self):
        r = topology_recommendation(v_in=12, v_out=5, i_out=2, isolated=True)
        assert r["recommended"] == "Flyback"

    def test_isolated_high_power(self):
        r = topology_recommendation(v_in=400, v_out=12, i_out=30, isolated=True)
        assert "LLC" in r["recommended"]


# ── Efficiency Estimate ──────────────────────────────────────────────────


class TestEfficiency:
    def test_basic(self):
        r = efficiency_estimate(v_in=12, v_out=5, i_out=2)
        assert 0 < r["estimated_efficiency_pct"] < 100
        assert r["total_loss_W"] > 0
        assert r["conduction_loss_W"] >= 0
        assert r["switching_loss_W"] >= 0

    def test_loss_breakdown_sums(self):
        r = efficiency_estimate(v_in=12, v_out=5, i_out=2)
        bd = r["breakdown"]
        cond_sum = bd["MOSFET_conduction_W"] + bd["inductor_DCR_W"] + bd["diode_or_SR_conduction_W"]
        sw_sum = bd["turn_on_loss_W"] + bd["turn_off_loss_W"]
        # Totals are rounded once; breakdown terms are rounded individually.
        assert pytest.approx(r["conduction_loss_W"], abs=0.01) == cond_sum
        assert pytest.approx(r["switching_loss_W"], abs=0.01) == sw_sum

    def test_sync_rect_more_efficient(self):
        diode = efficiency_estimate(v_in=12, v_out=5, i_out=2, sync_rect=False)
        sync = efficiency_estimate(v_in=12, v_out=5, i_out=2, sync_rect=True)
        assert sync["estimated_efficiency_pct"] > diode["estimated_efficiency_pct"]

    def test_rejects_zero_power(self):
        r = efficiency_estimate(v_in=12, v_out=0, i_out=2)
        assert "error" in r


# ── execute_tool dispatch ────────────────────────────────────────────────


class TestExecuteTool:
    def test_known_tool(self):
        result = execute_tool("buck_converter_design", v_in=12, v_out=5, i_out=2)
        data = json.loads(result)
        assert data["topology"] == "Buck"

    def test_unknown_tool(self):
        result = execute_tool("nonexistent_tool")
        data = json.loads(result)
        assert "error" in data

    def test_all_tools_registered(self):
        tools = get_available_tools()
        for t in tools:
            result = json.loads(execute_tool(t["name"], v_in=12, v_out=5, i_out=2, f_sw_khz=100,
                                             v_in_min=9, v_in_max=18))
            assert isinstance(result, dict)
