import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = "ardukod_muhendislik_portal_key_2026_xyz"
ADMIN_SIFRE = "admin123"

VERI_DOSYASI = "projeler.json"
ISTEK_DOSYASI = "istekler.json"

# ==============================================================================
# TAM DETAYLI, SANAYİ STANDARTLARINDA ÇALIŞAN C++ KODLARI & PİN TABLOLARI
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
            {"adet": "5x", "isim": "220Ω / 330Ω 1/4W Karbon Direnç", "link": "https://www.direnc.net"},
            {"adet": "1x", "isim": "830 Nokta Breadboard", "link": "https://www.direnc.net"},
            {"adet": "6x", "isim": "Erkek-Erkek Jumper Kablo", "link": "https://www.direnc.net"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez (Standart AVR Çekirdeği).",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω Seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "GND (Ortak Toprak Hattı)"}
                ],
                "kod": """/*
 * ArduKod - 5 LED Kara Simsek (Knight Rider)
 * Platform: Arduino Uno (ATmega328P - 5V)
 */

const int ledPinleri[] = {2, 3, 4, 5, 6};
const int ledSayisi = 5;
const unsigned long beklemeSuresi = 60; // ms cinsinden akis hizi

void setup() {
  Serial.begin(9600);
  Serial.println(F("[SISTEM] Kara Simsek baslatiliyor..."));
  
  for (int i = 0; i < ledSayisi; i++) {
    pinMode(ledPinleri[i], OUTPUT);
    digitalWrite(ledPinleri[i], LOW);
  }
}

void loop() {
  // Soldan Saga Kayma
  for (int i = 0; i < ledSayisi; i++) {
    digitalWrite(ledPinleri[i], HIGH);
    delay(beklemeSuresi);
    digitalWrite(ledPinleri[i], LOW);
  }

  // Sagdan Sola Geri Donus
  for (int i = ledSayisi - 2; i > 0; i--) {
    digitalWrite(ledPinleri[i], HIGH);
    delay(beklemeSuresi);
    digitalWrite(ledPinleri[i], LOW);
  }
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω Seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "Nano GND"}
                ],
                "kod": """/*
 * ArduKod - 5 LED Kara Simsek
 * Platform: Arduino Nano (ATmega328P - 5V)
 */

const uint8_t pinler[] = {2, 3, 4, 5, 6};
const uint8_t toplam = 5;

void setup() {
  for (uint8_t i = 0; i < toplam; i++) {
    pinMode(pinler[i], OUTPUT);
    digitalWrite(pinler[i], LOW);
  }
}

void loop() {
  for (uint8_t i = 0; i < toplam; i++) {
    digitalWrite(pinler[i], HIGH);
    delay(50);
    digitalWrite(pinler[i], LOW);
  }
  for (int8_t i = toplam - 2; i > 0; i--) {
    digitalWrite(pinler[i], HIGH);
    delay(50);
    digitalWrite(pinler[i], LOW);
  }
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez (ESP32 Core).",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "GPIO 18, 19, 21, 22, 23 (330Ω Seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "ESP32 GND"}
                ],
                "kod": """/*
 * ArduKod - ESP32 5 LED Kara Simsek
 * Platform: ESP32 DevKit V1 (3.3V Lojik)
 * Not: 3.3V akim siniri nedeniyle 330 ohm direnc onerilir.
 */

const int ledler[] = {18, 19, 21, 22, 23};
const int adet = 5;

void setup() {
  Serial.begin(115200);
  Serial.println("[ESP32] Kara Simsek Baslatildi.");
  for (int i = 0; i < adet; i++) {
    pinMode(ledler[i], OUTPUT);
    digitalWrite(ledler[i], LOW);
  }
}

void loop() {
  for (int i = 0; i < adet; i++) {
    digitalWrite(ledler[i], HIGH);
    vTaskDelay(pdMS_TO_TICKS(50)); // FreeRTOS uyumlu gecikme
    digitalWrite(ledler[i], LOW);
  }
  for (int i = adet - 2; i > 0; i--) {
    digitalWrite(ledler[i], HIGH);
    vTaskDelay(pdMS_TO_TICKS(50));
    digitalWrite(ledler[i], LOW);
  }
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D1, D2, D5, D6, D7 (GPIO 5, 4, 14, 12, 13)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "NodeMCU GND"}
                ],
                "kod": """/*
 * ArduKod - ESP8266 NodeMCU Kara Simsek
 * Platform: ESP8266 ESP-12E (NodeMCU V2/V3)
 */

const uint8_t leds[] = {D1, D2, D5, D6, D7};
const uint8_t sayi = 5;

void setup() {
  for (uint8_t i = 0; i < sayi; i++) {
    pinMode(leds[i], OUTPUT);
    digitalWrite(leds[i], LOW);
  }
}

void loop() {
  for (uint8_t i = 0; i < sayi; i++) {
    digitalWrite(leds[i], HIGH);
    delay(50);
    digitalWrite(leds[i], LOW);
  }
  for (int8_t i = sayi - 2; i > 0; i--) {
    digitalWrite(leds[i], HIGH);
    delay(50);
    digitalWrite(leds[i], LOW);
  }
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
        "malzemeler": [
            {"adet": "1x", "isim": "HC-SR04 Ultrasonik Mesafe Sensörü", "link": "https://www.direnc.net"},
            {"adet": "1x", "isim": "5V Aktif Buzzer", "link": "https://www.direnc.net"},
            {"adet": "1x", "isim": "Breadboard & Bağlantı Telleri", "link": ""},
            {"adet": "2x", "isim": "1kΩ & 2kΩ Direnç (ESP Gerilim Bölücü)", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "HC-SR04 Trig / Echo", "pin": "D9 (Çıkış) / D10 (Giriş)"},
                    {"bilesen": "Aktif Buzzer (+)", "pin": "D8 (220Ω seri)"}
                ],
                "kod": """/*
 * ArduKod - HC-SR04 Hassas Mesafe & Park Radarı
 * Platform: Arduino Uno (ATmega328P)
 */

const int trigPin = 9;
const int echoPin = 10;
const int buzzerPin = 8;

void setup() {
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  Serial.println(F("[RADAR] Ultrasonik sensor hazir."));
}

long mesafeOlc() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // 30ms zamanasimi (~5 metre siniri)
  long sure = pulseIn(echoPin, HIGH, 30000);
  if (sure == 0) return -1; // Yanki alinamadi
  return (sure * 0.0343) / 2;
}

void loop() {
  long mesafe = mesafeOlc();

  if (mesafe > 0 && mesafe <= 50) {
    Serial.print(F("Mesafe: ")); Serial.print(mesafe); Serial.println(F(" cm"));
    
    // Mesafeye bagli dinamik bip araligi (Park sensoru mantigi)
    int bipAraligi = map(mesafe, 3, 50, 40, 400);
    digitalWrite(buzzerPin, HIGH);
    delay(30);
    digitalWrite(buzzerPin, LOW);
    delay(bipAraligi);
  } else {
    digitalWrite(buzzerPin, LOW);
    delay(100);
  }
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "Trig / Echo", "pin": "D9 / D10"},
                    {"bilesen": "Buzzer (+)", "pin": "D8"}
                ],
                "kod": """// Arduino Nano - HC-SR04 Radar Kodu
const int trig = 9, echo = 10, buzz = 8;
void setup() {
  pinMode(trig, OUTPUT); pinMode(echo, INPUT); pinMode(buzz, OUTPUT);
}
void loop() {
  digitalWrite(trig, LOW); delayMicroseconds(2);
  digitalWrite(trig, HIGH); delayMicroseconds(10);
  digitalWrite(trig, LOW);
  long s = pulseIn(echo, HIGH, 25000);
  int d = (s * 0.0343) / 2;
  if (d > 0 && d < 30) {
    digitalWrite(buzz, HIGH); delay(30);
    digitalWrite(buzz, LOW); delay(map(d, 3, 30, 30, 250));
  } else delay(60);
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "VIN (5V) / GND"},
                    {"bilesen": "HC-SR04 Trig", "pin": "GPIO 5"},
                    {"bilesen": "HC-SR04 Echo", "pin": "GPIO 18 (1k/2k Gerilim Bölücü ile 3.3V)"},
                    {"bilesen": "Buzzer (+)", "pin": "GPIO 19"}
                ],
                "kod": """/*
 * ArduKod - ESP32 3.3V Guvenli Park Sensoru
 * ONEMLI: HC-SR04 Echo pini 5V verir!
 * GPIO 18'e baglamadan once 1k ve 2k direnclerle 3.3V seviyesine bolunuz.
 */

const int trigPin = 5;
const int echoPin = 18;
const int buzzPin = 19;

void setup() {
  Serial.begin(115200);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzPin, OUTPUT);
}

void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long sure = pulseIn(echoPin, HIGH, 30000);
  int cm = (sure * 0.0343) / 2;

  if (cm > 0 && cm < 40) {
    digitalWrite(buzzPin, HIGH);
    vTaskDelay(pdMS_TO_TICKS(30));
    digitalWrite(buzzPin, LOW);
    vTaskDelay(pdMS_TO_TICKS(map(cm, 3, 40, 30, 300)));
  } else {
    vTaskDelay(pdMS_TO_TICKS(100));
  }
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "VV (5V) / GND"},
                    {"bilesen": "Trig / Echo", "pin": "D1 (GPIO 5) / D2 (GPIO 4 - Bölücülü)"},
                    {"bilesen": "Buzzer (+)", "pin": "D5 (GPIO 14)"}
                ],
                "kod": """// ESP8266 NodeMCU - Mesafe Sensoru
const int trig = D1, echo = D2, buzz = D5;
void setup() {
  pinMode(trig, OUTPUT); pinMode(echo, INPUT); pinMode(buzz, OUTPUT);
}
void loop() {
  digitalWrite(trig, LOW); delayMicroseconds(2);
  digitalWrite(trig, HIGH); delayMicroseconds(10);
  digitalWrite(trig, LOW);
  long s = pulseIn(echo, HIGH, 30000);
  int cm = (s * 0.0343) / 2;
  if (cm > 0 && cm < 35) {
    digitalWrite(buzz, HIGH); delay(30);
    digitalWrite(buzz, LOW); delay(map(cm, 3, 35, 40, 300));
  } else delay(100);
}"""
            }
        }
    },
    "esp-wifi-web-server": {
        "kategori": "Haberleşme & IoT",
        "baslik": "Wi-Fi Web Server ile Tarayıcıdan Röle/LED Kontrolü",
        "zorluk": "İleri",
        "sure": "20 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [
            {"adet": "1x", "isim": "ESP32 NodeMCU veya Wemos D1 Mini", "link": "https://www.direnc.net"},
            {"adet": "1x", "isim": "5V / 3.3V Röle veya LED", "link": ""},
            {"adet": "1x", "isim": "Micro-USB Kablo", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici Wi-Fi Shield gerekir.",
                "baglanti": [{"bilesen": "Dahili Wi-Fi", "pin": "ATmega328P çipinde dahili Wi-Fi yoktur. ESP32 seçiniz."}],
                "kod": """// Arduino Uno tek basina kablosuz ag baglantisini desteklemez.
// Lutfen bu proje icin ESP32 veya ESP8266 sekmesine geciniz."""
            },
            "nano": {
                "kutuphaneler": "Harici Wi-Fi Shield gerekir.",
                "baglanti": [{"bilesen": "Dahili Wi-Fi", "pin": "Dahili Wi-Fi bulunmaz."}],
                "kod": """// Arduino Nano tek basina kablosuz ag baglantisini desteklemez.
// Lutfen bu proje icin ESP32 veya ESP8266 sekmesine geciniz."""
            },
            "esp32": {
                "kutuphaneler": "<WiFi.h>, <WebServer.h>",
                "baglanti": [
                    {"bilesen": "Kontrol Edilecek LED / Röle", "pin": "GPIO 2 (Dahili Mavi LED)"},
                    {"bilesen": "Besleme Hattı", "pin": "USB veya 5V VIN"}
                ],
                "kod": """/*
 * ArduKod - ESP32 Asenkron Web Server ile I/O Kontrolü
 * Platform: ESP32 Dev Module
 */

#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "WIFI_ADINIZ";
const char* password = "WIFI_SIFRENIZ";

WebServer server(80);
const int rolePin = 2; // Dahili LED veya Role

const char HTML_SAYFA[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ESP32 IoT Kontrol</title>
  <style>
    body { font-family: sans-serif; background: #121212; color: #fff; text-align: center; padding-top: 50px; }
    .btn { padding: 15px 35px; font-size: 18px; border: none; border-radius: 8px; cursor: pointer; text-decoration: none; margin: 10px; display: inline-block; font-weight: bold; }
    .btn-on { background: #238636; color: white; }
    .btn-off { background: #da3633; color: white; }
  </style>
</head>
<body>
  <h2>⚡ ESP32 Web Kontrol Paneli</h2>
  <p>Cihaz Durumu: <b>AKTIF</b></p>
  <a href="/on" class="btn btn-on">AC (HIGH)</a>
  <a href="/off" class="btn btn-off">KAPAT (LOW)</a>
</body>
</html>
)rawliteral";

void handleRoot() {
  server.send_P(200, "text/html", HTML_SAYFA);
}

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

  Serial.print("[WiFi] Baglaniliyor: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n[WiFi] Baglanti Basarili!");
  Serial.print("Tarayicidan girilecek IP: http://");
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
                "baglanti": [
                    {"bilesen": "Kontrol Edilecek LED / Röle", "pin": "D4 (GPIO 2 - Dahili LED)"}
                ],
                "kod": """/*
 * ArduKod - ESP8266 NodeMCU Web Server
 */

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "WIFI_ADINIZ";
const char* password = "WIFI_SIFRENIZ";

ESP8266WebServer server(80);
const int outPin = D4;

void setup() {
  Serial.begin(115200);
  pinMode(outPin, OUTPUT);
  digitalWrite(outPin, HIGH); // NodeMCU LED ters calisir (HIGH = Kapali)

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }

  Serial.println("\nIP: http://" + WiFi.localIP().toString());

  server.on("/", []() {
    server.send(200, "text/html", "<h2>NodeMCU Kontrol</h2><a href='/on'>AC</a> | <a href='/off'>KAPAT</a>");
  });
  server.on("/on", []() { digitalWrite(outPin, LOW); server.send(200, "text/plain", "ACILDI"); });
  server.on("/off", []() { digitalWrite(outPin, HIGH); server.send(200, "text/plain", "KAPANDI"); });

  server.begin();
}

void loop() {
  server.handleClient();
}"""
            }
        }
    }
}

# --- JSON YARDIMCI METOTLARI ---
def veri_yukle():
    if not os.path.exists(VERI_DOSYASI):
        with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(VARSAYILAN_PROJELER, f, ensure_ascii=False, indent=2)
        return VARSAYILAN_PROJELER
    try:
        with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
            d = json.load(f)
            # Eksik varsayılanları tamamla
            for k, v in VARSAYILAN_PROJELER.items():
                if k not in d:
                    d[k] = v
            return d
    except:
        return VARSAYILAN_PROJELER

def veri_kaydet(veri):
    with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

def istek_yukle():
    if not os.path.exists(ISTEK_DOSYASI): return []
    try:
        with open(ISTEK_DOSYASI, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def istek_kaydet(i):
    with open(ISTEK_DOSYASI, "w", encoding="utf-8") as f: json.dump(i, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

# HIZLANDIRMA: Tüm proje verisini tek seferde döndürür, sayfa anında önbelleğe alır
@app.route('/projeler-tam-veri', methods=['GET'])
def projeleri_tam_getir():
    return jsonify(veri_yukle())

@app.route('/proje/<id>/indir', methods=['POST'])
def indir_say(id):
    p = veri_yukle()
    if id in p:
        p[id]["indirme"] = p[id].get("indirme", 0) + 1
        veri_kaydet(p)
    return jsonify({"durum": "ok"})

@app.route('/istek-gonder', methods=['POST'])
def istek_ekle():
    d = request.get_json() or {}
    mesaj = d.get("mesaj", "").strip()
    iletisim = d.get("iletisim", "").strip()
    if not mesaj: return jsonify({"durum": "hata"}), 400
    istekler = istek_yukle()
    istekler.append({"mesaj": mesaj, "iletisim": iletisim})
    istek_kaydet(istekler)
    return jsonify({"durum": "basarili", "mesaj": "Talebiniz kaydedildi!"})

# ==============================================================================
# GÜVENLİ VE ŞİFRESİ GİZLİ ADMİN PANELİ
# ==============================================================================
ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head><meta charset="UTF-8"><title>Yetkili Girişi</title>
<style>
body{background:#0d1117;color:#fff;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;}
.box{background:#161b22;border:1px solid #30363d;padding:30px;border-radius:8px;width:300px;text-align:center;}
input{width:100%;box-sizing:border-box;padding:10px;margin:15px 0;background:#0d1117;border:1px solid #30363d;color:#fff;border-radius:6px;outline:none;}
button{width:100%;padding:10px;background:#00979d;border:none;color:#fff;font-weight:bold;border-radius:6px;cursor:pointer;}
</style></head>
<body>
<div class="box">
  <h3>⚡ ArduKod Yönetim</h3>
  <form method="POST">
    <input type="password" name="sifre" placeholder="Yönetici Parolası" required autofocus>
    <button type="submit">Giriş Yap</button>
  </form>
  {% if hata %}<p style="color:#f85149;margin-top:10px;font-size:13px;">{{ hata }}</p>{% endif %}
</div>
</body></html>
"""

ADMIN_PANEL_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head><meta charset="UTF-8"><title>ArduKod - Panel</title>
<style>
body{background:#0d1117;color:#fff;font-family:sans-serif;padding:20px;margin:0;}
.top{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #30363d;padding-bottom:15px;}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:15px;margin:20px 0;}
.card{background:#161b22;border:1px solid #30363d;padding:15px;border-radius:8px;}
.num{font-size:22px;font-weight:bold;color:#00979d;margin-top:5px;}
table{width:100%;border-collapse:collapse;margin-top:15px;background:#161b22;border-radius:8px;overflow:hidden;}
th,td{padding:10px 12px;border-bottom:1px solid #30363d;text-align:left;font-size:13.5px;}
th{background:#21262d;}
.btn{padding:6px 12px;border-radius:4px;cursor:pointer;border:none;font-weight:bold;text-decoration:none;font-size:12px;}
.btn-green{background:#238636;color:#fff;}
.btn-blue{background:#1f6feb;color:#fff;}
.btn-red{background:#da3633;color:#fff;}
.modal{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);align-items:center;justify-content:center;padding:20px;z-index:1000;}
.modal-content{background:#161b22;border:1px solid #30363d;padding:20px;border-radius:8px;width:750px;max-height:90vh;overflow-y:auto;}
input,select,textarea{width:100%;box-sizing:border-box;padding:8px;background:#0d1117;border:1px solid #30363d;color:#fff;border-radius:4px;margin-bottom:10px;font-family:inherit;}
</style></head>
<body>
<div class="top">
  <h2>⚡ ArduKod Yönetici Paneli</h2>
  <div>
    <button class="btn btn-green" onclick="yeniProjeModal()">+ Yeni Proje Ekle</button>
    <a href="/" target="_blank" class="btn btn-blue">Siteye Git</a>
    <a href="/admin/cikis" class="btn btn-red">Çıkış</a>
  </div>
</div>

<div class="stats">
  <div class="card">Toplam Proje: <div class="num">{{ projeler|length }}</div></div>
  <div class="card">Görüntülenme: <div class="num">{{ goruntulenme }}</div></div>
  <div class="card">Kod İndirme: <div class="num">{{ indirme }}</div></div>
  <div class="card">Gelen İstekler: <div class="num">{{ istekler|length }}</div></div>
</div>

<h3>📦 Proje & Link Yönetimi</h3>
<table>
  <thead><tr><th>ID</th><th>Başlık</th><th>Kategori</th><th>Görüntülenme</th><th>İşlemler</th></tr></thead>
  <tbody>
    {% for pid, p in projeler.items() %}
    <tr>
      <td><code>{{ pid }}</code></td>
      <td><b>{{ p.baslik }}</b></td>
      <td>{{ p.kategori }}</td>
      <td>{{ p.goruntulenme or 0 }}</td>
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
    <h3 id="mTitle">Proje Düzenleme</h3>
    <label>Proje ID:</label><input type="text" id="f_id">
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
    <label>Arduino Uno:</label><textarea id="f_kod_uno" rows="5"></textarea>
    <label>Arduino Nano:</label><textarea id="f_kod_nano" rows="5"></textarea>
    <label>ESP32:</label><textarea id="f_kod_esp32" rows="5"></textarea>
    <label>ESP8266:</label><textarea id="f_kod_esp8266" rows="5"></textarea>
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
    <input type="text" value="${link}" placeholder="Satın Alma Linki" style="flex:1.5;margin:0;" class="m_link">
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
  if((await res.json()).durum === 'basarili') { alert('Kaydedildi!'); location.reload(); }
}
async function sil(pid) {
  if(!confirm(pid + ' projesini silmek istiyor musunuz?')) return;
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
    projeler = veri_yukle()
    istekler = istek_yukle()
    g_top = sum(p.get("goruntulenme", 0) for p in projeler.values())
    i_top = sum(p.get("indirme", 0) for p in projeler.values())
    return render_template_string(ADMIN_PANEL_HTML, projeler=projeler, istekler=istekler, goruntulenme=g_top, indirme=i_top)

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
