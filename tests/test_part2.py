"""
tests/test_part2.py
===================
Pytest test suite for SmartRoute AI Part 2:
  - Fleet Utilisation Optimizer
  - Cold Chain Temperature Monitor
  - Integration tests (cold-chain -> risk engine, fleet -> route advisor)
  - MCP Server module tests

Run from repo root:
    cd bob-ai-hackathon-PI-NANT
    python -m pytest tests/test_part2.py -v

Or from src/:
    cd bob-ai-hackathon-PI-NANT/src
    python -m pytest ../tests/test_part2.py -v
"""

import os
import sys

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.join(_TESTS_DIR, "..", "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

# ---------------------------------------------------------------------------
# Imports under test
# ---------------------------------------------------------------------------
from core.fleet_optimizer import (
    load_vehicles,
    get_available_vehicles,
    get_idle_vehicles,
    get_fleet_summary,
    get_vehicle_utilisation,
    recommend_vehicle_for_shipment,
)
from core.cold_chain_monitor import (
    load_temperature_data,
    get_shipment_temperature_status,
    get_temperature_alerts,
    get_cold_chain_summary,
    get_temperature_risk,
    WARNING_DELTA_C,
)
from core.risk_engine import calculate_risk_by_id, score_all_shipments
from core.route_advisor import recommend_alternative_routes
import mcp_server as mcp


# ===========================================================================
# 1. Fleet Optimizer
# ===========================================================================

class TestFleetOptimizer:

    # ── Data loading ─────────────────────────────────────────────────────

    def test_load_vehicles_returns_list(self):
        vehicles = load_vehicles()
        assert isinstance(vehicles, list)
        assert len(vehicles) >= 5

    def test_each_vehicle_has_required_keys(self):
        for v in load_vehicles():
            for k in ("id", "name", "type", "carrier", "status",
                      "available_teu", "capacity_teu"):
                assert k in v, "Vehicle %s missing key %s" % (v.get("id"), k)

    # ── Available vehicles ────────────────────────────────────────────────

    def test_available_vehicles_all_have_status_available(self):
        for v in get_available_vehicles():
            assert v["status"] == "available"

    def test_available_vehicles_all_have_positive_teu(self):
        for v in get_available_vehicles():
            assert v["available_teu"] > 0

    def test_unavailable_vehicle_excluded(self):
        # V-005 is marked unavailable (engine failure)
        ids = [v["vehicle_id"] for v in get_available_vehicles()]
        assert "V-005" not in ids

    def test_cargo_type_filter(self):
        pharma = get_available_vehicles(cargo_type="pharmaceuticals")
        assert len(pharma) >= 1
        for v in pharma:
            assert "pharmaceuticals" in v["supported_cargo_types"]

    def test_cargo_type_filter_no_match(self):
        # fictional cargo type should return empty list
        result = get_available_vehicles(cargo_type="magic_cargo_type_xyz")
        assert result == []

    def test_reefer_filter(self):
        reefer = get_available_vehicles(needs_reefer=True)
        assert len(reefer) >= 1
        for v in reefer:
            assert v["available_reefer_slots"] >= 1

    def test_min_teu_filter(self):
        large = get_available_vehicles(min_teu=1000)
        assert len(large) >= 1
        for v in large:
            assert v["available_teu"] >= 1000

    def test_min_weight_filter(self):
        heavy = get_available_vehicles(min_weight_kg=40000)
        assert len(heavy) >= 1
        for v in heavy:
            assert v["available_weight_kg"] >= 40000

    def test_min_teu_too_large_returns_empty(self):
        result = get_available_vehicles(min_teu=9999999)
        assert result == []

    def test_available_vehicles_sorted_by_teu_desc(self):
        vehicles = get_available_vehicles()
        for i in range(len(vehicles) - 1):
            assert vehicles[i]["available_teu"] >= vehicles[i+1]["available_teu"]

    # ── Idle vehicles ─────────────────────────────────────────────────────

    def test_idle_vehicles_returns_list(self):
        idle = get_idle_vehicles()
        assert isinstance(idle, list)

    def test_idle_vehicles_are_available(self):
        for v in get_idle_vehicles():
            assert v["status"] == "available"

    def test_idle_vehicles_not_in_active_shipments(self):
        import json
        path = os.path.join(_SRC_DIR, "data", "shipments.json")
        with open(path) as f:
            shipments = json.load(f)["shipments"]
        active_statuses = {"in_transit", "delayed", "critical_delay", "loading"}
        assigned_ids = {
            s["vessel_id"] for s in shipments
            if s.get("status") in active_statuses and s.get("vessel_id")
        }
        for v in get_idle_vehicles():
            assert v["vehicle_id"] not in assigned_ids, (
                "Vehicle %s is idle but appears in active shipments" % v["vehicle_id"]
            )

    # ── Fleet summary ─────────────────────────────────────────────────────

    def test_fleet_summary_keys(self):
        summary = get_fleet_summary()
        for k in ("total", "available", "unavailable", "assigned",
                  "idle", "utilisation_pct", "reefer_capable_count",
                  "available_total_teu", "available_total_weight_kg"):
            assert k in summary

    def test_fleet_summary_total_equals_available_plus_unavailable(self):
        s = get_fleet_summary()
        assert s["total"] == s["available"] + s["unavailable"]

    def test_fleet_summary_assigned_plus_idle_equals_available(self):
        s = get_fleet_summary()
        assert s["assigned"] + s["idle"] == s["available"]

    def test_fleet_summary_utilisation_range(self):
        s = get_fleet_summary()
        assert 0.0 <= s["utilisation_pct"] <= 100.0

    def test_fleet_summary_unavailable_at_least_one(self):
        # V-005 is unavailable
        s = get_fleet_summary()
        assert s["unavailable"] >= 1

    # ── Vehicle utilisation ───────────────────────────────────────────────

    def test_vehicle_utilisation_returns_all_vehicles(self):
        util = get_vehicle_utilisation()
        assert len(util) == len(load_vehicles())

    def test_vehicle_utilisation_keys(self):
        for v in get_vehicle_utilisation():
            for k in ("vehicle_id", "name", "carrier", "status", "assigned",
                      "capacity_teu", "used_teu", "available_teu",
                      "load_pct", "is_idle"):
                assert k in v

    def test_vehicle_utilisation_load_pct_range(self):
        for v in get_vehicle_utilisation():
            assert 0.0 <= v["load_pct"] <= 100.0

    def test_unavailable_vehicle_is_not_idle(self):
        for v in get_vehicle_utilisation():
            if v["vehicle_id"] == "V-005":
                assert v["is_idle"] is False

    # ── Vehicle recommendation ────────────────────────────────────────────

    def test_recommend_vehicle_for_valid_shipment(self):
        result = recommend_vehicle_for_shipment("SHP-001")
        assert result["shipment_id"] == "SHP-001"
        assert "recommended_vehicle" in result
        assert "reason" in result
        assert "alternatives" in result

    def test_recommend_vehicle_for_cold_chain_shipment(self):
        # SHP-002 requires cold-chain (pharmaceuticals)
        result = recommend_vehicle_for_shipment("SHP-002")
        assert result["shipment_id"] == "SHP-002"
        if result["recommended_vehicle"] is not None:
            # Recommended vehicle must have reefer slots
            assert result["recommended_vehicle"]["available_reefer_slots"] >= 1

    def test_recommend_vehicle_for_nonexistent_shipment(self):
        result = recommend_vehicle_for_shipment("SHP-FAKE")
        assert result["recommended_vehicle"] is None
        assert "not found" in result["reason"].lower()
        assert result["alternatives"] == []

    def test_recommend_vehicle_reason_is_string(self):
        result = recommend_vehicle_for_shipment("SHP-001")
        assert isinstance(result["reason"], str)
        assert len(result["reason"]) > 0

    def test_recommend_vehicle_alternatives_are_list(self):
        result = recommend_vehicle_for_shipment("SHP-001")
        assert isinstance(result["alternatives"], list)


# ===========================================================================
# 2. Cold Chain Monitor
# ===========================================================================

class TestColdChainMonitor:

    # ── Data loading ──────────────────────────────────────────────────────

    def test_load_temperature_data_returns_list(self):
        data = load_temperature_data()
        assert isinstance(data, list)
        assert len(data) >= 2

    # ── Normal temperature detection ──────────────────────────────────────

    def test_normal_shipment_not_detected(self):
        # SHP-003 (automotive parts) has no excursions
        status = get_shipment_temperature_status("SHP-003")
        assert status["excursion_detected"] is False
        assert status["excursion_severity"] == "NORMAL"
        assert status["cold_chain_risk_score"] == 0

    def test_normal_status_keys(self):
        status = get_shipment_temperature_status("SHP-003")
        for k in ("shipment_id", "cargo_type", "latest_temp_c",
                  "excursion_detected", "excursion_severity",
                  "cold_chain_risk_score", "explanation", "readings"):
            assert k in status

    # ── Excursion detection ───────────────────────────────────────────────

    def test_shp002_excursion_detected(self):
        status = get_shipment_temperature_status("SHP-002")
        assert status["excursion_detected"] is True
        assert status["excursion_count"] >= 1

    def test_shp004_excursion_detected(self):
        status = get_shipment_temperature_status("SHP-004")
        assert status["excursion_detected"] is True
        assert status["excursion_count"] >= 1

    def test_excursion_severity_is_valid(self):
        valid = {"NORMAL", "WARNING", "CRITICAL"}
        for entry in load_temperature_data():
            sid = entry.get("shipment_id", "")
            status = get_shipment_temperature_status(sid)
            assert status["excursion_severity"] in valid

    # ── Critical vs Warning classification ───────────────────────────────

    def test_high_deviation_is_critical(self):
        # SHP-004: max deviation 2.7 C >> WARNING_DELTA_C — must be CRITICAL
        status = get_shipment_temperature_status("SHP-004")
        assert status["excursion_severity"] == "CRITICAL"

    def test_critical_has_risk_score_gt_zero(self):
        status = get_shipment_temperature_status("SHP-002")
        assert status["cold_chain_risk_score"] > 0

    # ── Risk score range ──────────────────────────────────────────────────

    def test_risk_score_range(self):
        for entry in load_temperature_data():
            sid = entry.get("shipment_id", "")
            status = get_shipment_temperature_status(sid)
            assert 0 <= status["cold_chain_risk_score"] <= 100

    def test_normal_has_zero_risk_score(self):
        status = get_shipment_temperature_status("SHP-003")
        assert status["cold_chain_risk_score"] == 0

    # ── Temperature alerts ────────────────────────────────────────────────

    def test_get_temperature_alerts_returns_only_excursions(self):
        alerts = get_temperature_alerts()
        assert len(alerts) >= 1
        for a in alerts:
            assert a["excursion_severity"] != "NORMAL"

    def test_temperature_alerts_sorted_by_risk_desc(self):
        alerts = get_temperature_alerts()
        for i in range(len(alerts) - 1):
            assert alerts[i]["cold_chain_risk_score"] >= alerts[i+1]["cold_chain_risk_score"]

    def test_temperature_alerts_keys(self):
        alerts = get_temperature_alerts()
        for a in alerts:
            for k in ("shipment_id", "excursion_severity", "cold_chain_risk_score",
                      "latest_temp_c", "explanation"):
                assert k in a

    def test_temperature_alerts_filtered_by_shipment(self):
        alerts = get_temperature_alerts(shipment_id="SHP-002")
        assert all(a["shipment_id"] == "SHP-002" for a in alerts)

    def test_temperature_alerts_no_excursion_returns_empty(self):
        # SHP-003 has no excursion — filter should return empty
        alerts = get_temperature_alerts(shipment_id="SHP-003")
        assert alerts == []

    # ── Cold-chain summary ────────────────────────────────────────────────

    def test_cold_chain_summary_keys(self):
        summary = get_cold_chain_summary()
        for k in ("total_tracked", "normal_count", "warning_count",
                  "critical_count", "shipments_with_excursions", "average_risk_score"):
            assert k in summary

    def test_cold_chain_summary_counts_consistent(self):
        s = get_cold_chain_summary()
        assert s["normal_count"] + s["warning_count"] + s["critical_count"] == s["total_tracked"]

    def test_cold_chain_summary_has_excursions(self):
        s = get_cold_chain_summary()
        assert s["shipments_with_excursions"] >= 1

    # ── Temperature risk ──────────────────────────────────────────────────

    def test_get_temperature_risk_keys(self):
        risk = get_temperature_risk("SHP-002")
        for k in ("shipment_id", "cold_chain_risk_score",
                  "excursion_severity", "excursion_detected", "explanation"):
            assert k in risk

    def test_get_temperature_risk_nonexistent(self):
        risk = get_temperature_risk("SHP-FAKE")
        assert risk["excursion_detected"] is False
        assert risk["cold_chain_risk_score"] == 0

    # ── Status for unknown shipment ───────────────────────────────────────

    def test_status_for_unknown_shipment_is_safe(self):
        status = get_shipment_temperature_status("SHP-NONEXISTENT")
        assert status["excursion_detected"] is False
        assert status["cold_chain_risk_score"] == 0
        assert "not found" in status["explanation"].lower() or \
               "no temperature data" in status["explanation"].lower()


# ===========================================================================
# 3. Integration Tests
# ===========================================================================

class TestIntegration:

    # ── Cold-chain risk contribution to risk engine ───────────────────────

    def test_cold_chain_contributes_to_risk(self):
        # SHP-002 (pharma) has excursions — cold_chain factor must be > 0
        r = calculate_risk_by_id("SHP-002")
        assert r["factor_breakdown"]["cold_chain"] > 0, (
            "Cold-chain excursion should contribute to risk score"
        )

    def test_cold_chain_contributes_to_shp004(self):
        r = calculate_risk_by_id("SHP-004")
        assert r["factor_breakdown"]["cold_chain"] > 0

    def test_non_cold_chain_has_zero_cold_points(self):
        # SHP-001 (electronics) — no cold-chain required
        r = calculate_risk_by_id("SHP-001")
        assert r["factor_breakdown"]["cold_chain"] == 0

    def test_risk_score_still_0_to_100(self):
        for s in score_all_shipments():
            assert 0 <= s["score"] <= 100

    def test_risk_score_factor_sum_equals_score(self):
        for s in score_all_shipments():
            total = sum(s["factor_breakdown"].values())
            assert s["score"] == min(total, 100)

    # ── Route + vehicle integration ───────────────────────────────────────

    def test_route_recommendation_includes_vehicle_info(self):
        rec = recommend_alternative_routes("SHP-001")
        assert rec["action_required"] is True
        for alt in rec["alternatives"]:
            assert "available_vehicles" in alt
            assert "vehicle_available" in alt

    def test_recommend_vehicle_for_disrupted_shipment(self):
        result = recommend_vehicle_for_shipment("SHP-006")
        assert result["shipment_id"] == "SHP-006"
        # Should either find a vehicle or give a clear reason
        assert result["reason"]

    def test_affected_shipments_all_have_risk_scores(self):
        from core.disruption_detector import get_affected_shipments
        affected = get_affected_shipments()
        for s in affected:
            risk = calculate_risk_by_id(s["shipment_id"])
            assert risk is not None
            assert risk["score"] > 0

    def test_route_and_vehicle_for_cold_chain(self):
        # SHP-004 (fresh produce, cold-chain)
        route_rec = recommend_alternative_routes("SHP-004")
        vehicle_rec = recommend_vehicle_for_shipment("SHP-004")
        assert route_rec["action_required"] is True
        # Vehicle recommendation should respect reefer requirement
        if vehicle_rec["recommended_vehicle"] is not None:
            assert vehicle_rec["recommended_vehicle"]["available_reefer_slots"] >= 1


# ===========================================================================
# 4. MCP Server
# ===========================================================================

class TestMCPServer:

    # ── Module imports ────────────────────────────────────────────────────

    def test_mcp_module_importable(self):
        import mcp_server
        assert mcp_server is not None

    def test_tools_dict_exists(self):
        assert hasattr(mcp, "TOOLS")
        assert isinstance(mcp.TOOLS, dict)

    def test_all_required_tools_registered(self):
        required = {
            "get_shipment_risk",
            "get_shipment_disruptions",
            "recommend_route",
            "recommend_vehicle",
            "get_fleet_status",
            "get_temperature_alerts",
            "explain_shipment",
        }
        assert required.issubset(set(mcp.TOOLS.keys()))

    def test_each_tool_has_fn_key(self):
        for name, tool in mcp.TOOLS.items():
            assert "fn" in tool, "Tool %s missing 'fn'" % name
            assert callable(tool["fn"]), "Tool %s 'fn' is not callable" % name

    def test_call_tool_function_exists(self):
        assert hasattr(mcp, "call_tool")
        assert callable(mcp.call_tool)

    # ── Valid calls ───────────────────────────────────────────────────────

    def test_get_shipment_risk_valid(self):
        result = mcp.call_tool("get_shipment_risk", {"shipment_id": "SHP-001"})
        assert "error" not in result or result.get("score") is not None
        assert "shipment_id" in result
        assert result["score"] is not None
        assert result["classification"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")

    def test_get_shipment_disruptions_valid(self):
        result = mcp.call_tool("get_shipment_disruptions", {"shipment_id": "SHP-001"})
        assert "disruptions" in result
        assert "disruption_count" in result
        assert isinstance(result["disruptions"], list)

    def test_recommend_route_valid(self):
        result = mcp.call_tool("recommend_route", {"shipment_id": "SHP-001"})
        assert "action_required" in result
        assert "recommendation" in result
        assert "alternatives" in result

    def test_recommend_vehicle_valid(self):
        result = mcp.call_tool("recommend_vehicle", {"shipment_id": "SHP-001"})
        assert "recommended_vehicle" in result
        assert "reason" in result

    def test_get_fleet_status_no_input(self):
        result = mcp.call_tool("get_fleet_status", {})
        assert "total" in result
        assert "available" in result
        assert "utilisation_pct" in result

    def test_get_temperature_alerts_no_filter(self):
        result = mcp.call_tool("get_temperature_alerts", {})
        assert "alerts" in result
        assert "alert_count" in result
        assert isinstance(result["alerts"], list)

    def test_get_temperature_alerts_with_filter(self):
        result = mcp.call_tool("get_temperature_alerts", {"shipment_id": "SHP-002"})
        assert "alerts" in result

    def test_explain_shipment_valid(self):
        result = mcp.call_tool("explain_shipment", {"shipment_id": "SHP-001"})
        assert "explanation" in result
        assert "source" in result
        assert result["source"] in ("mock", "watsonx")
        assert len(result["explanation"]) > 10

    # ── Invalid / edge cases ──────────────────────────────────────────────

    def test_invalid_tool_name_returns_error(self):
        result = mcp.call_tool("nonexistent_tool", {})
        assert "error" in result

    def test_valid_tool_invalid_shipment_id(self):
        result = mcp.call_tool("get_shipment_risk", {"shipment_id": "SHP-FAKE"})
        # Should return structured error, not crash
        assert "error" in result or result.get("score") is None

    def test_recommend_route_unknown_shipment(self):
        result = mcp.call_tool("recommend_route", {"shipment_id": "SHP-FAKE"})
        assert "recommendation" in result
        assert result["action_required"] is False

    def test_recommend_vehicle_unknown_shipment(self):
        result = mcp.call_tool("recommend_vehicle", {"shipment_id": "SHP-FAKE"})
        assert result["recommended_vehicle"] is None

    def test_explain_shipment_unknown_id(self):
        result = mcp.call_tool("explain_shipment", {"shipment_id": "SHP-FAKE"})
        # Should still return explanation text (from mock), not crash
        assert "explanation" in result

    def test_tools_call_real_functions_not_mocks(self):
        """Verify tools call real project functions by checking result structure."""
        # get_shipment_risk must return a real score, not a static value
        r1 = mcp.call_tool("get_shipment_risk", {"shipment_id": "SHP-006"})
        r2 = mcp.call_tool("get_shipment_risk", {"shipment_id": "SHP-005"})
        # SHP-006 has 16-day delay; SHP-005 is clean — scores must differ
        assert r1["score"] != r2["score"], (
            "Tool is returning same score for different shipments — likely hardcoded"
        )
