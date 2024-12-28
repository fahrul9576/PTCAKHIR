import time
import datetime
import requests
from ultralytics import YOLO
import cv2

# URL Firebase
firebase_url = "https://proket-43fc0-default-rtdb.asia-southeast1.firebasedatabase.app/status_kamera.json"

# Load model YOLO
model = YOLO("best.pt")

# Inisialisasi kamera
cap = cv2.VideoCapture(0)  

q
last_fire_detected = False  # Status api terakhir
fire_detected = False  # Status api saat ini
last_detection_time = 0  # Waktu deteksi terakhir
detection_interval = 10  # Interval untuk deteksi ulang dalam detik

# Fungsi untuk mengirim status ke Firebase
def send_to_firebase(status):
    firebase_url = "https://proket-43fc0-default-rtdb.asia-southeast1.firebasedatabase.app/status_kamera.json"
    try:
        data = {
            "fire_detected": status,
            "timestamp": datetime.datetime.now().isoformat()  # Timestamp deteksi
        }
        response = requests.put(firebase_url, json=data)
        if response.status_code == 200:
            print(f"Status berhasil dikirim ke Firebase: {data}")
        else:
            print(f"Gagal mengirim status ke Firebase: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Kesalahan saat mengirim ke Firebase: {e}")

# Mulai deteksi
while True:
    ret, frame = cap.read()
    if not ret:
        print("Gagal membaca frame.")
        break

    results = model(frame)
    detected = False

    # Periksa deteksi objek
    for detection in results[0].boxes:
        class_id = detection.cls.cpu().item()  # ID kelas objek
        confidence = detection.conf.cpu().item()  # Confidence level
        if class_id == 0 and confidence > 0.6:  # Misalnya ID api adalah 0
            detected = True

    # Update status jika ada deteksi baru atau tidak ada deteksi
    if detected != last_fire_detected:
        fire_detected = detected  # Update status deteksi
        last_fire_detected = detected  # Simpan status terakhir
        last_detection_time = time.time()  # Update waktu deteksi
        send_to_firebase(fire_detected)  # Kirim status ke Firebase

    # Tampilkan hasil deteksi pada frame
    annotated_frame = results[0].plot()
    cv2.imshow("Deteksi Api", annotated_frame)

    # Keluar jika tombol 'q' ditekan
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
