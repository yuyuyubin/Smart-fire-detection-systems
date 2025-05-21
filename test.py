import requests

url = "http://127.0.0.1:5000/predict"  # 또는 http://192.168.0.7:5000
files = {'image': open('test_fire2.jpg', 'rb')}
data = {
    'mq2': '300',
    'smoke': '400',
    'temp': '55',
    'humidity': '20',
    'flame': '0.9'
}

response = requests.post(url, files=files, data=data)
print(response.json())