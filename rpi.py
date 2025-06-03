import subprocess
import requests
import time
import threading

# Flask server addresses for image and streaming video
IMAGE_SERVER_URL = "http://192.168.0.27:5000/api/image"  # For sending prediction images
STREAM_SERVER_URL = "http://192.168.0.27:5000/api/stream-frame"  # For sending streaming video frames

CAPTURE_INTERVAL_PREDICTION = 5  # Capture interval in seconds for prediction image (5 seconds)
CAPTURE_INTERVAL_STREAM = 0.1   # Capture interval in seconds for streaming video (10 fps)

# 1. Start live video streaming using libcamera-vid (H.264 codec for streaming)
def start_video_stream():
    subprocess.Popen([  # Start streaming via H.264 codec
        "libcamera-vid",
        "-n", "-t", "0",  # Infinite stream
        "--width", "640", "--height", "480", "--framerate", "10", "--codec", "h264", "--inline", "--listen",
        "-o", "tcp://192.168.0.171:8888"  # Stream to this address using H.264 codec
    ])

# 2. Capture image for prediction using libcamera-still and send it to Flask server (5 seconds interval)
def capture_and_send_image():
    while True:
        try:
            # Capture an image using libcamera-still for prediction
            result = subprocess.run(
                [
                    "libcamera-still",
                    "-n", "-t", "1",  # Capture for 1 second
                    "--width", "640",
                    "--height", "480",
                    "--output", "-"  # Output to stdout
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if result.returncode != 0:
                print("Failed to capture image")
                continue

            # Send the captured image to Flask server for prediction (POST request)
            response = requests.post(
                IMAGE_SERVER_URL,
                files={"image": ("frame.jpg", result.stdout, "image/jpeg")}
            )
            print(f"Image sent for prediction | Status: {response.status_code}")

        except Exception as e:
            print(f"Error in capturing and sending image: {e}")
        
        time.sleep(CAPTURE_INTERVAL_PREDICTION)  # Capture image every `CAPTURE_INTERVAL_PREDICTION` seconds (5 sec)
# 3. Send the streaming frame to Flask server for streaming (10 fps)
def send_stream_frame():
    while True:
        try:
            # Capture a frame using libcamera-still for streaming
            result = subprocess.run(
                [
                    "libcamera-still",
                    "-n", "-t", "1",  # Capture for 1 second
                    "--width", "640",
                    "--height", "480",
                    "--output", "-"  # Output to stdout
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if result.returncode != 0:
                print("Failed to capture streaming frame")
                continue

            # Send the video frame to Flask server for streaming (POST request)
            response = requests.post(
                STREAM_SERVER_URL,
                files={"frame": ("stream_frame.jpg", result.stdout, "image/jpeg")}
            )
            print(f"Streaming frame sent | Status: {response.status_code}")

        except Exception as e:
            print(f"Error in sending stream frame: {e}")

        time.sleep(CAPTURE_INTERVAL_STREAM)  # Send frame every `CAPTURE_INTERVAL_STREAM` seconds (10 fps)

if __name__ == "__main__":
    # Start video streaming in a separate thread
    video_thread = threading.Thread(target=start_video_stream, daemon=True)
    video_thread.start()

    # Start capturing and sending images for prediction in a separate thread (5 sec interval)
    image_thread = threading.Thread(target=capture_and_send_image, daemon=True)
    image_thread.start()

    # Start sending video frames to Flask server for streaming (10 fps) in a separate thread
    stream_thread = threading.Thread(target=send_stream_frame, daemon=True)
    stream_thread.start()

    # Keep the main thread running to allow other tasks to continue
    while True:
        time.sleep(1)