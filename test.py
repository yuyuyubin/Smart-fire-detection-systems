import cv2

# ? Raspberry Pi�� ������� TCP MJPEG ��Ʈ�� �ּ�
url = "tcp://192.168.0.171:8888"

# ? OpenCV�� ��Ʈ�� ����
cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("? Failed to open stream")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("?? Failed to read frame")
        continue
    cv2.imshow("?? MJPEG Stream via TCP", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
