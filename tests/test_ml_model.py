"""
test_ml_model.py — Pytest suite for SmartRoute AI ML Delay Prediction Component
================================================================================
Verifies model serialization, loading, standalone prediction function, schema compliance,
and non-leakage rules.
"""

import os
import sys
import numpy as np
import pandas as pd
import pytest

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.join(_TESTS_DIR, "..", "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from ml.predict_delay import get_model_path, load_trained_model, predict_delay


@pytest.fixture
def sample_shipment_dict():
    """Return a representative single shipment feature dictionary."""
    return {
        "shipment_id": "SHP-TEST-9999",
        "transport_mode": "ocean",
        "origin_port": "Shanghai",
        "destination_port": "Los Angeles",
        "carrier": "Maersk",
        "cargo_type": "electronics",
        "cargo_weight_tons": 50.0,
        "container_count": 10,
        "distance_km": 10000.0,
        "priority": "high",
        "planned_transit_days": 20,
        "current_delay_days": 3,
        "deadline_pressure": 6.0,
        "remaining_days_to_deadline": 5,
        "route_changes": 1,
        "disruption_type": "port_congestion",
        "disruption_severity": 20,
        "disruption_duration_days": 5,
        "port_congestion_level": 7,
        "cyclone_risk": 0,
        "weather_severity": 3,
        "worker_strike": 0,
        "vessel_failure": 0,
        "customs_delay_days": 1,
        "vessel_capacity_teu": 10000,
        "vessel_load_teu": 8500,
        "available_capacity_teu": 1500,
        "reefer_required": 0,
        "reefer_available": 1,
        "temperature_controlled": 0,
        "temperature_excursions": 0,
        "max_temperature_deviation": 0.0,
        "cold_chain_severity": 0,
        "carrier_reliability_score": 90.0,
        "route_risk_score": 50.0,
        "previous_route_delay_rate": 0.20,
        "weather_forecast_risk": 4.0,
    }


def test_model_file_exists():
    """Test 1: Model binary file exists at expected path."""
    model_path = get_model_path()
    assert os.path.exists(model_path), f"Model file missing at: {model_path}"
    assert os.path.getsize(model_path) > 1000, "Model file is empty or corrupted."


def test_model_can_be_loaded():
    """Test 2: Pipeline can be loaded without error."""
    pipeline = load_trained_model()
    assert pipeline is not None
    assert hasattr(pipeline, "predict"), "Loaded object missing predict method."


def test_predict_delay_returns_numeric(sample_shipment_dict):
    """Test 3 & 4: predict_delay returns numeric float."""
    result = predict_delay(sample_shipment_dict)
    assert isinstance(result, (float, int))


def test_predict_delay_is_not_nan(sample_shipment_dict):
    """Test 5: Prediction is not NaN or infinity."""
    result = predict_delay(sample_shipment_dict)
    assert not np.isnan(result)
    assert not np.isinf(result)


def test_predict_delay_is_non_negative(sample_shipment_dict):
    """Test 6: Delay prediction is >= 0."""
    result = predict_delay(sample_shipment_dict)
    assert result >= 0.0


def test_predict_delay_handles_dataframe_input(sample_shipment_dict):
    """Test 7: Function accepts pandas DataFrame input."""
    df_sample = pd.DataFrame([sample_shipment_dict])
    result = predict_delay(df_sample)
    assert isinstance(result, float)
    assert result >= 0.0


def test_model_does_not_leak_shipment_id_or_actual_delay(sample_shipment_dict):
    """Test 8: Function safely strips shipment_id and actual_delay_days if passed."""
    leakage_dict = sample_shipment_dict.copy()
    leakage_dict["shipment_id"] = "LEAKED-ID"
    leakage_dict["actual_delay_days"] = 999.0  # target leakage attempt

    result_clean = predict_delay(sample_shipment_dict)
    result_leakage = predict_delay(leakage_dict)

    # Predictions must match regardless of shipment_id or target column input
    assert abs(result_clean - result_leakage) < 1e-5


def test_prediction_increases_with_higher_disruption_severity(sample_shipment_dict):
    """Test 9: Domain check - higher disruption duration & severity increases predicted delay."""
    low_disruption = sample_shipment_dict.copy()
    low_disruption["disruption_severity"] = 0
    low_disruption["disruption_duration_days"] = 0

    high_disruption = sample_shipment_dict.copy()
    high_disruption["disruption_severity"] = 35
    high_disruption["disruption_duration_days"] = 12

    pred_low = predict_delay(low_disruption)
    pred_high = predict_delay(high_disruption)

    assert pred_high > pred_low, f"High disruption delay ({pred_high}) should be greater than low disruption delay ({pred_low})"
