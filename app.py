import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = "ardukod_tam_yetkili_gizli_anahtar_2026"
ADMIN_SIFRE = "admin123"

VERI_DOSYASI = "projeler.json"
ISTEK_DOSYASI = "istekler.json"

# ==============================================================================
# 20 PROJENİN TAMAMI (Kusursuz 4 Kart Kodu, Pin Tabloları & Malzeme Listeleri)
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
            {"adet": "5x", "isim": "5mm LED", "link": "https://www.direnc.net"},
            {"adet": "5x", "isim": "220Ω Direnç", "link": ""},
            {"adet": "1x", "isim": "Breadboard", "link": ""},
            {"adet": "6x", "isim": "Jumper Kablo", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "GND"}
                ],
                "kod": "// Arduino Uno - Kara Simsek\nconst int pinler[] = {2, 3, 4, 5, 6};\nconst int adet = 5;\nvoid setup() {\n  for(int i=0; i<adet; i++) pinMode(pinler[i], OUTPUT);\n}\nvoid loop() {\n  for(int i=0; i<adet; i++) { digitalWrite(pinler[i], HIGH); delay(50); digitalWrite(pinler[i], LOW); }\n  for(int i=adet-2; i>0; i--) { digitalWrite(pinler[i], HIGH); delay(50); digitalWrite(pinler[i], LOW); }\n}"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "GND"}
                ],
                "kod": "// Arduino Nano - Kara Simsek\nconst int pinler[] = {2, 3, 4, 5, 6};\nconst int adet = 5;\nvoid setup() {\n  for(int i=0; i<adet; i++) pinMode(pinler[i], OUTPUT);\n}\nvoid loop() {\n  for(int i=0; i<adet; i++) { digitalWrite(pinler[i], HIGH); delay(50); digitalWrite(pinler[i], LOW); }\n  for(int i=adet-2; i>0; i--) { digitalWrite(pinler[i], HIGH); delay(50); digitalWrite(pinler[i], LOW); }\n}"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "GPIO 18, 19, 21, 22, 23 (330Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "GND"}
                ],
                "kod": "// ESP32 - Kara Simsek (3.3V Lojik)\nconst int pinler[] = {18, 19, 21, 22, 23};\nconst int adet = 5;\nvoid setup() {\n  for(int i=0; i<adet; i++) pinMode(pinler[i], OUTPUT);\n}\nvoid loop() {\n  for(int i=0; i<adet; i++) { digitalWrite(pinler[i], HIGH); delay(50); digitalWrite(pinler[i], LOW); }\n  for(int i=adet-2; i>0; i--) { digitalWrite(pinler[i], HIGH); delay(50); digitalWrite(pinler[i], LOW); }\n}"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D1, D2, D5, D6, D7 (GPIO 5,4,14,12,13)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "GND"}
                ],
                "kod": "// ESP8266 NodeMCU - Kara Simsek\nconst int pinler[] = {D1, D2, D5, D6, D7};\nconst int adet = 5;\nvoid setup() {\n  for(int i=0; i<adet; i++) pinMode(pinler[i], OUTPUT);\n}\nvoid loop() {\n  for(int i=0; i<adet; i++) { digitalWrite(pinler[i], HIGH); delay(50); digitalWrite(pinler[i], LOW); }\n  for(int i=adet-2; i>0; i--) { digitalWrite(pinler[i], HIGH); delay(50); digitalWrite(pinler[i], LOW); }\n}"
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
            {"adet": "1x", "isim": "Ortak Katot RGB LED", "link": ""},
            {"adet": "3x", "isim": "220Ω Direnç", "link": ""},
            {"adet": "4x", "isim": "Jumper Kablo", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "D9 / D10 / D11 (PWM)"}, {"bilesen": "Ortak Katot (-)", "pin": "GND"}],
                "kod": "// Uno RGB PWM\nconst int r=9, g=10, b=11;\nvoid setup() { pinMode(r, OUTPUT); pinMode(g, OUTPUT); pinMode(b, OUTPUT); }\nvoid loop() {\n  for(int i=0; i<255; i++) { analogWrite(r, i); analogWrite(g, 255-i); delay(5); }\n  for(int i=0; i<255; i++) { analogWrite(g, i); analogWrite(b, 255-i); delay(5); }\n  for(int i=0; i<255; i++) { analogWrite(b, i); analogWrite(r, 255-i); delay(5); }\n}"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "D9 / D10 / D11 (PWM)"}, {"bilesen": "Ortak Katot (-)", "pin": "GND"}],
                "kod": "// Nano RGB PWM\nconst int r=9, g=10, b=11;\nvoid setup() { pinMode(r, OUTPUT); pinMode(g, OUTPUT); pinMode(b, OUTPUT); }\nvoid loop() {\n  for(int i=0; i<255; i++) { analogWrite(r, i); analogWrite(g, 255-i); delay(5); }\n  for(int i=0; i<255; i++) { analogWrite(g, i); analogWrite(b, 255-i); delay(5); }\n  for(int i=0; i<255; i++) { analogWrite(b, i); analogWrite(r, 255-i); delay(5); }\n}"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez (Dahili ledc PWM motoru).",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "GPIO 18 / 19 / 21"}, {"bilesen": "Ortak Katot (-)", "pin": "GND"}],
                "kod": "// ESP32 Donanimsal PWM ile RGB\nconst int r=18, g=19, b=21;\nvoid setup() { ledcAttach(r, 5000, 8); ledcAttach(g, 5000, 8); ledcAttach(b, 5000, 8); }\nvoid loop() {\n  for(int i=0; i<255; i++) { ledcWrite(r, i); ledcWrite(g, 255-i); delay(5); }\n  for(int i=0; i<255; i++) { ledcWrite(g, i); ledcWrite(b, 255-i); delay(5); }\n  for(int i=0; i<255; i++) { ledcWrite(b, i); ledcWrite(r, 255-i); delay(5); }\n}"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "D1 / D2 / D5"}, {"bilesen": "Ortak Katot (-)", "pin": "GND"}],
                "kod": "// ESP8266 RGB PWM (0-1023)\nconst int r=D1, g=D2, b=D5;\nvoid setup() { pinMode(r, OUTPUT); pinMode(g, OUTPUT); pinMode(b, OUTPUT); }\nvoid loop() {\n  for(int i=0; i<1023; i+=5) { analogWrite(r, i); analogWrite(g, 1023-i); delay(5); }\n  for(int i=0; i<1023; i+=5) { analogWrite(g, i); analogWrite(b, 1023-i); delay(5); }\n  for(int i=0; i<1023; i+=5) { analogWrite(b, i); analogWrite(r, 1023-i); delay(5); }\n}"
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
        "malzemeler": [
            {"adet": "3x", "isim": "Kırmızı, Sarı, Yeşil LED", "link": ""},
            {"adet": "3x", "isim": "220Ω Direnç", "link": ""},
            {"adet": "4x", "isim": "Jumper Kablo", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Kırmızı / Sarı / Yeşil LED", "pin": "D2 / D3 / D4 (220Ω)"}, {"bilesen": "Katotlar (-)", "pin": "GND"}],
                "kod": "// Uno Trafik Isiklari\nconst int k=2, s=3, y=4;\nvoid setup() { pinMode(k, OUTPUT); pinMode(s, OUTPUT); pinMode(y, OUTPUT); }\nvoid loop() {\n  digitalWrite(k, HIGH); delay(4000); digitalWrite(s, HIGH); delay(1000);\n  digitalWrite(k, LOW); digitalWrite(s, LOW); digitalWrite(y, HIGH); delay(4000);\n  digitalWrite(y, LOW); digitalWrite(s, HIGH); delay(1000); digitalWrite(s, LOW);\n}"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Kırmızı / Sarı / Yeşil LED", "pin": "D2 / D3 / D4 (220Ω)"}, {"bilesen": "Katotlar (-)", "pin": "GND"}],
                "kod": "// Nano Trafik Isiklari\nconst int k=2, s=3, y=4;\nvoid setup() { pinMode(k, OUTPUT); pinMode(s, OUTPUT); pinMode(y, OUTPUT); }\nvoid loop() {\n  digitalWrite(k, HIGH); delay(4000); digitalWrite(s, HIGH); delay(1000);\n  digitalWrite(k, LOW); digitalWrite(s, LOW); digitalWrite(y, HIGH); delay(4000);\n  digitalWrite(y, LOW); digitalWrite(s, HIGH); delay(1000); digitalWrite(s, LOW);\n}"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Kırmızı / Sarı / Yeşil LED", "pin": "GPIO 18 / 19 / 21"}, {"bilesen": "Katotlar (-)", "pin": "GND"}],
                "kod": "// ESP32 Trafik Isiklari\nconst int k=18, s=19, y=21;\nvoid setup() { pinMode(k, OUTPUT); pinMode(s, OUTPUT); pinMode(y, OUTPUT); }\nvoid loop() {\n  digitalWrite(k, HIGH); delay(4000); digitalWrite(s, HIGH); delay(1000);\n  digitalWrite(k, LOW); digitalWrite(s, LOW); digitalWrite(y, HIGH); delay(4000);\n  digitalWrite(y, LOW); digitalWrite(s, HIGH); delay(1000); digitalWrite(s, LOW);\n}"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Kırmızı / Sarı / Yeşil LED", "pin": "D1 / D2 / D5"}, {"bilesen": "Katotlar (-)", "pin": "GND"}],
                "kod": "// ESP8266 Trafik Isiklari\nconst int k=D1, s=D2, y=D5;\nvoid setup() { pinMode(k, OUTPUT); pinMode(s, OUTPUT); pinMode(y, OUTPUT); }\nvoid loop() {\n  digitalWrite(k, HIGH); delay(4000); digitalWrite(s, HIGH); delay(1000);\n  digitalWrite(k, LOW); digitalWrite(s, LOW); digitalWrite(y, HIGH); delay(4000);\n  digitalWrite(y, LOW); digitalWrite(s, HIGH); delay(1000); digitalWrite(s, LOW);\n}"
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
        "malzemeler": [
            {"adet": "1x", "isim": "LDR (Fotodirenç)", "link": ""},
            {"adet": "1x", "isim": "10kΩ Direnç", "link": ""},
            {"adet": "1x", "isim": "5mm LED & 220Ω", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "LDR & 10k Ortak Bacak", "pin": "A0"}, {"bilesen": "LDR / 10k Diğer Uçlar", "pin": "5V ve GND"}, {"bilesen": "LED (+)", "pin": "D13"}],
                "kod": "// Uno LDR Otomatik Far\nconst int ldr=A0, led=13;\nvoid setup() { pinMode(led, OUTPUT); }\nvoid loop() { if(analogRead(ldr) < 400) digitalWrite(led, HIGH); else digitalWrite(led, LOW); delay(100); }"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "LDR & 10k Ortak Bacak", "pin": "A0"}, {"bilesen": "LDR / 10k Diğer Uçlar", "pin": "5V ve GND"}, {"bilesen": "LED (+)", "pin": "D13"}],
                "kod": "// Nano LDR Otomatik Far\nconst int ldr=A0, led=13;\nvoid setup() { pinMode(led, OUTPUT); }\nvoid loop() { if(analogRead(ldr) < 400) digitalWrite(led, HIGH); else digitalWrite(led, LOW); delay(100); }"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "LDR & 10k Ortak Bacak", "pin": "GPIO 34 (ADC1)"}, {"bilesen": "LDR / 10k Diğer Uçlar", "pin": "3.3V ve GND"}, {"bilesen": "LED (+)", "pin": "GPIO 2"}],
                "kod": "// ESP32 LDR (12-bit: 0-4095)\nconst int ldr=34, led=2;\nvoid setup() { pinMode(led, OUTPUT); }\nvoid loop() { if(analogRead(ldr) < 1500) digitalWrite(led, HIGH); else digitalWrite(led, LOW); delay(100); }"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "LDR & 10k Ortak Bacak", "pin": "A0 (Maks 1.0V/3.3V)"}, {"bilesen": "LDR / 10k Diğer Uçlar", "pin": "3.3V ve GND"}, {"bilesen": "LED (+)", "pin": "D4"}],
                "kod": "// ESP8266 LDR\nconst int ldr=A0, led=D4;\nvoid setup() { pinMode(led, OUTPUT); }\nvoid loop() { if(analogRead(ldr) < 450) digitalWrite(led, LOW); else digitalWrite(led, HIGH); delay(100); }"
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
            {"adet": "1x", "isim": "HC-SR04 Mesafe Sensörü", "link": ""},
            {"adet": "1x", "isim": "Buzzer", "link": ""},
            {"adet": "2x", "isim": "1kΩ ve 2kΩ Direnç (ESP koruması)", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "HC-SR04 VCC / GND", "pin": "5V / GND"}, {"bilesen": "Trig / Echo", "pin": "D9 / D10"}, {"bilesen": "Buzzer (+)", "pin": "D8"}],
                "kod": "// Uno Park Sensoru\nconst int trig=9, echo=10, buzz=8;\nvoid setup() { pinMode(trig, OUTPUT); pinMode(echo, INPUT); pinMode(buzz, OUTPUT); }\nvoid loop() {\n  digitalWrite(trig, LOW); delayMicroseconds(2); digitalWrite(trig, HIGH); delayMicroseconds(10); digitalWrite(trig, LOW);\n  long s = pulseIn(echo, HIGH, 30000); int d = (s*0.0343)/2;\n  if(d>0 && d<20) { digitalWrite(buzz, HIGH); delay(40); digitalWrite(buzz, LOW); delay(40); }\n}"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "HC-SR04 VCC / GND", "pin": "5V / GND"}, {"bilesen": "Trig / Echo", "pin": "D9 / D10"}, {"bilesen": "Buzzer (+)", "pin": "D8"}],
                "kod": "// Nano Park Sensoru\nconst int trig=9, echo=10, buzz=8;\nvoid setup() { pinMode(trig, OUTPUT); pinMode(echo, INPUT); pinMode(buzz, OUTPUT); }\nvoid loop() {\n  digitalWrite(trig, LOW); delayMicroseconds(2); digitalWrite(trig, HIGH); delayMicroseconds(10); digitalWrite(trig, LOW);\n  long s = pulseIn(echo, HIGH, 30000); int d = (s*0.0343)/2;\n  if(d>0 && d<20) { digitalWrite(buzz, HIGH); delay(40); digitalWrite(buzz, LOW); delay(40); }\n}"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "HC-SR04 VCC / GND", "pin": "VIN (5V) / GND"}, {"bilesen": "Trig / Echo", "pin": "GPIO 5 / GPIO 18 (1k/2k bolucu)"}, {"bilesen": "Buzzer (+)", "pin": "GPIO 19"}],
                "kod": "// ESP32 Park Sensoru (3.3V Korumali)\nconst int trig=5, echo=18, buzz=19;\nvoid setup() { pinMode(trig, OUTPUT); pinMode(echo, INPUT); pinMode(buzz, OUTPUT); }\nvoid loop() {\n  digitalWrite(trig, LOW); delayMicroseconds(2); digitalWrite(trig, HIGH); delayMicroseconds(10); digitalWrite(trig, LOW);\n  long s = pulseIn(echo, HIGH, 30000); int d = (s*0.0343)/2;\n  if(d>0 && d<20) { digitalWrite(buzz, HIGH); delay(40); digitalWrite(buzz, LOW); delay(40); }\n}"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "HC-SR04 VCC / GND", "pin": "VV (5V) / GND"}, {"bilesen": "Trig / Echo", "pin": "D1 / D2 (Bolucu)"}, {"bilesen": "Buzzer (+)", "pin": "D5"}],
                "kod": "// ESP8266 Park Sensoru\nconst int trig=D1, echo=D2, buzz=D5;\nvoid setup() { pinMode(trig, OUTPUT); pinMode(echo, INPUT); pinMode(buzz, OUTPUT); }\nvoid loop() {\n  digitalWrite(trig, LOW); delayMicroseconds(2); digitalWrite(trig, HIGH); delayMicroseconds(10); digitalWrite(trig, LOW);\n  long s = pulseIn(echo, HIGH, 30000); int d = (s*0.0343)/2;\n  if(d>0 && d<20) { digitalWrite(buzz, HIGH); delay(40); digitalWrite(buzz, LOW); delay(40); }\n}"
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
                "baglanti": [{"bilesen": "PIR VCC / GND", "pin": "5V / GND"}, {"bilesen": "PIR OUT", "pin": "D2"}, {"bilesen": "Alarm LED", "pin": "D13"}],
                "kod": "// Uno PIR Alarm\nvoid setup() { pinMode(2, INPUT); pinMode(13, OUTPUT); }\nvoid loop() { digitalWrite(13, digitalRead(2)); }"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "PIR VCC / GND", "pin": "5V / GND"}, {"bilesen": "PIR OUT", "pin": "D2"}, {"bilesen": "Alarm LED", "pin": "D13"}],
                "kod": "// Nano PIR Alarm\nvoid setup() { pinMode(2, INPUT); pinMode(13, OUTPUT); }\nvoid loop() { digitalWrite(13, digitalRead(2)); }"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "PIR VCC / GND", "pin": "VIN (5V) / GND"}, {"bilesen": "PIR OUT", "pin": "GPIO 13"}, {"bilesen": "Alarm LED", "pin": "GPIO 2"}],
                "kod": "// ESP32 PIR Alarm\nvoid setup() { pinMode(13, INPUT); pinMode(2, OUTPUT); }\nvoid loop() { digitalWrite(2, digitalRead(13)); }"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "PIR VCC / GND", "pin": "VV (5V) / GND"}, {"bilesen": "PIR OUT", "pin": "D7"}, {"bilesen": "Alarm LED", "pin": "D4"}],
                "kod": "// ESP8266 PIR Alarm\nvoid setup() { pinMode(D7, INPUT); pinMode(D4, OUTPUT); }\nvoid loop() { digitalWrite(D4, !digitalRead(D7)); }"
            }
        }
    },
    "dht11-sicaklik": {
        "kategori": "Sensörler",
        "baslik": "DHT11 Dijital Sıcaklık & Nem Ölçümü",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "DHT11 Sensörü", "link": ""}, {"adet": "1x", "isim": "10kΩ Pull-up Direnç", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<DHT.h> (Adafruit)",
                "baglanti": [{"bilesen": "DHT11 VCC / GND", "pin": "5V / GND"}, {"bilesen": "DATA", "pin": "D2 (10k pull-up)"}],
                "kod": "#include <DHT.h>\nDHT dht(2, DHT11);\nvoid setup() { Serial.begin(9600); dht.begin(); }\nvoid loop() { delay(2000); Serial.println(dht.readTemperature()); }"
            },
            "nano": {
                "kutuphaneler": "<DHT.h>",
                "baglanti": [{"bilesen": "DHT11 VCC / GND", "pin": "5V / GND"}, {"bilesen": "DATA", "pin": "D2"}],
                "kod": "#include <DHT.h>\nDHT dht(2, DHT11);\nvoid setup() { Serial.begin(9600); dht.begin(); }\nvoid loop() { delay(2000); Serial.println(dht.readTemperature()); }"
            },
            "esp32": {
                "kutuphaneler": "<DHT.h>",
                "baglanti": [{"bilesen": "DHT11 VCC / GND", "pin": "3.3V / GND"}, {"bilesen": "DATA", "pin": "GPIO 4"}],
                "kod": "#include <DHT.h>\nDHT dht(4, DHT11);\nvoid setup() { Serial.begin(115200); dht.begin(); }\nvoid loop() { delay(2000); Serial.println(dht.readTemperature()); }"
            },
            "esp8266": {
                "kutuphaneler": "<DHT.h>",
                "baglanti": [{"bilesen": "DHT11 VCC / GND", "pin": "3.3V / GND"}, {"bilesen": "DATA", "pin": "D4 (GPIO 2)"}],
                "kod": "#include <DHT.h>\nDHT dht(D4, DHT11);\nvoid setup() { Serial.begin(115200); dht.begin(); }\nvoid loop() { delay(2000); Serial.println(dht.readTemperature()); }"
            }
        }
    },
    "tcrt5000-cizgi": {
        "kategori": "Sensörler",
        "baslik": "TCRT5000 Çift Çıkışlı Kızılötesi Çizgi Sensörü",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "TCRT5000 Çizgi Takip Sensörü", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "TCRT5000 VCC / GND", "pin": "5V / GND"}, {"bilesen": "DO (Dijital Çıkış)", "pin": "D2"}, {"bilesen": "LED", "pin": "D13"}],
                "kod": "// Uno Cizgi Takip\nvoid setup() { pinMode(2, INPUT); pinMode(13, OUTPUT); }\nvoid loop() { digitalWrite(13, !digitalRead(2)); }"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "TCRT5000 VCC / GND", "pin": "5V / GND"}, {"bilesen": "DO", "pin": "D2"}, {"bilesen": "LED", "pin": "D13"}],
                "kod": "// Nano Cizgi Takip\nvoid setup() { pinMode(2, INPUT); pinMode(13, OUTPUT); }\nvoid loop() { digitalWrite(13, !digitalRead(2)); }"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "TCRT5000 VCC / GND", "pin": "3.3V / GND"}, {"bilesen": "DO", "pin": "GPIO 4"}, {"bilesen": "LED", "pin": "GPIO 2"}],
                "kod": "// ESP32 Cizgi Takip\nvoid setup() { pinMode(4, INPUT); pinMode(2, OUTPUT); }\nvoid loop() { digitalWrite(2, !digitalRead(4)); }"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "TCRT5000 VCC / GND", "pin": "3.3V / GND"}, {"bilesen": "DO", "pin": "D1"}, {"bilesen": "LED", "pin": "D4"}],
                "kod": "// ESP8266 Cizgi Takip\nvoid setup() { pinMode(D1, INPUT); pinMode(D4, OUTPUT); }\nvoid loop() { digitalWrite(D4, digitalRead(D1)); }"
            }
        }
    },
    "pot-analog-map": {
        "kategori": "Giriş & Kontrol",
        "baslik": "Potansiyometre ile LED Parlaklığı Ayarlama (Map)",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "10kΩ Potansiyometre", "link": ""}, {"adet": "1x", "isim": "LED & 220Ω Direnç", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Pot Orta Bacak", "pin": "A0"}, {"bilesen": "LED Anot (+)", "pin": "D9 (PWM)"}],
                "kod": "// Uno Pot PWM\nvoid setup() { pinMode(9, OUTPUT); }\nvoid loop() { analogWrite(9, map(analogRead(A0), 0, 1023, 0, 255)); delay(10); }"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Pot Orta Bacak", "pin": "A0"}, {"bilesen": "LED Anot (+)", "pin": "D9 (PWM)"}],
                "kod": "// Nano Pot PWM\nvoid setup() { pinMode(9, OUTPUT); }\nvoid loop() { analogWrite(9, map(analogRead(A0), 0, 1023, 0, 255)); delay(10); }"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Pot Orta Bacak", "pin": "GPIO 32 (ADC1)"}, {"bilesen": "LED Anot (+)", "pin": "GPIO 18"}],
                "kod": "// ESP32 Pot PWM\nvoid setup() { ledcAttach(18, 5000, 8); }\nvoid loop() { ledcWrite(18, map(analogRead(32), 0, 4095, 0, 255)); delay(10); }"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Pot Orta Bacak", "pin": "A0"}, {"bilesen": "LED Anot (+)", "pin": "D1"}],
                "kod": "// ESP8266 Pot PWM\nvoid setup() { pinMode(D1, OUTPUT); }\nvoid loop() { analogWrite(D1, analogRead(A0)); delay(10); }"
            }
        }
    },
    "buton-dahili-pullup": {
        "kategori": "Giriş & Kontrol",
        "baslik": "Dahili Pull-up Dirençli Buton Kontrolü",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "Push Buton", "link": ""}, {"adet": "1x", "isim": "Dahili / Harici LED", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Buton Bir Uç", "pin": "D2"}, {"bilesen": "Buton Diğer Uç", "pin": "GND"}, {"bilesen": "LED", "pin": "D13"}],
                "kod": "// Uno INPUT_PULLUP\nvoid setup() { pinMode(2, INPUT_PULLUP); pinMode(13, OUTPUT); }\nvoid loop() { digitalWrite(13, !digitalRead(2)); }"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Buton Bir Uç", "pin": "D2"}, {"bilesen": "Buton Diğer Uç", "pin": "GND"}, {"bilesen": "LED", "pin": "D13"}],
                "kod": "// Nano INPUT_PULLUP\nvoid setup() { pinMode(2, INPUT_PULLUP); pinMode(13, OUTPUT); }\nvoid loop() { digitalWrite(13, !digitalRead(2)); }"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Buton Bir Uç", "pin": "GPIO 4"}, {"bilesen": "Buton Diğer Uç", "pin": "GND"}, {"bilesen": "LED", "pin": "GPIO 2"}],
                "kod": "// ESP32 INPUT_PULLUP\nvoid setup() { pinMode(4, INPUT_PULLUP); pinMode(2, OUTPUT); }\nvoid loop() { digitalWrite(2, !digitalRead(4)); }"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Buton Bir Uç", "pin": "D2 (GPIO 4)"}, {"bilesen": "Buton Diğer Uç", "pin": "GND"}, {"bilesen": "LED", "pin": "D4"}],
                "kod": "// ESP8266 INPUT_PULLUP\nvoid setup() { pinMode(D2, INPUT_PULLUP); pinMode(D4, OUTPUT); }\nvoid loop() { digitalWrite(D4, digitalRead(D2)); }"
            }
        }
    },
    "joystick-analog-kontrol": {
        "kategori": "Giriş & Kontrol",
        "baslik": "Çift Eksenli Analog Joystick Okuma",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "2 Eksenli Joystick Modülü", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "VRx / VRy", "pin": "A0 / A1"}, {"bilesen": "SW (Buton)", "pin": "D2"}],
                "kod": "// Uno Joystick\nvoid setup() { Serial.begin(9600); pinMode(2, INPUT_PULLUP); }\nvoid loop() { Serial.print(\"X: \"); Serial.print(analogRead(A0)); Serial.print(\" Y: \"); Serial.println(analogRead(A1)); delay(200); }"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "VRx / VRy", "pin": "A0 / A1"}, {"bilesen": "SW", "pin": "D2"}],
                "kod": "// Nano Joystick\nvoid setup() { Serial.begin(9600); pinMode(2, INPUT_PULLUP); }\nvoid loop() { Serial.print(\"X: \"); Serial.print(analogRead(A0)); Serial.print(\" Y: \"); Serial.println(analogRead(A1)); delay(200); }"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "VRx / VRy", "pin": "GPIO 34 / 35"}, {"bilesen": "SW", "pin": "GPIO 15"}],
                "kod": "// ESP32 Joystick\nvoid setup() { Serial.begin(115200); pinMode(15, INPUT_PULLUP); }\nvoid loop() { Serial.print(\"X: \"); Serial.print(analogRead(34)); Serial.print(\" Y: \"); Serial.println(analogRead(35)); delay(200); }"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "VRx", "pin": "A0 (Tek ADC)"}, {"bilesen": "SW", "pin": "D2"}],
                "kod": "// ESP8266 Tek Eksen\nvoid setup() { Serial.begin(115200); }\nvoid loop() { Serial.println(analogRead(A0)); delay(200); }"
            }
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
                "baglanti": [{"bilesen": "Röle IN", "pin": "D7"}, {"bilesen": "VCC / GND", "pin": "5V / GND"}],
                "kod": "// Uno Role\nvoid setup() { pinMode(7, OUTPUT); }\nvoid loop() { digitalWrite(7, LOW); delay(2000); digitalWrite(7, HIGH); delay(2000); }"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Röle IN", "pin": "D7"}, {"bilesen": "VCC / GND", "pin": "5V / GND"}],
                "kod": "// Nano Role\nvoid setup() { pinMode(7, OUTPUT); }\nvoid loop() { digitalWrite(7, LOW); delay(2000); digitalWrite(7, HIGH); delay(2000); }"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Röle IN", "pin": "GPIO 19"}, {"bilesen": "VCC / GND", "pin": "VIN (5V) / GND"}],
                "kod": "// ESP32 Role\nvoid setup() { pinMode(19, OUTPUT); }\nvoid loop() { digitalWrite(19, LOW); delay(2000); digitalWrite(19, HIGH); delay(2000); }"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Röle IN", "pin": "D1"}, {"bilesen": "VCC / GND", "pin": "VV (5V) / GND"}],
                "kod": "// ESP8266 Role\nvoid setup() { pinMode(D1, OUTPUT); }\nvoid loop() { digitalWrite(D1, LOW); delay(2000); digitalWrite(D1, HIGH); delay(2000); }"
            }
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
                "baglanti": [{"bilesen": "Servo Sinyal (Turuncu)", "pin": "D9"}, {"bilesen": "Besleme (Kırmızı/Kahve)", "pin": "5V / GND"}],
                "kod": "#include <Servo.h>\nServo s;\nvoid setup() { s.attach(9); }\nvoid loop() { s.write(0); delay(1000); s.write(90); delay(1000); s.write(180); delay(1000); }"
            },
            "nano": {
                "kutuphaneler": "<Servo.h>",
                "baglanti": [{"bilesen": "Servo Sinyal", "pin": "D9"}, {"bilesen": "Besleme", "pin": "5V / GND"}],
                "kod": "#include <Servo.h>\nServo s;\nvoid setup() { s.attach(9); }\nvoid loop() { s.write(0); delay(1000); s.write(90); delay(1000); s.write(180); delay(1000); }"
            },
            "esp32": {
                "kutuphaneler": "<ESP32Servo.h>",
                "baglanti": [{"bilesen": "Servo Sinyal", "pin": "GPIO 18"}, {"bilesen": "Besleme", "pin": "VIN (5V) / GND"}],
                "kod": "#include <ESP32Servo.h>\nServo s;\nvoid setup() { s.attach(18); }\nvoid loop() { s.write(0); delay(1000); s.write(90); delay(1000); s.write(180); delay(1000); }"
            },
            "esp8266": {
                "kutuphaneler": "<Servo.h>",
                "baglanti": [{"bilesen": "Servo Sinyal", "pin": "D4"}, {"bilesen": "Besleme", "pin": "VV (5V) / GND"}],
                "kod": "#include <Servo.h>\nServo s;\nvoid setup() { s.attach(D4); }\nvoid loop() { s.write(0); delay(1000); s.write(90); delay(1000); s.write(180); delay(1000); }"
            }
        }
    },
    "l298n-dc-motor": {
        "kategori": "Motor & Güç",
        "baslik": "L298N Sürücü ile Çift Yönlü DC Motor & Hız Kontrolü",
        "zorluk": "İleri",
        "sure": "20 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "L298N Sürücü", "link": ""}, {"adet": "1x", "isim": "DC Motor", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "ENA (Hız)", "pin": "D5 (PWM)"}, {"bilesen": "IN1 / IN2", "pin": "D6 / D7"}],
                "kod": "// Uno L298N\nvoid setup() { pinMode(5, OUTPUT); pinMode(6, OUTPUT); pinMode(7, OUTPUT); }\nvoid loop() { digitalWrite(6, HIGH); digitalWrite(7, LOW); analogWrite(5, 200); delay(2000); }"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "ENA / IN1 / IN2", "pin": "D5 / D6 / D7"}],
                "kod": "// Nano L298N\nvoid setup() { pinMode(5, OUTPUT); pinMode(6, OUTPUT); pinMode(7, OUTPUT); }\nvoid loop() { digitalWrite(6, HIGH); digitalWrite(7, LOW); analogWrite(5, 200); delay(2000); }"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "ENA (Hız)", "pin": "GPIO 18"}, {"bilesen": "IN1 / IN2", "pin": "GPIO 19 / 21"}],
                "kod": "// ESP32 L298N\nvoid setup() { pinMode(19, OUTPUT); pinMode(21, OUTPUT); ledcAttach(18, 5000, 8); }\nvoid loop() { digitalWrite(19, HIGH); digitalWrite(21, LOW); ledcWrite(18, 200); delay(2000); }"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "ENA / IN1 / IN2", "pin": "D1 / D2 / D5"}],
                "kod": "// ESP8266 L298N\nvoid setup() { pinMode(D1, OUTPUT); pinMode(D2, OUTPUT); pinMode(D5, OUTPUT); }\nvoid loop() { digitalWrite(D2, HIGH); digitalWrite(D5, LOW); analogWrite(D1, 800); delay(2000); }"
            }
        }
    },
    "i2c-1602-lcd": {
        "kategori": "Ekranlar",
        "baslik": "I2C 1602 Karakter LCD Ekran Metin Yazdırma",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "1602 LCD + I2C Sırtlığı", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<LiquidCrystal_I2C.h>",
                "baglanti": [{"bilesen": "SDA / SCL", "pin": "A4 / A5"}, {"bilesen": "VCC / GND", "pin": "5V / GND"}],
                "kod": "#include <Wire.h>\n#include <LiquidCrystal_I2C.h>\nLiquidCrystal_I2C lcd(0x27, 16, 2);\nvoid setup() { lcd.init(); lcd.backlight(); lcd.print(\"ArduKod Uno\"); }\nvoid loop() {}"
            },
            "nano": {
                "kutuphaneler": "<LiquidCrystal_I2C.h>",
                "baglanti": [{"bilesen": "SDA / SCL", "pin": "A4 / A5"}, {"bilesen": "VCC / GND", "pin": "5V / GND"}],
                "kod": "#include <Wire.h>\n#include <LiquidCrystal_I2C.h>\nLiquidCrystal_I2C lcd(0x27, 16, 2);\nvoid setup() { lcd.init(); lcd.backlight(); lcd.print(\"ArduKod Nano\"); }\nvoid loop() {}"
            },
            "esp32": {
                "kutuphaneler": "<LiquidCrystal_I2C.h>",
                "baglanti": [{"bilesen": "SDA / SCL", "pin": "GPIO 21 / GPIO 22"}, {"bilesen": "VCC / GND", "pin": "VIN (5V) / GND"}],
                "kod": "#include <Wire.h>\n#include <LiquidCrystal_I2C.h>\nLiquidCrystal_I2C lcd(0x27, 16, 2);\nvoid setup() { Wire.begin(21, 22); lcd.init(); lcd.backlight(); lcd.print(\"ArduKod ESP32\"); }\nvoid loop() {}"
            },
            "esp8266": {
                "kutuphaneler": "<LiquidCrystal_I2C.h>",
                "baglanti": [{"bilesen": "SDA / SCL", "pin": "D2 (GPIO 4) / D1 (GPIO 5)"}, {"bilesen": "VCC / GND", "pin": "VV (5V) / GND"}],
                "kod": "#include <Wire.h>\n#include <LiquidCrystal_I2C.h>\nLiquidCrystal_I2C lcd(0x27, 16, 2);\nvoid setup() { Wire.begin(D2, D1); lcd.init(); lcd.backlight(); lcd.print(\"ArduKod ESP8266\"); }\nvoid loop() {}"
            }
        }
    },
    "ssd1306-oled": {
        "kategori": "Ekranlar",
        "baslik": "0.96 inç I2C SSD1306 OLED Grafik Ekran",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "0.96 OLED Ekran", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<Adafruit_SSD1306.h>, <Adafruit_GFX.h>",
                "baglanti": [{"bilesen": "SDA / SCL", "pin": "A4 / A5"}, {"bilesen": "VCC / GND", "pin": "5V / GND"}],
                "kod": "#include <Wire.h>\n#include <Adafruit_SSD1306.h>\nAdafruit_SSD1306 oled(128, 64, &Wire, -1);\nvoid setup() { oled.begin(SSD1306_SWITCHCAPVCC, 0x3C); oled.clearDisplay(); oled.setTextColor(WHITE); oled.setCursor(0,0); oled.println(\"ArduKod OLED\"); oled.display(); }\nvoid loop() {}"
            },
            "nano": {
                "kutuphaneler": "<Adafruit_SSD1306.h>",
                "baglanti": [{"bilesen": "SDA / SCL", "pin": "A4 / A5"}, {"bilesen": "VCC / GND", "pin": "5V / GND"}],
                "kod": "#include <Wire.h>\n#include <Adafruit_SSD1306.h>\nAdafruit_SSD1306 oled(128, 64, &Wire, -1);\nvoid setup() { oled.begin(SSD1306_SWITCHCAPVCC, 0x3C); oled.clearDisplay(); oled.setTextColor(WHITE); oled.setCursor(0,0); oled.println(\"ArduKod OLED\"); oled.display(); }\nvoid loop() {}"
            },
            "esp32": {
                "kutuphaneler": "<Adafruit_SSD1306.h>",
                "baglanti": [{"bilesen": "SDA / SCL", "pin": "GPIO 21 / GPIO 22"}, {"bilesen": "VCC / GND", "pin": "3.3V / GND"}],
                "kod": "#include <Wire.h>\n#include <Adafruit_SSD1306.h>\nAdafruit_SSD1306 oled(128, 64, &Wire, -1);\nvoid setup() { Wire.begin(21, 22); oled.begin(SSD1306_SWITCHCAPVCC, 0x3C); oled.clearDisplay(); oled.setTextColor(WHITE); oled.setCursor(0,0); oled.println(\"ESP32 OLED\"); oled.display(); }\nvoid loop() {}"
            },
            "esp8266": {
                "kutuphaneler": "<Adafruit_SSD1306.h>",
                "baglanti": [{"bilesen": "SDA / SCL", "pin": "D2 / D1"}, {"bilesen": "VCC / GND", "pin": "3.3V / GND"}],
                "kod": "#include <Wire.h>\n#include <Adafruit_SSD1306.h>\nAdafruit_SSD1306 oled(128, 64, &Wire, -1);\nvoid setup() { Wire.begin(D2, D1); oled.begin(SSD1306_SWITCHCAPVCC, 0x3C); oled.clearDisplay(); oled.setTextColor(WHITE); oled.setCursor(0,0); oled.println(\"ESP8266 OLED\"); oled.display(); }\nvoid loop() {}"
            }
        }
    },
    "max7219-dot-matrix": {
        "kategori": "Ekranlar",
        "baslik": "MAX7219 8x8 Kırmızı LED Dot Matrix Modülü",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "MAX7219 Dot Matrix", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<LedControl.h>",
                "baglanti": [{"bilesen": "DIN / CS / CLK", "pin": "D12 / D10 / D11"}],
                "kod": "#include <LedControl.h>\nLedControl lc(12, 11, 10, 1);\nvoid setup() { lc.shutdown(0,false); lc.setIntensity(0,8); lc.clearDisplay(0); lc.setLed(0,3,3,true); }\nvoid loop() {}"
            },
            "nano": {
                "kutuphaneler": "<LedControl.h>",
                "baglanti": [{"bilesen": "DIN / CS / CLK", "pin": "D12 / D10 / D11"}],
                "kod": "#include <LedControl.h>\nLedControl lc(12, 11, 10, 1);\nvoid setup() { lc.shutdown(0,false); lc.setIntensity(0,8); lc.clearDisplay(0); lc.setLed(0,3,3,true); }\nvoid loop() {}"
            },
            "esp32": {
                "kutuphaneler": "<LedControl.h>",
                "baglanti": [{"bilesen": "DIN / CS / CLK", "pin": "GPIO 23 / 5 / 18"}],
                "kod": "#include <LedControl.h>\nLedControl lc(23, 18, 5, 1);\nvoid setup() { lc.shutdown(0,false); lc.setIntensity(0,8); lc.clearDisplay(0); lc.setLed(0,3,3,true); }\nvoid loop() {}"
            },
            "esp8266": {
                "kutuphaneler": "<LedControl.h>",
                "baglanti": [{"bilesen": "DIN / CS / CLK", "pin": "D7 / D8 / D5"}],
                "kod": "#include <LedControl.h>\nLedControl lc(D7, D5, D8, 1);\nvoid setup() { lc.shutdown(0,false); lc.setIntensity(0,8); lc.clearDisplay(0); lc.setLed(0,3,3,true); }\nvoid loop() {}"
            }
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
                "baglanti": [{"bilesen": "Buzzer (+)", "pin": "D8"}, {"bilesen": "Buzzer (-)", "pin": "GND"}],
                "kod": "// Uno Buzzer Ton\nvoid setup() {}\nvoid loop() { tone(8, 440, 200); delay(300); tone(8, 880, 200); delay(500); }"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Buzzer (+)", "pin": "D8"}, {"bilesen": "Buzzer (-)", "pin": "GND"}],
                "kod": "// Nano Buzzer Ton\nvoid setup() {}\nvoid loop() { tone(8, 440, 200); delay(300); tone(8, 880, 200); delay(500); }"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Buzzer (+)", "pin": "GPIO 18"}, {"bilesen": "Buzzer (-)", "pin": "GND"}],
                "kod": "// ESP32 Donanimsal Ton\nvoid setup() { ledcAttach(18, 2000, 8); }\nvoid loop() { ledcWriteTone(18, 440); delay(300); ledcWriteTone(18, 880); delay(500); }"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Buzzer (+)", "pin": "D5"}, {"bilesen": "Buzzer (-)", "pin": "GND"}],
                "kod": "// ESP8266 Ton\nvoid setup() {}\nvoid loop() { tone(D5, 440, 200); delay(300); tone(D5, 880, 200); delay(500); }"
            }
        }
    },
    "rc522-rfid": {
        "kategori": "Haberleşme & IoT",
        "baslik": "RC522 13.56MHz RFID Kart Okuyucu",
        "zorluk": "İleri",
        "sure": "20 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "RC522 RFID Modülü & Kart", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<MFRC522.h>, <SPI.h>",
                "baglanti": [{"bilesen": "SDA / SCK / MOSI / MISO / RST", "pin": "D10 / D13 / D11 / D12 / D9"}],
                "kod": "#include <SPI.h>\n#include <MFRC522.h>\nMFRC522 rfid(10, 9);\nvoid setup() { Serial.begin(9600); SPI.begin(); rfid.PCD_Init(); }\nvoid loop() { if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) { Serial.println(\"Kart Okundu!\"); rfid.PICC_HaltA(); } }"
            },
            "nano": {
                "kutuphaneler": "<MFRC522.h>, <SPI.h>",
                "baglanti": [{"bilesen": "SDA / SCK / MOSI / MISO / RST", "pin": "D10 / D13 / D11 / D12 / D9"}],
                "kod": "#include <SPI.h>\n#include <MFRC522.h>\nMFRC522 rfid(10, 9);\nvoid setup() { Serial.begin(9600); SPI.begin(); rfid.PCD_Init(); }\nvoid loop() { if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) { Serial.println(\"Kart Okundu!\"); rfid.PICC_HaltA(); } }"
            },
            "esp32": {
                "kutuphaneler": "<MFRC522.h>, <SPI.h>",
                "baglanti": [{"bilesen": "SDA / SCK / MOSI / MISO / RST", "pin": "GPIO 5 / 18 / 23 / 19 / 22"}],
                "kod": "#include <SPI.h>\n#include <MFRC522.h>\nMFRC522 rfid(5, 22);\nvoid setup() { Serial.begin(115200); SPI.begin(); rfid.PCD_Init(); }\nvoid loop() { if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) { Serial.println(\"ESP32 Kart Okundu!\"); rfid.PICC_HaltA(); } }"
            },
            "esp8266": {
                "kutuphaneler": "<MFRC522.h>, <SPI.h>",
                "baglanti": [{"bilesen": "SDA / SCK / MOSI / MISO / RST", "pin": "D8 / D5 / D7 / D6 / D3"}],
                "kod": "#include <SPI.h>\n#include <MFRC522.h>\nMFRC522 rfid(D8, D3);\nvoid setup() { Serial.begin(115200); SPI.begin(); rfid.PCD_Init(); }\nvoid loop() { if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) { Serial.println(\"NodeMCU Kart Okundu!\"); rfid.PICC_HaltA(); } }"
            }
        }
    },
    "esp-wifi-web-server": {
        "kategori": "Haberleşme & IoT",
        "baslik": "Wi-Fi Web Server ile Tarayıcıdan LED Kontrolü",
        "zorluk": "İleri",
        "sure": "20 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [{"adet": "1x", "isim": "ESP32 veya NodeMCU", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici Wi-Fi shield gerektirir.",
                "baglanti": [{"bilesen": "Dahili Wi-Fi", "pin": "Bulunmuyor (ESP kartlarını seçin)"}],
                "kod": "// Arduino Uno tek basina Wi-Fi desteklemez.\n// ESP32 veya ESP8266 kartini seciniz."
            },
            "nano": {
                "kutuphaneler": "Harici Wi-Fi modülü gerektirir.",
                "baglanti": [{"bilesen": "Dahili Wi-Fi", "pin": "Bulunmuyor"}],
                "kod": "// Arduino Nano tek basina Wi-Fi desteklemez.\n// ESP32 veya ESP8266 kartini seciniz."
            },
            "esp32": {
                "kutuphaneler": "<WiFi.h>, <WebServer.h>",
                "baglanti": [{"bilesen": "LED", "pin": "GPIO 2 (Dahili LED)"}],
                "kod": "#include <WiFi.h>\n#include <WebServer.h>\nWebServer server(80);\nvoid setup() {\n  Serial.begin(115200); pinMode(2, OUTPUT);\n  WiFi.begin(\"WIFI_ADI\", \"SIFRE\");\n  while(WiFi.status() != WL_CONNECTED) delay(500);\n  Serial.println(WiFi.localIP());\n  server.on(\"/on\", []() { digitalWrite(2, HIGH); server.send(200, \"text/plain\", \"ACIK\"); });\n  server.on(\"/off\", []() { digitalWrite(2, LOW); server.send(200, \"text/plain\", \"KAPALI\"); });\n  server.begin();\n}\nvoid loop() { server.handleClient(); }"
            },
            "esp8266": {
                "kutuphaneler": "<ESP8266WiFi.h>, <ESP8266WebServer.h>",
                "baglanti": [{"bilesen": "LED", "pin": "D4 (Dahili LED)"}],
                "kod": "#include <ESP8266WiFi.h>\n#include <ESP8266WebServer.h>\nESP8266WebServer server(80);\nvoid setup() {\n  Serial.begin(115200); pinMode(D4, OUTPUT);\n  WiFi.begin(\"WIFI_ADI\", \"SIFRE\");\n  while(WiFi.status() != WL_CONNECTED) delay(500);\n  Serial.println(WiFi.localIP());\n  server.on(\"/on\", []() { digitalWrite(D4, LOW); server.send(200, \"text/plain\", \"ACIK\"); });\n  server.on(\"/off\", []() { digitalWrite(D4, HIGH); server.send(200, \"text/plain\", \"KAPALI\"); });\n  server.begin();\n}\nvoid loop() { server.handleClient(); }"
            }
        }
    }
}

# --- JSON YARDIMCI FONKSİYONLARI ---
def veri_yukle():
    if not os.path.exists(VERI_DOSYASI):
        with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(VARSAYILAN_PROJELER, f, ensure_ascii=False, indent=2)
        return VARSAYILAN_PROJELER
    try:
        with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
            d = json.load(f)
            # Eğer eksik kalmışsa 20 varsayılan projeyi tamamla
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
    if not os.path.exists(ISTEK_DOSYASI):
        return []
    try:
        with open(ISTEK_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def istek_kaydet(istekler):
    with open(ISTEK_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(istekler, f, ensure_ascii=False, indent=2)

# --- SİTE ÖNYÜZ ROTALARI ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projeler', methods=['GET'])
def projeleri_getir():
    projeler = veri_yukle()
    liste = []
    for anahtar, detay in projeler.items():
        liste.append({
            "id": anahtar,
            "baslik": detay.get("baslik", anahtar),
            "kategori": detay.get("kategori", "Genel"),
            "zorluk": detay.get("zorluk", "Başlangıç"),
            "sure": detay.get("sure", "10 Dk")
        })
    return jsonify(liste)

@app.route('/proje/<id>', methods=['GET'])
def tek_proje_getir(id):
    projeler = veri_yukle()
    if id in projeler:
        projeler[id]["goruntulenme"] = projeler[id].get("goruntulenme", 0) + 1
        veri_kaydet(projeler)
        return jsonify({"durum": "basarili", "veri": projeler[id]})
    ilk = list(projeler.values())[0]
    return jsonify({"durum": "basarili", "veri": ilk})

@app.route('/proje/<id>/indir', methods=['POST'])
def indirme_say(id):
    projeler = veri_yukle()
    if id in projeler:
        projeler[id]["indirme"] = projeler[id].get("indirme", 0) + 1
        veri_kaydet(projeler)
        return jsonify({"durum": "ok"})
    return jsonify({"durum": "hata"}), 404

@app.route('/istek-gonder', methods=['POST'])
def istek_gonder():
    data = request.get_json() or {}
    mesaj = data.get("mesaj", "").strip()
    iletisim = data.get("iletisim", "").strip()
    if not mesaj:
        return jsonify({"durum": "hata", "mesaj": "Mesaj boş olamaz."}), 400
    istekler = istek_yukle()
    istekler.append({"mesaj": mesaj, "iletisim": iletisim})
    istek_kaydet(istekler)
    return jsonify({"durum": "basarili", "mesaj": "Geri bildiriminiz iletildi!"})

# ==============================================================================
# TAM YETKİLİ ADMİN PANELİ (Giriş, CRUD, Linkler, Kodlar, İstatistikler)
# ==============================================================================
ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head><title>ArduKod - Yönetici Girişi</title>
<style>
body{background:#0d1117;color:#fff;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;}
.box{background:#161b22;border:1px solid #30363d;padding:30px;border-radius:8px;width:320px;text-align:center;}
input{width:100%;box-sizing:border-box;padding:10px;margin:15px 0;background:#0d1117;border:1px solid #30363d;color:#fff;border-radius:6px;outline:none;}
button{width:100%;padding:10px;background:#00979d;border:none;color:#fff;font-weight:bold;border-radius:6px;cursor:pointer;}
</style></head>
<body>
<div class="box">
  <h2>⚡ ArduKod Admin</h2>
  <form method="POST">
    <input type="password" name="sifre" placeholder="Yönetici Şifresi (admin123)" required autofocus>
    <button type="submit">Giriş Yap</button>
  </form>
  {% if hata %}<p style="color:#f85149;margin-top:10px;">{{ hata }}</p>{% endif %}
</div>
</body></html>
"""

ADMIN_PANEL_HTML = """
<!DOCTYPE html>
<html>
<head><title>ArduKod - Tam Yetkili Yönetim Paneli</title>
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
  <h2>⚡ ArduKod Tam Yetkili Yönetim</h2>
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
  <div class="card">Gelen Mesajlar: <div class="num">{{ istekler|length }}</div></div>
</div>

<h3>📦 Proje & Malzeme Linki Yönetimi</h3>
<table>
  <thead><tr><th>ID</th><th>Başlık</th><th>Kategori</th><th>Görüntülenme</th><th>İndirme</th><th>İşlemler</th></tr></thead>
  <tbody>
    {% for pid, p in projeler.items() %}
    <tr>
      <td><code>{{ pid }}</code></td>
      <td><b>{{ p.baslik }}</b></td>
      <td>{{ p.kategori }}</td>
      <td>{{ p.goruntulenme or 0 }}</td>
      <td>{{ p.indirme or 0 }}</td>
      <td>
        <button class="btn btn-blue" onclick='duzenleModal({{ pid|tojson }}, {{ p|tojson }})'>Düzenle / Kod / Link</button>
        <button class="btn btn-red" onclick="sil('{{ pid }}')">Sil</button>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<h3 style="margin-top:30px;">📩 Ziyaretçi Mesajları & Kod İstekleri</h3>
<table>
  <thead><tr><th>Mesaj</th><th>İletişim</th><th>İşlem</th></tr></thead>
  <tbody>
    {% for i in istekler %}
    <tr>
      <td>{{ i.mesaj }}</td>
      <td>{{ i.iletisim or '-' }}</td>
      <td><button class="btn btn-red" onclick="istekSil({{ loop.index0 }})">Sil</button></td>
    </tr>
    {% else %}
    <tr><td colspan="3" style="color:#8b949e;">Henüz bir geri bildirim gelmedi.</td></tr>
    {% endfor %}
  </tbody>
</table>

<!-- PROJE EKLEME / DÜZENLEME PENCERESİ -->
<div id="pModal" class="modal">
  <div class="modal-content">
    <h3 id="mTitle">Proje Yönetimi</h3>
    <label>Proje ID (Benzersiz):</label>
    <input type="text" id="f_id">

    <label>Başlık:</label>
    <input type="text" id="f_baslik">

    <div style="display:flex;gap:10px;">
      <div style="flex:1;"><label>Kategori:</label><input type="text" id="f_kategori"></div>
      <div style="flex:1;"><label>Zorluk:</label><input type="text" id="f_zorluk"></div>
      <div style="flex:1;"><label>Süre:</label><input type="text" id="f_sure"></div>
    </div>

    <h4>🔗 Malzemeler & Satın Alma Linkleri</h4>
    <div id="malzemeListesi"></div>
    <button type="button" class="btn btn-blue" onclick="malzemeSatiriEkle()" style="margin-bottom:15px;">+ Malzeme Ekle</button>

    <h4>💻 4 Kartın C++ Kodları</h4>
    <label>Arduino Uno Kodu:</label><textarea id="f_kod_uno" rows="4"></textarea>
    <label>Arduino Nano Kodu:</label><textarea id="f_kod_nano" rows="4"></textarea>
    <label>ESP32 Kodu:</label><textarea id="f_kod_esp32" rows="4"></textarea>
    <label>ESP8266 Kodu:</label><textarea id="f_kod_esp8266" rows="4"></textarea>

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
  malzemeSatiriEkle("1x", "Yeni Sensör", "https://...");
  document.getElementById('pModal').style.display = 'flex';
}

function duzenleModal(pid, p) {
  aktifProjeData = p;
  document.getElementById('mTitle').innerText = "Projeyi Düzenle: " + p.baslik;
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
    uno: { baglanti: [{"bilesen":"VCC/GND","pin":"5V/GND"}], kutuphaneler: "Harici kütüphane gerekmez." },
    nano: { baglanti: [{"bilesen":"VCC/GND","pin":"5V/GND"}], kutuphaneler: "Harici kütüphane gerekmez." },
    esp32: { baglanti: [{"bilesen":"VCC/GND","pin":"3.3V/GND"}], kutuphaneler: "Harici kütüphane gerekmez." },
    esp8266: { baglanti: [{"bilesen":"VCC/GND","pin":"3.3V/GND"}], kutuphaneler: "Harici kütüphane gerekmez." }
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
  const d = await res.json();
  if(d.durum === 'basarili') { alert('Proje başarıyla kaydedildi!'); location.reload(); }
  else { alert('Hata oluştu!'); }
}

async function sil(pid) {
  if(!confirm(pid + ' projesini silmek istediğinize emin misiniz?')) return;
  await fetch('/admin/proje-sil/' + pid, { method: 'POST' });
  location.reload();
}

async function istekSil(idx) {
  await fetch('/admin/istek-sil/' + idx, { method: 'POST' });
  location.reload();
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
    projeler = veri_yukle()
    istekler = istek_yukle()
    g_toplam = sum(p.get("goruntulenme", 0) for p in projeler.values())
    i_toplam = sum(p.get("indirme", 0) for p in projeler.values())
    return render_template_string(ADMIN_PANEL_HTML, projeler=projeler, istekler=istekler, goruntulenme=g_toplam, indirme=i_toplam)

@app.route('/admin/proje-kaydet', methods=['POST'])
def admin_proje_kaydet():
    if not session.get("admin"):
        return jsonify({"durum": "yetkisiz"}), 403
    d = request.get_json() or {}
    pid = d.get("id")
    if not pid:
        return jsonify({"durum": "hata"}), 400
    
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
    if not session.get("admin"):
        return jsonify({"durum": "yetkisiz"}), 403
    projeler = veri_yukle()
    if id in projeler:
        del projeler[id]
        veri_kaydet(projeler)
        return jsonify({"durum": "basarili"})
    return jsonify({"durum": "hata"}), 404

@app.route('/admin/istek-sil/<int:idx>', methods=['POST'])
def admin_istek_sil(idx):
    if not session.get("admin"):
        return jsonify({"durum": "yetkisiz"}), 403
    istekler = istek_yukle()
    if 0 <= idx < len(istekler):
        istekler.pop(idx)
        istek_kaydet(istekler)
        return jsonify({"durum": "basarili"})
    return jsonify({"durum": "hata"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
