# water_llm_engine.py

import os
import json
import random
import requests
import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LOG_FILE = "logs/water_llm_log.json"
os.makedirs("logs", exist_ok=True)

def call_gpt(prompt, temperature=0.3):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a water infrastructure expert and regulatory advisor."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )
    return response.choices[0].message.content.strip()

def get_real_time_inputs(location="London"):
    def fetch_rainfall_forecast():
        try:
            coords = {
                "London": (51.5074, -0.1278),
                "Manchester": (53.4808, -2.2426),
                "Birmingham": (52.4862, -1.8904),
                "Leeds": (53.8008, -1.5491)
            }
            lat, lon = coords.get(location, (51.5074, -0.1278))
            response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "hourly": "precipitation",
                    "forecast_days": 1
                }
            )
            data = response.json()
            return round(sum(data['hourly']['precipitation'][:12]), 2)
        except:
            return random.randint(10, 80)

    inputs = {
        'rainfall_forecast': fetch_rainfall_forecast(),
        'inflow_rate': random.randint(150, 400),
        'outflow_rate': random.randint(100, 300),
        'tank_level': random.randint(60, 95),
        'tank_capacity': 500000,
        'pump_speed': random.randint(800, 1500),
        'valve_a_status': random.choice(['Open', 'Closed', 'Partially Open']),
        'overflow_risk': random.choice(['High', 'Moderate', 'Low']),
        'pump_vibration': round(random.uniform(0.1, 2.5), 2),
        'valve_delay': random.randint(0, 10),
        'sensor_score': random.randint(1, 10),
        'level_drop': random.randint(0, 20),
        'overflow_duration': random.randint(5, 60),
        'overflow_count': random.randint(1, 10),
        'treated': random.choice(['Yes', 'No'])
    }

    print("\n📡 Water LLM Engine is monitoring real-time inputs:")
    for key, value in inputs.items():
        print(f"- {key.replace('_', ' ').title()}: {value}")

    return inputs

def predict_overflow(inputs):
    prompt = f"""
    The Water LLM Engine is analyzing stormwater infrastructure data.
    Inputs:
    - Rainfall forecast: {inputs['rainfall_forecast']} mm
    - Inflow rate: {inputs['inflow_rate']} L/s
    - Tank level: {inputs['tank_level']} %
    - Tank capacity: {inputs['tank_capacity']} L
    - Outflow rate: {inputs['outflow_rate']} L/s

    Predict if an overflow is likely in the next 12 hours. Provide reasoning.
    Simulate sewer network behavior based on rainfall and flow rates. Indicate if rerouting is needed.
    """
    return call_gpt(prompt)

def dynamic_control_advice(inputs):
    prompt = f"""
    Based on the system conditions monitored by the Water LLM Engine:
    - Pump 1 speed: {inputs['pump_speed']} RPM
    - Valve A status: {inputs['valve_a_status']}
    - Tank level: {inputs['tank_level']} %
    - Inflow rate: {inputs['inflow_rate']} L/s
    - Overflow risk: {inputs['overflow_risk']}

    Recommend immediate control actions:
    - Activate or reduce pump speed
    - Open or close valves
    - Redirect water to storm tanks or detention tanks
    - Delay discharges if necessary
    Suggest how these actions reduce risk and improve system performance.
    """
    return call_gpt(prompt)

def detect_anomalies(inputs):
    prompt = f"""
    The Water LLM Engine is performing anomaly detection.
    Sensor Data:
    - Pump vibration: {inputs['pump_vibration']} mm/s
    - Valve response delay: {inputs['valve_delay']} seconds
    - Sensor reliability score: {inputs['sensor_score']}/10
    - Unexpected level drop: {inputs['level_drop']} %

    Identify potential equipment failures and asset reliability issues.
    Recommend proactive maintenance steps that can lower long-term cost and extend equipment lifespan.
    """
    return call_gpt(prompt)

def compliance_check(inputs):
    prompt = f"""
    The Water LLM Engine is evaluating regulatory compliance.
    - Overflow duration: {inputs['overflow_duration']} minutes
    - Frequency this month: {inputs['overflow_count']} times
    - Treated before discharge: {inputs['treated']} 
    - Regulatory context: EA stormwater rules (UK)

    Determine if there is a compliance breach.
    Recommend necessary interventions to meet discharge regulations.
    """
    return call_gpt(prompt)

def run_all_analyses(all_inputs, location, scada_enabled=False):
    print("\n📥 Water LLM Engine is analyzing current state and generating recommendations...")

    results = {
        "Overflow Prediction": predict_overflow(all_inputs),
        "Dynamic Control Advisory": dynamic_control_advice(all_inputs),
        "Anomaly Detection": detect_anomalies(all_inputs),
        "Compliance Check": compliance_check(all_inputs)
    }

    # Self-learning placeholder (refine future recommendations based on past data)
    # e.g., analyze log file trends or scoring

    # Asset scoring logic (very basic prototype)
    critical_score = (all_inputs['pump_vibration'] + all_inputs['valve_delay']) / 2
    results["Asset Health Score"] = f"{10 - round(critical_score, 1)} / 10 — lower means more reliable"

    # Simulate SCADA pushback (just a placeholder toggle for now)
    if scada_enabled:
        results["SCADA Feedback"] = "✅ Control recommendations sent to SCADA interface. Awaiting response."
    else:
        results["SCADA Feedback"] = "⚠️ SCADA integration not enabled. Actions are advisory only."

    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "location": location,
        "inputs": all_inputs,
        "results": results,
        "scada_enabled": scada_enabled
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
    print("✅ Intervention logged.")
    return results

def get_logged_interventions():
    if not os.path.exists(LOG_FILE):
        return []
    entries = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"⚠️ Skipping malformed log line: {line[:80]}...")
    return entries



    return {
        "rainfall_forecast": "Expected rainfall in the next few hours. High values may signal future inflow.",
        "inflow_rate": "Water entering the system from sewers or runoff (litres/second).",
        "outflow_rate": "Water discharged or pumped out (litres/second).",
        "tank_level": "Current fill level of the storage tank (percentage).",
        "tank_capacity": "Total capacity of the tank (litres).",
        "pump_speed": "Speed of the pump motor (RPM). Higher = faster drainage.",
        "valve_a_status": "Status of main valve (Open/Closed/Partial).",
        "overflow_risk": "Predicted risk of overflow based on current flow and weather.",
        "pump_vibration": "Mechanical vibration from pump. High values may indicate faults.",
        "valve_delay": "Time delay in valve operation (seconds). High values = sluggish response.",
        "sensor_score": "Sensor reliability score from 1 (poor) to 10 (excellent).",
        "level_drop": "Unexpected drop in tank level (percentage) which may signal leakage.",
        "overflow_duration": "Total duration of overflow events (minutes).",
        "overflow_count": "Number of overflows recorded this month.",
        "treated": "Was the overflow water treated before discharge?"
    }

def get_parameter_descriptions():
    return {
        "rainfall_forecast": "Expected rainfall in the next few hours. High values may signal future inflow.",
        "inflow_rate": "Water entering the system from sewers or runoff (litres/second).",
        "outflow_rate": "Water discharged or pumped out (litres/second).",
        "tank_level": "Current fill level of the storage tank (percentage).",
        "tank_capacity": "Total capacity of the tank (litres).",
        "pump_speed": "Speed of the pump motor (RPM). Higher = faster drainage.",
        "valve_a_status": "Status of main valve (Open/Closed/Partial).",
        "overflow_risk": "Predicted risk of overflow based on current flow and weather.",
        "pump_vibration": "Mechanical vibration from pump. High values may indicate faults.",
        "valve_delay": "Time delay in valve operation (seconds). High values = sluggish response.",
        "sensor_score": "Sensor reliability score from 1 (poor) to 10 (excellent).",
        "level_drop": "Unexpected drop in tank level (percentage) which may signal leakage.",
        "overflow_duration": "Total duration of overflow events (minutes).",
        "overflow_count": "Number of overflows recorded this month.",
        "treated": "Was the overflow water treated before discharge?"
    }

def generate_regulatory_report(logs):
    """Returns a list of breach summaries for recent UWWTR/SODRP reporting."""
    report = []
    for entry in logs:
        if entry["results"].get("Compliance Check", "").lower().find("breach") != -1:
            report.append({
                "timestamp": entry["timestamp"],
                "location": entry["location"],
                "overflow_duration": entry["inputs"].get("overflow_duration", "N/A"),
                "overflow_count": entry["inputs"].get("overflow_count", "N/A"),
                "treated": entry["inputs"].get("treated", "N/A"),
                "compliance_status": entry["results"].get("Compliance Check", "N/A")
            })
    return {
        "total_breaches": len(report),
        "breach_details": report
    }

def recommend_infrastructure_upgrades(logs):
    """Analyzes recurring failures to recommend long-term upgrades."""
    from collections import Counter
    vibration_alerts = []
    valve_delays = []
    level_drops = []

    for entry in logs:
        v = entry["inputs"].get("pump_vibration", 0)
        d = entry["inputs"].get("valve_delay", 0)
        l = entry["inputs"].get("level_drop", 0)
        if v > 2.0:
            vibration_alerts.append(entry["location"])
        if d > 5:
            valve_delays.append(entry["location"])
        if l > 10:
            level_drops.append(entry["location"])

    return {
        "High Vibration Zones": dict(Counter(vibration_alerts)),
        "Frequent Valve Delay Zones": dict(Counter(valve_delays)),
        "Potential Leak Zones": dict(Counter(level_drops))
    }

def actuate_asset(command):
    """Send a mock or real command to SCADA. In production, connect to actual API."""
    print(f"🛠️ Sending SCADA command: {command}")
    return {"status": "success", "message": f"Command '{command}' sent to SCADA interface."}

def alert_operator(risk, action):
    """Send a simulated alert to operations team."""
    print(f"🚨 ALERT: Risk: {risk} | Recommended Action: {action}")
    return {"status": "alert_sent", "risk": risk, "action": action}

def suggest_action_for_risk(risk_description):
    """Uses GPT to recommend an operational action for a given risk."""
    prompt = f"As a water system operations expert, suggest an appropriate recommended action for the following risk:\n\n'{risk_description}'\n\nKeep the response concise."
    return call_gpt(prompt)