"""
risk_engine.py
==============
Deterministic shipment risk scoring (0-100) with four bands:
    LOW (0-24)  MEDIUM (25-49)  HIGH (50-74)  CRITICAL (75-100)

Scoring model
-------------
Factor                        Max pts  Notes
----------------------------  -------  -----------------------------------------
1. Active disruption severity    35    Worst active disruption drives the score
2. Delay days                    25    Non-linear scale
3. Deadline pressure             20    Days remaining until original ETA
4. Shipment priority             15    critical > high > medium > low
5. Cold-chain excursion           5    +5 if an excursion is in temp log

Public API
----------
    calculate_risk(shipment: dict)        -> dict
    calculate_risk_by_id(shipment_id)     -> dict | None
    score_all_shipments()                 -> list[dict]   (sorted highest first)
    get_risk_summary()                    -> dict
"""

import json
import logging
import os
from datetime import date, datetime

from .disruption_detector import get_shipment_disruptions, load_shipments

logger = logging.getLogger(__name__)

_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.normpath(os.path.join(_DIR, "..", "data"))

# ---------------------------------------------------------------------------
# Classification bands
# ---------------------------------------------------------------------------
_BANDS = [("CRITICAL", 75), ("HIGH", 50), ("MEDIUM", 25), ("LOW", 0)]


def _classify(score):
    for label, threshold in _BANDS:
        if score >= threshold:
            return label
    return "LOW"


# ---------------------------------------------------------------------------
# Per-factor scoring tables
# ---------------------------------------------------------------------------
_SEV_PTS = {"critical": 35, "high": 25, "medium": 15, "low": 8, "unknown": 0}
_PRI_PTS = {"critical": 15, "high": 10, "medium": 5, "low": 0}


def _score_disruption(disruptions):
    """(pts, explanation) for disruption severity factor."""
    if not disruptions:
        return 0, "No active disruptions (0/35 pts)."
    worst = disruptions[0]   # already sorted worst-first by detector
    sev = (worst.get("severity") or "unknown").lower()
    pts = _SEV_PTS.get(sev, 0)
    extra = " (%d total)" % len(disruptions) if len(disruptions) > 1 else ""
    return pts, "Disruption severity %s%s -> %d/35 pts. (%s)" % (
        sev.upper(), extra, pts, worst.get("title", ""))


def _score_delay(delay_days):
    """(pts, explanation) for delay factor."""
    d = max(0, int(delay_days or 0))
    if d == 0:
        pts = 0
    elif d <= 2:
        pts = 5
    elif d <= 5:
        pts = 10
    elif d <= 9:
        pts = 17
    elif d <= 13:
        pts = 22
    else:
        pts = 25
    return pts, "Delay %d day(s) -> %d/25 pts." % (d, pts)


def _score_deadline(shipment):
    """(pts, explanation) for deadline pressure factor."""
    eta_str = shipment.get("original_eta") or shipment.get("current_eta")
    if not eta_str:
        return 5, "ETA unknown – default pressure 5/20 pts."
    try:
        eta = datetime.strptime(eta_str, "%Y-%m-%d").date()
    except ValueError:
        return 5, "ETA unparseable ('%s') – default 5/20 pts." % eta_str
    remaining = (eta - date.today()).days
    if remaining < 0:
        pts, label = 20, "ETA already passed by %d day(s)" % abs(remaining)
    elif remaining <= 3:
        pts, label = 18, "ETA in %d day(s) – critical" % remaining
    elif remaining <= 7:
        pts, label = 14, "ETA in %d day(s) – high pressure" % remaining
    elif remaining <= 14:
        pts, label = 8, "ETA in %d day(s) – moderate" % remaining
    elif remaining <= 30:
        pts, label = 4, "ETA in %d day(s) – low pressure" % remaining
    else:
        pts, label = 0, "ETA in %d day(s) – minimal pressure" % remaining
    return pts, "%s -> %d/20 pts." % (label, pts)


def _score_priority(shipment):
    """(pts, explanation) for priority factor."""
    pri = (shipment.get("priority") or "low").lower()
    pts = _PRI_PTS.get(pri, 0)
    return pts, "Priority %s -> %d/15 pts." % (pri.upper(), pts)


def _score_cold_chain(shipment):
    """(pts, explanation) for cold-chain excursion factor (+5 if excursion found)."""
    if not shipment.get("requires_cold_chain"):
        return 0, "Cold-chain not required (0/5 pts)."
    try:
        path = os.path.join(_DATA, "temperature_readings.json")
        with open(path, "r", encoding="utf-8") as f:
            entries = json.load(f).get("temperature_readings", [])
        for entry in entries:
            if entry.get("shipment_id") != shipment["id"]:
                continue
            for r in entry.get("readings", []):
                if r.get("status") == "excursion":
                    return 5, "Temperature excursion detected in cold-chain log -> 5/5 pts."
        return 0, "Cold-chain required; no excursions in log (0/5 pts)."
    except Exception as exc:   # noqa: BLE001
        logger.warning("Could not read temperature data: %s", exc)
        return 0, "Temperature data unavailable (0/5 pts)."


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def calculate_risk(shipment):
    """
    Calculate risk score and classification for one shipment dict.

    Parameters
    ----------
    shipment : dict   A record from shipments.json (must have 'id').

    Returns
    -------
    dict
        shipment_id, score (int 0-100), classification (str),
        explanation (str), factor_breakdown (dict), disruptions (list)
    """
    shp_id = shipment.get("id", "UNKNOWN")
    disruptions = get_shipment_disruptions(shp_id)

    d_pts, d_msg = _score_disruption(disruptions)
    l_pts, l_msg = _score_delay(shipment.get("delay_days", 0))
    e_pts, e_msg = _score_deadline(shipment)
    p_pts, p_msg = _score_priority(shipment)
    c_pts, c_msg = _score_cold_chain(shipment)

    total = min(d_pts + l_pts + e_pts + p_pts + c_pts, 100)
    classification = _classify(total)

    explanation = (
        "Risk score: %d/100 — %s\n\n"
        "Contributing factors:\n"
        "  Disruption severity : %2d/35  %s\n"
        "  Current delay       : %2d/25  %s\n"
        "  Deadline pressure   : %2d/20  %s\n"
        "  Shipment priority   : %2d/15  %s\n"
        "  Cold-chain status   : %2d/5   %s"
    ) % (total, classification,
         d_pts, d_msg, l_pts, l_msg, e_pts, e_msg, p_pts, p_msg, c_pts, c_msg)

    return {
        "shipment_id": shp_id,
        "score": total,
        "classification": classification,
        "explanation": explanation,
        "factor_breakdown": {
            "disruption_severity": d_pts,
            "delay": l_pts,
            "deadline_pressure": e_pts,
            "priority": p_pts,
            "cold_chain": c_pts,
        },
        "disruptions": disruptions,
    }


def calculate_risk_by_id(shipment_id):
    """
    Calculate risk for a shipment looked up by ID.

    Returns dict (same as calculate_risk) or None if not found.
    """
    for s in load_shipments():
        if s["id"] == shipment_id:
            return calculate_risk(s)
    logger.warning("Shipment '%s' not found.", shipment_id)
    return None


def score_all_shipments():
    """
    Score every shipment; return list sorted by score descending.

    Each item is the calculate_risk() dict enriched with:
    description, carrier, origin, destination, status, priority,
    delay_days, requires_cold_chain.
    """
    results = []
    for s in load_shipments():
        r = calculate_risk(s)
        orig = s.get("origin", {})
        dest = s.get("destination", {})
        r.update({
            "description": s.get("description", ""),
            "carrier": s.get("carrier", ""),
            "origin": "%s, %s" % (orig.get("city", ""), orig.get("country", "")),
            "destination": "%s, %s" % (dest.get("city", ""), dest.get("country", "")),
            "status": s.get("status", ""),
            "priority": s.get("priority", ""),
            "delay_days": s.get("delay_days", 0),
            "requires_cold_chain": s.get("requires_cold_chain", False),
        })
        results.append(r)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def get_risk_summary():
    """
    Fleet-wide risk KPI for dashboard cards.

    Returns
    -------
    dict
        total_shipments, critical_count, high_count,
        medium_count, low_count, average_score
    """
    scores = score_all_shipments()
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for s in scores:
        counts[s["classification"]] += 1
    avg = round(sum(s["score"] for s in scores) / len(scores), 1) if scores else 0.0
    return {
        "total_shipments": len(scores),
        "critical_count": counts["CRITICAL"],
        "high_count": counts["HIGH"],
        "medium_count": counts["MEDIUM"],
        "low_count": counts["LOW"],
        "average_score": avg,
    }
