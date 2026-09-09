import json
import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "ardukod_gizli_anahtar_123"

VERI_DOSYASI = "projeler.json"
ADMIN_SIFRE = "admin123"

VARSAYILAN_PROJELER = {
    "kara-simsek": {
        "kategori": "Temel & LED",
        "baslik": "5 LED Kademeli Kara Şimşek (Knight Rider)",
        "kutuphaneler": "Harici kütüphaneye gerek yoktur.",
        "baglanti": [
            {"bilesen": "LED 1 Anot (+)", "pin": "Arduino Pin 2 (220Ω Direnç Seriye Bağlı)"},
            {"bilesen": "LED 2 Anot (+)", "pin": "Arduino Pin 3 (220Ω Direnç Seriye Bağlı)"},
            {"bilesen": "LED 3 Anot (+)", "pin": "Arduino Pin 4 (220Ω Direnç Seriye Bağlı)"},
            {"bilesen": "LED 4 Anot (+)", "pin": "Arduino Pin 5 (220Ω Direnç Seriye Bağlı)"},
            {"bilesen": "LED 5 Anot (+)", "pin": "Arduino Pin 6 (220Ω Direnç Seriye Bağlı)"},
            {"bilesen": "LED 1-5 Katotları (-)", "pin": "Breadboard Mavi Eksi Hattı -> Arduino GND"}
        ],
        "kod": """const int ledPinleri[] = {2, 3, 4, 5, 6};
const int ledSayisi = 5;
const int beklemeSuresi = 65;

void setup() {
  for (int i = 0; i < ledSayisi; i++) {
    pinMode(ledPinleri[i], OUTPUT);
    digitalWrite(ledPinleri[i], LOW);
  }
}

void loop() {
  for (int i = 0; i < ledSayisi; i++) {
    digitalWrite(ledPinleri[i], HIGH);
    delay(beklemeSuresi);
    digitalWrite(ledPinleri[i], LOW);
  }
  for (int i = ledSayisi - 2; i > 0; i--) {
    digitalWrite(ledPinleri[i], HIGH);
    delay(beklemeSuresi);
    digitalWrite(ledPinleri[i], LOW);
  }
}"""
    },
    "rgb-pwm": {
        "kategori": "Temel & LED",
        "baslik": "RGB LED Yumuşak Renk Geçişi (PWM Fade)",
        "kutuphaneler": "Harici kütüphaneye gerek yoktur.",
        "baglanti": [
            {"bilesen": "Kırmızı Bacak (Red)", "pin": "Dijital Pin 9 (PWM) - 220Ω Direnç"},
            {"bilesen": "Ortak Katot (En Uzun)", "pin": "Arduino GND"},
            {"bilesen": "Yeşil Bacak (Green)", "pin": "Dijital Pin 10 (PWM) - 220Ω Direnç"},
            {"bilesen": "Mavi Bacak (Blue)", "pin": "Dijital Pin 11 (PWM) - 220Ω Direnç"}
        ],
        "kod": """const int redPin = 9;
const int greenPin = 10;
const int bluePin = 11;

void setup() {
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
}

void renkAyarla(int kirmizi, int yesil, int mavi) {
  analogWrite(redPin, kirmizi);
  analogWrite(greenPin, yesil);
  analogWrite(bluePin, mavi);
}

void loop() {
  for (int i = 0; i <= 255; i++) {
    renkAyarla(255 - i, i, 0);
    delay(10);
  }
  for (int i = 0; i <= 255; i++) {
    renkAyarla(0, 255 - i, i);
    delay(10);
  }
  for (int i = 0; i <= 255; i++) {
    renkAyarla(i, 0, 255 - i);
    delay(10);
  }
}"""
    },
    "trafik-isiklari": {
        "kategori": "Temel & LED",
        "baslik": "Zaman Ayarlı Standart Trafik Işıkları",
        "kutuphaneler": "Harici kütüphaneye gerek yoktur.",
        "baglanti": [
            {"bilesen": "Kırmızı LED Anot (+)", "pin": "Dijital Pin 8 (220Ω Direnç)"},
            {"bilesen": "Sarı LED Anot (+)", "pin": "Dijital Pin 9 (220Ω Direnç)"},
            {"bilesen": "Yeşil LED Anot (+)", "pin": "Dijital Pin 10 (220Ω Direnç)"},
            {"bilesen": "Tüm Katotlar (-)", "pin": "Breadboard Ortak Toprak -> GND"}
        ],
        "kod": """const int kirmiziPin = 8;
const int sariPin = 9;
const int yesilPin = 10;

void setup() {
  pinMode(kirmiziPin, OUTPUT);
  pinMode(sariPin, OUTPUT);
  pinMode(yesilPin, OUTPUT);
}

void loop() {
  digitalWrite(kirmiziPin, HIGH);
  digitalWrite(sariPin, LOW);
  digitalWrite(yesilPin, LOW);
  delay(5000);

  digitalWrite(sariPin, HIGH);
  delay(1500);

  digitalWrite(kirmiziPin, LOW);
  digitalWrite(sariPin, LOW);
  digitalWrite(yesilPin, HIGH);
  delay(4000);

  for(int i=0; i<3; i++) {
    digitalWrite(yesilPin, LOW); delay(250);
    digitalWrite(yesilPin, HIGH); delay(250);
  }

  digitalWrite(yesilPin, LOW);
  digitalWrite(sariPin, HIGH);
  delay(1500);
  digitalWrite(sariPin, LOW);
}"""
    },
    "ldr-otomatik-isik": {
        "kategori": "Sensörler",
        "baslik": "LDR & Gerilim Bölücü ile Otomatik Far/Aydınlatma",
        "kutuphaneler": "Harici kütüphaneye gerek yoktur.",
        "baglanti": [
            {"bilesen": "LDR 1. Bacak", "pin": "Arduino 5V"},
            {"bilesen": "LDR 2. Bacak", "pin": "Arduino A0 ve 10kΩ Direnç Bacağı"},
            {"bilesen": "10kΩ Direnç Diğer Bacak", "pin": "Arduino GND"},
            {"bilesen": "Çıkış LED Anot (+)", "pin": "Dijital Pin 12 (220Ω Direnç)"},
            {"bilesen": "Çıkış LED Katot (-)", "pin": "Arduino GND"}
        ],
        "kod": """const int ldrPin = A0;
const int ledPin = 12;
const int ESIK_DEGER = 350;

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int isikSeviyesi = analogRead(ldrPin);
  Serial.print("Isik Seviyesi: ");
  Serial.println(isikSeviyesi);

  if (isikSeviyesi < ESIK_DEGER) {
    digitalWrite(ledPin, HIGH);
  } else {
    digitalWrite(ledPin, LOW);
  }
  delay(200);
}"""
    },
    "hc-sr04-radar": {
        "kategori": "Sensörler",
        "baslik": "HC-SR04 Ultrasonik Hassas Park Sensörü & Buzzer",
        "kutuphaneler": "Harici kütüphaneye gerek yoktur.",
        "baglanti": [
            {"bilesen": "HC-SR04 VCC", "pin": "Arduino 5V"},
            {"bilesen": "HC-SR04 GND", "pin": "Arduino GND"},
            {"bilesen": "HC-SR04 Trig", "pin": "Dijital Pin 9"},
            {"bilesen": "HC-SR04 Echo", "pin": "Dijital Pin 10"},
            {"bilesen": "Buzzer (+)", "pin": "Dijital Pin 8"},
            {"bilesen": "Buzzer (-)", "pin": "Arduino GND"}
        ],
        "kod": """const int trigPin = 9;
const int echoPin = 10;
const int buzzerPin = 8;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  Serial.begin(9600);
}

long mesafeOlcum() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long sure = pulseIn(echoPin, HIGH, 30000);
  if (sure == 0) return 999;
  return (sure * 0.0343) / 2;
}

void loop() {
  long mesafe = mesafeOlcum();
  Serial.print("Mesafe: "); Serial.print(mesafe); Serial.println(" cm");

  if (mesafe <= 10) {
    digitalWrite(buzzerPin, HIGH);
  } else if (mesafe <= 30) {
    digitalWrite(buzzerPin, HIGH); delay(60);
    digitalWrite(buzzerPin, LOW);  delay(60);
  } else if (mesafe <= 60) {
    digitalWrite(buzzerPin, HIGH); delay(150);
    digitalWrite(buzzerPin, LOW);  delay(250);
  } else {
    digitalWrite(buzzerPin, LOW);
    delay(100);
  }
}"""
    },
    "pir-alarm": {
        "kategori": "Sensörler",
        "baslik": "HC-SR501 PIR Hareket Algılamalı Hırsız Alarmı",
        "kutuphaneler": "Harici kütüphaneye gerek yoktur.",
        "baglanti": [
            {"bilesen": "PIR VCC", "pin": "Arduino 5V"},
            {"bilesen": "PIR GND", "pin": "Arduino GND"},
            {"bilesen": "PIR OUT", "pin": "Dijital Pin 2"},
            {"bilesen": "İkaz LED Anot (+)", "pin": "Dijital Pin 13"},
            {"bilesen": "Buzzer (+)", "pin": "Dijital Pin 8"},
            {"bilesen": "Buzzer (-)", "pin": "Arduino GND"}
        ],
        "kod": """const int pirPin = 2;
const int ledPin = 13;
const int buzzerPin = 8;

void setup() {
  pinMode(pirPin, INPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  Serial.begin(9600);
  Serial.println("PIR Kalibre Ediliyor (15 sn)...");
  delay(15000);
}

void loop() {
  int hareket = digitalRead(pirPin);
  if (hareket == HIGH) {
    digitalWrite(ledPin, HIGH);
    tone(buzzerPin, 1000);
    delay(500);
    noTone(buzzerPin);
  } else {
    digitalWrite(ledPin, LOW);
    noTone(buzzerPin);
  }
  delay(100);
}"""
    },
    "dht11-sicaklik-nem": {
        "kategori": "Sensörler",
        "baslik": "DHT11 Dijital Sıcaklık & Nem Ölçümü",
        "kutuphaneler": "DHT sensor library (Adafruit) ve Adafruit Unified Sensor",
        "baglanti": [
            {"bilesen": "DHT11 VCC", "pin": "Arduino 5V"},
            {"bilesen": "DHT11 DATA", "pin": "Arduino Dijital Pin 2 (5V arasına 10k pull-up direnç)"},
            {"bilesen": "DHT11 NC", "pin": "Boşta bırakılır (Bağlanmaz)"},
            {"bilesen": "DHT11 GND", "pin": "Arduino GND"}
        ],
        "kod": """#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  delay(2000);
  float nem = dht.readHumidity();
  float sicaklik = dht.readTemperature();

  if (isnan(nem) || isnan(sicaklik)) {
    Serial.println("HATA: DHT sensorunden veri okunamiyor!");
    return;
  }

  Serial.print("Nem: %"); Serial.print(nem);
  Serial.print(" | Sicaklik: "); Serial.print(sicaklik); Serial.println(" C");
}"""
    },
    "tcrt5000-cizgi-takip": {
        "kategori": "Sensörler",
        "baslik": "TCRT5000 Çift Çıkışlı Kızılötesi Çizgi Sensörü",
        "kutuphaneler": "Harici kütüphaneye gerek yoktur.",
        "baglanti": [
            {"bilesen": "VCC", "pin": "Arduino 5V"},
            {"bilesen": "GND", "pin": "Arduino GND"},
            {"bilesen": "D0 (Dijital Çıkış)", "pin": "Arduino Pin 3"},
            {"bilesen": "A0 (Analog Çıkış)", "pin": "Arduino Analog Pin A0"},
            {"bilesen": "Durum LED'i", "pin": "Arduino Dahili LED Pin 13"}
        ],
        "kod": """const int d0Pin = 3;
const int a0Pin = A0;
const int ledPin = 13;

void setup() {
  pinMode(d0Pin, INPUT);
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int dijitalDeger = digitalRead(d0Pin);
  int analogDeger = analogRead(a0Pin);

  Serial.print("Analog: "); Serial.print(analogDeger);
  Serial.print(" | Durum: ");

  if (dijitalDeger == HIGH) {
    Serial.println("SIYAH ZEMIN");
    digitalWrite(ledPin, HIGH);
  } else {
    Serial.println("BEYAZ ZEMIN");
    digitalWrite(ledPin, LOW);
  }
  delay(150);
}"""
    },
    "potansiyometre-pwm": {
        "kategori": "Giriş & Kontrol",
        "baslik": "Potansiyometre ile LED Parlaklığı Ayarlama (Map)",
        "kutuphaneler": "Harici kütüphaneye gerek yoktur.",
        "baglanti": [
            {"bilesen": "Pot Sol Bacak", "pin": "Arduino 5V"},
            {"bilesen": "Pot Orta Bacak (Wiper)", "pin": "Arduino Analog Pin A0"},
            {"bilesen": "Pot Sağ Bacak", "pin": "Arduino GND"},
            {"bilesen": "LED Anot (+)", "pin": "Dijital Pin 9 (PWM) - 220Ω Direnç"},
            {"bilesen": "LED Katot (-)", "pin": "Arduino GND"}
        ],
        "kod": """const int potPin = A0;
const int ledPin = 9;

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int hamVeri = analogRead(potPin);
  int parlaklik = map(hamVeri, 0, 1023, 0, 255);
  analogWrite(ledPin, parlaklik);

  Serial.print("Pot: "); Serial.print(hamVeri);
  Serial.print(" -> PWM: "); Serial.println(parlaklik);
  delay(20);
}"""
    },
    "buton-debounce": {
        "kategori": "Giriş & Kontrol",
        "baslik": "Parazitsiz (Debounce) Buton ile LED Toggle Aç/Kapat",
        "kutuphaneler": "Harici kütüphaneye gerek yoktur.",
        "baglanti": [
            {"bilesen": "Push Buton 1. Bacak", "pin": "Arduino Dijital Pin 2"},
            {"bilesen": "Push Buton 2. Bacak", "pin": "Arduino GND (Dahili INPUT_PULLUP kullanılır)"},
            {"bilesen": "LED Anot (+)", "pin": "Dijital Pin 8 (220Ω Direnç)"},
            {"bilesen": "LED Katot (-)", "pin": "Arduino GND"}
        ],
        "kod": """const int butonPin = 2;
const int ledPin = 8;

int ledDurumu = LOW;
int butonSonDurum = HIGH;
unsigned long sonArkZamani = 0;
const unsigned long arkGecikmesi = 50;

void setup() {
  pinMode(butonPin, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, ledDurumu);
}

void loop() {
  int okuma = digitalRead(butonPin);
  if (okuma != butonSonDurum) {
    sonArkZamani = millis();
  }

  if ((millis() - sonArkZamani) > arkGecikmesi) {
    static int onayliDurum = HIGH;
    if (okuma != onayliDurum) {
      onayliDurum = okuma;
      if (onayliDurum == LOW) {
        ledDurumu = !ledDurumu;
        digitalWrite(ledPin, ledDurumu);
      }
    }
  }
  butonSonDurum = okuma;
}"""
    },
    "analog-joystick": {
        "kategori": "Giriş & Kontrol",
        "baslik": "İki Eksenli Joystick & Entegre Buton Okuma",
        "kutuphaneler": "Harici kütüphaneye gerek yoktur.",
        "baglanti": [
            {"bilesen": "Joystick VCC", "pin": "Arduino 5V"},
            {"bilesen": "Joystick GND", "pin": "Arduino GND"},
            {"bilesen": "Joystick VRx", "pin": "Arduino Analog Pin A0"},
            {"bilesen": "Joystick VRy", "pin": "Arduino Analog Pin A1"},
            {"bilesen": "Joystick SW (Switch)", "pin": "Dijital Pin 2"}
        ],
        "kod": """const int xPin = A0;
const int yPin = A1;
const int swPin = 2;

void setup() {
  pinMode(swPin, INPUT_PULLUP);
  Serial.begin(9600);
}

void loop() {
  int xDeger = analogRead(xPin);
  int yDeger = analogRead(yPin);
  int swDurum = digitalRead(swPin);

  Serial.print("X: "); Serial.print(xDeger);
  Serial.print(" | Y: "); Serial.print(yDeger);
  Serial.print(" | Buton: ");
  Serial.println(swDurum == LOW ? "TIKLANDI" : "BOS");
  delay(150);
}"""
    },
    "servo-pot-kontrol": {
        "kategori": "Motor & Sürücü",
        "baslik": "Potansiyometre ile Konum Kontrollü SG90 Servo",
        "kutuphaneler": "<Servo.h> (Arduino dahili kütüphanesi)",
        "baglanti": [
            {"bilesen": "SG90 Kahverengi Kablo", "pin": "Arduino GND"},
            {"bilesen": "SG90 Kırmızı Kablo", "pin": "Arduino 5V"},
            {"bilesen": "SG90 Turuncu Kablo", "pin": "Dijital Pin 9 (PWM)"},
            {"bilesen": "Potansiyometre Orta Bacak", "pin": "Arduino Analog Pin A0"},
            {"bilesen": "Potansiyometre Dış Bacaklar", "pin": "Arduino 5V ve GND"}
        ],
        "kod": """#include <Servo.h>

Servo microServo;
const int potPin = A0;

void setup() {
  microServo.attach(9);
  Serial.begin(9600);
}

void loop() {
  int potDeger = analogRead(potPin);
  int aci = map(potDeger, 0, 1023, 0, 180);
  microServo.write(aci);

  Serial.print("Pot: "); Serial.print(potDeger);
  Serial.print(" -> Aci: "); Serial.println(aci);
  delay(15);
}"""
    },
    "l298n-dc-motor": {
        "kategori": "Motor & Sürücü",
        "baslik": "L298N Sürücü ile DC Motor Hız ve Yön Kontrolü",
        "kutuphaneler": "Harici kütüphaneye gerek yoktur.",
        "baglanti": [
            {"bilesen": "L298N 12V Klemens", "pin": "Harici Pil / Adaptör Artı (+)"},
            {"bilesen": "L298N GND Klemens", "pin": "Arduino GND VE Harici Pil Eksi (-) Ortak Toprak"},
            {"bilesen": "L298N ENA (Jumper Çıkarılır)", "pin": "Dijital Pin 9 (PWM)"},
            {"bilesen": "L298N IN1", "pin": "Dijital Pin 8"},
            {"bilesen": "L298N IN2", "pin": "Dijital Pin 7"},
            {"bilesen": "Motor OUT1 - OUT2", "pin": "DC Motor Klemenslerine"}
        ],
        "kod": """const int enaPin = 9;
const int in1Pin = 8;
const int in2Pin = 7;

void setup() {
  pinMode(enaPin, OUTPUT);
  pinMode(in1Pin, OUTPUT);
  pinMode(in2Pin, OUTPUT);
}

void motorSur(int yon, int hiz) {
  analogWrite(enaPin, hiz);
  if (yon == 1) {
    digitalWrite(in1Pin, HIGH); digitalWrite(in2Pin, LOW);
  } else if (yon == -1) {
    digitalWrite(in1Pin, LOW); digitalWrite(in2Pin, HIGH);
  } else {
    digitalWrite(in1Pin, LOW); digitalWrite(in2Pin, LOW);
  }
}

void loop() {
  motorSur(1, 255); delay(2000); // İleri Tam Hız
  motorSur(0, 0);   delay(1000); // Dur
  motorSur(-1, 150); delay(2000); // Geri Yarım Hız
  motorSur(0, 0);   delay(1000);
}"""
    },
    "step-motor-uln2003": {
        "kategori": "Motor & Sürücü",
        "baslik": "28BYJ-48 Step Motor ve ULN2003 Hassas Tur",
        "kutuphaneler": "<Stepper.h> (Arduino dahili kütüphanesi)",
        "baglanti": [
            {"bilesen": "ULN2003 IN1", "pin": "Arduino Pin 8"},
            {"bilesen": "ULN2003 IN2", "pin": "Arduino Pin 9"},
            {"bilesen": "ULN2003 IN3", "pin": "Arduino Pin 10"},
            {"bilesen": "ULN2003 IN4", "pin": "Arduino Pin 11"},
            {"bilesen": "ULN2003 5V-12V (+)", "pin": "Harici 5V Güç Kaynağı (+)"},
            {"bilesen": "ULN2003 GND (-)", "pin": "Harici Güç GND ve Arduino GND (Ortak)"}
        ],
        "kod": """#include <Stepper.h>

const int ADIM_SAYISI = 2048;
Stepper adimMotoru(ADIM_SAYISI, 8, 10, 9, 11);

void setup() {
  adimMotoru.setSpeed(12);
}

void loop() {
  adimMotoru.step(ADIM_SAYISI); // 1 Tam Tur
  delay(1000);
  adimMotoru.step(-ADIM_SAYISI / 2); // Yarım Tur Geri
  delay(1000);
}"""
    },
    "aktif-buzzer-kesik": {
        "kategori": "Ses & Uyarı",
        "baslik": "Aktif Buzzer ile Kesikli Acil Durum Sireni",
        "kutuphaneler": "Harici kütüphaneye gerek yoktur.",
        "baglanti": [
            {"bilesen": "Aktif Buzzer (+ Uzun)", "pin": "Arduino Dijital Pin 8"},
            {"bilesen": "Aktif Buzzer (- Kısa)", "pin": "Arduino GND"}
        ],
        "kod": """const int buzzerPin = 8;

void setup() {
  pinMode(buzzerPin, OUTPUT);
}

void bip(int tekrar, int sure, int duraklama) {
  for (int i = 0; i < tekrar; i++) {
    digitalWrite(buzzerPin, HIGH); delay(sure);
    digitalWrite(buzzerPin, LOW); delay(duraklama);
  }
}

void loop() {
  bip(3, 80, 80);
  delay(1000);
  bip(1, 600, 100);
  delay(2000);
}"""
    },
    "pasif-buzzer-nota": {
        "kategori": "Ses & Uyarı",
        "baslik": "Pasif Buzzer ile Frekans Tabanlı Melodi Çalma",
        "kutuphaneler": "Harici kütüphaneye gerek yoktur.",
        "baglanti": [
            {"bilesen": "Pasif Buzzer (+)", "pin": "Dijital Pin 8"},
            {"bilesen": "Pasif Buzzer (-)", "pin": "Arduino GND (100Ω Dirençle)"}
        ],
        "kod": """#define NOTE_C4 262
#define NOTE_D4 294
#define NOTE_E4 330
#define NOTE_F4 349
#define NOTE_G4 392
#define NOTE_A4 440
#define NOTE_B4 494
#define NOTE_C5 523

const int buzzerPin = 8;
int melodi[] = { NOTE_C4, NOTE_D4, NOTE_E4, NOTE_F4, NOTE_G4, NOTE_A4, NOTE_B4, NOTE_C5 };
int sureler[] = { 4, 4, 4, 4, 4, 4, 4, 2 };

void setup() {
  for (int i = 0; i < 8; i++) {
    int notaSuresi = 1000 / sureler[i];
    tone(buzzerPin, melodi[i], notaSuresi);
    int bekleme = notaSuresi * 1.30;
    delay(bekleme);
    noTone(buzzerPin);
  }
}

void loop() {}"""
    },
    "lcd-i2c-1602": {
        "kategori": "Ekran & Gösterge",
        "baslik": "16x2 Karakter LCD & PCF8574 I2C Modülü",
        "kutuphaneler": "<Wire.h> ve LiquidCrystal_I2C",
        "baglanti": [
            {"bilesen": "I2C Modülü GND", "pin": "Arduino GND"},
            {"bilesen": "I2C Modülü VCC", "pin": "Arduino 5V"},
            {"bilesen": "I2C Modülü SDA", "pin": "Arduino Uno A4 (Mega'da Pin 20)"},
            {"bilesen": "I2C Modülü SCL", "pin": "Arduino Uno A5 (Mega'da Pin 21)"}
        ],
        "kod": """#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print(">> ARDUKOD v1.0 <<");
  lcd.setCursor(0, 1);
  lcd.print("Sistem Hazir...");
  delay(2000);
}

int sayac = 0;

void loop() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Calisma Suresi:");
  lcd.setCursor(0, 1);
  lcd.print(sayac);
  lcd.print(" Saniye");
  sayac++;
  delay(1000);
}"""
    },
    "oled-i2c-ssd1306": {
        "kategori": "Ekran & Gösterge",
        "baslik": "0.96 inç Grafik I2C OLED Ekran (128x64)",
        "kutuphaneler": "<Wire.h>, <Adafruit_GFX.h> ve <Adafruit_SSD1306.h>",
        "baglanti": [
            {"bilesen": "OLED VCC", "pin": "Arduino 5V (veya 3.3V)"},
            {"bilesen": "OLED GND", "pin": "Arduino GND"},
            {"bilesen": "OLED SCL", "pin": "Arduino Analog Pin A5"},
            {"bilesen": "OLED SDA", "pin": "Arduino Analog Pin A4"}
        ],
        "kod": """#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define EKRAN_GENISLIK 128
#define EKRAN_YUKSEKLIK 64
#define OLED_RESET -1 

Adafruit_SSD1306 ekran(EKRAN_GENISLIK, EKRAN_YUKSEKLIK, &Wire, OLED_RESET);

void setup() {
  if (!ekran.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    for (;;);
  }
  ekran.clearDisplay();
  ekran.setTextSize(1);
  ekran.setTextColor(SSD1306_WHITE);
  ekran.setCursor(18, 0);
  ekran.println("ARDUINO OLEDI");
  ekran.drawLine(0, 10, 128, 10, SSD1306_WHITE);

  ekran.setTextSize(2);
  ekran.setCursor(20, 24);
  ekran.print("24.8 C");

  ekran.setTextSize(1);
  ekran.setCursor(10, 52);
  ekran.println("Sistem Durumu: OK");
  ekran.display();
}

void loop() {}"""
    },
    "role-220v-kontrol": {
        "kategori": "Güç & Röle",
        "baslik": "5V Tek Kanal Röle Modülü ile Yüksek Güç Kontrolü",
        "kutuphaneler": "Harici kütüphaneye gerek yoktur.",
        "baglanti": [
            {"bilesen": "Röle VCC", "pin": "Arduino 5V"},
            {"bilesen": "Röle GND", "pin": "Arduino GND"},
            {"bilesen": "Röle IN (Kontrol Sinyali)", "pin": "Arduino Dijital Pin 7"},
            {"bilesen": "Röle COM (Ortak Uç)", "pin": "Harici Şebeke Faz Kablosu"},
            {"bilesen": "Röle NO (Normalde Açık)", "pin": "Lambaya Giden Faz Kablosu"}
        ],
        "kod": """const int rolePin = 7;

void setup() {
  pinMode(rolePin, OUTPUT);
  digitalWrite(rolePin, HIGH); // Ilk acilista kapali (Active-LOW)
  Serial.begin(9600);
}

void loop() {
  digitalWrite(rolePin, LOW); // Role CEKILDI
  Serial.println("YUK ACIK");
  delay(5000);

  digitalWrite(rolePin, HIGH); // Role BIRAKILDI
  Serial.println("YUK KAPALI");
  delay(5000);
}"""
    },
    "bluetooth-hc05-terminal": {
        "kategori": "Haberleşme",
        "baslik": "HC-05 Bluetooth Seri Port İletişimi (SoftwareSerial)",
        "kutuphaneler": "<SoftwareSerial.h> (Arduino dahili kütüphanesi)",
        "baglanti": [
            {"bilesen": "HC-05 VCC", "pin": "Arduino 5V"},
            {"bilesen": "HC-05 GND", "pin": "Arduino GND"},
            {"bilesen": "HC-05 TXD", "pin": "Arduino Dijital Pin 10 (Yazılımsal RX)"},
            {"bilesen": "HC-05 RXD (3.3V Lojik)", "pin": "Arduino Pin 11 -> 1kΩ ve 2kΩ Direnç Bölücü ile"},
            {"bilesen": "Kontrol Edilen LED", "pin": "Dijital Pin 13"}
        ],
        "kod": """#include <SoftwareSerial.h>

SoftwareSerial btHatti(10, 11);
const int ledPin = 13;

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
  btHatti.begin(9600);
  Serial.println("Bluetooth Hazir...");
}

void loop() {
  if (btHatti.available()) {
    char komut = btHatti.read();
    if (komut == '1') {
      digitalWrite(ledPin, HIGH);
      btHatti.println("LED YANDI");
    } else if (komut == '0') {
      digitalWrite(ledPin, LOW);
      btHatti.println("LED SONDU");
    }
  }

  if (Serial.available()) {
    btHatti.write(Serial.read());
  }
}"""
    }
}

def verileri_yukle():
    if not os.path.exists(VERI_DOSYASI):
        with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(VARSAYILAN_PROJELER, f, ensure_ascii=False, indent=2)
        return VARSAYILAN_PROJELER
    try:
        with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return VARSAYILAN_PROJELER

def verileri_kaydet(projeler):
    with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(projeler, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projeler', methods=['GET'])
def projeleri_getir():
    projeler = verileri_yukle()
    liste = []
    for anahtar, detay in projeler.items():
        liste.append({
            "id": anahtar,
            "baslik": detay.get("baslik", anahtar),
            "kategori": detay.get("kategori", "Genel")
        })
    return jsonify(liste)

@app.route('/proje/<id>', methods=['GET'])
def tek_proje_getir(id):
    projeler = verileri_yukle()
    if id in projeler:
        return jsonify({"durum": "basarili", "veri": projeler[id]})
    return jsonify({"durum": "hata", "mesaj": "Proje bulunamadı."})

@app.route('/admin')
def admin_sayfasi():
    if not session.get('admin_girisi'):
        return render_template('admin_login.html')
    return render_template('admin.html')

@app.route('/admin/login', methods=['POST'])
def admin_login():
    veri = request.get_json() or {}
    sifre = veri.get('sifre', '')
    if sifre == ADMIN_SIFRE:
        session['admin_girisi'] = True
        return jsonify({"durum": "basarili"})
    return jsonify({"durum": "hata", "mesaj": "Yanlış şifre!"})

@app.route('/admin/logout', methods=['GET'])
def admin_logout():
    session.pop('admin_girisi', None)
    return redirect(url_for('admin_sayfasi'))

@app.route('/admin/kaydet', methods=['POST'])
def admin_kaydet():
    if not session.get('admin_girisi'):
        return jsonify({"durum": "hata", "mesaj": "Yetkisiz işlem!"}), 403

    veri = request.get_json() or {}
    proje_id = veri.get('id', '').strip().lower().replace(" ", "-")
    
    if not proje_id:
        return jsonify({"durum": "hata", "mesaj": "Proje kimliği (ID) boş olamaz."})

    projeler = verileri_yukle()
    projeler[proje_id] = {
        "kategori": veri.get('kategori', 'Genel'),
        "baslik": veri.get('baslik', ''),
        "kutuphaneler": veri.get('kutuphaneler', 'Harici kütüphaneye gerek yoktur.'),
        "baglanti": veri.get('baglanti', []),
        "kod": veri.get('kod', '')
    }
    verileri_kaydet(projeler)
    return jsonify({"durum": "basarili", "mesaj": "Proje başarıyla kaydedildi!"})

@app.route('/admin/sil/<id>', methods=['DELETE'])
def admin_sil(id):
    if not session.get('admin_girisi'):
        return jsonify({"durum": "hata", "mesaj": "Yetkisiz işlem!"}), 403

    projeler = verileri_yukle()
    if id in projeler:
        del projeler[id]
        verileri_kaydet(projeler)
        return jsonify({"durum": "basarili", "mesaj": "Proje silindi."})
    return jsonify({"durum": "hata", "mesaj": "Proje bulunamadı."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)