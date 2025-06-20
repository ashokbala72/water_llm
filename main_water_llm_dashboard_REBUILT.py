
import streamlit as st
import json
from Water_llm_COMPLETE_balancer_PROD_READY import (
    post_scada_command,
    send_mqtt_message,
    send_opcua_command,
    send_modbus_command,
    fetch_weather_data,
    fetch_sensor_data,
    actuate_asset,
    call_gpt,
    calculate_overflow_risk,
    overflow_control,
    get_real_time_inputs,
    predict_overflow,
    dynamic_control_advice,
    detect_anomalies,
    compliance_check,
    run_all_analyses,
    get_logged_interventions,
    get_parameter_descriptions,
    generate_regulatory_report,
    recommend_infrastructure_upgrades,
    alert_operator,
    load_balance_tanks,
    suggest_action_for_risk,
    fetch_tank_config,
    forecast_weather_with_gpt,
    storm_response_coordinator,
    check_asset_availability
)

st.set_page_config(page_title="Water LLM Validator", layout="wide")
st.title("🧪 Water LLM Function Validator")

tabs = st.tabs(["📘 Overview", "🧪 Function Validator"])

with tabs[0]:
    st.header("📘 Function Diagnostics Overview")

    function_docs = {
        "post_scada_command": "Connects to SCADA and sends a control command via POST request.",
        "send_mqtt_message": "Sends MQTT message to broker/topic for control signaling.",
        "send_opcua_command": "Executes command on OPC-UA server node.",
        "send_modbus_command": "Writes command to Modbus-compatible PLC over TCP.",
        "fetch_weather_data": "Fetches weather forecast (rainfall, timestamp) from configured API.",
        "fetch_sensor_data": "Retrieves inflow rate and tank fill % from live or mock sensor API.",
        "actuate_asset": "Sends command to one or more control interfaces (SCADA/MQTT/OPC/PLC).",
        "call_gpt": "Uses GPT-4 to generate advisory or simulate weather/risk narratives.",
        "calculate_overflow_risk": "Assesses overflow risk from rainfall and tank fill.",
        "overflow_control": "Executes valve/pump actions based on overflow risk.",
        "get_real_time_inputs": "Merges weather + sensor inputs into single snapshot.",
        "predict_overflow": "Predicts if overflow is likely (True/False).",
        "dynamic_control_advice": "Suggests pump or valve tuning based on tank fill.",
        "detect_anomalies": "Detects sensor outliers like negative flow or tank overfill.",
        "compliance_check": "Determines if current state violates regulatory thresholds.",
        "run_all_analyses": "Executes prediction, risk, compliance, anomaly, advisory in one call.",
        "get_logged_interventions": "Returns recent actuation or intervention logs.",
        "get_parameter_descriptions": "Describes system config parameters (rainfall, fill % etc).",
        "generate_regulatory_report": "Creates formatted report with location, rainfall, compliance.",
        "recommend_infrastructure_upgrades": "Suggests structural fixes like tanks or delay buffers.",
        "alert_operator": "Sends warning to operator console for manual override.",
        "load_balance_tanks": "Checks and redistributes tank load using real capacities.",
        "suggest_action_for_risk": "Returns advisory action string based on risk level.",
        "fetch_tank_config": "Loads zone and capacity for each tank from tank_config.csv.",
        "forecast_weather_with_gpt": "Uses GPT-4 to predict weather and risks over next few days.",
        "storm_response_coordinator": "Full storm scenario manager: prediction, control, alert, reporting.",
        "check_asset_availability": "Validates if declared assets (e.g., pumps, valves) are operational as per config."
    }

    for fname, desc in function_docs.items():
        with st.expander(f"🔹 {fname}", expanded=False):
            st.markdown(f"- {desc}")

with tabs[1]:
    st.header("🧪 Validate Functions in Engine")
    location = st.selectbox("🌍 Select City for Tests", ["London", "Manchester", "Birmingham", "Leeds"])

    all_functions = {
        "post_scada_command": post_scada_command,
        "send_mqtt_message": send_mqtt_message,
        "send_opcua_command": send_opcua_command,
        "send_modbus_command": send_modbus_command,
        "fetch_weather_data": fetch_weather_data,
        "fetch_sensor_data": fetch_sensor_data,
        "actuate_asset": actuate_asset,
        "call_gpt": call_gpt,
        "calculate_overflow_risk": calculate_overflow_risk,
        "overflow_control": overflow_control,
        "get_real_time_inputs": get_real_time_inputs,
        "predict_overflow": predict_overflow,
        "dynamic_control_advice": dynamic_control_advice,
        "detect_anomalies": detect_anomalies,
        "compliance_check": compliance_check,
        "run_all_analyses": run_all_analyses,
        "get_logged_interventions": get_logged_interventions,
        "get_parameter_descriptions": get_parameter_descriptions,
        "generate_regulatory_report": generate_regulatory_report,
        "recommend_infrastructure_upgrades": recommend_infrastructure_upgrades,
        "alert_operator": alert_operator,
        "load_balance_tanks": load_balance_tanks,
        "suggest_action_for_risk": suggest_action_for_risk,
        "fetch_tank_config": fetch_tank_config,
        "forecast_weather_with_gpt": forecast_weather_with_gpt,
        "storm_response_coordinator": storm_response_coordinator,
        "check_asset_availability": check_asset_availability
    }

    for fname, fcall in all_functions.items():
        with st.expander(f"🔹 {fname}", expanded=False):
            try:
                with st.spinner("Running..."):
                    result = (
                        fcall(command='open_valve') if fname == 'actuate_asset'
                        else fcall('Describe tank risks and recommendations') if fname == 'call_gpt'
                        else fcall(10, 50) if fname == 'calculate_overflow_risk'
                        else fcall(location) if fname in [
                            'overflow_control', 'get_real_time_inputs', 'load_balance_tanks',
                            'recommend_infrastructure_upgrades', 'forecast_weather_with_gpt',
                            'storm_response_coordinator', 'check_asset_availability'
                        ]
                        else fcall(rainfall_mm=10, tank_fill_percent=50) if fname == 'predict_overflow'
                        else fcall({'tank_fill_percent': 95, 'inflow_rate_lps': 120}) if fname == 'detect_anomalies'
                        else fcall(rainfall_mm=85, overflow_triggered=True) if fname == 'compliance_check'
                        else fcall(location=location, rainfall_mm=85, risk_level='HIGH') if fname == 'generate_regulatory_report'
                        else fcall(65) if fname == 'dynamic_control_advice'
                        else fcall('HIGH') if fname == 'suggest_action_for_risk'
                        else fcall('London') if fname == 'fetch_tank_config'
                        else fcall()
                    )

                    st.success("✅ Function executed successfully")
                    if isinstance(result, (dict, list)):
                        st.json(result)
                    elif isinstance(result, str):
                        try:
                            st.json(json.loads(result))
                        except:
                            st.code(result)
                    else:
                        st.write(result)

            except Exception as e:
                st.error(f"❌ Error while executing `{fname}`\n\n{str(e)}")
