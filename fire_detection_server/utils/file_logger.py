import json
import os

# 파일 경로 설정
LATEST_RESULT_PATH = "data/latest_result.json"
FIRE_LOG_PATH = "data/fire_log.json"
SENSOR_LOG_PATH = "data/sensor_log.json"

# 보드별 로그 파일 경로
BOARD_LOG_PATH = "data/board_logs"  # 각 보드별로 로그를 저장할 디렉토리

MAX_LOG_COUNT = 1000  # 로그의 최대 개수

# 디렉토리 생성
os.makedirs("data", exist_ok=True)
os.makedirs(BOARD_LOG_PATH, exist_ok=True)

# 최종 결과 JSON 저장
def save_result_json(data: dict):
    with open(LATEST_RESULT_PATH, 'w') as f:
        json.dump(data, f, indent=2)

# 보드별 로그 파일에 데이터 추가
def append_logs(board_id: str, data: dict):
    log_file_path = os.path.join(BOARD_LOG_PATH, f"{board_id}_log.json")

    # 기존 로그 로드
    logs = []
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

    # 데이터 검증 (예: 'timestamp'와 'board_id' 등이 반드시 있어야 한다)
    if "timestamp" not in data or "board_id" not in data:
        print(f"[ERROR] Invalid data format: Missing 'timestamp' or 'board_id' in {data}")
        return  # 유효하지 않은 데이터는 추가하지 않음

    # 새로운 로그 추가
    logs.append(data)

    # 로그가 최대 개수를 초과하면 오래된 로그 삭제
    if len(logs) > MAX_LOG_COUNT:
        logs = logs[-MAX_LOG_COUNT:]

    # 파일에 기록
    with open(log_file_path, 'w') as f:
        json.dump(logs, f, indent=2)

# 화재 로그에 데이터 추가
def append_fire_log(data: dict):
    if "fire_detected" not in data:
        print(f"[ERROR] Invalid data format: Missing 'fire_detected' in {data}")
        return  # 화재 감지 여부가 없으면 기록하지 않음

    # 화재 로그 파일 경로
    if not os.path.exists(FIRE_LOG_PATH):
        os.makedirs("data", exist_ok=True)
    
    # 기존 화재 로그 로드
    fire_logs = []
    if os.path.exists(FIRE_LOG_PATH):
        with open(FIRE_LOG_PATH, 'r') as f:
            try:
                fire_logs = json.load(f)
            except json.JSONDecodeError:
                fire_logs = []

    # 새로운 화재 로그 추가
    fire_logs.append(data)

    # 로그가 최대 개수를 초과하면 오래된 로그 삭제
    if len(fire_logs) > MAX_LOG_COUNT:
        fire_logs = fire_logs[-MAX_LOG_COUNT:]

    # 파일에 기록
    with open(FIRE_LOG_PATH, 'w') as f:
        json.dump(fire_logs, f, indent=2)

# 최신 결과 반환
def get_latest_result():
    if os.path.exists(LATEST_RESULT_PATH):
        with open(LATEST_RESULT_PATH, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

# 화재 이벤트 로그 가져오기
def get_fire_events():
    if os.path.exists(FIRE_LOG_PATH):
        with open(FIRE_LOG_PATH, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# 센서 로그 가져오기
def get_sensor_history():
    if os.path.exists(SENSOR_LOG_PATH):
        with open(SENSOR_LOG_PATH, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# 화재 로그 청소 (최대 개수 1000개로 유지)
def clean_old_fire_logs():
    if os.path.exists(FIRE_LOG_PATH):
        try:
            with open(FIRE_LOG_PATH, 'r') as f:
                logs = json.load(f)
            if len(logs) > MAX_LOG_COUNT:
                logs = logs[-MAX_LOG_COUNT:]
                with open(FIRE_LOG_PATH, 'w') as f:
                    json.dump(logs, f, indent=2)
        except json.JSONDecodeError:
            pass

# 센서 로그 청소 (최대 개수 1000개로 유지)
def clean_old_sensor_logs():
    if os.path.exists(SENSOR_LOG_PATH):
        try:
            with open(SENSOR_LOG_PATH, 'r') as f:
                logs = json.load(f)
            if len(logs) > MAX_LOG_COUNT:
                logs = logs[-MAX_LOG_COUNT:]
                with open(SENSOR_LOG_PATH, 'w') as f:
                    json.dump(logs, f, indent=2)
        except json.JSONDecodeError:
            pass

# 보드별 로그 파일을 청소 (최대 개수 1000개로 유지)
def clean_board_logs(board_id: str):
    log_file_path = os.path.join(BOARD_LOG_PATH, f"{board_id}_log.json")
    
    if os.path.exists(log_file_path):
        try:
            with open(log_file_path, 'r') as f:
                logs = json.load(f)
            if len(logs) > MAX_LOG_COUNT:
                logs = logs[-MAX_LOG_COUNT:]
                with open(log_file_path, 'w') as f:
                    json.dump(logs, f, indent=2)
        except json.JSONDecodeError:
            pass
