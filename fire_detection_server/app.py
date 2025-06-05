import os
import cv2
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import threading
import time
from datetime import datetime
from threading import Lock
from collections import deque
import json
from utils.prediction_handler import run_prediction_with_data
from utils.sensor_handler import save_sensor_data, get_latest_status, get_sensor_history
from utils.file_logger import save_result_json, append_logs, get_fire_status_log, get_latest_result, get_fire_events, clean_old_fire_logs, clean_old_sensor_logs
import traceback
app = Flask(__name__)
CORS(app)

# 큐(Queue)를 사용하여 최신 프레임을 관리
frame_queue = deque(maxlen=20)  # 최대 10개의 프레임을 저장
frame_lock = Lock()  # 프레임을 다룰 때 동기화

DETECTED_FOLDER = "static/detected"
RECEIVED_FOLDER = "temp/received"
BOARD_LOGS_FOLDER = "data/board_logs"  # 보드 상태 로그 저장 디렉토리
MAX_IMAGE_COUNT = 10
MAX_RECEIVED_IMAGES = 5

os.makedirs(DETECTED_FOLDER, exist_ok=True)
os.makedirs(RECEIVED_FOLDER, exist_ok=True)
os.makedirs(BOARD_LOGS_FOLDER, exist_ok=True)

# 보드 상태 로그를 갱신하는 파일 경로
board_status_log_file = os.path.join(BOARD_LOGS_FOLDER, "board_status_log.json")

# 보드 상태 로그를 기록하는 함수
def log_board_status(board_id, ip_address):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_data = {
        "board_id": board_id,
        "ip_address": ip_address,
        "timestamp": timestamp
    }

    # 기존 로그를 불러와서 최신 3개 보드 상태만 유지
    if os.path.exists(board_status_log_file):
        with open(board_status_log_file, 'r') as f:
            all_logs = json.load(f)
    else:
        all_logs = []

    # 새로운 보드 상태 추가
    all_logs = [log for log in all_logs if log['board_id'] != board_id]  # 기존 보드 정보 제거
    all_logs.append(log_data)

    # 최신 3개 보드 상태만 남기기
    all_logs = all_logs[-3:]

    # 갱신된 로그를 다시 저장
    with open(board_status_log_file, 'w') as f:
        json.dump(all_logs, f, indent=4)

    # 해당 보드 상태 로그를 기록한 후 3분 뒤 자동 삭제
    def delete_old_log():
        time.sleep(180)  # 3분
        with open(board_status_log_file, 'r') as f:
            all_logs = json.load(f)
        
        # 3분 이상 요청이 없는 보드 로그를 삭제
        all_logs = [log for log in all_logs if log['board_id'] != board_id]
        
        # 삭제된 내용을 다시 저장
        with open(board_status_log_file, 'w') as f:
            json.dump(all_logs, f, indent=4)

    threading.Thread(target=delete_old_log, daemon=True).start()

# 보드 상태 로그를 확인하는 API
@app.route('/api/board-status', methods=['GET'])
def get_board_status():
    if os.path.exists(board_status_log_file):
        with open(board_status_log_file, 'r') as f:
            all_logs = json.load(f)
        return jsonify(all_logs), 200
    else:
        return jsonify({"error": "No board status logs found."}), 404

@app.route('/api/fire-stat', methods=['GET'])
def fire_stat():
    # board_ids를 쿼리 파라미터로 전달받습니다.
    board_ids_param = request.args.get('board_ids')  # 쉼표로 구분된 하나의 값 받기
    
    if board_ids_param:
        # 쉼표로 구분된 값을 나누어서 리스트로 변환
        board_ids = board_ids_param.split(',')
        result = get_fire_status_log(board_ids)  # 주어진 board_ids에 대한 최신 화재 정보를 반환
        return jsonify(result), 200
    else:
        return jsonify({"error": "No board_ids provided"}), 400

# 예전 이미지 자동 정리
def clean_old_images():
    images = sorted([f for f in os.listdir(DETECTED_FOLDER) if f.endswith('.jpg')])
    if len(images) > MAX_IMAGE_COUNT:
        for img in images[:-MAX_IMAGE_COUNT]:
            os.remove(os.path.join(DETECTED_FOLDER, img))

def clean_old_received_images():
    images = sorted([f for f in os.listdir(RECEIVED_FOLDER) if f.endswith('.jpg')])
    if len(images) > MAX_RECEIVED_IMAGES:
        for img in images[:-MAX_RECEIVED_IMAGES]:
            os.remove(os.path.join(RECEIVED_FOLDER, img))

# ===============================
# 1. 라즈베리파이에서 스트리밍 이미지 수신 (/api/stream-frame)
# ===============================
@app.route('/api/stream-frame', methods=['POST'])
def receive_stream_frame():
    global frame_queue
    try:
        # 스트리밍 영상에서 한 프레임을 받음
        file = request.files.get('frame')
        if not file:
            return jsonify({"error": "No frame received"}), 400
        
        # 프레임을 큐에 넣음
        with frame_lock:
            frame_queue.append(file.read())  # 새로운 프레임을 큐에 추가
        
        return '', 204  # 성공적으로 받았음을 알림
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===============================
# 2. TCP MJPEG 영상 스트리밍 중계 (/video_feed)
# ===============================
@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            with frame_lock:
                if frame_queue:
                    # 큐에서 최신 프레임을 가져옴
                    frame = frame_queue.popleft()  # 가장 오래된 프레임을 꺼내서 보내기
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)  # 프레임 간 간격 설정
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ===============================
# 3. 센서 데이터 수신 및 저장 (/api/sensor-data)
# ===============================
def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        print(f"[WARN] float 변환 실패 → 기본값 0.0 사용 (value: {value})")
        return 0.0

@app.route('/api/sensor-data', methods=['POST'])
def sensor_data():
    try:
        data = request.get_json(force=True)  # force로 헤더 문제 방지
        if not data:
            return jsonify({"error": "No JSON payload"}), 400
        
        board_id = data.get('board_id', 'Unknown')
        ip_address = request.remote_addr
        print(f"[센서 데이터 수신] {data} from board: {board_id}")

        log_board_status(board_id, ip_address)

        prediction_result = None  # 예측 결과 저장용

        if board_id in ['esp1', 'esp2', 'esp3'] and any(k in data for k in ['mq2', 'temp', 'humidity', 'flame']):
            image_path = get_latest_received_image()
            print("[DEBUG] image_path:", image_path)

            if image_path:
                try:
                    # 안전한 float 변환으로 sensor_input 생성
                    sensor_input = np.array([[safe_float(data.get('mq2')),
                                              safe_float(data.get('temp')),
                                              safe_float(data.get('humidity')),
                                              safe_float(data.get('flame'))]])
                    print("[DEBUG] sensor_input:", sensor_input)

                    prediction_result = run_prediction_with_data(data, image_path)
                    prediction_result['board_id'] = board_id

                    print(f"""
[?? 예측 결과]
?? 시간: {prediction_result.get('timestamp', 'Unknown Time')}
?? 센서 화재 확률: {prediction_result.get('sensor_fire_probability', 'N/A')}%
???  이미지 화재 신뢰도: {prediction_result.get('image_fire_confidence', 'N/A')}%
?? 최종 예측 점수: {prediction_result.get('final_score', 'N/A')}%
?? 화재 감지 여부: {"?? 화재 발생" if prediction_result.get('fire_detected') else "? 정상"}
[Board ID]: {prediction_result.get('board_id')}
""".strip())

                except Exception as e:
                    print("[? 예측 중 오류 발생]", str(e))
                    traceback.print_exc()
                    raise

            else:
                print("[WARN] 이미지 경로가 존재하지 않아서 예측 생략됨")

        save_sensor_data(data)
        clean_old_sensor_logs()

        # 예측 결과가 있다면 함께 반환
        if prediction_result:
            return jsonify({"status": "success", "prediction": prediction_result}), 200
        else:
            return jsonify({"status": "success", "prediction": None}), 200

    except Exception as e:
        print("[? /api/sensor-data 예외 발생]:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
# ===============================
# 4. 이미지 수동 업로드 (/api/image)
# ===============================
@app.route('/api/image', methods=['POST'])
def image_data():
    try:
        image = request.files.get('image')
        if image is None:
            return jsonify({"error": "No image provided"}), 400
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"received_{ts}.jpg"
        filepath = os.path.join(RECEIVED_FOLDER, filename)
        image.save(filepath)
        clean_old_received_images()
        return jsonify({"status": "image received", "path": filepath})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===============================
# 5. 예측 및 센서 정보 제공 API들
# ===============================
@app.route('/api/fire-status', methods=['GET'])
def fire_status():
    return jsonify(get_latest_result())


@app.route('/api/latest-image', methods=['GET'])
def latest_image():
    try:
        images = sorted(os.listdir(DETECTED_FOLDER))
        if images:
            return jsonify({"image_url": f"/static/detected/{images[-1]}"}), 200
    except Exception as e:
        pass
    return jsonify({"image_url": None}), 404

@app.route('/api/sensors', methods=['GET'])
def sensors():
    return jsonify(get_latest_status())

@app.route('/api/sensors/history', methods=['GET'])
def sensors_history():
    return jsonify(get_sensor_history())

@app.route('/api/fire-events', methods=['GET'])
def fire_events():
    return jsonify(get_fire_events())

@app.route('/static/detected/<filename>')
def send_image(filename):
    return send_from_directory(DETECTED_FOLDER, filename)

# ===============================
# 6. 최신 수신 이미지 가져오기
# ===============================
def get_latest_received_image():
    """
    가장 최근에 저장된 이미지를 반환하는 함수입니다.
    만약 이미지가 없다면 None을 반환합니다.
    """
    images = sorted([f for f in os.listdir(RECEIVED_FOLDER) if f.endswith('.jpg')])
    if images:
        latest_image_path = os.path.join(RECEIVED_FOLDER, images[-1])
        print(f"[INFO] Latest image path: {latest_image_path}")  # 디버깅용 출력
        return latest_image_path
    return None  # 이미지가 없으면 None 반환

@app.route('/api/board-status/update', methods=['POST'])
def update_board_status():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload"}), 400
        
        board_id = data.get('board_id', 'Unknown')  # board_id를 확인
        ip_address = request.remote_addr  # 클라이언트 IP 주소 가져오기
        
        # 보드 상태 로그 기록
        log_board_status(board_id, ip_address)
        
        return jsonify({"status": "Board status updated successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# This function should be renamed to avoid overwriting the get_board_status function
@app.route('/api/board-status', methods=['GET'])
def get_board_status_from_file():
    if os.path.exists(board_status_log_file):
        with open(board_status_log_file, 'r') as f:
            all_logs = json.load(f)
        return jsonify(all_logs), 200
    else:
        return jsonify({"error": "No board status logs found."}), 
# ===============================
# 메인 실행
# ===============================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
