"""
Tests for pea.tools.calculator — every topology calculator, efficiency estimator,
DAB, cascade, magnetics design, and component library.
"""

import json
import math

import pytest

from pea.tools.calculator import (
    boost_converter_design,
    buck_boost_design,
    buck_converter_design,
    cascade_design,
    cuk_design,
    dab_design,
    efficiency_estimate,
    execute_tool,
    flyback_design,
    forward_design,
    get_available_tools,
    inductor_design,
    llc_design,
    sepic_design,
    topology_recommendation,
    transformer_design,
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

    def test_bidirectional_isolated_recommends_dab(self):
        r = topology_recommendation(v_in=400, v_out=48, i_out=20, isolated=True, bidirectional=True)
        assert r["recommended"] == "DAB"

    def test_extreme_step_down_recommends_cascade(self):
        r = topology_recommendation(v_in=400, v_out=3.3, i_out=5)
        assert "cascade" in r["recommended"].lower() or "Buck" in r["recommended"]

    def test_extreme_step_up_recommends_cascade(self):
        r = topology_recommendation(v_in=3.3, v_out=400, i_out=0.1)
        assert "cascade" in r["recommended"].lower() or "Boost" in r["recommended"]

    def test_high_power_isolated_includes_dab(self):
        r = topology_recommendation(v_in=400, v_out=48, i_out=30, isolated=True)
        all_options = [r["recommended"]] + r.get("alternatives", [])
        assert any("DAB" in opt for opt in all_options)


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


# ── DAB ──────────────────────────────────────────────────────────────────


class TestDAB:
    def test_basic(self):
        r = dab_design(v1=400, v2=48, p_rated=1000)
        assert r["topology"] == "DAB"
        assert r["leakage_inductance_uH"] > 0
        assert r["I_L_peak_A"] > 0
        assert r["I_L_rms_A"] > 0

    def test_turns_ratio(self):
        r = dab_design(v1=400, v2=48, p_rated=1000)
        assert pytest.approx(r["turns_ratio_n"], abs=0.001) == 48 / 400

    def test_zvs_achievable(self):
        r = dab_design(v1=400, v2=48, p_rated=1000, phi_deg=30)
        assert r["ZVS_status"] == "Achievable"

    def test_rejects_zero_power(self):
        r = dab_design(v1=400, v2=48, p_rated=0)
        assert "error" in r

    def test_rejects_invalid_phase(self):
        r = dab_design(v1=400, v2=48, p_rated=1000, phi_deg=0)
        assert "error" in r

    def test_secondary_currents(self):
        r = dab_design(v1=400, v2=48, p_rated=1000)
        n = r["turns_ratio_n"]
        assert pytest.approx(r["I_sec_peak_A"], abs=0.1) == r["I_L_peak_A"] / n
        assert pytest.approx(r["I_sec_rms_A"], abs=0.1) == r["I_L_rms_A"] / n


# ── Cascade ──────────────────────────────────────────────────────────────


class TestCascade:
    def test_auto_select_high_power_isolated(self):
        r = cascade_design(v_in=230, v_out=12, i_out=20)
        assert r["topology"] == "Cascade"
        assert "stage_1" in r or "stages" in r

    def test_auto_select_extreme_stepdown(self):
        r = cascade_design(v_in=400, v_out=3.3, i_out=5)
        assert r["topology"] == "Cascade"

    def test_rejects_zero_power(self):
        r = cascade_design(v_in=12, v_out=0, i_out=2)
        assert "error" in r

    def test_moderate_ratio_no_cascade(self):
        r = cascade_design(v_in=12, v_out=5, i_out=2)
        assert r["topology"] == "Cascade"
        assert "sufficient" in r.get("pattern", "").lower() or "stage" in r


# ── Inductor Design ─────────────────────────────────────────────────────


class TestInductorDesign:
    def test_basic(self):
        r = inductor_design(inductance_uH=100, i_peak=5, i_rms=3)
        assert r["design"] == "Inductor"
        assert r["turns"] > 0
        assert r["core"] != ""
        assert r["wire_AWG"] > 0
        assert r["B_peak_mT"] > 0

    def test_core_loss_positive(self):
        r = inductor_design(inductance_uH=100, i_peak=5, i_rms=3)
        assert r["core_loss_mW"] >= 0
        assert r["copper_loss_mW"] >= 0
        assert r["total_loss_mW"] > 0

    def test_different_core_shape(self):
        r = inductor_design(inductance_uH=100, i_peak=5, i_rms=3, core_shape="ETD")
        assert r["core_shape"] == "ETD"

    def test_different_material(self):
        r = inductor_design(inductance_uH=100, i_peak=5, i_rms=3, material="3C90")
        assert r["material"] == "3C90"

    def test_unknown_material_error(self):
        r = inductor_design(inductance_uH=100, i_peak=5, i_rms=3, material="FAKE")
        assert "error" in r

    def test_unknown_core_error(self):
        r = inductor_design(inductance_uH=100, i_peak=5, i_rms=3, core_shape="FAKE")
        assert "error" in r


# ── Transformer Design ──────────────────────────────────────────────────


class TestTransformerDesign:
    def test_basic(self):
        r = transformer_design(v_pri=400, v_sec=12, power_W=500)
        assert r["design"] == "Transformer"
        assert r["N_primary"] > 0
        assert r["N_secondary"] > 0
        assert r["turns_ratio_actual"] > 0

    def test_rejects_zero_power(self):
        r = transformer_design(v_pri=400, v_sec=12, power_W=0)
        assert "error" in r

    def test_loss_breakdown(self):
        r = transformer_design(v_pri=400, v_sec=12, power_W=500)
        assert r["core_loss_mW"] >= 0
        assert r["copper_loss_mW"] >= 0

    def test_different_shape_and_material(self):
        r = transformer_design(v_pri=400, v_sec=12, power_W=500, core_shape="PQ", material="N97")
        assert r["core_shape"] == "PQ"
        assert r["material"] == "N97"


# ── Magnetics Data ───────────────────────────────────────────────────────


class TestMagneticsData:
    def test_core_shapes_available(self):
        from pea.tools.magnetics_data import get_available_core_shapes
        shapes = get_available_core_shapes()
        assert "EE" in shapes
        assert "PQ" in shapes
        assert "ETD" in shapes

    def test_materials_available(self):
        from pea.tools.magnetics_data import get_available_materials
        mats = get_available_materials()
        assert "N87" in mats
        assert "3C90" in mats

    def test_material_info(self):
        from pea.tools.magnetics_data import get_material_info
        info = get_material_info("N87")
        assert info is not None
        assert info["bsat"] > 0
        assert "steinmetz" in info

    def test_core_sizes(self):
        from pea.tools.magnetics_data import get_core_sizes
        sizes = get_core_sizes("EE")
        assert sizes is not None
        assert len(sizes) > 0
        assert "Ae" in sizes[0]


# ── Component Library ────────────────────────────────────────────────────


class TestComponentLibrary:
    def test_search_mosfets(self):
        from pea.components.schema import search_mosfets
        results = search_mosfets(vds_min_V=60, id_min_A=10)
        assert len(results) > 0
        for m in results:
            assert m["vds_max_V"] >= 60
            assert m["id_max_A"] >= 10

    def test_search_mosfets_by_technology(self):
        from pea.components.schema import search_mosfets
        gan = search_mosfets(technology="GaN")
        assert len(gan) > 0
        assert all(m["technology"] == "GaN" for m in gan)

    def test_search_diodes(self):
        from pea.components.schema import search_diodes
        results = search_diodes(vr_min_V=100, if_min_A=5)
        assert len(results) > 0

    def test_search_capacitors(self):
        from pea.components.schema import search_capacitors
        results = search_capacitors(voltage_min_V=25)
        assert len(results) > 0

    def test_recommend_components(self):
        from pea.components.schema import recommend_components
        r = recommend_components(v_in=12, v_out=5, i_out=2)
        assert "recommended_mosfets" in r
        assert "recommended_diodes" in r
        assert "recommended_output_caps" in r


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

    def test_dab_via_dispatch(self):
        result = execute_tool("dab_design", v1=400, v2=48, p_rated=1000)
        data = json.loads(result)
        assert data["topology"] == "DAB"

    def test_inductor_via_dispatch(self):
        result = execute_tool("inductor_design", inductance_uH=100, i_peak=5, i_rms=3)
        data = json.loads(result)
        assert data["design"] == "Inductor"

    def test_transformer_via_dispatch(self):
        result = execute_tool("transformer_design", v_pri=400, v_sec=12, power_W=500)
        data = json.loads(result)
        assert data["design"] == "Transformer"

    def test_cascade_via_dispatch(self):
        result = execute_tool("cascade_design", v_in=230, v_out=12, i_out=20)
        data = json.loads(result)
        assert data["topology"] == "Cascade"

    def test_all_tools_registered(self):
        tools = get_available_tools()
        for t in tools:
            # Provide a superset of possible kwargs
            result = json.loads(execute_tool(
                t["name"], v_in=12, v_out=5, i_out=2, f_sw_khz=100,
                v_in_min=9, v_in_max=18,
                v1=400, v2=48, p_rated=1000,
                inductance_uH=100, i_peak=5, i_rms=3,
                v_pri=400, v_sec=12, power_W=500,
            ))
            assert isinstance(result, dict)
