# utils/sensor_handler.py
import json
import os
from datetime import datetime

SENSOR_LOG_FILE = "data/sensor_log.json"
LATEST_STATUS_FILE = "data/latest_status.json"

def save_sensor_status(status):
    # 타임스탬프 추가
    status_with_time = status.copy()
    status_with_time["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 최신 상태 저장
    with open(LATEST_STATUS_FILE, "w") as f:
        json.dump(status_with_time, f)

    # 이력 저장
    logs = []
    if os.path.exists(SENSOR_LOG_FILE):
        with open(SENSOR_LOG_FILE, "r") as f:
            logs = json.load(f)
    logs.append(status_with_time)
    with open(SENSOR_LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def get_latest_status():
    try:
        with open(LATEST_STATUS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"error": "No sensor data available"}

def get_sensor_history(limit=100):
    try:
        with open(SENSOR_LOG_FILE, "r") as f:
            logs = json.load(f)
        return logs[-limit:]
    except:
        return []
