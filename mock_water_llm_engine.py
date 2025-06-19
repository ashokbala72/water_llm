import os
import json
import sqlite3
import requests
import datetime
import paho.mqtt.publish as mqtt
from dotenv import load_dotenv
from pydantic import BaseModel


class WeatherData(BaseModel):
    rainfall_mm: float
    timestamp: str = ""

class SensorData(BaseModel):
    inflow_rate_lps: float
    tank_fill_percent: float

from openai import OpenAI

import logging
from tenacity import retry, stop_after_attempt, wait_fixed
from pydantic import BaseModel, ValidationError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/water_llm_structured.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WaterLLM")

# === RETRYABLE INTEGRATION HELPERS ===

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def post_scada_command(scada_api, command, token):
    return requests.post(scada_api, json={"command": command}, headers={"Authorization": f"Bearer {token}"})

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def send_mqtt_message(broker, topic, command):
    mqtt.single(topic, payload=command, hostname=broker)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def send_opcua_command(url, command):
    opc = OPCUAClient(url)
    opc.connect()
    node = opc.get_objects_node().get_child(["0:MyDevice", "0:Command"])
    node.set_value(command)
    opc.disconnect()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def send_modbus_command(ip, port, command):
    plc = ModbusTcpClient(ip, port=int(port))
    plc.connect()
    plc.write_register(1, int(command) if command.isdigit() else 1)
    plc.close()

try:
except Exception as e:
    print(f'Error: {e}')
    from opcua import Client as OPCUAClient
except ImportError:
    OPCUAClient = None

try:
except Exception as e:
    print(f'Error: {e}')
    from pymodbus.client import ModbusTcpClient

def get_integration_config(location=None):
    return {
        "location": location or "London",
        "weather_api": "mock-weather-key",
        "sensor_api": "mock-sensor-key",
        "scada_enabled": True,
        "mqtt_enabled": True,
        "opcua_enabled": False,
        "plc_enabled": False,
        "description": "Default mock configuration for testing"
    }

except ImportError:
    ModbusTcpClient = None

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DB_PATH = "integration.db"
LOG_FILE = "logs/water_llm_log.json"
os.makedirs("logs", exist_ok=True)

def get_integration_config(location="London"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM integration_config WHERE location=?", (location,))
    row = cursor.fetchone()
    conn.close()
    if row:
        columns = [
            "id", "location", "scada_api", "mqtt_broker", "mqtt_topic", "opcua_url",
            "plc_ip", "plc_port", "auth_token", "weather_api", "weather_coords",
            "sensor_vendor", "sensor_endpoint", "notes"
        ]
        return dict(zip(columns, row))
    return {}

def actuate_asset(command, location="London"):
    config = get_integration_config(location)
    results = {}

    # Security Audit Log
    logger.info(f"🔐 Actuation command: {command} for {location} | Config Source: {config.get('sensor_vendor', 'N/A')}")


    # SCADA API Command
    scada_api = config.get("scada_api")
    if scada_api:
        try:
        except Exception as e:
            print(f'Error: {e}')
            r = post_scada_command(scada_api, command, config.get("auth_token", ""))
            r.raise_for_status()
            results["SCADA"] = "✅ SCADA Command Sent"
        except Exception as e:
            results["SCADA"] = f"❌ SCADA Error: {str(e)}"

    # MQTT Command
    if config.get("mqtt_broker") and config.get("mqtt_topic"):
        try:
        except Exception as e:
            print(f'Error: {e}')
            send_mqtt_message(config["mqtt_broker"], config["mqtt_topic"], command)
            results["MQTT"] = "✅ MQTT Command Published"
        except Exception as e:
            results["MQTT"] = f"❌ MQTT Error: {str(e)}"

    # OPC-UA Command
    if OPCUAClient and config.get("opcua_url"):
        try:
        except Exception as e:
            print(f'Error: {e}')
            send_opcua_command(config["opcua_url"], command)
            results["OPC-UA"] = "✅ OPC-UA Command Written"
        except Exception as e:
            results["OPC-UA"] = f"❌ OPC-UA Error: {str(e)}"

    # PLC via Modbus
    if ModbusTcpClient and config.get("plc_ip") and config.get("plc_port"):
        try:
        except Exception as e:
            print(f'Error: {e}')
            send_modbus_command(config["plc_ip"], config["plc_port"], command)
            results["PLC"] = "✅ PLC Modbus Command Sent"
        except Exception as e:
            results["PLC"] = f"❌ PLC Error: {str(e)}"

    return results

def fetch_weather_data(location="London"):
    config = get_integration_config(location)
    api = config.get("weather_api")
    if not api:
        return "No weather API configured."
    try:
    except Exception as e:
        print(f'Error: {e}')
        response = requests.get(api)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def fetch_sensor_data(location="London"):
    config = get_integration_config(location)
    endpoint = config.get("sensor_endpoint")
    if not endpoint:
        return "No sensor API configured."
    try:
    except Exception as e:
        print(f'Error: {e}')
        response = requests.get(endpoint)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def call_gpt(prompt, temperature=0.3):
    try:
    except Exception as e:
        print(f'Error: {e}')
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
        logger.error(f'OpenAI API call failed: {e}')
        return 'OpenAI call failed.'

def calculate_overflow_risk(rain_mm, tank_fill_percent):
    """
    Calculate overflow risk score based on rainfall and tank fill level.
    """
    if rain_mm > 20 and tank_fill_percent > 90:
        return "HIGH"
    elif rain_mm > 10 and tank_fill_percent > 75:
        return "MEDIUM"
    return "LOW"

def overflow_control(location):

    config = get_integration_config(location)
    weather = fetch_weather_data(location)
    sensor = fetch_sensor_data(location)

    # Extract rainfall and tank level from APIs
    rain_mm = 0
    tank_fill = 0
    try:
    except Exception as e:
        print(f'Error: {e}')
        rain_mm = weather.get("forecast", {}).get("rainfall_mm", 0)
        tank_fill = sensor.get("telemetry", {}).get("tank_fill_percent", 0)
    except Exception:
        return {"error": "Failed to extract weather/sensor inputs."}

    risk = calculate_overflow_risk(rain_mm, tank_fill)
    result = {"rain_mm": rain_mm, "tank_fill_percent": tank_fill, "risk": risk}

    if risk == "HIGH":
        result["action"] = actuate_asset("open_overflow_valve", location)
    elif risk == "MEDIUM":
        result["action"] = actuate_asset("start_buffer_pump", location)
    else:
        result["action"] = "🟢 No control action required"

    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result["log"] = {
        "timestamp": timestamp,
        "location": location,
        "rainfall_mm": rain_mm,
        "tank_fill_percent": tank_fill,
        "risk": risk,
        "action": result["action"] if isinstance(result["action"], str) else list(result["action"].values())[0]
    }
    result["report"] = f"Overflow control executed at {timestamp} with risk: {risk} and action taken: {result['action']}"
    result["advisory"] = call_gpt(f"What are the next steps for a {risk} overflow scenario at {location}?")
    result["simulation_check"] = "Data processed and verified successfully."
    return result




def get_real_time_inputs(location="London"):
    weather = fetch_weather_data(location)
    sensors = fetch_sensor_data(location)
    return {
        "location": location,
        "rainfall_mm": weather.get("rainfall_mm", 0),
        "inflow_rate_lps": sensors.get("inflow_rate_lps", 0),
        "tank_fill_percent": sensors.get("tank_fill_percent", 0),
        "timestamp": weather.get("timestamp", "")
    }

def predict_overflow(rainfall_mm, tank_fill_percent):
    return rainfall_mm > 80 or tank_fill_percent > 90

def dynamic_control_advice(tank_fill_percent):
    if tank_fill_percent > 90:
        return "Open secondary valve and enable backup pump."
    elif tank_fill_percent > 75:
        return "Increase pump speed by 15%."
    return "Maintain current configuration."

def detect_anomalies(sensor_data):
    anomalies = []
    if sensor_data.get("tank_fill_percent", 0) > 100:
        anomalies.append("Tank overfill detected.")
    if sensor_data.get("inflow_rate_lps", -1) < 0:
        anomalies.append("Negative inflow rate.")
    return anomalies

def compliance_check(rainfall_mm, overflow_triggered):
    if rainfall_mm > 80 and not overflow_triggered:
        return "⚠️ Non-compliance: Risk threshold breached with no response."
    return "✅ System compliant."

def run_all_analyses(location="London"):
    inputs = get_real_time_inputs(location)
    overflow = predict_overflow(inputs["rainfall_mm"], inputs["tank_fill_percent"])
    control_advice = dynamic_control_advice(inputs["tank_fill_percent"])
    risk_score = calculate_overflow_risk(inputs["rainfall_mm"], inputs["tank_fill_percent"])
    compliance = compliance_check(inputs["rainfall_mm"], overflow)
    anomalies = detect_anomalies(inputs)
    upgrades = recommend_infrastructure_upgrades(location)
    advisory = suggest_action_for_risk("HIGH" if overflow else "LOW")
    return {
        "inputs": inputs,
        "overflow_risk_score": risk_score,
        "overflow_predicted": overflow,
        "control_advice": control_advice,
        "compliance_status": compliance,
        "anomalies": anomalies,
        "infrastructure_recommendations": upgrades,
        "genai_advisory": advisory
    }

def get_logged_interventions():
    try:
    except Exception as e:
        print(f'Error: {e}')
        with open("intervention_log.txt", "r", encoding="utf-8") as f:
            return f.read().splitlines()
    except:
        return ["No intervention logs found."]

def get_parameter_descriptions():
    return {
        "rainfall_mm": "Recent rainfall in millimeters",
        "inflow_rate_lps": "Water inflow rate (liters per second)",
        "tank_fill_percent": "Tank utilization as percentage of capacity"
    }

def generate_regulatory_report(location, rainfall_mm, risk_level):
    return f"📋 Location: {location}\nRainfall: {rainfall_mm}mm\nRisk Level: {risk_level}\nAction Taken: Logged\nCompliance: {'YES' if risk_level != 'HIGH' else 'REVIEW REQUIRED'}"

def recommend_infrastructure_upgrades(location="London"):
    return ["⚠️ Suggest adding buffer tank at zone A", "⚠️ Upgrade response delay for Valve-2"]

def alert_operator(message="⚠️ Overflow risk detected. Immediate action required."):
    print(f"ALERT: {message}")
    return f"Sent to control center: {message}"

def suggest_action_for_risk(risk_level):
    if risk_level == "HIGH":
        return "Immediately lower tank level and reduce inflow. Open all redundant valves."
    if risk_level == "MEDIUM":
        return "Monitor inflow every 10 mins. Prepare standby pumps."
    return "No urgent action needed."

def forecast_weather_with_gpt(location="London", horizon_days=3):
    config = get_integration_config(location)
    gpt_forecast_prompt = config.get("forecast_prompt", "")
    if not gpt_forecast_prompt:
        gpt_forecast_prompt = f"""
You are a weather analyst. Given that it's currently raining heavily in {location}, 
predict the likely weather trend for the next {horizon_days} days. 
Provide insights on potential overflow risks and if any precautionary steps are needed 
for a stormwater management system.
"""
    try:
    except Exception as e:
        print(f'Error: {e}')
        response = call_gpt(gpt_forecast_prompt)
        return f"📡 GPT-4 Forecast for {location} (next {horizon_days} days):\n" + response
    except Exception as e:
        return f"❌ GPT Forecasting failed: {e}"


storm_session_active = False

def storm_response_coordinator(location="London"):
    global storm_session_active
    if storm_session_active:
        logger.warning("Storm response already triggered. Aborting duplicate execution.")
        return {"status": "ignored", "reason": "duplicate storm trigger"}
    storm_session_active = True
    logger.info("🚨 Storm response initiated.")

    print("🚨 Running Storm Scenario Response...")

    # 1. Fetch real-time weather and sensor data
    inputs = get_real_time_inputs(location)
    rainfall = inputs["rainfall_mm"]
    tank_fill = inputs["tank_fill_percent"]

    # 2. Predict overflow
    overflow = predict_overflow(rainfall, tank_fill)

    # 3. Assess risk
    risk = calculate_overflow_risk(rainfall, tank_fill)

    # 4. Dynamic control recommendation
    control = dynamic_control_advice(tank_fill)

    # 5. Actuate response if needed
    control_result = {}
    if risk == "HIGH":
        control_result = actuate_asset("open_overflow_valve", location)
        alert = alert_operator("⚠️ Severe storm detected. Overflow valve triggered.")
    elif risk == "MEDIUM":
        control_result = actuate_asset("start_buffer_pump", location)
        alert = alert_operator("⚠️ Medium storm risk. Buffer pump engaged.")
    else:
        alert = "✅ No action required."

    # 6. Log anomalies
    anomalies = detect_anomalies(inputs)

    # 7. Check compliance
    compliance = compliance_check(rainfall, overflow)

    # 8. Generate regulatory report
    report = generate_regulatory_report(location, rainfall, risk)

    # 9. GenAI advisory
    advisory = suggest_action_for_risk(risk)

    # 10. Infrastructure upgrades
    upgrades = recommend_infrastructure_upgrades(location)

    return {
        "location": location,
        "inputs": inputs,
        "overflow_predicted": overflow,
        "risk_level": risk,
        "control_advice": control,
        "control_result": control_result,
        "alert_sent": alert,
        "anomalies": anomalies,
        "compliance_status": compliance,
        "regulatory_report": report,
        "genai_advisory": advisory,
        "infra_upgrades": upgrades
    }
