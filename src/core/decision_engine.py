"""
decision_engine.py
==================
End-to-end operational decision orchestrator for SmartRoute AI.

This module is the ONLY place that wires together all core modules into
a single structured shipment analysis result.  It does NOT duplicate any
scoring logic — it exclusively calls the existing, tested functions in:
    risk_engine, disruption_detector, route_advisor, fleet_optimizer,
    cold_chain_monitor, watsonx_client

Recommended-action rules are deterministic (no randomness) and are
aligned with the existing risk classification thresholds defined in
risk_engine.py:
    CRITICAL  >= 75
    HIGH      >= 50
    MEDIUM    >= 25
    LOW        0-24

Public API
----------
    analyse_shipment(shipment_id: str) -> dict
        Full end-to-end analysis for one shipment.

    build_watsonx_prompt(analysis: dict) -> str
        Builds a rich, structured prompt from the analysis result for
        IBM watsonx.ai.  The LLM explains the already-calculated result;
        it does NOT replace the deterministic engine.

    is_valid_analysis(analysis: dict) -> bool
        Returns True when the analysis contains real data (not an error).
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy imports of core modules (same pattern as the rest of the project)
# ---------------------------------------------------------------------------
from .disruption_detector import load_shipments
from .risk_engine import calculate_risk_by_id
from .disruption_detector import get_shipment_disruptions
from .route_advisor import recommend_alternative_routes
from .fleet_optimizer import recommend_vehicle_for_shipment
from .cold_chain_monitor import get_shipment_temperature_status


# ---------------------------------------------------------------------------
# Action and priority vocabularies
# ---------------------------------------------------------------------------
_ACTIONS = {
    "reroute_escalate":        "Reroute Shipment + Escalate to Logistics Manager",
    "escalate":                "Escalate to Logistics Manager",
    "reroute_cold":            "Reroute + Immediate Cold-Chain Intervention",
    "reroute":                 "Reroute Shipment",
    "assign_vehicle":          "Assign Alternative Vehicle",
    "cold_intervention":       "Immediate Cold-Chain Intervention",
    "monitor_temperature":     "Monitor Temperature Closely",
    "prioritize":              "Prioritise Shipment",
    "continue_monitoring":     "Continue Monitoring",
    "no_action":               "No Action Required",
}

_PRIORITIES = {
    "reroute_escalate":        "IMMEDIATE",
    "escalate":                "IMMEDIATE",
    "reroute_cold":            "IMMEDIATE",
    "reroute":                 "HIGH",
    "assign_vehicle":          "HIGH",
    "cold_intervention":       "IMMEDIATE",
    "monitor_temperature":     "MEDIUM",
    "prioritize":              "HIGH",
    "continue_monitoring":     "MEDIUM",
    "no_action":               "LOW",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_shipment_raw(shipment_id: str) -> Optional[dict]:
    """Return the raw shipment dict or None."""
    return next((s for s in load_shipments() if s["id"] == shipment_id), None)


def _determine_action(
    risk_level: str,
    cold_severity: str,         # "NORMAL" | "WARNING" | "CRITICAL"
    has_alternatives: bool,
    has_suitable_vehicle: bool,
    delay_days: int,
    requires_cold_chain: bool,
) -> tuple[str, list[str]]:
    """
    Apply deterministic rules to select an action key and supporting factors.

    Returns
    -------
    (action_key, supporting_factors)
    """
    factors: list[str] = []

    # ── Rule 1: CRITICAL risk ──────────────────────────────────────────────
    if risk_level == "CRITICAL":
        factors.append("Risk level is CRITICAL (score ≥ 75)")
        if has_alternatives:
            factors.append("Alternative routes are available")
            return "reroute_escalate", factors
        else:
            factors.append("No pre-defined route alternatives available")
            return "escalate", factors

    # ── Rule 2: HIGH risk with critical cold-chain ─────────────────────────
    if risk_level == "HIGH" and cold_severity == "CRITICAL":
        factors.append("Risk level is HIGH")
        factors.append("Cold-chain excursion severity is CRITICAL")
        if has_alternatives:
            factors.append("Alternative routes are available")
            return "reroute_cold", factors
        return "cold_intervention", factors

    # ── Rule 3: HIGH risk with alternatives ───────────────────────────────
    if risk_level == "HIGH" and has_alternatives:
        factors.append("Risk level is HIGH")
        factors.append("Alternative routes are available")
        return "reroute", factors

    # ── Rule 4: HIGH risk with suitable vehicle ────────────────────────────
    if risk_level == "HIGH" and has_suitable_vehicle:
        factors.append("Risk level is HIGH")
        factors.append("A suitable replacement vehicle is available")
        return "assign_vehicle", factors

    # ── Rule 5: Critical cold-chain excursion regardless of risk level ─────
    if requires_cold_chain and cold_severity == "CRITICAL":
        factors.append("Cold-chain excursion severity is CRITICAL")
        return "cold_intervention", factors

    # ── Rule 6: Warning cold-chain ─────────────────────────────────────────
    if requires_cold_chain and cold_severity == "WARNING":
        factors.append("Temperature excursions detected (WARNING severity)")
        return "monitor_temperature", factors

    # ── Rule 7: HIGH risk with excessive delay ─────────────────────────────
    if risk_level == "HIGH" and delay_days >= 7:
        factors.append("Risk level is HIGH")
        factors.append(f"Shipment is delayed by {delay_days} day(s)")
        return "prioritize", factors

    # ── Rule 8: MEDIUM ─────────────────────────────────────────────────────
    if risk_level == "MEDIUM":
        factors.append("Risk level is MEDIUM — situation is being monitored")
        return "continue_monitoring", factors

    # ── Default: LOW risk ──────────────────────────────────────────────────
    factors.append("Risk level is LOW — shipment is on schedule")
    return "no_action", factors


def _determine_escalation(
    risk_level: str,
    cold_severity: str,
    delay_days: int,
) -> tuple[bool, list[str]]:
    """
    Determine whether escalation is required.

    Escalation is required when ANY of:
    - risk_level == "CRITICAL"
    - risk_level == "HIGH" AND cold_severity == "CRITICAL"
    - risk_level == "HIGH" AND delay_days >= 10

    Returns
    -------
    (escalation_required, reasons)
    """
    reasons: list[str] = []

    if risk_level == "CRITICAL":
        reasons.append("Risk level is CRITICAL")

    if risk_level == "HIGH" and cold_severity == "CRITICAL":
        reasons.append("HIGH risk combined with CRITICAL cold-chain excursion")

    if risk_level == "HIGH" and delay_days >= 10:
        reasons.append(f"HIGH risk with severe delay of {delay_days} day(s)")

    return bool(reasons), reasons


def _data_sources_status(
    shipment: Optional[dict],
    disruptions: list,
    route_result: Optional[dict],
    vehicle_result: Optional[dict],
    cold_chain: Optional[dict],
) -> dict:
    """Return a status dict for each data source (for UI transparency)."""
    return {
        "shipment_data":     "loaded" if shipment else "not_found",
        "disruption_data":   "loaded" if disruptions is not None else "unavailable",
        "route_data":        "loaded" if route_result else "unavailable",
        "vehicle_data":      "loaded" if vehicle_result else "unavailable",
        "temperature_data":  "loaded" if cold_chain else "not_applicable",
        "source":            "DEMO — local JSON files",
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyse_shipment(shipment_id: str) -> dict:
    """
    Produce a complete operational decision analysis for one shipment.

    Calls all core modules in sequence.  Returns a structured dict that
    the Streamlit UI, MCP server, and watsonx prompt builder can use
    directly.  Does NOT call IBM watsonx.ai — the AI explanation is a
    separate, user-triggered step.

    Parameters
    ----------
    shipment_id : str   e.g. "SHP-001"

    Returns
    -------
    dict with keys:
        error (str|None)        — set when shipment_id is not found
        shipment_id (str)
        shipment (dict|None)    — raw record from shipments.json
        risk_score (int)
        risk_level (str)        — CRITICAL / HIGH / MEDIUM / LOW
        risk_factors (dict)     — factor_breakdown from risk_engine
        risk_explanation (str)  — factor narrative from risk_engine
        disruptions (list)
        route_result (dict)     — from route_advisor
        vehicle_result (dict)   — from fleet_optimizer
        cold_chain (dict|None)  — from cold_chain_monitor (None if N/A)
        recommended_action (str)
        action_key (str)        — machine-readable action identifier
        action_priority (str)   — IMMEDIATE / HIGH / MEDIUM / LOW
        action_reason (str)
        supporting_factors (list[str])
        escalation_required (bool)
        escalation_reasons (list[str])
        data_sources (dict)
    """
    # ── 1. Load raw shipment ───────────────────────────────────────────────
    shipment = _get_shipment_raw(shipment_id)
    if shipment is None:
        logger.warning("decision_engine: shipment '%s' not found.", shipment_id)
        return {
            "error": "Shipment '%s' not found in the system." % shipment_id,
            "shipment_id": shipment_id,
            "shipment": None,
            "risk_score": 0,
            "risk_level": "UNKNOWN",
            "risk_factors": {},
            "risk_explanation": "",
            "disruptions": [],
            "route_result": {},
            "vehicle_result": {},
            "cold_chain": None,
            "recommended_action": "Shipment not found",
            "action_key": "no_action",
            "action_priority": "LOW",
            "action_reason": "Shipment ID not found in the dataset.",
            "supporting_factors": [],
            "escalation_required": False,
            "escalation_reasons": [],
            "data_sources": _data_sources_status(None, [], None, None, None),
        }

    # ── 2. Risk assessment ─────────────────────────────────────────────────
    risk_result = calculate_risk_by_id(shipment_id) or {}
    risk_score = risk_result.get("score", 0)
    risk_level = risk_result.get("classification", "LOW")
    risk_factors = risk_result.get("factor_breakdown", {})
    risk_explanation = risk_result.get("explanation", "")

    # ── 3. Disruptions ────────────────────────────────────────────────────
    disruptions = get_shipment_disruptions(shipment_id)

    # ── 4. Route alternatives ─────────────────────────────────────────────
    route_result = recommend_alternative_routes(shipment_id)
    alternatives = route_result.get("alternatives", [])

    # ── 5. Vehicle recommendation ─────────────────────────────────────────
    vehicle_result = recommend_vehicle_for_shipment(shipment_id)
    has_vehicle = vehicle_result.get("recommended_vehicle") is not None

    # ── 6. Cold-chain status ──────────────────────────────────────────────
    requires_cold_chain = bool(shipment.get("requires_cold_chain"))
    cold_chain: Optional[dict] = None
    cold_severity = "NORMAL"
    if requires_cold_chain:
        cold_chain = get_shipment_temperature_status(shipment_id)
        cold_severity = cold_chain.get("excursion_severity", "NORMAL")

    # ── 7. Recommended action ─────────────────────────────────────────────
    delay_days = int(shipment.get("delay_days", 0))
    action_key, supporting_factors = _determine_action(
        risk_level=risk_level,
        cold_severity=cold_severity,
        has_alternatives=bool(alternatives),
        has_suitable_vehicle=has_vehicle,
        delay_days=delay_days,
        requires_cold_chain=requires_cold_chain,
    )
    recommended_action = _ACTIONS[action_key]
    action_priority = _PRIORITIES[action_key]

    # Build a short human-readable reason
    action_reason = _build_action_reason(
        action_key, risk_level, risk_score,
        disruptions, cold_severity, delay_days,
        alternatives, vehicle_result,
    )

    # ── 8. Escalation ─────────────────────────────────────────────────────
    escalation_required, escalation_reasons = _determine_escalation(
        risk_level=risk_level,
        cold_severity=cold_severity,
        delay_days=delay_days,
    )

    # ── 9. Data source status ─────────────────────────────────────────────
    data_sources = _data_sources_status(
        shipment, disruptions, route_result, vehicle_result, cold_chain
    )

    return {
        "error": None,
        "shipment_id": shipment_id,
        "shipment": shipment,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "risk_explanation": risk_explanation,
        "disruptions": disruptions,
        "route_result": route_result,
        "vehicle_result": vehicle_result,
        "cold_chain": cold_chain,
        "recommended_action": recommended_action,
        "action_key": action_key,
        "action_priority": action_priority,
        "action_reason": action_reason,
        "supporting_factors": supporting_factors,
        "escalation_required": escalation_required,
        "escalation_reasons": escalation_reasons,
        "data_sources": data_sources,
        "ml_delay_prediction": route_result.get("ml_delay_prediction", {}),
    }


def _build_action_reason(
    action_key: str,
    risk_level: str,
    risk_score: int,
    disruptions: list,
    cold_severity: str,
    delay_days: int,
    alternatives: list,
    vehicle_result: dict,
) -> str:
    """Build a short, plain-English reason for the recommended action."""
    disr_count = len(disruptions)
    disr_titles = (
        " and ".join(d["title"] for d in disruptions[:2])
        if disruptions else "no active disruptions"
    )
    alt_count = len(alternatives)

    if action_key == "reroute_escalate":
        return (
            "Risk score is %d/100 (%s) with %d active disruption(s) (%s). "
            "%d alternative route(s) available. Immediate rerouting and "
            "management escalation are both required."
            % (risk_score, risk_level, disr_count, disr_titles, alt_count)
        )
    if action_key == "escalate":
        return (
            "Risk score is %d/100 (CRITICAL) with %d active disruption(s). "
            "No pre-defined alternative routes are available. "
            "Logistics manager must be notified immediately to arrange alternatives."
            % (risk_score, disr_count)
        )
    if action_key == "reroute_cold":
        return (
            "Risk score is %d/100 (HIGH) with cold-chain excursion severity CRITICAL. "
            "%d alternative route(s) available. Cargo integrity is at risk; "
            "immediate rerouting and cold-chain intervention required."
            % (risk_score, alt_count)
        )
    if action_key == "reroute":
        return (
            "Risk score is %d/100 (HIGH) with %d active disruption(s) (%s). "
            "%d alternative route(s) available that avoid the active disruption(s)."
            % (risk_score, disr_count, disr_titles, alt_count)
        )
    if action_key == "assign_vehicle":
        best = (vehicle_result.get("recommended_vehicle") or {})
        vname = best.get("name", "a suitable vessel")
        return (
            "Risk score is %d/100 (HIGH). A suitable replacement vehicle (%s) "
            "is available. Assigning an alternative vehicle may reduce delay impact."
            % (risk_score, vname)
        )
    if action_key == "cold_intervention":
        return (
            "Cold-chain excursion severity is CRITICAL. "
            "Temperature-sensitive cargo requires immediate corrective action "
            "to prevent spoilage or regulatory non-compliance."
        )
    if action_key == "monitor_temperature":
        return (
            "Temperature excursions have been detected (WARNING severity). "
            "No immediate rerouting required, but close temperature monitoring "
            "is essential to prevent escalation."
        )
    if action_key == "prioritize":
        return (
            "Risk score is %d/100 (HIGH) with a delay of %d day(s). "
            "Shipment should be prioritised for next available capacity."
            % (risk_score, delay_days)
        )
    if action_key == "continue_monitoring":
        return (
            "Risk score is %d/100 (MEDIUM). Active disruptions are present "
            "but have not reached HIGH severity threshold. Continue monitoring."
            % risk_score
        )
    return "Risk score is %d/100 (%s). No immediate action is required." % (
        risk_score, risk_level
    )


def build_watsonx_prompt(analysis: dict) -> str:
    """
    Build a rich, structured prompt from a completed analysis result.

    The prompt feeds IBM watsonx.ai with enough context to produce a
    concise, accurate, operational explanation.  The LLM should EXPLAIN
    the deterministic result — not recalculate risk.

    Parameters
    ----------
    analysis : dict   Result from analyse_shipment()

    Returns
    -------
    str   Prompt string ready to pass to generate_ai_explanation()
    """
    sid     = analysis.get("shipment_id", "UNKNOWN")
    score   = analysis.get("risk_score", 0)
    level   = analysis.get("risk_level", "UNKNOWN")
    action  = analysis.get("recommended_action", "—")
    esc     = "YES" if analysis.get("escalation_required") else "NO"

    # Disruptions
    disrs = analysis.get("disruptions", [])
    disr_text = (
        "; ".join(
            "%s (%s, +%d days)" % (
                d["title"], d["severity"].upper(), d["estimated_delay_days"]
            )
            for d in disrs
        ) if disrs else "None"
    )

    # Risk factors
    fb = analysis.get("risk_factors", {})
    factors_text = (
        "Disruption severity %d/35 | Delay %d/25 | Deadline pressure %d/20 | "
        "Priority %d/15 | Cold-chain %d/5"
    ) % (
        fb.get("disruption_severity", 0),
        fb.get("delay", 0),
        fb.get("deadline_pressure", 0),
        fb.get("priority", 0),
        fb.get("cold_chain", 0),
    )

    # Routes
    alts = analysis.get("route_result", {}).get("alternatives", [])
    route_text = (
        " | ".join(
            "%s (+%d days, +$%s)" % (
                a["description"], a["extra_delay_days"],
                "{:,}".format(a["extra_cost_usd"])
            )
            for a in alts[:2]
        ) if alts else "No pre-defined alternatives"
    )

    # Vehicle
    vr   = analysis.get("vehicle_result", {})
    best = vr.get("recommended_vehicle")
    veh_text = (
        "%s (%s, %d TEU available, reefer slots: %d)" % (
            best["name"], best["carrier"],
            best["available_teu"], best.get("available_reefer_slots", 0)
        ) if best else vr.get("reason", "No suitable vehicle found")
    )

    # Cold-chain
    cc = analysis.get("cold_chain")
    cold_text = "Not applicable (no cold-chain requirement)"
    if cc:
        cold_text = (
            "Safe range: %s–%s °C | Latest: %s °C | "
            "Excursions: %d | Severity: %s | Risk score: %d/100"
        ) % (
            cc.get("required_temp_min_c", "?"),
            cc.get("required_temp_max_c", "?"),
            cc.get("latest_temp_c", "?"),
            cc.get("excursion_count", 0),
            cc.get("excursion_severity", "NORMAL"),
            cc.get("cold_chain_risk_score", 0),
        )

    prompt = (
        "You are an operational supply chain risk advisor. "
        "A logistics coordinator needs a concise, plain-English explanation of the "
        "current situation for shipment %(sid)s. "
        "Use the structured data below. Do NOT invent facts or data not provided.\n\n"
        "--- STRUCTURED ANALYSIS ---\n"
        "Shipment ID       : %(sid)s\n"
        "Risk Score        : %(score)d/100 (%(level)s)\n"
        "Risk Factor Breakdown: %(factors)s\n"
        "Active Disruptions: %(disr)s\n"
        "Route Alternatives: %(route)s\n"
        "Vehicle Recommendation: %(veh)s\n"
        "Cold-Chain Status : %(cold)s\n"
        "Recommended Action: %(action)s\n"
        "Escalation Required: %(esc)s\n"
        "---------------------------\n\n"
        "Please answer these four questions concisely (2-3 sentences each):\n"
        "1. What happened to this shipment?\n"
        "2. Why is it at risk — what are the main factors?\n"
        "3. What is the recommended operational action and why?\n"
        "4. What should the logistics coordinator monitor next?"
    ) % {
        "sid":     sid,
        "score":   score,
        "level":   level,
        "factors": factors_text,
        "disr":    disr_text,
        "route":   route_text,
        "veh":     veh_text,
        "cold":    cold_text,
        "action":  action,
        "esc":     esc,
    }

    return prompt


def is_valid_analysis(analysis: dict) -> bool:
    """Return True when the analysis contains real data (not an error result)."""
    return analysis.get("error") is None and analysis.get("shipment") is not None
