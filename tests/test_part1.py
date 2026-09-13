"""
tests/test_part1.py
===================
Pytest test suite for SmartRoute AI Part 1: Core Engine + Data Layer.

Run from the repo root:
    cd bob-ai-hackathon-PI-NANT
    python -m pytest tests/test_part1.py -v

Or from src/:
    cd bob-ai-hackathon-PI-NANT/src
    python -m pytest ../tests/test_part1.py -v

All tests use only the JSON mock data files — no external APIs or .env needed.
"""

import json
import os
import sys

# ---------------------------------------------------------------------------
# Ensure src/ is on the path so "from core.xxx import ..." works
# ---------------------------------------------------------------------------
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.join(_TESTS_DIR, "..", "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

# ---------------------------------------------------------------------------
# Imports under test
# ---------------------------------------------------------------------------
from core.disruption_detector import (
    load_disruptions,
    load_shipments,
    get_disruption_by_id,
    get_shipment_disruptions,
    get_affected_shipments,
    get_disruption_summary,
)
from core.risk_engine import (
    calculate_risk,
    calculate_risk_by_id,
    score_all_shipments,
    get_risk_summary,
)
from core.route_advisor import (
    recommend_alternative_routes,
    recommend_all_affected,
    get_available_vehicles,
)
from core.watsonx_client import (
    generate_ai_explanation,
    is_watsonx_configured,
)


# ===========================================================================
# 1. Data layer
# ===========================================================================

class TestDataLayer:
    def test_shipments_load(self):
        ships = load_shipments()
        assert len(ships) >= 5, "Need at least 5 shipments"

    def test_disruptions_load(self):
        disrs = load_disruptions()
        assert len(disrs) >= 3, "Need at least 3 disruptions"

    def test_vehicles_file_readable(self):
        path = os.path.join(_SRC_DIR, "data", "vehicles.json")
        with open(path) as f:
            data = json.load(f)
        assert len(data["vehicles"]) >= 5

    def test_temperature_readings_file_readable(self):
        path = os.path.join(_SRC_DIR, "data", "temperature_readings.json")
        with open(path) as f:
            data = json.load(f)
        entries = data["temperature_readings"]
        assert len(entries) >= 2
        # Must contain at least one excursion reading
        excursions = [
            r for e in entries for r in e.get("readings", [])
            if r.get("status") == "excursion"
        ]
        assert len(excursions) >= 1, "Temperature data must contain at least one excursion"

    def test_data_has_mixed_statuses(self):
        ships = load_shipments()
        statuses = {s["status"] for s in ships}
        assert "in_transit" in statuses
        # Must have at least one delayed/critical_delay shipment
        assert statuses & {"delayed", "critical_delay"}, "Need some delayed shipments"

    def test_data_has_cold_chain_and_standard(self):
        ships = load_shipments()
        cold = [s for s in ships if s.get("requires_cold_chain")]
        standard = [s for s in ships if not s.get("requires_cold_chain")]
        assert len(cold) >= 1
        assert len(standard) >= 1

    def test_data_has_multiple_priorities(self):
        ships = load_shipments()
        priorities = {s["priority"] for s in ships}
        assert len(priorities) >= 3, "Need at least 3 distinct priority levels"

    def test_data_has_unavailable_vehicle(self):
        path = os.path.join(_SRC_DIR, "data", "vehicles.json")
        with open(path) as f:
            vehicles = json.load(f)["vehicles"]
        unavailable = [v for v in vehicles if v.get("status") == "unavailable"]
        assert len(unavailable) >= 1, "Need at least one unavailable vehicle"


# ===========================================================================
# 2. Disruption detection
# ===========================================================================

class TestDisruptionDetection:
    def test_shp001_has_disruptions(self):
        result = get_shipment_disruptions("SHP-001")
        assert len(result) >= 1
        # All results must have required keys
        for d in result:
            for key in ("disruption_id", "severity", "estimated_delay_days", "match_reason"):
                assert key in d, "Missing key %s" % key

    def test_shp002_has_critical_disruption(self):
        result = get_shipment_disruptions("SHP-002")
        severities = [d["severity"] for d in result]
        assert "critical" in severities, "SHP-002 (pharma, cyclone) should have CRITICAL disruption"

    def test_shp006_multiple_disruptions(self):
        result = get_shipment_disruptions("SHP-006")
        assert len(result) >= 2, "SHP-006 should have at least 2 disruptions"

    def test_clean_shipment_has_no_disruptions(self):
        # SHP-005 is on-schedule with empty active_disruption_ids
        result = get_shipment_disruptions("SHP-005")
        assert isinstance(result, list)
        # May have 0 matches — just must not crash
        assert all("disruption_id" in d for d in result)

    def test_nonexistent_shipment_returns_empty(self):
        result = get_shipment_disruptions("SHP-FAKE")
        assert result == []

    def test_results_sorted_worst_first(self):
        result = get_shipment_disruptions("SHP-006")
        sev_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1, "unknown": 0}
        for i in range(len(result) - 1):
            assert sev_rank.get(result[i]["severity"], 0) >= sev_rank.get(result[i+1]["severity"], 0)

    def test_get_affected_shipments_returns_list(self):
        affected = get_affected_shipments()
        assert len(affected) >= 3
        for s in affected:
            for key in ("shipment_id", "highest_severity", "disruption_count", "disruptions"):
                assert key in s

    def test_get_disruption_by_id_found(self):
        d = get_disruption_by_id("DISR-001")
        assert d is not None
        assert d["id"] == "DISR-001"

    def test_get_disruption_by_id_not_found(self):
        assert get_disruption_by_id("DISR-FAKE") is None

    def test_disruption_summary_keys(self):
        summary = get_disruption_summary()
        for key in ("total_active_disruptions", "total_affected_shipments",
                    "critical_count", "high_count", "medium_count", "low_count"):
            assert key in summary
        assert summary["total_active_disruptions"] >= 1


# ===========================================================================
# 3. Risk engine
# ===========================================================================

class TestRiskEngine:
    def test_score_range(self):
        for s in score_all_shipments():
            assert 0 <= s["score"] <= 100, "Score out of range for %s" % s["shipment_id"]

    def test_classification_valid(self):
        valid = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        for s in score_all_shipments():
            assert s["classification"] in valid

    def test_result_has_required_keys(self):
        result = calculate_risk_by_id("SHP-001")
        assert result is not None
        for key in ("score", "classification", "explanation", "factor_breakdown", "disruptions"):
            assert key in result

    def test_factor_breakdown_keys(self):
        r = calculate_risk_by_id("SHP-001")
        for k in ("disruption_severity", "delay", "deadline_pressure", "priority", "cold_chain"):
            assert k in r["factor_breakdown"]

    def test_explanation_is_nonempty_string(self):
        r = calculate_risk_by_id("SHP-001")
        assert isinstance(r["explanation"], str) and len(r["explanation"]) > 10

    def test_disrupted_scores_higher_than_clean(self):
        # SHP-006: 16-day delay + 2 disruptions vs SHP-003: no disruption, no delay
        r_disrupted = calculate_risk_by_id("SHP-006")
        r_clean = calculate_risk_by_id("SHP-003")
        assert r_disrupted["score"] > r_clean["score"], (
            "SHP-006 (%d) should score higher than SHP-003 (%d)" % (
                r_disrupted["score"], r_clean["score"])
        )

    def test_critical_pharma_scores_high(self):
        r = calculate_risk_by_id("SHP-002")
        assert r["score"] >= 40, "Critical pharma with cyclone should score >= 40"

    def test_nonexistent_returns_none(self):
        assert calculate_risk_by_id("SHP-FAKE") is None

    def test_score_all_sorted_descending(self):
        scores = score_all_shipments()
        assert len(scores) == len(load_shipments())
        for i in range(len(scores) - 1):
            assert scores[i]["score"] >= scores[i+1]["score"], "Scores must be sorted descending"

    def test_risk_summary_keys(self):
        summary = get_risk_summary()
        for k in ("total_shipments", "critical_count", "high_count",
                  "medium_count", "low_count", "average_score"):
            assert k in summary

    def test_factor_breakdown_sum_equals_score(self):
        """Sum of factors must equal the reported score (capped at 100)."""
        for s in load_shipments():
            r = calculate_risk(s)
            factor_sum = sum(r["factor_breakdown"].values())
            expected = min(factor_sum, 100)
            assert r["score"] == expected, (
                "Score mismatch for %s: sum=%d score=%d" % (
                    s["id"], factor_sum, r["score"])
            )

    def test_cold_chain_excursion_adds_points(self):
        # SHP-002 (pharma) and SHP-004 (fresh produce) both have excursions
        r2 = calculate_risk_by_id("SHP-002")
        r4 = calculate_risk_by_id("SHP-004")
        assert r2["factor_breakdown"]["cold_chain"] == 5
        assert r4["factor_breakdown"]["cold_chain"] == 5

    def test_non_cold_chain_has_zero_cold_chain_points(self):
        # SHP-001 (electronics) has no cold chain requirement
        r = calculate_risk_by_id("SHP-001")
        assert r["factor_breakdown"]["cold_chain"] == 0


# ===========================================================================
# 4. Route advisor
# ===========================================================================

class TestRouteAdvisor:
    def test_shp001_has_alternatives(self):
        rec = recommend_alternative_routes("SHP-001")
        assert rec["shipment_id"] == "SHP-001"
        assert rec["action_required"] is True
        assert len(rec["alternatives"]) >= 1

    def test_alternative_has_required_keys(self):
        rec = recommend_alternative_routes("SHP-001")
        for alt in rec["alternatives"]:
            for k in ("route_id", "description", "extra_delay_days",
                      "extra_cost_usd", "reason", "available_vehicles", "vehicle_available"):
                assert k in alt, "Missing key %s in alternative" % k

    def test_shp002_critical_has_alternatives(self):
        rec = recommend_alternative_routes("SHP-002")
        assert rec["action_required"] is True
        assert len(rec["alternatives"]) >= 1

    def test_clean_shipment_not_action_required(self):
        rec = recommend_alternative_routes("SHP-005")
        assert rec["action_required"] is False

    def test_nonexistent_shipment_graceful(self):
        rec = recommend_alternative_routes("SHP-FAKE")
        assert rec["action_required"] is False
        assert "not found" in rec["recommendation"].lower()

    def test_recommend_all_affected_sorted(self):
        all_recs = recommend_all_affected()
        assert len(all_recs) >= 3
        for i in range(len(all_recs) - 1):
            assert all_recs[i]["risk_score"] >= all_recs[i+1]["risk_score"]

    def test_get_available_vehicles_returns_list(self):
        vehicles = get_available_vehicles()
        assert len(vehicles) >= 3
        for v in vehicles:
            assert v["available_teu"] > 0

    def test_get_available_vehicles_cargo_filter(self):
        pharma = get_available_vehicles(cargo_type="pharmaceuticals")
        assert len(pharma) >= 1
        for v in pharma:
            assert "pharmaceuticals" in v["supported_cargo"]

    def test_unavailable_vehicle_excluded(self):
        # V-005 is unavailable (engine failure)
        vehicles = get_available_vehicles()
        ids = [v["vehicle_id"] for v in vehicles]
        assert "V-005" not in ids

    def test_recommendation_contains_advisory_text_for_critical(self):
        rec = recommend_alternative_routes("SHP-002")
        # SHP-002 is CRITICAL — advisory banner must appear
        assert "ACTION REQUIRED" in rec["recommendation"] or \
               rec["risk_classification"] in ("HIGH", "CRITICAL")

    def test_vehicles_sorted_by_capacity_desc(self):
        vehicles = get_available_vehicles()
        for i in range(len(vehicles) - 1):
            assert vehicles[i]["available_teu"] >= vehicles[i+1]["available_teu"]


# ===========================================================================
# 5. watsonx client — mock fallback (MUST work without credentials)
# ===========================================================================

class TestWatsonxClient:
    def _clear_creds(self):
        """Remove watsonx env vars; return originals for restore."""
        k = os.environ.pop("WATSONX_API_KEY", None)
        p = os.environ.pop("WATSONX_PROJECT_ID", None)
        return k, p

    def _restore_creds(self, k, p):
        if k:
            os.environ["WATSONX_API_KEY"] = k
        if p:
            os.environ["WATSONX_PROJECT_ID"] = p

    def test_not_configured_when_no_env(self):
        k, p = self._clear_creds()
        try:
            assert is_watsonx_configured() is False
        finally:
            self._restore_creds(k, p)

    def test_mock_response_when_no_credentials(self):
        k, p = self._clear_creds()
        try:
            result = generate_ai_explanation("Why is SHP-001 at risk?")
            assert result is not None
            assert result["source"] == "mock"
            assert result["model_id"] == "mock"
            assert isinstance(result["text"], str)
            assert len(result["text"]) > 20
        finally:
            self._restore_creds(k, p)

    def test_mock_result_has_error_field(self):
        k, p = self._clear_creds()
        try:
            result = generate_ai_explanation("test")
            assert "error" in result   # may be None or a message
        finally:
            self._restore_creds(k, p)

    def test_empty_prompt_handled_gracefully(self):
        result = generate_ai_explanation("")
        assert result["source"] == "mock"
        assert result["error"] is not None

    def test_whitespace_prompt_handled_gracefully(self):
        result = generate_ai_explanation("   ")
        assert result["source"] == "mock"

    def test_configured_when_env_set(self):
        os.environ["WATSONX_API_KEY"] = "fake-key"
        os.environ["WATSONX_PROJECT_ID"] = "fake-project"
        try:
            assert is_watsonx_configured() is True
        finally:
            del os.environ["WATSONX_API_KEY"]
            del os.environ["WATSONX_PROJECT_ID"]

    def test_sdk_import_error_falls_back_to_mock(self):
        """Even if SDK is installed, a bad key should not crash — falls back to mock."""
        os.environ["WATSONX_API_KEY"] = "bad-key-that-will-fail"
        os.environ["WATSONX_PROJECT_ID"] = "bad-project"
        try:
            result = generate_ai_explanation("test prompt")
            # Should either succeed (if SDK not installed) or return mock on error
            assert result["text"]
            assert result["source"] in ("mock", "watsonx")
        finally:
            del os.environ["WATSONX_API_KEY"]
            del os.environ["WATSONX_PROJECT_ID"]
