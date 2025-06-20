import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Integration Config", layout="wide")
st.title("🔧 Integration Configuration")

# Connect to or create the database
conn = sqlite3.connect('integration.db')
cursor = conn.cursor()

# Ensure the integration_config table exists with correct schema
cursor.execute("""
CREATE TABLE IF NOT EXISTS integration_config (
    location TEXT PRIMARY KEY,
    scada_api TEXT,
    auth_token TEXT,
    mqtt_broker TEXT,
    mqtt_topic TEXT,
    opcua_url TEXT,
    plc_ip TEXT,
    plc_port TEXT,
    weather_api TEXT,
    sensor_vendor TEXT,
    sensor_endpoint TEXT,
    notes TEXT
)
""")

# Select or create location
locations = [row[0] for row in cursor.execute("SELECT location FROM integration_config")]
location = st.selectbox("📍 Location", locations + ["Other"])
if location == "Other":
    location = st.text_input("Enter new location")

# Load existing values if available
existing = {}
if location:
    row = cursor.execute("SELECT * FROM integration_config WHERE location = ?", (location,)).fetchone()
    if row:
        columns = [desc[0] for desc in cursor.description]
        existing = dict(zip(columns, row))

# Input fields
scada_api = st.text_input("🔌 SCADA API", value=existing.get("scada_api", ""))
auth_token = st.text_input("🔑 Auth Token", value=existing.get("auth_token", ""))
mqtt_broker = st.text_input("📡 MQTT Broker", value=existing.get("mqtt_broker", ""))
mqtt_topic = st.text_input("🧵 MQTT Topic", value=existing.get("mqtt_topic", ""))
opcua_url = st.text_input("🕹️ OPC-UA URL", value=existing.get("opcua_url", ""))
plc_ip = st.text_input("📟 PLC IP", value=existing.get("plc_ip", ""))
plc_port = st.text_input("🔢 PLC Port", value=existing.get("plc_port", ""))
weather_api = st.text_input("🌦️ Weather API", value=existing.get("weather_api", ""))
sensor_vendor = st.text_input("🏷️ Sensor Vendor", value=existing.get("sensor_vendor", ""))
sensor_endpoint = st.text_input("📍 Sensor Endpoint", value=existing.get("sensor_endpoint", ""))
notes = st.text_area("📝 Notes", value=existing.get("notes", ""))

# CSV upload for tank_config.csv
st.subheader("📁 Upload tank_config.csv")
uploaded_tank_file = st.file_uploader("Upload tank config file", type=["csv"], key="tank_csv")
if uploaded_tank_file:
    with open("tank_config.csv", "wb") as f:
        f.write(uploaded_tank_file.getbuffer())
    st.success("✅ tank_config.csv saved.")
    st.dataframe(pd.read_csv(uploaded_tank_file))

# CSV upload for asset_config.csv
st.subheader("📁 Upload asset_config.csv")
st.caption("Expected columns: location, asset, expected_value (e.g., `penstock_open`, `true`)")
uploaded_asset_file = st.file_uploader("Upload asset config file", type=["csv"], key="asset_csv")
if uploaded_asset_file:
    with open("asset_config.csv", "wb") as f:
        f.write(uploaded_asset_file.getbuffer())
    st.success("✅ asset_config.csv saved.")
    st.dataframe(pd.read_csv(uploaded_asset_file))


# CSV upload for river_impact_config.csv
st.subheader("📁 Upload river_impact_config.csv")
st.caption("Expected columns: location, zone, river_name, impact_severity (HIGH/MEDIUM/LOW)")
uploaded_river_file = st.file_uploader("Upload river impact config file", type=["csv"], key="river_csv")
if uploaded_river_file:
    with open("river_impact_config.csv", "wb") as f:
        f.write(uploaded_river_file.getbuffer())
    st.success("✅ river_impact_config.csv saved.")
    st.dataframe(pd.read_csv(uploaded_river_file))


# Save button
if st.button("💾 Save Integration Settings"):
    cursor.execute("""
    INSERT OR REPLACE INTO integration_config (
        location, scada_api, auth_token, mqtt_broker, mqtt_topic,
        opcua_url, plc_ip, plc_port, weather_api, sensor_vendor,
        sensor_endpoint, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        location, scada_api, auth_token, mqtt_broker, mqtt_topic,
        opcua_url, plc_ip, plc_port, weather_api, sensor_vendor,
        sensor_endpoint, notes
    ))
    conn.commit()
    st.success(f"✅ Saved settings for {location}")
