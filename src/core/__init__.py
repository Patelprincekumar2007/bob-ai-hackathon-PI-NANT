"""
SmartRoute AI — core package
Import shortcuts for Person 2 (MCP server) and Person 3 (Streamlit UI).

Part 1:
    from core.disruption_detector import get_affected_shipments, get_shipment_disruptions
    from core.risk_engine import calculate_risk_by_id, score_all_shipments, get_risk_summary
    from core.route_advisor import recommend_alternative_routes, recommend_all_affected
    from core.watsonx_client import generate_ai_explanation, is_watsonx_configured

Part 2:
    from core.fleet_optimizer import (
        get_available_vehicles, get_idle_vehicles,
        get_fleet_summary, get_vehicle_utilisation,
        recommend_vehicle_for_shipment,
    )
    from core.cold_chain_monitor import (
        get_temperature_alerts, get_shipment_temperature_status,
        get_cold_chain_summary, get_temperature_risk,
    )
"""
