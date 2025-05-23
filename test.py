import requests
import time
import os

# Flask server URL (replace with the actual server IP address)
url = "http://192.168.0.171:5000/predict"

while True:
    print("?? Capturing image using libcamera...")
    ret = os.system("libcamera-jpeg -o latest.jpg --width 416 --height 416 --nopreview")
    if ret != 0 or not os.path.exists("latest.jpg"):
        print("? Failed to capture image.")
        time.sleep(2)
        continue

    try:
        # Prepare image and sensor data
        with open("latest.jpg", "rb") as img_file:
            files = {
                'image': ("frame.jpg", img_file, 'image/jpeg')
            }
            data = {
                'mq2': '300',
                'smoke': '400',
                'temp': '55',
                'humidity': '30',
                'flame': '0.8'
            }

            print("?? Sending image and sensor data to the server...")
            response = requests.post(url, files=files, data=data, timeout=10)
            result = response.json()

            # Print the result
            print("? Server response:", result)

            if result.get("fire_detected"):
                print("?? FIRE DETECTED!")
            else:
                print("? No fire detected.")

        # ? Delete the latest.jpg file after sending it
        if os.path.exists("latest.jpg"):
            os.remove("latest.jpg")
            print("??? latest.jpg file has been deleted.")

    except Exception as e:
        print(f"? Failed to send request: {e}")

    # Wait 10 seconds before the next frame
    time.sleep(10)
