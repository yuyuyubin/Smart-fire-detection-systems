from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from utils.prediction_handler import run_prediction
from utils.sensor_handler import get_latest_status, get_sensor_history
from utils.file_logger import get_latest_result, get_fire_events

app = Flask(__name__)
CORS(app)

@app.route('/api/predict', methods=['POST'])
def predict():
    return run_prediction(request)

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
