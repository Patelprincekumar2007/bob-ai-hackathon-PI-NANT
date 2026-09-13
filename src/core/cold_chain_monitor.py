"""
cold_chain_monitor.py
=====================
Cold Chain Temperature Monitor for SmartRoute AI.

Reads temperature log data from src/data/temperature_readings.json and:
  - Detects temperature excursions (readings outside the safe range)
  - Classifies excursion severity: NORMAL / WARNING / CRITICAL
  - Calculates a cold-chain risk score (0-100)
  - Returns structured data ready for dashboard display

Severity thresholds (configurable at module level)
---------------------------------------------------
    NORMAL   — all readings within bounds
    WARNING  — 1-2 excursion readings OR deviation <= WARNING_DELTA_C
    CRITICAL — 3+ excursion readings OR deviation > WARNING_DELTA_C

Public API
----------
    load_temperature_data()                       -> list[dict]
    get_temperature_alerts(shipment_id=None)      -> list[dict]
    get_shipment_temperature_status(shipment_id)  -> dict
    get_cold_chain_summary()                      -> dict
    get_temperature_risk(shipment_id)             -> dict
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.normpath(os.path.join(_DIR, "..", "data"))

# ---------------------------------------------------------------------------
# Configurable thresholds
# ---------------------------------------------------------------------------
# A deviation above WARNING_DELTA_C from the nearest bound triggers CRITICAL.
# Set to 1.0 so that a >1 C excursion (common in real pharma/produce) is CRITICAL.
WARNING_DELTA_C = 1.0
# Max cold-chain risk score (out of 100).  Scaled by excursion count + deviation.
MAX_COLD_RISK = 100


# ---------------------------------------------------------------------------
# Data loader
# ---------------------------------------------------------------------------

def load_temperature_data():
    """Load all temperature reading entries from temperature_readings.json.

    Returns
    -------
    list[dict]  One entry per shipment tracked, each containing a list of
                readings.  Returns [] on file error.
    """
    path = os.path.join(_DATA, "temperature_readings.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("temperature_readings", [])
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        logger.error("Could not load temperature_readings.json: %s", exc)
        return []


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _excursion_info(readings, temp_min, temp_max):
    """
    Analyse a list of reading dicts against [temp_min, temp_max].

    Returns
    -------
    tuple: (excursion_count, max_deviation_c, latest_temp, min_temp, max_temp)
        excursion_count  — number of readings flagged as 'excursion' or
                           outside bounds
        max_deviation_c  — largest absolute deviation from the nearest bound
        latest_temp      — temperature_c of the most recent reading
        min_temp         — lowest temperature_c seen
        max_temp         — highest temperature_c seen
    """
    excursion_count = 0
    max_dev = 0.0
    temps = []

    for r in readings:
        t = r.get("temperature_c")
        if t is None:
            continue
        temps.append(t)
        status = r.get("status", "normal")
        # Count as excursion if flagged OR actually outside range
        out_of_range = (
            (temp_min is not None and t < temp_min) or
            (temp_max is not None and t > temp_max)
        )
        if status == "excursion" or out_of_range:
            excursion_count += 1
            # Calculate deviation from nearest bound
            if temp_max is not None and t > temp_max:
                dev = t - temp_max
            elif temp_min is not None and t < temp_min:
                dev = temp_min - t
            else:
                dev = 0.0
            max_dev = max(max_dev, dev)

    latest = temps[-1] if temps else None
    min_t = min(temps) if temps else None
    max_t = max(temps) if temps else None
    return excursion_count, max_dev, latest, min_t, max_t


def _classify_severity(excursion_count, max_deviation_c):
    """Return NORMAL / WARNING / CRITICAL based on excursion count and deviation."""
    if excursion_count == 0:
        return "NORMAL"
    if excursion_count >= 3 or max_deviation_c > WARNING_DELTA_C:
        return "CRITICAL"
    return "WARNING"


def _cold_risk_score(excursion_count, max_deviation_c, total_readings):
    """
    Deterministic cold-chain risk score 0-100.

    Score formula:
      base  = min(excursion_count / total_readings * 60, 60)   — frequency component
      bonus = min(max_deviation_c / WARNING_DELTA_C * 40, 40)  — deviation component
    """
    if total_readings == 0 or excursion_count == 0:
        return 0
    freq_score = min(excursion_count / total_readings * 60, 60)
    dev_score = min(max_deviation_c / WARNING_DELTA_C * 40, 40)
    return round(min(freq_score + dev_score, MAX_COLD_RISK))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_shipment_temperature_status(shipment_id):
    """
    Full temperature status for a single cold-chain shipment.

    Parameters
    ----------
    shipment_id : str   e.g. "SHP-002"

    Returns
    -------
    dict
        shipment_id, cargo_type,
        required_temp_min_c, required_temp_max_c,
        latest_temp_c, min_observed_c, max_observed_c,
        reading_count, excursion_count,
        excursion_detected (bool), excursion_severity (str),
        cold_chain_risk_score (int 0-100),
        explanation (str),
        readings (list[dict])   — all raw readings

    If shipment_id has no temperature data, returns a dict with
    excursion_detected=False and a descriptive explanation.
    """
    entries = load_temperature_data()
    entry = next((e for e in entries if e.get("shipment_id") == shipment_id), None)

    if entry is None:
        return {
            "shipment_id": shipment_id,
            "cargo_type": "unknown",
            "required_temp_min_c": None,
            "required_temp_max_c": None,
            "latest_temp_c": None,
            "min_observed_c": None,
            "max_observed_c": None,
            "reading_count": 0,
            "excursion_count": 0,
            "excursion_detected": False,
            "excursion_severity": "NORMAL",
            "cold_chain_risk_score": 0,
            "explanation": "No temperature data found for shipment %s." % shipment_id,
            "readings": [],
        }

    temp_min = entry.get("required_temp_min_c")
    temp_max = entry.get("required_temp_max_c")
    readings = entry.get("readings", [])
    total = len(readings)

    exc_count, max_dev, latest, min_t, max_t = _excursion_info(readings, temp_min, temp_max)
    severity = _classify_severity(exc_count, max_dev)
    risk_score = _cold_risk_score(exc_count, max_dev, total)

    if exc_count == 0:
        explanation = (
            "All %d reading(s) within safe range [%s, %s] C. "
            "Latest: %.1f C. Cold-chain risk: %d/100."
            % (total, temp_min, temp_max, latest or 0, risk_score)
        )
    else:
        explanation = (
            "%d excursion(s) detected in %d reading(s). "
            "Max deviation from safe range: %.1f C. "
            "Severity: %s. "
            "Safe range: [%s, %s] C. Latest: %.1f C. Cold-chain risk: %d/100."
            % (exc_count, total, max_dev, severity,
               temp_min, temp_max, latest or 0, risk_score)
        )

    return {
        "shipment_id": shipment_id,
        "cargo_type": entry.get("cargo_type", ""),
        "required_temp_min_c": temp_min,
        "required_temp_max_c": temp_max,
        "latest_temp_c": latest,
        "min_observed_c": min_t,
        "max_observed_c": max_t,
        "reading_count": total,
        "excursion_count": exc_count,
        "excursion_detected": exc_count > 0,
        "excursion_severity": severity,
        "cold_chain_risk_score": risk_score,
        "explanation": explanation,
        "readings": readings,
    }


def get_temperature_alerts(shipment_id=None):
    """
    Return temperature alerts for shipments with at least one excursion.

    Parameters
    ----------
    shipment_id : str | None
        If provided, return alerts for that shipment only.
        If None, return alerts for all shipments with excursions.

    Returns
    -------
    list[dict]  Sorted by cold_chain_risk_score descending. Each dict:
        shipment_id, cargo_type, excursion_severity,
        excursion_count, cold_chain_risk_score,
        latest_temp_c, required_temp_min_c, required_temp_max_c,
        explanation
    """
    entries = load_temperature_data()

    if shipment_id:
        entries = [e for e in entries if e.get("shipment_id") == shipment_id]

    alerts = []
    for entry in entries:
        sid = entry.get("shipment_id", "")
        status = get_shipment_temperature_status(sid)
        if not status["excursion_detected"]:
            continue
        alerts.append({
            "shipment_id": sid,
            "cargo_type": status["cargo_type"],
            "excursion_severity": status["excursion_severity"],
            "excursion_count": status["excursion_count"],
            "cold_chain_risk_score": status["cold_chain_risk_score"],
            "latest_temp_c": status["latest_temp_c"],
            "required_temp_min_c": status["required_temp_min_c"],
            "required_temp_max_c": status["required_temp_max_c"],
            "explanation": status["explanation"],
        })

    alerts.sort(key=lambda x: x["cold_chain_risk_score"], reverse=True)
    return alerts


def get_cold_chain_summary():
    """
    Fleet-wide cold-chain health summary for dashboard KPI cards.

    Returns
    -------
    dict
        total_tracked, normal_count, warning_count, critical_count,
        shipments_with_excursions, average_risk_score
    """
    entries = load_temperature_data()
    counts = {"NORMAL": 0, "WARNING": 0, "CRITICAL": 0}
    risk_scores = []
    exc_shipments = 0

    for entry in entries:
        sid = entry.get("shipment_id", "")
        status = get_shipment_temperature_status(sid)
        sev = status["excursion_severity"]
        counts[sev] = counts.get(sev, 0) + 1
        risk_scores.append(status["cold_chain_risk_score"])
        if status["excursion_detected"]:
            exc_shipments += 1

    avg = round(sum(risk_scores) / len(risk_scores), 1) if risk_scores else 0.0
    return {
        "total_tracked": len(entries),
        "normal_count": counts["NORMAL"],
        "warning_count": counts["WARNING"],
        "critical_count": counts["CRITICAL"],
        "shipments_with_excursions": exc_shipments,
        "average_risk_score": avg,
    }


def get_temperature_risk(shipment_id):
    """
    Convenience wrapper returning just the risk score and severity for a shipment.

    Returns
    -------
    dict
        shipment_id, cold_chain_risk_score (int), excursion_severity (str),
        excursion_detected (bool), explanation (str)
    """
    status = get_shipment_temperature_status(shipment_id)
    return {
        "shipment_id": shipment_id,
        "cold_chain_risk_score": status["cold_chain_risk_score"],
        "excursion_severity": status["excursion_severity"],
        "excursion_detected": status["excursion_detected"],
        "explanation": status["explanation"],
    }
