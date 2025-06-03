import os
import cv2
import numpy as np
import tensorflow as tf
from ultralytics import YOLO
from datetime import datetime
from utils.file_logger import save_result_json, append_logs, append_fire_log  # append_fire_log 추가

# 모델 로드
sensor_model = tf.keras.models.load_model(os.path.join("models", "fire_sensor_model_v2.h5"))
image_model = YOLO(os.path.join("models", "best8_ver2.pt"))

# 예측 처리 함수
def run_prediction_with_data(sensor_data, image_path):
    try:
        # 센서 데이터에서 board_id 가져오기
        board_id = sensor_data.get('board_id', 'Unknown')
        
        # 1. 센서 데이터 입력 처리 (센서 데이터는 4개 값)
        sensor_input = np.array([[float(sensor_data.get('mq2', 0)),
                                  float(sensor_data.get('flame', 0)),
                                  float(sensor_data.get('temp', 0)),
                                  float(sensor_data.get('humidity', 0))]])  # 4개의 입력 값
        
        # 센서 데이터로부터 화재 확률 예측
        sensor_prob = float(sensor_model.predict(sensor_input)[0][0]) * 100
        
        # 2. 이미지 입력 처리 (YOLO 모델 사용)
        results = image_model.predict(image_path, conf=0.25)
        fire_conf = 0
        fire_detected = False
        img = cv2.imread(image_path)

        # 3. 이미지에서 화재 탐지
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

        # 4. 센서 예측과 이미지 예측 결합
        final_score = sensor_prob * 0.6 + fire_conf * 0.4
        fire_status = final_score >= 70

        save_path = ""
        if fire_status:
            os.makedirs("static/detected", exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"static/detected/fire_{ts}.jpg"
            cv2.imwrite(save_path, img)

        # 5. 예측 결과 반환
        result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sensor_fire_probability": round(sensor_prob, 2),
            "image_fire_confidence": round(fire_conf, 2),
            "final_score": round(final_score, 2),
            "fire_detected": fire_status,
            "image_path": save_path,
            "board_id": board_id  # board_id를 예측 결과에 포함
        }

        # 6. 예측 결과와 로그 저장
        save_result_json(result)  # 최종 예측 결과 저장
        append_logs(board_id, result)  # 특정 board_id의 로그 저장

        # 7. 화재가 감지되었든 아니든 항상 fire_log에 기록
        append_fire_log(result)  # fire_log.json에 화재 이벤트 저장

        return result

    except Exception as e:
        # 예측 실패 시 오류 반환
        print(f"[ERROR] 예측 실패: {e}")
        return {"error": str(e)}
