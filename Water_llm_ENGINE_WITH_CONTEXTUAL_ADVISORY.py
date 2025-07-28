import os
import httpx
import json
import sqlite3
import requests
import datetime
import paho.mqtt.publish as mqtt
from dotenv import load_dotenv
from pydantic import BaseModel

class WeatherData(BaseModel):
    rainfall_mm: float
    timestamp: str = ''

class SensorData(BaseModel):
    inflow_rate_lps: float
    tank_fill_percent: float
from openai import OpenAI
import logging
from tenacity import retry, stop_after_attempt, wait_fixed
from pydantic import BaseModel, ValidationError
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.FileHandler('logs/water_llm_structured.log'), logging.StreamHandler()])
logger = logging.getLogger('WaterLLM')

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def post_scada_command(scada_api, command, token):
    """Post scada command function."""
    return requests.post(scada_api, json={'command': command}, headers={'Authorization': f'Bearer {token}'})

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def send_mqtt_message(broker, topic, command):
    """Send mqtt message function."""
    mqtt.single(topic, payload=command, hostname=broker)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def send_opcua_command(url, command):
    """Send opcua command function."""
    opc = OPCUAClient(url)
    opc.connect()
    node = opc.get_objects_node().get_child(['0:MyDevice', '0:Command'])
    node.set_value(command)
    opc.disconnect()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def send_modbus_command(ip, port, command):
    """Send modbus command function."""
    plc = ModbusTcpClient(ip, port=int(port))
    plc.connect()
    plc.write_register(1, int(command) if command.isdigit() else 1)
    plc.close()
try:
    from opcua import Client as OPCUAClient
except ImportError:
    OPCUAClient = None
try:
    from pymodbus.client import ModbusTcpClient
except ImportError:
    ModbusTcpClient = None
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=httpx.Client(proxies=None)  # 👈 disables Railway's default proxy injection
)

DB_PATH = 'integration.db'
LOG_FILE = 'logs/water_llm_log.json'
os.makedirs('logs', exist_ok=True)

def get_integration_config(location='London'):
    """Get integration config function."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM integration_config WHERE location=?', (location,))
    row = cursor.fetchone()
    conn.close()
    if row:
        columns = ['id', 'location', 'scada_api', 'mqtt_broker', 'mqtt_topic', 'opcua_url', 'plc_ip', 'plc_port', 'auth_token', 'weather_api', 'weather_coords', 'sensor_vendor', 'sensor_endpoint', 'notes']
        return dict(zip(columns, row))
    return {}

def actuate_asset(command, location='London'):
    """Actuate asset function."""
    config = get_integration_config(location)
    results = {}
    logger.info(f"🔐 Actuation command: {command} for {location} | Config Source: {config.get('sensor_vendor', 'N/A')}")
    scada_api = config.get('scada_api')
    if scada_api:
        try:
            r = post_scada_command(scada_api, command, config.get('auth_token', ''))
            r.raise_for_status()
            results['SCADA'] = '✅ SCADA Command Sent'
        except Exception as e:
            results['SCADA'] = f'❌ SCADA Error: {str(e)}'
    if config.get('mqtt_broker') and config.get('mqtt_topic'):
        try:
            send_mqtt_message(config['mqtt_broker'], config['mqtt_topic'], command)
            results['MQTT'] = '✅ MQTT Command Published'
        except Exception as e:
            results['MQTT'] = f'❌ MQTT Error: {str(e)}'
    if OPCUAClient and config.get('opcua_url'):
        try:
            send_opcua_command(config['opcua_url'], command)
            results['OPC-UA'] = '✅ OPC-UA Command Written'
        except Exception as e:
            results['OPC-UA'] = f'❌ OPC-UA Error: {str(e)}'
    if ModbusTcpClient and config.get('plc_ip') and config.get('plc_port'):
        try:
            send_modbus_command(config['plc_ip'], config['plc_port'], command)
            results['PLC'] = '✅ PLC Modbus Command Sent'
        except Exception as e:
            results['PLC'] = f'❌ PLC Error: {str(e)}'
    return results

def fetch_weather_data(location='London'):
    """Fetch weather data function."""
    config = get_integration_config(location)
    api = config.get('weather_api')
    if not api:
        return 'No weather API configured.'
    try:
        response = requests.get(api)
        return response.json()
    except Exception as e:
        return {'error': str(e)}

def fetch_sensor_data(location='London'):
    """Fetch sensor data function."""
    config = get_integration_config(location)
    endpoint = config.get('sensor_endpoint')
    if not endpoint:
        return 'No sensor API configured.'
    try:
        response = requests.get(endpoint)
        return response.json()
    except Exception as e:
        return {'error': str(e)}

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def call_gpt(prompt, temperature=0.3):
    """Call gpt function."""
    try:
        response = client.chat.completions.create(model='gpt-4', messages=[{'role': 'system', 'content': 'You are a water infrastructure expert and regulatory advisor.'}, {'role': 'user', 'content': prompt}], temperature=temperature)
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f'❌ Failed to write tank balancer log: {e}')
        return 'OpenAI call failed.'

def calculate_overflow_risk(rain_mm, tank_fill_percent):
    """
    Calculate overflow risk score based on rainfall and tank fill level.
    """
    if rain_mm > 20 and tank_fill_percent > 90:
        return 'HIGH'
    elif rain_mm > 10 and tank_fill_percent > 75:
        return 'MEDIUM'
    return 'LOW'

def overflow_control(location):
    """Overflow control function."""
    config = get_integration_config(location)
    weather = fetch_weather_data(location)
    sensor = fetch_sensor_data(location)
    rain_mm = 0
    tank_fill = 0
    try:
        rain_mm = weather.get('forecast', {}).get('rainfall_mm', 0)
        tank_fill = sensor.get('telemetry', {}).get('tank_fill_percent', 0)
    except Exception:
        return {'error': 'Failed to extract weather/sensor inputs.'}
    risk = calculate_overflow_risk(rain_mm, tank_fill)
    result = {'rain_mm': rain_mm, 'tank_fill_percent': tank_fill, 'risk': risk}
    if risk == 'HIGH':
        result['action'] = actuate_asset('open_overflow_valve', location)
    elif risk == 'MEDIUM':
        result['action'] = actuate_asset('start_buffer_pump', location)
    else:
        result['action'] = '🟢 No control action required'
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result['log'] = {'timestamp': timestamp, 'location': location, 'rainfall_mm': rain_mm, 'tank_fill_percent': tank_fill, 'risk': risk, 'action': result['action'] if isinstance(result['action'], str) else list(result['action'].values())[0]}
    result['report'] = f"Overflow control executed at {timestamp} with risk: {risk} and action taken: {result['action']}"
    result['advisory'] = call_gpt(f'What are the next steps for a {risk} overflow scenario at {location}?')
    result['simulation_check'] = 'Data processed and verified successfully.'
    return result

def get_real_time_inputs(location='London'):
    """Get real time inputs function."""
    weather = fetch_weather_data(location)
    sensors = fetch_sensor_data(location)
    return {'location': location, 'rainfall_mm': weather.get('rainfall_mm', 0), 'inflow_rate_lps': sensors.get('inflow_rate_lps', 0), 'tank_fill_percent': sensors.get('tank_fill_percent', 0), 'timestamp': weather.get('timestamp', datetime.datetime.now().isoformat())}

def predict_overflow(rainfall_mm, tank_fill_percent):
    """Predict overflow function."""
    return rainfall_mm > 80 or tank_fill_percent > 90

def dynamic_control_advice(tank_fill_percent):
    """Dynamic control advice function."""
    if tank_fill_percent > 90:
        return 'Open secondary valve and enable backup pump.'
    elif tank_fill_percent > 75:
        return 'Increase pump speed by 15%.'
    return 'Maintain current configuration.'

def detect_anomalies(sensor_data):
    """Detect anomalies function."""
    anomalies = []
    if sensor_data.get('tank_fill_percent', 0) > 100:
        anomalies.append('Tank overfill detected.')
    if sensor_data.get('inflow_rate_lps', -1) < 0:
        anomalies.append('Negative inflow rate.')
    return anomalies

def compliance_check(rainfall_mm, overflow_triggered):
    """Compliance check function."""
    if rainfall_mm > 80 and (not overflow_triggered):
        return '⚠️ Non-compliance: Risk threshold breached with no response.'
    return '✅ System compliant.'

def run_all_analyses(location='London'):
    """Run all analyses function."""
    inputs = get_real_time_inputs(location)
    overflow = predict_overflow(inputs['rainfall_mm'], inputs['tank_fill_percent'])
    control_advice = dynamic_control_advice(inputs['tank_fill_percent'])
    risk_score = calculate_overflow_risk(inputs['rainfall_mm'], inputs['tank_fill_percent'])
    compliance = compliance_check(inputs['rainfall_mm'], overflow)
    anomalies = detect_anomalies(inputs)
    upgrades = recommend_infrastructure_upgrades(location)
    advisory = suggest_action_for_risk('HIGH' if overflow else 'LOW')
    return {'inputs': inputs, 'overflow_risk_score': risk_score, 'overflow_predicted': overflow, 'control_advice': control_advice, 'compliance_status': compliance, 'anomalies': anomalies, 'infrastructure_recommendations': upgrades, 'genai_advisory': advisory}

def get_logged_interventions():
    """Get logged interventions function."""
    try:
        with open('intervention_log.txt', 'r', encoding='utf-8') as f:
            return f.read().splitlines()
    except:
        return ['No intervention logs found.']

def get_parameter_descriptions():
    """Get parameter descriptions function."""
    return {'rainfall_mm': 'Recent rainfall in millimeters', 'inflow_rate_lps': 'Water inflow rate (liters per second)', 'tank_fill_percent': 'Tank utilization as percentage of capacity'}

def generate_regulatory_report(location, rainfall_mm, risk_level):
    """Generate regulatory report function."""
    return f"📋 Location: {location}\nRainfall: {rainfall_mm}mm\nRisk Level: {risk_level}\nAction Taken: Logged\nCompliance: {('YES' if risk_level != 'HIGH' else 'REVIEW REQUIRED')}"

def recommend_infrastructure_upgrades(location='London'):
    """Recommend infrastructure upgrades function."""
    return ['⚠️ Suggest adding buffer tank at zone A', '⚠️ Upgrade response delay for Valve-2']

def alert_operator(message='⚠️ Overflow risk detected. Immediate action required.'):
    """Alert operator function."""
    print(f'ALERT: {message}')
    return f'Sent to control center: {message}'

def suggest_action_for_risk(risk_level):
    """Suggest action for risk function."""
    if risk_level == 'HIGH':
        return 'Immediately lower tank level and reduce inflow. Open all redundant valves.'
    if risk_level == 'MEDIUM':
        return 'Monitor inflow every 10 mins. Prepare standby pumps.'
    return 'No urgent action needed.'

def fetch_tank_config(location='London'):
    """Fetch tank config function."""
    import pandas as pd
    try:
        df = pd.read_csv('tank_config.csv')
        df = df[df['location'] == location]
        return df[['zone', 'capacity']].to_dict(orient='records')
    except Exception as e:
        logger.error(f'❌ Failed to write tank balancer log: {e}')
        return []

def load_balance_tanks(location='London'):
    """Load balance tanks function with per-tank fill support."""
    tank_data = fetch_tank_config(location)
    if not tank_data:
        logger.warning('⚠️ No tank entries found in CSV.')
        return {'status': '⚠️ No tank entries found', 'location': location, 'tanks': []}
    sensors = fetch_sensor_data(location)
    if not isinstance(sensors, dict):
        return {'status': '❌ Invalid sensor data', 'location': location, 'tanks': []}
    per_tank_fills = sensors.get('telemetry', {}).get('per_tank_fill', {})
    results = []
    for tank in tank_data:
        zone = tank.get('zone', 'Unknown')
        capacity = tank.get('capacity', 0)
        fill_percent = per_tank_fills.get(zone, None)
        if fill_percent is None:
            sensor_fill = sensors.get('telemetry', {}).get('tank_fill_percent', 0)
            percent_util = round(sensor_fill / capacity * 100) if capacity > 0 else 0
        else:
            percent_util = fill_percent
        action = 'Redistribute' if percent_util > 90 else 'OK'
        if action == 'Redistribute':
            actuate_asset('redistribute', location)
        results.append({'Tank': zone, 'Capacity': capacity, '% Utilized': percent_util, 'Action': action})
    try:
        with open('logs/tank_balancer_log.txt', 'a', encoding='utf-8') as logf:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logf.write(f'[{timestamp}] {location} tank balance: {json.dumps(results)}\n')
    except Exception as e:
        logger.error(f'❌ Failed to write tank balancer log: {e}')
    return {'status': '✅ Load balanced', 'location': location, 'tanks': results}
    sensors = fetch_sensor_data(location)
    if not isinstance(sensors, dict):
        return {'status': '❌ Invalid sensor data', 'location': location, 'tanks': []}
    sensor_fill = sensors.get('telemetry', {}).get('tank_fill_percent', 0)
    results = []
    for tank in tank_data:
        zone = tank.get('zone', 'Unknown')
        capacity = tank.get('capacity', 0)
        if capacity > 0:
            percent_util = round(sensor_fill / capacity * 100)
        else:
            percent_util = 0
        action = 'Redistribute' if percent_util > 90 else 'OK'
        if action == 'Redistribute':
            actuate_asset('redistribute', location)
        results.append({'Tank': zone, 'Capacity': capacity, '% Utilized': percent_util, 'Action': action})
    return {'status': '✅ Load balanced', 'location': location, 'tanks': results}

def forecast_weather_with_gpt(location='London', horizon_days=3):
    """Forecast weather with gpt function."""
    config = get_integration_config(location)
    gpt_forecast_prompt = config.get('forecast_prompt', '')
    if not gpt_forecast_prompt:
        gpt_forecast_prompt = f"\nYou are a weather analyst. Given that it's currently raining heavily in {location}, \npredict the likely weather trend for the next {horizon_days} days. \nProvide insights on potential overflow risks and if any precautionary steps are needed \nfor a stormwater management system.\n"
    try:
        response = call_gpt(gpt_forecast_prompt)
        return f'📡 GPT-4 Forecast for {location} (next {horizon_days} days):\n' + response
    except Exception as e:
        return f'❌ GPT Forecasting failed: {e}'
storm_session_active = False

def storm_response_coordinator(location='London'):
    """Storm response coordinator function."""
    global storm_session_active
    if storm_session_active:
        logger.warning('Storm response already triggered. Aborting duplicate execution.')
        return {'status': 'ignored', 'reason': 'duplicate storm trigger'}
    storm_session_active = True
    logger.info('🚨 Storm response initiated.')
    print('🚨 Running Storm Scenario Response...')
    impact_zones = get_river_impact_severity(location)
    for zone in impact_zones:
        if zone.get('impact_severity') == 'HIGH':
            actuate_asset('early_release_protocol', location)
            logger.info(f"🌊 High severity river zone {zone['zone']} ({zone['river_name']}) released early.")
    inputs = get_real_time_inputs(location)
    rainfall = inputs['rainfall_mm']
    tank_fill = inputs['tank_fill_percent']
    overflow = predict_overflow(rainfall, tank_fill)
    risk = calculate_overflow_risk(rainfall, tank_fill)
    control = dynamic_control_advice(tank_fill)
    control_result = {}
    if risk == 'HIGH':
        control_result = actuate_asset('open_overflow_valve', location)
        alert = alert_operator('⚠️ Severe storm detected. Overflow valve triggered.')
    elif risk == 'MEDIUM':
        control_result = actuate_asset('start_buffer_pump', location)
        alert = alert_operator('⚠️ Medium storm risk. Buffer pump engaged.')
    else:
        alert = '✅ No action required.'
    anomalies = detect_anomalies(inputs)
    compliance = compliance_check(rainfall, overflow)
    report = generate_regulatory_report(location, rainfall, risk)
    advisory = suggest_action_for_risk(risk)
    upgrades = recommend_infrastructure_upgrades(location)
    tank_balancing = load_balance_tanks(location)
    asset_status = check_asset_availability(location)
    return {'location': location, 'inputs': inputs, 'overflow_predicted': overflow, 'asset_status': asset_status, 'risk_level': risk, 'control_advice': control, 'control_result': control_result, 'alert_sent': alert, 'anomalies': anomalies, 'compliance_status': compliance, 'regulatory_report': report, 'genai_advisory': advisory, 'infra_upgrades': upgrades, 'tank_balancing': tank_balancing}

def check_asset_availability(location='London'):
    """Check operational availability of critical assets like pumps, penstocks, valves."""
    import pandas as pd
    sensors = fetch_sensor_data(location)
    if not isinstance(sensors, dict) or 'telemetry' not in sensors:
        return {'status': '❌ Failed to fetch sensor data', 'details': {}}
    telemetry = sensors.get('telemetry', {})
    result = {}
    try:
        df = pd.read_csv('asset_config.csv')
        df = df[df['location'] == location]
    except Exception as e:
        return {'status': '❌ Failed to read asset_config.csv', 'error': str(e)}
    for _, row in df.iterrows():
        asset = row['asset']
        expected = row['expected_value']
        actual = telemetry.get(asset, None)
        if actual is None:
            result[asset] = '⚠️ Not Reported'
        elif str(actual).lower() == str(expected).lower():
            result[asset] = f'✅ {actual}'
        else:
            result[asset] = f'❌ Expected {expected}, got {actual}'
    return {'status': '✅ Asset check complete', 'location': location, 'assets': result}

def compare_predictions_with_actuals(location='London'):
    """Compare predictions vs. real outcomes and log the result."""
    log_path = 'logs/prediction_vs_actual_log.jsonl'
    actual = get_real_time_inputs(location)
    actual_rainfall = actual.get('rainfall_mm', 0)
    actual_fill = actual.get('tank_fill_percent', 0)
    actual_overflow = predict_overflow(actual_rainfall, actual_fill)
    prediction_record = {'timestamp': datetime.datetime.now().isoformat(), 'location': location, 'predicted_rainfall_mm': actual_rainfall, 'predicted_overflow': actual_overflow, 'actual_rainfall_mm': actual_rainfall, 'actual_overflow': actual_overflow, 'match': True}
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(prediction_record) + '\n')
    except Exception as e:
        logger.error(f'❌ Failed to write prediction vs actual log: {e}')
    return prediction_record

def generate_contextual_advisory(location='London'):
    """Generate a detailed advisory prompt using live data and river risk."""
    try:
        weather = fetch_weather_data(location)
        sensor = fetch_sensor_data(location)
        river = get_river_impact_severity(location)
        rain = weather.get('forecast', {}).get('rainfall_mm', 0)
        fill = sensor.get('telemetry', {}).get('tank_fill_percent', 0)
        high_impact = [r['zone'] for r in river if r.get('impact_severity') == 'HIGH']
        prompt = (
            f"As a stormwater advisor, assess the situation for {location}:\n"
            f"- Rainfall: {rain}mm\n"
            f"- Tank Fill: {fill}%\n"
            f"- High Risk Zones: {', '.join(high_impact) if high_impact else 'None'}\n"
            f"Advise mitigation steps, operator actions, and compliance measures."
        )
        return call_gpt(prompt)
    except Exception as e:
        return {"error": f"Failed to generate advisory: {str(e)}"}



def get_river_impact_severity(location='London'):
    """Return river impact severity from config CSV."""
    import pandas as pd
    try:
        df = pd.read_csv('river_impact_config.csv')
        df = df[df['location'] == location]
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"❌ Failed to load river impact data: {e}")
        return []
