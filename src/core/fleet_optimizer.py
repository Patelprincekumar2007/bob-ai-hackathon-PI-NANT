"""
fleet_optimizer.py
==================
Fleet Utilisation Optimizer for SmartRoute AI.

Loads vehicle data from src/data/vehicles.json and provides:
  - Available vehicle lookup with flexible filtering
  - Idle vehicle detection (available but not assigned to any active shipment)
  - Fleet utilisation metrics
  - Best-vehicle recommendation for a shipment

All data is read from JSON files — no database required.

Public API
----------
    load_vehicles()                          -> list[dict]
    get_available_vehicles(cargo_type, needs_reefer, min_teu, min_weight_kg)
                                             -> list[dict]
    get_idle_vehicles()                      -> list[dict]
    get_fleet_summary()                      -> dict
    get_vehicle_utilisation()                -> dict
    recommend_vehicle_for_shipment(shp_id)   -> dict
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.normpath(os.path.join(_DIR, "..", "data"))


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def load_vehicles():
    """Load all vehicle records from vehicles.json.

    Returns
    -------
    list[dict]  All vehicle records (available and unavailable).
    """
    path = os.path.join(_DATA, "vehicles.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("vehicles", [])
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        logger.error("Could not load vehicles.json: %s", exc)
        return []


def _load_shipments():
    """Load shipments to determine which vessels are actively assigned."""
    path = os.path.join(_DATA, "shipments.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("shipments", [])
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        logger.error("Could not load shipments.json: %s", exc)
        return []


def _assigned_vessel_ids():
    """Return the set of vessel IDs currently assigned to active shipments."""
    active_statuses = {"in_transit", "delayed", "critical_delay", "loading"}
    assigned = set()
    for s in _load_shipments():
        if s.get("status") in active_statuses and s.get("vessel_id"):
            assigned.add(s["vessel_id"])
    return assigned


def _fmt_location(v):
    loc = v.get("current_location") or {}
    city = loc.get("city") or ""
    country = loc.get("country") or ""
    return "%s, %s" % (city, country) if city else "Unknown"


def _vehicle_to_summary(v):
    """Convert a raw vehicle dict to a clean summary dict."""
    return {
        "vehicle_id": v["id"],
        "name": v.get("name", ""),
        "type": v.get("type", ""),
        "carrier": v.get("carrier", ""),
        "status": v.get("status", "unknown"),
        "available_teu": v.get("available_teu", 0),
        "capacity_teu": v.get("capacity_teu", 0),
        "available_weight_kg": v.get("available_weight_kg", 0),
        "available_reefer_slots": v.get("available_reefer_slots", 0),
        "current_location": _fmt_location(v),
        "next_departure": v.get("next_departure"),
        "next_route_id": v.get("next_route_id"),
        "supported_cargo_types": v.get("supported_cargo_types", []),
        "notes": v.get("notes", ""),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_available_vehicles(
    cargo_type=None,
    needs_reefer=False,
    min_teu=0,
    min_weight_kg=0,
):
    """
    Return vehicles that are available and meet the specified requirements.

    Parameters
    ----------
    cargo_type : str | None
        If set, only return vehicles that support this cargo type.
    needs_reefer : bool
        If True, only return vehicles with at least 1 available reefer slot.
    min_teu : int
        Minimum available TEU capacity required.
    min_weight_kg : int
        Minimum available weight capacity required (kg).

    Returns
    -------
    list[dict]  Sorted by available TEU descending. Each dict contains:
        vehicle_id, name, type, carrier, status, available_teu,
        capacity_teu, available_weight_kg, available_reefer_slots,
        current_location, next_departure, next_route_id,
        supported_cargo_types, notes
    """
    results = []
    for v in load_vehicles():
        if v.get("status") != "available":
            continue
        if (v.get("available_teu") or 0) < max(1, min_teu):
            continue
        if (v.get("available_weight_kg") or 0) < min_weight_kg:
            continue
        if needs_reefer and (v.get("available_reefer_slots") or 0) < 1:
            continue
        if cargo_type and cargo_type not in v.get("supported_cargo_types", []):
            continue
        results.append(_vehicle_to_summary(v))

    results.sort(key=lambda x: x["available_teu"], reverse=True)
    return results


def get_idle_vehicles():
    """
    Return vehicles that are available but not assigned to any active shipment.

    A vehicle is 'idle' when:
      - status == "available"
      - its ID does not appear as vessel_id in any in_transit/delayed shipment

    Returns
    -------
    list[dict]  Same structure as get_available_vehicles().
    """
    assigned = _assigned_vessel_ids()
    results = []
    for v in load_vehicles():
        if v.get("status") != "available":
            continue
        if v["id"] not in assigned:
            results.append(_vehicle_to_summary(v))
    results.sort(key=lambda x: x["available_teu"], reverse=True)
    return results


def get_fleet_summary():
    """
    High-level fleet overview for dashboard KPI cards.

    Returns
    -------
    dict
        total, available, unavailable, assigned, idle,
        utilisation_pct (float 0-100), reefer_capable_count,
        available_total_teu, available_total_weight_kg
    """
    vehicles = load_vehicles()
    assigned = _assigned_vessel_ids()
    total = len(vehicles)
    available = sum(1 for v in vehicles if v.get("status") == "available")
    unavailable = total - available
    assigned_count = sum(
        1 for v in vehicles
        if v.get("status") == "available" and v["id"] in assigned
    )
    idle = available - assigned_count
    utilisation_pct = round((assigned_count / total * 100) if total else 0.0, 1)
    reefer_capable = sum(
        1 for v in vehicles
        if v.get("status") == "available" and (v.get("available_reefer_slots") or 0) > 0
    )
    avail_teu = sum(
        v.get("available_teu", 0) for v in vehicles if v.get("status") == "available"
    )
    avail_weight = sum(
        v.get("available_weight_kg", 0) for v in vehicles if v.get("status") == "available"
    )
    return {
        "total": total,
        "available": available,
        "unavailable": unavailable,
        "assigned": assigned_count,
        "idle": idle,
        "utilisation_pct": utilisation_pct,
        "reefer_capable_count": reefer_capable,
        "available_total_teu": avail_teu,
        "available_total_weight_kg": avail_weight,
    }


def get_vehicle_utilisation():
    """
    Per-vehicle utilisation details.

    Returns
    -------
    list[dict]  One entry per vehicle. Each dict contains:
        vehicle_id, name, carrier, status, assigned (bool),
        capacity_teu, used_teu, available_teu,
        load_pct (float 0-100), is_idle (bool)
    """
    assigned = _assigned_vessel_ids()
    result = []
    for v in load_vehicles():
        cap = v.get("capacity_teu") or 0
        used = v.get("current_load_teu") or 0
        avail = v.get("available_teu") or 0
        load_pct = round(used / cap * 100, 1) if cap else 0.0
        is_available = v.get("status") == "available"
        is_assigned = v["id"] in assigned
        result.append({
            "vehicle_id": v["id"],
            "name": v.get("name", ""),
            "carrier": v.get("carrier", ""),
            "status": v.get("status", "unknown"),
            "assigned": is_assigned,
            "capacity_teu": cap,
            "used_teu": used,
            "available_teu": avail,
            "load_pct": load_pct,
            "is_idle": is_available and not is_assigned,
        })
    result.sort(key=lambda x: x["load_pct"], reverse=True)
    return result


def recommend_vehicle_for_shipment(shipment_id):
    """
    Recommend the best available vehicle for a given shipment.

    Selection criteria (in order of priority):
      1. Vehicle must be available and have capacity (TEU + weight).
      2. Vehicle must support the shipment's cargo type.
      3. If cold-chain is required, vehicle must have reefer slots.
      4. Among eligible vehicles, prefer: most available TEU, then most reefer slots.

    Parameters
    ----------
    shipment_id : str   e.g. "SHP-001"

    Returns
    -------
    dict
        shipment_id, recommended_vehicle (dict | None),
        reason (str), alternatives (list[dict])
    """
    # Load shipment
    path = os.path.join(_DATA, "shipments.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            shipments = json.load(f).get("shipments", [])
    except (FileNotFoundError, json.JSONDecodeError):
        shipments = []

    shipment = next((s for s in shipments if s["id"] == shipment_id), None)
    if shipment is None:
        return {
            "shipment_id": shipment_id,
            "recommended_vehicle": None,
            "reason": "Shipment '%s' not found." % shipment_id,
            "alternatives": [],
        }

    cargo_type = shipment.get("cargo_type", "")
    needs_reefer = bool(shipment.get("requires_cold_chain"))
    weight_needed = shipment.get("weight_kg", 0)

    candidates = get_available_vehicles(
        cargo_type=cargo_type,
        needs_reefer=needs_reefer,
        min_teu=1,
        min_weight_kg=weight_needed,
    )

    if not candidates:
        # Relax reefer constraint as fallback message
        reason = (
            "No available vehicle found that supports cargo type '%s'%s "
            "with sufficient capacity (weight: %d kg). "
            "Consider arranging charter or contacting carriers directly."
            % (cargo_type,
               " with reefer capability" if needs_reefer else "",
               weight_needed)
        )
        return {
            "shipment_id": shipment_id,
            "recommended_vehicle": None,
            "reason": reason,
            "alternatives": [],
        }

    # Sort: reefer slots first (if needed), then TEU
    if needs_reefer:
        candidates.sort(key=lambda x: (x["available_reefer_slots"], x["available_teu"]), reverse=True)
    else:
        candidates.sort(key=lambda x: x["available_teu"], reverse=True)

    best = candidates[0]
    reason = (
        "Recommended %s (%s, carrier: %s). "
        "Available capacity: %d TEU / %d kg%s. "
        "Departure: %s from %s."
        % (
            best["name"], best["type"], best["carrier"],
            best["available_teu"], best["available_weight_kg"],
            (", %d reefer slots" % best["available_reefer_slots"]) if needs_reefer else "",
            best["next_departure"] or "TBD",
            best["current_location"],
        )
    )

    return {
        "shipment_id": shipment_id,
        "recommended_vehicle": best,
        "reason": reason,
        "alternatives": candidates[1:4],   # up to 3 alternatives
    }
