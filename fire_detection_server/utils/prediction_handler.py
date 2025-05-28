import json, os, cv2
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

        sensor_input = np.array([[float(data['mq2']), float(data['smoke']),
                                  float(data['temp']), float(data['humidity']),
                                  float(data['flame'])]])
        sensor_prob = float(sensor_model.predict(sensor_input)[0][0]) * 100

        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        filepath = os.path.join(temp_dir, "received.jpg")
        image.save(filepath)

        results = image_model.predict(filepath, conf=0.25)
        fire_conf = 0
        fire_detected = False
        img = cv2.imread(filepath)

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

        save_path = ""
        if fire_status:
            os.makedirs("static/detected", exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"static/detected/fire_{ts}.jpg"
            cv2.imwrite(save_path, img)

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
        return jsonify(result)

    except Exception as e:
        print(f"[❌ ERROR] {e}")
        return jsonify({"error": str(e)}), 500
