# 로깅 관련 함수들
import os  # os 모듈 추가
import json
# 파일 경로 설정
LATEST_RESULT_PATH = "data/latest_result.json"
FIRE_LOG_PATH = "data/fire_log.json"
SENSOR_LOG_PATH = "data/sensor_log.json"
FIRE_STATUS_LOG_FILE = "data/fire_status_log.json" 
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

def save_fire_status_log(result):
    """
    최신 화재 정보를 fire_status_log.json 파일에 저장합니다.
    """
    try:
        # 기존의 fire_status_log.json을 읽어옵니다.
        if os.path.exists(FIRE_STATUS_LOG_FILE):
            with open(FIRE_STATUS_LOG_FILE, "r") as file:
                fire_status_log = json.load(file)
        else:
            fire_status_log = []

        # board_id를 기준으로 최신 정보만 갱신
        updated = False
        for entry in fire_status_log:
            if entry['board_id'] == result['board_id']:
                # 최신 정보로 덮어쓰기
                entry.update(result)
                updated = True
                break

        if not updated:
            # 새로운 보드 정보 추가
            fire_status_log.append(result)

        # 최신 화재 정보 저장
        with open(FIRE_STATUS_LOG_FILE, "w") as file:
            json.dump(fire_status_log, file, indent=4)

    except Exception as e:
        print(f"[ERROR] 화재 정보 저장 실패: {e}")

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
                logs = []  # JSON 디코딩 오류시 빈 리스트로 초기화

    # 데이터 검증 (예: 'timestamp'와 'board_id' 등이 반드시 있어야 한다)
    if "timestamp" not in data or "board_id" not in data:
        print(f"[ERROR] Invalid data format: Missing 'timestamp' or 'board_id' in {data}")
        return  # 유효하지 않은 데이터는 추가하지 않음

    # 보드별 로그 데이터 구조 변경 (fire_log와 다르게)
    board_log = {
        "board_id": data.get("board_id"),
        "timestamp": data.get("timestamp"),
        "sensor_data": data.get("sensor_data", {}),  # 센서 데이터 포함
        "fire_detected": data.get("fire_detected"),
        "image_path": data.get("image_path")
    }

    # 새로운 로그 추가
    logs.append(board_log)

    # 로그가 최대 개수를 초과하면 오래된 로그 삭제
    if len(logs) > MAX_LOG_COUNT:
        logs = logs[-MAX_LOG_COUNT:]  # 최신 로그만 남기기

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


def get_fire_status_log(board_ids=None):
    """
    최신 화재 정보를 반환하는 함수입니다.
    board_ids가 제공되면 해당 보드들의 결과만 반환합니다.
    """
    try:
        # fire_status_log.json에서 화재 정보를 읽어옵니다.
        if os.path.exists(FIRE_STATUS_LOG_FILE):
            with open(FIRE_STATUS_LOG_FILE, "r") as file:
                fire_status_log = json.load(file)
        else:
            fire_status_log = []

        if board_ids:
            # 주어진 board_ids에 해당하는 결과만 반환 (여러 개의 보드 가능)
            filtered_results = [entry for entry in fire_status_log if entry['board_id'] in board_ids]
            return filtered_results if filtered_results else None  # 해당 board_id가 없으면 None 반환
        else:
            # 모든 결과를 반환
            return fire_status_log
    except Exception as e:
        return {"error": str(e)}

    except Exception as e:
        print(f"[ERROR] 화재 정보 읽기 실패: {e}")
        return []  # 오류 발생 시 빈 리스트 반환