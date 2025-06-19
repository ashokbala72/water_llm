
import streamlit as st
import sqlite3
import os

DB_PATH = "integration.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS integration_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT UNIQUE,
            scada_api TEXT,
            mqtt_broker TEXT,
            mqtt_topic TEXT,
            opcua_url TEXT,
            plc_ip TEXT,
            plc_port INTEGER,
            auth_token TEXT,
            weather_api TEXT,
            weather_coords TEXT,
            sensor_vendor TEXT,
            sensor_endpoint TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_existing_config(location):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM integration_config WHERE location=?", (location,))
    row = cursor.fetchone()
    conn.close()
    if row:
        keys = ["id", "location", "scada_api", "mqtt_broker", "mqtt_topic", "opcua_url", "plc_ip", "plc_port",
                "auth_token", "weather_api", "weather_coords", "sensor_vendor", "sensor_endpoint", "notes"]
        return dict(zip(keys, row))
    return {}

def save_config(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO integration_config (
            location, scada_api, mqtt_broker, mqtt_topic, opcua_url,
            plc_ip, plc_port, auth_token, weather_api, weather_coords,
            sensor_vendor, sensor_endpoint, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(location) DO UPDATE SET
            scada_api=excluded.scada_api,
            mqtt_broker=excluded.mqtt_broker,
            mqtt_topic=excluded.mqtt_topic,
            opcua_url=excluded.opcua_url,
            plc_ip=excluded.plc_ip,
            plc_port=excluded.plc_port,
            auth_token=excluded.auth_token,
            weather_api=excluded.weather_api,
            weather_coords=excluded.weather_coords,
            sensor_vendor=excluded.sensor_vendor,
            sensor_endpoint=excluded.sensor_endpoint,
            notes=excluded.notes
    """, (
        data["location"], data["scada_api"], data["mqtt_broker"], data["mqtt_topic"],
        data["opcua_url"], data["plc_ip"], data["plc_port"], data["auth_token"],
        data["weather_api"], data["weather_coords"], data["sensor_vendor"],
        data["sensor_endpoint"], data["notes"]
    ))
    conn.commit()
    conn.close()

st.set_page_config(page_title="🛠️ Water LLM Integration Config", layout="centered")
tab1, tab2 = st.tabs(["ℹ️ Overview", "⚙️ Integration Settings"])

# Overview Tab
with tab1:
    st.title("ℹ️ Water LLM Integration System – Overview")
    st.markdown("""
This application configures how the **Water LLM Engine** connects to real-time systems like SCADA, sensors, weather APIs, MQTT brokers, OPC-UA servers, and PLC controllers.

---

### 🔧 How It Works (Updated Overview):

This panel controls how the **Water LLM Engine** connects with real-world infrastructure components, including **SCADA**, **sensors**, **weather APIs**, **PLC**, **MQTT**, and **OPC-UA systems**.

All integration details are saved to a local SQLite database (`integration.db`) and accessed by the Water LLM engine during runtime.

---

### 📘 Function Overview with Dependency Mapping:

| 🧠 Function Name | 💡 Description | ⚙️ Depends on Setting |
|------------------|----------------|------------------------|
| `get_integration_config()` | Fetches the integration settings for a given location. | `integration.db` |
| `fetch_weather_data()` | Retrieves live rainfall/weather data. | `weather_api` |
| `fetch_sensor_data()` | Retrieves live tank/inflow sensor values. | `sensor_endpoint` |
| `post_scada_command()` | Sends actuation command to SCADA via HTTP POST. | `scada_api`, `auth_token` |
| `send_mqtt_message()` | Publishes MQTT message to configured topic. | `mqtt_broker`, `mqtt_topic` |
| `send_opcua_command()` | Sends command via OPC-UA protocol. | `opcua_url` |
| `send_modbus_command()` | Sends command using Modbus to a PLC. | `plc_ip`, `plc_port` |
| `actuate_asset()` | Unified command dispatcher — uses SCADA, MQTT, OPC-UA, or PLC. | All control integration fields |
| `get_real_time_inputs()` | Aggregates weather and sensor readings. | `weather_api`, `sensor_endpoint` |
| `call_gpt()` | Calls OpenAI for GenAI suggestions. | `.env → OPENAI_API_KEY` |
| `calculate_overflow_risk()` | Evaluates overflow risk based on rainfall and tank fill. | Sensor + weather inputs |
| `overflow_control()` | Performs risk assessment and actuation. | Uses all real-time config |
| `predict_overflow()` | Boolean check for overflow condition. | Sensor + weather inputs |
| `dynamic_control_advice()` | Rule-based control logic depending on tank fill. | `tank_fill_percent` |
| `detect_anomalies()` | Detects sensor abnormalities. | `sensor_endpoint` |
| `compliance_check()` | Checks if overflow action matched rainfall condition. | Weather + overflow |
| `recommend_infrastructure_upgrades()` | Returns advisory on infra improvements. | `location` |
| `suggest_action_for_risk()` | Returns text recommendation for overflow risk levels. | Risk level |
| `generate_regulatory_report()` | Outputs compliance report text for authorities. | Weather + risk level |
| `alert_operator()` | Logs and simulates emergency alert message. | N/A |
| `run_all_analyses()` | Composite call for all analytical and advisory modules. | All input/output functions |
| `get_logged_interventions()` | Loads log of past actuation events. | `intervention_log.txt` |
| `get_parameter_descriptions()` | Explains what each sensor parameter means. | N/A |
| `forecast_weather_with_gpt()` | Predicts multi-day rainfall trends with GPT. | `weather_api`, `forecast_prompt`, `.env` |
| `storm_response_coordinator()` | Triggers end-to-end storm response. | ALL control and sensor integration settings |

---

### ✅ Engine Retrieval Sample

Once integration settings are saved via this app, the engine uses:

```python
from integration_settings import get_integration_config
config = get_integration_config("London")
```

This enables dynamic and location-specific behavior across all 25 core functions.
    """)
    st.markdown("""
This application configures how the **Water LLM Engine** connects to real-time systems like SCADA, sensors, weather APIs, MQTT brokers, OPC-UA servers, and PLC controllers.

---

### 🔧 How It Works:

1. **Settings Input (Other Tab)**  
   You enter integration values such as:
   - SCADA API URL
   - MQTT Broker and Topic
   - OPC-UA Server URL
   - PLC IP and Port
   - Weather API and coordinates
   - Sensor endpoints
   - Notes or metadata

2. **Storage in SQLite**  
   The values are saved in a local database file: `integration.db`, with a dynamic schema.

3. **Engine Usage**  
   The Water LLM Engine (e.g., `engine_integration.py`) retrieves the correct config via:
   ```python
   from engine_integration import get_integration_config
   ```

4. **Dynamic Integration**  
   - The engine sends commands via SCADA API
   - Publishes MQTT messages
   - Connects to OPC-UA/PLC based on stored config
   - Uses weather/sensor APIs as per config
    """)

# Settings Tab
with tab2:
    init_db()
    st.title("⚙️ Integration Settings")

    location = st.selectbox("🌍 Location", ["London", "Manchester", "Birmingham", "Leeds"])
    existing = get_existing_config(location)

    scada_api = st.text_input("🔗 SCADA API Endpoint", value=existing.get("scada_api", ""))
    mqtt_broker = st.text_input("📡 MQTT Broker URL", value=existing.get("mqtt_broker", ""))
    mqtt_topic = st.text_input("📨 MQTT Topic", value=existing.get("mqtt_topic", ""))
    opcua_url = st.text_input("📶 OPC-UA Server URL", value=existing.get("opcua_url", ""))
    plc_ip = st.text_input("🧠 PLC Gateway IP", value=existing.get("plc_ip", ""))
    plc_port = st.number_input("🔌 PLC Port", min_value=1, max_value=65535, value=int(existing.get("plc_port", 502)))
    auth_token = st.text_input("🔐 Auth Token / API Key", type="password", value=existing.get("auth_token", ""))

    st.markdown("---")
    st.subheader("🌦️ Weather & Sensor Integration")
    weather_api = st.text_input("🌍 Weather API Endpoint", value=existing.get("weather_api", ""))
    weather_coords = st.text_input("📍 Location Coordinates", value=existing.get("weather_coords", ""))
    sensor_vendor = st.text_input("🏭 Sensor Vendor Name", value=existing.get("sensor_vendor", ""))
    sensor_endpoint = st.text_input("🛰️ Sensor Data API Endpoint", value=existing.get("sensor_endpoint", ""))

    st.markdown("---")
    notes = st.text_area("📝 Integration Notes", value=existing.get("notes", ""))

    if st.button("💾 Save Settings"):
        save_config({
            "location": location,
            "scada_api": scada_api,
            "mqtt_broker": mqtt_broker,
            "mqtt_topic": mqtt_topic,
            "opcua_url": opcua_url,
            "plc_ip": plc_ip,
            "plc_port": plc_port,
            "auth_token": auth_token,
            "weather_api": weather_api,
            "weather_coords": weather_coords,
            "sensor_vendor": sensor_vendor,
            "sensor_endpoint": sensor_endpoint,
            "notes": notes
        })
        st.success("✅ Configuration saved successfully.")
