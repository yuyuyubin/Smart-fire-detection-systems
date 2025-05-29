from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import os
from datetime import datetime
import cv2
from utils.prediction_handler import run_prediction, manual_prediction, run_prediction_with_data
from utils.sensor_handler import save_sensor_data, get_latest_status, get_sensor_history
from utils.file_logger import save_result_json, append_logs, get_latest_result, get_fire_events

app = Flask(__name__)
CORS(app)

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            continue
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/sensor-data', methods=['POST'])
def sensor_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload"}), 400
        
        print(f"[센서 데이터 수신] {data}")  # 여기서 터미널 출력

        save_sensor_data(data)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"[센서 데이터 수신 오류] {e}")  # 에러도 출력
        return jsonify({"error": str(e)}), 500

@app.route('/api/image', methods=['POST'])
def image_data():
    try:
        image = request.files.get('image')
        if image is None:
            return jsonify({"error": "No image provided"}), 400

        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(temp_dir, f"image_{ts}.jpg")
        image.save(filepath)

        sensor_data = get_latest_status()
        if not sensor_data:
            return jsonify({"error": "No sensor data available"}), 400

        result = run_prediction_with_data(sensor_data, filepath)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/manual-predict', methods=['POST'])
def manual_predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload"}), 400
        result = manual_prediction(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/fire-status', methods=['GET'])
def fire_status():
    return jsonify(get_latest_result())

@app.route('/api/latest-image', methods=['GET'])
def latest_image():
    try:
        images = sorted(os.listdir("static/detected"))
        if images:
            return jsonify({"image_url": f"/static/detected/{images[-1]}"})
    except:
        pass
    return jsonify({"image_url": None})

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
    return send_from_directory("static/detected", filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
