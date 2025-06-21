
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🌪️ Deep Storm Simulator — Full Engine Function Walkthrough")

if st.button("🚨 Begin Full Mocked Storm Simulation"):
    location = "London"
    st.header("📍 Scenario Context")
    st.markdown(f"""
    - **Location**: {location}  
    - **Rainfall**: 85 mm  
    - **Tank Fill**: 95%  
    - **Inflow Rate**: 110 lps  
    - **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
    """)

    st.header("🌊 River Impact Assessment (`get_river_impact_severity`)")
    river_df = pd.DataFrame([
        {"zone": "North", "river_name": "Thames", "impact_severity": "HIGH"},
        {"zone": "South", "river_name": "Lee", "impact_severity": "MEDIUM"}
    ])
    st.dataframe(river_df)
    st.markdown("- 🔄 Early release initiated for **Thames** → `actuate_asset('early_release_protocol')`")

    st.header("📡 Real-Time Inputs (`get_real_time_inputs`)")
    st.json({
        "rainfall_mm": 85,
        "tank_fill_percent": 95,
        "inflow_rate_lps": 110
    })

    st.header("⚠️ Overflow Prediction & Risk Calculation — Full Breakdown (`predict_overflow`, `calculate_overflow_risk`)")
    st.subheader("📈 Step 1: Predict Overflow")
    st.markdown("- Condition: Rainfall > 80 or Tank Fill > 90 → Overflow = True")
    st.subheader("🔥 Step 2: Calculate Risk Level")
    st.markdown("- Risk = HIGH (Rainfall > 20 and Fill > 90)")
    st.markdown("- Function: `predict_overflow`, `calculate_overflow_risk`")
    st.markdown("- Overflow: `True`, Risk Level: `HIGH`")

    st.header("🧠 Dynamic Control Advice (`dynamic_control_advice`)")
    st.markdown("- Advice: `Open secondary valve and enable backup pump`")

    st.header("📟 Actuation Commands (`actuate_asset`)")
    st.json({
        "SCADA": "✅ open_overflow_valve",
        "MQTT": "✅ topic: storm/overflow",
        "OPC-UA": "✅ node 2041",
        "PLC": "✅ Modbus coil set"
    })

    st.header("🚨 Operator Alert (`alert_operator`)")
    st.success("⚠️ Severe storm detected. Overflow valve triggered.")

    st.header("🚨 Anomaly Detection — Full Breakdown (`detect_anomalies`)")
    st.subheader("🔍 Step 1: Read Sensor Telemetry")
    st.markdown("- Inflow rate: -1 → Invalid")
    st.markdown("- Tank fill > 100% → Overfill")
    st.subheader("⚠️ Step 2: Flag Anomalies")
    st.markdown("- Output: ['Negative inflow', 'Overfill detected']")
    st.markdown("- Detected: Negative inflow, overfill >100%")

    st.header("🧾 Compliance Check — Full Breakdown (`compliance_check`)")
    st.subheader("📋 Step 1: Evaluate Overflow vs Rainfall Threshold")
    st.markdown("- Rainfall > 80 and Overflow Triggered → ✅ Compliant")
    st.subheader("🧮 Step 2: Final Compliance Result")
    st.markdown("- Result: System Compliant")
    st.markdown("- Status: ✅ System compliant")

    st.header("📄 Regulatory Report (`generate_regulatory_report`)")
    st.code("📋 Location: London\nRainfall: 85mm\nRisk: HIGH\nCompliance: REVIEW REQUIRED")

    st.header("📢 Risk-Based GenAI Advisory (`suggest_action_for_risk`)")
    st.markdown("- Action: Lower level, reduce inflow, open valves")

    st.header("🏗️ Infrastructure Upgrade Suggestions")
    st.markdown("- Add buffer tank @ Zone A")
    st.markdown("- Upgrade delay for Valve-2")

    st.header("🛢️ Tank Load Balancer — Full Breakdown")

    st.subheader("📥 Step 1: Load Tank Configuration (`fetch_tank_config`)")
    st.json([
        {"zone": "North", "capacity": 100},
        {"zone": "South", "capacity": 150}
    ])

    st.subheader("📥 Step 2: Fetch Sensor Data (`fetch_sensor_data`)")
    st.json({
        "telemetry": {
            "tank_fill_percent": 95,
            "per_tank_fill": {
                "North": 95,
                "South": 60
            }
        }
    })

    st.subheader("🧮 Step 3: Compute Utilization (`load_balance_tanks` logic)")
    tank_df = pd.DataFrame([
        {"Tank": "North", "Capacity": 100, "Fill %": 95, "Action": "Redistribute"},
        {"Tank": "South", "Capacity": 150, "Fill %": 60, "Action": "OK"}
    ])
    st.dataframe(tank_df)

    st.subheader("⚙️ Step 4: Actuate if Needed")
    st.json({
        "Tank": "North",
        "Command": "redistribute",
        "SCADA": "✅ Sent",
        "MQTT": "✅ Sent",
        "OPC-UA": "✅ Sent",
        "PLC": "✅ Sent"
    })

    st.subheader("📝 Step 5: Log Output (`tank_balancer_log.txt`)")
    st.code("""[2025-06-21 00:14:02] London tank balance:
[
  {"Tank": "North", "Capacity": 100, "% Utilized": 95, "Action": "Redistribute"},
  {"Tank": "South", "Capacity": 150, "% Utilized": 60, "Action": "OK"}
]""")

    st.header("🏭 Asset Availability Check — Full Breakdown (`check_asset_availability`)")
    st.subheader("📥 Step 1: Load Asset Config (`asset_config.csv`)")
    st.markdown("- Expected Values:")
    st.json({
        "Pump-A": "Available",
        "Valve-B": "Operational",
        "Drainage-C": "Clear"
    })
    st.subheader("📡 Step 2: Fetch Telemetry (`fetch_sensor_data`)")
    st.json({
        "telemetry": {
            "Pump-A": "Available",
            "Valve-B": "Operational",
            "Drainage-C": "Blocked"
        }
    })
    st.subheader("🔎 Step 3: Compare Actual vs Expected")
    st.json({
        "Pump-A": "✅ Available",
        "Valve-B": "✅ Operational",
        "Drainage-C": "❌ Expected Clear, got Blocked"
    })
    st.subheader("⚠️ Step 4: Trigger Advisory if Blocked")
    st.warning("⚠️ Drainage-C is blocked. Operator alert triggered.")
    st.markdown("- Suggested Action: Inspect blockage. Activate bypass if required.")
    st.json({
        "Pump-A": "✅ Available",
        "Valve-B": "✅ Operational",
        "Drainage-C": "❌ Blocked"
    })

    st.header("🧠 Contextual Advisory (`generate_contextual_advisory`, `call_gpt`)")
    st.markdown("> GPT: Activate overflow channels. Notify North. Prep pump capacity.")

    st.header("📊 Compare Predictions vs Actuals")
    st.json({
        "predicted_overflow": True,
        "actual_overflow": True,
        "match": True
    })

    st.header("📝 Intervention Log")
    st.markdown("- Valve-B opened at 14:03")
    st.markdown("- Alert sent to Thames operator")

    st.header("🔄 Forecast via GPT")
    st.markdown("> Rain expected for 3 days. 90mm/day. Risk: sustained overflow.")

    st.header("📚 Parameter Descriptions")
    st.json({
        "rainfall_mm": "Rainfall (mm)",
        "inflow_rate_lps": "Inflow rate (lps)",
        "tank_fill_percent": "Tank fill %"
    })

    st.success("✅ All 28 Functions Simulated — Internal Logic Shown for Tank Balancer")
