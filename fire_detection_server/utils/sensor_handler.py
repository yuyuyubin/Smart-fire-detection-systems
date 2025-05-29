import json
import os
from datetime import datetime

SENSOR_LOG_PATH = "data/sensor_log.json"
LATEST_STATUS_PATH = "data/latest_status.json"

def save_sensor_data(data: dict):
    os.makedirs("data", exist_ok=True)
    data_with_ts = {"timestamp": datetime.now().isoformat(), **data}
    with open(LATEST_STATUS_PATH, 'w') as f:
        json.dump(data_with_ts, f)

    logs = []
    if os.path.exists(SENSOR_LOG_PATH):
        with open(SENSOR_LOG_PATH, 'r') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    logs.append(data_with_ts)
    with open(SENSOR_LOG_PATH, 'w') as f:
        json.dump(logs, f, indent=2)

def get_latest_status():
    if os.path.exists(LATEST_STATUS_PATH):
        with open(LATEST_STATUS_PATH, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def get_sensor_history():
    if os.path.exists(SENSOR_LOG_PATH):
        with open(SENSOR_LOG_PATH, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []
