import streamlit as st
import inspect
import json
import pandas as pd
from Water_llm_ENGINE_WITH_CONTEXTUAL_ADVISORY import *

st.set_page_config(layout="wide")
st.title("💧 Water LLM Engine Dashboard")

# Fetch all user-defined functions from the engine
engine_funcs = [obj for name, obj in globals().items() if inspect.isfunction(obj) and obj.__module__ == "Water_llm_ENGINE_WITH_CONTEXTUAL_ADVISORY"]
func_map = {f.__name__: f for f in engine_funcs}

# UI Tabs
tab1, tab2 = st.tabs(["📌 Overview", "🧪 Function Validator"])

# Overview Tab
with tab1:
    st.header("📌 Engine Function Overview")
    for fname, func in func_map.items():
        with st.expander(f"🔧 {fname}() - Click to expand"):
            doc = inspect.getdoc(func)
            st.markdown(f"**Purpose:**\n> {doc if doc else 'No docstring provided.'}")
            st.markdown(f"**Integration Points:**\n> Typically involves DB/API/CSV/SCADA/GPT based on implementation.")
            st.markdown(f"**Post-Execution:**\n> Logs actions, returns results, or triggers infrastructure commands.")

# Validator Tab
with tab2:
    st.header("🧪 Validate All Engine Functions")
    city = st.selectbox("🌍 Select City for Testing", ["London", "Manchester", "Leeds", "Birmingham"])

    dummy_inputs = {
        'location': city,
        'command': 'test_command',
        'token': 'dummy_token',
        'scada_api': 'http://example.com/api',
        'broker': 'localhost',
        'topic': 'test/topic',
        'url': 'opc.tcp://localhost:4840',
        'ip': '127.0.0.1',
        'port': 502,
        'rain_mm': 30,
        'tank_fill_percent': 95,
        'rainfall_mm': 85,
        'overflow_triggered': True,
        'sensor_data': {'tank_fill_percent': 101, 'inflow_rate_lps': -5},
        'risk_level': 'HIGH',
        'horizon_days': 3,
        'message': 'Test alert'
    }

    dummy_inputs['rainfall_mm'] = int(dummy_inputs['rainfall_mm'])
    dummy_inputs['tank_fill_percent'] = int(dummy_inputs['tank_fill_percent'])

    for fname, func in func_map.items():
        with st.expander(f"🧪 {fname}() - Click to run and view result"):
            try:
                sig = inspect.signature(func)
                args = {}
                for param in sig.parameters.values():
                    if param.name in dummy_inputs:
                        args[param.name] = dummy_inputs[param.name]
                    elif param.default == inspect.Parameter.empty:
                        args[param.name] = city

                result = func(**args) if args else func()
                st.success("✅ Function executed successfully")

                if fname == "check_asset_availability" and isinstance(result, dict) and "assets" in result:
                    st.subheader("🔍 Asset Availability Details")
                    st.json(result["assets"])
                elif fname == "get_river_impact_severity" and isinstance(result, list):
                    st.subheader("🌊 River Impact Zones")
                    st.dataframe(pd.DataFrame(result))
                elif isinstance(result, (dict, list)):
                    st.json(result)
                else:
                    st.write(result)

            except Exception as e:
                st.error(f"❌ Execution failed: {e}")
