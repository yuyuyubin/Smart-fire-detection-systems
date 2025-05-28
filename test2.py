import requests
import time
import os
from datetime import datetime

# ✅ Flask 서버 URL (IP는 실시간 서버 IP로 맞춰줘야 함)
url = "http://192.168.0.171:5000/predict"

# ✅ 루프 시작
while True:
    print("📸 Capturing image using libcamera...")
    
    # 최신 이미지 파일 이름 설정 (타임스탬프 포함 가능)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_filename = f"latest.jpg"

    # ✅ libcamera-jpeg 명령어 실행
    ret = os.system(f"libcamera-jpeg -o {image_filename} --width 416 --height 416 --nopreview")
    
    # 실패 처리
    if ret != 0 or not os.path.exists(image_filename):
        print("❌ Failed to capture image.")
        time.sleep(2)
        continue

    try:
        # ✅ 센서 데이터 설정 (여기서 실시간 측정값으로 대체 가능)
        sensor_data = {
            'mq2': '300',         # 예: 가스 농도
            'smoke': '400',       # 예: 연기 농도
            'temp': '55',         # 온도 (°C)
            'humidity': '30',     # 습도 (%)
            'flame': '0.8'        # 불꽃 감지 확률 (0~1)
        }

        # ✅ 이미지 파일과 센서 데이터를 함께 전송
        with open(image_filename, "rb") as img_file:
            files = {
                'image': ("frame.jpg", img_file, 'image/jpeg')
            }

            print("🔗 Sending image and sensor data to the server...")
            response = requests.post(url, files=files, data=sensor_data, timeout=10)

            if response.status_code != 200:
                raise Exception(f"Bad status code: {response.status_code}")

            result = response.json()
            print("✅ Server response:")
            for k, v in result.items():
                print(f"  {k}: {v}")

            # 화재 여부 판단
            if result.get("fire_detected"):
                print("🚨 FIRE DETECTED!")
                # 여기에 부저 동작 등 추가 가능
            else:
                print("✅ No fire detected.")

    except Exception as e:
        print(f"⚠️ Failed to send request or parse response: {e}")

    finally:
        # ✅ 이미지 파일 삭제
        if os.path.exists(image_filename):
            os.remove(image_filename)
            print("🧹 Deleted temporary image file.")

        # ✅ 다음 요청까지 대기 시간
        time.sleep(10)
