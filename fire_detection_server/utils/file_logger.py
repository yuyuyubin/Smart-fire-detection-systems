import json
import os

LATEST_RESULT_PATH = "data/latest_result.json"
FIRE_LOG_PATH = "data/fire_log.json"
MAX_LOG_COUNT = 1000  # 최대 저장할 로그 개수

def save_result_json(data: dict):
    os.makedirs("data", exist_ok=True)
    with open(LATEST_RESULT_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def append_logs(data: dict):
    os.makedirs("data", exist_ok=True)
    logs = []
    if os.path.exists(FIRE_LOG_PATH):
        with open(FIRE_LOG_PATH, 'r') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    logs.append(data)

    # 최대 로그 개수 초과 시 오래된 로그 삭제
    if len(logs) > MAX_LOG_COUNT:
        logs = logs[-MAX_LOG_COUNT:]

    with open(FIRE_LOG_PATH, 'w') as f:
        json.dump(logs, f, indent=2)

def get_latest_result():
    if os.path.exists(LATEST_RESULT_PATH):
        with open(LATEST_RESULT_PATH, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def get_fire_events():
    if os.path.exists(FIRE_LOG_PATH):
        with open(FIRE_LOG_PATH, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []
