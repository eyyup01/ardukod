import os
import json
from flask import Flask, request, jsonify, session, redirect, render_template_string

app = Flask(__name__)
app.secret_key = "ardukod_tam_surum_stabil_2026"
ADMIN_SIFRE = "admin123"

# ==============================================================================
# 20 PROJENİN TAMAMI (EKSİKSİZ, DOĞRULANMIŞ C++ KODLARI & PİN TABLOLARI)
# ==============================================================================
PROJELER = {
    "kara-simsek": {
        "kategori": "Temel & LED",
        "baslik": "5 LED Kademeli Kara Şimşek (Knight Rider)",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "5x", "isim": "5mm Parlak LED", "link": "https://www.direnc.net"},
            {"adet": "5x", "isim": "220Ω / 330Ω Direnç", "link": "https://www.direnc.net"},
            {"adet": "1x", "isim": "Breadboard", "link": "https://www.direnc.net"},
            {"adet": "6x", "isim": "Erkek-Erkek Jumper", "link": "https://www.direnc.net"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "GND"}
                ],
                "kod": "/* ArduKod - 5 LED Kara Simsek (Uno) */\nconst int pinler[] = {2, 3, 4, 5, 6};\nconst int adet = 5;\nvoid setup() {\n  for(int i=0; i<adet; i++) pinMode(pinler[i], OUTPUT);\n}\nvoid loop() {\n  for(int i=0; i<adet; i++) { digitalWrite(pinler[i], HIGH); delay(50); digitalWrite(pinler[i], LOW); }\n  for(int i=adet-2; i>0; i--) { digitalWrite(pinler[i], HIGH); delay(50); digitalWrite(pinler[i], LOW); }\n}"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "Nano GND"}
                ],
                "kod": "/* ArduKod - 5 LED Kara Simsek (Nano) */\nconst int pinler[] = {2, 3, 4, 5, 6};\nconst int adet = 5;\nvoid setup() {\n  for(int i=0; i<adet; i++) pinMode(pinler[i], OUTPUT);\n}\nvoid loop() {\n  for(int i=0; i<adet; i++) { digitalWrite(pinler[i], HIGH); delay(50); digitalWrite(pinler[i], LOW); }\n  for(int i=adet-2; i>0; i--) { digitalWrite(pinler[i], HIGH); delay(50); digitalWrite(pinler[i], LOW); }\n}"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "GPIO 18, 19, 21, 22, 23 (330Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "ESP32 GND"}
                ],
                "kod": "/* ArduKod - 5 LED Kara Simsek (ESP32) */\nconst int pinler[] = {18, 19, 21, 22, 23};\nconst int adet = 5;\nvoid setup() {\n  for(int i=0; i<adet; i++) pinMode(pinler[i], OUTPUT);\n}\nvoid loop() {\n  for(int i=0; i<adet; i++) { digitalWrite(pinler[i], HIGH); delay(50); digitalWrite(pinler[i], LOW); }\n  for(int i=adet-2; i>0; i--) { digitalWrite(pinler[i], HIGH); delay(50); digitalWrite(pinler[i], LOW); }\n}"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D1, D2, D5, D6, D7 (GPIO 5,4,14,12,13)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "NodeMCU GND"}
                ],
                "kod": "/* ArduKod - 5 LED Kara Simsek (ESP8266) */\nconst int pinler[] = {D1, D2, D5, D6, D7};\nconst int adet = 5;\nvoid setup() {\n  for(int i=0; i<adet; i++) pinMode(pinler[i], OUTPUT);\n}\nvoid loop() {\n  for(int i=0; i<adet; i++) { digitalWrite(pinler[i], HIGH); delay(50); digitalWrite(pinler[i], LOW); }\n  for(int i=adet-2; i>0; i--) { digitalWrite(pinler[i], HIGH); delay(50); digitalWrite(pinler[i], LOW); }\n}"
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
            {"adet": "3x", "isim": "220Ω Direnç", "link": ""},
            {"adet": "4x", "isim": "Jumper Kablo", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "D9 / D10 / D11 (PWM)"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": "const int r=9, g=10, b=11;\nvoid setup(){ pinMode(r,OUTPUT); pinMode(g,OUTPUT); pinMode(b,OUTPUT); }\nvoid loop(){\n  for(int i=0; i<255; i++){ analogWrite(r,i); analogWrite(g,255-i); delay(5); }\n  for(int i=0; i<255; i++){ analogWrite(g,i); analogWrite(b,255-i); delay(5); }\n  for(int i=0; i<255; i++){ analogWrite(b,i); analogWrite(r,255-i); delay(5); }\n}"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "D9 / D10 / D11 (PWM)"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": "const int r=9, g=10, b=11;\nvoid setup(){ pinMode(r,OUTPUT); pinMode(g,OUTPUT); pinMode(b,OUTPUT); }\nvoid loop(){\n  for(int i=0; i<255; i++){ analogWrite(r,i); analogWrite(g,255-i); delay(5); }\n  for(int i=0; i<255; i++){ analogWrite(g,i); analogWrite(b,255-i); delay(5); }\n  for(int i=0; i<255; i++){ analogWrite(b,i); analogWrite(r,255-i); delay(5); }\n}"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "GPIO 18 / 19 / 21"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": "const int r=18, g=19, b=21;\nvoid setup(){\n  ledcAttach(r, 5000, 8); ledcAttach(g, 5000, 8); ledcAttach(b, 5000, 8);\n}\nvoid loop(){\n  for(int i=0; i<255; i++){ ledcWrite(r,i); ledcWrite(g,255-i); delay(5); }\n  for(int i=0; i<255; i++){ ledcWrite(g,i); ledcWrite(b,255-i); delay(5); }\n  for(int i=0; i<255; i++){ ledcWrite(b,i); ledcWrite(r,255-i); delay(5); }\n}"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "D1 / D2 / D5"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": "const int r=D1, g=D2, b=D5;\nvoid setup(){ pinMode(r,OUTPUT); pinMode(g,OUTPUT); pinMode(b,OUTPUT); }\nvoid loop(){\n  for(int i=0; i<1023; i+=5){ analogWrite(r,i); analogWrite(g,1023-i); delay(5); }\n  for(int i=0; i<1023; i+=5){ analogWrite(g,i); analogWrite(b,1023-i); delay(5); }\n  for(int i=0; i<1023; i+=5){ analogWrite(b,i); analogWrite(r,1023-i); delay(5); }\n}"
            }
        }
    },
    "trafik-isiklari": {
        "kategori": "Temel & LED",
        "baslik": "Zaman Ayarlı Standart Trafik Işıkları",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [{"adet": "3x", "isim": "Kırmızı, Sarı, Yeşil LED", "link": ""}, {"adet": "3x", "isim": "220Ω Direnç", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Kırmızı/Sarı/Yeşil", "pin": "D2 / D3 / D4"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": "const int k=2, s=3, y=4;\nvoid setup(){ pinMode(k,OUTPUT); pinMode(s,OUTPUT); pinMode(y,OUTPUT); }\nvoid loop(){\n  digitalWrite(k,HIGH); delay(4000); digitalWrite(s,HIGH); delay(1000);\n  digitalWrite(k,LOW); digitalWrite(s,LOW); digitalWrite(y,HIGH); delay(4000);\n  digitalWrite(y,LOW); digitalWrite(s,HIGH); delay(1000); digitalWrite(s,LOW);\n}"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Kırmızı/Sarı/Yeşil", "pin": "D2 / D3 / D4"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": "const int k=2, s=3, y=4;\nvoid setup(){ pinMode(k,OUTPUT); pinMode(s,OUTPUT); pinMode(y,OUTPUT); }\nvoid loop(){\n  digitalWrite(k,HIGH); delay(4000); digitalWrite(s,HIGH); delay(1000);\n  digitalWrite(k,LOW); digitalWrite(s,LOW); digitalWrite(y,HIGH); delay(4000);\n  digitalWrite(y,LOW); digitalWrite(s,HIGH); delay(1000); digitalWrite(s,LOW);\n}"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Kırmızı/Sarı/Yeşil", "pin": "GPIO 18 / 19 / 21"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": "const int k=18, s=19, y=21;\nvoid setup(){ pinMode(k,OUTPUT); pinMode(s,OUTPUT); pinMode(y,OUTPUT); }\nvoid loop(){\n  digitalWrite(k,HIGH); delay(4000); digitalWrite(s,HIGH); delay(1000);\n  digitalWrite(k,LOW); digitalWrite(s,LOW); digitalWrite(y,HIGH); delay(4000);\n  digitalWrite(y,LOW); digitalWrite(s,HIGH); delay(1000); digitalWrite(s,LOW);\n}"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Kırmızı/Sarı/Yeşil", "pin": "D1 / D2 / D5"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": "const int k=D1, s=D2, y=D5;\nvoid setup(){ pinMode(k,OUTPUT); pinMode(s,OUTPUT); pinMode(y,OUTPUT); }\nvoid loop(){\n  digitalWrite(k,HIGH); delay(4000); digitalWrite(s,HIGH); delay(1000);\n  digitalWrite(k,LOW); digitalWrite(s,LOW); digitalWrite(y,HIGH); delay(4000);\n  digitalWrite(y,LOW); digitalWrite(s,HIGH); delay(1000); digitalWrite(s,LOW);\n}"
            }
        }
    },
    "ldr-otomatik-far": {
        "kategori": "Sensörler",
        "baslik": "LDR & Gerilim Bölücü ile Otomatik Far/Aydınlatma",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [{"adet": "1x", "isim": "LDR (Fotodirenç)", "link": ""}, {"adet": "1x", "isim": "10kΩ Direnç", "link": ""}, {"adet": "1x", "isim": "LED & 220Ω", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "LDR & 10k Ortak", "pin": "A0"}, {"bilesen": "LED (+)", "pin": "D13"}],
                "kod": "void setup(){ pinMode(13,OUTPUT); }\nvoid loop(){ if(analogRead(A0)<400) digitalWrite(13,HIGH); else digitalWrite(13,LOW); delay(100); }"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "LDR & 10k Ortak", "pin": "A0"}, {"bilesen": "LED (+)", "pin": "D13"}],
                "kod": "void setup(){ pinMode(13,OUTPUT); }\nvoid loop(){ if(analogRead(A0)<400) digitalWrite(13,HIGH); else digitalWrite(13,LOW); delay(100); }"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "LDR & 10k Ortak", "pin": "GPIO 34 (ADC)"}, {"bilesen": "LED (+)", "pin": "GPIO 2"}],
                "kod": "void setup(){ pinMode(2,OUTPUT); }\nvoid loop(){ if(analogRead(34)<1500) digitalWrite(2,HIGH); else digitalWrite(2,LOW); delay(100); }"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "LDR & 10k Ortak", "pin": "A0"}, {"bilesen": "LED (+)", "pin": "D4"}],
                "kod": "void setup(){ pinMode(D4,OUTPUT); }\nvoid loop(){ if(analogRead(A0)<450) digitalWrite(D4,LOW); else digitalWrite(D4,HIGH); delay(100); }"
            }
        }
    },
    "hc-sr04-radar": {
        "kategori": "Sensörler",
        "baslik": "HC-SR04 Ultrasonik Hassas Park Sensörü & Buzzer",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [{"adet": "1x", "isim": "HC-SR04 Sensör", "link": "https://www.direnc.net"}, {"adet": "1x", "isim": "Buzzer", "link": ""}],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "D9 / D10"}, {"bilesen": "Buzzer (+)", "pin": "D8"}],
                "kod": "const int trig=9, echo=10, buzz=8;\nvoid setup(){ pinMode(trig,OUTPUT); pinMode(echo,INPUT); pinMode(buzz,OUTPUT); }\nvoid loop(){\n  digitalWrite(trig,LOW); delayMicroseconds(2); digitalWrite(trig,HIGH); delayMicroseconds(10); digitalWrite(trig,LOW);\n  long s=pulseIn(echo,HIGH,30000); int d=(s*0.0343)/2;\n  if(d>0 && d<30){ digitalWrite(buzz,HIGH); delay(30); digitalWrite(buzz,LOW); delay(d*10); } else delay(100);\n}"
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "D9 / D10"}, {"bilesen": "Buzzer (+)", "pin": "D8"}],
                "kod": "const int trig=9, echo=10, buzz=8;\nvoid setup(){ pinMode(trig,OUTPUT); pinMode(echo,INPUT); pinMode(buzz,OUTPUT); }\nvoid loop(){\n  digitalWrite(trig,LOW); delayMicroseconds(2); digitalWrite(trig,HIGH); delayMicroseconds(10); digitalWrite(trig,LOW);\n  long s=pulseIn(echo,HIGH,30000); int d=(s*0.0343)/2;\n  if(d>0 && d<30){ digitalWrite(buzz,HIGH); delay(30); digitalWrite(buzz,LOW); delay(d*10); } else delay(100);\n}"
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "GPIO 5 / GPIO 18 (Bölücülü)"}, {"bilesen": "Buzzer (+)", "pin": "GPIO 19"}],
                "kod": "const int trig=5, echo=18, buzz=19;\nvoid setup(){ pinMode(trig,OUTPUT); pinMode(echo,INPUT); pinMode(buzz,OUTPUT); }\nvoid loop(){\n  digitalWrite(trig,LOW); delayMicroseconds(2); digitalWrite(trig,HIGH); delayMicroseconds(10); digitalWrite(trig,LOW);\n  long s=pulseIn(echo,HIGH,30000); int d=(s*0.0343)/2;\n  if(d>0 && d<30){ digitalWrite(buzz,HIGH); delay(30); digitalWrite(buzz,LOW); delay(d*10); } else delay(100);\n}"
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "D1 / D2 (Bölücülü)"}, {"bilesen": "Buzzer (+)", "pin": "D5"}],
                "kod": "const int trig=D1, echo=D2, buzz=D5;\nvoid setup(){ pinMode(trig,OUTPUT); pinMode(echo,INPUT); pinMode(buzz,OUTPUT); }\nvoid loop(){\n  digitalWrite(trig,LOW); delayMicroseconds(2); digitalWrite(trig,HIGH); delayMicroseconds(10); digitalWrite(trig,LOW);\n  long s=pulseIn(echo,HIGH,30000); int d=(s*0.0343)/2;\n  if(d>0 && d<30){ digitalWrite(buzz,HIGH); delay(30); digitalWrite(buzz,LOW); delay(d*10); } else delay(100);\n}"
            }
        }
    },
    "hc-sr501-pir": {
        "kategori": "Sensörler",
        "baslik": "HC-SR501 PIR Hareket Algılamalı Hırsız Alarmı",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [{"adet": "1x", "isim": "PIR Sensörü", "link": ""}],
        "kartlar": {
            "uno": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"PIR OUT","pin":"D2"},{"bilesen":"LED","pin":"D13"}],"kod":"void setup(){ pinMode(2,INPUT); pinMode(13,OUTPUT); }\nvoid loop(){ digitalWrite(13, digitalRead(2)); }"},
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
        "malzemeler": [{"adet": "1x", "isim": "DHT11 Sensörü", "link": ""}],
        "kartlar": {
            "uno": {"kutuphaneler":"<DHT.h>","baglanti":[{"bilesen":"DATA","pin":"D2 (10k pull-up)"}],"kod":"#include <DHT.h>\nDHT dht(2, DHT11);\nvoid setup(){ Serial.begin(9600); dht.begin(); }\nvoid loop(){ delay(2000); Serial.print(\"Sicaklik: \"); Serial.println(dht.readTemperature()); }"},
            "nano": {"kutuphaneler":"<DHT.h>","baglanti":[{"bilesen":"DATA","pin":"D2"}],"kod":"#include <DHT.h>\nDHT dht(2, DHT11);\nvoid setup(){ Serial.begin(9600); dht.begin(); }\nvoid loop(){ delay(2000); Serial.println(dht.readTemperature()); }"},
            "esp32": {"kutuphaneler":"<DHT.h>","baglanti":[{"bilesen":"DATA","pin":"GPIO 4"}],"kod":"#include <DHT.h>\nDHT dht(4, DHT11);\nvoid setup(){ Serial.begin(115200); dht.begin(); }\nvoid loop(){ delay(2000); Serial.println(dht.readTemperature()); }"},
            "esp8266": {"kutuphaneler":"<DHT.h>","baglanti":[{"bilesen":"DATA","pin":"D4 (GPIO 2)"}],"kod":"#include <DHT.h>\nDHT dht(D4, DHT11);\nvoid setup(){ Serial.begin(115200); dht.begin(); }\nvoid loop(){ delay(2000); Serial.println(dht.readTemperature()); }"}
        }
    },
    "tcrt5000-cizgi": {
        "kategori": "Sensörler",
        "baslik": "TCRT5000 Çift Çıkışlı Kızılötesi Çizgi Sensörü",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [{"adet": "1x", "isim": "TCRT5000 Modülü", "link": ""}],
        "kartlar": {
            "uno": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"DO Çıkış","pin":"D2"},{"bilesen":"LED","pin":"D13"}],"kod":"void setup(){ pinMode(2,INPUT); pinMode(13,OUTPUT); }\nvoid loop(){ digitalWrite(13, !digitalRead(2)); }"},
            "nano": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"DO Çıkış","pin":"D2"},{"bilesen":"LED","pin":"D13"}],"kod":"void setup(){ pinMode(2,INPUT); pinMode(13,OUTPUT); }\nvoid loop(){ digitalWrite(13, !digitalRead(2)); }"},
            "esp32": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"DO Çıkış","pin":"GPIO 4"},{"bilesen":"LED","pin":"GPIO 2"}],"kod":"void setup(){ pinMode(4,INPUT); pinMode(2,OUTPUT); }\nvoid loop(){ digitalWrite(2, !digitalRead(4)); }"},
            "esp8266": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"DO Çıkış","pin":"D1"},{"bilesen":"LED","pin":"D4"}],"kod":"void setup(){ pinMode(D1,INPUT); pinMode(D4,OUTPUT); }\nvoid loop(){ digitalWrite(D4, digitalRead(D1)); }"}
        }
    },
    "pot-analog-map": {
        "kategori": "Giriş & Kontrol",
        "baslik": "Potansiyometre ile LED Parlaklığı Ayarlama (Map)",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [{"adet": "1x", "isim": "10kΩ Potansiyometre", "link": ""}],
        "kartlar": {
            "uno": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Pot Orta Bacak","pin":"A0"},{"bilesen":"LED (+)", "pin":"D9 (PWM)"}],"kod":"void setup(){ pinMode(9,OUTPUT); }\nvoid loop(){ analogWrite(9, map(analogRead(A0),0,1023,0,255)); delay(10); }"},
            "nano": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Pot Orta Bacak","pin":"A0"},{"bilesen":"LED (+)", "pin":"D9 (PWM)"}],"kod":"void setup(){ pinMode(9,OUTPUT); }\nvoid loop(){ analogWrite(9, map(analogRead(A0),0,1023,0,255)); delay(10); }"},
            "esp32": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Pot Orta Bacak","pin":"GPIO 32"},{"bilesen":"LED (+)", "pin":"GPIO 18"}],"kod":"void setup(){ ledcAttach(18,5000,8); }\nvoid loop(){ ledcWrite(18, map(analogRead(32),0,4095,0,255)); delay(10); }"},
            "esp8266": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Pot Orta Bacak","pin":"A0"},{"bilesen":"LED (+)", "pin":"D1"}],"kod":"void setup(){ pinMode(D1,OUTPUT); }\nvoid loop(){ analogWrite(D1, analogRead(A0)); delay(10); }"}
        }
    },
    "buton-dahili-pullup": {
        "kategori": "Giriş & Kontrol",
        "baslik": "Dahili Pull-up Dirençli Buton Kontrolü",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [{"adet": "1x", "isim": "Push Buton", "link": ""}],
        "kartlar": {
            "uno": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Buton","pin":"D2 ve GND"},{"bilesen":"LED","pin":"D13"}],"kod":"void setup(){ pinMode(2,INPUT_PULLUP); pinMode(13,OUTPUT); }\nvoid loop(){ digitalWrite(13, !digitalRead(2)); }"},
            "nano": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Buton","pin":"D2 ve GND"},{"bilesen":"LED","pin":"D13"}],"kod":"void setup(){ pinMode(2,INPUT_PULLUP); pinMode(13,OUTPUT); }\nvoid loop(){ digitalWrite(13, !digitalRead(2)); }"},
            "esp32": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Buton","pin":"GPIO 4 ve GND"},{"bilesen":"LED","pin":"GPIO 2"}],"kod":"void setup(){ pinMode(4,INPUT_PULLUP); pinMode(2,OUTPUT); }\nvoid loop(){ digitalWrite(2, !digitalRead(4)); }"},
            "esp8266": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Buton","pin":"D2 ve GND"},{"bilesen":"LED","pin":"D4"}],"kod":"void setup(){ pinMode(D2,INPUT_PULLUP); pinMode(D4,OUTPUT); }\nvoid loop(){ digitalWrite(D4, digitalRead(D2)); }"}
        }
    },
    "joystick-analog-kontrol": {
        "kategori": "Giriş & Kontrol",
        "baslik": "Çift Eksenli Analog Joystick Okuma",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [{"adet": "1x", "isim": "Joystick Modülü", "link": ""}],
        "kartlar": {
            "uno": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"VRx / VRy","pin":"A0 / A1"}],"kod":"void setup(){ Serial.begin(9600); }\nvoid loop(){ Serial.print(\"X: \"); Serial.print(analogRead(A0)); Serial.print(\" Y: \"); Serial.println(analogRead(A1)); delay(200); }"},
            "nano": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"VRx / VRy","pin":"A0 / A1"}],"kod":"void setup(){ Serial.begin(9600); }\nvoid loop(){ Serial.print(\"X: \"); Serial.print(analogRead(A0)); Serial.print(\" Y: \"); Serial.println(analogRead(A1)); delay(200); }"},
            "esp32": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"VRx / VRy","pin":"GPIO 34 / 35"}],"kod":"void setup(){ Serial.begin(115200); }\nvoid loop(){ Serial.print(\"X: \"); Serial.print(analogRead(34)); Serial.print(\" Y: \"); Serial.println(analogRead(35)); delay(200); }"},
            "esp8266": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"VRx","pin":"A0"}],"kod":"void setup(){ Serial.begin(115200); }\nvoid loop(){ Serial.println(analogRead(A0)); delay(200); }"}
        }
    },
    "role-220v-kontrol": {
        "kategori": "Motor & Güç",
        "baslik": "5V Tek Kanal Röle ile Yüksek Güç Kontrolü",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [{"adet": "1x", "isim": "5V Röle", "link": ""}],
        "kartlar": {
            "uno": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Röle IN","pin":"D7"}],"kod":"void setup(){ pinMode(7,OUTPUT); }\nvoid loop(){ digitalWrite(7,LOW); delay(2000); digitalWrite(7,HIGH); delay(2000); }"},
            "nano": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Röle IN","pin":"D7"}],"kod":"void setup(){ pinMode(7,OUTPUT); }\nvoid loop(){ digitalWrite(7,LOW); delay(2000); digitalWrite(7,HIGH); delay(2000); }"},
            "esp32": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Röle IN","pin":"GPIO 19"}],"kod":"void setup(){ pinMode(19,OUTPUT); }\nvoid loop(){ digitalWrite(19,LOW); delay(2000); digitalWrite(19,HIGH); delay(2000); }"},
            "esp8266": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Röle IN","pin":"D1"}],"kod":"void setup(){ pinMode(D1,OUTPUT); }\nvoid loop(){ digitalWrite(D1,LOW); delay(2000); digitalWrite(D1,HIGH); delay(2000); }"}
        }
    },
    "sg90-servo-motor": {
        "kategori": "Motor & Güç",
        "baslik": "SG90 Mikro Servo Motor 0-180 Derece Açı Kontrolü",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [{"adet": "1x", "isim": "SG90 Servo", "link": ""}],
        "kartlar": {
            "uno": {"kutuphaneler":"<Servo.h>","baglanti":[{"bilesen":"Sinyal","pin":"D9"}],"kod":"#include <Servo.h>\nServo s;\nvoid setup(){ s.attach(9); }\nvoid loop(){ s.write(0); delay(1000); s.write(90); delay(1000); s.write(180); delay(1000); }"},
            "nano": {"kutuphaneler":"<Servo.h>","baglanti":[{"bilesen":"Sinyal","pin":"D9"}],"kod":"#include <Servo.h>\nServo s;\nvoid setup(){ s.attach(9); }\nvoid loop(){ s.write(0); delay(1000); s.write(90); delay(1000); s.write(180); delay(1000); }"},
            "esp32": {"kutuphaneler":"<ESP32Servo.h>","baglanti":[{"bilesen":"Sinyal","pin":"GPIO 18"}],"kod":"#include <ESP32Servo.h>\nServo s;\nvoid setup(){ s.attach(18); }\nvoid loop(){ s.write(0); delay(1000); s.write(90); delay(1000); s.write(180); delay(1000); }"},
            "esp8266": {"kutuphaneler":"<Servo.h>","baglanti":[{"bilesen":"Sinyal","pin":"D4"}],"kod":"#include <Servo.h>\nServo s;\nvoid setup(){ s.attach(D4); }\nvoid loop(){ s.write(0); delay(1000); s.write(90); delay(1000); s.write(180); delay(1000); }"}
        }
    },
    "l298n-dc-motor": {
        "kategori": "Motor & Güç",
        "baslik": "L298N Sürücü ile Çift Yönlü DC Motor & Hız Kontrolü",
        "zorluk": "İleri",
        "sure": "20 Dk",
        "malzemeler": [{"adet": "1x", "isim": "L298N Modülü", "link": ""}],
        "kartlar": {
            "uno": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"ENA / IN1 / IN2","pin":"D5 (PWM) / D6 / D7"}],"kod":"void setup(){ pinMode(5,OUTPUT); pinMode(6,OUTPUT); pinMode(7,OUTPUT); }\nvoid loop(){ digitalWrite(6,HIGH); digitalWrite(7,LOW); analogWrite(5,200); delay(2000); }"},
            "nano": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"ENA / IN1 / IN2","pin":"D5 / D6 / D7"}],"kod":"void setup(){ pinMode(5,OUTPUT); pinMode(6,OUTPUT); pinMode(7,OUTPUT); }\nvoid loop(){ digitalWrite(6,HIGH); digitalWrite(7,LOW); analogWrite(5,200); delay(2000); }"},
            "esp32": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"ENA / IN1 / IN2","pin":"GPIO 18 / 19 / 21"}],"kod":"void setup(){ pinMode(19,OUTPUT); pinMode(21,OUTPUT); ledcAttach(18,5000,8); }\nvoid loop(){ digitalWrite(19,HIGH); digitalWrite(21,LOW); ledcWrite(18,200); delay(2000); }"},
            "esp8266": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"ENA / IN1 / IN2","pin":"D1 / D2 / D5"}],"kod":"void setup(){ pinMode(D1,OUTPUT); pinMode(D2,OUTPUT); pinMode(D5,OUTPUT); }\nvoid loop(){ digitalWrite(D2,HIGH); digitalWrite(D5,LOW); analogWrite(D1,800); delay(2000); }"}
        }
    },
    "i2c-1602-lcd": {
        "kategori": "Ekranlar",
        "baslik": "I2C 1602 Karakter LCD Ekran Metin Yazdırma",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [{"adet": "1x", "isim": "1602 LCD + I2C", "link": ""}],
        "kartlar": {
            "uno": {"kutuphaneler":"<LiquidCrystal_I2C.h>","baglanti":[{"bilesen":"SDA / SCL","pin":"A4 / A5"}],"kod":"#include <Wire.h>\n#include <LiquidCrystal_I2C.h>\nLiquidCrystal_I2C lcd(0x27, 16, 2);\nvoid setup(){ lcd.init(); lcd.backlight(); lcd.print(\"ArduKod Uno\"); }\nvoid loop(){}"},
            "nano": {"kutuphaneler":"<LiquidCrystal_I2C.h>","baglanti":[{"bilesen":"SDA / SCL","pin":"A4 / A5"}],"kod":"#include <Wire.h>\n#include <LiquidCrystal_I2C.h>\nLiquidCrystal_I2C lcd(0x27, 16, 2);\nvoid setup(){ lcd.init(); lcd.backlight(); lcd.print(\"ArduKod Nano\"); }\nvoid loop(){}"},
            "esp32": {"kutuphaneler":"<LiquidCrystal_I2C.h>","baglanti":[{"bilesen":"SDA / SCL","pin":"GPIO 21 / 22"}],"kod":"#include <Wire.h>\n#include <LiquidCrystal_I2C.h>\nLiquidCrystal_I2C lcd(0x27, 16, 2);\nvoid setup(){ Wire.begin(21,22); lcd.init(); lcd.backlight(); lcd.print(\"ArduKod ESP32\"); }\nvoid loop(){}"},
            "esp8266": {"kutuphaneler":"<LiquidCrystal_I2C.h>","baglanti":[{"bilesen":"SDA / SCL","pin":"D2 / D1"}],"kod":"#include <Wire.h>\n#include <LiquidCrystal_I2C.h>\nLiquidCrystal_I2C lcd(0x27, 16, 2);\nvoid setup(){ Wire.begin(D2,D1); lcd.init(); lcd.backlight(); lcd.print(\"ArduKod ESP8266\"); }\nvoid loop(){}"}
        }
    },
    "ssd1306-oled": {
        "kategori": "Ekranlar",
        "baslik": "0.96 inç I2C SSD1306 OLED Grafik Ekran",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [{"adet": "1x", "isim": "0.96 OLED", "link": ""}],
        "kartlar": {
            "uno": {"kutuphaneler":"<Adafruit_SSD1306.h>","baglanti":[{"bilesen":"SDA / SCL","pin":"A4 / A5"}],"kod":"#include <Wire.h>\n#include <Adafruit_SSD1306.h>\nAdafruit_SSD1306 oled(128,64,&Wire,-1);\nvoid setup(){ oled.begin(SSD1306_SWITCHCAPVCC,0x3C); oled.clearDisplay(); oled.setTextColor(WHITE); oled.println(\"ArduKod OLED\"); oled.display(); }\nvoid loop(){}"},
            "nano": {"kutuphaneler":"<Adafruit_SSD1306.h>","baglanti":[{"bilesen":"SDA / SCL","pin":"A4 / A5"}],"kod":"#include <Wire.h>\n#include <Adafruit_SSD1306.h>\nAdafruit_SSD1306 oled(128,64,&Wire,-1);\nvoid setup(){ oled.begin(SSD1306_SWITCHCAPVCC,0x3C); oled.clearDisplay(); oled.setTextColor(WHITE); oled.println(\"ArduKod OLED\"); oled.display(); }\nvoid loop(){}"},
            "esp32": {"kutuphaneler":"<Adafruit_SSD1306.h>","baglanti":[{"bilesen":"SDA / SCL","pin":"GPIO 21 / 22"}],"kod":"#include <Wire.h>\n#include <Adafruit_SSD1306.h>\nAdafruit_SSD1306 oled(128,64,&Wire,-1);\nvoid setup(){ Wire.begin(21,22); oled.begin(SSD1306_SWITCHCAPVCC,0x3C); oled.clearDisplay(); oled.setTextColor(WHITE); oled.println(\"ESP32 OLED\"); oled.display(); }\nvoid loop(){}"},
            "esp8266": {"kutuphaneler":"<Adafruit_SSD1306.h>","baglanti":[{"bilesen":"SDA / SCL","pin":"D2 / D1"}],"kod":"#include <Wire.h>\n#include <Adafruit_SSD1306.h>\nAdafruit_SSD1306 oled(128,64,&Wire,-1);\nvoid setup(){ Wire.begin(D2,D1); oled.begin(SSD1306_SWITCHCAPVCC,0x3C); oled.clearDisplay(); oled.setTextColor(WHITE); oled.println(\"ESP8266 OLED\"); oled.display(); }\nvoid loop(){}"}
        }
    },
    "max7219-dot-matrix": {
        "kategori": "Ekranlar",
        "baslik": "MAX7219 8x8 Kırmızı LED Dot Matrix Modülü",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [{"adet": "1x", "isim": "MAX7219 Modül", "link": ""}],
        "kartlar": {
            "uno": {"kutuphaneler":"<LedControl.h>","baglanti":[{"bilesen":"DIN / CS / CLK","pin":"D12 / D10 / D11"}],"kod":"#include <LedControl.h>\nLedControl lc(12,11,10,1);\nvoid setup(){ lc.shutdown(0,false); lc.setIntensity(0,8); lc.clearDisplay(0); lc.setLed(0,3,3,true); }\nvoid loop(){}"},
            "nano": {"kutuphaneler":"<LedControl.h>","baglanti":[{"bilesen":"DIN / CS / CLK","pin":"D12 / D10 / D11"}],"kod":"#include <LedControl.h>\nLedControl lc(12,11,10,1);\nvoid setup(){ lc.shutdown(0,false); lc.setIntensity(0,8); lc.clearDisplay(0); lc.setLed(0,3,3,true); }\nvoid loop(){}"},
            "esp32": {"kutuphaneler":"<LedControl.h>","baglanti":[{"bilesen":"DIN / CS / CLK","pin":"GPIO 23 / 5 / 18"}],"kod":"#include <LedControl.h>\nLedControl lc(23,18,5,1);\nvoid setup(){ lc.shutdown(0,false); lc.setIntensity(0,8); lc.clearDisplay(0); lc.setLed(0,3,3,true); }\nvoid loop(){}"},
            "esp8266": {"kutuphaneler":"<LedControl.h>","baglanti":[{"bilesen":"DIN / CS / CLK","pin":"D7 / D8 / D5"}],"kod":"#include <LedControl.h>\nLedControl lc(D7,D5,D8,1);\nvoid setup(){ lc.shutdown(0,false); lc.setIntensity(0,8); lc.clearDisplay(0); lc.setLed(0,3,3,true); }\nvoid loop(){}"}
        }
    },
    "buzzer-melodi": {
        "kategori": "Ses & Bildirim",
        "baslik": "Pasif Buzzer ile Ton ve Melodi Çalma",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [{"adet": "1x", "isim": "Pasif Buzzer", "link": ""}],
        "kartlar": {
            "uno": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Buzzer (+)","pin":"D8"}],"kod":"void setup(){}\nvoid loop(){ tone(8,440,200); delay(300); tone(8,880,200); delay(500); }"},
            "nano": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Buzzer (+)","pin":"D8"}],"kod":"void setup(){}\nvoid loop(){ tone(8,440,200); delay(300); tone(8,880,200); delay(500); }"},
            "esp32": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Buzzer (+)","pin":"GPIO 18"}],"kod":"void setup(){ ledcAttach(18,2000,8); }\nvoid loop(){ ledcWriteTone(18,440); delay(300); ledcWriteTone(18,880); delay(500); }"},
            "esp8266": {"kutuphaneler":"Harici gerekmez.","baglanti":[{"bilesen":"Buzzer (+)","pin":"D5"}],"kod":"void setup(){}\nvoid loop(){ tone(D5,440,200); delay(300); tone(D5,880,200); delay(500); }"}
        }
    },
    "rc522-rfid": {
        "kategori": "Haberleşme & IoT",
        "baslik": "RC522 13.56MHz RFID Kart Okuyucu",
        "zorluk": "İleri",
        "sure": "20 Dk",
        "malzemeler": [{"adet": "1x", "isim": "RC522 RFID", "link": ""}],
        "kartlar": {
            "uno": {"kutuphaneler":"<MFRC522.h>","baglanti":[{"bilesen":"SDA / SCK / MOSI / MISO / RST","pin":"D10 / D13 / D11 / D12 / D9"}],"kod":"#include <SPI.h>\n#include <MFRC522.h>\nMFRC522 rfid(10,9);\nvoid setup(){ Serial.begin(9600); SPI.begin(); rfid.PCD_Init(); }\nvoid loop(){ if(rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()){ Serial.println(\"Kart Okundu!\"); rfid.PICC_HaltA(); } }"},
            "nano": {"kutuphaneler":"<MFRC522.h>","baglanti":[{"bilesen":"SDA / SCK / MOSI / MISO / RST","pin":"D10 / D13 / D11 / D12 / D9"}],"kod":"#include <SPI.h>\n#include <MFRC522.h>\nMFRC522 rfid(10,9);\nvoid setup(){ Serial.begin(9600); SPI.begin(); rfid.PCD_Init(); }\nvoid loop(){ if(rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()){ Serial.println(\"Kart Okundu!\"); rfid.PICC_HaltA(); } }"},
            "esp32": {"kutuphaneler":"<MFRC522.h>","baglanti":[{"bilesen":"SDA / SCK / MOSI / MISO / RST","pin":"GPIO 5 / 18 / 23 / 19 / 22"}],"kod":"#include <SPI.h>\n#include <MFRC522.h>\nMFRC522 rfid(5,22);\nvoid setup(){ Serial.begin(115200); SPI.begin(); rfid.PCD_Init(); }\nvoid loop(){ if(rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()){ Serial.println(\"ESP32 Kart Okundu!\"); rfid.PICC_HaltA(); } }"},
            "esp8266": {"kutuphaneler":"<MFRC522.h>","baglanti":[{"bilesen":"SDA / SCK / MOSI / MISO / RST","pin":"D8 / D5 / D7 / D6 / D3"}],"kod":"#include <SPI.h>\n#include <MFRC522.h>\nMFRC522 rfid(D8,D3);\nvoid setup(){ Serial.begin(115200); SPI.begin(); rfid.PCD_Init(); }\nvoid loop(){ if(rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()){ Serial.println(\"NodeMCU Kart Okundu!\"); rfid.PICC_HaltA(); } }"}
        }
    },
    "esp-wifi-web-server": {
        "kategori": "Haberleşme & IoT",
        "baslik": "Wi-Fi Web Server ile Tarayıcıdan LED Kontrolü",
        "zorluk": "İleri",
        "sure": "20 Dk",
        "malzemeler": [{"adet": "1x", "isim": "ESP32 / NodeMCU", "link": ""}],
        "kartlar": {
            "uno": {"kutuphaneler":"Harici Wi-Fi gerekir.","baglanti":[{"bilesen":"Wi-Fi","pin":"Uno Wi-Fi içermez (ESP seçiniz)"}],"kod":"// Arduino Uno dahili Wi-Fi barindirmaz. Lutfen ESP32 sekmesini secin."},
            "nano": {"kutuphaneler":"Harici Wi-Fi gerekir.","baglanti":[{"bilesen":"Wi-Fi","pin":"Nano Wi-Fi içermez"}],"kod":"// Arduino Nano dahili Wi-Fi barindirmaz. Lutfen ESP32 sekmesini secin."},
            "esp32": {"kutuphaneler":"<WiFi.h>, <WebServer.h>","baglanti":[{"bilesen":"LED","pin":"GPIO 2"}],"kod":"#include <WiFi.h>\n#include <WebServer.h>\nWebServer server(80);\nvoid setup(){\n  Serial.begin(115200); pinMode(2,OUTPUT);\n  WiFi.begin(\"WIFI_ADI\",\"SIFRE\");\n  while(WiFi.status()!=WL_CONNECTED) delay(500);\n  Serial.println(WiFi.localIP());\n  server.on(\"/on\",[](){ digitalWrite(2,HIGH); server.send(200,\"text/plain\",\"ACIK\"); });\n  server.on(\"/off\",[](){ digitalWrite(2,LOW); server.send(200,\"text/plain\",\"KAPALI\"); });\n  server.begin();\n}\nvoid loop(){ server.handleClient(); }"},
            "esp8266": {"kutuphaneler":"<ESP8266WiFi.h>, <ESP8266WebServer.h>","baglanti":[{"bilesen":"LED","pin":"D4"}],"kod":"#include <ESP8266WiFi.h>\n#include <ESP8266WebServer.h>\nESP8266WebServer server(80);\nvoid setup(){\n  Serial.begin(115200); pinMode(D4,OUTPUT);\n  WiFi.begin(\"WIFI_ADI\",\"SIFRE\");\n  while(WiFi.status()!=WL_CONNECTED) delay(500);\n  Serial.println(WiFi.localIP());\n  server.on(\"/on\",[](){ digitalWrite(D4,LOW); server.send(200,\"text/plain\",\"ACIK\"); });\n  server.on(\"/off\",[](){ digitalWrite(D4,HIGH); server.send(200,\"text/plain\",\"KAPALI\"); });\n  server.begin();\n}\nvoid loop(){ server.handleClient(); }"}
        }
    }
}

# ==============================================================================
# EKSİKSİZ ANA SAYFA HTML (ARAÇLAR, HUB, KARTLAR & DOĞRUDAN VERİ ENJEKSİYONU)
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

        /* 1. HUB (KART SEÇİCİ) */
        .hub-wrapper { max-width: 960px; margin: 40px auto; padding: 0 20px; text-align: center; }
        .hub-title { font-size: 28px; margin-bottom: 8px; }
        .hub-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-top: 30px; }
        .hub-card { background-color: var(--panel-bg); border: 1px solid var(--border); border-radius: 12px; padding: 24px; cursor: pointer; text-align: left; transition: 0.2s; }
        .hub-card:hover { border-color: var(--primary); transform: translateY(-3px); }

        /* 2. ATÖLYE ARAÇLARI */
        .tools-wrapper { max-width: 860px; margin: 30px auto; padding: 0 20px; }
        .tool-card { background-color: var(--panel-bg); border: 1px solid var(--border); border-radius: 10px; padding: 24px; margin-bottom: 24px; }
        .tool-title { font-size: 18px; font-weight: bold; margin-bottom: 16px; color: var(--primary); }
        .resistor-display { background: #2a2015; height: 48px; max-width: 320px; margin: 15px auto 20px auto; border-radius: 10px; display: flex; align-items: center; justify-content: space-around; padding: 0 20px; border: 2px solid #5a4632; }
        .resistor-band { width: 14px; height: 100%; border-radius: 2px; }
        .band-selectors { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; }
        select, input[type="text"] { width: 100%; padding: 9px; background-color: var(--bg-color); border: 1px solid var(--border); color: #fff; border-radius: 6px; outline: none; }
        .result-box { margin-top: 18px; background-color: rgba(0, 151, 157, 0.1); border: 1px solid var(--primary); border-radius: 8px; padding: 14px; text-align: center; font-size: 20px; font-weight: bold; color: var(--accent-green); }

        /* 3. PROJE KÜTÜPHANESİ */
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

    <!-- 1. HUB VIEW -->
    <div id="hubView" class="view-section active">
        <div class="hub-wrapper">
            <h1 class="hub-title">Geliştirici & Maker Merkezi</h1>
            <div style="color:var(--text-sub);">Çalışmak istediğiniz platformu veya atölye hesaplama aracını seçin</div>
            <div class="hub-grid">
                <div class="hub-card" onclick="kartaGit('uno')"><h3>🔵 Arduino Uno</h3><p style="color:var(--text-sub);font-size:13px;">5V lojik devreler ve temel pin kütüphanesi.</p></div>
                <div class="hub-card" onclick="kartaGit('nano')"><h3>🔷 Arduino Nano</h3><p style="color:var(--text-sub);font-size:13px;">Breadboard uyumlu kompakt devreler.</p></div>
                <div class="hub-card" onclick="kartaGit('esp32')"><h3>⚡ ESP32 (3.3V)</h3><p style="color:var(--text-sub);font-size:13px;">Wi-Fi, Bluetooth ve IoT pin konfigürasyonları.</p></div>
                <div class="hub-card" onclick="kartaGit('esp8266')"><h3>📶 ESP8266 NodeMCU</h3><p style="color:var(--text-sub);font-size:13px;">Ekonomik Wi-Fi ve sensör otomasyonları.</p></div>
                <div class="hub-card" onclick="ekranDegistir('tools')"><h3>🛠️ Atölye Araçları</h3><p style="color:var(--text-sub);font-size:13px;">Direnç ve kondansatör kod çözücüler.</p></div>
            </div>
        </div>
    </div>

    <!-- 2. ATÖLYE ARAÇLARI VIEW -->
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

    <!-- 3. WORKSPACE VIEW -->
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

                <div style="font-weight:bold; color:var(--primary); margin:20px 0 8px 0;">💻 C++ Kaynak Kodu</div>
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
    // 20 PROJE DOĞRUDAN HAFIZADA ENJEKTE (SIFIR AĞ İSTEĞİ, SIFIR GECİKME)
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
# GİZLİ ADMİN PANELİ (ŞİFRE EKRANDA ASLA YAZMAZ)
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
