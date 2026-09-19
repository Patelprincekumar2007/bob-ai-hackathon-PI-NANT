from pydantic import BaseModel, Field
from typing import Optional

class ShipmentFeatures(BaseModel):
    shipment_id: Optional[str] = None
    transport_mode: str = "ocean"
    origin_port: str
    destination_port: str
    carrier: str
    cargo_type: str
    cargo_weight_tons: float
    container_count: int
    distance_km: float
    priority: str
    planned_transit_days: int
    current_delay_days: int
    deadline_pressure: float
    remaining_days_to_deadline: int
    route_changes: int
    disruption_type: str
    disruption_severity: int
    disruption_duration_days: int
    port_congestion_level: int
    cyclone_risk: int
    weather_severity: int
    worker_strike: int
    vessel_failure: int
    customs_delay_days: int
    vessel_capacity_teu: int
    vessel_load_teu: int
    available_capacity_teu: int
    reefer_required: int
    reefer_available: int
    temperature_controlled: int
    temperature_excursions: int
    max_temperature_deviation: float
    cold_chain_severity: int
    carrier_reliability_score: float
    route_risk_score: float
    previous_route_delay_rate: float
    weather_forecast_risk: float

class PredictRequest(BaseModel):
    features: ShipmentFeatures

class PredictResponse(BaseModel):
    success: bool
    prediction: float
    model: dict
