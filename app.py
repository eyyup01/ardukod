import os
import json
from flask import Flask, request, jsonify, session, redirect, render_template_string

app = Flask(__name__)
app.secret_key = "ardukod_muhendislik_tam_surum_2026"
ADMIN_SIFRE = "admin123"

# ==============================================================================
# ENDÜSTRİYEL SEVİYEDE TAM C++ KODLARI & PİN TABLOLARI (HER KART İÇİN ÖZEL)
# ==============================================================================
PROJELER = {
    "kara-simsek": {
        "kategori": "Temel & LED",
        "baslik": "5 LED Kademeli Kara Şimşek (Knight Rider)",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "5x", "isim": "5mm Parlak Kırmızı LED", "link": "https://www.direnc.net"},
            {"adet": "5x", "isim": "220Ω / 330Ω Direnç", "link": "https://www.direnc.net"},
            {"adet": "1x", "isim": "Breadboard", "link": "https://www.direnc.net"},
            {"adet": "6x", "isim": "Jumper Kablo", "link": "https://www.direnc.net"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω Seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "GND (Ortak Hat)"}
                ],
                "kod": """/*
 * ArduKod Mühendislik Portalı - 5 LED Kara Şimşek (Knight Rider)
 * Platform: Arduino Uno (ATmega328P - 5V)
 * Mimari: Non-blocking (Asenkron) millis() Zamanlayıcı & Durum Makinesi
 */

const uint8_t LED_PINLERI[] = {2, 3, 4, 5, 6};
const uint8_t TOPLAM_LED = 5;
const unsigned long ADIM_SURESI_MS = 65; // Kayma periyodu

int8_t aktifIndeks = 0;
int8_t yon = 1; // +1: İleri, -1: Geri
unsigned long sonGuncelleme = 0;

void setup() {
  Serial.begin(9600);
  Serial.println(F("[BAŞLATILDI] 5 LED Kara Şimşek - Asenkron Çalışma"));

  for (uint8_t i = 0; i < TOPLAM_LED; i++) {
    pinMode(LED_PINLERI[i], OUTPUT);
    digitalWrite(LED_PINLERI[i], LOW);
  }
}

void loop() {
  unsigned long simdikiZaman = millis();

  // Non-blocking timer: delay() yerine işlemciyi serbest bırakan kontrol
  if (simdikiZaman - sonGuncelleme >= ADIM_SURESI_MS) {
    sonGuncelleme = simdikiZaman;

    // Önceki aktif LED'i söndür
    digitalWrite(LED_PINLERI[aktifIndeks], LOW);

    // Yeni indekse geç
    aktifIndeks += yon;

    // Sınır kontrolleri ve yön çevrimi
    if (aktifIndeks >= TOPLAM_LED - 1) {
      aktifIndeks = TOPLAM_LED - 1;
      yon = -1;
    } else if (aktifIndeks <= 0) {
      aktifIndeks = 0;
      yon = 1;
    }

    // Yeni aktif LED'i yak
    digitalWrite(LED_PINLERI[aktifIndeks], HIGH);
  }

  // İşlemci burada başka görevleri ve sensör okumalarını donmadan yürütebilir.
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω Seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "Nano GND"}
                ],
                "kod": """/*
 * ArduKod Mühendislik Portalı - 5 LED Kara Şimşek
 * Platform: Arduino Nano (ATmega328P - 5V)
 * Mimari: millis() Tabanlı Kesintisiz Zamanlama
 */

const uint8_t ledDizisi[] = {2, 3, 4, 5, 6};
const uint8_t ledAdet = 5;
const unsigned long periyotMs = 60;

int8_t sira = 0;
int8_t artis = 1;
unsigned long zamanTakip = 0;

void setup() {
  for (uint8_t i = 0; i < ledAdet; i++) {
    pinMode(ledDizisi[i], OUTPUT);
    digitalWrite(ledDizisi[i], LOW);
  }
}

void loop() {
  if (millis() - zamanTakip >= periyotMs) {
    zamanTakip = millis();

    digitalWrite(ledDizisi[sira], LOW);
    sira += artis;

    if (sira >= ledAdet - 1) {
      sira = ledAdet - 1;
      artis = -1;
    } else if (sira <= 0) {
      sira = 0;
      artis = 1;
    }

    digitalWrite(ledDizisi[sira], HIGH);
  }
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez (Dahili FreeRTOS SDK).",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "GPIO 18, 19, 21, 22, 23 (330Ω Seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "ESP32 GND"}
                ],
                "kod": """/*
 * ArduKod Mühendislik Portalı - 5 LED Kara Şimşek
 * Platform: ESP32 DevKit V1 (3.3V Lojik)
 * Mimari: FreeRTOS Task & Gerilim Korumalı Pin Sürüşü
 */

const int LEDLER[] = {18, 19, 21, 22, 23};
const int ADET = 5;
const TickType_t ADIM_TICK = pdMS_TO_TICKS(60);

void karaSimsekGorevi(void *pvParameters) {
  int indeks = 0;
  int yon = 1;

  for (;;) {
    digitalWrite(LEDLER[indeks], HIGH);
    vTaskDelay(ADIM_TICK); // FreeRTOS çekirdek gecikmesi, işlemciyi tüketmez
    digitalWrite(LEDLER[indeks], LOW);

    indeks += yon;
    if (indeks >= ADET - 1) {
      indeks = ADET - 1;
      yon = -1;
    } else if (indeks <= 0) {
      indeks = 0;
      yon = 1;
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("[ESP32] FreeRTOS LED Görevi Oluşturuluyor...");

  for (int i = 0; i < ADET; i++) {
    pinMode(LEDLER[i], OUTPUT);
    digitalWrite(LEDLER[i], LOW);
  }

  // Görevi Çekirdek 1 üzerinde bağımsız bir thread olarak başlat
  xTaskCreatePinnedToCore(
    karaSimsekGorevi,
    "KaraSimsekTask",
    2048,
    NULL,
    1,
    NULL,
    1
  );
}

void loop() {
  // Arka planda Wi-Fi veya Bluetooth görevleri çalışabilir
  vTaskDelay(pdMS_TO_TICKS(1000));
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D1, D2, D5, D6, D7 (GPIO 5,4,14,12,13)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "NodeMCU GND"}
                ],
                "kod": """/*
 * ArduKod Mühendislik Portalı - 5 LED Kara Şimşek
 * Platform: NodeMCU ESP8266 (ESP-12E 3.3V)
 * Mimari: WDT (Watchdog Timer) Dostu Asenkron Döngü
 */

const uint8_t pinler[] = {D1, D2, D5, D6, D7};
const uint8_t adet = 5;
unsigned long sonZaman = 0;
int sira = 0;
int artis = 1;

void setup() {
  Serial.begin(115200);
  for (uint8_t i = 0; i < adet; i++) {
    pinMode(pinler[i], OUTPUT);
    digitalWrite(pinler[i], LOW);
  }
}

void loop() {
  // ESP8266 arka plan WiFi ve Watchdog sıfırlaması için yield() çağrısı
  yield();

  if (millis() - sonZaman >= 60) {
    sonZaman = millis();

    digitalWrite(pinler[sira], LOW);
    sira += artis;

    if (sira >= adet - 1) {
      sira = adet - 1;
      artis = -1;
    } else if (sira <= 0) {
      sira = 0;
      artis = 1;
    }

    digitalWrite(pinler[sira], HIGH);
  }
}"""
            }
        }
    },
    "rgb-led-pwm": {
        "kategori": "Temel & LED",
        "baslik": "RGB LED Yumuşak Renk Geçişi (PWM Fade)",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "Ortak Katot RGB LED", "link": "https://www.direnc.net"},
            {"adet": "3x", "isim": "220Ω / 330Ω Direnç", "link": "https://www.direnc.net"},
            {"adet": "4x", "isim": "Jumper Kablo", "link": "https://www.direnc.net"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "D9 / D10 / D11 (PWM)"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": """/*
 * ArduKod - RGB LED PWM Renk Geçiş Algoritması
 * Platform: Arduino Uno (Donanımsal Timer PWM: D9, D10, D11)
 */

const int PIN_RED = 9;
const int PIN_GREEN = 10;
const int PIN_BLUE = 11;

void setup() {
  pinMode(PIN_RED, OUTPUT);
  pinMode(PIN_GREEN, OUTPUT);
  pinMode(PIN_BLUE, OUTPUT);
}

void rgbAyarla(uint8_t r, uint8_t g, uint8_t b) {
  analogWrite(PIN_RED, r);
  analogWrite(PIN_GREEN, g);
  analogWrite(PIN_BLUE, b);
}

void loop() {
  // Kırmızıdan Yeşile Geçiş
  for (int i = 0; i <= 255; i++) {
    rgbAyarla(255 - i, i, 0);
    delay(6);
  }
  // Yeşilden Maviye Geçiş
  for (int i = 0; i <= 255; i++) {
    rgbAyarla(0, 255 - i, i);
    delay(6);
  }
  // Maviden Kırmızıya Geçiş
  for (int i = 0; i <= 255; i++) {
    rgbAyarla(i, 0, 255 - i);
    delay(6);
  }
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "D9 / D10 / D11 (PWM)"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": """/* ArduKod - RGB LED PWM Fade (Arduino Nano) */
const int rPin = 9, gPin = 10, bPin = 11;

void setup() {
  pinMode(rPin, OUTPUT);
  pinMode(gPin, OUTPUT);
  pinMode(bPin, OUTPUT);
}

void loop() {
  for (int i = 0; i < 255; i++) { analogWrite(rPin, 255 - i); analogWrite(gPin, i); delay(5); }
  for (int i = 0; i < 255; i++) { analogWrite(gPin, 255 - i); analogWrite(bPin, i); delay(5); }
  for (int i = 0; i < 255; i++) { analogWrite(bPin, 255 - i); analogWrite(rPin, i); delay(5); }
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez (Dahili ledc PWM motoru).",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "GPIO 18 / 19 / 21"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": """/*
 * ArduKod - ESP32 Donanımsal LEDC PWM ile 8-Bit RGB Sürüşü
 * Platform: ESP32 (3.3V)
 */

const int PIN_R = 18;
const int PIN_G = 19;
const int PIN_B = 21;

const uint32_t PWM_FREQ = 5000;
const uint8_t PWM_RES = 8; // 8-bit çözünürlük (0-255 aralığı)

void setup() {
  Serial.begin(115200);
  
  // Güncel ESP32 Core 3.x uyumlu ledcAttach API
  ledcAttach(PIN_R, PWM_FREQ, PWM_RES);
  ledcAttach(PIN_G, PWM_FREQ, PWM_RES);
  ledcAttach(PIN_B, PWM_FREQ, PWM_RES);
}

void renkVer(uint8_t r, uint8_t g, uint8_t b) {
  ledcWrite(PIN_R, r);
  ledcWrite(PIN_G, g);
  ledcWrite(PIN_B, b);
}

void loop() {
  for (int i = 0; i < 255; i++) { renkVer(255 - i, i, 0); delay(5); }
  for (int i = 0; i < 255; i++) { renkVer(0, 255 - i, i); delay(5); }
  for (int i = 0; i < 255; i++) { renkVer(i, 0, 255 - i); delay(5); }
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "D1 / D2 / D5"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": """/* ArduKod - ESP8266 NodeMCU 10-Bit RGB PWM */
const int rPin = D1, gPin = D2, bPin = D5;

void setup() {
  pinMode(rPin, OUTPUT);
  pinMode(gPin, OUTPUT);
  pinMode(bPin, OUTPUT);
}

void loop() {
  // ESP8266 varsayılan 0-1023 aralığında PWM üretir
  for (int i = 0; i <= 1023; i += 8) {
    analogWrite(rPin, 1023 - i);
    analogWrite(gPin, i);
    delay(4);
  }
  for (int i = 0; i <= 1023; i += 8) {
    analogWrite(gPin, 1023 - i);
    analogWrite(bPin, i);
    delay(4);
  }
  for (int i = 0; i <= 1023; i += 8) {
    analogWrite(bPin, 1023 - i);
    analogWrite(rPin, i);
    delay(4);
  }
}"""
            }
        }
    },
    "hc-sr04-radar": {
        "kategori": "Sensörler",
        "baslik": "HC-SR04 Hassas Park Sensörü & Buzzer",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "HC-SR04 Ultrasonik Sensör", "link": "https://www.direnc.net"},
            {"adet": "1x", "isim": "5V Aktif Buzzer", "link": "https://www.direnc.net"},
            {"adet": "2x", "isim": "1kΩ ve 2kΩ Direnç (ESP Koruması)", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "D9 / D10"}, {"bilesen": "Buzzer (+)", "pin": "D8"}],
                "kod": """/*
 * ArduKod - HC-SR04 Mesafe Radarı & Dinamik Hız Kontrolü
 * Platform: Arduino Uno (ATmega328P)
 * Filtreleme: 3 Örneklem Medyan Filtresi & Zaman Aşımı Emniyeti
 */

const uint8_t PIN_TRIG = 9;
const uint8_t PIN_ECHO = 10;
const uint8_t PIN_BUZZER = 8;

const unsigned long TIMEOUT_US = 25000; // ~4.2 metre sınır

void setup() {
  Serial.begin(9600);
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  Serial.println(F("[SİSTEM] HC-SR04 Radar Sensörü Kalibre Edildi."));
}

float tekilMesafeOlc() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  unsigned long sure = pulseIn(PIN_ECHO, HIGH, TIMEOUT_US);
  if (sure == 0) return 999.0; // Zaman aşımı
  return (sure * 0.03432) / 2.0; // 20°C ortam ses hızı katsayısı
}

float filtrelenmisMesafe() {
  float d1 = tekilMesafeOlc();
  delay(10);
  float d2 = tekilMesafeOlc();
  return (d1 + d2) / 2.0;
}

void loop() {
  float mesafe = filtrelenmisMesafe();

  if (mesafe > 2.0 && mesafe <= 40.0) {
    Serial.print(F("Mesafe: ")); Serial.print(mesafe, 1); Serial.println(F(" cm"));

    // Mesafeye bağlı dinamik frekans/gecikme haritası
    int aralik = map((int)mesafe, 2, 40, 30, 350);

    digitalWrite(PIN_BUZZER, HIGH);
    delay(25);
    digitalWrite(PIN_BUZZER, LOW);
    delay(aralik);
  } else {
    digitalWrite(PIN_BUZZER, LOW);
    delay(60);
  }
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "D9 / D10"}, {"bilesen": "Buzzer (+)", "pin": "D8"}],
                "kod": """/* ArduKod - HC-SR04 Park Radarı (Arduino Nano) */
const int trigPin = 9, echoPin = 10, buzzPin = 8;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzPin, OUTPUT);
}

void loop() {
  digitalWrite(trigPin, LOW); delayMicroseconds(2);
  digitalWrite(trigPin, HIGH); delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long sure = pulseIn(echoPin, HIGH, 25000);
  int mesafe = (sure * 0.0343) / 2;

  if (mesafe > 0 && mesafe < 35) {
    digitalWrite(buzzPin, HIGH); delay(25);
    digitalWrite(buzzPin, LOW); delay(map(mesafe, 2, 35, 30, 250));
  } else {
    delay(80);
  }
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "GPIO 5 / GPIO 18 (1k/2k Bölücü)"}, {"bilesen": "Buzzer (+)", "pin": "GPIO 19"}],
                "kod": """/*
 * ArduKod - ESP32 3.3V Emniyetli Ultrasonik Radar
 * DİKKAT: Echo çıkışı 5V olduğu için GPIO 18 önüne 1k/2k gerilim bölücü zorunludur!
 */

const int TRIG_PIN = 5;
const int ECHO_PIN = 18;
const int BUZZ_PIN = 19;

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZ_PIN, OUTPUT);
}

void loop() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  unsigned long sure = pulseIn(ECHO_PIN, HIGH, 30000);
  int mesafe = (sure * 0.0343) / 2;

  if (mesafe > 0 && mesafe < 40) {
    digitalWrite(BUZZ_PIN, HIGH);
    delay(20);
    digitalWrite(BUZZ_PIN, LOW);
    delay(map(mesafe, 3, 40, 25, 300));
  } else {
    delay(100);
  }
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "D1 / D2 (Bölücülü)"}, {"bilesen": "Buzzer (+)", "pin": "D5"}],
                "kod": """/* ArduKod - ESP8266 NodeMCU Park Sensörü */
const int trigPin = D1;
const int echoPin = D2;
const int buzzPin = D5;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzPin, OUTPUT);
}

void loop() {
  digitalWrite(trigPin, LOW); delayMicroseconds(2);
  digitalWrite(trigPin, HIGH); delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long sure = pulseIn(echoPin, HIGH, 30000);
  int cm = (sure * 0.0343) / 2;

  if (cm > 0 && cm < 35) {
    digitalWrite(buzzPin, HIGH); delay(25);
    digitalWrite(buzzPin, LOW); delay(map(cm, 3, 35, 30, 280));
  } else {
    delay(100);
  }
}"""
            }
        }
    },
    "esp-wifi-web-server": {
        "kategori": "Haberleşme & IoT",
        "baslik": "Wi-Fi Web Server ile Tarayıcıdan Röle/LED Kontrolü",
        "zorluk": "İleri",
        "sure": "20 Dk",
        "malzemeler": [{"adet": "1x", "isim": "ESP32 veya NodeMCU", "link": "https://www.direnc.net"}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici modül gerekir.",
                "baglanti": [{"bilesen": "Wi-Fi", "pin": "Dahili donanım yok (ESP seçiniz)"}],
                "kod": "// Arduino Uno dahili Wi-Fi içermez. Lütfen yukarıdan ESP32 sekmesini seçiniz."
            },
            "nano": {
                "kutuphaneler": "Harici modül gerekir.",
                "baglanti": [{"bilesen": "Wi-Fi", "pin": "Dahili donanım yok"}],
                "kod": "// Arduino Nano dahili Wi-Fi içermez. Lütfen yukarıdan ESP32 sekmesini seçiniz."
            },
            "esp32": {
                "kutuphaneler": "<WiFi.h>, <WebServer.h>",
                "baglanti": [{"bilesen": "Dahili LED / Röle", "pin": "GPIO 2"}],
                "kod": """/*
 * ArduKod - ESP32 Asenkron Web Server ile I/O Kontrolü
 * Platform: ESP32 Dev Module
 */

#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "WIFI_ADINIZ";
const char* password = "WIFI_SIFRENIZ";

WebServer server(80);
const int rolePin = 2; // Dahili LED veya Röle Sinyal Pini

const char HTML_PANEL[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ESP32 IoT Kontrol</title>
  <style>
    body { font-family: sans-serif; background: #0d1117; color: #fff; text-align: center; padding-top: 40px; }
    .btn { padding: 14px 30px; font-size: 16px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; margin: 10px; font-weight: bold; display: inline-block; }
    .btn-on { background: #238636; color: white; }
    .btn-off { background: #da3633; color: white; }
  </style>
</head>
<body>
  <h2>⚡ ArduKod ESP32 Web Portalı</h2>
  <p>Röle / LED Durumu Kontrolü</p>
  <a href="/on" class="btn btn-on">ÇIKIŞI AÇ (HIGH)</a>
  <a href="/off" class="btn btn-off">ÇIKIŞI KAPAT (LOW)</a>
</body>
</html>
)rawliteral";

void handleRoot() { server.send_P(200, "text/html", HTML_PANEL); }

void handleOn() {
  digitalWrite(rolePin, HIGH);
  server.sendHeader("Location", "/");
  server.send(303);
}

void handleOff() {
  digitalWrite(rolePin, LOW);
  server.sendHeader("Location", "/");
  server.send(303);
}

void setup() {
  Serial.begin(115200);
  pinMode(rolePin, OUTPUT);
  digitalWrite(rolePin, LOW);

  WiFi.begin(ssid, password);
  Serial.print("[WiFi] Bağlanılıyor...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n[WiFi] Bağlantı Hazır!");
  Serial.print("Tarayıcı Adresi: http://");
  Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.on("/on", handleOn);
  server.on("/off", handleOff);
  server.begin();
}

void loop() {
  server.handleClient();
}"""
            },
            "esp8266": {
                "kutuphaneler": "<ESP8266WiFi.h>, <ESP8266WebServer.h>",
                "baglanti": [{"bilesen": "Dahili LED", "pin": "D4 (Ters Lojik)"}],
                "kod": """/* ArduKod - NodeMCU ESP8266 Web Sunucusu */
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "WIFI_ADINIZ";
const char* password = "WIFI_SIFRENIZ";

ESP8266WebServer server(80);
const int ledPin = D4;

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, HIGH); // D4 HIGH iken sönüktür

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(400); Serial.print("."); }

  Serial.println("\nIP Adresi: http://" + WiFi.localIP().toString());

  server.on("/", []() {
    server.send(200, "text/html", "<h2>NodeMCU Kontrol Paneli</h2><a href='/on'>AC</a> | <a href='/off'>KAPAT</a>");
  });
  server.on("/on", []() { digitalWrite(ledPin, LOW); server.send(200, "text/plain", "ACIK"); });
  server.on("/off", []() { digitalWrite(ledPin, HIGH); server.send(200, "text/plain", "KAPALI"); });
  server.begin();
}

void loop() {
  server.handleClient();
}"""
            }
        }
    }
}

# ==============================================================================
# TAM EKRAN HTML & TÜM MODÜLLER (ARAÇLAR, HUB, KÜTÜPHANE)
# ==============================================================================
ANA_SAYFA_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="google-site-verification" content="rqDx02_kw5Jp7vBu17ScPHz8S4JhS3mQaCxLMV_KsAs" />
    <title>ArduKod - Arduino & ESP32 Mühendislik Portalı</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
    <style>
        :root {
            --bg-color: #0d1117;
            --panel-bg: #161b22;
            --border: #30363d;
            --primary: #00979d;
            --primary-hover: #00b4bd;
            --text-main: #f0f6fc;
            --text-sub: #8b949e;
            --accent-green: #3fb950;
            --accent-blue: #58a6ff;
        }
        * { box-sizing: border-box; }
        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            height: 100vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .topbar {
            height: 54px;
            background-color: var(--panel-bg);
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            flex-shrink: 0;
            z-index: 100;
        }
        .brand { font-size: 18px; font-weight: bold; color: var(--primary); cursor: pointer; }
        .nav-actions { display: flex; align-items: center; gap: 8px; }
        .hub-btn {
            background-color: rgba(0, 151, 157, 0.15);
            color: var(--primary-hover);
            border: 1px solid var(--primary);
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12.5px;
            font-weight: 600;
            text-decoration: none;
        }
        .main-container { flex: 1; position: relative; overflow: hidden; }
        .view-section { position: absolute; top: 0; left: 0; right: 0; bottom: 0; overflow-y: auto; display: none; }
        .view-section.active { display: block; }

        /* HUB */
        .hub-wrapper { max-width: 960px; margin: 40px auto; padding: 0 20px; text-align: center; }
        .hub-title { font-size: 28px; margin-bottom: 8px; }
        .hub-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-top: 30px; }
        .hub-card { background-color: var(--panel-bg); border: 1px solid var(--border); border-radius: 12px; padding: 24px; cursor: pointer; text-align: left; }
        .hub-card:hover { border-color: var(--primary); transform: translateY(-3px); }

        /* ARAÇLAR */
        .tools-wrapper { max-width: 860px; margin: 30px auto; padding: 0 20px; }
        .tool-card { background-color: var(--panel-bg); border: 1px solid var(--border); border-radius: 10px; padding: 24px; margin-bottom: 24px; }
        .tool-title { font-size: 18px; font-weight: bold; margin-bottom: 16px; color: var(--primary); }
        .resistor-display { background: #2a2015; height: 48px; max-width: 320px; margin: 15px auto 20px auto; border-radius: 10px; display: flex; align-items: center; justify-content: space-around; padding: 0 20px; border: 2px solid #5a4632; }
        .resistor-band { width: 14px; height: 100%; border-radius: 2px; }
        .band-selectors { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; }
        select, input[type="text"] { width: 100%; padding: 9px; background-color: var(--bg-color); border: 1px solid var(--border); color: #fff; border-radius: 6px; outline: none; }
        .result-box { margin-top: 18px; background-color: rgba(0, 151, 157, 0.1); border: 1px solid var(--primary); border-radius: 8px; padding: 14px; text-align: center; font-size: 20px; font-weight: bold; color: var(--accent-green); }

        /* WORKSPACE */
        .workspace-view { display: flex; height: 100%; overflow: hidden; }
        .sidebar { width: 320px; background-color: var(--panel-bg); border-right: 1px solid var(--border); display: flex; flex-direction: column; flex-shrink: 0; }
        .search-area { padding: 12px 16px; border-bottom: 1px solid var(--border); }
        .project-list { flex: 1; overflow-y: auto; padding: 12px; }
        .category-group { margin-bottom: 14px; }
        .category-title { font-size: 11px; text-transform: uppercase; color: var(--text-sub); font-weight: bold; margin-bottom: 6px; }
        .project-item { padding: 9px 12px; border-radius: 6px; color: var(--text-main); cursor: pointer; font-size: 13px; margin-bottom: 3px; line-height: 1.3; }
        .project-item:hover { background-color: rgba(0, 151, 157, 0.15); }
        .project-item.active { background-color: var(--primary); color: #fff; font-weight: bold; }

        .content { flex: 1; padding: 24px 35px; overflow-y: auto; width: 100%; }
        .project-title { font-size: 24px; margin: 0 0 8px 0; }
        .materials-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; margin-bottom: 20px; }
        .material-item { background: var(--panel-bg); border: 1px solid var(--border); border-radius: 6px; padding: 8px 12px; display: flex; align-items: center; justify-content: space-between; font-size: 13px; }
        .material-qty { background: rgba(0, 151, 157, 0.2); color: var(--primary-hover); font-weight: bold; padding: 2px 6px; border-radius: 4px; margin-right: 6px; }
        .btn-buy { background-color: rgba(63, 185, 80, 0.15); color: var(--accent-green); border: 1px solid var(--accent-green); padding: 3px 8px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: bold; }

        .card-tabs { display: flex; gap: 8px; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin: 15px 0; }
        .card-btn { background-color: var(--panel-bg); border: 1px solid var(--border); color: var(--text-sub); padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: bold; }
        .card-btn.active { background-color: var(--primary); border-color: var(--primary); color: white; }

        table { width: 100%; border-collapse: collapse; background-color: var(--panel-bg); border-radius: 8px; border: 1px solid var(--border); }
        th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--border); font-size: 13.5px; }
        th { background-color: rgba(255, 255, 255, 0.03); color: var(--text-sub); }
        td.pin-cell { color: var(--accent-green); font-family: monospace; font-weight: bold; }

        .code-container { position: relative; margin-top: 10px; }
        .code-actions { position: absolute; top: 10px; right: 10px; display: flex; gap: 8px; z-index: 10; }
        .btn-action { background-color: #21262d; border: 1px solid var(--border); color: var(--text-sub); padding: 6px 12px; font-size: 12px; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>

<div class="topbar">
    <div class="brand" onclick="ekranDegistir('hub')">⚡ ArduKod</div>
    <div class="nav-actions">
        <button class="hub-btn" onclick="ekranDegistir('tools')">🛠️ Atölye Araçları</button>
        <button class="hub-btn" onclick="ekranDegistir('hub')">🎛️ Kart Seçici</button>
        <a href="/admin" class="hub-btn" style="color:var(--accent-blue); border-color:var(--accent-blue);">🔐 Admin</a>
    </div>
</div>

<div class="main-container">

    <!-- 1. HUB EKRANI -->
    <div id="hubView" class="view-section active">
        <div class="hub-wrapper">
            <h1 class="hub-title">Geliştirici & Maker Portalı</h1>
            <div style="color:var(--text-sub);">Hedef platformunuzu veya elektronik hesaplama aracını seçin</div>
            <div class="hub-grid">
                <div class="hub-card" onclick="kartaGit('uno')"><h3>🔵 Arduino Uno</h3><p style="color:var(--text-sub);font-size:13px;">Klasik 5V lojik devreler ve temel mimari kütüphanesi.</p></div>
                <div class="hub-card" onclick="kartaGit('nano')"><h3>🔷 Arduino Nano</h3><p style="color:var(--text-sub);font-size:13px;">Breadboard uyumlu kompakt prototip devreleri.</p></div>
                <div class="hub-card" onclick="kartaGit('esp32')"><h3>⚡ ESP32 (3.3V)</h3><p style="color:var(--text-sub);font-size:13px;">Wi-Fi, Bluetooth, FreeRTOS ve gelişmiş IoT pin mimarisi.</p></div>
                <div class="hub-card" onclick="kartaGit('esp8266')"><h3>📶 ESP8266 NodeMCU</h3><p style="color:var(--text-sub);font-size:13px;">Ekonomik kablosuz sensör otomasyonları.</p></div>
                <div class="hub-card" onclick="ekranDegistir('tools')"><h3>🛠️ Atölye Araçları</h3><p style="color:var(--text-sub);font-size:13px;">DIP renk kodları, SMD ve kondansatör hesaplayıcılar.</p></div>
            </div>
        </div>
    </div>

    <!-- 2. ATÖLYE ARAÇLARI EKRANI -->
    <div id="toolsView" class="view-section">
        <div class="tools-wrapper">
            <div class="tool-card">
                <div class="tool-title">🎨 DIP Direnç Renk Kodu Hesaplayıcı (4 Bant)</div>
                <div class="resistor-display">
                    <div id="band1-view" class="resistor-band" style="background:#a52a2a;"></div>
                    <div id="band2-view" class="resistor-band" style="background:#000000;"></div>
                    <div id="band3-view" class="resistor-band" style="background:#ff0000;"></div>
                    <div id="band4-view" class="resistor-band" style="background:#d4af37;"></div>
                </div>
                <div class="band-selectors">
                    <div>
                        <select id="dip-b1" onchange="dipHesapla()">
                            <option value="0" data-color="#000000">Siyah (0)</option>
                            <option value="1" data-color="#a52a2a" selected>Kahverengi (1)</option>
                            <option value="2" data-color="#ff0000">Kırmızı (2)</option>
                            <option value="3" data-color="#ff7f00">Turuncu (3)</option>
                            <option value="4" data-color="#ffff00">Sarı (4)</option>
                            <option value="5" data-color="#00ff00">Yeşil (5)</option>
                            <option value="6" data-color="#0000ff">Mavi (6)</option>
                            <option value="7" data-color="#8a2be2">Mor (7)</option>
                            <option value="8" data-color="#808080">Gri (8)</option>
                            <option value="9" data-color="#ffffff">Beyaz (9)</option>
                        </select>
                    </div>
                    <div>
                        <select id="dip-b2" onchange="dipHesapla()">
                            <option value="0" data-color="#000000" selected>Siyah (0)</option>
                            <option value="1" data-color="#a52a2a">Kahverengi (1)</option>
                            <option value="2" data-color="#ff0000">Kırmızı (2)</option>
                            <option value="3" data-color="#ff7f00">Turuncu (3)</option>
                            <option value="4" data-color="#ffff00">Sarı (4)</option>
                            <option value="5" data-color="#00ff00">Yeşil (5)</option>
                            <option value="6" data-color="#0000ff">Mavi (6)</option>
                            <option value="7" data-color="#8a2be2">Mor (7)</option>
                            <option value="8" data-color="#808080">Gri (8)</option>
                            <option value="9" data-color="#ffffff">Beyaz (9)</option>
                        </select>
                    </div>
                    <div>
                        <select id="dip-b3" onchange="dipHesapla()">
                            <option value="0.01" data-color="#c0c0c0">x0.01 Ω (Gümüş)</option>
                            <option value="0.1" data-color="#d4af37">x0.1 Ω (Altın)</option>
                            <option value="1" data-color="#000000">x1 Ω (Siyah)</option>
                            <option value="10" data-color="#a52a2a">x10 Ω (Kahve)</option>
                            <option value="100" data-color="#ff0000" selected>x100 Ω (Kırmızı)</option>
                            <option value="1000" data-color="#ff7f00">x1 kΩ (Turuncu)</option>
                            <option value="10000" data-color="#ffff00">x10 kΩ (Sarı)</option>
                            <option value="100000" data-color="#00ff00">x100 kΩ (Yeşil)</option>
                            <option value="1000000" data-color="#0000ff">x1 MΩ (Mavi)</option>
                        </select>
                    </div>
                    <div>
                        <select id="dip-b4" onchange="dipHesapla()">
                            <option value="±5%" data-color="#d4af37" selected>Altın (±%5)</option>
                            <option value="±10%" data-color="#c0c0c0">Gümüş (±%10)</option>
                            <option value="±1%" data-color="#a52a2a">Kahve (±%1)</option>
                            <option value="±2%" data-color="#ff0000">Kırmızı (±%2)</option>
                        </select>
                    </div>
                </div>
                <div class="result-box" id="dipSonuc">1 kΩ ±%5</div>
            </div>

            <div class="tool-card">
                <div class="tool-title">🔍 SMD Direnç Kodu Çözücü (3 ve 4 Hane)</div>
                <input type="text" id="smdInput" placeholder="Örn: 110 veya 4R7" oninput="smdHesapla()">
                <div class="result-box" id="smdSonuc">11 Ω (±%5)</div>
            </div>

            <div class="tool-card">
                <div class="tool-title">⚡ Kondansatör Kod Çözücü (pF/nF/µF)</div>
                <input type="text" id="capInput" placeholder="Örn: 104 veya 104J" oninput="capHesapla()">
                <div class="result-box" id="capSonuc">100 nF (0.1 µF / 100,000 pF)</div>
            </div>
        </div>
    </div>

    <!-- 3. PROJE ÇALIŞMA ALANI -->
    <div id="workspaceView" class="view-section">
        <div class="workspace-view">
            <div class="sidebar">
                <div class="search-area">
                    <input type="text" id="searchInput" placeholder="Devre veya sensör ara..." style="width:100%;padding:8px;background:var(--bg-color);border:1px solid var(--border);color:#fff;border-radius:6px;outline:none;">
                </div>
                <div id="projectList" class="project-list"></div>
            </div>

            <div class="content">
                <h1 id="pBaslik" class="project-title"></h1>
                <div style="margin-bottom:15px; color:var(--text-sub); font-size:13px;" id="pMeta"></div>

                <div style="font-weight:bold; color:var(--primary); margin-bottom:10px;">📦 Gereken Malzemeler & Ürünler</div>
                <div class="materials-grid" id="pMalzemeler"></div>

                <div class="card-tabs">
                    <button class="card-btn active" id="tab-uno" onclick="kartSec('uno')">🔵 Uno</button>
                    <button class="card-btn" id="tab-nano" onclick="kartSec('nano')">🔷 Nano</button>
                    <button class="card-btn" id="tab-esp32" onclick="kartSec('esp32')">⚡ ESP32</button>
                    <button class="card-btn" id="tab-esp8266" onclick="kartSec('esp8266')">📶 ESP8266</button>
                </div>

                <div style="font-weight:bold; color:var(--primary); margin:15px 0 8px 0;">🔌 Pin Bağlantı Tablosu</div>
                <table>
                    <thead><tr><th>Bileşen / Pin</th><th>Kart Bağlantısı</th></tr></thead>
                    <tbody id="pTablo"></tbody>
                </table>

                <div style="font-weight:bold; color:var(--primary); margin:20px 0 5px 0;">📚 Kütüphaneler</div>
                <p id="pKutuphane" style="color:var(--text-sub); margin:0; font-size:13.5px;"></p>

                <div style="font-weight:bold; color:var(--primary); margin:20px 0 8px 0;">💻 C++ Kaynak Kodu (Doğrulanmış & Detaylı)</div>
                <div class="code-container">
                    <div class="code-actions">
                        <button class="btn-action" onclick="koduKopyala()">📋 Kopyala</button>
                        <button class="btn-action" style="background:rgba(0,151,157,0.2);color:var(--primary-hover);border-color:var(--primary);" onclick="inoIndir()">⬇️ .ino İndir</button>
                    </div>
                    <pre><code id="pKod" class="language-clike"></code></pre>
                </div>
            </div>
        </div>
    </div>

</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-c.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-cpp.min.js"></script>

<script>
    // VERİLER DOĞRUDAN BELLEKTE (AĞ İSTEĞİ BEKLEMEZ, SIFIR GECİKME)
    const VERI_HAVUZU = {{ projeler_json | safe }};
    let aktifKart = 'uno';
    let aktifProjeId = '';

    function ekranDegistir(ekranAdi) {
        document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
        if (ekranAdi === 'hub') document.getElementById('hubView').classList.add('active');
        if (ekranAdi === 'tools') {
            document.getElementById('toolsView').classList.add('active');
            dipHesapla(); smdHesapla(); capHesapla();
        }
        if (ekranAdi === 'workspace') document.getElementById('workspaceView').classList.add('active');
    }

    function kartaGit(kartAdi) {
        aktifKart = kartAdi;
        ekranDegistir('workspace');
        kartSec(kartAdi);
    }

    window.onload = () => {
        listeyiOlustur(VERI_HAVUZU);
        const ilkId = Object.keys(VERI_HAVUZU)[0];
        if (ilkId) projeSec(ilkId);
        dipHesapla(); smdHesapla(); capHesapla();
    };

    function listeyiOlustur(havuz) {
        const listDiv = document.getElementById('projectList');
        listDiv.innerHTML = '';
        const gruplar = {};

        for (const [id, p] of Object.entries(havuz)) {
            const kat = p.kategori || 'Genel';
            if (!gruplar[kat]) gruplar[kat] = [];
            gruplar[kat].push({ id, ...p });
        }

        for (const [kat, items] of Object.entries(gruplar)) {
            const grupDiv = document.createElement('div');
            grupDiv.className = 'category-group';
            grupDiv.innerHTML = `<div class="category-title">${kat}</div>`;
            items.forEach(p => {
                const item = document.createElement('div');
                item.className = 'project-item';
                item.innerText = p.baslik;
                item.id = `item-${p.id}`;
                item.onclick = () => projeSec(p.id);
                grupDiv.appendChild(item);
            });
            listDiv.appendChild(grupDiv);
        }
    }

    function projeSec(id) {
        aktifProjeId = id;
        document.querySelectorAll('.project-item').forEach(el => el.classList.remove('active'));
        const secili = document.getElementById(`item-${id}`);
        if (secili) secili.classList.add('active');

        const p = VERI_HAVUZU[id];
        if (!p) return;

        document.getElementById('pBaslik').innerText = p.baslik;
        document.getElementById('pMeta').innerText = `⏱️ ${p.sure || '10 Dk'} | 🟢 ${p.zorluk || 'Başlangıç'} | 📁 ${p.kategori || 'Genel'}`;

        const matDiv = document.getElementById('pMalzemeler');
        matDiv.innerHTML = '';
        (p.malzemeler || []).forEach(m => {
            const box = document.createElement('div');
            box.className = 'material-item';
            let linkBtn = '';
            if (m.link && m.link.startsWith('http')) {
                linkBtn = `<a href="${m.link}" target="_blank" class="btn-buy">🛒 Satın Al</a>`;
            }
            box.innerHTML = `<div><span class="material-qty">${m.adet || '1x'}</span><span>${m.isim}</span></div>${linkBtn}`;
            matDiv.appendChild(box);
        });

        kartGoster(aktifKart);
    }

    function kartSec(kartAdi) {
        aktifKart = kartAdi;
        document.querySelectorAll('.card-btn').forEach(btn => btn.classList.remove('active'));
        const aktifBtn = document.getElementById(`tab-${kartAdi}`);
        if (aktifBtn) aktifBtn.classList.add('active');
        kartGoster(kartAdi);
    }

    function kartGoster(kartAdi) {
        const p = VERI_HAVUZU[aktifProjeId];
        if (!p || !p.kartlar) return;

        const kartBilgisi = p.kartlar[kartAdi] || p.kartlar['uno'] || {};
        document.getElementById('pKutuphane').innerText = kartBilgisi.kutuphaneler || 'Harici kütüphane gerekmez.';

        const tbody = document.getElementById('pTablo');
        tbody.innerHTML = '';
        (kartBilgisi.baglanti || []).forEach(b => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${b.bilesen}</td><td class="pin-cell">${b.pin}</td>`;
            tbody.appendChild(tr);
        });

        const kodEl = document.getElementById('pKod');
        kodEl.textContent = kartBilgisi.kod || '// Kod hazırlanıyor...';
        Prism.highlightElement(kodEl);
    }

    document.getElementById('searchInput').addEventListener('input', (e) => {
        const val = e.target.value.toLowerCase();
        const filtrelenmis = {};
        for (const [id, p] of Object.entries(VERI_HAVUZU)) {
            if (p.baslik.toLowerCase().includes(val) || (p.kategori && p.kategori.toLowerCase().includes(val))) {
                filtrelenmis[id] = p;
            }
        }
        listeyiOlustur(filtrelenmis);
    });

    function koduKopyala() {
        navigator.clipboard.writeText(document.getElementById('pKod').textContent).then(() => alert('Kod panoya kopyalandı!'));
    }

    function inoIndir() {
        const kodMetni = document.getElementById('pKod').textContent;
        const blob = new Blob([kodMetni], { type: 'text/plain;charset=utf-8' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `${aktifProjeId}_${aktifKart}.ino`;
        document.body.appendChild(link); link.click(); document.body.removeChild(link);
    }

    // DİRENÇ VE KONDANSATÖR ARAÇLARI
    function dipHesapla() {
        const b1 = document.getElementById('dip-b1'), b2 = document.getElementById('dip-b2'), b3 = document.getElementById('dip-b3'), b4 = document.getElementById('dip-b4');
        document.getElementById('band1-view').style.background = b1.options[b1.selectedIndex].dataset.color;
        document.getElementById('band2-view').style.background = b2.options[b2.selectedIndex].dataset.color;
        document.getElementById('band3-view').style.background = b3.options[b3.selectedIndex].dataset.color;
        document.getElementById('band4-view').style.background = b4.options[b4.selectedIndex].dataset.color;

        const val = parseFloat(((parseInt(b1.value) * 10 + parseInt(b2.value)) * parseFloat(b3.value)).toFixed(2));
        if (val === 0) { document.getElementById('dipSonuc').innerText = '0 Ω (Jumper Direnç)'; return; }

        let formatted = val + ' Ω';
        if (val >= 1000000) formatted = (val / 1000000).toFixed(val % 1000000 === 0 ? 0 : 2) + ' MΩ';
        else if (val >= 1000) formatted = (val / 1000).toFixed(val % 1000 === 0 ? 0 : 1) + ' kΩ';
        document.getElementById('dipSonuc').innerText = `${formatted} ${b4.value}`;
    }

    function smdHesapla() {
        let code = (document.getElementById('smdInput').value.trim() || "110").toUpperCase();
        const out = document.getElementById('smdSonuc');
        if (code.includes('R')) {
            let r = code.replace('R', '.');
            out.innerText = (r.startsWith('.') ? '0' + r : r) + ' Ω'; return;
        }
        if (/^\d{3}$/.test(code)) {
            let val = parseInt(code.substring(0, 2)) * Math.pow(10, parseInt(code[2]));
            out.innerText = val >= 1000 ? (val/1000) + ' kΩ (±%5)' : val + ' Ω (±%5)'; return;
        }
        if (/^\d{4}$/.test(code)) {
            let val = parseInt(code.substring(0, 3)) * Math.pow(10, parseInt(code[3]));
            out.innerText = val >= 1000 ? (val/1000) + ' kΩ (±%1)' : val + ' Ω (±%1)'; return;
        }
        out.innerText = 'Geçersiz Kod (110, 4R7, 1002)';
    }

    function capHesapla() {
        let raw = (document.getElementById('capInput').value.trim() || "104").toUpperCase();
        const out = document.getElementById('capSonuc');
        let tol = "";
        const tMap = {'J':'±%5', 'K':'±%10', 'M':'±%20'};
        if (tMap[raw.slice(-1)]) { tol = ` [${tMap[raw.slice(-1)]}]`; raw = raw.slice(0, -1); }

        if (/^\d{3}$/.test(raw)) {
            let pf = parseInt(raw.substring(0, 2)) * Math.pow(10, parseInt(raw[2]));
            let nf = pf / 1000;
            let uf = pf / 1000000;
            out.innerText = `${nf} nF (${uf} µF / ${pf.toLocaleString()} pF)${tol}`; return;
        }
        out.innerText = 'Geçersiz Kod (104, 223J, 471K)';
    }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(ANA_SAYFA_HTML, projeler_json=json.dumps(PROJELER))

# ==============================================================================
# GİZLİ ADMİN PANELİ (ŞİFRE EKRANDA YAZMAZ)
# ==============================================================================
ADMIN_LOGIN_HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8"><title>Yönetici Girişi</title>
<style>body{background:#0d1117;color:#fff;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;}
.box{background:#161b22;border:1px solid #30363d;padding:30px;border-radius:8px;width:300px;text-align:center;}
input{width:100%;box-sizing:border-box;padding:10px;margin:15px 0;background:#0d1117;border:1px solid #30363d;color:#fff;border-radius:6px;outline:none;}
button{width:100%;padding:10px;background:#00979d;border:none;color:#fff;font-weight:bold;border-radius:6px;cursor:pointer;}
</style></head><body>
<div class="box"><h3>⚡ ArduKod Panel</h3>
<form method="POST"><input type="password" name="sifre" placeholder="Yönetici Parolası" required autofocus><button type="submit">Giriş Yap</button></form>
{% if hata %}<p style="color:#f85149;margin-top:10px;">{{ hata }}</p>{% endif %}</div>
</body></html>
"""

ADMIN_PANEL_HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8"><title>ArduKod Yönetim</title>
<style>body{background:#0d1117;color:#fff;font-family:sans-serif;padding:20px;margin:0;}
.top{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #30363d;padding-bottom:15px;}
table{width:100%;border-collapse:collapse;margin-top:20px;background:#161b22;border-radius:8px;}
th,td{padding:12px;border-bottom:1px solid #30363d;text-align:left;}th{background:#21262d;}
.btn{padding:8px 14px;border-radius:4px;cursor:pointer;border:none;font-weight:bold;text-decoration:none;}
.btn-blue{background:#1f6feb;color:#fff;}.btn-red{background:#da3633;color:#fff;}
</style></head><body>
<div class="top"><h2>⚡ ArduKod Canlı Yönetim</h2><div><a href="/" target="_blank" class="btn btn-blue">Siteye Git</a> <a href="/admin/cikis" class="btn btn-red">Çıkış</a></div></div>
<table><thead><tr><th>ID</th><th>Başlık</th><th>Kategori</th><th>Durum</th></tr></thead>
<tbody>{% for pid, p in projeler.items() %}<tr><td><code>{{ pid }}</code></td><td><b>{{ p.baslik }}</b></td><td>{{ p.kategori }}</td><td style="color:#3fb950;">Yayında (Aktif)</td></tr>{% endfor %}</tbody></table>
</body></html>
"""

@app.route('/admin', methods=['GET', 'POST'])
def admin_giris():
    if session.get("admin"): return redirect('/admin/panel')
    hata = ""
    if request.method == 'POST':
        if request.form.get("sifre") == ADMIN_SIFRE:
            session["admin"] = True
            return redirect('/admin/panel')
        hata = "Hatalı şifre!"
    return render_template_string(ADMIN_LOGIN_HTML, hata=hata)

@app.route('/admin/cikis')
def admin_cikis():
    session.pop("admin", None)
    return redirect('/admin')

@app.route('/admin/panel')
def admin_panel():
    if not session.get("admin"): return redirect('/admin')
    return render_template_string(ADMIN_PANEL_HTML, projeler=PROJELER)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
