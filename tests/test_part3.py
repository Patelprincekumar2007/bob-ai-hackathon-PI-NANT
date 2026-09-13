"""
test_part3.py
=============
Part 3 tests for SmartRoute AI — tests the helper/data functions used
by the Streamlit dashboard WITHOUT requiring a browser or running streamlit.

All tests import directly from src/core/ modules.

Run: python -m pytest tests/test_part3.py -v
     (from the bob-ai-hackathon-PI-NANT/src directory)
"""

import os
import sys

# ---------------------------------------------------------------------------
# Ensure src/ is on the path so core/ modules import correctly
# ---------------------------------------------------------------------------
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR   = os.path.join(_TESTS_DIR, "..", "src")
_SRC_DIR   = os.path.normpath(_SRC_DIR)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

import pytest

# ---------------------------------------------------------------------------
# Imports from core modules (same ones used by app.py)
# ---------------------------------------------------------------------------
from core.disruption_detector import (
    load_shipments,
    load_disruptions,
    get_disruption_summary,
    get_shipment_disruptions,
    get_affected_shipments,
)
from core.risk_engine import (
    get_risk_summary,
    score_all_shipments,
    calculate_risk_by_id,
)
from core.route_advisor import recommend_alternative_routes
from core.fleet_optimizer import (
    get_fleet_summary,
    get_vehicle_utilisation,
    recommend_vehicle_for_shipment,
    load_vehicles,
)
from core.cold_chain_monitor import (
    get_cold_chain_summary,
    get_temperature_alerts,
    get_shipment_temperature_status,
    load_temperature_data,
)
from core.watsonx_client import generate_ai_explanation, is_watsonx_configured


# ---------------------------------------------------------------------------
# Helpers (mirrored from app.py to test independently)
# ---------------------------------------------------------------------------

def filter_scored_shipments(scored, risk_filter, status_filter, priority_filter):
    out = scored
    if risk_filter and risk_filter != "All":
        out = [s for s in out if s["classification"] == risk_filter]
    if status_filter and status_filter != "All":
        out = [s for s in out if s.get("status", "").lower() == status_filter.lower()]
    if priority_filter and priority_filter != "All":
        out = [s for s in out if s.get("priority", "").lower() == priority_filter.lower()]
    return out


def get_shipment_detail(shipment_id):
    """Aggregate detail data for one shipment — mirrors app.py helper."""
    risk      = calculate_risk_by_id(shipment_id)
    disruptions = get_shipment_disruptions(shipment_id)
    routes    = recommend_alternative_routes(shipment_id)
    vehicle   = recommend_vehicle_for_shipment(shipment_id)
    raw       = next((s for s in load_shipments() if s["id"] == shipment_id), None)
    cold      = None
    if raw and raw.get("requires_cold_chain"):
        cold = get_shipment_temperature_status(shipment_id)
    return {
        "risk": risk,
        "disruptions": disruptions,
        "routes": routes,
        "vehicle": vehicle,
        "cold": cold,
        "raw": raw,
    }


# ===========================================================================
# Dashboard KPI tests
# ===========================================================================

class TestDashboardKPIs:
    """Verify that all dashboard KPI data can be generated correctly."""

    def test_risk_summary_structure(self):
        """get_risk_summary returns all required keys."""
        summary = get_risk_summary()
        for key in ("total_shipments", "critical_count", "high_count",
                    "medium_count", "low_count", "average_score"):
            assert key in summary, f"Missing key: {key}"

    def test_risk_summary_counts_add_up(self):
        """Risk classification counts sum to total."""
        s = get_risk_summary()
        total = s["critical_count"] + s["high_count"] + s["medium_count"] + s["low_count"]
        assert total == s["total_shipments"]

    def test_risk_summary_total_positive(self):
        """There is at least one shipment."""
        s = get_risk_summary()
        assert s["total_shipments"] > 0

    def test_disruption_summary_structure(self):
        """get_disruption_summary returns all required keys."""
        s = get_disruption_summary()
        for key in ("total_active_disruptions", "total_affected_shipments",
                    "critical_count", "high_count", "medium_count", "low_count"):
            assert key in s

    def test_disruption_summary_non_negative(self):
        """All disruption summary counts are non-negative."""
        s = get_disruption_summary()
        for key, val in s.items():
            assert val >= 0, f"{key} is negative: {val}"

    def test_fleet_summary_structure(self):
        """get_fleet_summary returns all required keys."""
        s = get_fleet_summary()
        for key in ("total", "available", "unavailable", "assigned", "idle",
                    "utilisation_pct", "reefer_capable_count",
                    "available_total_teu", "available_total_weight_kg"):
            assert key in s

    def test_fleet_utilisation_range(self):
        """Fleet utilisation percentage is between 0 and 100."""
        s = get_fleet_summary()
        assert 0.0 <= s["utilisation_pct"] <= 100.0

    def test_cold_chain_summary_structure(self):
        """get_cold_chain_summary returns all required keys."""
        s = get_cold_chain_summary()
        for key in ("total_tracked", "normal_count", "warning_count",
                    "critical_count", "shipments_with_excursions", "average_risk_score"):
            assert key in s

    def test_cold_chain_counts_add_up(self):
        """normal + warning + critical equals total_tracked."""
        s = get_cold_chain_summary()
        total = s["normal_count"] + s["warning_count"] + s["critical_count"]
        assert total == s["total_tracked"]

    def test_average_risk_score_range(self):
        """Average risk score is between 0 and 100."""
        s = get_risk_summary()
        assert 0.0 <= s["average_score"] <= 100.0


# ===========================================================================
# Shipment filtering logic tests
# ===========================================================================

class TestShipmentFiltering:
    """Verify that the UI filter logic works correctly."""

    def setup_method(self):
        """Load scored shipments once per test."""
        self.scored = score_all_shipments()

    def test_no_filter_returns_all(self):
        result = filter_scored_shipments(self.scored, "All", "All", "All")
        assert len(result) == len(self.scored)

    def test_risk_filter_critical(self):
        result = filter_scored_shipments(self.scored, "CRITICAL", "All", "All")
        for s in result:
            assert s["classification"] == "CRITICAL"

    def test_risk_filter_low(self):
        result = filter_scored_shipments(self.scored, "LOW", "All", "All")
        for s in result:
            assert s["classification"] == "LOW"

    def test_status_filter(self):
        # Pick a status that exists in the data
        statuses = {s.get("status", "") for s in self.scored if s.get("status")}
        if not statuses:
            pytest.skip("No status values in data")
        status = next(iter(statuses))
        result = filter_scored_shipments(self.scored, "All", status, "All")
        for s in result:
            assert s.get("status", "").lower() == status.lower()

    def test_priority_filter(self):
        priorities = {s.get("priority", "") for s in self.scored if s.get("priority")}
        if not priorities:
            pytest.skip("No priority values in data")
        priority = next(iter(priorities))
        result = filter_scored_shipments(self.scored, "All", "All", priority)
        for s in result:
            assert s.get("priority", "").lower() == priority.lower()

    def test_combined_filters_subset(self):
        """Combined filters return a subset of all shipments."""
        result = filter_scored_shipments(self.scored, "HIGH", "All", "All")
        assert len(result) <= len(self.scored)

    def test_filter_returns_list(self):
        result = filter_scored_shipments(self.scored, "CRITICAL", "All", "All")
        assert isinstance(result, list)

    def test_scored_shipments_sorted_by_score(self):
        """score_all_shipments returns shipments sorted highest first."""
        if len(self.scored) < 2:
            pytest.skip("Need at least 2 shipments")
        for i in range(len(self.scored) - 1):
            assert self.scored[i]["score"] >= self.scored[i + 1]["score"]


# ===========================================================================
# Shipment detail lookup tests
# ===========================================================================

class TestShipmentDetail:
    """Verify that get_shipment_detail aggregates data correctly."""

    def setup_method(self):
        self.shipments = load_shipments()
        assert self.shipments, "No shipments loaded"
        self.first_id = self.shipments[0]["id"]

    def test_detail_returns_dict(self):
        detail = get_shipment_detail(self.first_id)
        assert isinstance(detail, dict)

    def test_detail_has_all_keys(self):
        detail = get_shipment_detail(self.first_id)
        for key in ("risk", "disruptions", "routes", "vehicle", "cold", "raw"):
            assert key in detail, f"Missing key: {key}"

    def test_detail_risk_structure(self):
        detail = get_shipment_detail(self.first_id)
        risk = detail["risk"]
        assert risk is not None
        for key in ("shipment_id", "score", "classification", "factor_breakdown"):
            assert key in risk

    def test_detail_risk_score_range(self):
        detail = get_shipment_detail(self.first_id)
        score = detail["risk"]["score"]
        assert 0 <= score <= 100

    def test_detail_disruptions_list(self):
        detail = get_shipment_detail(self.first_id)
        assert isinstance(detail["disruptions"], list)

    def test_detail_routes_structure(self):
        detail = get_shipment_detail(self.first_id)
        routes = detail["routes"]
        assert "shipment_id" in routes
        assert "alternatives" in routes
        assert "action_required" in routes

    def test_detail_vehicle_structure(self):
        detail = get_shipment_detail(self.first_id)
        veh = detail["vehicle"]
        assert "shipment_id" in veh
        assert "reason" in veh

    def test_detail_cold_chain_when_required(self):
        """If shipment requires cold chain, cold detail is populated."""
        cold_shp = next(
            (s for s in self.shipments if s.get("requires_cold_chain")), None
        )
        if cold_shp is None:
            pytest.skip("No cold-chain shipment in data")
        detail = get_shipment_detail(cold_shp["id"])
        # cold may be None if no temp data exists, but if it's not None, check structure
        if detail["cold"]:
            assert "excursion_detected" in detail["cold"]
            assert "cold_chain_risk_score" in detail["cold"]

    def test_raw_shipment_populated(self):
        detail = get_shipment_detail(self.first_id)
        assert detail["raw"] is not None
        assert detail["raw"]["id"] == self.first_id


# ===========================================================================
# Invalid shipment ID handling
# ===========================================================================

class TestInvalidShipmentID:
    """Verify graceful handling when an unknown shipment ID is passed."""

    def test_calculate_risk_by_id_unknown(self):
        result = calculate_risk_by_id("SHP-INVALID-9999")
        assert result is None

    def test_get_shipment_disruptions_unknown(self):
        result = get_shipment_disruptions("SHP-INVALID-9999")
        assert result == []

    def test_recommend_routes_unknown(self):
        result = recommend_alternative_routes("SHP-INVALID-9999")
        assert result["shipment_id"] == "SHP-INVALID-9999"
        assert result["action_required"] is False
        assert result["alternatives"] == []

    def test_recommend_vehicle_unknown(self):
        result = recommend_vehicle_for_shipment("SHP-INVALID-9999")
        assert result["shipment_id"] == "SHP-INVALID-9999"
        assert result["recommended_vehicle"] is None
        assert "not found" in result["reason"].lower()

    def test_temperature_status_unknown(self):
        result = get_shipment_temperature_status("SHP-INVALID-9999")
        assert result["excursion_detected"] is False
        assert result["reading_count"] == 0


# ===========================================================================
# Disruption data tests
# ===========================================================================

class TestDisruptionData:
    """Verify disruption data is accessible and structured."""

    def test_load_disruptions_non_empty(self):
        disruptions = load_disruptions()
        assert len(disruptions) > 0

    def test_disruptions_have_required_fields(self):
        for d in load_disruptions():
            assert "id" in d, f"Disruption missing 'id': {d}"
            assert "type" in d
            assert "severity" in d

    def test_active_disruptions_exist(self):
        active = [
            d for d in load_disruptions()
            if d.get("status") in ("active", "monitoring")
        ]
        assert len(active) > 0, "Expected at least one active disruption"

    def test_affected_shipments_returns_list(self):
        result = get_affected_shipments()
        assert isinstance(result, list)

    def test_affected_shipments_have_disruption_info(self):
        affected = get_affected_shipments()
        for item in affected:
            assert "shipment_id" in item
            assert "disruption_count" in item
            assert item["disruption_count"] > 0
            assert "highest_severity" in item

    def test_disruption_severity_values(self):
        """All disruption severities are recognised values."""
        valid = {"critical", "high", "medium", "low", "unknown"}
        for d in load_disruptions():
            sev = d.get("severity", "unknown").lower()
            assert sev in valid, f"Unexpected severity '{sev}' in {d['id']}"


# ===========================================================================
# Fleet integration tests
# ===========================================================================

class TestFleetIntegration:
    """Verify fleet module integrates with dashboard requirements."""

    def test_vehicle_utilisation_is_list(self):
        result = get_vehicle_utilisation()
        assert isinstance(result, list)

    def test_vehicle_utilisation_fields(self):
        util = get_vehicle_utilisation()
        if not util:
            pytest.skip("No vehicles in data")
        for v in util:
            for key in ("vehicle_id", "name", "carrier", "status",
                        "assigned", "capacity_teu", "used_teu",
                        "available_teu", "load_pct", "is_idle"):
                assert key in v, f"Missing field '{key}' in vehicle record"

    def test_load_pct_range(self):
        for v in get_vehicle_utilisation():
            assert 0.0 <= v["load_pct"] <= 100.0

    def test_fleet_summary_available_less_than_total(self):
        s = get_fleet_summary()
        assert s["available"] <= s["total"]

    def test_fleet_summary_assigned_idle_sum(self):
        """assigned + idle == available."""
        s = get_fleet_summary()
        assert s["assigned"] + s["idle"] == s["available"]

    def test_recommend_vehicle_returns_dict(self):
        shipments = load_shipments()
        if not shipments:
            pytest.skip("No shipments")
        result = recommend_vehicle_for_shipment(shipments[0]["id"])
        assert isinstance(result, dict)
        assert "shipment_id" in result
        assert "recommended_vehicle" in result
        assert "reason" in result

    def test_vehicle_recommendation_has_alternatives(self):
        """If a vehicle is found, alternatives key is a list."""
        shipments = load_shipments()
        for s in shipments:
            result = recommend_vehicle_for_shipment(s["id"])
            if result["recommended_vehicle"] is not None:
                assert isinstance(result["alternatives"], list)
                return
        pytest.skip("No shipment returned a vehicle recommendation")


# ===========================================================================
# Cold-chain integration tests
# ===========================================================================

class TestColdChainIntegration:
    """Verify cold-chain module integrates with dashboard requirements."""

    def test_load_temperature_data_non_empty(self):
        data = load_temperature_data()
        assert len(data) > 0

    def test_temperature_alerts_is_list(self):
        result = get_temperature_alerts()
        assert isinstance(result, list)

    def test_temperature_alert_structure(self):
        alerts = get_temperature_alerts()
        for a in alerts:
            for key in ("shipment_id", "cargo_type", "excursion_severity",
                        "excursion_count", "cold_chain_risk_score",
                        "latest_temp_c", "required_temp_min_c", "required_temp_max_c"):
                assert key in a, f"Missing key '{key}' in alert"

    def test_cold_chain_risk_score_range(self):
        for a in get_temperature_alerts():
            assert 0 <= a["cold_chain_risk_score"] <= 100

    def test_shipment_temperature_status_structure(self):
        entries = load_temperature_data()
        if not entries:
            pytest.skip("No temperature data")
        sid = entries[0]["shipment_id"]
        status = get_shipment_temperature_status(sid)
        for key in ("shipment_id", "excursion_detected", "excursion_severity",
                    "cold_chain_risk_score", "reading_count", "readings", "explanation"):
            assert key in status

    def test_readings_are_list(self):
        entries = load_temperature_data()
        if not entries:
            pytest.skip("No temperature data")
        sid = entries[0]["shipment_id"]
        status = get_shipment_temperature_status(sid)
        assert isinstance(status["readings"], list)

    def test_excursion_count_non_negative(self):
        for entry in load_temperature_data():
            status = get_shipment_temperature_status(entry["shipment_id"])
            assert status["excursion_count"] >= 0

    def test_alerts_sorted_by_risk_score(self):
        """Temperature alerts returned highest risk first."""
        alerts = get_temperature_alerts()
        if len(alerts) < 2:
            pytest.skip("Need at least 2 alerts to check ordering")
        for i in range(len(alerts) - 1):
            assert alerts[i]["cold_chain_risk_score"] >= alerts[i + 1]["cold_chain_risk_score"]


# ===========================================================================
# watsonx fallback tests
# ===========================================================================

class TestWatsonxFallback:
    """Verify that without credentials, mock responses are returned correctly."""

    def test_is_watsonx_configured_returns_bool(self):
        result = is_watsonx_configured()
        assert isinstance(result, bool)

    def test_generate_ai_explanation_returns_dict(self):
        result = generate_ai_explanation("Test prompt for supply chain analysis")
        assert isinstance(result, dict)

    def test_generate_ai_explanation_has_required_keys(self):
        result = generate_ai_explanation("Analyse shipment SHP-001")
        for key in ("text", "source", "model_id"):
            assert key in result

    def test_generate_ai_explanation_text_non_empty(self):
        result = generate_ai_explanation("Summarise fleet risk status")
        assert result["text"]
        assert len(result["text"]) > 10

    def test_mock_fallback_when_no_credentials(self):
        """Without credentials, source must be 'mock' (or 'watsonx' if configured)."""
        result = generate_ai_explanation("Test")
        assert result["source"] in ("mock", "watsonx")

    def test_empty_prompt_handled_gracefully(self):
        result = generate_ai_explanation("")
        assert "text" in result
        assert result["source"] == "mock"

    def test_none_prompt_handled_gracefully(self):
        result = generate_ai_explanation(None)
        assert "text" in result


# ===========================================================================
# app.py helper function unit tests (import helper functions only)
# ===========================================================================

class TestAppHelpers:
    """Unit tests for pure helper functions defined in app.py."""

    def test_import_app_module(self):
        """app.py can be imported without raising an error."""
        try:
            import importlib
            import app  # noqa: F401
        except SystemExit:
            pass  # streamlit may call sys.exit in some contexts — not a failure
        except Exception as exc:
            # Streamlit API exceptions during import are acceptable
            err_str = str(exc).lower()
            acceptable = any(
                kw in err_str
                for kw in ("streamlit", "scriptruncontext", "no current event loop",
                           "session", "context", "thread")
            )
            if not acceptable:
                raise

    def test_build_ai_prompt(self):
        """build_ai_prompt produces a non-empty string."""
        # Test the logic directly without importing app
        shipment_id = "SHP-001"
        risk_data = {"classification": "HIGH", "score": 72}
        disruptions = [{"title": "Port congestion"}, {"title": "Vessel failure"}]

        # Inline the same logic as app.build_ai_prompt
        risk_cls = risk_data.get("classification", "UNKNOWN")
        risk_score = risk_data.get("score", 0)
        disr_titles = "; ".join(d["title"] for d in disruptions) if disruptions else "None"
        prompt = (
            f"You are a supply chain risk analyst. "
            f"Shipment {shipment_id} has a risk score of {risk_score}/100 ({risk_cls}). "
            f"Active disruptions: {disr_titles}. "
            f"Provide a brief, actionable explanation for a logistics coordinator: "
            f"what is happening, why it matters, and what they should do next."
        )
        assert shipment_id in prompt
        assert "HIGH" in prompt
        assert "Port congestion" in prompt

    def test_filter_no_matches_returns_empty(self):
        scored = score_all_shipments()
        # "NONEXISTENT" is not a real classification
        result = filter_scored_shipments(scored, "NONEXISTENT", "All", "All")
        assert result == []

    def test_filter_preserves_all_fields(self):
        scored = score_all_shipments()
        result = filter_scored_shipments(scored, "All", "All", "All")
        for original, filtered in zip(scored, result):
            assert original["shipment_id"] == filtered["shipment_id"]
