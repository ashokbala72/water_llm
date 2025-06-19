
import os
import json
import sqlite3
import requests
import datetime
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed
import logging
from openai import OpenAI

# === Logging Setup ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("WaterLLM")

# === Load API Key ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DB_PATH = "integration.db"

def get_real_time_inputs():
    return {
        "rainfall_mm": 85,
        "tank_fill_percent": 96,
        "timestamp": str(datetime.datetime.now())
    }

def calculate_overflow_risk(rain_mm, tank_fill_percent):
    if rain_mm > 20 and tank_fill_percent > 90:
        return "HIGH"
    elif rain_mm > 10 and tank_fill_percent > 75:
        return "MEDIUM"
    return "LOW"

def predict_overflow(rain_mm, tank_fill_percent):
    return rain_mm > 80 or tank_fill_percent > 90

def dynamic_control_advice(tank_fill_percent):
    if tank_fill_percent > 90:
        return "Open secondary valve and enable backup pump."
    elif tank_fill_percent > 75:
        return "Increase pump speed by 15%."
    return "Maintain current configuration."

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def call_gpt(prompt, temperature=0.3):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a water infrastructure expert and regulatory advisor."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        return "OpenAI call failed."

def generate_genai_advisory():
    return "Activate backup pump, notify operators, and monitor overflow every 15 minutes."

def generate_regulatory_report(location="London", rain=85, risk_level="HIGH"):
    return f"[REGULATORY REPORT]\nLocation: {location}\nRainfall: {rain} mm\nRisk: {risk_level}\n\n🚨 Anomalies Detected: ['Simulated anomaly: Tank level sensor reading unstable.']\n\n🏗️ Recommended Infra: Install higher capacity drainage and redundant pumps."

def detect_anomalies(sensor_data):
    return ["🔍 Simulated anomaly: Tank level sensor reading unstable."]

def recommend_infrastructure_upgrades():
    return ["Add overflow basin", "Upgrade pump firmware", "Install remote valve controller"]

def actuate_asset(action):
    return f"Simulated actuation: {action}"

def compliance_check(rainfall_mm, overflow_predicted):
    if rainfall_mm > 80 or overflow_predicted:
        return "NON-COMPLIANT: Overflow protocol violated."
    return "COMPLIANT"

def run_all_analyses(location="London"):
    inputs = get_real_time_inputs()
    rainfall = inputs["rainfall_mm"]
    tank = inputs["tank_fill_percent"]
    risk = calculate_overflow_risk(rainfall, tank)
    anomalies = detect_anomalies({"tank_sensor": {"reading": tank}, "rain_sensor": {"reading": rainfall}})
    advisory = generate_genai_advisory()
    upgrades = recommend_infrastructure_upgrades()
    compliance = compliance_check(rainfall, predict_overflow(rainfall, tank))
    return {
        "inputs": inputs,
        "overflow_risk": risk,
        "anomalies": anomalies,
        "advisory": advisory,
        "recommendations": upgrades,
        "compliance": compliance
    }

def alert_operator(message):
    return f"ALERT SENT TO OPERATOR: {message}"

def suggest_action_for_risk(risk):
    if risk == "HIGH":
        return "Deploy mobile pump team and send emergency SMS alert."
    elif risk == "MEDIUM":
        return "Run diagnostic on valve throughput."
    return "Monitor hourly."

def overflow_control(location="London"):
    inputs = get_real_time_inputs()
    rain = inputs["rainfall_mm"]
    tank = inputs["tank_fill_percent"]
    risk = calculate_overflow_risk(rain, tank)
    advisory = call_gpt(f"Risk is {risk} with {rain}mm rain and {tank}% tank. What should be done?")
    return {
        "rain_mm": rain,
        "tank_fill_percent": tank,
        "risk": risk,
        "action": {"command": dynamic_control_advice(tank)},
        "advisory": advisory
    }

def fetch_weather_data(location="London"):
    return {"forecast": {"rainfall_mm": 85}}

def fetch_sensor_data(location="London"):
    return {"telemetry": {"tank_fill_percent": 96}}

def forecast_risk_assessment(location="London"):
    rain = 85
    tank = 96
    risk = calculate_overflow_risk(rain, tank)
    advisory = generate_genai_advisory()
    return {
        "forecast_rainfall_mm": rain,
        "forecast_tank_fill_percent": tank,
        "predicted_risk": risk,
        "overflow_predicted": True,
        "advisory": advisory
    }

def storm_response_coordinator(location="London"):
    inputs = get_real_time_inputs()
    rainfall = inputs["rainfall_mm"]
    tank = inputs["tank_fill_percent"]
    risk = calculate_overflow_risk(rainfall, tank)
    overflow = predict_overflow(rainfall, tank)
    control = dynamic_control_advice(tank)
    advisory = generate_genai_advisory()
    report = generate_regulatory_report(location, rainfall, risk)
    anomalies = detect_anomalies({"tank_sensor": {"reading": tank}, "rain_sensor": {"reading": rainfall}})
    upgrades = recommend_infrastructure_upgrades()
    alert_sent = alert_operator("HIGH RISK DETECTED")
    return {
        "location": location,
        "inputs": inputs,
        "risk_level": risk,
        "overflow_predicted": overflow,
        "control_advice": control,
        "control_result": {"status": "Executed", "details": control},
        "genai_advisory": advisory,
        "regulatory_report": report,
        "anomalies": anomalies,
        "infra_upgrades": upgrades,
        "alert_sent": alert_sent
    }
