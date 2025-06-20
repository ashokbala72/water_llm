
import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "integration.db"
CSV_FILE = "tank_config.csv"

st.set_page_config(page_title="🛠️ Integration Settings Clean", layout="centered")
st.title("⚙️ Water LLM Integration Configurator")

# --- Utility: Load locations from DB ---
def get_locations():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT location FROM integration_config")
    locations = [row[0] for row in cursor.fetchall()]
    conn.close()
    return locations

# --- Utility: Load settings for selected location ---
def load_settings(location):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(integration_config)")
    columns_info = cursor.fetchall()
    column_names = [col[1] for col in columns_info]
    cursor.execute("SELECT * FROM integration_config WHERE location=?", (location,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(zip(column_names, row))
    return {}

# --- Utility: Save settings back to DB ---
def save_settings(settings):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    keys = list(settings.keys())
    values = [settings[k] for k in keys]
    placeholders = ",".join(["?"] * len(keys))
    columns = ",".join(keys)
    update_clause = ",".join([f"{k}=?" for k in keys])
    cursor.execute("SELECT 1 FROM integration_config WHERE location=?", (settings["location"],))
    exists = cursor.fetchone()
    if exists:
        cursor.execute(f"UPDATE integration_config SET {update_clause} WHERE location=?", values + [settings["location"]])
    else:
        cursor.execute(f"INSERT INTO integration_config ({columns}) VALUES ({placeholders})", values)
    conn.commit()
    conn.close()

# --- UI: Select location ---
locations = get_locations()
selected = st.selectbox("🌍 Select Location", ["-- Add New --"] + locations, key="location_selector")

if selected != "-- Add New --":
    data = load_settings(selected)
else:
    data = {
        "location": "",
        "scada_api": "",
        "mqtt_broker": "",
        "mqtt_topic": "",
        "opcua_url": "",
        "plc_ip": "",
        "plc_port": "",
        "auth_token": "",
        "weather_api": "",
        "weather_coords": "",
        "sensor_vendor": "",
        "sensor_endpoint": "",
        "notes": ""
    }

# --- UI: Basic Settings ---
st.text_input("Location", value=data.get("location", ""), key="location_input", disabled=(selected != "-- Add New --"))

fields = [
    ("SCADA API", "scada_api"),
    ("MQTT Broker", "mqtt_broker"),
    ("MQTT Topic", "mqtt_topic"),
    ("OPC-UA URL", "opcua_url"),
    ("PLC IP", "plc_ip"),
    ("PLC Port", "plc_port"),
    ("Auth Token", "auth_token"),
    ("Weather API", "weather_api"),
    ("Weather Coordinates", "weather_coords"),
    ("Sensor Vendor", "sensor_vendor"),
    ("Sensor Endpoint", "sensor_endpoint"),
    ("Notes", "notes")
]

for label, key in fields:
    st.text_input(label, value=data.get(key, ""), key=key)

# --- UI: CSV Upload ---
st.markdown("### 📤 Upload `tank_config.csv`")
uploaded_file = st.file_uploader("Choose CSV file", type=["csv"], key="upload_tank_csv")
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        if all(col in df.columns for col in ["location", "zone", "capacity"]):
            df.to_csv(CSV_FILE, index=False)
            st.success("✅ CSV uploaded and saved")
            # Optional preview
            st.dataframe(df)
        else:
            st.error("❌ CSV must contain columns: location, zone, capacity")
    except Exception as e:
        st.error(f"❌ Error reading CSV: {e}")

# --- UI: Save Settings Button ---
if st.button("💾 Save Settings", key="save_button"):
    new_data = {key: st.session_state.get(key, "") for _, key in fields}
    new_data["location"] = data["location"] if selected != "-- Add New --" else st.session_state.get("location_input")
    try:
        save_settings(new_data)
        st.success("✅ Settings saved successfully.")
    except Exception as e:
        st.error(f"❌ Failed to save settings: {e}")
