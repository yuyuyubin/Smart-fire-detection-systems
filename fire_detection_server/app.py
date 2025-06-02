from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from datetime import datetime
import os
import time
from utils.prediction_handler import run_prediction, manual_prediction, run_prediction_with_data
from utils.sensor_handler import save_sensor_data, get_latest_status, get_sensor_history
from utils.file_logger import save_result_json, append_logs, get_latest_result, get_fire_events

app = Flask(__name__)
CORS(app)

# 🔁 전역 변수로 마지막 프레임 저장
last_frame = None

# ✅ /upload_frame: 라즈베리파이에서 실시간 프레임 POST
@app.route('/upload_frame', methods=['POST'])
def upload_frame():
    global last_frame
    last_frame = request.data  # JPEG 바이트
    return '', 200

# ✅ /video_feed: MJPEG 형식으로 실시간 프레임 브라우저에 전송
@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            if last_frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + last_frame + b'\r\n')
            time.sleep(0.1)  # 약 10fps
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/sensor-data', methods=['POST'])
def sensor_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload"}), 400
        print(f"[📡 센서 수신] {data}")
        save_sensor_data(data)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"[❌ 센서 수신 오류] {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/image', methods=['POST'])
def image_data():
    try:
        image = request.files.get('image')
        if image is None:
            print("[❌ 오류] 이미지 파일 누락")
            return jsonify({"error": "No image provided"}), 400

        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(temp_dir, f"image_{ts}.jpg")
        image.save(filepath)
        print(f"[📷 이미지 수신] 저장 위치: {filepath}")

        sensor_data = get_latest_status()
        if not sensor_data:
            print("[⚠️ 경고] 센서 데이터 없음")
            return jsonify({"error": "No sensor data available"}), 400

        print(f"[🔍 예측 시작] 센서값: {sensor_data}")
        result = run_prediction_with_data(sensor_data, filepath)
        print(f"[✅ 예측 완료] 결과: {result}")
        return jsonify(result)
    except Exception as e:
        print(f"[❌ 예측 오류] {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/manual-predict', methods=['POST'])
def manual_predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload"}), 400
        print(f"[🧪 수동 예측 요청] 입력 데이터: {data}")
        result = manual_prediction(data)
        print(f"[✅ 수동 예측 완료] 결과: {result}")
        return jsonify(result)
    except Exception as e:
        print(f"[❌ 수동 예측 오류] {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/fire-status', methods=['GET'])
def fire_status():
    print("[🌐 요청] /api/fire-status")
    return jsonify(get_latest_result())

@app.route('/api/latest-image', methods=['GET'])
def latest_image():
    try:
        images = sorted(os.listdir("static/detected"))
        if images:
            print(f"[📸 최신 이미지] {images[-1]}")
            return jsonify({"image_url": f"/static/detected/{images[-1]}"})
    except Exception as e:
        print(f"[❌ 이미지 경로 오류] {e}")
    return jsonify({"image_url": None})

@app.route('/api/sensors', methods=['GET'])
def sensors():
    print("[🌐 요청] /api/sensors")
    return jsonify(get_latest_status())

@app.route('/api/sensors/history', methods=['GET'])
def sensors_history():
    print("[🌐 요청] /api/sensors/history")
    return jsonify(get_sensor_history())

@app.route('/api/fire-events', methods=['GET'])
def fire_events():
    print("[🌐 요청] /api/fire-events")
    return jsonify(get_fire_events())

@app.route('/static/detected/<filename>')
def send_image(filename):
    print(f"[📤 이미지 전송] {filename}")
    return send_from_directory("static/detected", filename)

if __name__ == '__main__':
    print("[🚀 서버 시작] http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000)
