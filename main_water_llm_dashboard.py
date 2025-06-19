
import streamlit as st
from Water_llm_COMPLETE import (
    run_all_analyses,
    storm_response_coordinator,
    forecast_weather_with_gpt
)

st.set_page_config(page_title="💧 Water LLM Dashboard", layout="wide")

st.title("💧 Water LLM Monitoring & Forecasting")

# Location selection
location = st.selectbox("🌍 Select Monitoring Location", ["London", "Manchester", "Birmingham", "Leeds"])

st.markdown("---")
tab1, tab2, tab3 = st.tabs(["📊 Real-Time Analysis", "⛈️ Storm Response", "📡 Forecast Advisory"])

with tab1:
    st.header("📊 Real-Time Water System Analysis")
    if st.button("🔍 Run Full Analysis"):
        with st.spinner("Running diagnostics..."):
            results = run_all_analyses(location)
        st.success("✅ Analysis complete")

        st.subheader("📥 Input Snapshot")
        st.json(results["inputs"])

        st.subheader("🛑 Overflow Risk Score")
        st.code(results["overflow_risk_score"])

        st.subheader("💡 Dynamic Control Advisory")
        st.code(results["control_advice"])

        st.subheader("⚠️ Anomalies Detected")
        if results["anomalies"]:
            st.error("\n".join(results["anomalies"]))
        else:
            st.success("No anomalies detected.")

        st.subheader("✅ Compliance Status")
        st.code(results["compliance_status"])

        st.subheader("🏗️ Infrastructure Recommendations")
        for upgrade in results["infrastructure_recommendations"]:
            st.warning(upgrade)

        st.subheader("🤖 GenAI Advisory")
        st.markdown(results["genai_advisory"])

with tab2:
    st.header("⛈️ Trigger Storm Response")
    if st.button("🚨 Initiate Storm Protocol"):
        with st.spinner("Coordinating storm response..."):
            storm_result = storm_response_coordinator(location)
        st.success("✅ Storm response executed")

        st.subheader("📥 Sensor + Weather Snapshot")
        st.json(storm_result["inputs"])

        st.subheader("🛑 Risk Level")
        st.code(storm_result["risk_level"])

        st.subheader("⚙️ Control Advice")
        st.code(storm_result["control_advice"])

        st.subheader("🚨 Alert Sent")
        st.code(storm_result["alert_sent"])

        st.subheader("✅ Compliance Check")
        st.code(storm_result["compliance_status"])

        st.subheader("📋 Regulatory Report")
        st.text(storm_result["regulatory_report"])

        st.subheader("🏗️ Infrastructure Upgrades")
        for u in storm_result["infra_upgrades"]:
            st.warning(u)

        st.subheader("🤖 GenAI Advisory")
        st.markdown(storm_result["genai_advisory"])

with tab3:
    st.header("📡 GPT-Based Weather & Overflow Forecast")
    horizon = st.slider("📅 Forecast Days", min_value=1, max_value=5, value=3)
    if st.button("📈 Generate Forecast"):
        with st.spinner("Fetching GenAI forecast..."):
            forecast = forecast_weather_with_gpt(location, horizon_days=horizon)
        st.success("✅ Forecast complete")
        st.markdown(forecast)
