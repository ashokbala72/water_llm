
import os
import json
import sqlite3
import requests
import datetime
import paho.mqtt.publish as mqtt
from dotenv import load_dotenv
from openai import OpenAI

try:
    from opcua import Client as OPCUAClient
except ImportError:
    OPCUAClient = None

try:
    from pymodbus.client import ModbusTcpClient
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

    # SCADA API Command
    scada_api = config.get("scada_api")
    if scada_api:
        try:
            r = requests.post(scada_api, json={"command": command}, headers={"Authorization": f"Bearer {config.get('auth_token', '')}"})
            r.raise_for_status()
            results["SCADA"] = "✅ SCADA Command Sent"
        except Exception as e:
            results["SCADA"] = f"❌ SCADA Error: {str(e)}"

    # MQTT Command
    if config.get("mqtt_broker") and config.get("mqtt_topic"):
        try:
            mqtt.single(config["mqtt_topic"], payload=command, hostname=config["mqtt_broker"])
            results["MQTT"] = "✅ MQTT Command Published"
        except Exception as e:
            results["MQTT"] = f"❌ MQTT Error: {str(e)}"

    # OPC-UA Command
    if OPCUAClient and config.get("opcua_url"):
        try:
            opc = OPCUAClient(config["opcua_url"])
            opc.connect()
            node = opc.get_objects_node().get_child(["0:MyDevice", "0:Command"])
            node.set_value(command)
            opc.disconnect()
            results["OPC-UA"] = "✅ OPC-UA Command Written"
        except Exception as e:
            results["OPC-UA"] = f"❌ OPC-UA Error: {str(e)}"

    # PLC via Modbus
    if ModbusTcpClient and config.get("plc_ip") and config.get("plc_port"):
        try:
            plc = ModbusTcpClient(config["plc_ip"], port=int(config["plc_port"]))
            plc.connect()
            plc.write_register(1, int(command) if command.isdigit() else 1)
            plc.close()
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
        response = requests.get(endpoint)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

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
