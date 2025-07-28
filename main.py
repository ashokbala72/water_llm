from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from water_llm_engine_2 import (
    overflow_control,
    run_all_analyses,
    generate_contextual_advisory,
    storm_response_coordinator
)

app = FastAPI(title="Water LLM Engine API")

# -----------------------------
# 🔧 Request Models
# -----------------------------
class LocationInput(BaseModel):
    location: str = 'London'

class RiskInput(BaseModel):
    risk_level: str

class ReportInput(BaseModel):
    location: str
    rainfall_mm: float
    risk_level: str

class ForecastInput(BaseModel):
    location: str = 'London'
    horizon_days: Optional[int] = 3

# -----------------------------
# 🔁 Core Endpoints
# -----------------------------
@app.post("/overflow-control")
def api_overflow_control(input: LocationInput):
    return overflow_control(input.location)

@app.post("/run-analyses")
def api_run_all_analyses(input: LocationInput):
    return run_all_analyses(input.location)

@app.post("/load-balance")
def api_load_balance(input: LocationInput):
    return load_balance_tanks(input.location)

@app.post("/forecast")
def api_forecast_weather(input: ForecastInput):
    return forecast_weather_with_gpt(input.location, input.horizon_days)

@app.post("/storm-response")
def api_storm_response(input: LocationInput):
    return storm_response_coordinator(input.location)

@app.post("/inputs")
def api_inputs(input: LocationInput):
    return get_real_time_inputs(input.location)

@app.post("/prediction-compare")
def api_prediction_comparison(input: LocationInput):
    return compare_predictions_with_actuals(input.location)

@app.post("/check-assets")
def api_check_assets(input: LocationInput):
    return check_asset_availability(input.location)

@app.post("/infra-upgrades")
def api_infra_upgrades(input: LocationInput):
    return recommend_infrastructure_upgrades(input.location)

@app.post("/risk-advice")
def api_risk_action(input: RiskInput):
    return suggest_action_for_risk(input.risk_level)

@app.post("/regulatory-report")
def api_regulatory_report(input: ReportInput):
    return generate_regulatory_report(input.location, input.rainfall_mm, input.risk_level)

@app.post("/contextual-advisory")
def api_contextual_advisory(input: LocationInput):
    return generate_contextual_advisory(input.location)

@app.post("/river-severity")
def api_river_severity(input: LocationInput):
    return get_river_impact_severity(input.location)

# -----------------------------
# 🧾 Utilities
# -----------------------------
@app.get("/interventions")
def api_get_intervention_logs():
    return get_logged_interventions()

@app.get("/parameters")
def api_parameters():
    return get_parameter_descriptions()
