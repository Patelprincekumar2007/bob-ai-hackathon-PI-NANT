"""
tests/test_decision_engine.py
==============================
Pytest tests for:
  - Decision Engine (src/core/decision_engine.py)
  - Recommended Action Engine (deterministic rules)
  - Escalation logic
  - MCP consistency: MCP tool results == core engine results
  - Watsonx fallback behaviour
  - Invalid/missing data scenarios

Run from repo root:
    cd bob-ai-hackathon-PI-NANT
    python -m pytest tests/test_decision_engine.py -v

All tests use only local JSON data — no external APIs required.
"""

import os
import sys

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.normpath(os.path.join(_TESTS_DIR, "..", "src"))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

import pytest

from core.decision_engine import (
    analyse_shipment,
    build_watsonx_prompt,
    is_valid_analysis,
    _determine_action,
    _determine_escalation,
)
from core.risk_engine import calculate_risk_by_id
from core.disruption_detector import load_shipments
from core.watsonx_client import generate_ai_explanation, is_watsonx_configured
import mcp_server as mcp


# ===========================================================================
# Helper — valid shipment IDs in the demo dataset
# ===========================================================================
_ALL_IDS = [s["id"] for s in load_shipments()]
_COLD_IDS = [s["id"] for s in load_shipments() if s.get("requires_cold_chain")]
_DISRUPTED = [
    s["id"] for s in load_shipments()
    if s.get("active_disruption_ids")
]


# ===========================================================================
# 1. Decision Engine — structure
# ===========================================================================

class TestDecisionEngineStructure:
    """analyse_shipment() returns the expected top-level keys."""

    _REQUIRED_KEYS = [
        "error", "shipment_id", "shipment", "risk_score", "risk_level",
        "risk_factors", "risk_explanation", "disruptions", "route_result",
        "vehicle_result", "cold_chain", "recommended_action", "action_key",
        "action_priority", "action_reason", "supporting_factors",
        "escalation_required", "escalation_reasons", "data_sources",
    ]

    def test_returns_all_required_keys_for_valid_id(self):
        result = analyse_shipment("SHP-001")
        for key in self._REQUIRED_KEYS:
            assert key in result, "Missing key: %s" % key

    def test_error_is_none_for_valid_id(self):
        result = analyse_shipment("SHP-001")
        assert result["error"] is None

    def test_shipment_is_dict_for_valid_id(self):
        result = analyse_shipment("SHP-001")
        assert isinstance(result["shipment"], dict)

    def test_risk_score_is_int(self):
        result = analyse_shipment("SHP-001")
        assert isinstance(result["risk_score"], int)
        assert 0 <= result["risk_score"] <= 100

    def test_risk_level_is_valid(self):
        result = analyse_shipment("SHP-001")
        assert result["risk_level"] in ("CRITICAL", "HIGH", "MEDIUM", "LOW")

    def test_action_priority_is_valid(self):
        result = analyse_shipment("SHP-001")
        assert result["action_priority"] in ("IMMEDIATE", "HIGH", "MEDIUM", "LOW")

    def test_escalation_required_is_bool(self):
        result = analyse_shipment("SHP-001")
        assert isinstance(result["escalation_required"], bool)

    def test_escalation_reasons_is_list(self):
        result = analyse_shipment("SHP-001")
        assert isinstance(result["escalation_reasons"], list)

    def test_supporting_factors_is_list(self):
        result = analyse_shipment("SHP-001")
        assert isinstance(result["supporting_factors"], list)

    def test_data_sources_is_dict(self):
        result = analyse_shipment("SHP-001")
        assert isinstance(result["data_sources"], dict)
        assert "source" in result["data_sources"]

    def test_all_valid_shipments_produce_no_error(self):
        for sid in _ALL_IDS:
            result = analyse_shipment(sid)
            assert result["error"] is None, (
                "Unexpected error for %s: %s" % (sid, result["error"])
            )

    def test_is_valid_analysis_true_for_valid(self):
        result = analyse_shipment("SHP-001")
        assert is_valid_analysis(result) is True

    def test_is_valid_analysis_false_for_invalid(self):
        result = analyse_shipment("SHP-INVALID-9999")
        assert is_valid_analysis(result) is False


# ===========================================================================
# 2. Invalid shipment ID handling
# ===========================================================================

class TestInvalidShipmentID:
    """analyse_shipment() handles bad IDs safely."""

    def test_missing_id_returns_error_key(self):
        result = analyse_shipment("SHP-DOES-NOT-EXIST")
        assert result["error"] is not None

    def test_missing_id_no_exception(self):
        # Must not raise — just return an error dict
        result = analyse_shipment("NOTEXIST")
        assert isinstance(result, dict)

    def test_missing_id_risk_score_zero(self):
        result = analyse_shipment("XXXX")
        assert result["risk_score"] == 0

    def test_missing_id_escalation_false(self):
        result = analyse_shipment("XXXX")
        assert result["escalation_required"] is False

    def test_empty_string_id(self):
        result = analyse_shipment("")
        assert isinstance(result, dict)
        assert result["error"] is not None


# ===========================================================================
# 3. Deterministic Recommended Action rules
# ===========================================================================

class TestRecommendedAction:
    """_determine_action() produces the correct key for each scenario."""

    def test_critical_with_alternatives_is_reroute_escalate(self):
        key, _ = _determine_action(
            risk_level="CRITICAL", cold_severity="NORMAL",
            has_alternatives=True, has_suitable_vehicle=True,
            delay_days=5, requires_cold_chain=False,
        )
        assert key == "reroute_escalate"

    def test_critical_without_alternatives_is_escalate(self):
        key, _ = _determine_action(
            risk_level="CRITICAL", cold_severity="NORMAL",
            has_alternatives=False, has_suitable_vehicle=False,
            delay_days=3, requires_cold_chain=False,
        )
        assert key == "escalate"

    def test_high_with_critical_cold_and_alternatives_is_reroute_cold(self):
        key, _ = _determine_action(
            risk_level="HIGH", cold_severity="CRITICAL",
            has_alternatives=True, has_suitable_vehicle=True,
            delay_days=5, requires_cold_chain=True,
        )
        assert key == "reroute_cold"

    def test_high_with_critical_cold_no_alternatives_is_cold_intervention(self):
        key, _ = _determine_action(
            risk_level="HIGH", cold_severity="CRITICAL",
            has_alternatives=False, has_suitable_vehicle=False,
            delay_days=5, requires_cold_chain=True,
        )
        assert key == "cold_intervention"

    def test_high_with_alternatives_no_cold_is_reroute(self):
        key, _ = _determine_action(
            risk_level="HIGH", cold_severity="NORMAL",
            has_alternatives=True, has_suitable_vehicle=True,
            delay_days=5, requires_cold_chain=False,
        )
        assert key == "reroute"

    def test_high_with_vehicle_no_alternatives_is_assign_vehicle(self):
        key, _ = _determine_action(
            risk_level="HIGH", cold_severity="NORMAL",
            has_alternatives=False, has_suitable_vehicle=True,
            delay_days=5, requires_cold_chain=False,
        )
        assert key == "assign_vehicle"

    def test_cold_critical_low_risk_is_cold_intervention(self):
        key, _ = _determine_action(
            risk_level="LOW", cold_severity="CRITICAL",
            has_alternatives=False, has_suitable_vehicle=False,
            delay_days=0, requires_cold_chain=True,
        )
        assert key == "cold_intervention"

    def test_cold_warning_is_monitor_temperature(self):
        key, _ = _determine_action(
            risk_level="MEDIUM", cold_severity="WARNING",
            has_alternatives=False, has_suitable_vehicle=False,
            delay_days=2, requires_cold_chain=True,
        )
        assert key == "monitor_temperature"

    def test_medium_no_cold_is_continue_monitoring(self):
        key, _ = _determine_action(
            risk_level="MEDIUM", cold_severity="NORMAL",
            has_alternatives=False, has_suitable_vehicle=False,
            delay_days=2, requires_cold_chain=False,
        )
        assert key == "continue_monitoring"

    def test_low_is_no_action(self):
        key, _ = _determine_action(
            risk_level="LOW", cold_severity="NORMAL",
            has_alternatives=False, has_suitable_vehicle=False,
            delay_days=0, requires_cold_chain=False,
        )
        assert key == "no_action"

    def test_action_is_deterministic_same_inputs(self):
        """Same inputs must always produce the same action."""
        kwargs = dict(
            risk_level="HIGH", cold_severity="NORMAL",
            has_alternatives=True, has_suitable_vehicle=True,
            delay_days=5, requires_cold_chain=False,
        )
        k1, _ = _determine_action(**kwargs)
        k2, _ = _determine_action(**kwargs)
        assert k1 == k2

    def test_supporting_factors_is_non_empty_list(self):
        _, factors = _determine_action(
            risk_level="CRITICAL", cold_severity="NORMAL",
            has_alternatives=True, has_suitable_vehicle=True,
            delay_days=3, requires_cold_chain=False,
        )
        assert len(factors) > 0

    def test_recommended_action_string_non_empty(self):
        """analyse_shipment recommended_action must be a non-empty string."""
        for sid in _ALL_IDS:
            result = analyse_shipment(sid)
            assert isinstance(result["recommended_action"], str)
            assert len(result["recommended_action"]) > 0


# ===========================================================================
# 4. Escalation logic
# ===========================================================================

class TestEscalationLogic:
    """_determine_escalation() and analyse_shipment() escalation behaviour."""

    def test_critical_requires_escalation(self):
        req, reasons = _determine_escalation("CRITICAL", "NORMAL", 0)
        assert req is True
        assert len(reasons) > 0

    def test_high_with_critical_cold_requires_escalation(self):
        req, reasons = _determine_escalation("HIGH", "CRITICAL", 3)
        assert req is True

    def test_high_with_long_delay_requires_escalation(self):
        req, reasons = _determine_escalation("HIGH", "NORMAL", 10)
        assert req is True

    def test_high_with_delay_less_than_10_no_escalation(self):
        req, _ = _determine_escalation("HIGH", "NORMAL", 9)
        # 9 days is below the 10-day escalation threshold
        assert req is False

    def test_medium_no_escalation(self):
        req, _ = _determine_escalation("MEDIUM", "NORMAL", 5)
        assert req is False

    def test_low_no_escalation(self):
        req, _ = _determine_escalation("LOW", "NORMAL", 0)
        assert req is False

    def test_shp006_critical_delay_escalation(self):
        """SHP-006 has 16-day delay and multiple disruptions — should escalate."""
        result = analyse_shipment("SHP-006")
        # SHP-006 has 16 delay days and two disruptions — very likely CRITICAL
        if result["risk_level"] in ("CRITICAL", "HIGH"):
            # Must escalate given severity
            assert result["escalation_required"] is True


# ===========================================================================
# 5. Cold-chain integration
# ===========================================================================

class TestColdChainIntegration:
    """Cold-chain shipments get cold_chain populated; others get None."""

    def test_cold_chain_shipment_has_cold_chain_data(self):
        for sid in _COLD_IDS:
            result = analyse_shipment(sid)
            assert result["cold_chain"] is not None, (
                "Cold-chain shipment %s has no cold_chain data" % sid
            )

    def test_non_cold_chain_shipment_has_none(self):
        non_cold = [s["id"] for s in load_shipments()
                    if not s.get("requires_cold_chain")]
        for sid in non_cold:
            result = analyse_shipment(sid)
            assert result["cold_chain"] is None, (
                "Non-cold shipment %s unexpectedly has cold_chain data" % sid
            )

    def test_cold_chain_has_required_fields(self):
        for sid in _COLD_IDS:
            result = analyse_shipment(sid)
            cc = result["cold_chain"]
            for field in ("excursion_detected", "excursion_severity",
                          "cold_chain_risk_score", "reading_count"):
                assert field in cc, "cold_chain missing %s for %s" % (field, sid)


# ===========================================================================
# 6. Risk score consistency — decision engine == core engine
# ===========================================================================

class TestRiskScoreConsistency:
    """decision_engine must produce the same score as calculate_risk_by_id()."""

    def test_score_matches_risk_engine_for_all_shipments(self):
        for sid in _ALL_IDS:
            core = calculate_risk_by_id(sid)
            eng  = analyse_shipment(sid)
            assert eng["risk_score"] == core["score"], (
                "Score mismatch for %s: engine=%d core=%d"
                % (sid, eng["risk_score"], core["score"])
            )

    def test_risk_level_matches_risk_engine_for_all_shipments(self):
        for sid in _ALL_IDS:
            core = calculate_risk_by_id(sid)
            eng  = analyse_shipment(sid)
            assert eng["risk_level"] == core["classification"], (
                "Level mismatch for %s: engine=%s core=%s"
                % (sid, eng["risk_level"], core["classification"])
            )


# ===========================================================================
# 7. MCP consistency — MCP tool results == core engine
# ===========================================================================

class TestMCPConsistency:
    """MCP tool results must be consistent with the core engine."""

    def test_mcp_risk_score_matches_core_for_all_ids(self):
        for sid in _ALL_IDS:
            mcp_result  = mcp.tool_get_shipment_risk(sid)
            core_result = calculate_risk_by_id(sid)
            assert mcp_result["score"] == core_result["score"], (
                "MCP score != core for %s" % sid
            )

    def test_mcp_risk_classification_matches_core(self):
        for sid in _ALL_IDS:
            mcp_result  = mcp.tool_get_shipment_risk(sid)
            core_result = calculate_risk_by_id(sid)
            assert mcp_result["classification"] == core_result["classification"], (
                "MCP classification != core for %s" % sid
            )

    def test_mcp_disruptions_count_matches_core(self):
        from core.disruption_detector import get_shipment_disruptions
        for sid in _ALL_IDS:
            mcp_result  = mcp.tool_get_shipment_disruptions(sid)
            core_result = get_shipment_disruptions(sid)
            assert mcp_result["disruption_count"] == len(core_result), (
                "MCP disruption count != core for %s" % sid
            )

    def test_mcp_recommend_route_returns_dict(self):
        for sid in _ALL_IDS:
            result = mcp.tool_recommend_route(sid)
            assert isinstance(result, dict)
            assert "action_required" in result

    def test_mcp_recommend_vehicle_returns_dict(self):
        for sid in _ALL_IDS:
            result = mcp.tool_recommend_vehicle(sid)
            assert isinstance(result, dict)
            assert "shipment_id" in result

    def test_mcp_fleet_status_returns_dict(self):
        result = mcp.tool_get_fleet_status()
        assert isinstance(result, dict)
        assert "total" in result

    def test_mcp_temperature_alerts_returns_dict(self):
        result = mcp.tool_get_temperature_alerts()
        assert isinstance(result, dict)
        assert "alert_count" in result

    def test_mcp_explain_shipment_returns_text(self):
        result = mcp.tool_explain_shipment("SHP-001")
        assert isinstance(result["explanation"], str)
        assert len(result["explanation"]) > 0

    def test_mcp_explain_shipment_source_is_watsonx_or_mock(self):
        result = mcp.tool_explain_shipment("SHP-001")
        assert result["source"] in ("watsonx", "mock")

    def test_mcp_explain_shipment_invalid_id_no_exception(self):
        result = mcp.tool_explain_shipment("SHP-INVALID-9999")
        assert isinstance(result, dict)
        assert "explanation" in result

    def test_all_seven_mcp_tools_registered(self):
        expected = {
            "get_shipment_risk", "get_shipment_disruptions",
            "recommend_route", "recommend_vehicle",
            "get_fleet_status", "get_temperature_alerts",
            "explain_shipment",
        }
        assert expected == set(mcp.TOOLS.keys())

    def test_mcp_invalid_id_returns_error_not_exception(self):
        result = mcp.tool_get_shipment_risk("NO-SUCH-ID")
        assert "error" in result
        assert result["score"] is None


# ===========================================================================
# 8. watsonx fallback behaviour
# ===========================================================================

class TestWatsonxFallback:
    """Verify demo mode / fallback works when credentials are absent."""

    def test_generate_ai_explanation_always_returns_dict(self):
        result = generate_ai_explanation("Test prompt")
        assert isinstance(result, dict)

    def test_result_has_text_source_model_error(self):
        result = generate_ai_explanation("Test prompt")
        for key in ("text", "source", "model_id"):
            assert key in result, "Missing key: %s" % key

    def test_source_is_watsonx_or_mock(self):
        result = generate_ai_explanation("Test prompt")
        assert result["source"] in ("watsonx", "mock")

    def test_demo_mode_source_is_mock_when_no_credentials(self):
        """When watsonx is not configured, source must be 'mock'."""
        if not is_watsonx_configured():
            result = generate_ai_explanation("Some prompt")
            assert result["source"] == "mock"

    def test_mock_text_not_empty(self):
        result = generate_ai_explanation("Some prompt")
        assert len(result["text"]) > 0

    def test_empty_prompt_handled_gracefully(self):
        result = generate_ai_explanation("")
        assert isinstance(result, dict)
        assert result["source"] in ("watsonx", "mock")


# ===========================================================================
# 9. Watsonx prompt builder
# ===========================================================================

class TestWatsonxPromptBuilder:
    """build_watsonx_prompt() produces non-empty, structured prompts."""

    def test_prompt_is_non_empty_string(self):
        analysis = analyse_shipment("SHP-001")
        prompt = build_watsonx_prompt(analysis)
        assert isinstance(prompt, str)
        assert len(prompt) > 100

    def test_prompt_contains_shipment_id(self):
        analysis = analyse_shipment("SHP-004")
        prompt = build_watsonx_prompt(analysis)
        assert "SHP-004" in prompt

    def test_prompt_contains_risk_score(self):
        analysis = analyse_shipment("SHP-004")
        prompt = build_watsonx_prompt(analysis)
        assert str(analysis["risk_score"]) in prompt

    def test_prompt_contains_recommended_action(self):
        analysis = analyse_shipment("SHP-004")
        prompt = build_watsonx_prompt(analysis)
        # The recommended action string should appear in the prompt
        assert analysis["recommended_action"][:20] in prompt

    def test_invalid_shipment_prompt_still_builds(self):
        analysis = analyse_shipment("SHP-INVALID")
        # Even an error analysis should build a prompt without crashing
        prompt = build_watsonx_prompt(analysis)
        assert isinstance(prompt, str)


# ===========================================================================
# 10. Empty/missing data scenarios
# ===========================================================================

class TestEdgeCases:
    """Robustness checks for edge cases."""

    def test_shipment_without_cold_chain_no_crash(self):
        """Non-cold-chain shipments should not crash the engine."""
        non_cold = [s["id"] for s in load_shipments()
                    if not s.get("requires_cold_chain")]
        for sid in non_cold:
            result = analyse_shipment(sid)
            assert result["error"] is None

    def test_shipment_with_no_disruptions_produces_valid_result(self):
        """SHP-003 and SHP-005 have no active_disruption_ids."""
        no_disr = [s["id"] for s in load_shipments()
                   if not s.get("active_disruption_ids")]
        for sid in no_disr:
            result = analyse_shipment(sid)
            assert result["error"] is None
            assert isinstance(result["disruptions"], list)

    def test_analyse_all_shipments_no_exception(self):
        """Full suite — no exceptions for any shipment in the dataset."""
        for sid in _ALL_IDS:
            result = analyse_shipment(sid)
            assert isinstance(result, dict)

    def test_mcp_call_tool_unknown_tool(self):
        result = mcp.call_tool("nonexistent_tool", {})
        assert "error" in result

    def test_mcp_call_tool_missing_required_param(self):
        result = mcp.call_tool("get_shipment_risk", {})  # missing shipment_id
        assert "error" in result
