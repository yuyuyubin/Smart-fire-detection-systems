import requests
import os

url = "https://smartfire2.share.zrok.io/api/predict"
image_path = "test_fire.jpg"

# 이미지 파일 존재 여부 확인
if not os.path.exists(image_path):
    print(f"❌ 파일을 찾을 수 없습니다: {image_path}")
    exit()

# 요청 구성
files = {
    'image': (image_path, open(image_path, 'rb'), 'image/jpeg')
}
data = {
    'mq2': '300',
    'smoke': '400',
    'temp': '55',
    'humidity': '30',
    'flame': '0.8'
}

print("🔗 Sending request to server...")
response = requests.post(url, files=files, data=data)

# 응답 처리
try:
    result = response.json()
    print("✅ Server response:")
    for k, v in result.items():
        print(f"🔸 {k}: {v}")
except Exception as e:
    print("❗ 예외 발생:", e)
    print(f"📦 Status code: {response.status_code}")
    print(f"📄 Raw text: {response.text}")