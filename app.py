from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "ardukod_gizli_anahtar_123"
ADMIN_SIFRE = "admin123"

# ==============================================================================
# TAM 20 ADET DOĞRULANMIŞ VE KARTA ÖZEL PROJE (Uno, Nano, ESP32, ESP8266)
# ==============================================================================
PROJELER = {
    # 1. KARA ŞİMŞEK
    "kara-simsek": {
        "kategori": "Temel & LED",
        "baslik": "5 LED Kademeli Kara Şimşek",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "5x", "isim": "5mm LED"},
            {"adet": "5x", "isim": "220Ω / 330Ω Direnç"},
            {"adet": "1x", "isim": "Breadboard"},
            {"adet": "6x", "isim": "Erkek-Erkek Jumper"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "GND"}
                ],
                "kod": """// Arduino Uno - 5 LED Kara Simsek
const int pinler[] = {2, 3, 4, 5, 6};
const int adet = 5;

void setup() {
  for (int i = 0; i < adet; i++) pinMode(pinler[i], OUTPUT);
}

void loop() {
  for (int i = 0; i < adet; i++) {
    digitalWrite(pinler[i], HIGH);
    delay(50);
    digitalWrite(pinler[i], LOW);
  }
  for (int i = adet - 2; i > 0; i--) {
    digitalWrite(pinler[i], HIGH);
    delay(50);
    digitalWrite(pinler[i], LOW);
  }
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "GND"}
                ],
                "kod": """// Arduino Nano - 5 LED Kara Simsek
const int pinler[] = {2, 3, 4, 5, 6};
const int adet = 5;

void setup() {
  for (int i = 0; i < adet; i++) pinMode(pinler[i], OUTPUT);
}

void loop() {
  for (int i = 0; i < adet; i++) {
    digitalWrite(pinler[i], HIGH);
    delay(50);
    digitalWrite(pinler[i], LOW);
  }
  for (int i = adet - 2; i > 0; i--) {
    digitalWrite(pinler[i], HIGH);
    delay(50);
    digitalWrite(pinler[i], LOW);
  }
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "GPIO 18, 19, 21, 22, 23 (330Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "GND"}
                ],
                "kod": """// ESP32 - 5 LED Kara Simsek (3.3V Uyumlu)
const int pinler[] = {18, 19, 21, 22, 23};
const int adet = 5;

void setup() {
  for (int i = 0; i < adet; i++) pinMode(pinler[i], OUTPUT);
}

void loop() {
  for (int i = 0; i < adet; i++) {
    digitalWrite(pinler[i], HIGH);
    delay(50);
    digitalWrite(pinler[i], LOW);
  }
  for (int i = adet - 2; i > 0; i--) {
    digitalWrite(pinler[i], HIGH);
    delay(50);
    digitalWrite(pinler[i], LOW);
  }
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D1, D2, D5, D6, D7 (GPIO 5,4,14,12,13)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "GND"}
                ],
                "kod": """// ESP8266 NodeMCU - 5 LED Kara Simsek
const int pinler[] = {D1, D2, D5, D6, D7};
const int adet = 5;

void setup() {
  for (int i = 0; i < adet; i++) pinMode(pinler[i], OUTPUT);
}

void loop() {
  for (int i = 0; i < adet; i++) {
    digitalWrite(pinler[i], HIGH);
    delay(50);
    digitalWrite(pinler[i], LOW);
  }
  for (int i = adet - 2; i > 0; i--) {
    digitalWrite(pinler[i], HIGH);
    delay(50);
    digitalWrite(pinler[i], LOW);
  }
}"""
            }
        }
    },

    # 2. PWM İLE RGB LED FADE
    "rgb-led-pwm": {
        "kategori": "Temel & LED",
        "baslik": "RGB LED Yumuşak Renk Geçişi (PWM)",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "Ortak Katot RGB LED"},
            {"adet": "3x", "isim": "220Ω / 330Ω Direnç"},
            {"adet": "4x", "isim": "Jumper Kablo"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "RGB Kırmızı (R)", "pin": "D9 (PWM) (220Ω)"},
                    {"bilesen": "RGB Yeşil (G)", "pin": "D10 (PWM) (220Ω)"},
                    {"bilesen": "RGB Mavi (B)", "pin": "D11 (PWM) (220Ω)"},
                    {"bilesen": "Ortak Katot (-)", "pin": "GND"}
                ],
                "kod": """// Arduino Uno - RGB LED PWM Renk Gecisi
const int red = 9, green = 10, blue = 11;

void setup() {
  pinMode(red, OUTPUT);
  pinMode(green, OUTPUT);
  pinMode(blue, OUTPUT);
}

void loop() {
  for (int i = 0; i < 255; i++) { analogWrite(red, i); analogWrite(green, 255-i); delay(5); }
  for (int i = 0; i < 255; i++) { analogWrite(green, i); analogWrite(blue, 255-i); delay(5); }
  for (int i = 0; i < 255; i++) { analogWrite(blue, i); analogWrite(red, 255-i); delay(5); }
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "RGB Kırmızı (R)", "pin": "D9 (PWM) (220Ω)"},
                    {"bilesen": "RGB Yeşil (G)", "pin": "D10 (PWM) (220Ω)"},
                    {"bilesen": "RGB Mavi (B)", "pin": "D11 (PWM) (220Ω)"},
                    {"bilesen": "Ortak Katot (-)", "pin": "GND"}
                ],
                "kod": """// Arduino Nano - RGB LED PWM Renk Gecisi
const int red = 9, green = 10, blue = 11;

void setup() {
  pinMode(red, OUTPUT);
  pinMode(green, OUTPUT);
  pinMode(blue, OUTPUT);
}

void loop() {
  for (int i = 0; i < 255; i++) { analogWrite(red, i); analogWrite(green, 255-i); delay(5); }
  for (int i = 0; i < 255; i++) { analogWrite(green, i); analogWrite(blue, 255-i); delay(5); }
  for (int i = 0; i < 255; i++) { analogWrite(blue, i); analogWrite(red, 255-i); delay(5); }
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez (Dahili ledc PWM motoru).",
                "baglanti": [
                    {"bilesen": "RGB Kırmızı (R)", "pin": "GPIO 18 (330Ω)"},
                    {"bilesen": "RGB Yeşil (G)", "pin": "GPIO 19 (330Ω)"},
                    {"bilesen": "RGB Mavi (B)", "pin": "GPIO 21 (330Ω)"},
                    {"bilesen": "Ortak Katot (-)", "pin": "GND"}
                ],
                "kod": """// ESP32 - Donanimsal PWM ile RGB Kontrol
const int rPin = 18, gPin = 19, bPin = 21;

void setup() {
  ledcAttach(rPin, 5000, 8); // 5kHz, 8-bit (0-255)
  ledcAttach(gPin, 5000, 8);
  ledcAttach(bPin, 5000, 8);
}

void loop() {
  for (int i = 0; i < 255; i++) { ledcWrite(rPin, i); ledcWrite(gPin, 255-i); delay(5); }
  for (int i = 0; i < 255; i++) { ledcWrite(gPin, i); ledcWrite(bPin, 255-i); delay(5); }
  for (int i = 0; i < 255; i++) { ledcWrite(bPin, i); ledcWrite(rPin, 255-i); delay(5); }
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "RGB Kırmızı (R)", "pin": "D1 (GPIO 5) (330Ω)"},
                    {"bilesen": "RGB Yeşil (G)", "pin": "D2 (GPIO 4) (330Ω)"},
                    {"bilesen": "RGB Mavi (B)", "pin": "D5 (GPIO 14) (330Ω)"},
                    {"bilesen": "Ortak Katot (-)", "pin": "GND"}
                ],
                "kod": """// ESP8266 NodeMCU - RGB PWM Kontrol (0-1023)
const int rPin = D1, gPin = D2, bPin = D5;

void setup() {
  pinMode(rPin, OUTPUT);
  pinMode(gPin, OUTPUT);
  pinMode(bPin, OUTPUT);
}

void loop() {
  for (int i = 0; i < 1023; i += 4) { analogWrite(rPin, i); analogWrite(gPin, 1023-i); delay(5); }
  for (int i = 0; i < 1023; i += 4) { analogWrite(gPin, i); analogWrite(bPin, 1023-i); delay(5); }
  for (int i = 0; i < 1023; i += 4) { analogWrite(bPin, i); analogWrite(rPin, 1023-i); delay(5); }
}"""
            }
        }
    },

    # 3. BUTON İLE TOGGLE (DEBOUNCE)
    "debounce-buton": {
        "kategori": "Giriş & Kontrol",
        "baslik": "Kararlı Buton (Debounce & INPUT_PULLUP)",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "Push Buton"},
            {"adet": "1x", "isim": "5mm LED"},
            {"adet": "1x", "isim": "220Ω Direnç"},
            {"adet": "3x", "isim": "Jumper Kablo"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "Buton Bacağı 1", "pin": "D2 (Dahili Pull-up aktif)"},
                    {"bilesen": "Buton Bacağı 2", "pin": "GND"},
                    {"bilesen": "LED Anot (+)", "pin": "D13 (220Ω)"},
                    {"bilesen": "LED Katot (-)", "pin": "GND"}
                ],
                "kod": """// Arduino Uno - Debounce Buton Toggle
const int btn = 2, led = 13;
bool ledDurum = false;
int sonDurum = HIGH;
unsigned long sonZaman = 0;

void setup() {
  pinMode(btn, INPUT_PULLUP);
  pinMode(led, OUTPUT);
}

void loop() {
  int okunan = digitalRead(btn);
  if (okunan != sonDurum) sonZaman = millis();
  if ((millis() - sonZaman) > 40) {
    if (okunan == LOW && sonDurum == HIGH) {
      ledDurum = !ledDurum;
      digitalWrite(led, ledDurum);
    }
  }
  sonDurum = okunan;
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "Buton Bacağı 1", "pin": "D2 (Dahili Pull-up)"},
                    {"bilesen": "Buton Bacağı 2", "pin": "GND"},
                    {"bilesen": "LED Anot (+)", "pin": "D13 (220Ω)"},
                    {"bilesen": "LED Katot (-)", "pin": "GND"}
                ],
                "kod": """// Arduino Nano - Buton Toggle
const int btn = 2, led = 13;
bool ledDurum = false;
int sonDurum = HIGH;
unsigned long sonZaman = 0;

void setup() {
  pinMode(btn, INPUT_PULLUP);
  pinMode(led, OUTPUT);
}

void loop() {
  int okunan = digitalRead(btn);
  if (okunan != sonDurum) sonZaman = millis();
  if ((millis() - sonZaman) > 40) {
    if (okunan == LOW && sonDurum == HIGH) {
      ledDurum = !ledDurum;
      digitalWrite(led, ledDurum);
    }
  }
  sonDurum = okunan;
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "Buton Bacağı 1", "pin": "GPIO 4 (INPUT_PULLUP)"},
                    {"bilesen": "Buton Bacağı 2", "pin": "GND"},
                    {"bilesen": "LED Anot (+)", "pin": "GPIO 2 (Dahili LED)"},
                    {"bilesen": "LED Katot (-)", "pin": "GND"}
                ],
                "kod": """// ESP32 - Debounce Buton ile Dahili LED Toggle
const int btn = 4, led = 2;
bool ledDurum = false;
int sonDurum = HIGH;
unsigned long sonZaman = 0;

void setup() {
  pinMode(btn, INPUT_PULLUP);
  pinMode(led, OUTPUT);
}

void loop() {
  int okunan = digitalRead(btn);
  if (okunan != sonDurum) sonZaman = millis();
  if ((millis() - sonZaman) > 40) {
    if (okunan == LOW && sonDurum == HIGH) {
      ledDurum = !ledDurum;
      digitalWrite(led, ledDurum);
    }
  }
  sonDurum = okunan;
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "Buton Bacağı 1", "pin": "D3 (GPIO 0, INPUT_PULLUP)"},
                    {"bilesen": "Buton Bacağı 2", "pin": "GND"},
                    {"bilesen": "LED Anot (+)", "pin": "D4 (GPIO 2, Dahili Mavi LED)"},
                    {"bilesen": "LED Katot (-)", "pin": "GND"}
                ],
                "kod": """// ESP8266 NodeMCU - Flash Butonu (D3) ile Toggle
const int btn = D3, led = D4;
bool ledDurum = false;
int sonDurum = HIGH;
unsigned long sonZaman = 0;

void setup() {
  pinMode(btn, INPUT_PULLUP);
  pinMode(led, OUTPUT);
}

void loop() {
  int okunan = digitalRead(btn);
  if (okunan != sonDurum) sonZaman = millis();
  if ((millis() - sonZaman) > 40) {
    if (okunan == LOW && sonDurum == HIGH) {
      ledDurum = !ledDurum;
      digitalWrite(led, !ledDurum); // ESP8266 dahili LED ters mantikla (LOW) yanar
    }
  }
  sonDurum = okunan;
}"""
            }
        }
    },

    # 4. HC-SR04 MESAFE VE BUZZER
    "hc-sr04-radar": {
        "kategori": "Sensörler",
        "baslik": "HC-SR04 Mesafe Sensörü & Sesli Uyarı",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "HC-SR04 Ultrasonik Sensör"},
            {"adet": "1x", "isim": "5V / 3.3V Buzzer"},
            {"adet": "1x", "isim": "Breadboard"},
            {"adet": "6x", "isim": "Jumper Kablo"},
            {"adet": "2x", "isim": "1kΩ ve 2kΩ Direnç (ESP32 / ESP8266 Echo koruması)"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "HC-SR04 Trig", "pin": "D9"},
                    {"bilesen": "HC-SR04 Echo", "pin": "D10"},
                    {"bilesen": "Buzzer (+)", "pin": "D8"}
                ],
                "kod": """// Arduino Uno - HC-SR04 Park Sensoru
const int trig = 9, echo = 10, buzz = 8;

void setup() {
  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);
  pinMode(buzz, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  digitalWrite(trig, LOW); delayMicroseconds(2);
  digitalWrite(trig, HIGH); delayMicroseconds(10);
  digitalWrite(trig, LOW);

  long sure = pulseIn(echo, HIGH, 30000);
  int mesafe = (sure * 0.0343) / 2;

  if (mesafe > 0 && mesafe < 20) {
    digitalWrite(buzz, HIGH); delay(40);
    digitalWrite(buzz, LOW); delay(40);
  }
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "HC-SR04 Trig", "pin": "D9"},
                    {"bilesen": "HC-SR04 Echo", "pin": "D10"},
                    {"bilesen": "Buzzer (+)", "pin": "D8"}
                ],
                "kod": """// Arduino Nano - HC-SR04 Park Sensoru
const int trig = 9, echo = 10, buzz = 8;

void setup() {
  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);
  pinMode(buzz, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  digitalWrite(trig, LOW); delayMicroseconds(2);
  digitalWrite(trig, HIGH); delayMicroseconds(10);
  digitalWrite(trig, LOW);

  long sure = pulseIn(echo, HIGH, 30000);
  int mesafe = (sure * 0.0343) / 2;

  if (mesafe > 0 && mesafe < 20) {
    digitalWrite(buzz, HIGH); delay(40);
    digitalWrite(buzz, LOW); delay(40);
  }
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "VIN (5V) / GND"},
                    {"bilesen": "HC-SR04 Trig", "pin": "GPIO 5"},
                    {"bilesen": "HC-SR04 Echo", "pin": "GPIO 18 (1kΩ/2kΩ gerilim bölücü ile)"},
                    {"bilesen": "Buzzer (+)", "pin": "GPIO 19"}
                ],
                "kod": """// ESP32 - HC-SR04 (3.3V Lojik Guvenli)
const int trig = 5, echo = 18, buzz = 19;

void setup() {
  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);
  pinMode(buzz, OUTPUT);
  Serial.begin(115200);
}

void loop() {
  digitalWrite(trig, LOW); delayMicroseconds(2);
  digitalWrite(trig, HIGH); delayMicroseconds(10);
  digitalWrite(trig, LOW);

  long sure = pulseIn(echo, HIGH, 30000);
  int mesafe = (sure * 0.0343) / 2;

  if (mesafe > 0 && mesafe < 20) {
    digitalWrite(buzz, HIGH); delay(40);
    digitalWrite(buzz, LOW); delay(40);
  }
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "VV (5V) / GND"},
                    {"bilesen": "HC-SR04 Trig", "pin": "D1 (GPIO 5)"},
                    {"bilesen": "HC-SR04 Echo", "pin": "D2 (GPIO 4) (Gerilim bölücü)"},
                    {"bilesen": "Buzzer (+)", "pin": "D5 (GPIO 14)"}
                ],
                "kod": """// ESP8266 NodeMCU - HC-SR04 Mesafe
const int trig = D1, echo = D2, buzz = D5;

void setup() {
  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);
  pinMode(buzz, OUTPUT);
  Serial.begin(115200);
}

void loop() {
  digitalWrite(trig, LOW); delayMicroseconds(2);
  digitalWrite(trig, HIGH); delayMicroseconds(10);
  digitalWrite(trig, LOW);

  long sure = pulseIn(echo, HIGH, 30000);
  int mesafe = (sure * 0.0343) / 2;

  if (mesafe > 0 && mesafe < 20) {
    digitalWrite(buzz, HIGH); delay(40);
    digitalWrite(buzz, LOW); delay(40);
  }
}"""
            }
        }
    },

    # 5. DHT11 SICAKLIK & NEM
    "dht11-sicaklik": {
        "kategori": "Sensörler",
        "baslik": "DHT11 Dijital Sıcaklık & Nem Ölçümü",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "DHT11 Sensörü"},
            {"adet": "1x", "isim": "10kΩ Direnç (Pull-up)"},
            {"adet": "3x", "isim": "Jumper Kablo"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<DHT.h> (Adafruit DHT Sensor Library)",
                "baglanti": [
                    {"bilesen": "DHT11 VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "DHT11 DATA", "pin": "D2 (10kΩ ile 5V pull-up)"}
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
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  if (!isnan(h) && !isnan(t)) {
    Serial.print("Nem: %"); Serial.print(h);
    Serial.print(" | Sicaklik: "); Serial.print(t); Serial.println(" C");
  }
}"""
            },
            "nano": {
                "kutuphaneler": "<DHT.h> (Adafruit DHT Sensor Library)",
                "baglanti": [
                    {"bilesen": "DHT11 VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "DHT11 DATA", "pin": "D2 (10kΩ pull-up)"}
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
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  if (!isnan(h) && !isnan(t)) {
    Serial.print("Nem: %"); Serial.print(h);
    Serial.print(" | Sicaklik: "); Serial.print(t); Serial.println(" C");
  }
}"""
            },
            "esp32": {
                "kutuphaneler": "<DHT.h> (Adafruit DHT Sensor Library)",
                "baglanti": [
                    {"bilesen": "DHT11 VCC / GND", "pin": "3.3V / GND"},
                    {"bilesen": "DHT11 DATA", "pin": "GPIO 4 (4.7kΩ ile 3.3V pull-up)"}
                ],
                "kod": """#include <DHT.h>
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();
}

void loop() {
  delay(2000);
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  if (!isnan(h) && !isnan(t)) {
    Serial.print("Nem: %"); Serial.print(h);
    Serial.print(" | Sicaklik: "); Serial.print(t); Serial.println(" C");
  }
}"""
            },
            "esp8266": {
                "kutuphaneler": "<DHT.h> (Adafruit DHT Sensor Library)",
                "baglanti": [
                    {"bilesen": "DHT11 VCC / GND", "pin": "3.3V / GND"},
                    {"bilesen": "DHT11 DATA", "pin": "D4 (GPIO 2, 4.7kΩ pull-up)"}
                ],
                "kod": """#include <DHT.h>
#define DHTPIN D4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();
}

void loop() {
  delay(2000);
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  if (!isnan(h) && !isnan(t)) {
    Serial.print("Nem: %"); Serial.print(h);
    Serial.print(" | Sicaklik: "); Serial.print(t); Serial.println(" C");
  }
}"""
            }
        }
    },

    # 6. LDR IŞIK SENSÖRÜ
    "ldr-otomatik-far": {
        "kategori": "Sensörler",
        "baslik": "LDR Işık Sensörü ile Otomatik Aydınlatma",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "LDR (Fotodirenç)"},
            {"adet": "1x", "isim": "10kΩ Direnç (Bölücü)"},
            {"adet": "1x", "isim": "LED ve 220Ω Direnç"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LDR & 10k Ortak Uç", "pin": "A0 (Analog Giriş)"},
                    {"bilesen": "LDR Diğer Uç", "pin": "5V"},
                    {"bilesen": "10k Direnç Ucu", "pin": "GND"},
                    {"bilesen": "LED (+)", "pin": "D13"}
                ],
                "kod": """// Uno - LDR Otomatik Aydinlatma (10-bit: 0-1023)
const int ldr = A0, led = 13;

void setup() {
  pinMode(led, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int isik = analogRead(ldr);
  if (isik < 400) digitalWrite(led, HIGH);
  else digitalWrite(led, LOW);
  delay(100);
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LDR & 10k Ortak Uç", "pin": "A0"},
                    {"bilesen": "LDR Diğer Uç", "pin": "5V"},
                    {"bilesen": "10k Direnç Ucu", "pin": "GND"},
                    {"bilesen": "LED (+)", "pin": "D13"}
                ],
                "kod": """// Nano - LDR Otomatik Aydinlatma
const int ldr = A0, led = 13;

void setup() {
  pinMode(led, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int isik = analogRead(ldr);
  if (isik < 400) digitalWrite(led, HIGH);
  else digitalWrite(led, LOW);
  delay(100);
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LDR & 10k Ortak Uç", "pin": "GPIO 34 (ADC1, Sadece Giriş)"},
                    {"bilesen": "LDR Diğer Uç", "pin": "3.3V"},
                    {"bilesen": "10k Direnç Ucu", "pin": "GND"},
                    {"bilesen": "LED (+)", "pin": "GPIO 2"}
                ],
                "kod": """// ESP32 - LDR Aydinlatma (12-bit ADC: 0-4095)
const int ldr = 34, led = 2;

void setup() {
  pinMode(led, OUTPUT);
  Serial.begin(115200);
}

void loop() {
  int isik = analogRead(ldr);
  if (isik < 1500) digitalWrite(led, HIGH);
  else digitalWrite(led, LOW);
  delay(100);
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LDR & 10k Ortak Uç", "pin": "A0 (Tek Analog Giriş: Maks 1.0V/3.3V)"},
                    {"bilesen": "LDR Diğer Uç", "pin": "3.3V"},
                    {"bilesen": "10k Direnç Ucu", "pin": "GND"},
                    {"bilesen": "LED (+)", "pin": "D4"}
                ],
                "kod": """// ESP8266 NodeMCU - LDR Aydinlatma (10-bit: 0-1023)
const int ldr = A0, led = D4;

void setup() {
  pinMode(led, OUTPUT);
  Serial.begin(115200);
}

void loop() {
  int isik = analogRead(ldr);
  if (isik < 450) digitalWrite(led, LOW); // NodeMCU LED ters lojiktir
  else digitalWrite(led, HIGH);
  delay(100);
}"""
            }
        }
    },

    # 7. HC-SR501 PIR HAREKET
    "pir-hareket-alarm": {
        "kategori": "Sensörler",
        "baslik": "HC-SR501 PIR Hareket Dedektörü & Alarm",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "HC-SR501 PIR Sensörü"},
            {"adet": "1x", "isim": "LED ve Buzzer"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "PIR VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "PIR OUT", "pin": "D2 (Dijital Giriş)"},
                    {"bilesen": "Alarm LED", "pin": "D13"}
                ],
                "kod": """// Uno - PIR Hareket Alarmi
const int pir = 2, led = 13;

void setup() {
  pinMode(pir, INPUT);
  pinMode(led, OUTPUT);
}

void loop() {
  if (digitalRead(pir) == HIGH) digitalWrite(led, HIGH);
  else digitalWrite(led, LOW);
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "PIR VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "PIR OUT", "pin": "D2"},
                    {"bilesen": "Alarm LED", "pin": "D13"}
                ],
                "kod": """// Nano - PIR Hareket
const int pir = 2, led = 13;

void setup() {
  pinMode(pir, INPUT);
  pinMode(led, OUTPUT);
}

void loop() {
  if (digitalRead(pir) == HIGH) digitalWrite(led, HIGH);
  else digitalWrite(led, LOW);
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "PIR VCC / GND", "pin": "VIN (5V) / GND"},
                    {"bilesen": "PIR OUT", "pin": "GPIO 13 (3.3V Çıkış verir, uyumludur)"},
                    {"bilesen": "Alarm LED", "pin": "GPIO 2"}
                ],
                "kod": """// ESP32 - PIR Hareket Alarmi
const int pir = 13, led = 2;

void setup() {
  pinMode(pir, INPUT);
  pinMode(led, OUTPUT);
}

void loop() {
  if (digitalRead(pir) == HIGH) digitalWrite(led, HIGH);
  else digitalWrite(led, LOW);
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "PIR VCC / GND", "pin": "VV (5V) / GND"},
                    {"bilesen": "PIR OUT", "pin": "D7 (GPIO 13)"},
                    {"bilesen": "Alarm LED", "pin": "D4"}
                ],
                "kod": """// ESP8266 - PIR Hareket
const int pir = D7, led = D4;

void setup() {
  pinMode(pir, INPUT);
  pinMode(led, OUTPUT);
}

void loop() {
  if (digitalRead(pir) == HIGH) digitalWrite(led, LOW);
  else digitalWrite(led, HIGH);
}"""
            }
        }
    },

    # 8. 16x2 I2C LCD EKRAN
    "lcd-i2c-1602": {
        "kategori": "Ekran & Gösterge",
        "baslik": "16x2 LCD Ekran (I2C PCF8574 Modüllü)",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "16x2 I2C LCD Ekran (0x27)"},
            {"adet": "4x", "isim": "Dişi-Erkek Jumper Kablo"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<Wire.h> ve <LiquidCrystal_I2C.h>",
                "baglanti": [
                    {"bilesen": "LCD VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "LCD SDA", "pin": "A4 (veya ayrılmış SDA pini)"},
                    {"bilesen": "LCD SCL", "pin": "A5 (veya ayrılmış SCL pini)"}
                ],
                "kod": """#include <Wire.h>
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0); lcd.print("ArduKod Portal");
  lcd.setCursor(0, 1); lcd.print("Uno Aktif!");
}
void loop() {}"""
            },
            "nano": {
                "kutuphaneler": "<Wire.h> ve <LiquidCrystal_I2C.h>",
                "baglanti": [
                    {"bilesen": "LCD VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "LCD SDA", "pin": "A4"},
                    {"bilesen": "LCD SCL", "pin": "A5"}
                ],
                "kod": """#include <Wire.h>
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0); lcd.print("ArduKod Portal");
  lcd.setCursor(0, 1); lcd.print("Nano Aktif!");
}
void loop() {}"""
            },
            "esp32": {
                "kutuphaneler": "<Wire.h> ve <LiquidCrystal_I2C.h>",
                "baglanti": [
                    {"bilesen": "LCD VCC / GND", "pin": "VIN (5V) / GND"},
                    {"bilesen": "LCD SDA", "pin": "GPIO 21 (Donanımsal I2C)"},
                    {"bilesen": "LCD SCL", "pin": "GPIO 22 (Donanımsal I2C)"}
                ],
                "kod": """#include <Wire.h>
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Wire.begin(21, 22);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0); lcd.print("ESP32 IoT Hub");
  lcd.setCursor(0, 1); lcd.print("LCD Hazir!");
}
void loop() {}"""
            },
            "esp8266": {
                "kutuphaneler": "<Wire.h> ve <LiquidCrystal_I2C.h>",
                "baglanti": [
                    {"bilesen": "LCD VCC / GND", "pin": "VV (5V) / GND"},
                    {"bilesen": "LCD SDA", "pin": "D2 (GPIO 4)"},
                    {"bilesen": "LCD SCL", "pin": "D1 (GPIO 5)"}
                ],
                "kod": """#include <Wire.h>
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Wire.begin(D2, D1); // SDA=D2, SCL=D1
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0); lcd.print("NodeMCU ESP8266");
  lcd.setCursor(0, 1); lcd.print("LCD Calisiyor!");
}
void loop() {}"""
            }
        }
    },

    # 9. 0.96 OLED (SSD1306)
    "oled-ssd1306": {
        "kategori": "Ekran & Gösterge",
        "baslik": "0.96 inç I2C OLED Ekran (SSD1306 128x64)",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "0.96 I2C SSD1306 OLED"},
            {"adet": "4x", "isim": "Jumper Kablo"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<Adafruit_GFX.h> ve <Adafruit_SSD1306.h>",
                "baglanti": [
                    {"bilesen": "OLED VCC / GND", "pin": "5V veya 3.3V / GND"},
                    {"bilesen": "OLED SDA", "pin": "A4"},
                    {"bilesen": "OLED SCL", "pin": "A5"}
                ],
                "kod": """#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
Adafruit_SSD1306 display(128, 64, &Wire, -1);

void setup() {
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(10, 25);
  display.println("ArduKod OLED Uno");
  display.display();
}
void loop() {}"""
            },
            "nano": {
                "kutuphaneler": "<Adafruit_GFX.h> ve <Adafruit_SSD1306.h>",
                "baglanti": [
                    {"bilesen": "OLED VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "OLED SDA", "pin": "A4"},
                    {"bilesen": "OLED SCL", "pin": "A5"}
                ],
                "kod": """#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
Adafruit_SSD1306 display(128, 64, &Wire, -1);

void setup() {
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(10, 25);
  display.println("Nano OLED Hazir");
  display.display();
}
void loop() {}"""
            },
            "esp32": {
                "kutuphaneler": "<Adafruit_GFX.h> ve <Adafruit_SSD1306.h>",
                "baglanti": [
                    {"bilesen": "OLED VCC / GND", "pin": "3.3V / GND"},
                    {"bilesen": "OLED SDA", "pin": "GPIO 21"},
                    {"bilesen": "OLED SCL", "pin": "GPIO 22"}
                ],
                "kod": """#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
Adafruit_SSD1306 display(128, 64, &Wire, -1);

void setup() {
  Wire.begin(21, 22);
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(5, 20);
  display.println("ESP32 OLED Grafik");
  display.display();
}
void loop() {}"""
            },
            "esp8266": {
                "kutuphaneler": "<Adafruit_GFX.h> ve <Adafruit_SSD1306.h>",
                "baglanti": [
                    {"bilesen": "OLED VCC / GND", "pin": "3.3V / GND"},
                    {"bilesen": "OLED SDA", "pin": "D2 (GPIO 4)"},
                    {"bilesen": "OLED SCL", "pin": "D1 (GPIO 5)"}
                ],
                "kod": """#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
Adafruit_SSD1306 display(128, 64, &Wire, -1);

void setup() {
  Wire.begin(D2, D1);
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(10, 20);
  display.println("NodeMCU OLED OK");
  display.display();
}
void loop() {}"""
            }
        }
    },

    # 10. SG90 SERVO MOTOR
    "sg90-servo": {
        "kategori": "Motor & Sürücü",
        "baslik": "SG90 Mikro Servo Açısal Sürme (0-180°)",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "SG90 Servo Motor"},
            {"adet": "3x", "isim": "Jumper Kablo"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<Servo.h>",
                "baglanti": [
                    {"bilesen": "Servo Kırmızı (VCC)", "pin": "5V"},
                    {"bilesen": "Servo Kahve (GND)", "pin": "GND"},
                    {"bilesen": "Servo Turuncu (Sinyal)", "pin": "D9 (PWM)"}
                ],
                "kod": """#include <Servo.h>
Servo motor;

void setup() {
  motor.attach(9);
}

void loop() {
  motor.write(0); delay(1000);
  motor.write(90); delay(1000);
  motor.write(180); delay(1000);
}"""
            },
            "nano": {
                "kutuphaneler": "<Servo.h>",
                "baglanti": [
                    {"bilesen": "Servo VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "Servo Sinyal", "pin": "D9"}
                ],
                "kod": """#include <Servo.h>
Servo motor;

void setup() {
  motor.attach(9);
}

void loop() {
  motor.write(0); delay(1000);
  motor.write(90); delay(1000);
  motor.write(180); delay(1000);
}"""
            },
            "esp32": {
                "kutuphaneler": "<ESP32Servo.h>",
                "baglanti": [
                    {"bilesen": "Servo VCC / GND", "pin": "VIN (5V) / GND"},
                    {"bilesen": "Servo Sinyal", "pin": "GPIO 18"}
                ],
                "kod": """#include <ESP32Servo.h>
Servo motor;

void setup() {
  motor.setPeriodHertz(50); // Standart 50Hz servo
  motor.attach(18, 500, 2400);
}

void loop() {
  motor.write(0); delay(1000);
  motor.write(90); delay(1000);
  motor.write(180); delay(1000);
}"""
            },
            "esp8266": {
                "kutuphaneler": "<Servo.h>",
                "baglanti": [
                    {"bilesen": "Servo VCC / GND", "pin": "VV (5V) / GND"},
                    {"bilesen": "Servo Sinyal", "pin": "D4 (GPIO 2)"}
                ],
                "kod": """#include <Servo.h>
Servo motor;

void setup() {
  motor.attach(D4);
}

void loop() {
  motor.write(0); delay(1000);
  motor.write(90); delay(1000);
  motor.write(180); delay(1000);
}"""
            }
        }
    },

    # 11. 28BYJ-48 STEP MOTOR (ULN2003)
    "step-motor-uln2003": {
        "kategori": "Motor & Sürücü",
        "baslik": "28BYJ-48 Step Motor & ULN2003 Sürücü",
        "zorluk": "Orta",
        "sure": "20 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "28BYJ-48 Step Motor"},
            {"adet": "1x", "isim": "ULN2003 Sürücü Kartı"},
            {"adet": "6x", "isim": "Jumper Kablo"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<Stepper.h>",
                "baglanti": [
                    {"bilesen": "ULN2003 VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "IN1, IN2, IN3, IN4", "pin": "D8, D9, D10, D11"}
                ],
                "kod": """#include <Stepper.h>
const int adim = 2048; // 1 tam tur
Stepper adimMotoru(adim, 8, 10, 9, 11);

void setup() {
  adimMotoru.setSpeed(10);
}

void loop() {
  adimMotoru.step(adim); delay(1000);
  adimMotoru.step(-adim); delay(1000);
}"""
            },
            "nano": {
                "kutuphaneler": "<Stepper.h>",
                "baglanti": [
                    {"bilesen": "ULN2003 VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "IN1, IN2, IN3, IN4", "pin": "D8, D9, D10, D11"}
                ],
                "kod": """#include <Stepper.h>
const int adim = 2048;
Stepper adimMotoru(adim, 8, 10, 9, 11);

void setup() {
  adimMotoru.setSpeed(10);
}

void loop() {
  adimMotoru.step(adim); delay(1000);
  adimMotoru.step(-adim); delay(1000);
}"""
            },
            "esp32": {
                "kutuphaneler": "<Stepper.h>",
                "baglanti": [
                    {"bilesen": "ULN2003 VCC / GND", "pin": "VIN (5V) / GND"},
                    {"bilesen": "IN1, IN2, IN3, IN4", "pin": "GPIO 19, 18, 5, 17"}
                ],
                "kod": """#include <Stepper.h>
const int adim = 2048;
Stepper adimMotoru(adim, 19, 5, 18, 17);

void setup() {
  adimMotoru.setSpeed(12);
}

void loop() {
  adimMotoru.step(adim); delay(1000);
  adimMotoru.step(-adim); delay(1000);
}"""
            },
            "esp8266": {
                "kutuphaneler": "<Stepper.h>",
                "baglanti": [
                    {"bilesen": "ULN2003 VCC / GND", "pin": "VV (5V) / GND"},
                    {"bilesen": "IN1, IN2, IN3, IN4", "pin": "D5, D6, D7, D8"}
                ],
                "kod": """#include <Stepper.h>
const int adim = 2048;
Stepper adimMotoru(adim, D5, D7, D6, D8);

void setup() {
  adimMotoru.setSpeed(10);
}

void loop() {
  adimMotoru.step(adim); delay(1000);
  adimMotoru.step(-adim); delay(1000);
}"""
            }
        }
    },

    # 12. L298N ÇİFT DC MOTOR
    "l298n-dc-motor": {
        "kategori": "Motor & Sürücü",
        "baslik": "L298N Çift DC Motor Hız ve Yön Kontrolü",
        "zorluk": "Orta",
        "sure": "20 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "L298N Sürücü Kartı"},
            {"adet": "1x", "isim": "DC Motor"},
            {"adet": "1x", "isim": "Harici Pil / Güç Kaynağı"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "L298N GND", "pin": "Arduino GND (Ortak Toprak)"},
                    {"bilesen": "IN1 / IN2", "pin": "D7 / D8 (Yön)"},
                    {"bilesen": "ENA (Hız)", "pin": "D6 (PWM)"}
                ],
                "kod": """// Uno - L298N Motor
const int in1 = 7, in2 = 8, ena = 6;

void setup() {
  pinMode(in1, OUTPUT); pinMode(in2, OUTPUT); pinMode(ena, OUTPUT);
}

void loop() {
  digitalWrite(in1, HIGH); digitalWrite(in2, LOW);
  analogWrite(ena, 200); delay(2000); // İleri
  digitalWrite(in1, LOW); digitalWrite(in2, HIGH);
  analogWrite(ena, 150); delay(2000); // Geri
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "L298N GND", "pin": "Nano GND"},
                    {"bilesen": "IN1 / IN2", "pin": "D7 / D8"},
                    {"bilesen": "ENA", "pin": "D6 (PWM)"}
                ],
                "kod": """// Nano - L298N Motor
const int in1 = 7, in2 = 8, ena = 6;

void setup() {
  pinMode(in1, OUTPUT); pinMode(in2, OUTPUT); pinMode(ena, OUTPUT);
}

void loop() {
  digitalWrite(in1, HIGH); digitalWrite(in2, LOW);
  analogWrite(ena, 200); delay(2000);
  digitalWrite(in1, LOW); digitalWrite(in2, HIGH);
  delay(2000);
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "L298N GND", "pin": "ESP32 GND"},
                    {"bilesen": "IN1 / IN2", "pin": "GPIO 18 / GPIO 19"},
                    {"bilesen": "ENA", "pin": "GPIO 23 (PWM)"}
                ],
                "kod": """// ESP32 - L298N Donanimsal PWM ile Motor
const int in1 = 18, in2 = 19, ena = 23;

void setup() {
  pinMode(in1, OUTPUT); pinMode(in2, OUTPUT);
  ledcAttach(ena, 1000, 8); // 1kHz 8-bit
}

void loop() {
  digitalWrite(in1, HIGH); digitalWrite(in2, LOW);
  ledcWrite(ena, 220); delay(2000);
  digitalWrite(in1, LOW); digitalWrite(in2, HIGH);
  ledcWrite(ena, 180); delay(2000);
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "L298N GND", "pin": "NodeMCU GND"},
                    {"bilesen": "IN1 / IN2", "pin": "D5 / D6"},
                    {"bilesen": "ENA", "pin": "D1"}
                ],
                "kod": """// NodeMCU - L298N Motor
const int in1 = D5, in2 = D6, ena = D1;

void setup() {
  pinMode(in1, OUTPUT); pinMode(in2, OUTPUT); pinMode(ena, OUTPUT);
}

void loop() {
  digitalWrite(in1, HIGH); digitalWrite(in2, LOW);
  analogWrite(ena, 700); delay(2000);
  digitalWrite(in1, LOW); digitalWrite(in2, HIGH);
  analogWrite(ena, 500); delay(2000);
}"""
            }
        }
    },

    # 13. 5V RÖLE İLE 220V KONTROLÜ
    "role-modulu-kontrol": {
        "kategori": "Giriş & Kontrol",
        "baslik": "5V Tek Kanal Röle Modülü ile Yüksek Güç Anahtarlama",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "5V veya 3.3V Optokuplörlü Röle"},
            {"adet": "3x", "isim": "Jumper Kablo"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "Röle VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "Röle IN", "pin": "D7 (Ters Mantık: LOW ile çeker)"}
                ],
                "kod": """// Uno - 5V Role Kontrolu (Active LOW)
const int role = 7;

void setup() {
  pinMode(role, OUTPUT);
  digitalWrite(role, HIGH); // Baslangicta kapali
}

void loop() {
  digitalWrite(role, LOW); delay(2000);  // Role CEKTI
  digitalWrite(role, HIGH); delay(2000); // Role BIRAKTI
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "Röle VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "Röle IN", "pin": "D7"}
                ],
                "kod": """// Nano - Role Kontrolu
const int role = 7;

void setup() {
  pinMode(role, OUTPUT);
  digitalWrite(role, HIGH);
}

void loop() {
  digitalWrite(role, LOW); delay(2000);
  digitalWrite(role, HIGH); delay(2000);
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "Röle VCC / GND", "pin": "VIN (5V) / GND"},
                    {"bilesen": "Röle IN", "pin": "GPIO 26"}
                ],
                "kod": """// ESP32 - 3.3V Uyumlu Optokuplorlu Role
const int role = 26;

void setup() {
  pinMode(role, OUTPUT);
  digitalWrite(role, HIGH);
}

void loop() {
  digitalWrite(role, LOW); delay(2000);
  digitalWrite(role, HIGH); delay(2000);
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "Röle VCC / GND", "pin": "VV (5V) / GND"},
                    {"bilesen": "Röle IN", "pin": "D6 (GPIO 12)"}
                ],
                "kod": """// ESP8266 - Role Modulu
const int role = D6;

void setup() {
  pinMode(role, OUTPUT);
  digitalWrite(role, HIGH);
}

void loop() {
  digitalWrite(role, LOW); delay(2000);
  digitalWrite(role, HIGH); delay(2000);
}"""
            }
        }
    },

    # 14. POTANSİYOMETRE İLE MAP
    "pot-analog-map": {
        "kategori": "Giriş & Kontrol",
        "baslik": "Potansiyometre ile LED Parlaklığı (map fonksiyonu)",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "10kΩ Potansiyometre"},
            {"adet": "1x", "isim": "5mm LED & 220Ω Direnç"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "Pot Orta Uç", "pin": "A0"},
                    {"bilesen": "Pot Yan Uçlar", "pin": "5V ve GND"},
                    {"bilesen": "LED (+)", "pin": "D9 (PWM)"}
                ],
                "kod": """// Uno - 10-bit Analog'tan 8-bit PWM'e Map
const int pot = A0, led = 9;

void setup() { pinMode(led, OUTPUT); }

void loop() {
  int ham = analogRead(pot);
  int parlaklik = map(ham, 0, 1023, 0, 255);
  analogWrite(led, parlaklik);
  delay(10);
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "Pot Orta Uç", "pin": "A0"},
                    {"bilesen": "Pot Yan Uçlar", "pin": "5V ve GND"},
                    {"bilesen": "LED (+)", "pin": "D9 (PWM)"}
                ],
                "kod": """// Nano - Pot Kontrol
const int pot = A0, led = 9;

void setup() { pinMode(led, OUTPUT); }

void loop() {
  int ham = analogRead(pot);
  analogWrite(led, map(ham, 0, 1023, 0, 255));
  delay(10);
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "Pot Orta Uç", "pin": "GPIO 32 (ADC1)"},
                    {"bilesen": "Pot Yan Uçlar", "pin": "3.3V ve GND"},
                    {"bilesen": "LED (+)", "pin": "GPIO 18"}
                ],
                "kod": """// ESP32 - 12-bit Analog (0-4095) ile PWM
const int pot = 32, led = 18;

void setup() {
  ledcAttach(led, 5000, 8);
}

void loop() {
  int ham = analogRead(pot);
  int pwmVal = map(ham, 0, 4095, 0, 255);
  ledcWrite(led, pwmVal);
  delay(10);
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "Pot Orta Uç", "pin": "A0 (Maks 1.0V/3.3V)"},
                    {"bilesen": "Pot Yan Uçlar", "pin": "3.3V ve GND"},
                    {"bilesen": "LED (+)", "pin": "D1"}
                ],
                "kod": """// NodeMCU - Pot Parlaklik
const int pot = A0, led = D1;

void setup() { pinMode(led, OUTPUT); }

void loop() {
  int ham = analogRead(pot); // 0-1023
  analogWrite(led, ham);     // ESP8266 PWM 0-1023
  delay(10);
}"""
            }
        }
    },

    # 15. RC522 RFID KART OKUYUCU
    "rc522-rfid-okuyucu": {
        "kategori": "Sensörler",
        "baslik": "RC522 RFID 13.56MHz SPI Kart Okuyucu",
        "zorluk": "İleri",
        "sure": "25 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "MFRC522 RFID Okuyucu"},
            {"adet": "1x", "isim": "RFID Kart / Anahtarlık"},
            {"adet": "7x", "isim": "Dişi-Erkek Jumper"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<SPI.h> ve <MFRC522.h>",
                "baglanti": [
                    {"bilesen": "RC522 3.3V / GND", "pin": "3.3V (Asla 5V verme!) / GND"},
                    {"bilesen": "RC522 RST / SDA (SS)", "pin": "D9 / D10"},
                    {"bilesen": "MOSI / MISO / SCK", "pin": "D11 / D12 / D13"}
                ],
                "kod": """#include <SPI.h>
#include <MFRC522.h>
#define SS_PIN 10
#define RST_PIN 9
MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  Serial.println("Karti yaklastirin...");
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;
  Serial.print("Kart UID: ");
  for (byte i = 0; i < rfid.uid.size; i++) {
    Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(rfid.uid.uidByte[i], HEX);
  }
  Serial.println();
  rfid.PICC_HaltA();
}"""
            },
            "nano": {
                "kutuphaneler": "<SPI.h> ve <MFRC522.h>",
                "baglanti": [
                    {"bilesen": "RC522 VCC (3.3V)", "pin": "3.3V"},
                    {"bilesen": "RST / SDA(SS)", "pin": "D9 / D10"},
                    {"bilesen": "MOSI / MISO / SCK", "pin": "D11 / D12 / D13"}
                ],
                "kod": """#include <SPI.h>
#include <MFRC522.h>
MFRC522 rfid(10, 9);

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;
  Serial.println("Kart Algilandi!");
  rfid.PICC_HaltA();
}"""
            },
            "esp32": {
                "kutuphaneler": "<SPI.h> ve <MFRC522.h>",
                "baglanti": [
                    {"bilesen": "RC522 3.3V / GND", "pin": "3.3V / GND"},
                    {"bilesen": "RST / SS", "pin": "GPIO 22 / GPIO 5"},
                    {"bilesen": "MOSI / MISO / SCK", "pin": "GPIO 23 / GPIO 19 / GPIO 18"}
                ],
                "kod": """#include <SPI.h>
#include <MFRC522.h>
#define SS_PIN 5
#define RST_PIN 22
MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(115200);
  SPI.begin(18, 19, 23, 5); // SCK, MISO, MOSI, SS
  rfid.PCD_Init();
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;
  Serial.print("ESP32 Kart UID: ");
  for (byte i = 0; i < rfid.uid.size; i++) Serial.print(rfid.uid.uidByte[i], HEX);
  Serial.println();
  rfid.PICC_HaltA();
}"""
            },
            "esp8266": {
                "kutuphaneler": "<SPI.h> ve <MFRC522.h>",
                "baglanti": [
                    {"bilesen": "RC522 3.3V / GND", "pin": "3.3V / GND"},
                    {"bilesen": "RST / SS (SDA)", "pin": "D3 (GPIO 0) / D8 (GPIO 15)"},
                    {"bilesen": "MOSI / MISO / SCK", "pin": "D7 / D6 / D5"}
                ],
                "kod": """#include <SPI.h>
#include <MFRC522.h>
MFRC522 rfid(D8, D3);

void setup() {
  Serial.begin(115200);
  SPI.begin();
  rfid.PCD_Init();
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;
  Serial.println("NodeMCU RFID Kart Okundu!");
  rfid.PICC_HaltA();
}"""
            }
        }
    },

    # 16. MPU6050 JİROSKOP & İVMEÖLÇER
    "mpu6050-jiroskop": {
        "kategori": "Sensörler",
        "baslik": "MPU6050 6-Eksen İvme ve Jiroskop Sensörü",
        "zorluk": "İleri",
        "sure": "20 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "MPU-6050 I2C Modülü"},
            {"adet": "4x", "isim": "Jumper Kablo"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<Wire.h> ve <MPU6050_light.h>",
                "baglanti": [
                    {"bilesen": "MPU6050 VCC / GND", "pin": "5V (veya 3.3V) / GND"},
                    {"bilesen": "MPU6050 SDA / SCL", "pin": "A4 / A5"}
                ],
                "kod": """#include <Wire.h>
#include <MPU6050_light.h>
MPU6050 mpu(Wire);

void setup() {
  Serial.begin(9600);
  Wire.begin();
  mpu.begin();
  mpu.calcOffsets(); // Kalibrasyon
}

void loop() {
  mpu.update();
  Serial.print("X: "); Serial.print(mpu.getAngleX());
  Serial.print(" | Y: "); Serial.println(mpu.getAngleY());
  delay(100);
}"""
            },
            "nano": {
                "kutuphaneler": "<Wire.h> ve <MPU6050_light.h>",
                "baglanti": [
                    {"bilesen": "MPU6050 VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "MPU6050 SDA / SCL", "pin": "A4 / A5"}
                ],
                "kod": """#include <Wire.h>
#include <MPU6050_light.h>
MPU6050 mpu(Wire);

void setup() {
  Serial.begin(9600);
  Wire.begin();
  mpu.begin();
  mpu.calcOffsets();
}

void loop() {
  mpu.update();
  Serial.println(mpu.getAngleZ());
  delay(100);
}"""
            },
            "esp32": {
                "kutuphaneler": "<Wire.h> ve <MPU6050_light.h>",
                "baglanti": [
                    {"bilesen": "MPU6050 VCC / GND", "pin": "3.3V / GND"},
                    {"bilesen": "MPU6050 SDA / SCL", "pin": "GPIO 21 / GPIO 22"}
                ],
                "kod": """#include <Wire.h>
#include <MPU6050_light.h>
MPU6050 mpu(Wire);

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  mpu.begin();
  mpu.calcOffsets();
}

void loop() {
  mpu.update();
  Serial.printf("Aci X: %.2f | Y: %.2f\\n", mpu.getAngleX(), mpu.getAngleY());
  delay(50);
}"""
            },
            "esp8266": {
                "kutuphaneler": "<Wire.h> ve <MPU6050_light.h>",
                "baglanti": [
                    {"bilesen": "MPU6050 VCC / GND", "pin": "3.3V / GND"},
                    {"bilesen": "MPU6050 SDA / SCL", "pin": "D2 (GPIO 4) / D1 (GPIO 5)"}
                ],
                "kod": """#include <Wire.h>
#include <MPU6050_light.h>
MPU6050 mpu(Wire);

void setup() {
  Serial.begin(115200);
  Wire.begin(D2, D1);
  mpu.begin();
  mpu.calcOffsets();
}

void loop() {
  mpu.update();
  Serial.println(mpu.getAngleX());
  delay(100);
}"""
            }
        }
    },

    # 17. BMP280 BASINÇ & RAKIM
    "bmp280-barometre": {
        "kategori": "Sensörler",
        "baslik": "BMP280 Barometrik Basınç ve Rakım Sensörü",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "BMP280 I2C Barometre (3.3V)"},
            {"adet": "4x", "isim": "Jumper Kablo"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<Adafruit_BMP280.h>",
                "baglanti": [
                    {"bilesen": "BMP280 VCC (DİKKAT: 3.3V!)", "pin": "3.3V"},
                    {"bilesen": "BMP280 GND", "pin": "GND"},
                    {"bilesen": "SDA / SCL", "pin": "A4 / A5"}
                ],
                "kod": """#include <Wire.h>
#include <Adafruit_BMP280.h>
Adafruit_BMP280 bmp;

void setup() {
  Serial.begin(9600);
  if (!bmp.begin(0x76)) Serial.println("BMP280 bulunamadi (0x76/0x77)");
}

void loop() {
  Serial.print("Basinc: "); Serial.print(bmp.readPressure() / 100.0F); Serial.println(" hPa");
  Serial.print("Yaklasik Rakim: "); Serial.print(bmp.readAltitude(1013.25)); Serial.println(" m");
  delay(2000);
}"""
            },
            "nano": {
                "kutuphaneler": "<Adafruit_BMP280.h>",
                "baglanti": [
                    {"bilesen": "BMP280 3.3V / GND", "pin": "3.3V / GND"},
                    {"bilesen": "SDA / SCL", "pin": "A4 / A5"}
                ],
                "kod": """#include <Wire.h>
#include <Adafruit_BMP280.h>
Adafruit_BMP280 bmp;

void setup() {
  Serial.begin(9600);
  bmp.begin(0x76);
}

void loop() {
  Serial.println(bmp.readPressure() / 100.0F);
  delay(2000);
}"""
            },
            "esp32": {
                "kutuphaneler": "<Adafruit_BMP280.h>",
                "baglanti": [
                    {"bilesen": "BMP280 3.3V / GND", "pin": "3.3V / GND"},
                    {"bilesen": "SDA / SCL", "pin": "GPIO 21 / GPIO 22"}
                ],
                "kod": """#include <Wire.h>
#include <Adafruit_BMP280.h>
Adafruit_BMP280 bmp;

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  bmp.begin(0x76);
}

void loop() {
  Serial.printf("Basinc: %.2f hPa | Rakim: %.1f m\\n", bmp.readPressure()/100.0F, bmp.readAltitude(1013.25));
  delay(2000);
}"""
            },
            "esp8266": {
                "kutuphaneler": "<Adafruit_BMP280.h>",
                "baglanti": [
                    {"bilesen": "BMP280 3.3V / GND", "pin": "3.3V / GND"},
                    {"bilesen": "SDA / SCL", "pin": "D2 (GPIO 4) / D1 (GPIO 5)"}
                ],
                "kod": """#include <Wire.h>
#include <Adafruit_BMP280.h>
Adafruit_BMP280 bmp;

void setup() {
  Serial.begin(115200);
  Wire.begin(D2, D1);
  bmp.begin(0x76);
}

void loop() {
  Serial.println(bmp.readPressure() / 100.0F);
  delay(2000);
}"""
            }
        }
    },

    # 18. NRF24L01 KABLOSUZ İLETİŞİM
    "nrf24l01-kablosuz": {
        "kategori": "Haberleşme & IoT",
        "baslik": "NRF24L01 2.4GHz RF Kablosuz Verici (Transmitter)",
        "zorluk": "İleri",
        "sure": "25 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "nRF24L01+ Modülü"},
            {"adet": "1x", "isim": "10µF veya 100µF Elektrolitik Kondansatör (Parazit için)"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<SPI.h> ve <RF24.h>",
                "baglanti": [
                    {"bilesen": "NRF24 VCC (DİKKAT: 3.3V!)", "pin": "Arduino 3.3V (Kondansatör paralel)"},
                    {"bilesen": "CE / CSN", "pin": "D9 / D10"},
                    {"bilesen": "SCK / MOSI / MISO", "pin": "D13 / D11 / D12"}
                ],
                "kod": """#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9, 10);
const byte adres[6] = "00001";

void setup() {
  radio.begin();
  radio.openWritingPipe(adres);
  radio.setPALevel(RF24_PA_LOW);
  radio.stopListening();
}

void loop() {
  const char mesaj[] = "ArduKod Selam!";
  radio.write(&mesaj, sizeof(mesaj));
  delay(1000);
}"""
            },
            "nano": {
                "kutuphaneler": "<SPI.h> ve <RF24.h>",
                "baglanti": [
                    {"bilesen": "NRF24 3.3V / GND", "pin": "Nano 3.3V / GND"},
                    {"bilesen": "CE / CSN", "pin": "D9 / D10"},
                    {"bilesen": "SCK / MOSI / MISO", "pin": "D13 / D11 / D12"}
                ],
                "kod": """#include <SPI.h>
#include <RF24.h>
RF24 radio(9, 10);
const byte adres[6] = "00001";

void setup() {
  radio.begin();
  radio.openWritingPipe(adres);
  radio.stopListening();
}

void loop() {
  const char metin[] = "Nano Veri";
  radio.write(&metin, sizeof(metin));
  delay(1000);
}"""
            },
            "esp32": {
                "kutuphaneler": "<SPI.h> ve <RF24.h>",
                "baglanti": [
                    {"bilesen": "NRF24 3.3V / GND", "pin": "3.3V / GND"},
                    {"bilesen": "CE / CSN", "pin": "GPIO 4 / GPIO 5"},
                    {"bilesen": "SCK / MOSI / MISO", "pin": "GPIO 18 / GPIO 23 / GPIO 19"}
                ],
                "kod": """#include <SPI.h>
#include <RF24.h>
RF24 radio(4, 5);
const byte adres[6] = "00001";

void setup() {
  radio.begin();
  radio.openWritingPipe(adres);
  radio.stopListening();
}

void loop() {
  const char metin[] = "ESP32 RF";
  radio.write(&metin, sizeof(metin));
  delay(1000);
}"""
            },
            "esp8266": {
                "kutuphaneler": "<SPI.h> ve <RF24.h>",
                "baglanti": [
                    {"bilesen": "NRF24 3.3V / GND", "pin": "3.3V / GND"},
                    {"bilesen": "CE / CSN", "pin": "D2 (GPIO 4) / D8 (GPIO 15)"},
                    {"bilesen": "SCK / MOSI / MISO", "pin": "D5 / D7 / D6"}
                ],
                "kod": """#include <SPI.h>
#include <RF24.h>
RF24 radio(D2, D8);
const byte adres[6] = "00001";

void setup() {
  radio.begin();
  radio.openWritingPipe(adres);
  radio.stopListening();
}

void loop() {
  const char metin[] = "ESP8266 RF";
  radio.write(&metin, sizeof(metin));
  delay(1000);
}"""
            }
        }
    },

    # 19. MAX7219 8x8 LED MATRİS
    "max7219-matris": {
        "kategori": "Ekran & Gösterge",
        "baslik": "MAX7219 Dot Matrix 8x8 LED Ekran",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "MAX7219 8x8 Dot Matris Modülü"},
            {"adet": "5x", "isim": "Jumper Kablo"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<LedControl.h>",
                "baglanti": [
                    {"bilesen": "Matris VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "DIN / CS / CLK", "pin": "D12 / D10 / D11"}
                ],
                "kod": """#include <LedControl.h>
LedControl lc = LedControl(12, 11, 10, 1); // DIN, CLK, CS, 1 Cihaz

void setup() {
  lc.shutdown(0, false);
  lc.setIntensity(0, 8); // Parlaklik 0-15
  lc.clearDisplay(0);
}

void loop() {
  for (int r = 0; r < 8; r++) {
    for (int c = 0; c < 8; c++) {
      lc.setLed(0, r, c, true);
      delay(30);
      lc.setLed(0, r, c, false);
    }
  }
}"""
            },
            "nano": {
                "kutuphaneler": "<LedControl.h>",
                "baglanti": [
                    {"bilesen": "Matris VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "DIN / CS / CLK", "pin": "D12 / D10 / D11"}
                ],
                "kod": """#include <LedControl.h>
LedControl lc = LedControl(12, 11, 10, 1);

void setup() {
  lc.shutdown(0, false);
  lc.setIntensity(0, 8);
  lc.clearDisplay(0);
}

void loop() {
  lc.setRow(0, 3, B00111100);
  delay(1000);
  lc.clearDisplay(0);
  delay(500);
}"""
            },
            "esp32": {
                "kutuphaneler": "<LedControl.h>",
                "baglanti": [
                    {"bilesen": "Matris VCC / GND", "pin": "VIN (5V) / GND"},
                    {"bilesen": "DIN / CS / CLK", "pin": "GPIO 23 / GPIO 5 / GPIO 18"}
                ],
                "kod": """#include <LedControl.h>
LedControl lc = LedControl(23, 18, 5, 1); // DIN, CLK, CS

void setup() {
  lc.shutdown(0, false);
  lc.setIntensity(0, 6);
  lc.clearDisplay(0);
}

void loop() {
  lc.setRow(0, 0, B11111111);
  delay(500);
  lc.clearDisplay(0);
  delay(500);
}"""
            },
            "esp8266": {
                "kutuphaneler": "<LedControl.h>",
                "baglanti": [
                    {"bilesen": "Matris VCC / GND", "pin": "VV (5V) / GND"},
                    {"bilesen": "DIN / CS / CLK", "pin": "D7 (GPIO 13) / D8 (GPIO 15) / D5 (GPIO 14)"}
                ],
                "kod": """#include <LedControl.h>
LedControl lc = LedControl(D7, D5, D8, 1);

void setup() {
  lc.shutdown(0, false);
  lc.setIntensity(0, 6);
  lc.clearDisplay(0);
}

void loop() {
  lc.setLed(0, 4, 4, true);
  delay(500);
  lc.clearDisplay(0);
  delay(500);
}"""
            }
        }
    },

    # 20. DS18B20 SU GEÇİRMEZ SICAKLIK
    "ds18b20-su-sicaklik": {
        "kategori": "Sensörler",
        "baslik": "DS18B20 Su Geçirmez Dijital Termometre (1-Wire)",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "DS18B20 Su Geçirmez Sensör"},
            {"adet": "1x", "isim": "4.7kΩ Direnç (Pull-up zorunlu)"},
            {"adet": "3x", "isim": "Jumper Kablo"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "<OneWire.h> ve <DallasTemperature.h>",
                "baglanti": [
                    {"bilesen": "DS18B20 Kırmızı (VCC)", "pin": "5V"},
                    {"bilesen": "DS18B20 Siyah (GND)", "pin": "GND"},
                    {"bilesen": "DS18B20 Sarı (DATA)", "pin": "D2 (4.7kΩ ile 5V'a pull-up)"}
                ],
                "kod": """#include <OneWire.h>
#include <DallasTemperature.h>
#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(9600);
  sensors.begin();
}

void loop() {
  sensors.requestTemperatures();
  float sicaklik = sensors.getTempCByIndex(0);
  Serial.print("Su Sicakligi: "); Serial.print(sicaklik); Serial.println(" C");
  delay(1500);
}"""
            },
            "nano": {
                "kutuphaneler": "<OneWire.h> ve <DallasTemperature.h>",
                "baglanti": [
                    {"bilesen": "DS18B20 Kırmızı / Siyah", "pin": "5V / GND"},
                    {"bilesen": "DS18B20 Sarı (DATA)", "pin": "D2 (4.7kΩ pull-up)"}
                ],
                "kod": """#include <OneWire.h>
#include <DallasTemperature.h>
OneWire oneWire(2);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(9600);
  sensors.begin();
}

void loop() {
  sensors.requestTemperatures();
  Serial.println(sensors.getTempCByIndex(0));
  delay(1500);
}"""
            },
            "esp32": {
                "kutuphaneler": "<OneWire.h> ve <DallasTemperature.h>",
                "baglanti": [
                    {"bilesen": "DS18B20 Kırmızı / Siyah", "pin": "3.3V / GND"},
                    {"bilesen": "DS18B20 Sarı (DATA)", "pin": "GPIO 4 (4.7kΩ ile 3.3V pull-up)"}
                ],
                "kod": """#include <OneWire.h>
#include <DallasTemperature.h>
#define ONE_WIRE_BUS 4
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(115200);
  sensors.begin();
}

void loop() {
  sensors.requestTemperatures();
  Serial.printf("ESP32 Sicaklik: %.2f C\\n", sensors.getTempCByIndex(0));
  delay(1500);
}"""
            },
            "esp8266": {
                "kutuphaneler": "<OneWire.h> ve <DallasTemperature.h>",
                "baglanti": [
                    {"bilesen": "DS18B20 Kırmızı / Siyah", "pin": "3.3V / GND"},
                    {"bilesen": "DS18B20 Sarı (DATA)", "pin": "D4 (GPIO 2, 4.7kΩ pull-up)"}
                ],
                "kod": """#include <OneWire.h>
#include <DallasTemperature.h>
#define ONE_WIRE_BUS D4
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(115200);
  sensors.begin();
}

void loop() {
  sensors.requestTemperatures();
  Serial.println(sensors.getTempCByIndex(0));
  delay(1500);
}"""
            }
        }
    }
}

# --- ROTALAR ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projeler', methods=['GET'])
def projeleri_getir():
    liste = []
    for anahtar, detay in PROJELER.items():
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
    if id in PROJELER:
        return jsonify({"durum": "basarili", "veri": PROJELER[id]})
    return jsonify({"durum": "hata", "mesaj": "Proje bulunamadı."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
