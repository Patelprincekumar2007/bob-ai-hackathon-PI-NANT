"""
api.py — SmartRoute AI FastAPI backend
Run: uvicorn src.api:app --reload --port 8000
"""
import os, sys
_SRC = os.path.dirname(os.path.abspath(__file__))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from core.disruption_detector import load_disruptions, load_shipments, get_disruption_summary, get_shipment_disruptions
from core.risk_engine import get_risk_summary, score_all_shipments, calculate_risk_by_id
from core.route_advisor import recommend_alternative_routes, recommend_all_affected, ROUTE_ALTERNATIVES
from core.fleet_optimizer import get_fleet_summary, get_vehicle_utilisation, recommend_vehicle_for_shipment
from core.cold_chain_monitor import get_cold_chain_summary, get_temperature_alerts, get_shipment_temperature_status, load_temperature_data
from core.watsonx_client import generate_ai_explanation, is_watsonx_configured

from ml.predict_delay import load_trained_model, predict_delay
from ml.schemas import ShipmentFeatures, PredictResponse
from ml.feature_mapper import map_shipment_to_features

app = FastAPI(title="SmartRoute AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Dashboard / summary ──────────────────────────────────────────────────────
@app.get("/api/dashboard")
def dashboard():
    return {
        "risk":  get_risk_summary(),
        "disruptions": get_disruption_summary(),
        "fleet": get_fleet_summary(),
        "cold_chain": get_cold_chain_summary(),
    }

# ── Shipments ────────────────────────────────────────────────────────────────
@app.get("/api/shipments")
def shipments():
    return score_all_shipments()

@app.get("/api/shipments/{sid}")
def shipment_detail(sid: str):
    risk   = calculate_risk_by_id(sid)
    disrs  = get_shipment_disruptions(sid)
    routes = recommend_alternative_routes(sid)
    veh    = recommend_vehicle_for_shipment(sid)
    raw    = next((s for s in load_shipments() if s["id"] == sid), None)
    cold   = get_shipment_temperature_status(sid) if raw and raw.get("requires_cold_chain") else None
    return dict(risk=risk, disruptions=disrs, routes=routes, vehicle=veh, cold=cold, raw=raw)

# ── Disruptions ──────────────────────────────────────────────────────────────
@app.get("/api/disruptions")
def disruptions():
    return load_disruptions()

# ── Fleet ─────────────────────────────────────────────────────────────────────
@app.get("/api/fleet")
def fleet():
    return {
        "summary": get_fleet_summary(),
        "utilisation": get_vehicle_utilisation(),
    }

@app.get("/api/fleet/recommend/{sid}")
def fleet_recommend(sid: str):
    return recommend_vehicle_for_shipment(sid)

# ── Cold chain ────────────────────────────────────────────────────────────────
@app.get("/api/cold-chain")
def cold_chain():
    return {
        "summary": get_cold_chain_summary(),
        "alerts":  get_temperature_alerts(),
    }

@app.get("/api/cold-chain/{sid}")
def cold_chain_shipment(sid: str):
    return get_shipment_temperature_status(sid)

# ── Routes & Dynamic Corridors ───────────────────────────────────────────────
@app.get("/api/routes")
def routes_list():
    return {
        "alternatives_catalog": ROUTE_ALTERNATIVES,
        "affected_recommendations": recommend_all_affected(),
    }

@app.get("/api/routes/recommend/{sid}")
def routes_recommend(sid: str):
    return recommend_alternative_routes(sid)

# ── ML Prediction ────────────────────────────────────────────────────────────
@app.get("/api/ml/health")
def ml_health():
    try:
        pipeline = load_trained_model()
        # Fallback to string if schema isn't present
        features = list(ShipmentFeatures.model_fields.keys())
        return {
            "loaded": True,
            "model_type": type(pipeline).__name__,
            "model_name": "Random Forest Delay Predictor",
            "features": features
        }
    except Exception as e:
        return {"loaded": False, "error": str(e)}

@app.get("/api/ml/features/{sid}")
def ml_features(sid: str):
    raw = next((s for s in load_shipments() if s["id"] == sid), None)
    if not raw:
        return {"error": "Shipment not found"}
    features = map_shipment_to_features(raw)
    return features

@app.post("/api/ml/predict", response_model=PredictResponse)
def ml_predict(features: ShipmentFeatures):
    try:
        data_dict = features.model_dump()
        pred = predict_delay(data_dict)
        return PredictResponse(
            success=True,
            prediction=pred,
            model={"name": "Random Forest", "version": "1.0.0"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return PredictResponse(success=False, prediction=0.0, model={"error": str(e)})

# ── AI ────────────────────────────────────────────────────────────────────────
@app.get("/api/ai/status")
def ai_status():
    return {"configured": is_watsonx_configured()}

@app.post("/api/ai/explain")
def ai_explain(body: dict):
    result = generate_ai_explanation(body.get("prompt",""))
    return result

# ── Serve React frontend (after build) ───────────────────────────────────────
_DIST = os.path.join(os.path.dirname(_SRC), "frontend", "dist")
if os.path.isdir(_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        return FileResponse(os.path.join(_DIST, "index.html"))
