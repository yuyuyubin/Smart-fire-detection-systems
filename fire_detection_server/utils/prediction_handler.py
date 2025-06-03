import json
import os
import cv2
import numpy as np
import tensorflow as tf
from ultralytics import YOLO
from datetime import datetime
import joblib  # joblib을 사용하여 scaler를 로드합니다.
from utils.file_logger import save_result_json, append_logs, append_fire_log, save_fire_status_log  # save_fire_status_log 추가

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
def run_prediction_with_data(sensor_data, image_path):
    try:
        # 센서 데이터에서 board_id 가져오기
        board_id = sensor_data.get('board_id', 'Unknown')
        
        # 1. 센서 데이터 입력 처리 (센서 데이터는 4개 값)
        sensor_input = np.array([[float(sensor_data.get('mq2', 0)),
                                  float(sensor_data.get('temp', 0)),
                                  float(sensor_data.get('humidity', 0)),
                                  float(sensor_data.get('flame', 0))]])  # 4개의 입력 값
        
        # 센서 데이터 출력 (터미널에)
        print(f"[센서 데이터] board_id: {board_id}, mq2: {sensor_data.get('mq2', 0)}, temp: {sensor_data.get('temp', 0)}, humidity: {sensor_data.get('humidity', 0)}, flame: {sensor_data.get('flame', 0)}")

        # 2. 센서 데이터 정규화 (훈련 시 사용한 scaler로 변환)
        sensor_input_scaled = scaler.transform(sensor_input)  # 정규화 적용

        # 센서 데이터로부터 화재 확률 예측
        sensor_prob = float(sensor_model.predict(sensor_input_scaled)[0][0]) * 100
        
        # 3. 이미지 입력 처리 (YOLO 모델 사용)
        results = image_model.predict(image_path, conf=0.25)
        fire_conf = 0
        fire_detected = False
        img = cv2.imread(image_path)

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

            # 이미지 저장 후 오래된 이미지 삭제
            clean_old_images()  # 오래된 이미지 삭제 호출

        # 6. 예측 결과 반환
        result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sensor_fire_probability": round(sensor_prob, 2),
            "image_fire_confidence": round(fire_conf, 2),
            "final_score": round(final_score, 2),
            "fire_detected": fire_status,
            "image_path": save_path,
            "board_id": board_id  # board_id를 예측 결과에 포함
        }

        # 센서 데이터와 예측 결과를 함께 포함하여 하나의 항목으로 로그 저장
        data_with_sensor = {**result, "sensor_data": sensor_data}  # 예측 결과와 센서 데이터를 합침
        save_result_json(result)  # 최종 예측 결과 저장
        append_logs(board_id, data_with_sensor)  # 센서 데이터와 예측 결과를 함께 로그에 저장

        # 7. 화재가 감지되었든 아니든 항상 fire_log에 기록
        append_fire_log(result)  # fire_log.json에 화재 이벤트 저장

        # 화재 상태를 따로 저장하는 함수 호출
        save_fire_status_log(result)  # fire_status_log 저장

        return result

    except Exception as e:
        # 예측 실패 시 오류 반환
        print(f"[ERROR] 예측 실패: {e}")
        return {"error": str(e)}
