import json
import os
import numpy as np
import tensorflow as tf
from datetime import datetime
import joblib

# 모델 로드
sensor_model = tf.keras.models.load_model(os.path.join("models", "fire_sensor_model_.h5"))

# 스칼라 로드
scaler = joblib.load(os.path.join("models", "scaler.pkl"))

# 예측 처리 함수 (스칼라 적용)
def run_prediction_with_data(sensor_data):
    try:
        # 센서 데이터에서 board_id 가져오기
        board_id = sensor_data.get('board_id', 'Unknown')

        # 1. 센서 데이터 입력 처리 (X_train 형식에 맞춰서 'mq2', 'temp', 'humidity', 'flame' 순서로)
        sensor_input = np.array([[float(sensor_data.get('mq2', 0)),
                                  float(sensor_data.get('temp', 0)),  # 'temp' -> 'temperature' 수정
                                  float(sensor_data.get('humidity', 0)),
                                  float(sensor_data.get('flame', 0))]])  # 순서 맞추기
        
        # 센서 데이터 출력 (터미널에)
        print(f"[센서 데이터] board_id: {board_id}, mq2: {sensor_data.get('mq2', 0)}, temp: {sensor_data.get('temp', 0)}, humidity: {sensor_data.get('humidity', 0)}, flame: {sensor_data.get('flame', 0)}")

        # 2. 센서 데이터 정규화 (훈련 시 사용한 scaler로 변환)
        sensor_input_scaled = scaler.transform(sensor_input)  # 정규화 적용

        # 3. 모델을 사용하여 예측
        sensor_prob = float(sensor_model.predict(sensor_input_scaled)[0][0]) * 100

        # 예측 확률을 95%로 제한 (선택 사항)
        if sensor_prob > 95:
            sensor_prob = 95

        # 예측 결과를 터미널에 출력
        print(f"[예측 결과] Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Sensor Fire Probability: {sensor_prob}%")
        print(f"Fire Detected: {'Yes' if sensor_prob >= 70 else 'No'}")

        # 예측 결과 반환
        result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sensor_fire_probability": round(sensor_prob, 2),
            "final_score": round(sensor_prob, 2),
            "fire_detected": sensor_prob >= 70,
            "board_id": board_id  # board_id를 예측 결과에 포함
        }

        return result

    except Exception as e:
        # 예측 실패 시 오류 반환
        print(f"[ERROR] 예측 실패: {e}")
        return {"error": str(e)}

# 예시 센서 데이터
sensor_data = {
    "board_id": "esp1",
    "mq2": 46,        # 첫 번째 센서 값
    "temp": 24.0,        # 두 번째 센서 값
    "humidity": 59.8,  # 세 번째 센서 값
    "flame": 0         # 네 번째 센서 값
}

# 예측 실행
if __name__ == "__main__":
    result = run_prediction_with_data(sensor_data)

    # 예측 결과 출력
    print("\n최종 예측 결과:")
    print(json.dumps(result, indent=4))