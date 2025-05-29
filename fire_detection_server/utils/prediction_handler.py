import os
import cv2
import numpy as np
import tensorflow as tf
from ultralytics import YOLO
from datetime import datetime
from flask import jsonify
from utils.file_logger import save_result_json, append_logs

sensor_model = tf.keras.models.load_model(os.path.join("models", "fire_model_with_fuzzy.h5"))
image_model = YOLO(os.path.join("models", "best8_ver2.pt"))

def run_prediction(request):
    try:
        data = request.form
        image = request.files.get('image')
        if image is None:
            return jsonify({'error': 'No image provided'}), 400

        sensor_input = np.array([[float(data.get('mq2', 0)),
                                  float(data.get('flame', 0)),
                                  float(data.get('temperature', 0)),
                                  float(data.get('humidity', 0))]])
        sensor_prob = float(sensor_model.predict(sensor_input)[0][0]) * 100

        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        filepath = os.path.join(temp_dir, "received.jpg")
        image.save(filepath)
        print(f"[이미지 수신] 저장 경로: {filepath}")

        sensor_dict = {
            'mq2': float(data.get('mq2', 0)),
            'flame': float(data.get('flame', 0)),
            'temp': float(data.get('temperature', 0)),
            'humidity': float(data.get('humidity', 0))
        }
        return run_prediction_with_data(sensor_dict, filepath)
    except Exception as e:
        print(f"[❌ ERROR] {e}")
        return jsonify({"error": str(e)}), 500

def run_prediction_with_data(sensor_data, image_path):
    try:
        print(f"[예측 시작] 센서 데이터: {sensor_data}, 이미지 경로: {image_path}")

        sensor_input = np.array([[float(sensor_data.get('mq2', 0)),
                                  float(sensor_data.get('flame', 0)),
                                  float(sensor_data.get('temp', 0)),
                                  float(sensor_data.get('humidity', 0))]])
        sensor_prob = float(sensor_model.predict(sensor_input)[0][0]) * 100

        results = image_model.predict(image_path, conf=0.25)
        fire_conf = 0
        fire_detected = False
        img = cv2.imread(image_path)

        for r in results:
            for box in r.boxes:
                cls_name = image_model.names[int(box.cls[0])].lower()
                if "fire" in cls_name or "flame" in cls_name:
                    fire_detected = True
                    fire_conf = float(box.conf[0]) * 100
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    label = f"{cls_name} {fire_conf:.1f}%"
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(img, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        final_score = sensor_prob * 0.6 + fire_conf * 0.4
        fire_status = final_score >= 70

        print(f"[예측 완료] 센서 확률: {sensor_prob:.2f}%, 이미지 확률: {fire_conf:.2f}%, 최종 점수: {final_score:.2f}%, 화재 감지: {fire_status}")

        save_path = ""
        if fire_status:
            os.makedirs("static/detected", exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"static/detected/fire_{ts}.jpg"
            cv2.imwrite(save_path, img)
            print(f"[화재 이미지 저장] {save_path}")

        result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sensor_fire_probability": round(sensor_prob, 2),
            "image_fire_confidence": round(fire_conf, 2),
            "final_score": round(final_score, 2),
            "fire_detected": fire_status,
            "image_path": save_path
        }

        save_result_json(result)
        append_logs(result)
        return result
    except Exception as e:
        print(f"[❌ ERROR] {e}")
        return {"error": str(e)}

def manual_prediction(data):
    try:
        sensor_input = np.array([[float(data.get('mq2', 0)),
                                  float(data.get('flame', 0)),
                                  float(data.get('temp', 0)),
                                  float(data.get('humidity', 0))]])
        sensor_prob = float(sensor_model.predict(sensor_input)[0][0]) * 100

        image_path = data.get('image_path')
        if not image_path or not os.path.exists(image_path):
            return {"error": "Invalid or missing image_path"}

        results = image_model.predict(image_path, conf=0.25)
        fire_conf = 0
        fire_detected = False
        img = cv2.imread(image_path)

        for r in results:
            for box in r.boxes:
                cls_name = image_model.names[int(box.cls[0])].lower()
                if "fire" in cls_name or "flame" in cls_name:
                    fire_detected = True
                    fire_conf = float(box.conf[0]) * 100
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    label = f"{cls_name} {fire_conf:.1f}%"
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(img, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        final_score = sensor_prob * 0.6 + fire_conf * 0.4
        fire_status = final_score >= 70

        result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sensor_fire_probability": round(sensor_prob, 2),
            "image_fire_confidence": round(fire_conf, 2),
            "final_score": round(final_score, 2),
            "fire_detected": fire_status,
            "image_path": image_path
        }
        return result
    except Exception as e:
        return {"error": str(e)}
