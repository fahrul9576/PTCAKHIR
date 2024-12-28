#include <Arduino.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <DHT.h>

// Konfigurasi Wi-Fi
#define SSID "vivo 1820"
#define PASSWORD "fahrulll"

// Konfigurasi Firebase
#define API_KEY "AIzaSyCIRHt94I-s5x6gSPYksiQMWOp3L7PCRMQ"
#define DATABASE_URL "https://proket-43fc0-default-rtdb.asia-southeast1.firebasedatabase.app/"

// Pin konfigurasi
#define DHT_PIN 15
#define MQ2_PIN 32
#define BUZZER_PIN 5  // Ganti pin untuk buzzer
int threshold = 2000;
DHT dht(DHT_PIN, DHT22);

// Firebase objek
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

// Fungsi untuk menentukan status suhu berdasarkan rentang
String interpretTemperature(float temp) {
  if (temp == 0) {
    return "Dingin Beku";
  } else if (temp <= 10) {
    return "Sangat Dingin";
  } else if (temp <= 20) {
    return "Sejuk";
  } else if (temp <= 30) {
    return "Hangat";
  } else if (temp <= 40) {
    return "Cukup Panas";
  } else if (temp <= 50) {
    return "Panas Tinggi";
  } else if (temp <= 60) {
    return "Sangat Panas";
  } else if (temp <= 70) {
    return "Panas Ekstrem";
  } else if (temp <= 80) {
    return "Panas Dekat Didih";
  } else if (temp <= 90) {
    return "Titik Didih";
  } else {
    return "Ekstrem Kritis";
  }
}

void setup() {
  Serial.begin(115200);

  // Menghubungkan ke Wi-Fi
  WiFi.begin(SSID, PASSWORD);
  Serial.print("Menghubungkan ke Wi-Fi ");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print("> ");
    delay(300);
  }
  Serial.println();
  Serial.print("Terhubung ke Wi-Fi dengan IP: ");
  Serial.println(WiFi.localIP());

  // Konfigurasi Firebase
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;

  if (Firebase.signUp(&config, &auth, "", "")) {
    Serial.println("Terhubung ke Firebase");
  } else {
    Serial.printf("Error Firebase: %s\n", config.signer.signupError.message.c_str());
  }

  Firebase.begin(&config, &auth);

  // Inisialisasi DHT
  dht.begin();

  // Inisialisasi pin
  pinMode(MQ2_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);  // Inisialisasi pin buzzer
  digitalWrite(BUZZER_PIN, LOW);  // Matikan buzzer di awal
}

void loop() {
  // Membaca sensor DHT
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  float f = dht.readTemperature(true);

  if (isnan(h) || isnan(t) || isnan(f)) {
    Serial.println(F("Gagal membaca nilai Sensor DHT!"));
    return;
  }

  Serial.print(F("Kelembaban: "));
  Serial.print(h);
  Serial.print(F("%, Suhu: "));
  Serial.print(t);
  Serial.print(F("\u00B0C / "));
  Serial.print(f);
  Serial.println(F("\u00B0F"));

  // Interpretasi status suhu
  String statusSuhu = interpretTemperature(t);
  Serial.print("Status suhu: ");
  Serial.println(statusSuhu);

  // Membaca nilai sensor MQ2
  int smokeValue = analogRead(MQ2_PIN);
  Serial.print("Nilai asap: ");
  Serial.println(smokeValue);

  // Mengirim data ke Firebase
  if (Firebase.ready()) {
    if (!Firebase.RTDB.setString(&fbdo, "/DATA_SENSOR/SUHU", String(t))) {
      Serial.println("Gagal mengirim data suhu ke Firebase.");
      Serial.println(fbdo.errorReason());
    }
    if (!Firebase.RTDB.setString(&fbdo, "/DATA_SENSOR/KELEMBABAN", String(h))) {
      Serial.println("Gagal mengirim data kelembaban ke Firebase.");
      Serial.println(fbdo.errorReason());
    }
    if (!Firebase.RTDB.setString(&fbdo, "/DATA_SENSOR/LEVEL_ASAP", String(smokeValue))) {
      Serial.println("Gagal mengirim data level asap ke Firebase.");
      Serial.println(fbdo.errorReason());
    }

    // Mengirim status suhu ke Firebase
    if (!Firebase.RTDB.setString(&fbdo, "/STATUS_SUHU", statusSuhu)) {
      Serial.println("Gagal mengirim status suhu ke Firebase.");
      Serial.println(fbdo.errorReason());
    }

    // Mengirim status kebakaran ke Firebase
    String statusAsap = (smokeValue > threshold) ? "TERDETEKSI" : "AMAN";
    if (!Firebase.RTDB.setString(&fbdo, "/STATUS_ASAP", statusAsap)) {
      Serial.println("Gagal mengirim status kebakaran ke Firebase.");
      Serial.println(fbdo.errorReason());
    }

    // Membaca status kamera dari Firebase
    if (Firebase.RTDB.getBool(&fbdo, "/status_kamera/fire_detected")) {
      bool fireDetected = fbdo.boolData();
      if (fireDetected) {
        Serial.println("KEBAKARAN TERDETEKSI OLEH KAMERA! Menyalakan buzzer...");
        digitalWrite(BUZZER_PIN, HIGH);  // Nyalakan buzzer
        delay(5000);  // Buzzer akan berbunyi selama 5 detik
        digitalWrite(BUZZER_PIN, LOW);   // Matikan buzzer
      }
    } else {
      Serial.println("Gagal membaca status kamera dari Firebase.");
      Serial.println(fbdo.errorReason());
    }
  } else {
    Serial.println("Firebase belum siap.");
  }

  // Mengontrol buzzer berdasarkan nilai asap
  if (smokeValue > threshold) {
    Serial.println("POTENSI KEBAKARAN TERDETEKSI! Menyalakan buzzer...");
    digitalWrite(BUZZER_PIN, HIGH);  // Nyalakan buzzer
    delay(5000);  // Buzzer akan berbunyi selama 5 detik
    digitalWrite(BUZZER_PIN, LOW);   // Matikan buzzer
  }

  delay(50);
}
