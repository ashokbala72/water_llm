
import streamlit as st
import datetime
import time
import json
from water_llm_engine import run_all_analyses, get_real_time_inputs, get_logged_interventions, get_parameter_descriptions

st.set_page_config(page_title="💧 Water LLM - Overflow Control & Compliance", layout="wide")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📖 Overview", "🧠 Main App", "📶 Monitoring Log", "📒 Intervention Log", "📤 Regulatory Reporting"])

# -------- OVERVIEW TAB --------

with tab1:
    st.title("📖 Water LLM Overview")

    st.markdown("""
This application uses the **Water LLM Engine** (built on GPT-4) to support AI-driven stormwater management. It performs:

- 🌧 **Overflow Prediction**
- ⚙️ **Dynamic Pump and Valve Control Advisory**
- 🚨 **Anomaly Detection**
- 📜 **Regulatory Compliance Analysis**
- 🧠 **Asset Health Scoring**
- 🔁 **SCADA Feedback Monitoring**

### 🧠 AI-Assisted Intervention:
The **Water LLM Engine** monitors **SCADA systems**, **IoT sensor data**, and **weather forecasts** in real time or through simulation. It processes this data using GPT-4 to forecast potential storm overflows and generate **intervention recommendations** such as adjusting pump speed, opening valves, or rerouting to storm tanks to avoid regulatory breaches and infrastructure damage. These decisions are logged for reporting and audit.

### 🔍 Data Sources:
- **Rainfall Forecast**: Real-time from Open-Meteo API
- **Pump Speed, Inflow/Outflow Rates, Tank Level, Valve Status**: Simulated SCADA feeds
- **Vibration, Valve Delay, Sensor Score, Level Drop**: Equipment diagnostics
- **Overflow Duration, Count, Treated Status**: Historical logs

### 🏗️ To Make This Production-Ready:
- Integrate with **real-time SCADA systems** or **IoT sensors** for pump, valve, tank, and flow data.
- Replace simulated diagnostics with actual **sensor telemetry** (vibration, delay, etc.).
- Use **cloud-based data ingestion pipelines** to store and query live operational data.
- Securely connect to official **weather APIs** and **regulatory databases**.
- Implement **alerting and decision logging** for auditability and compliance.
- Deploy on a secure platform with **role-based access**, **API gateways**, and **logging/monitoring** tools.
""")

    
    st.markdown("### ⚙️ Water LLM Engine Functional Overview")

    engine_data = {
        "Function Name": ["get_real_time_inputs", "predict_overflow", "dynamic_control_advice",
            "detect_anomalies", "compliance_check", "run_all_analyses",
            "get_logged_interventions", "get_parameter_descriptions",
            "generate_regulatory_report", "recommend_infrastructure_upgrades",
            "actuate_asset", "alert_operator", "suggest_action_for_risk", "calculate_overflow_risk", "overflow_control"],
        "Layman Description": ["Fetches real-time or simulated input data like rainfall, inflow, tank level, etc.",
            "Predicts whether an overflow might happen soon based on system inputs.",
            "Suggests how to adjust pumps/valves to reduce overflow risk.",
            "Identifies strange sensor behavior or equipment issues needing attention.",
            "Checks if overflow rules are being violated and recommends fixes.",
            "Runs all AI analyses and returns a full set of insights for decision-making.",
            "Retrieves past logged recommendations and system states for audits.",
            "Provides explanations for each system parameter in simple terms.",
            "Summarizes logged breaches in format suitable for regulatory reporting.",
            "Finds recurring problems and suggests upgrades to avoid future failures.",
            "Simulates or sends control commands (like opening a valve) to SCADA.",
            "Sends risk alerts and advisories to the operations team.",
            "Generates AI suggestions for any described risk in plain terms.", "Computes overflow risk using rainfall and tank level thresholds.", "Automatically triggers SCADA or PLC actions based on risk score."]
    }

    import pandas as pd
    df = pd.DataFrame(engine_data)
    st.dataframe(df, use_container_width=True)
with tab2:
    results = {}
    st.title("🧠 Water LLM Assistant")
    location = st.selectbox("Select Location", ["London", "Manchester", "Birmingham", "Leeds"])
    mock_mode = st.toggle("Mock Mode (Use Simulated Data)", value=True)
    scada_enabled = st.checkbox("Enable SCADA Integration", value=False)

    st.subheader("🔧 System Inputs")
    inputs = get_real_time_inputs(location)
    st.info("Using simulated sensor and weather data." if mock_mode else "Using real-time inputs.")

    if st.button("🔍 Run Water LLM Analyses"):
        with st.spinner("Running Water LLM..."):
            time.sleep(1.5)
            results = run_all_analyses(inputs, location, scada_enabled)
        st.subheader("📊 Results")
        for section in ["Overflow Prediction", "Dynamic Control Advisory", "Anomaly Detection", "Compliance Check"]:
            with st.expander(section):
                st.markdown(results.get(section, "No result returned."))

        with st.expander("🧠 Asset Health Score"):
            score = results.get("Asset Health Score", "N/A")
            st.markdown(f"**Reliability Score:** {score}")
            try:
                numeric = float(score.split("/")[0].strip())
                st.progress(numeric / 10)
            except:
                st.warning("Score format not recognized.")

        with st.expander("🔁 SCADA Feedback"):
            st.markdown(results.get("SCADA Feedback", "No SCADA feedback available."))

# -------- MONITORING LOG TAB --------
with tab3:
    st.title("📶 Water LLM Monitoring Log")
    st.markdown("Below are the latest observed values from SCADA and sensor simulations.")
    preview = get_real_time_inputs()
    descriptions = get_parameter_descriptions()
    for k, v in preview.items():
        label = f"**{k.replace('_', ' ').title()}**: {v}"
        explanation = descriptions.get(k, "")
        st.markdown(f"{label}  \n*→ {explanation}*")

# -------- INTERVENTION LOG TAB --------
with tab4:
    st.title("📒 Intervention Log")
    st.subheader("📋 Intervention Log (from logs/water_llm_log.json)")
    log_entries = get_logged_interventions()
    if log_entries:
        for entry in reversed(log_entries[-10:]):
            st.markdown(f"**🕒 {entry['timestamp']} – {entry['location']}**")
            st.markdown("- **Overflow Risk:** " + entry['inputs'].get('overflow_risk', 'N/A'))
            st.markdown("- **Recommendation:** " + entry['results'].get('Dynamic Control Advisory', '').split("\n")[0])
            st.markdown("- **Asset Score:** " + entry['results'].get('Asset Health Score', 'N/A'))
            st.markdown("- **SCADA Feedback:** " + entry['results'].get('SCADA Feedback', 'N/A'))
            st.markdown("---")
        st.download_button("📥 Download Full Log as JSON", json.dumps(log_entries, indent=2), file_name="water_llm_log.json")
    else:
        st.info("No logged interventions found in file.")

# -------- REGULATORY REPORTING TAB --------
with tab5:
    st.title("📤 Regulatory Reporting")
    inputs, results = None, None

    selected_location = st.selectbox("📍 Select Location", ["London", "Manchester", "Birmingham", "Leeds"])
    mode_selected = st.radio("📡 Select Data Mode", ["Mock Data", "Real-Time Data"])
    authority = st.selectbox("🏛️ Send Report To", ["Environment Agency", "DEFRA", "Ofwat", "Local Council"])
    scada_enabled = st.checkbox("Enable SCADA Integration for this Report", value=False)

    mock_mode = mode_selected == "Mock Data"

    inputs, results = None, None
    if st.button("🔍 Run Analysis for Report"):
        with st.spinner("Running Water LLM..."):
            inputs = get_real_time_inputs(selected_location)
            results = run_all_analyses(inputs, selected_location, scada_enabled)
    if results and inputs:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        st.markdown("### 🧾 Regulatory Report Summary")
        st.write(f"**Location:** {selected_location}")
        st.write(f"**Mode:** {'Simulated (Mock)' if mock_mode else 'Live Real-Time'}")
        st.write(f"**SCADA Integration:** {'Enabled' if scada_enabled else 'Disabled'}")
        st.write(f"**Timestamp:** {timestamp}")

        st.markdown("### 🔍 Snapshot of Sensor Inputs")
        for k, v in inputs.items():
            st.write(f"- **{k.replace('_', ' ').title()}**: {v}")

        st.markdown("### 📜 Key GenAI Outputs for Compliance")
        overflow = results.get("Overflow Prediction", "N/A")
        compliance = results.get("Compliance Check", "N/A")
        scada_feedback = results.get("SCADA Feedback", "N/A")

        st.markdown(f"- **Overflow Prediction:** {overflow}")
        st.markdown(f"- **Compliance Check:** {compliance}")
        st.markdown(f"- **SCADA Feedback:** {scada_feedback}")

        notes = st.text_area("✏️ Add any explanatory notes for the authority (optional):")

        report_md = f"""# Regulatory Report – Water LLM System

**Location:** {selected_location}  
**Mode:** {"Simulated (Mock)" if mock_mode else "Live Real-Time"}  
**SCADA Integration:** {"Enabled" if scada_enabled else "Disabled"}  
**Generated On:** {timestamp}  

## 🔧 Sensor Inputs
{chr(10).join([f"- {k.replace('_', ' ').title()}: {v}" for k, v in inputs.items()])}

## 📊 GenAI Outputs
- Overflow Prediction: {overflow}
- Compliance Check: {compliance}
- SCADA Feedback: {scada_feedback}

## 📝 Notes to Authority
{notes if notes else "No additional notes provided."}
"""

        st.download_button("📥 Download Report (.md)", report_md, file_name=f"regulatory_report_{selected_location.lower()}.md")

        if st.button(f"📤 Send to {authority}"):
            st.success(f"✅ Report successfully submitted to **{authority}** on {timestamp}")