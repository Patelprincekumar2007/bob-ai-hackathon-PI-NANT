from src.core.disruption_detector import get_shipment_disruptions
from src.core.fleet_optimizer import recommend_vehicle_for_shipment
from src.core.cold_chain_monitor import get_shipment_temperature_status

def map_shipment_to_features(raw_shipment: dict) -> dict:
    """
    Maps a raw SmartRoute shipment dictionary and its context to the 36-feature
    format expected by the delay prediction model.
    """
    sid = raw_shipment.get("id", "")
    
    # Base shipment info
    origin = raw_shipment.get("origin", {}).get("city", "Shanghai")
    dest = raw_shipment.get("destination", {}).get("city", "Los Angeles")
    carrier = raw_shipment.get("carrier", "MaerskLine")
    cargo_type = raw_shipment.get("cargo_type", "general")
    weight_kg = raw_shipment.get("weight_kg", 20000)
    cargo_weight_tons = weight_kg / 1000.0
    container_count = max(1, int(raw_shipment.get("volume_m3", 30) / 30)) # Rough TEU estimate
    priority = raw_shipment.get("priority", "medium")
    
    # Time info
    planned_transit = 30 # Mock default
    current_delay_days = raw_shipment.get("delay_days", 0)
    remaining_days = 15 # Mock default
    deadline_pressure = 5.0 # Mid pressure
    
    # Route info
    distance_km = 8000.0 # Mock default
    route_changes = 0
    route_risk_score = 50.0
    prev_route_delay_rate = 0.15
    
    # Disruptions context
    disruptions = get_shipment_disruptions(sid)
    disruption_type = "none"
    disruption_severity = 0
    disruption_duration = 0
    port_congestion = 2
    cyclone = 0
    weather = 2
    strike = 0
    vessel_fail = 0
    customs = 0
    
    if disruptions:
        d = disruptions[0] # Take most severe
        d_title = d.get("title", "").lower()
        if "cyclone" in d_title or "weather" in d_title:
            disruption_type = "weather"
            cyclone = 1 if "cyclone" in d_title else 0
            weather = 8
        elif "strike" in d_title:
            disruption_type = "strike"
            strike = 1
        elif "congestion" in d_title:
            disruption_type = "port_congestion"
            port_congestion = 8
        elif "engine" in d_title or "vessel" in d_title:
            disruption_type = "vessel_failure"
            vessel_fail = 1
        
        disruption_severity = 25 if d.get("severity") == "critical" else 15
        disruption_duration = d.get("estimated_delay_days", 3)

    # Fleet context
    veh = recommend_vehicle_for_shipment(sid)
    vessel_cap = 10000
    vessel_load = 8000
    avail_cap = 2000
    if veh:
        vessel_cap = veh.get("capacity_teu", 10000)
        avail_cap = veh.get("available_teu", 2000)
        vessel_load = vessel_cap - avail_cap

    # Cold chain context
    cold = get_shipment_temperature_status(sid)
    reefer_req = 1 if raw_shipment.get("requires_cold_chain") else 0
    reefer_avail = 1
    temp_ctrl = 1 if reefer_req else 0
    temp_exc = 0
    max_dev = 0.0
    cold_sev = 0
    if cold:
        temp_exc = cold.get("excursion_count", 0)
        max_dev = 2.5 if temp_exc > 0 else 0.0
        cold_sev = 8 if cold.get("excursion_severity") == "CRITICAL" else 0

    features = {
        "shipment_id": sid,
        "transport_mode": "ocean",
        "origin_port": origin,
        "destination_port": dest,
        "carrier": carrier,
        "cargo_type": cargo_type,
        "cargo_weight_tons": cargo_weight_tons,
        "container_count": container_count,
        "distance_km": distance_km,
        "priority": priority,
        "planned_transit_days": planned_transit,
        "current_delay_days": current_delay_days,
        "deadline_pressure": deadline_pressure,
        "remaining_days_to_deadline": remaining_days,
        "route_changes": route_changes,
        "disruption_type": disruption_type,
        "disruption_severity": disruption_severity,
        "disruption_duration_days": disruption_duration,
        "port_congestion_level": port_congestion,
        "cyclone_risk": cyclone,
        "weather_severity": weather,
        "worker_strike": strike,
        "vessel_failure": vessel_fail,
        "customs_delay_days": customs,
        "vessel_capacity_teu": vessel_cap,
        "vessel_load_teu": vessel_load,
        "available_capacity_teu": avail_cap,
        "reefer_required": reefer_req,
        "reefer_available": reefer_avail,
        "temperature_controlled": temp_ctrl,
        "temperature_excursions": temp_exc,
        "max_temperature_deviation": max_dev,
        "cold_chain_severity": cold_sev,
        "carrier_reliability_score": 85.0,
        "route_risk_score": route_risk_score,
        "previous_route_delay_rate": prev_route_delay_rate,
        "weather_forecast_risk": 3.0
    }
    return features
