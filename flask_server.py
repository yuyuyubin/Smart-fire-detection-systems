from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from ultralytics import YOLO
import os

app = Flask(__name__)

# 모델 로드
sensor_model = tf.keras.models.load_model("fire_model_with_fuzzy.h5")
image_model = YOLO("fire_mode2_image.pt")

@app.route('/predict', methods=['POST'])
def predict_fire():
    try:
        # ✅ 센서 데이터 파싱
        data = request.form
        mq2 = float(data['mq2'])
        smoke = float(data['smoke'])
        temp = float(data['temp'])
        humidity = float(data['humidity'])
        flame = float(data['flame'])

        sensor_input = np.array([[mq2, smoke, temp, humidity, flame]])
        sensor_prob = float(sensor_model.predict(sensor_input)[0][0]) * 100

        # ✅ 이미지 파일 처리
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image = request.files['image']
        filepath = "received_image.jpg"
        image.save(filepath)

        image_result = image_model.predict(source=filepath, conf=0.25)
        fire_detected = False
        image_conf = 0.0

        for r in image_result:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                cls_name = image_model.names[cls_id].lower()
                if "fire" in cls_name or "flame" in cls_name:
                    fire_detected = True
                    image_conf = float(box.conf[0]) * 100
                    break

        # ✅ 가중 평균 계산
        final_score = (sensor_prob * 0.6) + (image_conf * 0.4)
        fire_status = final_score >= 70  # 최종 화재 판단 기준

        return jsonify({
            "sensor_fire_probability": round(sensor_prob, 2),
            "image_fire_confidence": round(image_conf, 2),
            "final_score": round(final_score, 2),
            "fire_detected": fire_status
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
