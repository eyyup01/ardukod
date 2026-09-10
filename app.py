import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = "ardukod_tam_yetkili_ozel_anahtar_9988_xyz"
ADMIN_SIFRE = "admin123"

# ==============================================================================
# DOĞRUDAN BELLEKTEN ÇALIŞAN EKSİKSİZ PROJELER (KODLAR ASLA SİLİNMEZ)
# ==============================================================================
PROJELER_DEPO = {
    "kara-simsek": {
        "kategori": "Temel & LED",
        "baslik": "5 LED Kademeli Kara Şimşek (Knight Rider)",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "5x", "isim": "5mm Parlak Kırmızı LED", "link": "https://www.direnc.net"},
            {"adet": "5x", "isim": "220Ω / 330Ω Direnç", "link": "https://www.direnc.net"},
            {"adet": "1x", "isim": "Breadboard", "link": "https://www.direnc.net"},
            {"adet": "6x", "isim": "Erkek-Erkek Jumper Kablo", "link": "https://www.direnc.net"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "Arduino GND"}
                ],
                "kod": """/* ArduKod - 5 LED Kara Simsek (Arduino Uno) */
const int pinler[] = {2, 3, 4, 5, 6};
const int adet = 5;
const int bekleme = 50;

void setup() {
  for (int i = 0; i < adet; i++) {
    pinMode(pinler[i], OUTPUT);
    digitalWrite(pinler[i], LOW);
  }
}

void loop() {
  for (int i = 0; i < adet; i++) {
    digitalWrite(pinler[i], HIGH);
    delay(bekleme);
    digitalWrite(pinler[i], LOW);
  }
  for (int i = adet - 2; i > 0; i--) {
    digitalWrite(pinler[i], HIGH);
    delay(bekleme);
    digitalWrite(pinler[i], LOW);
  }
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "Nano GND"}
                ],
                "kod": """/* ArduKod - 5 LED Kara Simsek (Arduino Nano) */
const int pinler[] = {2, 3, 4, 5, 6};
const int adet = 5;

void setup() {
  for (int i = 0; i < adet; i++) {
    pinMode(pinler[i], OUTPUT);
    digitalWrite(pinler[i], LOW);
  }
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
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "ESP32 GND"}
                ],
                "kod": """/* ArduKod - 5 LED Kara Simsek (ESP32 - 3.3V) */
const int pinler[] = {18, 19, 21, 22, 23};
const int adet = 5;

void setup() {
  for (int i = 0; i < adet; i++) {
    pinMode(pinler[i], OUTPUT);
    digitalWrite(pinler[i], LOW);
  }
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
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D1, D2, D5, D6, D7 (GPIO 5, 4, 14, 12, 13)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "NodeMCU GND"}
                ],
                "kod": """/* ArduKod - 5 LED Kara Simsek (NodeMCU ESP8266) */
const int pinler[] = {D1, D2, D5, D6, D7};
const int adet = 5;

void setup() {
  for (int i = 0; i < adet; i++) {
    pinMode(pinler[i], OUTPUT);
    digitalWrite(pinler[i], LOW);
  }
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
                "kod": """/* ArduKod - RGB LED Fade (Arduino Uno) */
const int redPin = 9;
const int greenPin = 10;
const int bluePin = 11;

void setup() {
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
}

void loop() {
  for (int i = 0; i < 255; i++) { analogWrite(redPin, i); analogWrite(greenPin, 255 - i); delay(5); }
  for (int i = 0; i < 255; i++) { analogWrite(greenPin, i); analogWrite(bluePin, 255 - i); delay(5); }
  for (int i = 0; i < 255; i++) { analogWrite(bluePin, i); analogWrite(redPin, 255 - i); delay(5); }
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "D9 / D10 / D11 (PWM)"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": """/* ArduKod - RGB LED Fade (Arduino Nano) */
const int redPin = 9;
const int greenPin = 10;
const int bluePin = 11;

void setup() {
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
}

void loop() {
  for (int i = 0; i < 255; i++) { analogWrite(redPin, i); analogWrite(greenPin, 255 - i); delay(5); }
  for (int i = 0; i < 255; i++) { analogWrite(greenPin, i); analogWrite(bluePin, 255 - i); delay(5); }
  for (int i = 0; i < 255; i++) { analogWrite(bluePin, i); analogWrite(redPin, 255 - i); delay(5); }
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez (Dahili PWM Donanımı).",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "GPIO 18 / 19 / 21"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": """/* ArduKod - RGB LED PWM (ESP32) */
const int r = 18, g = 19, b = 21;

void setup() {
  ledcAttach(r, 5000, 8);
  ledcAttach(g, 5000, 8);
  ledcAttach(b, 5000, 8);
}

void loop() {
  for (int i = 0; i < 255; i++) { ledcWrite(r, i); ledcWrite(g, 255 - i); delay(5); }
  for (int i = 0; i < 255; i++) { ledcWrite(g, i); ledcWrite(b, 255 - i); delay(5); }
  for (int i = 0; i < 255; i++) { ledcWrite(b, i); ledcWrite(r, 255 - i); delay(5); }
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "D1 / D2 / D5"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": """/* ArduKod - RGB LED PWM (NodeMCU ESP8266) */
const int r = D1, g = D2, b = D5;

void setup() {
  pinMode(r, OUTPUT); pinMode(g, OUTPUT); pinMode(b, OUTPUT);
}

void loop() {
  for (int i = 0; i < 1023; i += 5) { analogWrite(r, i); analogWrite(g, 1023 - i); delay(5); }
  for (int i = 0; i < 1023; i += 5) { analogWrite(g, i); analogWrite(b, 1023 - i); delay(5); }
  for (int i = 0; i < 1023; i += 5) { analogWrite(b, i); analogWrite(r, 1023 - i); delay(5); }
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
            {"adet": "1x", "isim": "5V Aktif Buzzer", "link": "https://www.direnc.net"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "D9 / D10"}, {"bilesen": "Buzzer (+)", "pin": "D8"}],
                "kod": """/* ArduKod - HC-SR04 Park Sensoru (Arduino Uno) */
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
  digitalWrite(trigPin, LOW); delayMicroseconds(2);
  digitalWrite(trigPin, HIGH); delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long sure = pulseIn(echoPin, HIGH, 30000);
  int mesafe = (sure * 0.0343) / 2;

  if (mesafe > 0 && mesafe < 30) {
    digitalWrite(buzzerPin, HIGH);
    delay(30);
    digitalWrite(buzzerPin, LOW);
    delay(mesafe * 10);
  } else {
    delay(100);
  }
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "D9 / D10"}, {"bilesen": "Buzzer (+)", "pin": "D8"}],
                "kod": """/* ArduKod - HC-SR04 Park Sensoru (Arduino Nano) */
const int trigPin = 9;
const int echoPin = 10;
const int buzzerPin = 8;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
}

void loop() {
  digitalWrite(trigPin, LOW); delayMicroseconds(2);
  digitalWrite(trigPin, HIGH); delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long sure = pulseIn(echoPin, HIGH, 30000);
  int mesafe = (sure * 0.0343) / 2;

  if (mesafe > 0 && mesafe < 30) {
    digitalWrite(buzzerPin, HIGH);
    delay(30);
    digitalWrite(buzzerPin, LOW);
    delay(mesafe * 10);
  } else {
    delay(100);
  }
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "GPIO 5 / GPIO 18 (Bölücülü)"}, {"bilesen": "Buzzer (+)", "pin": "GPIO 19"}],
                "kod": """/* ArduKod - HC-SR04 (ESP32 - 3.3V Guvenli) */
const int trigPin = 5;
const int echoPin = 18;
const int buzzerPin = 19;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
}

void loop() {
  digitalWrite(trigPin, LOW); delayMicroseconds(2);
  digitalWrite(trigPin, HIGH); delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long sure = pulseIn(echoPin, HIGH, 30000);
  int mesafe = (sure * 0.0343) / 2;

  if (mesafe > 0 && mesafe < 30) {
    digitalWrite(buzzerPin, HIGH);
    delay(30);
    digitalWrite(buzzerPin, LOW);
    delay(mesafe * 10);
  } else {
    delay(100);
  }
}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "D1 / D2 (Bölücülü)"}, {"bilesen": "Buzzer (+)", "pin": "D5"}],
                "kod": """/* ArduKod - HC-SR04 (NodeMCU ESP8266) */
const int trigPin = D1;
const int echoPin = D2;
const int buzzerPin = D5;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
}

void loop() {
  digitalWrite(trigPin, LOW); delayMicroseconds(2);
  digitalWrite(trigPin, HIGH); delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long sure = pulseIn(echoPin, HIGH, 30000);
  int mesafe = (sure * 0.0343) / 2;

  if (mesafe > 0 && mesafe < 30) {
    digitalWrite(buzzerPin, HIGH);
    delay(30);
    digitalWrite(buzzerPin, LOW);
    delay(mesafe * 10);
  } else {
    delay(100);
  }
}"""
            }
        }
    }
}

# DOĞRUDAN BELLEKTEN OKUR, BOZUK DOSYAYA BAKMAZ
@app.route('/')
def index():
    return render_template('index.html', projeler_data=PROJELER_DEPO)

@app.route('/proje/<id>/indir', methods=['POST'])
def indir_say(id):
    return jsonify({"durum": "ok"})

# --- ADMIN PANELİ (PAROLA ASLA EKRANDA YAZMAZ) ---
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
    return render_template_string(ADMIN_PANEL_HTML, projeler=PROJELER_DEPO)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
