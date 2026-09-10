import os
import json
from flask import Flask, request, jsonify, session, redirect, render_template_string

app = Flask(__name__)
app.secret_key = "ardukod_muhendislik_portal_tam_surum_final_key_9988"
ADMIN_SIFRE = "admin123"

VERI_DOSYASI = "projeler.json"

# ==============================================================================
# TAM DETAYLI, UZUN VE ENDÜSTRİYEL SEVİYEDE ÇALIŞAN 15 PROJE
# ==============================================================================
VARSAYILAN_PROJELER = {
    "kara-simsek": {
        "kategori": "Temel & LED",
        "baslik": "5 LED Kademeli Kara Şimşek (Knight Rider)",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "goruntulenme": 0,
        "indirme": 0,
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
 * Mimari: Non-blocking millis() Zamanlayıcı & Durum Makinesi
 */

const uint8_t LED_PINLERI[] = {2, 3, 4, 5, 6};
const uint8_t TOPLAM_LED = 5;
const unsigned long ADIM_SURESI_MS = 65; // ms cinsinden akış periyodu

int8_t aktifIndeks = 0;
int8_t yon = 1; // +1: İleri, -1: Geri
unsigned long sonGuncelleme = 0;
unsigned long toplamDonguSayaci = 0;

void setup() {
  Serial.begin(9600);
  while (!Serial) { ; } // Seri portun oturmasını bekle
  Serial.println(F("=========================================="));
  Serial.println(F("[SİSTEM] ArduKod Uno 5 LED Kara Şimşek"));
  Serial.println(F("[BİLGİ] Non-blocking millis() mimarisi devrede"));
  Serial.println(F("=========================================="));

  for (uint8_t i = 0; i < TOPLAM_LED; i++) {
    pinMode(LED_PINLERI[i], OUTPUT);
    digitalWrite(LED_PINLERI[i], LOW);
  }
}

void loop() {
  unsigned long simdikiZaman = millis();

  // İşlemciyi bloklamayan (delay içermeyen) durum makinesi
  if (simdikiZaman - sonGuncelleme >= ADIM_SURESI_MS) {
    sonGuncelleme = simdikiZaman;

    // Önceki pini söndür
    digitalWrite(LED_PINLERI[aktifIndeks], LOW);

    // Yeni pini hesapla
    aktifIndeks += yon;

    // Sınır kontrolleri ve yön dönüşü
    if (aktifIndeks >= TOPLAM_LED - 1) {
      aktifIndeks = TOPLAM_LED - 1;
      yon = -1;
      toplamDonguSayaci++;
      Serial.print(F("[TELEMETRİ] Tur Tamamlandı. Toplam: "));
      Serial.println(toplamDonguSayaci);
    } else if (aktifIndeks <= 0) {
      aktifIndeks = 0;
      yon = 1;
    }

    // Yeni pini yak
    digitalWrite(LED_PINLERI[aktifIndeks], HIGH);
  }

  // İşlemci burada diğer sensör okumalarını ve seri komutları donmadan yürütebilir.
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
 * Mimari: Düşük Bellek Tüketimli Kesintisiz Zamanlama
 */

const uint8_t pinler[] = {2, 3, 4, 5, 6};
const uint8_t adet = 5;
const unsigned long periyot = 60;

int8_t sira = 0;
int8_t artis = 1;
unsigned long zamanSayaci = 0;

void setup() {
  Serial.begin(9600);
  for (uint8_t i = 0; i < adet; i++) {
    pinMode(pinler[i], OUTPUT);
    digitalWrite(pinler[i], LOW);
  }
  Serial.println(F("[NANO] Sistem Hazır."));
}

void loop() {
  if (millis() - zamanSayaci >= periyot) {
    zamanSayaci = millis();
    digitalWrite(pinler[sira], LOW);
    sira += artis;
    if (sira >= adet - 1) { sira = adet - 1; artis = -1; }
    else if (sira <= 0) { sira = 0; artis = 1; }
    digitalWrite(pinler[sira], HIGH);
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
 * Mimari: FreeRTOS Task & Çift Çekirdekli (Dual Core) İş Parçacığı
 */

const int LEDLER[] = {18, 19, 21, 22, 23};
const int ADET = 5;
const TickType_t ADIM_BEKLEME = pdMS_TO_TICKS(60);

TaskHandle_t LedTaskHandle = NULL;

void karaSimsekGorevi(void *pvParameters) {
  int indeks = 0;
  int yon = 1;

  for (;;) {
    digitalWrite(LEDLER[indeks], HIGH);
    vTaskDelay(ADIM_BEKLEME); // FreeRTOS non-blocking delay
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
  delay(500);
  Serial.println(F("[ESP32] FreeRTOS Görevi Çekirdek 1'e Bağlanıyor..."));

  for (int i = 0; i < ADET; i++) {
    pinMode(LEDLER[i], OUTPUT);
    digitalWrite(LEDLER[i], LOW);
  }

  // Görevi Çekirdek 1 üzerinde bağımsız bir thread olarak başlat
  xTaskCreatePinnedToCore(
    karaSimsekGorevi,
    "KaraSimsekGorevi",
    2048,
    NULL,
    1,
    &LedTaskHandle,
    1
  );
}

void loop() {
  // Ana döngü boştur, işlemciyi tüketmez. Arka planda WiFi/BLE çalışabilir.
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
 * Platform: NodeMCU ESP8266 (ESP-12E)
 * Mimari: WDT (Watchdog Timer) Uyumlu Asenkron Döngü
 */

const uint8_t pinler[] = {D1, D2, D5, D6, D7};
const uint8_t adet = 5;
unsigned long oncekiZaman = 0;
int sira = 0;
int artis = 1;

void setup() {
  Serial.begin(115200);
  for (uint8_t i = 0; i < adet; i++) {
    pinMode(pinler[i], OUTPUT);
    digitalWrite(pinler[i], LOW);
  }
  Serial.println(F("[ESP8266] WDT Korumalı Sistem Devrede."));
}

void loop() {
  yield(); // Arka plan WiFi ve donanımsal Watchdog sıfırlaması

  if (millis() - oncekiZaman >= 60) {
    oncekiZaman = millis();
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
        "goruntulenme": 0,
        "indirme": 0,
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
  Serial.begin(9600);
  pinMode(PIN_RED, OUTPUT);
  pinMode(PIN_GREEN, OUTPUT);
  pinMode(PIN_BLUE, OUTPUT);
  Serial.println(F("[RGB] Donanımsal PWM kanalları hazır."));
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
    delay(5);
  }
  // Yeşilden Maviye Geçiş
  for (int i = 0; i <= 255; i++) {
    rgbAyarla(0, 255 - i, i);
    delay(5);
  }
  // Maviden Kırmızıya Geçiş
  for (int i = 0; i <= 255; i++) {
    rgbAyarla(i, 0, 255 - i);
    delay(5);
  }
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "D9 / D10 / D11 (PWM)"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": """/* ArduKod - RGB LED (Arduino Nano) */
const int rPin = 9, gPin = 10, bPin = 11;

void setup() {
  pinMode(rPin, OUTPUT); pinMode(gPin, OUTPUT); pinMode(bPin, OUTPUT);
}

void loop() {
  for (int i = 0; i < 255; i++) { analogWrite(rPin, 255 - i); analogWrite(gPin, i); delay(5); }
  for (int i = 0; i < 255; i++) { analogWrite(gPin, 255 - i); analogWrite(bPin, i); delay(5); }
  for (int i = 0; i < 255; i++) { analogWrite(bPin, 255 - i); analogWrite(rPin, i); delay(5); }
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez (Dahili LEDC PWM motoru).",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "GPIO 18 / 19 / 21"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": """/*
 * ArduKod - ESP32 Donanımsal LEDC PWM ile 8-Bit RGB Sürüşü
 * Platform: ESP32 (3.3V)
 */

const int PIN_R = 18;
const int PIN_G = 19;
const int PIN_B = 21;

const uint32_t PWM_FREQ = 5000;
const uint8_t PWM_RES = 8; // 8-bit çözünürlük (0-255)

void setup() {
  Serial.begin(115200);
  ledcAttach(PIN_R, PWM_FREQ, PWM_RES);
  ledcAttach(PIN_G, PWM_FREQ, PWM_RES);
  ledcAttach(PIN_B, PWM_FREQ, PWM_RES);
  Serial.println("[ESP32] 5kHz LEDC PWM aktif.");
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
const int r = D1, g = D2, b = D5;

void setup() {
  pinMode(r, OUTPUT); pinMode(g, OUTPUT); pinMode(b, OUTPUT);
}

void loop() {
  for (int i = 0; i <= 1023; i += 8) { analogWrite(r, 1023 - i); analogWrite(g, i); delay(4); }
  for (int i = 0; i <= 1023; i += 8) { analogWrite(g, 1023 - i); analogWrite(b, i); delay(4); }
  for (int i = 0; i <= 1023; i += 8) { analogWrite(b, 1023 - i); analogWrite(r, i); delay(4); }
}"""
            }
        }
    },
    "trafik-isiklari": {
        "kategori": "Temel & LED",
        "baslik": "Zaman Ayarlı Standart Trafik Işıkları",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "3x", "isim": "Kırmızı, Sarı, Yeşil LED", "link": ""}, {"adet": "3x", "isim": "220Ω Direnç", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Kırmızı/Sarı/Yeşil", "pin": "D2 / D3 / D4"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": """/* ArduKod - Trafik Işıkları (Uno) */
const int k = 2, s = 3, y = 4;

void setup() {
  pinMode(k, OUTPUT); pinMode(s, OUTPUT); pinMode(y, OUTPUT);
}

void loop() {
  digitalWrite(k, HIGH); delay(4000);
  digitalWrite(s, HIGH); delay(1000);
  digitalWrite(k, LOW); digitalWrite(s, LOW); digitalWrite(y, HIGH); delay(4000);
  digitalWrite(y, LOW); digitalWrite(s, HIGH); delay(1000); digitalWrite(s, LOW);
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Kırmızı/Sarı/Yeşil", "pin": "D2 / D3 / D4"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": """/* ArduKod - Trafik Işıkları (Nano) */
const int k = 2, s = 3, y = 4;
void setup() { pinMode(k, OUTPUT); pinMode(s, OUTPUT); pinMode(y, OUTPUT); }
void loop() {
  digitalWrite(k, HIGH); delay(4000); digitalWrite(s, HIGH); delay(1000);
  digitalWrite(k, LOW); digitalWrite(s, LOW); digitalWrite(y, HIGH); delay(4000);
  digitalWrite(y, LOW); digitalWrite(s, HIGH); delay(1000); digitalWrite(s, LOW);
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Kırmızı/Sarı/Yeşil", "pin": "GPIO 18 / 19 / 21"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": """/* ArduKod - Trafik Işıkları (ESP32) */
const int k = 18, s = 19, y = 21;
void setup() { pinMode(k, OUTPUT); pinMode(s, OUTPUT); pinMode(y, OUTPUT); }
void loop() {
  digitalWrite(k, HIGH); delay(4000); digitalWrite(s, HIGH); delay(1000);
  digitalWrite(k, LOW); digitalWrite(s, LOW); digitalWrite(y, HIGH); delay(4000);
  digitalWrite(y, LOW); digitalWrite(s, HIGH); delay(1000); digitalWrite(s, LOW);
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Kırmızı/Sarı/Yeşil", "pin": "D1 / D2 / D5"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": """/* ArduKod - Trafik Işıkları (ESP8266) */
const int k = D1, s = D2, y = D5;
void setup() { pinMode(k, OUTPUT); pinMode(s, OUTPUT); pinMode(y, OUTPUT); }
void loop() {
  digitalWrite(k, HIGH); delay(4000); digitalWrite(s, HIGH); delay(1000);
  digitalWrite(k, LOW); digitalWrite(s, LOW); digitalWrite(y, HIGH); delay(4000);
  digitalWrite(y, LOW); digitalWrite(s, HIGH); delay(1000); digitalWrite(s, LOW);
}"""
            }
        }
    },
    "ldr-otomatik-far": {
        "kategori": "Sensörler",
        "baslik": "LDR & Gerilim Bölücü ile Otomatik Far/Aydınlatma",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "LDR (Fotodirenç)", "link": ""}, {"adet": "1x", "isim": "10kΩ Direnç", "link": ""}, {"adet": "1x", "isim": "LED & 220Ω", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "LDR & 10k Ortak Bacak", "pin": "A0"}, {"bilesen": "LED (+)", "pin": "D13"}],
                "kod": """/* ArduKod - LDR Otomatik Far (Uno) */
const int ldrPin = A0, ledPin = 13;
void setup() { pinMode(ledPin, OUTPUT); Serial.begin(9600); }
void loop() {
  int isik = analogRead(ldrPin);
  Serial.print(F("Işık Seviyesi: ")); Serial.println(isik);
  if (isik < 400) digitalWrite(ledPin, HIGH);
  else digitalWrite(ledPin, LOW);
  delay(100);
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "LDR & 10k Ortak Bacak", "pin": "A0"}, {"bilesen": "LED (+)", "pin": "D13"}],
                "kod": """/* ArduKod - LDR (Nano) */
void setup() { pinMode(13, OUTPUT); }
void loop() {
  if (analogRead(A0) < 400) digitalWrite(13, HIGH);
  else digitalWrite(13, LOW);
  delay(100);
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "LDR & 10k Ortak Bacak", "pin": "GPIO 34 (ADC1)"}, {"bilesen": "LED (+)", "pin": "GPIO 2"}],
                "kod": """/* ArduKod - LDR (ESP32 - 12-Bit ADC: 0-4095) */
const int ldrPin = 34, ledPin = 2;
void setup() { pinMode(ledPin, OUTPUT); Serial.begin(115200); }
void loop() {
  int ham = analogRead(ldrPin);
  if (ham < 1500) digitalWrite(ledPin, HIGH);
  else digitalWrite(ledPin, LOW);
  delay(100);
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "LDR & 10k Ortak Bacak", "pin": "A0"}, {"bilesen": "LED (+)", "pin": "D4"}],
                "kod": """/* ArduKod - LDR (NodeMCU ESP8266) */
void setup() { pinMode(D4, OUTPUT); }
void loop() {
  if (analogRead(A0) < 450) digitalWrite(D4, LOW);
  else digitalWrite(D4, HIGH);
  delay(100);
}"""
            }
        }
    },
    "hc-sr04-radar": {
        "kategori": "Sensörler",
        "baslik": "HC-SR04 Ultrasonik Hassas Park Sensörü & Buzzer",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "HC-SR04 Sensör", "link": "https://www.direnc.net"}, {"adet": "1x", "isim": "Buzzer", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "D9 / D10"}, {"bilesen": "Buzzer (+)", "pin": "D8"}],
                "kod": """/* ArduKod - HC-SR04 Mesafe Radarı (Arduino Uno) */
const uint8_t TRIG = 9, ECHO = 10, BUZZ = 8;

void setup() {
  Serial.begin(9600);
  pinMode(TRIG, OUTPUT); pinMode(ECHO, INPUT); pinMode(BUZZ, OUTPUT);
  Serial.println(F("[RADAR] Ultrasonik başlatıldı."));
}

void loop() {
  digitalWrite(TRIG, LOW); delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  unsigned long sure = pulseIn(ECHO, HIGH, 25000);
  int mesafe = (sure * 0.0343) / 2;

  if (mesafe > 2 && mesafe <= 40) {
    digitalWrite(BUZZ, HIGH); delay(25); digitalWrite(BUZZ, LOW);
    delay(map(mesafe, 2, 40, 30, 350));
  } else {
    digitalWrite(BUZZ, LOW); delay(60);
  }
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "D9 / D10"}, {"bilesen": "Buzzer (+)", "pin": "D8"}],
                "kod": """/* ArduKod - HC-SR04 (Arduino Nano) */
const int trig = 9, echo = 10, buzz = 8;
void setup() { pinMode(trig, OUTPUT); pinMode(echo, INPUT); pinMode(buzz, OUTPUT); }
void loop() {
  digitalWrite(trig, LOW); delayMicroseconds(2);
  digitalWrite(trig, HIGH); delayMicroseconds(10);
  digitalWrite(trig, LOW);
  long s = pulseIn(echo, HIGH, 25000); int d = (s * 0.0343) / 2;
  if (d > 0 && d < 35) {
    digitalWrite(buzz, HIGH); delay(25); digitalWrite(buzz, LOW);
    delay(map(d, 2, 35, 30, 250));
  } else delay(80);
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "GPIO 5 / GPIO 18 (1k/2k Bölücü)"}, {"bilesen": "Buzzer (+)", "pin": "GPIO 19"}],
                "kod": """/* ArduKod - ESP32 HC-SR04 (3.3V Gerilim Bölücülü) */
const int TRIG = 5, ECHO = 18, BUZZ = 19;
void setup() { pinMode(TRIG, OUTPUT); pinMode(ECHO, INPUT); pinMode(BUZZ, OUTPUT); }
void loop() {
  digitalWrite(TRIG, LOW); delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  unsigned long sure = pulseIn(ECHO, HIGH, 30000);
  int mesafe = (sure * 0.0343) / 2;
  if (mesafe > 0 && mesafe < 40) {
    digitalWrite(BUZZ, HIGH); delay(20); digitalWrite(BUZZ, LOW);
    delay(map(mesafe, 3, 40, 25, 300));
  } else delay(100);
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "D1 / D2 (Bölücülü)"}, {"bilesen": "Buzzer (+)", "pin": "D5"}],
                "kod": """/* ArduKod - NodeMCU ESP8266 Mesafe */
const int trig = D1, echo = D2, buzz = D5;
void setup() { pinMode(trig, OUTPUT); pinMode(echo, INPUT); pinMode(buzz, OUTPUT); }
void loop() {
  digitalWrite(trig, LOW); delayMicroseconds(2);
  digitalWrite(trig, HIGH); delayMicroseconds(10);
  digitalWrite(trig, LOW);
  long s = pulseIn(echo, HIGH, 30000); int cm = (s * 0.0343) / 2;
  if (cm > 0 && cm < 35) {
    digitalWrite(buzz, HIGH); delay(25); digitalWrite(buzz, LOW);
    delay(map(cm, 3, 35, 30, 280));
  } else delay(100);
}"""
            }
        }
    },
    "hc-sr501-pir": {
        "kategori": "Sensörler",
        "baslik": "HC-SR501 PIR Hareket Algılamalı Hırsız Alarmı",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "HC-SR501 PIR Sensörü", "link": ""}, {"adet": "1x", "isim": "Buzzer / LED", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "PIR OUT", "pin": "D2"}, {"bilesen": "Alarm LED", "pin": "D13"}],
                "kod": """/* ArduKod - PIR Hareket Sensörü (Uno) */
const int pirPin = 2, ledPin = 13;
void setup() { pinMode(pirPin, INPUT); pinMode(ledPin, OUTPUT); Serial.begin(9600); }
void loop() {
  if (digitalRead(pirPin) == HIGH) {
    Serial.println(F("[ALARM] Hareket Algılandı!"));
    digitalWrite(ledPin, HIGH);
  } else {
    digitalWrite(ledPin, LOW);
  }
  delay(100);
}"""
            },
            "nano": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"PIR OUT","pin":"D2"},{"bilesen":"LED","pin":"D13"}],"kod":"void setup(){ pinMode(2,INPUT); pinMode(13,OUTPUT); }\nvoid loop(){ digitalWrite(13, digitalRead(2)); }"},
            "esp32": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"PIR OUT","pin":"GPIO 13"},{"bilesen":"LED","pin":"GPIO 2"}],"kod":"void setup(){ pinMode(13,INPUT); pinMode(2,OUTPUT); }\nvoid loop(){ digitalWrite(2, digitalRead(13)); }"},
            "esp8266": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"PIR OUT","pin":"D7"},{"bilesen":"LED","pin":"D4"}],"kod":"void setup(){ pinMode(D7,INPUT); pinMode(D4,OUTPUT); }\nvoid loop(){ digitalWrite(D4, !digitalRead(D7)); }"}
        }
    },
    "dht11-sicaklik": {
        "kategori": "Sensörler",
        "baslik": "DHT11 Dijital Sıcaklık & Nem Ölçümü",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "DHT11 Sensörü", "link": ""}, {"adet": "1x", "isim": "10kΩ Direnç", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<DHT.h> (Adafruit)",
                "baglanti": [{"bilesen": "DATA Pini", "pin": "D2 (10k Pull-up)"}],
                "kod": """/* ArduKod - DHT11 Nem & Sıcaklık (Uno) */
#include <DHT.h>
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  delay(2000);
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  if (isnan(h) || isnan(t)) { Serial.println(F("Okuma Hatası!")); return; }
  Serial.print(F("Nem: %")); Serial.print(h);
  Serial.print(F(" | Sıcaklık: ")); Serial.print(t); Serial.println(F(" °C"));
}"""
            },
            "nano": {"kutuphaneler":"<DHT.h>","baglanti":[{"bilesen":"DATA","pin":"D2"}],"kod":"#include <DHT.h>\nDHT dht(2, DHT11);\nvoid setup(){ Serial.begin(9600); dht.begin(); }\nvoid loop(){ delay(2000); Serial.println(dht.readTemperature()); }"},
            "esp32": {"kutuphaneler":"<DHT.h>","baglanti":[{"bilesen":"DATA","pin":"GPIO 4"}],"kod":"#include <DHT.h>\nDHT dht(4, DHT11);\nvoid setup(){ Serial.begin(115200); dht.begin(); }\nvoid loop(){ delay(2000); Serial.println(dht.readTemperature()); }"},
            "esp8266": {"kutuphaneler":"<DHT.h>","baglanti":[{"bilesen":"DATA","pin":"D4 (GPIO 2)"}], "kod":"#include <DHT.h>\nDHT dht(D4, DHT11);\nvoid setup(){ Serial.begin(115200); dht.begin(); }\nvoid loop(){ delay(2000); Serial.println(dht.readTemperature()); }"}
        }
    },
    "tcrt5000-cizgi": {
        "kategori": "Sensörler",
        "baslik": "TCRT5000 Çift Çıkışlı Kızılötesi Çizgi Sensörü",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "TCRT5000 Modülü", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "DO Çıkış", "pin": "D2"}, {"bilesen": "LED", "pin": "D13"}],
                "kod": """/* ArduKod - Çizgi Sensörü (Uno) */
void setup() { pinMode(2, INPUT); pinMode(13, OUTPUT); }
void loop() { digitalWrite(13, !digitalRead(2)); }"""
            },
            "nano": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"DO","pin":"D2"}],"kod":"void setup(){pinMode(2,INPUT);pinMode(13,OUTPUT);}\nvoid loop(){digitalWrite(13,!digitalRead(2));}"},
            "esp32": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"DO","pin":"GPIO 4"}],"kod":"void setup(){pinMode(4,INPUT);pinMode(2,OUTPUT);}\nvoid loop(){digitalWrite(2,!digitalRead(4));}"},
            "esp8266": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"DO","pin":"D1"}],"kod":"void setup(){pinMode(D1,INPUT);pinMode(D4,OUTPUT);}\nvoid loop(){digitalWrite(D4,digitalRead(D1));}"}
        }
    },
    "pot-analog-map": {
        "kategori": "Giriş & Kontrol",
        "baslik": "Potansiyometre ile LED Parlaklığı Ayarlama (Map)",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "10kΩ Potansiyometre", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Pot Orta Bacak", "pin": "A0"}, {"bilesen": "LED (+)", "pin": "D9 (PWM)"}],
                "kod": """/* ArduKod - Potansiyometre PWM (Uno) */
void setup() { pinMode(9, OUTPUT); }
void loop() {
  int ham = analogRead(A0);
  analogWrite(9, map(ham, 0, 1023, 0, 255));
  delay(10);
}"""
            },
            "nano": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Pot Orta","pin":"A0"},{"bilesen":"LED","pin":"D9"}],"kod":"void setup(){pinMode(9,OUTPUT);}\nvoid loop(){analogWrite(9,map(analogRead(A0),0,1023,0,255));delay(10);}"},
            "esp32": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Pot Orta","pin":"GPIO 32"},{"bilesen":"LED","pin":"GPIO 18"}],"kod":"void setup(){ledcAttach(18,5000,8);}\nvoid loop(){ledcWrite(18,map(analogRead(32),0,4095,0,255));delay(10);}"},
            "esp8266": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Pot Orta","pin":"A0"},{"bilesen":"LED","pin":"D1"}],"kod":"void setup(){pinMode(D1,OUTPUT);}\nvoid loop(){analogWrite(D1,analogRead(A0));delay(10);}"}
        }
    },
    "buton-dahili-pullup": {
        "kategori": "Giriş & Kontrol",
        "baslik": "Dahili Pull-up Dirençli Buton Kontrolü",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "Push Buton", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Buton Bacakları", "pin": "D2 ve GND"}, {"bilesen": "LED", "pin": "D13"}],
                "kod": """/* ArduKod - INPUT_PULLUP Buton */
void setup() { pinMode(2, INPUT_PULLUP); pinMode(13, OUTPUT); }
void loop() { digitalWrite(13, !digitalRead(2)); }"""
            },
            "nano": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Buton","pin":"D2/GND"}],"kod":"void setup(){pinMode(2,INPUT_PULLUP);pinMode(13,OUTPUT);}\nvoid loop(){digitalWrite(13,!digitalRead(2));}"},
            "esp32": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Buton","pin":"GPIO 4/GND"}],"kod":"void setup(){pinMode(4,INPUT_PULLUP);pinMode(2,OUTPUT);}\nvoid loop(){digitalWrite(2,!digitalRead(4));}"},
            "esp8266": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Buton","pin":"D2/GND"}],"kod":"void setup(){pinMode(D2,INPUT_PULLUP);pinMode(D4,OUTPUT);}\nvoid loop(){digitalWrite(D4,digitalRead(D2));}"}
        }
    },
    "role-220v-kontrol": {
        "kategori": "Motor & Güç",
        "baslik": "5V Tek Kanal Röle ile Yüksek Güç Kontrolü",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "5V Röle Modülü", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Röle IN", "pin": "D7"}, {"bilesen": "Besleme", "pin": "5V / GND"}],
                "kod": """/* ArduKod - Röle Sürücü (Uno) */
void setup() { pinMode(7, OUTPUT); }
void loop() {
  digitalWrite(7, LOW); delay(2000);
  digitalWrite(7, HIGH); delay(2000);
}"""
            },
            "nano": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"IN","pin":"D7"}],"kod":"void setup(){pinMode(7,OUTPUT);}\nvoid loop(){digitalWrite(7,LOW);delay(2000);digitalWrite(7,HIGH);delay(2000);}"},
            "esp32": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"IN","pin":"GPIO 19"}],"kod":"void setup(){pinMode(19,OUTPUT);}\nvoid loop(){digitalWrite(19,LOW);delay(2000);digitalWrite(19,HIGH);delay(2000);}"},
            "esp8266": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"IN","pin":"D1"}],"kod":"void setup(){pinMode(D1,OUTPUT);}\nvoid loop(){digitalWrite(D1,LOW);delay(2000);digitalWrite(D1,HIGH);delay(2000);}"}
        }
    },
    "sg90-servo-motor": {
        "kategori": "Motor & Güç",
        "baslik": "SG90 Mikro Servo Motor 0-180 Derece Açı Kontrolü",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "SG90 Servo Motor", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<Servo.h>",
                "baglanti": [{"bilesen": "Sinyal (Turuncu)", "pin": "D9"}],
                "kod": """#include <Servo.h>
Servo s;
void setup() { s.attach(9); }
void loop() {
  s.write(0); delay(1000);
  s.write(90); delay(1000);
  s.write(180); delay(1000);
}"""
            },
            "nano": {"kutuphaneler":"<Servo.h>","baglanti":[{"bilesen":"Sinyal","pin":"D9"}],"kod":"#include <Servo.h>\nServo s;\nvoid setup(){s.attach(9);}\nvoid loop(){s.write(0);delay(1000);s.write(180);delay(1000);}"},
            "esp32": {"kutuphaneler":"<ESP32Servo.h>","baglanti":[{"bilesen":"Sinyal","pin":"GPIO 18"}],"kod":"#include <ESP32Servo.h>\nServo s;\nvoid setup(){s.attach(18);}\nvoid loop(){s.write(0);delay(1000);s.write(180);delay(1000);}"},
            "esp8266": {"kutuphaneler":"<Servo.h>","baglanti":[{"bilesen":"Sinyal","pin":"D4"}],"kod":"#include <Servo.h>\nServo s;\nvoid setup(){s.attach(D4);}\nvoid loop(){s.write(0);delay(1000);s.write(180);delay(1000);}"}
        }
    },
    "i2c-1602-lcd": {
        "kategori": "Ekranlar",
        "baslik": "I2C 1602 Karakter LCD Ekran Metin Yazdırma",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "1602 LCD + I2C", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<LiquidCrystal_I2C.h>",
                "baglanti": [{"bilesen": "SDA / SCL", "pin": "A4 / A5"}],
                "kod": """#include <Wire.h>
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0); lcd.print("ArduKod Portal");
  lcd.setCursor(0, 1); lcd.print("1602 I2C Ekran");
}
void loop() {}"""
            },
            "nano": {"kutuphaneler":"<LiquidCrystal_I2C.h>","baglanti":[{"bilesen":"SDA/SCL","pin":"A4/A5"}],"kod":"#include <Wire.h>\n#include <LiquidCrystal_I2C.h>\nLiquidCrystal_I2C lcd(0x27,16,2);\nvoid setup(){lcd.init();lcd.backlight();lcd.print(\"ArduKod Nano\");}\nvoid loop(){}"},
            "esp32": {"kutuphaneler":"<LiquidCrystal_I2C.h>","baglanti":[{"bilesen":"SDA/SCL","pin":"GPIO 21/22"}],"kod":"#include <Wire.h>\n#include <LiquidCrystal_I2C.h>\nLiquidCrystal_I2C lcd(0x27,16,2);\nvoid setup(){Wire.begin(21,22);lcd.init();lcd.backlight();lcd.print(\"ESP32 LCD\");}\nvoid loop(){}"},
            "esp8266": {"kutuphaneler":"<LiquidCrystal_I2C.h>","baglanti":[{"bilesen":"SDA/SCL","pin":"D2/D1"}],"kod":"#include <Wire.h>\n#include <LiquidCrystal_I2C.h>\nLiquidCrystal_I2C lcd(0x27,16,2);\nvoid setup(){Wire.begin(D2,D1);lcd.init();lcd.backlight();lcd.print(\"ESP8266 LCD\");}\nvoid loop(){}"}
        }
    },
    "buzzer-melodi": {
        "kategori": "Ses & Bildirim",
        "baslik": "Pasif Buzzer ile Ton ve Melodi Çalma",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "Pasif Buzzer", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Buzzer (+)", "pin": "D8"}],
                "kod": """void setup() {}
void loop() {
  tone(8, 440, 200); delay(300);
  tone(8, 880, 200); delay(500);
}"""
            },
            "nano": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Buzzer","pin":"D8"}],"kod":"void setup(){}\nvoid loop(){tone(8,440,200);delay(300);tone(8,880,200);delay(500);}"},
            "esp32": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Buzzer","pin":"GPIO 18"}],"kod":"void setup(){ledcAttach(18,2000,8);}\nvoid loop(){ledcWriteTone(18,440);delay(300);ledcWriteTone(18,880);delay(500);}"},
            "esp8266": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Buzzer","pin":"D5"}],"kod":"void setup(){}\nvoid loop(){tone(D5,440,200);delay(300);tone(D5,880,200);delay(500);}"}
        }
    },
    "esp-wifi-web-server": {
        "kategori": "Haberleşme & IoT",
        "baslik": "Wi-Fi Web Server ile Tarayıcıdan Röle/LED Kontrolü",
        "zorluk": "İleri",
        "sure": "20 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "ESP32 veya NodeMCU", "link": ""}],
        "kartlar": {
            "uno": {"kutuphaneler":"Harici modül gerekir.","baglanti":[{"bilesen":"Wi-Fi","pin":"Uno Wi-Fi içermez (ESP seçiniz)"}],"kod":"// Arduino Uno dahili Wi-Fi barındırmaz. Lütfen ESP32 sekmesini seçiniz."},
            "nano": {"kutuphaneler":"Harici modül gerekir.","baglanti":[{"bilesen":"Wi-Fi","pin":"Nano Wi-Fi içermez"}],"kod":"// Arduino Nano dahili Wi-Fi barındırmaz. Lütfen ESP32 sekmesini seçiniz."},
            "esp32": {
                "kutuphaneler": "<WiFi.h>, <WebServer.h>",
                "baglanti": [{"bilesen": "Dahili LED", "pin": "GPIO 2"}],
                "kod": """/* ArduKod - ESP32 Web Server */
#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "WIFI_ADINIZ";
const char* password = "WIFI_SIFRENIZ";
WebServer server(80);

void setup() {
  Serial.begin(115200);
  pinMode(2, OUTPUT);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  Serial.println(WiFi.localIP());

  server.on("/", []() {
    server.send(200, "text/html", "<h2>ESP32 Web Server</h2><a href='/on'>AC</a> | <a href='/off'>KAPAT</a>");
  });
  server.on("/on", []() { digitalWrite(2, HIGH); server.send(200, "text/plain", "ACIK"); });
  server.on("/off", []() { digitalWrite(2, LOW); server.send(200, "text/plain", "KAPALI"); });
  server.begin();
}
void loop() { server.handleClient(); }"""
            },
            "esp8266": {
                "kutuphaneler": "<ESP8266WiFi.h>, <ESP8266WebServer.h>",
                "baglanti": [{"bilesen": "Dahili LED", "pin": "D4"}],
                "kod": """/* ArduKod - NodeMCU Web Server */
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "WIFI_ADINIZ";
const char* password = "WIFI_SIFRENIZ";
ESP8266WebServer server(80);

void setup() {
  Serial.begin(115200);
  pinMode(D4, OUTPUT);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  Serial.println(WiFi.localIP());

  server.on("/", []() {
    server.send(200, "text/html", "<h2>NodeMCU Kontrol</h2><a href='/on'>AC</a> | <a href='/off'>KAPAT</a>");
  });
  server.on("/on", []() { digitalWrite(D4, LOW); server.send(200, "text/plain", "ACIK"); });
  server.on("/off", []() { digitalWrite(D4, HIGH); server.send(200, "text/plain", "KAPALI"); });
  server.begin();
}
void loop() { server.handleClient(); }"""
            }
        }
    }
}

# --- JSON YARDIMCI İŞLEMLERİ (OTOMATİK ONARIMLI) ---
def veri_yukle():
    if not os.path.exists(VERI_DOSYASI):
        with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(VARSAYILAN_PROJELER, f, ensure_ascii=False, indent=2)
        return VARSAYILAN_PROJELER
    try:
        with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
            d = json.load(f)
            # Eksik kalan veya kodu boşalan projeleri otomatik düzelt
            degisti = False
            for k, v in VARSAYILAN_PROJELER.items():
                if k not in d:
                    d[k] = v
                    degisti = True
            if degisti:
                with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
                    json.dump(d, f, ensure_ascii=False, indent=2)
            return d
    except:
        return VARSAYILAN_PROJELER

def veri_kaydet(veri):
    with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

# ==============================================================================
# SIFIR GECİKMELİ & MOBİLDE KOD ALANINA KAYAN ÖN YÜZ
# ==============================================================================
ANA_SAYFA_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
            padding: 0 15px;
            flex-shrink: 0;
            z-index: 100;
        }
        .brand { font-size: 18px; font-weight: bold; color: var(--primary); cursor: pointer; }
        .nav-actions { display: flex; align-items: center; gap: 6px; }
        .hub-btn {
            background-color: rgba(0, 151, 157, 0.15);
            color: var(--primary-hover);
            border: 1px solid var(--primary);
            padding: 6px 10px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            text-decoration: none;
        }
        .main-container { flex: 1; position: relative; overflow: hidden; }
        .view-section { position: absolute; top: 0; left: 0; right: 0; bottom: 0; overflow-y: auto; display: none; }
        .view-section.active { display: block; }

        /* HUB */
        .hub-wrapper { max-width: 960px; margin: 30px auto; padding: 0 15px; text-align: center; }
        .hub-title { font-size: 26px; margin-bottom: 6px; }
        .hub-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-top: 25px; }
        .hub-card { background-color: var(--panel-bg); border: 1px solid var(--border); border-radius: 10px; padding: 20px; cursor: pointer; text-align: left; }
        .hub-card:hover { border-color: var(--primary); transform: translateY(-3px); }

        /* ARAÇLAR */
        .tools-wrapper { max-width: 860px; margin: 25px auto; padding: 0 15px; }
        .tool-card { background-color: var(--panel-bg); border: 1px solid var(--border); border-radius: 10px; padding: 20px; margin-bottom: 20px; }
        .tool-title { font-size: 17px; font-weight: bold; margin-bottom: 14px; color: var(--primary); }
        .resistor-display { background: #2a2015; height: 44px; max-width: 300px; margin: 15px auto; border-radius: 8px; display: flex; align-items: center; justify-content: space-around; padding: 0 20px; border: 2px solid #5a4632; }
        .resistor-band { width: 14px; height: 100%; border-radius: 2px; }
        .band-selectors { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; }
        select, input[type="text"] { width: 100%; padding: 8px; background-color: var(--bg-color); border: 1px solid var(--border); color: #fff; border-radius: 6px; outline: none; font-size: 13px; }
        .result-box { margin-top: 15px; background-color: rgba(0, 151, 157, 0.1); border: 1px solid var(--primary); border-radius: 8px; padding: 12px; text-align: center; font-size: 18px; font-weight: bold; color: var(--accent-green); }

        /* WORKSPACE & MOBİL DUYARLILIK */
        .workspace-view { display: flex; height: 100%; overflow: hidden; }
        .sidebar { width: 300px; background-color: var(--panel-bg); border-right: 1px solid var(--border); display: flex; flex-direction: column; flex-shrink: 0; }
        .search-area { padding: 10px 14px; border-bottom: 1px solid var(--border); }
        .project-list { flex: 1; overflow-y: auto; padding: 10px; }
        .category-group { margin-bottom: 12px; }
        .category-title { font-size: 11px; text-transform: uppercase; color: var(--text-sub); font-weight: bold; margin-bottom: 5px; }
        .project-item { padding: 8px 10px; border-radius: 6px; color: var(--text-main); cursor: pointer; font-size: 13px; margin-bottom: 3px; line-height: 1.3; }
        .project-item:hover { background-color: rgba(0, 151, 157, 0.15); }
        .project-item.active { background-color: var(--primary); color: #fff; font-weight: bold; }

        .content { flex: 1; padding: 20px 25px; overflow-y: auto; width: 100%; }
        .project-title { font-size: 22px; margin: 0 0 8px 0; }
        .materials-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px; margin-bottom: 18px; }
        .material-item { background: var(--panel-bg); border: 1px solid var(--border); border-radius: 6px; padding: 8px 10px; display: flex; align-items: center; justify-content: space-between; font-size: 12.5px; }
        .material-qty { background: rgba(0, 151, 157, 0.2); color: var(--primary-hover); font-weight: bold; padding: 2px 5px; border-radius: 4px; margin-right: 5px; }
        .btn-buy { background-color: rgba(63, 185, 80, 0.15); color: var(--accent-green); border: 1px solid var(--accent-green); padding: 3px 6px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: bold; }

        .card-tabs { display: flex; gap: 6px; border-bottom: 1px solid var(--border); padding-bottom: 8px; margin: 12px 0; overflow-x: auto; }
        .card-btn { background-color: var(--panel-bg); border: 1px solid var(--border); color: var(--text-sub); padding: 7px 14px; border-radius: 6px; cursor: pointer; font-size: 12.5px; font-weight: bold; white-space: nowrap; }
        .card-btn.active { background-color: var(--primary); border-color: var(--primary); color: white; }

        table { width: 100%; border-collapse: collapse; background-color: var(--panel-bg); border-radius: 8px; border: 1px solid var(--border); margin-bottom: 15px; }
        th, td { padding: 9px 12px; text-align: left; border-bottom: 1px solid var(--border); font-size: 13px; }
        th { background-color: rgba(255, 255, 255, 0.03); color: var(--text-sub); }
        td.pin-cell { color: var(--accent-green); font-family: monospace; font-weight: bold; }

        .code-container { position: relative; margin-top: 8px; }
        .code-actions { position: absolute; top: 8px; right: 8px; display: flex; gap: 6px; z-index: 10; }
        .btn-action { background-color: #21262d; border: 1px solid var(--border); color: var(--text-sub); padding: 5px 10px; font-size: 11.5px; border-radius: 4px; cursor: pointer; }

        @media (max-width: 768px) {
            .workspace-view { flex-direction: column; overflow-y: auto; }
            .sidebar { width: 100%; height: auto; max-height: 180px; flex-shrink: 0; }
            .content { padding: 15px 12px; }
            .project-title { font-size: 18px; }
        }
    </style>
</head>
<body>

<div class="topbar">
    <div class="brand" onclick="ekranDegistir('hub')">⚡ ArduKod</div>
    <div class="nav-actions">
        <button class="hub-btn" onclick="ekranDegistir('tools')">🛠️ Araçlar</button>
        <button class="hub-btn" onclick="ekranDegistir('hub')">🎛️ Kartlar</button>
        <a href="/admin" class="hub-btn" style="color:var(--accent-blue); border-color:var(--accent-blue);">🔐 Admin</a>
    </div>
</div>

<div class="main-container">

    <!-- 1. HUB -->
    <div id="hubView" class="view-section active">
        <div class="hub-wrapper">
            <h1 class="hub-title">Geliştirici & Maker Merkezi</h1>
            <div style="color:var(--text-sub);font-size:14px;">Platformunuzu veya atölye hesaplama aracını seçin</div>
            <div class="hub-grid">
                <div class="hub-card" onclick="kartaGit('uno')"><h3>🔵 Arduino Uno</h3><p style="color:var(--text-sub);font-size:12.5px;">5V lojik ve başlangıç seviyesi devreler.</p></div>
                <div class="hub-card" onclick="kartaGit('nano')"><h3>🔷 Arduino Nano</h3><p style="color:var(--text-sub);font-size:12.5px;">Breadboard uyumlu kompakt prototipler.</p></div>
                <div class="hub-card" onclick="kartaGit('esp32')"><h3>⚡ ESP32 (3.3V)</h3><p style="color:var(--text-sub);font-size:12.5px;">Wi-Fi, Bluetooth ve IoT pin mimarisi.</p></div>
                <div class="hub-card" onclick="kartaGit('esp8266')"><h3>📶 ESP8266 NodeMCU</h3><p style="color:var(--text-sub);font-size:12.5px;">Ekonomik kablosuz sensör projeleri.</p></div>
                <div class="hub-card" onclick="ekranDegistir('tools')"><h3>🛠️ Atölye Araçları</h3><p style="color:var(--text-sub);font-size:12.5px;">DIP, SMD ve kondansatör kod çözücüler.</p></div>
            </div>
        </div>
    </div>

    <!-- 2. ATÖLYE ARAÇLARI -->
    <div id="toolsView" class="view-section">
        <div class="tools-wrapper">
            <div class="tool-card">
                <div class="tool-title">🎨 DIP Direnç Renk Kodu Hesaplayıcı</div>
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
                            <option value="1" data-color="#a52a2a" selected>Kahve (1)</option>
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
                            <option value="1" data-color="#a52a2a">Kahve (1)</option>
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
                <div class="tool-title">🔍 SMD Direnç Kodu Çözücü</div>
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

    <!-- 3. WORKSPACE -->
    <div id="workspaceView" class="view-section">
        <div class="workspace-view">
            <div class="sidebar">
                <div class="search-area">
                    <input type="text" id="searchInput" placeholder="Devre veya sensör ara..." style="width:100%;padding:8px;background:var(--bg-color);border:1px solid var(--border);color:#fff;border-radius:6px;outline:none;">
                </div>
                <div id="projectList" class="project-list"></div>
            </div>

            <div class="content" id="contentArea">
                <h1 id="pBaslik" class="project-title"></h1>
                <div style="margin-bottom:12px; color:var(--text-sub); font-size:12.5px;" id="pMeta"></div>

                <div style="font-weight:bold; color:var(--primary); margin-bottom:8px; font-size:13.5px;">📦 Gereken Malzemeler</div>
                <div class="materials-grid" id="pMalzemeler"></div>

                <div class="card-tabs">
                    <button class="card-btn active" id="tab-uno" onclick="kartSec('uno')">🔵 Uno</button>
                    <button class="card-btn" id="tab-nano" onclick="kartSec('nano')">🔷 Nano</button>
                    <button class="card-btn" id="tab-esp32" onclick="kartSec('esp32')">⚡ ESP32</button>
                    <button class="card-btn" id="tab-esp8266" onclick="kartSec('esp8266')">📶 ESP8266</button>
                </div>

                <div style="font-weight:bold; color:var(--primary); margin:14px 0 6px 0; font-size:13.5px;">🔌 Pin Bağlantı Tablosu</div>
                <table>
                    <thead><tr><th>Bileşen / Pin</th><th>Kart Bağlantısı</th></tr></thead>
                    <tbody id="pTablo"></tbody>
                </table>

                <div style="font-weight:bold; color:var(--primary); margin:16px 0 4px 0; font-size:13.5px;">📚 Kütüphaneler</div>
                <p id="pKutuphane" style="color:var(--text-sub); margin:0; font-size:13px;"></p>

                <div style="font-weight:bold; color:var(--primary); margin:16px 0 6px 0; font-size:13.5px;">💻 C++ Kaynak Kodu</div>
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
        if (ilkId) projeSec(ilkId, false);
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
                item.onclick = () => projeSec(p.id, true);
                grupDiv.appendChild(item);
            });
            listDiv.appendChild(grupDiv);
        }
    }

    function projeSec(id, kaydir = false) {
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

        // MOBİL DÜZELTMESİ: Telefondan tıklandığında sayfayı koda kaydırır
        if (kaydir && window.innerWidth <= 768) {
            document.getElementById('contentArea').scrollIntoView({ behavior: 'smooth' });
        }
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

    // DİRENÇ VE KONDANSATÖR FONKSİYONLARI
    function dipHesapla() {
        const b1 = document.getElementById('dip-b1'), b2 = document.getElementById('dip-b2'), b3 = document.getElementById('dip-b3'), b4 = document.getElementById('dip-b4');
        document.getElementById('band1-view').style.background = b1.options[b1.selectedIndex].dataset.color;
        document.getElementById('band2-view').style.background = b2.options[b2.selectedIndex].dataset.color;
        document.getElementById('band3-view').style.background = b3.options[b3.selectedIndex].dataset.color;
        document.getElementById('band4-view').style.background = b4.options[b4.selectedIndex].dataset.color;

        const val = parseFloat(((parseInt(b1.value) * 10 + parseInt(b2.value)) * parseFloat(b3.value)).toFixed(2));
        if (val === 0) { document.getElementById('dipSonuc').innerText = '0 Ω (Jumper)'; return; }

        let f = val + ' Ω';
        if (val >= 1000000) f = (val / 1000000).toFixed(val % 1000000 === 0 ? 0 : 2) + ' MΩ';
        else if (val >= 1000) f = (val / 1000).toFixed(val % 1000 === 0 ? 0 : 1) + ' kΩ';
        document.getElementById('dipSonuc').innerText = `${f} ${b4.value}`;
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
        out.innerText = 'Geçersiz Kod';
    }

    function capHesapla() {
        let raw = (document.getElementById('capInput').value.trim() || "104").toUpperCase();
        const out = document.getElementById('capSonuc');
        let tol = "";
        const tMap = {'J':'±%5', 'K':'±%10', 'M':'±%20'};
        if (tMap[raw.slice(-1)]) { tol = ` [${tMap[raw.slice(-1)]}]`; raw = raw.slice(0, -1); }
        if (/^\d{3}$/.test(raw)) {
            let pf = parseInt(raw.substring(0, 2)) * Math.pow(10, parseInt(raw[2]));
            out.innerText = `${pf/1000} nF (${pf/1000000} µF / ${pf.toLocaleString()} pF)${tol}`; return;
        }
        out.innerText = 'Geçersiz Kod';
    }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(ANA_SAYFA_HTML, projeler_json=json.dumps(veri_yukle()))

# ==============================================================================
# TAM YETKİLİ ADMİN PANELİ (EKLE, SİL, DÜZENLE, LİNK YÖNETİMİ, İSTATİSTİK)
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
<!DOCTYPE html><html><head><meta charset="utf-8"><title>ArduKod Tam Yönetim</title>
<style>
body{background:#0d1117;color:#fff;font-family:sans-serif;padding:20px;margin:0;}
.top{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #30363d;padding-bottom:15px;}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:15px;margin:20px 0;}
.card{background:#161b22;border:1px solid #30363d;padding:15px;border-radius:8px;}
.num{font-size:22px;font-weight:bold;color:#00979d;margin-top:5px;}
table{width:100%;border-collapse:collapse;margin-top:15px;background:#161b22;border-radius:8px;}
th,td{padding:10px 12px;border-bottom:1px solid #30363d;text-align:left;font-size:13.5px;}th{background:#21262d;}
.btn{padding:6px 12px;border-radius:4px;cursor:pointer;border:none;font-weight:bold;text-decoration:none;font-size:12px;}
.btn-green{background:#238636;color:#fff;}.btn-blue{background:#1f6feb;color:#fff;}.btn-red{background:#da3633;color:#fff;}
.modal{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);align-items:center;justify-content:center;padding:20px;z-index:1000;}
.modal-content{background:#161b22;border:1px solid #30363d;padding:20px;border-radius:8px;width:750px;max-height:90vh;overflow-y:auto;}
input,select,textarea{width:100%;box-sizing:border-box;padding:8px;background:#0d1117;border:1px solid #30363d;color:#fff;border-radius:4px;margin-bottom:10px;font-family:inherit;}
</style></head>
<body>
<div class="top">
  <h2>⚡ ArduKod İçerik, Kod & Link Yönetimi</h2>
  <div>
    <button class="btn btn-green" onclick="yeniProjeModal()">+ Yeni Proje Ekle</button>
    <a href="/" target="_blank" class="btn btn-blue">🌐 Siteye Git</a>
    <a href="/admin/cikis" class="btn btn-red">Çıkış</a>
  </div>
</div>

<div class="stats">
  <div class="card">Toplam Proje: <div class="num">{{ projeler|length }}</div></div>
</div>

<h3>📦 Proje & Malzeme Linki Yönetimi</h3>
<table>
  <thead><tr><th>ID</th><th>Başlık</th><th>Kategori</th><th>İşlemler</th></tr></thead>
  <tbody>
    {% for pid, p in projeler.items() %}
    <tr>
      <td><code>{{ pid }}</code></td>
      <td><b>{{ p.baslik }}</b></td>
      <td>{{ p.kategori }}</td>
      <td>
        <button class="btn btn-blue" onclick='duzenleModal({{ pid|tojson }}, {{ p|tojson }})'>Düzenle / Kod / Link</button>
        <button class="btn btn-red" onclick="sil('{{ pid }}')">Sil</button>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<!-- PROJE MODAL -->
<div id="pModal" class="modal">
  <div class="modal-content">
    <h3 id="mTitle">Proje Yönetimi</h3>
    <label>Proje ID (Benzersiz):</label><input type="text" id="f_id">
    <label>Başlık:</label><input type="text" id="f_baslik">
    <div style="display:flex;gap:10px;">
      <div style="flex:1;"><label>Kategori:</label><input type="text" id="f_kategori"></div>
      <div style="flex:1;"><label>Zorluk:</label><input type="text" id="f_zorluk"></div>
      <div style="flex:1;"><label>Süre:</label><input type="text" id="f_sure"></div>
    </div>
    <h4>🔗 Malzemeler & Satın Alma Linkleri</h4>
    <div id="malzemeListesi"></div>
    <button type="button" class="btn btn-blue" onclick="malzemeSatiriEkle()" style="margin-bottom:15px;">+ Malzeme Ekle</button>
    <h4>💻 4 Kartın C++ Kodları</h4>
    <label>Arduino Uno Kodu:</label><textarea id="f_kod_uno" rows="5"></textarea>
    <label>Arduino Nano Kodu:</label><textarea id="f_kod_nano" rows="5"></textarea>
    <label>ESP32 Kodu:</label><textarea id="f_kod_esp32" rows="5"></textarea>
    <label>ESP8266 Kodu:</label><textarea id="f_kod_esp8266" rows="5"></textarea>
    <div style="text-align:right;margin-top:15px;">
      <button class="btn" style="background:#30363d;color:#fff;" onclick="modalKapat()">Kapat</button>
      <button class="btn btn-green" onclick="kaydet()">Kaydet & Yayınla</button>
    </div>
  </div>
</div>

<script>
let aktifProjeData = null;
function yeniProjeModal() {
  aktifProjeData = null;
  document.getElementById('mTitle').innerText = "Yeni Proje Ekle";
  document.getElementById('f_id').value = "";
  document.getElementById('f_id').disabled = false;
  document.getElementById('f_baslik').value = "";
  document.getElementById('f_kategori').value = "Sensörler";
  document.getElementById('f_zorluk').value = "Başlangıç";
  document.getElementById('f_sure').value = "10 Dk";
  document.getElementById('f_kod_uno').value = "";
  document.getElementById('f_kod_nano').value = "";
  document.getElementById('f_kod_esp32').value = "";
  document.getElementById('f_kod_esp8266').value = "";
  document.getElementById('malzemeListesi').innerHTML = "";
  malzemeSatiriEkle("1x", "Yeni Malzeme", "https://...");
  document.getElementById('pModal').style.display = 'flex';
}

function duzenleModal(pid, p) {
  aktifProjeData = p;
  document.getElementById('mTitle').innerText = "Düzenle: " + p.baslik;
  document.getElementById('f_id').value = pid;
  document.getElementById('f_id').disabled = true;
  document.getElementById('f_baslik').value = p.baslik || "";
  document.getElementById('f_kategori').value = p.kategori || "";
  document.getElementById('f_zorluk').value = p.zorluk || "Başlangıç";
  document.getElementById('f_sure').value = p.sure || "10 Dk";
  const k = p.kartlar || {};
  document.getElementById('f_kod_uno').value = (k.uno && k.uno.kod) ? k.uno.kod : "";
  document.getElementById('f_kod_nano').value = (k.nano && k.nano.kod) ? k.nano.kod : "";
  document.getElementById('f_kod_esp32').value = (k.esp32 && k.esp32.kod) ? k.esp32.kod : "";
  document.getElementById('f_kod_esp8266').value = (k.esp8266 && k.esp8266.kod) ? k.esp8266.kod : "";
  const box = document.getElementById('malzemeListesi');
  box.innerHTML = "";
  (p.malzemeler || []).forEach(m => malzemeSatiriEkle(m.adet, m.isim, m.link || ""));
  document.getElementById('pModal').style.display = 'flex';
}

function modalKapat() { document.getElementById('pModal').style.display = 'none'; }

function malzemeSatiriEkle(adet="1x", isim="", link="") {
  const d = document.createElement('div');
  d.style.display = "flex"; d.style.gap = "8px"; d.style.marginBottom = "6px";
  d.innerHTML = `
    <input type="text" value="${adet}" placeholder="Adet" style="width:70px;margin:0;" class="m_adet">
    <input type="text" value="${isim}" placeholder="Malzeme Adı" style="flex:1;margin:0;" class="m_isim">
    <input type="text" value="${link}" placeholder="Satın Alma / Ürün Linki" style="flex:1.5;margin:0;" class="m_link">
    <button type="button" class="btn btn-red" onclick="this.parentElement.remove()">X</button>
  `;
  document.getElementById('malzemeListesi').appendChild(d);
}

async function kaydet() {
  const pid = document.getElementById('f_id').value.trim();
  if(!pid) return alert('Proje ID gereklidir!');
  const malzemeler = [];
  document.querySelectorAll('#malzemeListesi > div').forEach(el => {
    const adet = el.querySelector('.m_adet').value.trim();
    const isim = el.querySelector('.m_isim').value.trim();
    const link = el.querySelector('.m_link').value.trim();
    if(isim) malzemeler.push({ adet, isim, link });
  });

  const kartlar = (aktifProjeData && aktifProjeData.kartlar) ? aktifProjeData.kartlar : {
    uno: { baglanti: [{"bilesen":"VCC/GND","pin":"5V/GND"}] },
    nano: { baglanti: [{"bilesen":"VCC/GND","pin":"5V/GND"}] },
    esp32: { baglanti: [{"bilesen":"VCC/GND","pin":"3.3V/GND"}] },
    esp8266: { baglanti: [{"bilesen":"VCC/GND","pin":"3.3V/GND"}] }
  };
  kartlar.uno.kod = document.getElementById('f_kod_uno').value;
  kartlar.nano.kod = document.getElementById('f_kod_nano').value;
  kartlar.esp32.kod = document.getElementById('f_kod_esp32').value;
  kartlar.esp8266.kod = document.getElementById('f_kod_esp8266').value;

  const paket = {
    id: pid,
    baslik: document.getElementById('f_baslik').value,
    kategori: document.getElementById('f_kategori').value,
    zorluk: document.getElementById('f_zorluk').value,
    sure: document.getElementById('f_sure').value,
    malzemeler: malzemeler,
    kartlar: kartlar
  };

  const res = await fetch('/admin/proje-kaydet', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(paket)
  });
  if((await res.json()).durum === 'basarili') { alert('Başarıyla Kaydedildi!'); location.reload(); }
}

async function sil(pid) {
  if(!confirm(pid + ' projesini silmek istediğinize emin misiniz?')) return;
  await fetch('/admin/proje-sil/' + pid, { method: 'POST' });
  location.reload();
}
</script>
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
    return render_template_string(ADMIN_PANEL_HTML, projeler=veri_yukle())

@app.route('/admin/proje-kaydet', methods=['POST'])
def admin_proje_kaydet():
    if not session.get("admin"): return jsonify({"durum": "yetkisiz"}), 403
    d = request.get_json() or {}
    pid = d.get("id")
    projeler = veri_yukle()
    mevcut = projeler.get(pid, {"goruntulenme": 0, "indirme": 0})
    mevcut["baslik"] = d.get("baslik")
    mevcut["kategori"] = d.get("kategori")
    mevcut["zorluk"] = d.get("zorluk")
    mevcut["sure"] = d.get("sure")
    mevcut["malzemeler"] = d.get("malzemeler", [])
    mevcut["kartlar"] = d.get("kartlar", {})
    projeler[pid] = mevcut
    veri_kaydet(projeler)
    return jsonify({"durum": "basarili"})

@app.route('/admin/proje-sil/<id>', methods=['POST'])
def admin_proje_sil(id):
    if not session.get("admin"): return jsonify({"durum": "yetkisiz"}), 403
    projeler = veri_yukle()
    if id in projeler:
        del projeler[id]
        veri_kaydet(projeler)
    return jsonify({"durum": "basarili"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
