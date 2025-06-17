
import os
import json
import sqlite3
import requests
import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DB_PATH = "integration.db"
LOG_FILE = "logs/water_llm_log.json"
os.makedirs("logs", exist_ok=True)

def get_integration_config(location="London"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT scada_api, mqtt_broker, mqtt_topic, opcua_url, plc_ip, plc_port, auth_token FROM integration_config WHERE location=?", (location,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "scada_api": row[0],
            "mqtt_broker": row[1],
            "mqtt_topic": row[2],
            "opcua_url": row[3],
            "plc_ip": row[4],
            "plc_port": row[5],
            "auth_token": row[6]
        }
    return {}

def actuate_asset(command, location="London"):
    config = get_integration_config(location)
    scada_api = config.get("scada_api")
    if scada_api:
        try:
            response = requests.post(scada_api, json={"command": command}, headers={"Authorization": f"Bearer {config.get('auth_token', '')}"})
            response.raise_for_status()
            return {"status": "success", "message": response.json().get("message", "Command sent")}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    else:
        return {"status": "error", "message": "No SCADA API configured for this location"}

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
