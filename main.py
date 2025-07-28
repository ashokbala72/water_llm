# main.py
from fastapi import FastAPI, Query, Body
from pydantic import BaseModel
from typing import Optional
from Water_llm_ENGINE_WITH_CONTEXTUAL_ADVISORY import *
try:
    import openai
    print("✅ OpenAI module loaded successfully.")
except ModuleNotFoundError as e:
    print(f"❌ Module load failed: {e}")

app = FastAPI(title="Water LLM Stormwater Engine API")

class AnomalyInput(BaseModel):
    tank_fill_percent: float
    inflow_rate_lps: float

class OverflowInput(BaseModel):
    rainfall_mm: float
    tank_fill_percent: float

class ComplianceInput(BaseModel):
    rainfall_mm: float
    overflow_triggered: bool

class ReportInput(BaseModel):
    location: str
    rainfall_mm: float
    risk_level: str

class AlertInput(BaseModel):
    message: str

class SuggestionInput(BaseModel):
    risk_level: str

@app.get("/get_integration_config")
def api_get_integration_config(location: str = "London"):
    return get_integration_config(location)

@app.get("/actuate_asset")
def api_actuate_asset(command: str, location: str = "London"):
    return actuate_asset(command, location)

@app.get("/overflow_control")
def api_overflow_control(location: str = "London"):
    return overflow_control(location)

@app.get("/storm_response")
def api_storm_response(location: str = "London"):
    return storm_response_coordinator(location)

@app.get("/run_all_analyses")
def api_run_all_analyses(location: str = "London"):
    return run_all_analyses(location)

@app.get("/forecast_weather")
def api_forecast_weather(location: str = "London", horizon_days: int = 3):
    return forecast_weather_with_gpt(location, horizon_days)

@app.get("/load_balance_tanks")
def api_load_balance_tanks(location: str = "London"):
    return load_balance_tanks(location)

@app.get("/check_assets")
def api_check_assets(location: str = "London"):
    return check_asset_availability(location)

@app.get("/contextual_advisory")
def api_contextual_advisory(location: str = "London"):
    return generate_contextual_advisory(location)

@app.get("/compare_predictions")
def api_compare_predictions(location: str = "London"):
    return compare_predictions_with_actuals(location)

@app.post("/predict_overflow")
def api_predict_overflow_post(data: OverflowInput):
    return predict_overflow(data.rainfall_mm, data.tank_fill_percent)

@app.post("/dynamic_control_advice")
def api_dynamic_control_advice_post(tank_fill: float = Body(...)):
    return dynamic_control_advice(tank_fill)

@app.post("/detect_anomalies")
def api_detect_anomalies_post(data: AnomalyInput):
    return detect_anomalies(data.dict())

@app.post("/compliance_check")
def api_compliance_check_post(data: ComplianceInput):
    return compliance_check(data.rainfall_mm, data.overflow_triggered)

@app.post("/regulatory_report")
def api_regulatory_report_post(data: ReportInput):
    return generate_regulatory_report(data.location, data.rainfall_mm, data.risk_level)

@app.post("/alert_operator")
def api_alert_operator_post(data: AlertInput):
    return alert_operator(data.message)

@app.post("/suggest_action")
def api_suggest_action_post(data: SuggestionInput):
    return suggest_action_for_risk(data.risk_level)

@app.get("/logged_interventions")
def api_logged_interventions():
    return get_logged_interventions()

@app.get("/parameter_descriptions")
def api_parameter_descriptions():
    return get_parameter_descriptions()

@app.get("/river_impact_severity")
def api_river_impact_severity(location: str = "London"):
    return get_river_impact_severity(location)

@app.get("/coordinate")
def api_coordinate(location: str = "London"):
    return storm_response_coordinator(location)
