"""
disruption_detector.py
=======================
Matches active supply-chain disruptions against shipments.

All data is loaded from src/data/ JSON files — no external APIs.

Matching rules (any one is sufficient):
    1. Shipment's active_disruption_ids list contains the disruption ID.
    2. Shipment's route_id is in the disruption's affected_routes.
    3. Shipment's carrier is in the disruption's affected_carriers.
    4. Origin or destination port code is in the disruption's affected_ports.
    5. Shipment's vessel_id is in the disruption's affected_vessel_ids.

Public API
----------
    load_shipments()                     -> list[dict]
    load_disruptions()                   -> list[dict]
    get_disruption_by_id(id)             -> dict | None
    get_shipment_disruptions(shp_id)     -> list[dict]
    get_affected_shipments()             -> list[dict]
    get_disruption_summary()             -> dict
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.normpath(os.path.join(_DIR, "..", "data"))

_SEVERITY_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1, "unknown": 0}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _data_path(name):
    return os.path.join(_DATA, name)


def _rank(severity):
    return _SEVERITY_RANK.get((severity or "unknown").lower(), 0)


def _highest(severities):
    return max(severities, key=_rank) if severities else "unknown"


def _affects(disruption, shipment):
    """Return True when the disruption affects the shipment."""
    # Rule 1 – explicit link
    if disruption["id"] in shipment.get("active_disruption_ids", []):
        return True
    # Rule 2 – route
    if shipment.get("route_id") in disruption.get("affected_routes", []):
        return True
    # Rule 3 – carrier
    if shipment.get("carrier") in disruption.get("affected_carriers", []):
        return True
    # Rule 4 – ports
    aff_ports = disruption.get("affected_ports", [])
    orig = (shipment.get("origin") or {}).get("port_code", "")
    dest = (shipment.get("destination") or {}).get("port_code", "")
    if orig in aff_ports or dest in aff_ports:
        return True
    # Rule 5 – vessel
    if shipment.get("vessel_id") in disruption.get("affected_vessel_ids", []):
        return True
    return False


def _match_reason(disruption, shipment):
    """Human-readable explanation of why the disruption was matched."""
    reasons = []
    if disruption["id"] in shipment.get("active_disruption_ids", []):
        reasons.append("explicitly linked in shipment record")
    if shipment.get("route_id") in disruption.get("affected_routes", []):
        reasons.append("shipment route %s is affected" % shipment.get("route_id"))
    if shipment.get("carrier") in disruption.get("affected_carriers", []):
        reasons.append("carrier %s is affected" % shipment.get("carrier"))
    aff_ports = disruption.get("affected_ports", [])
    orig = (shipment.get("origin") or {}).get("port_code", "")
    dest = (shipment.get("destination") or {}).get("port_code", "")
    if orig in aff_ports:
        reasons.append("origin port %s is affected" % orig)
    if dest in aff_ports:
        reasons.append("destination port %s is affected" % dest)
    if shipment.get("vessel_id") in disruption.get("affected_vessel_ids", []):
        reasons.append("vessel %s is directly involved" % shipment.get("vessel_id"))
    return "; ".join(reasons) if reasons else "general area overlap"


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def load_shipments():
    """Load all shipments from shipments.json. Returns list[dict]."""
    with open(_data_path("shipments.json"), "r", encoding="utf-8") as f:
        return json.load(f).get("shipments", [])


def load_disruptions():
    """Load all disruptions from disruptions.json. Returns list[dict]."""
    with open(_data_path("disruptions.json"), "r", encoding="utf-8") as f:
        return json.load(f).get("disruptions", [])


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_disruption_by_id(disruption_id):
    """
    Return a single disruption record by ID, or None if not found.

    Parameters
    ----------
    disruption_id : str   e.g. "DISR-001"
    """
    for d in load_disruptions():
        if d["id"] == disruption_id:
            return d
    return None


def get_shipment_disruptions(shipment_id):
    """
    Return all ACTIVE disruptions that affect a specific shipment.

    Parameters
    ----------
    shipment_id : str   e.g. "SHP-001"

    Returns
    -------
    list[dict]  sorted worst-severity first. Each dict contains:
        disruption_id, type, title, severity, status,
        estimated_delay_days, additional_cost_usd, description, match_reason
    """
    target = next((s for s in load_shipments() if s["id"] == shipment_id), None)
    if target is None:
        logger.warning("Shipment '%s' not found.", shipment_id)
        return []

    results = []
    for d in load_disruptions():
        if d.get("status") not in ("active", "monitoring"):
            continue
        if not _affects(d, target):
            continue
        results.append({
            "disruption_id": d["id"],
            "type": d.get("type", "unknown"),
            "title": d.get("title", ""),
            "severity": d.get("severity", "unknown"),
            "status": d.get("status", "unknown"),
            "estimated_delay_days": d.get("estimated_delay_days", 0),
            "additional_cost_usd": d.get("additional_cost_usd", 0),
            "description": d.get("description", ""),
            "match_reason": _match_reason(d, target),
        })

    results.sort(key=lambda x: _rank(x["severity"]), reverse=True)
    return results


def get_affected_shipments():
    """
    Return a summary list of all shipments with at least one active disruption.

    Returns
    -------
    list[dict]  sorted worst-severity first. Each dict contains:
        shipment_id, description, carrier, origin, destination,
        status, priority, delay_days, disruption_count,
        highest_severity, disruptions, requires_cold_chain
    """
    active = {
        d["id"]: d for d in load_disruptions()
        if d.get("status") in ("active", "monitoring")
    }
    results = []
    for s in load_shipments():
        matched = []
        for d in active.values():
            if not _affects(d, s):
                continue
            matched.append({
                "disruption_id": d["id"],
                "type": d.get("type", "unknown"),
                "title": d.get("title", ""),
                "severity": d.get("severity", "unknown"),
                "estimated_delay_days": d.get("estimated_delay_days", 0),
                "match_reason": _match_reason(d, s),
            })
        if not matched:
            continue
        matched.sort(key=lambda x: _rank(x["severity"]), reverse=True)
        orig = s.get("origin", {})
        dest = s.get("destination", {})
        results.append({
            "shipment_id": s["id"],
            "description": s.get("description", ""),
            "carrier": s.get("carrier", ""),
            "origin": "%s, %s" % (orig.get("city", ""), orig.get("country", "")),
            "destination": "%s, %s" % (dest.get("city", ""), dest.get("country", "")),
            "status": s.get("status", ""),
            "priority": s.get("priority", ""),
            "delay_days": s.get("delay_days", 0),
            "disruption_count": len(matched),
            "highest_severity": _highest([m["severity"] for m in matched]),
            "disruptions": matched,
            "requires_cold_chain": s.get("requires_cold_chain", False),
        })
    results.sort(key=lambda x: (_rank(x["highest_severity"]) * -1, -x["delay_days"]))
    return results


def get_disruption_summary():
    """
    Fleet-wide disruption KPI summary for dashboard cards.

    Returns
    -------
    dict
        total_active_disruptions, total_affected_shipments,
        critical_count, high_count, medium_count, low_count
    """
    active_count = sum(
        1 for d in load_disruptions()
        if d.get("status") in ("active", "monitoring")
    )
    affected = get_affected_shipments()
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for s in affected:
        sev = s["highest_severity"].lower()
        if sev in counts:
            counts[sev] += 1
    return {
        "total_active_disruptions": active_count,
        "total_affected_shipments": len(affected),
        "critical_count": counts["critical"],
        "high_count": counts["high"],
        "medium_count": counts["medium"],
        "low_count": counts["low"],
    }
