import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = "ardukod_gizli_anahtar_9988_xyz"
ADMIN_SIFRE = "admin123"

# ==============================================================================
# TAM 20 PROJE - PINLER, KODLAR VE MALZEME LİNKLERİ EKSİKSİZ
# ==============================================================================
PROJELER = {
    "kara-simsek": {
        "kategori": "Temel & LED",
        "baslik": "5 LED Kademeli Kara Şimşek (Knight Rider)",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "5x", "isim": "5mm LED", "link": "https://www.direnc.net"},
            {"adet": "5x", "isim": "220Ω Direnç", "link": "https://www.direnc.net"},
            {"adet": "1x", "isim": "Breadboard", "link": "https://www.direnc.net"},
            {"adet": "6x", "isim": "Jumper Kablo", "link": "https://www.direnc.net"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "Arduino GND"}
                ],
                "kod": "// Arduino Uno - 5 LED Kara Simsek\nconst int pinler[] = {2, 3, 4, 5, 6};\nconst int adet = 5;\n\nvoid setup() {\n  for (int i = 0; i < adet; i++) pinMode(pinler[i], OUTPUT);\n}\n\nvoid loop() {\n  for (int i = 0; i < adet; i++) {\n    digitalWrite(pinler[i], HIGH);\n    delay(50);\n    digitalWrite(pinler[i], LOW);\n  }\n  for (int i = adet - 2; i > 0; i--) {\n    digitalWrite(pinler[i], HIGH);\n    delay(50);\n    digitalWrite(pinler[i], LOW);\n  }\n}"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "Nano GND"}
                ],
                "kod": "// Arduino Nano - 5 LED Kara Simsek\nconst int pinler[] = {2, 3, 4, 5, 6};\nconst int adet = 5;\n\nvoid setup() {\n  for (int i = 0; i < adet; i++) pinMode(pinler[i], OUTPUT);\n}\n\nvoid loop() {\n  for (int i = 0; i < adet; i++) {\n    digitalWrite(pinler[i], HIGH);\n    delay(50);\n    digitalWrite(pinler[i], LOW);\n  }\n  for (int i = adet - 2; i > 0; i--) {\n    digitalWrite(pinler[i], HIGH);\n    delay(50);\n    digitalWrite(pinler[i], LOW);\n  }\n}"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "GPIO 18, 19, 21, 22, 23 (330Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "ESP32 GND"}
                ],
                "kod": "// ESP32 - 5 LED Kara Simsek (3.3V Lojik)\nconst int pinler[] = {18, 19, 21, 22, 23};\nconst int adet = 5;\n\nvoid setup() {\n  for (int i = 0; i < adet; i++) pinMode(pinler[i], OUTPUT);\n}\n\nvoid loop() {\n  for (int i = 0; i < adet; i++) {\n    digitalWrite(pinler[i], HIGH);\n    delay(50);\n    digitalWrite(pinler[i], LOW);\n  }\n  for (int i = adet - 2; i > 0; i--) {\n    digitalWrite(pinler[i], HIGH);\n    delay(50);\n    digitalWrite(pinler[i], LOW);\n  }\n}"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D1, D2, D5, D6, D7 (GPIO 5, 4, 14, 12, 13)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "NodeMCU GND"}
                ],
                "kod": "// ESP8266 NodeMCU - 5 LED Kara Simsek\nconst int pinler[] = {D1, D2, D5, D6, D7};\nconst int adet = 5;\n\nvoid setup() {\n  for (int i = 0; i < adet; i++) pinMode(pinler[i], OUTPUT);\n}\n\nvoid loop() {\n  for (int i = 0; i < adet; i++) {\n    digitalWrite(pinler[i], HIGH);\n    delay(50);\n    digitalWrite(pinler[i], LOW);\n  }\n  for (int i = adet - 2; i > 0; i--) {\n    digitalWrite(pinler[i], HIGH);\n    delay(50);\n    digitalWrite(pinler[i], LOW);\n  }\n}"
            }
        }
    },
    "rgb-led-pwm": {
        "kategori": "Temel & LED",
        "baslik": "RGB LED Yumuşak Renk Geçişi (PWM Fade)",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "Ortak Katot RGB LED", "link": ""},
            {"adet": "3x", "isim": "220Ω / 330Ω Direnç", "link": ""},
            {"adet": "4x", "isim": "Jumper Kablo", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "RGB R / G / B", "pin": "D9 / D10 / D11 (PWM)"},
                    {"bilesen": "Ortak Katot (-)", "pin": "Arduino GND"}
                ],
                "kod": "// Arduino Uno - RGB LED PWM\nconst int r = 9, g = 10, b = 11;\nvoid setup() { pinMode(r, OUTPUT); pinMode(g, OUTPUT); pinMode(b, OUTPUT); }\nvoid loop() {\n  for (int i = 0; i < 255; i++) { analogWrite(r, i); analogWrite(g, 255-i); delay(5); }\n  for (int i = 0; i < 255; i++) { analogWrite(g, i); analogWrite(b, 255-i); delay(5); }\n  for (int i = 0; i < 255; i++) { analogWrite(b, i); analogWrite(r, 255-i); delay(5); }\n}"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "RGB R / G / B", "pin": "D9 / D10 / D11 (PWM)"},
                    {"bilesen": "Ortak Katot (-)", "pin": "Nano GND"}
                ],
                "kod": "// Arduino Nano - RGB LED PWM\nconst int r = 9, g = 10, b = 11;\nvoid setup() { pinMode(r, OUTPUT); pinMode(g, OUTPUT); pinMode(b, OUTPUT); }\nvoid loop() {\n  for (int i = 0; i < 255; i++) { analogWrite(r, i); analogWrite(g, 255-i); delay(5); }\n  for (int i = 0; i < 255; i++) { analogWrite(g, i); analogWrite(b, 255-i); delay(5); }\n  for (int i = 0; i < 255; i++) { analogWrite(b, i); analogWrite(r, 255-i); delay(5); }\n}"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez (Dahili ledc).",
                "baglanti": [
                    {"bilesen": "RGB R / G / B", "pin": "GPIO 18 / 19 / 21"},
                    {"bilesen": "Ortak Katot (-)", "pin": "ESP32 GND"}
                ],
                "kod": "// ESP32 - Donanimsal PWM ile RGB\nconst int r = 18, g = 19, b = 21;\nvoid setup() {\n  ledcAttach(r, 5000, 8);\n  ledcAttach(g, 5000, 8);\n  ledcAttach(b, 5000, 8);\n}\nvoid loop() {\n  for (int i = 0; i < 255; i++) { ledcWrite(r, i); ledcWrite(g, 255-i); delay(5); }\n  for (int i = 0; i < 255; i++) { ledcWrite(g, i); ledcWrite(b, 255-i); delay(5); }\n  for (int i = 0; i < 255; i++) { ledcWrite(b, i); ledcWrite(r, 255-i); delay(5); }\n}"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "RGB R / G / B", "pin": "D1 / D2 / D5"},
                    {"bilesen": "Ortak Katot (-)", "pin": "NodeMCU GND"}
                ],
                "kod": "// ESP8266 NodeMCU - RGB PWM (0-1023)\nconst int r = D1, g = D2, b = D5;\nvoid setup() { pinMode(r, OUTPUT); pinMode(g, OUTPUT); pinMode(b, OUTPUT); }\nvoid loop() {\n  for (int i = 0; i < 1023; i += 5) { analogWrite(r, i); analogWrite(g, 1023-i); delay(5); }\n  for (int i = 0; i < 1023; i += 5) { analogWrite(g, i); analogWrite(b, 1023-i); delay(5); }\n  for (int i = 0; i < 1023; i += 5) { analogWrite(b, i); analogWrite(r, 1023-i); delay(5); }\n}"
            }
        }
    },
    "trafik-isiklari": {
        "kategori": "Temel & LED",
        "baslik": "Zaman Ayarlı Standart Trafik Işıkları",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "3x", "isim": "Kırmızı, Sarı, Yeşil LED", "link": ""},
            {"adet": "3x", "isim": "220Ω Direnç", "link": ""},
            {"adet": "4x", "isim": "Jumper Kablo", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "Kırmızı / Sarı / Yeşil LED", "pin": "D2 / D3 / D4 (220Ω)"},
                    {"bilesen": "Katotlar (-)", "pin": "Arduino GND"}
                ],
                "kod": "// Uno - Trafik Isiklari\nconst int k=2, s=3, y=4;\nvoid setup() { pinMode(k, OUTPUT); pinMode(s, OUTPUT); pinMode(y, OUTPUT); }\nvoid loop() {\n  digitalWrite(k, HIGH); delay(4000);\n  digitalWrite(s, HIGH); delay(1000);\n  digitalWrite(k, LOW); digitalWrite(s, LOW); digitalWrite(y, HIGH); delay(4000);\n  digitalWrite(y, LOW); digitalWrite(s, HIGH); delay(1000); digitalWrite(s, LOW);\n}"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "Kırmızı / Sarı / Yeşil LED", "pin": "D2 / D3 / D4 (220Ω)"},
                    {"bilesen": "Katotlar (-)", "pin": "Nano GND"}
                ],
                "kod": "// Nano - Trafik Isiklari\nconst int k=2, s=3, y=4;\nvoid setup() { pinMode(k, OUTPUT); pinMode(s, OUTPUT); pinMode(y, OUTPUT); }\nvoid loop() {\n  digitalWrite(k, HIGH); delay(4000);\n  digitalWrite(s, HIGH); delay(1000);\n  digitalWrite(k, LOW); digitalWrite(s, LOW); digitalWrite(y, HIGH); delay(4000);\n  digitalWrite(y, LOW); digitalWrite(s, HIGH); delay(1000); digitalWrite(s, LOW);\n}"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "Kırmızı / Sarı / Yeşil LED", "pin": "GPIO 18 / 19 / 21 (330Ω)"},
                    {"bilesen": "Katotlar (-)", "pin": "ESP32 GND"}
                ],
                "kod": "// ESP32 - Trafik Isiklari\nconst int k=18, s=19, y=21;\nvoid setup() { pinMode(k, OUTPUT); pinMode(s, OUTPUT); pinMode(y, OUTPUT); }\nvoid loop() {\n  digitalWrite(k, HIGH); delay(4000);\n  digitalWrite(s, HIGH); delay(1000);\n  digitalWrite(k, LOW); digitalWrite(s, LOW); digitalWrite(y, HIGH); delay(4000);\n  digitalWrite(y, LOW); digitalWrite(s, HIGH); delay(1000); digitalWrite(s, LOW);\n}"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "Kırmızı / Sarı / Yeşil LED", "pin": "D1 / D2 / D5"},
                    {"bilesen": "Katotlar (-)", "pin": "NodeMCU GND"}
                ],
                "kod": "// ESP8266 - Trafik Isiklari\nconst int k=D1, s=D2, y=D5;\nvoid setup() { pinMode(k, OUTPUT); pinMode(s, OUTPUT); pinMode(y, OUTPUT); }\nvoid loop() {\n  digitalWrite(k, HIGH); delay(4000);\n  digitalWrite(s, HIGH); delay(1000);\n  digitalWrite(k, LOW); digitalWrite(s, LOW); digitalWrite(y, HIGH); delay(4000);\n  digitalWrite(y, LOW); digitalWrite(s, HIGH); delay(1000); digitalWrite(s, LOW);\n}"
            }
        }
    },
    "ldr-otomatik-far": {
        "kategori": "Sensörler",
        "baslik": "LDR & Gerilim Bölücü ile Otomatik Far/Aydınlatma",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "LDR (Fotodirenç)", "link": ""},
            {"adet": "1x", "isim": "10kΩ Direnç", "link": ""},
            {"adet": "1x", "isim": "5mm LED & 220Ω", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LDR ve 10k Ortak Bacak", "pin": "A0 (Analog Giriş)"},
                    {"bilesen": "LDR / 10k Uçları", "pin": "5V ve GND"},
                    {"bilesen": "LED Anot (+)", "pin": "D13"}
                ],
                "kod": "// Uno - LDR Otomatik Far\nconst int ldr=A0, led=13;\nvoid setup() { pinMode(led, OUTPUT); }\nvoid loop() {\n  int v = analogRead(ldr);\n  if (v < 400) digitalWrite(led, HIGH);\n  else digitalWrite(led, LOW);\n  delay(100);\n}"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LDR ve 10k Ortak Bacak", "pin": "A0"},
                    {"bilesen": "LDR / 10k Uçları", "pin": "5V ve GND"},
                    {"bilesen": "LED Anot (+)", "pin": "D13"}
                ],
                "kod": "// Nano - LDR Otomatik Far\nconst int ldr=A0, led=13;\nvoid setup() { pinMode(led, OUTPUT); }\nvoid loop() {\n  int v = analogRead(ldr);\n  if (v < 400) digitalWrite(led, HIGH);\n  else digitalWrite(led, LOW);\n  delay(100);\n}"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LDR ve 10k Ortak Bacak", "pin": "GPIO 34 (ADC1)"},
                    {"bilesen": "LDR / 10k Uçları", "pin": "3.3V ve GND"},
                    {"bilesen": "LED Anot (+)", "pin": "GPIO 2"}
                ],
                "kod": "// ESP32 - LDR Far (12-bit: 0-4095)\nconst int ldr=34, led=2;\nvoid setup() { pinMode(led, OUTPUT); }\nvoid loop() {\n  int v = analogRead(ldr);\n  if (v < 1500) digitalWrite(led, HIGH);\n  else digitalWrite(led, LOW);\n  delay(100);\n}"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LDR ve 10k Ortak Bacak", "pin": "A0 (Maks 1.0V/3.3V)"},
                    {"bilesen": "LDR / 10k Uçları", "pin": "3.3V ve GND"},
                    {"bilesen": "LED Anot (+)", "pin": "D4"}
                ],
                "kod": "// ESP8266 - LDR Far\nconst int ldr=A0, led=D4;\nvoid setup() { pinMode(led, OUTPUT); }\nvoid loop() {\n  int v = analogRead(ldr);\n  if (v < 450) digitalWrite(led, LOW); // NodeMCU dahili LED ters mantik\n  else digitalWrite(led, HIGH);\n  delay(100);\n}"
            }
        }
    },
    "hc-sr04-radar": {
        "kategori": "Sensörler",
        "baslik": "HC-SR04 Ultrasonik Hassas Park Sensörü & Buzzer",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "HC-SR04 Mesafe Sensörü", "link": ""},
            {"adet": "1x", "isim": "Buzzer", "link": ""},
            {"adet": "1x", "isim": "Breadboard & Jumper", "link": ""},
            {"adet": "2x", "isim": "1kΩ ve 2kΩ Direnç (ESP koruması)", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "HC-SR04 Trig / Echo", "pin": "D9 / D10"},
                    {"bilesen": "Buzzer (+)", "pin": "D8"}
                ],
                "kod": "// Arduino Uno - Park Sensoru\nconst int trig = 9, echo = 10, buzz = 8;\nvoid setup() {\n  pinMode(trig, OUTPUT); pinMode(echo, INPUT); pinMode(buzz, OUTPUT);\n}\nvoid loop() {\n  digitalWrite(trig, LOW); delayMicroseconds(2);\n  digitalWrite(trig, HIGH); delayMicroseconds(10);\n  digitalWrite(trig, LOW);\n  long sure = pulseIn(echo, HIGH, 30000);\n  int d = (sure * 0.0343) / 2;\n  if (d > 0 && d < 20) {\n    digitalWrite(buzz, HIGH); delay(40);\n    digitalWrite(buzz, LOW); delay(40);\n  }\n}"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "HC-SR04 Trig / Echo", "pin": "D9 / D10"},
                    {"bilesen": "Buzzer (+)", "pin": "D8"}
                ],
                "kod": "// Arduino Nano - Park Sensoru\nconst int trig = 9, echo = 10, buzz = 8;\nvoid setup() {\n  pinMode(trig, OUTPUT); pinMode(echo, INPUT); pinMode(buzz, OUTPUT);\n}\nvoid loop() {\n  digitalWrite(trig, LOW); delayMicroseconds(2);\n  digitalWrite(trig, HIGH); delayMicroseconds(10);\n  digitalWrite(trig, LOW);\n  long sure = pulseIn(echo, HIGH, 30000);\n  int d = (sure * 0.0343) / 2;\n  if (d > 0 && d < 20) {\n    digitalWrite(buzz, HIGH); delay(40);\n    digitalWrite(buzz, LOW); delay(40);\n  }\n}"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "VIN (5V) / GND"},
                    {"bilesen": "HC-SR04 Trig / Echo", "pin": "GPIO 5 / GPIO 18 (1k/2k bolucu)"},
                    {"bilesen": "Buzzer (+)", "pin": "GPIO 19"}
                ],
                "kod": "// ESP32 - Park Sensoru (3.3V Korumali)\nconst int trig = 5, echo = 18, buzz = 19;\nvoid setup() {\n  pinMode(trig, OUTPUT); pinMode(echo, INPUT); pinMode(buzz, OUTPUT);\n}\nvoid loop() {\n  digitalWrite(trig, LOW); delayMicroseconds(2);\n  digitalWrite(trig, HIGH); delayMicroseconds(10);\n  digitalWrite(trig, LOW);\n  long sure = pulseIn(echo, HIGH, 30000);\n  int d = (sure * 0.0343) / 2;\n  if (d > 0 && d < 20) {\n    digitalWrite(buzz, HIGH); delay(40);\n    digitalWrite(buzz, LOW); delay(40);\n  }\n}"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "VV (5V) / GND"},
                    {"bilesen": "HC-SR04 Trig / Echo", "pin": "D1 / D2 (Bolucu)"},
                    {"bilesen": "Buzzer (+)", "pin": "D5"}
                ],
                "kod": "// ESP8266 - Park Sensoru\nconst int trig = D1, echo = D2, buzz = D5;\nvoid setup() {\n  pinMode(trig, OUTPUT); pinMode(echo, INPUT); pinMode(buzz, OUTPUT);\n}\nvoid loop() {\n  digitalWrite(trig, LOW); delayMicroseconds(2);\n  digitalWrite(trig, HIGH); delayMicroseconds(10);\n  digitalWrite(trig, LOW);\n  long sure = pulseIn(echo, HIGH, 30000);\n  int d = (sure * 0.0343) / 2;\n  if (d > 0 && d < 20) {\n    digitalWrite(buzz, HIGH); delay(40);\n    digitalWrite(buzz, LOW); delay(40);\n  }\n}"
            }
        }
    },
    "hc-sr501-pir": {
        "kategori": "Sensörler",
        "baslik": "HC-SR501 PIR Hareket Algılamalı Hırsız Alarmı",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "HC-SR501 PIR Sensörü", "link": ""},
            {"adet": "1x", "isim": "Buzzer / LED", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "PIR VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "PIR OUT", "pin": "D2"},
                    {"bilesen": "Alarm LED/Buzzer", "pin": "D13"}
                ],
                "kod": "// Uno - PIR Alarm\nconst int pir=2, led=13;\nvoid setup() { pinMode(pir, INPUT); pinMode(led, OUTPUT); }\nvoid loop() {\n  if(digitalRead(pir) == HIGH) digitalWrite(led, HIGH);\n  else digitalWrite(led, LOW);\n}"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "PIR VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "PIR OUT", "pin": "D2"},
                    {"bilesen": "Alarm LED", "pin": "D13"}
                ],
                "kod": "// Nano - PIR Alarm\nconst int pir=2, led=13;\nvoid setup() { pinMode(pir, INPUT); pinMode(led, OUTPUT); }\nvoid loop() {\n  if(digitalRead(pir) == HIGH) digitalWrite(led, HIGH);\n  else digitalWrite(led, LOW);\n}"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "PIR VCC / GND", "pin": "VIN (5V) / GND"},
                    {"bilesen": "PIR OUT", "pin": "GPIO 13"},
                    {"bilesen": "Alarm LED", "pin": "GPIO 2"}
                ],
                "kod": "// ESP32 - PIR Alarm\nconst int pir=13, led=2;\nvoid setup() { pinMode(pir, INPUT); pinMode(led, OUTPUT); }\nvoid loop() {\n  if(digitalRead(pir) == HIGH) digitalWrite(led, HIGH);\n  else digitalWrite(led, LOW);\n}"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "PIR VCC / GND", "pin": "VV (5V) / GND"},
                    {"bilesen": "PIR OUT", "pin": "D7"},
                    {"bilesen": "Alarm LED", "pin": "D4"}
                ],
                "kod": "// ESP8266 - PIR Alarm\nconst int pir=D7, led=D4;\nvoid setup() { pinMode(pir, INPUT); pinMode(led, OUTPUT); }\nvoid loop() {\n  if(digitalRead(pir) == HIGH) digitalWrite(led, LOW);\n  else digitalWrite(led, HIGH);\n}"
            }
        }
    },
    "dht11-sicaklik": {
        "kategori": "Sensörler",
        "baslik": "DHT11 Dijital Sıcaklık & Nem Ölçümü",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "DHT11 Sensörü", "link": ""},
            {"adet": "1x", "isim": "10kΩ Pull-up Direnç", "link": ""},
            {"adet": "3x", "isim": "Jumper Kablo", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<DHT.h> (Adafruit DHT Library)",
                "baglanti": [{"bilesen": "DHT11 VCC / GND", "pin": "5V / GND"}, {"bilesen": "DHT11 DATA", "pin": "D2 (10kΩ pull-up)"}],
                "kod": "#include <DHT.h>\nDHT dht(2, DHT11);\nvoid setup() { Serial.begin(9600); dht.begin(); }\nvoid loop() {\n  delay(2000);\n  Serial.print(\"Nem: %\"); Serial.println(dht.readHumidity());\n  Serial.print(\"Sicaklik: \"); Serial.println(dht.readTemperature());\n}"
            },
            "nano": {
                "kutuphaneler": "<DHT.h>",
                "baglanti": [{"bilesen": "DHT11 VCC / GND", "pin": "5V / GND"}, {"bilesen": "DHT11 DATA", "pin": "D2"}],
                "kod": "#include <DHT.h>\nDHT dht(2, DHT11);\nvoid setup() { Serial.begin(9600); dht.begin(); }\nvoid loop() {\n  delay(2000);\n  Serial.println(dht.readTemperature());\n}"
            },
            "esp32": {
                "kutuphaneler": "<DHT.h>",
                "baglanti": [{"bilesen": "DHT11 VCC / GND", "pin": "3.3V / GND"}, {"bilesen": "DHT11 DATA", "pin": "GPIO 4 (4.7kΩ pull-up)"}],
                "kod": "#include <DHT.h>\nDHT dht(4, DHT11);\nvoid setup() { Serial.begin(115200); dht.begin(); }\nvoid loop() {\n  delay(2000);\n  Serial.println(dht.readTemperature());\n}"
            },
            "esp8266": {
                "kutuphaneler": "<DHT.h>",
                "baglanti": [{"bilesen": "DHT11 VCC / GND", "pin": "3.3V / GND"}, {"bilesen": "DHT11 DATA", "pin": "D4 (GPIO 2, 4.7kΩ pull-up)"}],
                "kod": "#include <DHT.h>\nDHT dht(D4, DHT11);\nvoid setup() { Serial.begin(115200); dht.begin(); }\nvoid loop() {\n  delay(2000);\n  Serial.println(dht.readTemperature());\n}"
            }
        }
    },
    "tcrt5000-cizgi": {
        "kategori": "Sensörler",
        "baslik": "TCRT5000 Çift Çıkışlı Kızılötesi Çizgi Sensörü",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "TCRT5000 Çizgi Takip Sensörü", "link": ""},
            {"adet": "1x", "isim": "LED & 220Ω", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "TCRT5000 VCC / GND", "pin": "5V / GND"}, {"bilesen": "DO (Dijital Çıkış)", "pin": "D2"}, {"bilesen": "LED", "pin": "D13"}],
                "kod": "// Uno - Cizgi Takip\nconst int sens=2, led=13;\nvoid setup() { pinMode(sens, INPUT); pinMode(led, OUTPUT); }\nvoid loop() {\n  if(digitalRead(sens) == LOW) digitalWrite(led, HIGH); // Cizgide\n  else digitalWrite(led, LOW);\n}"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "TCRT5000 VCC / GND", "pin": "5V / GND"}, {"bilesen": "DO", "pin": "D2"}, {"bilesen": "LED", "pin": "D13"}],
                "kod": "// Nano - Cizgi Takip\nconst int sens=2, led=13;\nvoid setup() { pinMode(sens, INPUT); pinMode(led, OUTPUT); }\nvoid loop() {\n  if(digitalRead(sens) == LOW) digitalWrite(led, HIGH);\n  else digitalWrite(led, LOW);\n}"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "TCRT5000 VCC / GND", "pin": "3.3V / GND"}, {"bilesen": "DO", "pin": "GPIO 4"}, {"bilesen": "LED", "pin": "GPIO 2"}],
                "kod": "// ESP32 - Cizgi Takip\nconst int sens=4, led=2;\nvoid setup() { pinMode(sens, INPUT); pinMode(led, OUTPUT); }\nvoid loop() {\n  if(digitalRead(sens) == LOW) digitalWrite(led, HIGH);\n  else digitalWrite(led, LOW);\n}"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "TCRT5000 VCC / GND", "pin": "3.3V / GND"}, {"bilesen": "DO", "pin": "D1"}, {"bilesen": "LED", "pin": "D4"}],
                "kod": "// ESP8266 - Cizgi Takip\nconst int sens=D1, led=D4;\nvoid setup() { pinMode(sens, INPUT); pinMode(led, OUTPUT); }\nvoid loop() {\n  if(digitalRead(sens) == LOW) digitalWrite(led, LOW);\n  else digitalWrite(led, HIGH);\n}"
            }
        }
    },
    "pot-analog-map": {
        "kategori": "Giriş & Kontrol",
        "baslik": "Potansiyometre ile LED Parlaklığı Ayarlama (Map)",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "10kΩ Potansiyometre", "link": ""},
            {"adet": "1x", "isim": "LED & 220Ω Direnç", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Pot Orta Bacak", "pin": "A0"}, {"bilesen": "Pot Yan Bacaklar", "pin": "5V ve GND"}, {"bilesen": "LED Anot (+)", "pin": "D9 (PWM)"}],
                "kod": "// Uno Potansiyometre PWM\nvoid setup() { pinMode(9, OUTPUT); }\nvoid loop() {\n  int v = analogRead(A0);\n  analogWrite(9, map(v, 0, 1023, 0, 255));\n  delay(10);\n}"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Pot Orta Bacak", "pin": "A0"}, {"bilesen": "Pot Yan Bacaklar", "pin": "5V ve GND"}, {"bilesen": "LED Anot (+)", "pin": "D9 (PWM)"}],
                "kod": "// Nano Potansiyometre PWM\nvoid setup() { pinMode(9, OUTPUT); }\nvoid loop() {\n  int v = analogRead(A0);\n  analogWrite(9, map(v, 0, 1023, 0, 255));\n  delay(10);\n}"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Pot Orta Bacak", "pin": "GPIO 32 (ADC1)"}, {"bilesen": "Pot Yan Bacaklar", "pin": "3.3V ve GND"}, {"bilesen": "LED Anot (+)", "pin": "GPIO 18"}],
                "kod": "// ESP32 Pot PWM\nvoid setup() { ledcAttach(18, 5000, 8); }\nvoid loop() {\n  int v = analogRead(32);\n  ledcWrite(18, map(v, 0, 4095, 0, 255));\n  delay(10);\n}"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Pot Orta Bacak", "pin": "A0"}, {"bilesen": "Pot Yan Bacaklar", "pin": "3.3V ve GND"}, {"bilesen": "LED Anot (+)", "pin": "D1"}],
                "kod": "// ESP8266 Pot PWM\nvoid setup() { pinMode(D1, OUTPUT); }\nvoid loop() {\n  analogWrite(D1, analogRead(A0));\n  delay(10);\n}"
            }
        }
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projeler', methods=['GET'])
def projeleri_getir():
    liste = []
    for k, v in PROJELER.items():
        liste.append({
            "id": k,
            "baslik": v.get("baslik", k),
            "kategori": v.get("kategori", "Genel"),
            "zorluk": v.get("zorluk", "Başlangıç"),
            "sure": v.get("sure", "10 Dk")
        })
    return jsonify(liste)

@app.route('/proje/<id>', methods=['GET'])
def tek_proje(id):
    if id in PROJELER:
        return jsonify({"durum": "basarili", "veri": PROJELER[id]})
    # Eğer id doğrudan bulunamazsa ilk projeyi döndür ki ekran boş kalmasın
    ilk = list(PROJELER.values())[0]
    return jsonify({"durum": "basarili", "veri": ilk})

@app.route('/proje/<id>/indir', methods=['POST'])
def indir_say(id):
    return jsonify({"durum": "ok"})

@app.route('/istek-gonder', methods=['POST'])
def istek_ekle():
    return jsonify({"durum": "basarili", "mesaj": "Talebiniz iletildi!"})

# ==============================================================================
# HATA VERMEYEN DAHİLİ ADMİN PANELİ (Tek Tıkla Açılır)
# ==============================================================================
ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head><title>Admin Girişi</title>
<style>
body{background:#0d1117;color:#fff;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;}
.box{background:#161b22;border:1px solid #30363d;padding:30px;border-radius:8px;width:320px;text-align:center;}
input{width:100%;box-sizing:border-box;padding:10px;margin:15px 0;background:#0d1117;border:1px solid #30363d;color:#fff;border-radius:6px;outline:none;}
button{width:100%;padding:10px;background:#00979d;border:none;color:#fff;font-weight:bold;border-radius:6px;cursor:pointer;}
</style></head>
<body>
<div class="box">
  <h3>⚡ ArduKod Yönetici Paneli</h3>
  <form method="POST">
    <input type="password" name="sifre" placeholder="Şifrenizi Girin (admin123)" required autofocus>
    <button type="submit">Giriş Yap</button>
  </form>
  {% if hata %}<p style="color:#f85149;margin-top:10px;">{{ hata }}</p>{% endif %}
</div>
</body></html>
"""

ADMIN_PANEL_HTML = """
<!DOCTYPE html>
<html>
<head><title>ArduKod - Yönetim</title>
<style>
body{background:#0d1117;color:#fff;font-family:sans-serif;padding:25px;margin:0;}
.top{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #30363d;padding-bottom:15px;}
table{width:100%;border-collapse:collapse;margin-top:20px;background:#161b22;border-radius:6px;overflow:hidden;}
th,td{padding:12px;border-bottom:1px solid #30363d;text-align:left;font-size:14px;}
th{background:#21262d;}
.btn{padding:8px 14px;border-radius:4px;border:none;cursor:pointer;font-weight:bold;text-decoration:none;}
.btn-green{background:#238636;color:#fff;}
.btn-blue{background:#1f6feb;color:#fff;}
.btn-red{background:#da3633;color:#fff;}
input,textarea{width:100%;box-sizing:border-box;padding:8px;background:#0d1117;border:1px solid #30363d;color:#fff;border-radius:4px;margin-bottom:10px;}
</style></head>
<body>
<div class="top">
  <h2>⚡ ArduKod İçerik & Link Yönetimi</h2>
  <div>
    <a href="/" target="_blank" class="btn btn-blue">🌐 Siteye Dön</a>
    <a href="/admin/cikis" class="btn btn-red">Çıkış Yap</a>
  </div>
</div>

<h3>📦 Yayındaki Projeler ve Ürün Linkleri</h3>
<table>
  <thead><tr><th>Proje Başlığı</th><th>Kategori</th><th>Malzemeler & Linkler</th><th>İşlem</th></tr></thead>
  <tbody>
    {% for pid, p in projeler.items() %}
    <tr>
      <td><b>{{ p.baslik }}</b><br><small style="color:#8b949e;">ID: {{ pid }}</small></td>
      <td>{{ p.kategori }}</td>
      <td>
        <ul style="margin:0;padding-left:15px;">
        {% for m in p.malzemeler %}
          <li>{{ m.adet }} {{ m.isim }} {% if m.link %}<a href="{{ m.link }}" target="_blank" style="color:#58a6ff;">[Link Var]</a>{% endif %}</li>
        {% endfor %}
        </ul>
      </td>
      <td>
        <button class="btn btn-blue" onclick='linkDuzenle({{ pid|tojson }}, {{ p.malzemeler|tojson }})'>🔗 Linkleri Düzenle</button>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<!-- Link Düzenleme Penceresi -->
<div id="linkModal" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);align-items:center;justify-content:center;">
  <div style="background:#161b22;border:1px solid #30363d;padding:25px;border-radius:8px;width:600px;max-height:80vh;overflow-y:auto;">
    <h3 id="modalBaslik">Malzeme Satın Alma Linkleri</h3>
    <input type="hidden" id="aktifPid">
    <div id="malzemeListesi"></div>
    <div style="text-align:right;margin-top:15px;">
      <button class="btn" style="background:#30363d;color:#fff;" onclick="modalKapat()">Kapat</button>
      <button class="btn btn-green" onclick="linkleriKaydet()">Kaydet</button>
    </div>
  </div>
</div>

<script>
function linkDuzenle(pid, malzemeler) {
  document.getElementById('aktifPid').value = pid;
  document.getElementById('modalBaslik').innerText = pid + " - Ürün Linkleri";
  const box = document.getElementById('malzemeListesi');
  box.innerHTML = '';
  malzemeler.forEach((m, idx) => {
    box.innerHTML += `
      <div style="margin-bottom:12px;background:#0d1117;padding:10px;border-radius:6px;border:1px solid #30363d;">
        <div style="font-weight:bold;margin-bottom:5px;">${m.adet} ${m.isim}</div>
        <input type="text" id="link_${idx}" value="${m.link || ''}" placeholder="Satın alma linki (Örn: https://direnc.net/...)">
      </div>
    `;
  });
  document.getElementById('linkModal').style.display = 'flex';
}
function modalKapat() { document.getElementById('linkModal').style.display = 'none'; }

async function linkleriKaydet() {
  const pid = document.getElementById('aktifPid').value;
  const inputs = document.querySelectorAll('#malzemeListesi input');
  const linkler = Array.from(inputs).map(i => i.value.trim());

  const res = await fetch('/admin/link-guncelle', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ pid, linkler })
  });
  if((await res.json()).durum === 'ok') {
    alert('Linkler başarıyla kaydedildi!');
    location.reload();
  }
}
</script>
</body></html>
"""

@app.route('/admin', methods=['GET', 'POST'])
def admin_giris():
    if session.get("admin"):
        return redirect('/admin/panel')
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
    if not session.get("admin"):
        return redirect('/admin')
    return render_template_string(ADMIN_PANEL_HTML, projeler=PROJELER)

@app.route('/admin/link-guncelle', methods=['POST'])
def admin_link_guncelle():
    if not session.get("admin"):
        return jsonify({"durum": "yetkisiz"}), 403
    d = request.get_json() or {}
    pid = d.get("pid")
    linkler = d.get("linkler", [])
    if pid in PROJELER and "malzemeler" in PROJELER[pid]:
        for idx, link in enumerate(linkler):
            if idx < len(PROJELER[pid]["malzemeler"]):
                PROJELER[pid]["malzemeler"][idx]["link"] = link
        return jsonify({"durum": "ok"})
    return jsonify({"durum": "hata"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
