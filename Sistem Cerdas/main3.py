import cv2
import urllib.request
import numpy as np
import time
from ultralytics import YOLO
import os
import requests  # Untuk mengirim data ke Firebase

# Load model YOLO untuk deteksi api
model = YOLO(f"{os.getcwd()}/best.pt")
cap = cv2.VideoCapture(1)
# Alamat IP ESP32-CAM
url = "http://192.168.0.67/cam-mid.jpg"

# URL Firebase Realtime Database
firebase_url = "https://proket-43fc0-default-rtdb.asia-southeast1.firebasedatabase.app/fire_status.json"
# Fungsi untuk mengirim status ke Firebase
def send_to_firebase(status):
    try:
        data = {
            "fire_detected": status,
            "timestamp": time.time()  # Timestamp untuk tracking waktu
        }
        response = requests.put(firebase_url, json=data)  # Pastikan URL diakhiri dengan .json
        if response.status_code == 200:
            print(f"Status berhasil dikirim ke Firebase: {data}")
        else:
            print(f"Gagal mengirim status ke Firebase: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Kesalahan saat mengirim ke Firebase: {e}")

# Fungsi untuk streaming video dari ESP32-CAM
def stream_video(url):
    while True:  # Loop utama untuk mencoba menyambung ulang jika terjadi kesalahan
        try:
            # Buka koneksi stream dengan timeout
            stream = urllib.request.urlopen(url, timeout=10)
            bytes_stream = b""

            print("Memulai stream...")

            while True:
                # Membaca data gambar dari stream
                bytes_stream += stream.read(1024)
                a = bytes_stream.find(b"\xff\xd8")  # Awal JPEG
                b = bytes_stream.find(b"\xff\xd9")  # Akhir JPEG

                if a != -1 and b != -1:
                    # Ekstraksi data gambar
                    jpg = bytes_stream[a : b + 2]
                    bytes_stream = bytes_stream[b + 2 :]

                    # Decode gambar menjadi format OpenCV
                    img_np = np.frombuffer(jpg, dtype=np.uint8)
                    img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

                    if img is not None:
                        # Mulai waktu pemrosesan
                        start_time = time.time()

                        # Deteksi api menggunakan YOLO
                        results = model(img, conf=0.8)
                        fire_detected = 0  # Default: Tidak ada api

                        for result in results:
                            boxes = result.boxes
                            for box in boxes:
                                x1, y1, x2, y2 = box.xyxy.tolist()[0]
                                c = box.cls
                                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                                label = model.names[int(c)]

                                if label == "fire":  # Jika objek adalah api
                                    fire_detected = 1
                                    # Gambar bounding box dan label
                                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                                    cv2.putText(
                                        img,
                                        label,
                                        (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.9,
                                        (0, 255, 0),
                                        2,
                                    )

                        # Akhiri waktu pemrosesan
                        end_time = time.time()

                        # Cetak status deteksi api dan waktu pemrosesan
                        print(f"Fire detected: {fire_detected} | Processing time: {end_time - start_time:.2f} seconds")

                        # Kirim status deteksi ke Firebase
                        send_to_firebase(fire_detected)

                        # Tampilkan video dengan bounding box
                        cv2.imshow("ESP32-CAM Stream", img)

                    # Berhenti jika tombol 'q' ditekan
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        print("Berhenti...")
                        break

        except urllib.error.HTTPError as e:
            print(f"Kesalahan HTTP: {e.code} - {e.reason}")
            time.sleep(1)  # Tunggu sebelum mencoba lagi
        except urllib.error.URLError as e:
            print(f"Kesalahan URL: {e.reason}. Periksa jaringan atau alamat ESP32-CAM Anda.")
            time.sleep(1)  # Tunggu sebelum mencoba lagi
        except cv2.error as e:
            print(f"Kesalahan OpenCV: {e}")
        except Exception as e:
            print(f"Kesalahan tak terduga: {e}")
            time.sleep(1)  # Tunggu sebelum mencoba lagi
        finally:
            try:
                stream.close()  # Pastikan stream ditutup
            except:
                pass

# Main program
if __name__ == "__main__":
    try:
        stream_video(url)
    except KeyboardInterrupt:
        print("Program dihentikan oleh pengguna.")
    finally:
        cv2.destroyAllWindows()  # Tutup semua jendela OpenCV
