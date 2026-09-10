from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "ardukod_gizli_anahtar_123"
ADMIN_SIFRE = "admin123"

# ==============================================================================
# ÇOKLU KART DESTEKLİ, DOĞRULANMIŞ PROJELER (Uno, Nano, ESP32, ESP8266)
# ==============================================================================
PROJELER = {
    "kara-simsek": {
        "kategori": "Temel & LED",
        "baslik": "5 LED Kademeli Kara Şimşek",
        "kutuphaneler": "Harici kütüphane gerekmez.",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "5x", "isim": "5mm LED"},
            {"adet": "5x", "isim": "220Ω / 330Ω Direnç"},
            {"adet": "1x", "isim": "Breadboard"},
            {"adet": "6x", "isim": "Erkek-Erkek Jumper"}
        ],
        "sema_url": "",
        "kartlar": {
            "uno": {
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "Arduino GND"}
                ],
                "kod": """// Arduino Uno - 5 LED Kara Simsek
const int pinler[] = {2, 3, 4, 5, 6};
const int adet = 5;

void setup() {
  for (int i = 0; i < adet; i++) {
    pinMode(pinler[i], OUTPUT);
  }
}

void loop() {
  for (int i = 0; i < adet; i++) {
    digitalWrite(pinler[i], HIGH);
    delay(60);
    digitalWrite(pinler[i], LOW);
  }
  for (int i = adet - 2; i > 0; i--) {
    digitalWrite(pinler[i], HIGH);
    delay(60);
    digitalWrite(pinler[i], LOW);
  }
}"""
            },
            "nano": {
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "Nano GND"}
                ],
                "kod": """// Arduino Nano - 5 LED Kara Simsek
const int pinler[] = {2, 3, 4, 5, 6};
const int adet = 5;

void setup() {
  for (int i = 0; i < adet; i++) {
    pinMode(pinler[i], OUTPUT);
  }
}

void loop() {
  for (int i = 0; i < adet; i++) {
    digitalWrite(pinler[i], HIGH);
    delay(60);
    digitalWrite(pinler[i], LOW);
  }
  for (int i = adet - 2; i > 0; i--) {
    digitalWrite(pinler[i], HIGH);
    delay(60);
    digitalWrite(pinler[i], LOW);
  }
}"""
            },
            "esp32": {
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "GPIO 18, 19, 21, 22, 23 (330Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "ESP32 GND"}
                ],
                "kod": """// ESP32 - 5 LED Kara Simsek (3.3V Lojik)
const int pinler[] = {18, 19, 21, 22, 23};
const int adet = 5;

void setup() {
  for (int i = 0; i < adet; i++) {
    pinMode(pinler[i], OUTPUT);
  }
}

void loop() {
  for (int i = 0; i < adet; i++) {
    digitalWrite(pinler[i], HIGH);
    delay(60);
    digitalWrite(pinler[i], LOW);
  }
  for (int i = adet - 2; i > 0; i--) {
    digitalWrite(pinler[i], HIGH);
    delay(60);
    digitalWrite(pinler[i], LOW);
  }
}"""
            },
            "esp8266": {
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D1, D2, D5, D6, D7 (GPIO 5, 4, 14, 12, 13)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "NodeMCU GND"}
                ],
                "kod": """// ESP8266 NodeMCU - 5 LED Kara Simsek
const int pinler[] = {D1, D2, D5, D6, D7};
const int adet = 5;

void setup() {
  for (int i = 0; i < adet; i++) {
    pinMode(pinler[i], OUTPUT);
  }
}

void loop() {
  for (int i = 0; i < adet; i++) {
    digitalWrite(pinler[i], HIGH);
    delay(60);
    digitalWrite(pinler[i], LOW);
  }
  for (int i = adet - 2; i > 0; i--) {
    digitalWrite(pinler[i], HIGH);
    delay(60);
    digitalWrite(pinler[i], LOW);
  }
}"""
            }
        }
    },
    "hc-sr04-radar": {
        "kategori": "Sensörler",
        "baslik": "HC-SR04 Mesafe Sensörü & Sesli Uyarı",
        "kutuphaneler": "Harici kütüphane gerekmez.",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "HC-SR04 Ultrasonik Sensör"},
            {"adet": "1x", "isim": "Buzzer"},
            {"adet": "1x", "isim": "Breadboard"},
            {"adet": "6x", "isim": "Jumper Kablo"},
            {"adet": "2x", "isim": "1kΩ ve 2kΩ Direnç (ESP voltaj bölücü için)"}
        ],
        "sema_url": "",
        "kartlar": {
            "uno": {
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "Arduino 5V / GND"},
                    {"bilesen": "HC-SR04 Trig", "pin": "D9"},
                    {"bilesen": "HC-SR04 Echo", "pin": "D10"},
                    {"bilesen": "Buzzer (+)", "pin": "D8"}
                ],
                "kod": """// Arduino Uno - Mesafe Uyarici
const int trigPin = 9;
const int echoPin = 10;
const int buzzerPin = 8;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long sure = pulseIn(echoPin, HIGH, 30000);
  int mesafe = (sure * 0.0343) / 2;

  if (mesafe > 0 && mesafe < 20) {
    digitalWrite(buzzerPin, HIGH);
    delay(50);
    digitalWrite(buzzerPin, LOW);
    delay(50);
  }
}"""
            },
            "nano": {
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "Nano 5V / GND"},
                    {"bilesen": "HC-SR04 Trig", "pin": "D9"},
                    {"bilesen": "HC-SR04 Echo", "pin": "D10"},
                    {"bilesen": "Buzzer (+)", "pin": "D8"}
                ],
                "kod": """// Arduino Nano - Mesafe Uyarici
const int trigPin = 9;
const int echoPin = 10;
const int buzzerPin = 8;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long sure = pulseIn(echoPin, HIGH, 30000);
  int mesafe = (sure * 0.0343) / 2;

  if (mesafe > 0 && mesafe < 20) {
    digitalWrite(buzzerPin, HIGH);
    delay(50);
    digitalWrite(buzzerPin, LOW);
    delay(50);
  }
}"""
            },
            "esp32": {
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "ESP32 VIN (5V) / GND"},
                    {"bilesen": "HC-SR04 Trig", "pin": "GPIO 5"},
                    {"bilesen": "HC-SR04 Echo", "pin": "GPIO 18 (1kΩ + 2kΩ Gerilim Bölücü ile 3.3V)"},
                    {"bilesen": "Buzzer (+)", "pin": "GPIO 19"}
                ],
                "kod": """// ESP32 - Mesafe Uyarici (3.3V Korumali)
const int trigPin = 5;
const int echoPin = 18;
const int buzzerPin = 19;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  Serial.begin(115200);
}

void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long sure = pulseIn(echoPin, HIGH, 30000);
  int mesafe = (sure * 0.0343) / 2;

  if (mesafe > 0 && mesafe < 20) {
    digitalWrite(buzzerPin, HIGH);
    delay(50);
    digitalWrite(buzzerPin, LOW);
    delay(50);
  }
}"""
            },
            "esp8266": {
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "NodeMCU VV (5V) / GND"},
                    {"bilesen": "HC-SR04 Trig", "pin": "D1 (GPIO 5)"},
                    {"bilesen": "HC-SR04 Echo", "pin": "D2 (GPIO 4) (1kΩ + 2kΩ Gerilim Bölücü ile 3.3V)"},
                    {"bilesen": "Buzzer (+)", "pin": "D5 (GPIO 14)"}
                ],
                "kod": """// ESP8266 NodeMCU - Mesafe Uyarici
const int trigPin = D1;
const int echoPin = D2;
const int buzzerPin = D5;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  Serial.begin(115200);
}

void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long sure = pulseIn(echoPin, HIGH, 30000);
  int mesafe = (sure * 0.0343) / 2;

  if (mesafe > 0 && mesafe < 20) {
    digitalWrite(buzzerPin, HIGH);
    delay(50);
    digitalWrite(buzzerPin, LOW);
    delay(50);
  }
}"""
            }
        }
    },
    "dht11-sicaklik": {
        "kategori": "Sensörler",
        "baslik": "DHT11 Dijital Sıcaklık & Nem Ölçümü",
        "kutuphaneler": "<DHT.h> (Adafruit DHT Library)",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "1x", "isim": "DHT11 Sensörü"},
            {"adet": "1x", "isim": "10kΩ Direnç (Pull-up)"},
            {"adet": "1x", "isim": "Breadboard ve Jumper"}
        ],
        "sema_url": "",
        "kartlar": {
            "uno": {
                "baglanti": [
                    {"bilesen": "DHT11 VCC / GND", "pin": "Arduino 5V / GND"},
                    {"bilesen": "DHT11 Data", "pin": "D2 (10kΩ ile 5V pull-up)"}
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
                "baglanti": [
                    {"bilesen": "DHT11 VCC / GND", "pin": "Nano 5V / GND"},
                    {"bilesen": "DHT11 Data", "pin": "D2 (10kΩ pull-up)"}
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
                "baglanti": [
                    {"bilesen": "DHT11 VCC / GND", "pin": "ESP32 3.3V / GND"},
                    {"bilesen": "DHT11 Data", "pin": "GPIO 4 (4.7kΩ ile 3.3V pull-up)"}
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
                "baglanti": [
                    {"bilesen": "DHT11 VCC / GND", "pin": "NodeMCU 3.3V / GND"},
                    {"bilesen": "DHT11 Data", "pin": "D4 (GPIO 2) (4.7kΩ pull-up)"}
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
    }
}

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
