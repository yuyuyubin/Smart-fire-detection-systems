import json
import os
import cv2
import numpy as np
import tensorflow as tf
from ultralytics import YOLO
from datetime import datetime
import joblib  # joblib을 사용하여 scaler를 로드합니다.
from utils.file_logger import save_result_json, append_logs, append_fire_log, save_fire_status_log  # save_fire_status_log 추가
import traceback
# 모델 로드
sensor_model = tf.keras.models.load_model(os.path.join("models", "fire_sensor_model_.h5"))
image_model = YOLO(os.path.join("models", "best8_ver2.pt"))

# 스칼라 로드 (정규화에 사용할 scaler)
scaler = joblib.load(os.path.join("models", "scaler.pkl"))

# 이미지 디렉토리와 최대 이미지 개수 설정
DETECTED_FOLDER = "static/detected"
MAX_IMAGE_COUNT = 10  # 저장할 최대 이미지 개수

os.makedirs(DETECTED_FOLDER, exist_ok=True)



# 오래된 이미지 삭제 함수
def clean_old_images():
    images = sorted([f for f in os.listdir(DETECTED_FOLDER) if f.endswith('.jpg')])
    if len(images) > MAX_IMAGE_COUNT:
        for img in images[:-MAX_IMAGE_COUNT]:
            os.remove(os.path.join(DETECTED_FOLDER, img))

# 예측 처리 함수

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        print(f"[WARN] float 변환 실패: {value} → 기본값 0.0 적용")
        return 0.0

def run_prediction_with_data(sensor_data, image_path):
    try:
        board_id = sensor_data.get('board_id', 'Unknown')

        # 1. 센서 데이터 입력 처리
        sensor_input = np.array([[safe_float(sensor_data.get('mq2')),
                                  safe_float(sensor_data.get('temp')),
                                  safe_float(sensor_data.get('humidity')),
                                  safe_float(sensor_data.get('flame'))]])

        print(f"[센서 데이터] board_id: {board_id}, mq2: {sensor_data.get('mq2')}, temp: {sensor_data.get('temp')}, humidity: {sensor_data.get('humidity')}, flame: {sensor_data.get('flame')}")

        # 2. 정규화 및 예측
        sensor_input_scaled = scaler.transform(sensor_input)
        sensor_prob = float(sensor_model.predict(sensor_input_scaled)[0][0]) * 100

        # 3. 이미지 예측
        results = image_model.predict(image_path, conf=0.25)
        fire_conf = 0
        fire_detected = False
        img = cv2.imread(image_path)

        if img is None:
            raise ValueError(f"이미지를 읽을 수 없습니다: {image_path}")

        # 4. 이미지에서 화재 탐지
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

        # 5. 센서 예측과 이미지 예측 결합
        final_score = sensor_prob * 0.6 + fire_conf * 0.4
        fire_status = final_score >= 30

        save_path = ""
        if fire_status:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"static/detected/fire_{ts}.jpg"
            cv2.imwrite(save_path, img)
            clean_old_images()

        # 6. 예측 결과 반환
        result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sensor_fire_probability": round(sensor_prob, 2),
            "image_fire_confidence": round(fire_conf, 2),
            "final_score": round(final_score, 2),
            "fire_detected": fire_status,
            "image_path": save_path,
            "board_id": board_id
        }

        data_with_sensor = {**result, "sensor_data": sensor_data}
        save_result_json(result)
        append_logs(board_id, data_with_sensor)
        append_fire_log(result)
        save_fire_status_log(result)

        return result

    except Exception as e:
       print("[? run_prediction_with_data 예외 발생]:", str(e))
       traceback.print_exc()   # ? 콘솔에 구체적인 에러 라인까지 출력
       raise                   # ? Flask에게도 오류 알림