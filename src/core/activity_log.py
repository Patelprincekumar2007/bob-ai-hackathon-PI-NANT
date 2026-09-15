"""
activity_log.py — NEW FILE (SmartRoute AI additive extension)
=============================================================
Persists operator review flags per shipment to src/data/review_flags.json.

Never modifies any existing data file (shipments.json, disruptions.json,
vehicles.json, temperature_readings.json).

Public API
----------
    load_review_flags()                       -> dict[shipment_id, dict]
    is_reviewed(shipment_id)                  -> bool
    mark_reviewed(shipment_id, reviewer="ops") -> None
    unmark_reviewed(shipment_id)              -> None
    get_review_flag(shipment_id)              -> dict | None

Data shape in review_flags.json
--------------------------------
{
  "review_flags": {
    "SHP-001": {"reviewed": true, "reviewer": "ops", "timestamp": "2026-09-13T17:00:00"}
  }
}
"""

import json
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_DIR = os.path.dirname(os.path.abspath(__file__))
_FLAGS_PATH = os.path.normpath(os.path.join(_DIR, "..", "data", "review_flags.json"))


def _load_raw() -> dict:
    """Load raw JSON from disk; return empty structure on any error."""
    try:
        with open(_FLAGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict) or "review_flags" not in data:
                return {"review_flags": {}}
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"review_flags": {}}


def _save_raw(data: dict) -> None:
    """Write data to disk; logs error and silently continues on failure."""
    try:
        os.makedirs(os.path.dirname(_FLAGS_PATH), exist_ok=True)
        with open(_FLAGS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError as exc:
        logger.error("Could not write review_flags.json: %s", exc)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_review_flags() -> dict:
    """
    Return all review flags as a dict keyed by shipment_id.

    Returns
    -------
    dict[str, dict]   e.g. {"SHP-001": {"reviewed": True, "reviewer": "ops", "timestamp": "..."}}
    """
    return _load_raw().get("review_flags", {})


def is_reviewed(shipment_id: str) -> bool:
    """Return True if the shipment has been marked reviewed."""
    flags = load_review_flags()
    return bool(flags.get(shipment_id, {}).get("reviewed", False))


def get_review_flag(shipment_id: str) -> dict | None:
    """Return the review flag dict for a shipment, or None if not flagged."""
    return load_review_flags().get(shipment_id)


def mark_reviewed(shipment_id: str, reviewer: str = "ops") -> None:
    """
    Mark a shipment as reviewed by ops.

    Parameters
    ----------
    shipment_id : str   e.g. "SHP-001"
    reviewer    : str   Reviewer label, defaults to "ops"
    """
    data = _load_raw()
    data["review_flags"][shipment_id] = {
        "reviewed": True,
        "reviewer": reviewer,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    _save_raw(data)
    logger.info("Shipment %s marked reviewed by %s.", shipment_id, reviewer)


def unmark_reviewed(shipment_id: str) -> None:
    """Remove the review flag for a shipment."""
    data = _load_raw()
    if shipment_id in data.get("review_flags", {}):
        del data["review_flags"][shipment_id]
        _save_raw(data)
        logger.info("Review flag cleared for shipment %s.", shipment_id)
