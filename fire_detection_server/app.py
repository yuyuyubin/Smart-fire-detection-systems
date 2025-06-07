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

app = Flask(__name__)
CORS(app)
status_lock = Lock()
frame_queue = deque(maxlen=20)
frame_lock = Lock()

DETECTED_FOLDER = "static/detected"
RECEIVED_FOLDER = "temp/received"
BOARD_LOGS_FOLDER = "data/board_logs"
MAX_IMAGE_COUNT = 10
MAX_RECEIVED_IMAGES = 5

os.makedirs(DETECTED_FOLDER, exist_ok=True)
os.makedirs(RECEIVED_FOLDER, exist_ok=True)
os.makedirs(BOARD_LOGS_FOLDER, exist_ok=True)

board_status_log_file = os.path.join(BOARD_LOGS_FOLDER, "board_status_log.json")

def log_board_status(board_id, ip_address):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_data = {
        "board_id": board_id,
        "ip_address": ip_address,
        "timestamp": timestamp
    }

    with status_lock:
        if os.path.exists(board_status_log_file):
            with open(board_status_log_file, 'r') as f:
                try:
                    all_logs = json.load(f)
                except:
                    all_logs = []
        else:
            all_logs = []

        all_logs = [log for log in all_logs if log['board_id'] != board_id]
        all_logs.append(log_data)
        all_logs = all_logs[-3:]

        with open(board_status_log_file, 'w') as f:
            json.dump(all_logs, f, indent=4)

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
    board_ids_param = request.args.get('board_ids')
    if board_ids_param:
        board_ids = board_ids_param.split(',')
        result = get_fire_status_log(board_ids)
        return jsonify(result), 200
    else:
        return jsonify({"error": "No board_ids provided"}), 400

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

@app.route('/api/stream-frame', methods=['POST'])
def receive_stream_frame():
    try:
        file = request.files.get('frame')
        if not file:
            return jsonify({"error": "No frame received"}), 400
        with frame_lock:
            frame_queue.append(file.read())
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            with frame_lock:
                if frame_queue:
                    frame = frame_queue.popleft()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/sensor-data', methods=['POST'])
def sensor_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload"}), 400

        board_id = data.get('board_id', 'Unknown')
        ip_address = request.remote_addr
        print(f"[센서 데이터 수신] {data} from board: {board_id}")
        log_board_status(board_id, ip_address)

        if board_id in ['esp1', 'esp2', 'esp3'] and any(k in data for k in ['mq2', 'temp', 'humidity', 'flame']):
            image_path = get_latest_received_image()
            if image_path:
                result = run_prediction_with_data(data, image_path)
                result['board_id'] = board_id
                print(f"""
[🔥 예측 결과]
🕒 시간: {result.get('timestamp', 'Unknown Time')}
📟 센서 화재 확률: {result.get('sensor_fire_probability', 'N/A')}%
🖼️  이미지 화재 신뢰도: {result.get('image_fire_confidence', 'N/A')}%
📊 최종 예측 점수: {result.get('final_score', 'N/A')}%
🚨 화재 감지 여부: {"🔥 화재 발생" if result.get('fire_detected') else "✅ 정상"}
[Board ID]: {result.get('board_id')}
""".strip())

        save_sensor_data(data)
        clean_old_sensor_logs()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

def get_latest_received_image():
    images = sorted([f for f in os.listdir(RECEIVED_FOLDER) if f.endswith('.jpg')])
    if images:
        latest_image_path = os.path.join(RECEIVED_FOLDER, images[-1])
        print(f"[INFO] Latest image path: {latest_image_path}")
        return latest_image_path
    return None
@app.route('/api/board-status/update', methods=['POST'])
def update_board_status():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload"}), 400

        board_id = data.get('board_id', 'Unknown')
        ip_address = request.remote_addr
        log_board_status(board_id, ip_address)
        return jsonify({"status": "Board status updated successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/board-status', methods=['GET'])
def board_status():
    if not os.path.exists(board_status_log_file):
        return jsonify({"error": "No board status logs found."}), 404

    try:
        with open(board_status_log_file, 'r') as f:
            logs = json.load(f)
    except Exception as e:
        return jsonify({"error": f"Failed to load board status logs: {str(e)}"}), 500

    latest_by_board = {}
    for log in logs:
        board_id = log.get('board_id')
        if not board_id:
            continue
        latest_by_board[board_id] = {
            "board_id": board_id,
            "ip_address": log.get('ip_address'),
            "timestamp": log.get('timestamp')
        }

    return jsonify(latest_by_board), 200    
## 각 센서 정보 구별해서 제공하는 api
@app.route('/api/board-latest-log', methods=['GET'])
def get_latest_logs_per_board():
    board_ids = ['esp1', 'esp2', 'esp3']
    results = []

    for board_id in board_ids:
        log_path = os.path.join(BOARD_LOGS_FOLDER, f"{board_id}_log.json")
        if not os.path.exists(log_path):
            continue

        try:
            with open(log_path, 'r') as f:
                logs = json.load(f)
            if logs:
                latest = logs[-1]
                results.append({
                    "board_id": board_id,
                    "fire_detected": latest.get("fire_detected"),
                    "final_score": latest.get("final_score"),
                    "sensor_fire_probability": latest.get("sensor_fire_probability"),
                    "image_fire_confidence": latest.get("image_fire_confidence"),
                    "timestamp": latest.get("timestamp")
                })
        except Exception as e:
            print(f"[ERROR] {board_id}_log.json 읽기 실패: {e}")
            continue

    return jsonify(results), 200
## 센서 그래프용 데이터 제공 API
@app.route('/api/sensors/graph-data', methods=['GET'])
def sensors_graph_data():
    board_ids = ['esp1', 'esp2', 'esp3']
    data = {}

    for board_id in board_ids:
        log_path = os.path.join(BOARD_LOGS_FOLDER, f"{board_id}_log.json")
        if not os.path.exists(log_path):
            print(f"[WARN] {log_path} 파일이 존재하지 않습니다.")
            continue

        try:
            with open(log_path, 'r') as f:
                logs = json.load(f)
                data[board_id] = logs  # 전체 파일 내용을 그대로 담기
        except Exception as e:
            print(f"[ERROR] {board_id}_log.json 읽기 실패: {e}")
            data[board_id] = []

    return jsonify(data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
