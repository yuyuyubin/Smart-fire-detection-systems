from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from ultralytics import YOLO
from datetime import datetime
import os
import shutil
import cv2

app = Flask(__name__)

# Load models
sensor_model = tf.keras.models.load_model("fire_model_with_fuzzy.h5")
image_model = YOLO("fire_mode2_image.pt")

@app.route('/predict', methods=['POST'])
def predict_fire():
    try:
        # Parse sensor data
        data = request.form
        mq2 = float(data['mq2'])
        smoke = float(data['smoke'])
        temp = float(data['temp'])
        humidity = float(data['humidity'])
        flame = float(data['flame'])

        sensor_input = np.array([[mq2, smoke, temp, humidity, flame]])
        sensor_prob = float(sensor_model.predict(sensor_input)[0][0]) * 100

        # Check for image file
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image = request.files['image']
        filepath = "received_image.jpg"
        image.save(filepath)

        # Run YOLO prediction
        image_result = image_model.predict(source=filepath, conf=0.25)
        fire_detected = False
        image_conf = 0.0

        # Load image for drawing boxes
        img = cv2.imread(filepath)

        # Draw bounding boxes for fire detections
        for r in image_result:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                cls_name = image_model.names[cls_id].lower()

                if "fire" in cls_name or "flame" in cls_name:
                    fire_detected = True
                    image_conf = float(box.conf[0]) * 100

                    # Get box coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    # Draw rectangle
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    # Add label
                    label = f"{cls_name} {image_conf:.2f}%"
                    cv2.putText(img, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Calculate final fire probability
        final_score = (sensor_prob * 0.6) + (image_conf * 0.4)
        fire_status = final_score >= 70

        # Log to terminal
        print(f"[FIRE CHECK] Sensor={sensor_prob:.1f}%, Image={image_conf:.1f}%, Final={final_score:.1f}% �� Detected={fire_status}")

        # Save image if fire is detected
        if fire_status:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = f"static/detected/fire_{timestamp}.jpg"
            os.makedirs("static/detected", exist_ok=True)
            cv2.imwrite(save_path, img)
            print(f"[?? IMAGE SAVED] {save_path}")

        # Return result
        return jsonify({
            "sensor_fire_probability": round(sensor_prob, 2),
            "image_fire_confidence": round(image_conf, 2),
            "final_score": round(final_score, 2),
            "fire_detected": fire_status
        })

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
