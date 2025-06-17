
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
   The values are saved in a local database file: `integration.db`, with this schema:
   ```sql
   CREATE TABLE integration_config (
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
   );
   ```

3. **Engine Usage**  
   The Water LLM Engine (e.g., `engine_integration.py`) uses:
   ```python
   from engine_integration import get_integration_config
   config = get_integration_config("London")
   ```
   Based on the location, it retrieves the correct endpoints and credentials.

4. **Dynamic Integration**  
   - The engine sends commands via SCADA API
   - Publishes MQTT messages
   - Connects to OPC-UA/PLC based on stored config
   - Uses weather/sensor APIs as per config

---

### 🧪 Next Step:
Go to the **Integration Settings** tab and enter your location-specific configuration.
    """)

# Settings Tab
with tab2:
    init_db()
    st.title("⚙️ Integration Settings")

    location = st.selectbox("🌍 Location", ["London", "Manchester", "Birmingham", "Leeds"])
    scada_api = st.text_input("🔗 SCADA API Endpoint")
    mqtt_broker = st.text_input("📡 MQTT Broker URL")
    mqtt_topic = st.text_input("📨 MQTT Topic")
    opcua_url = st.text_input("📶 OPC-UA Server URL")
    plc_ip = st.text_input("🧠 PLC Gateway IP")
    plc_port = st.number_input("🔌 PLC Port", min_value=1, max_value=65535, value=502)
    auth_token = st.text_input("🔐 Auth Token / API Key", type="password")

    st.markdown("---")
    st.subheader("🌦️ Weather & Sensor Integration")
    weather_api = st.text_input("🌍 Weather API Endpoint (e.g., Open-Meteo)")
    weather_coords = st.text_input("📍 Location Coordinates (lat,lon)", placeholder="51.5074,-0.1278")
    sensor_vendor = st.text_input("🏭 Sensor Vendor Name")
    sensor_endpoint = st.text_input("🛰️ Sensor Data API Endpoint")

    st.markdown("---")
    notes = st.text_area("📝 Integration Notes")

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
