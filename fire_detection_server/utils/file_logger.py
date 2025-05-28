import json, os

FIRE_LOG_FILE = "data/fire_log.json"
LATEST_RESULT_FILE = "data/latest_result.json"

def save_result_json(result):
    with open(LATEST_RESULT_FILE, "w") as f:
        json.dump(result, f)

def get_latest_result():
    try:
        with open(LATEST_RESULT_FILE) as f:
            return json.load(f)
    except:
        return {"fire_detected": False}

def append_logs(result):
    logs = []
    if os.path.exists(FIRE_LOG_FILE):
        with open(FIRE_LOG_FILE, "r") as f:
            logs = json.load(f)
    logs.append(result)
    with open(FIRE_LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def get_fire_events():
    try:
        with open(FIRE_LOG_FILE, "r") as f:
            logs = json.load(f)
        return [log for log in logs if log.get("fire_detected")]
    except:
        return []
