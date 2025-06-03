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
from utils.prediction_handler import run_prediction_with_data
from utils.sensor_handler import save_sensor_data, get_latest_status, get_sensor_history
from utils.file_logger import save_result_json, append_logs, get_latest_result, get_fire_events, clean_old_fire_logs, clean_old_sensor_logs

app = Flask(__name__)
CORS(app)

# 큐(Queue)를 사용하여 최신 프레임을 관리
frame_queue = deque(maxlen=20)  # 최대 10개의 프레임을 저장
frame_lock = Lock()  # 프레임을 다룰 때 동기화

DETECTED_FOLDER = "static/detected"
RECEIVED_FOLDER = "temp/received"
MAX_IMAGE_COUNT = 10
MAX_RECEIVED_IMAGES = 5

os.makedirs(DETECTED_FOLDER, exist_ok=True)
os.makedirs(RECEIVED_FOLDER, exist_ok=True)

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
@app.route('/api/sensor-data', methods=['POST'])
def sensor_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload"}), 400
        
        board_id = data.get('board_id', 'Unknown')  # board_id를 확인
        print(f"[센서 데이터 수신] {data} from board: {board_id}")

        # 보드별로 센서 데이터가 수신되었을 때만 예측을 실행하도록 처리
        if board_id in ['esp1', 'esp2', 'esp3'] and any(k in data for k in ['mq2', 'temp', 'humidity','flame']):
            # 센서 데이터가 유효하면 예측 함수 호출
            image_path = get_latest_received_image()  # 최신 이미지 가져오기
            if image_path:
                result = run_prediction_with_data(data, image_path)

                # 예측 결과에 board_id 포함
                result['board_id'] = board_id  # 예측 결과에 board_id 추가

                # 예측 결과 출력
                print(f"""
[🔥 예측 결과]
🕒 시간: {result.get('timestamp', 'Unknown Time')}
📟 센서 화재 확률: {result.get('sensor_fire_probability', 'N/A')}%
🖼️  이미지 화재 신뢰도: {result.get('image_fire_confidence', 'N/A')}%
📊 최종 예측 점수: {result.get('final_score', 'N/A')}%
🚨 화재 감지 여부: {"🔥 화재 발생" if result.get('fire_detected') else "✅ 정상"}
[Board ID]: {result.get('board_id')}
""".strip())

                # 보드별 로그 파일에 예측 결과 저장
               

        save_sensor_data(data)  # 센서 데이터 저장
        clean_old_sensor_logs()
        return jsonify({"status": "success"}), 200
    except Exception as e:
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
    images = sorted([f for f in os.listdir(RECEIVED_FOLDER) if f.endswith('.jpg')])
    if images:
        return os.path.join(RECEIVED_FOLDER, images[-1])  # 최신 이미지 경로 반환
    return None  # 이미지가 없으면 None 반환

# ===============================
# 메인 실행
# ===============================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
