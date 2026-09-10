import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "ardukod_super_gizli_anahtar_9988"
ADMIN_SIFRE = "admin123"  # Admin panel şifresi (istediğin gibi değiştirebilirsin)

VERI_DOSYASI = "projeler.json"
ISTEK_DOSYASI = "istekler.json"
ISTATISTIK_DOSYASI = "istatistik.json"

# ==============================================================================
# VARSAYILAN 20 PROJE (Eğer projeler.json yoksa otomatik oluşturulur)
# ==============================================================================
VARSAYILAN_PROJELER = {
    "kara-simsek": {
        "kategori": "Temel & LED",
        "baslik": "5 LED Kademeli Kara Şimşek",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [
            {"adet": "5x", "isim": "5mm LED", "link": "https://www.direnc.net"},
            {"adet": "5x", "isim": "220Ω / 330Ω Direnç", "link": ""},
            {"adet": "1x", "isim": "Breadboard", "link": ""},
            {"adet": "6x", "isim": "Erkek-Erkek Jumper", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "GND"}
                ],
                "kod": """// Arduino Uno - 5 LED Kara Simsek\nconst int pinler[] = {2, 3, 4, 5, 6};\nconst int adet = 5;\n\nvoid setup() {\n  for (int i = 0; i < adet; i++) pinMode(pinler[i], OUTPUT);\n}\n\nvoid loop() {\n  for (int i = 0; i < adet; i++) {\n    digitalWrite(pinler[i], HIGH);\n    delay(50);\n    digitalWrite(pinler[i], LOW);\n  }\n  for (int i = adet - 2; i > 0; i--) {\n    digitalWrite(pinler[i], HIGH);\n    delay(50);\n    digitalWrite(pinler[i], LOW);\n  }\n}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "GND"}
                ],
                "kod": """// Arduino Nano - 5 LED Kara Simsek\nconst int pinler[] = {2, 3, 4, 5, 6};\nconst int adet = 5;\n\nvoid setup() {\n  for (int i = 0; i < adet; i++) pinMode(pinler[i], OUTPUT);\n}\n\nvoid loop() {\n  for (int i = 0; i < adet; i++) {\n    digitalWrite(pinler[i], HIGH);\n    delay(50);\n    digitalWrite(pinler[i], LOW);\n  }\n  for (int i = adet - 2; i > 0; i--) {\n    digitalWrite(pinler[i], HIGH);\n    delay(50);\n    digitalWrite(pinler[i], LOW);\n  }\n}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "GPIO 18, 19, 21, 22, 23 (330Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "GND"}
                ],
                "kod": """// ESP32 - 5 LED Kara Simsek (3.3V Uyumlu)\nconst int pinler[] = {18, 19, 21, 22, 23};\nconst int adet = 5;\n\nvoid setup() {\n  for (int i = 0; i < adet; i++) pinMode(pinler[i], OUTPUT);\n}\n\nvoid loop() {\n  for (int i = 0; i < adet; i++) {\n    digitalWrite(pinler[i], HIGH);\n    delay(50);\n    digitalWrite(pinler[i], LOW);\n  }\n  for (int i = adet - 2; i > 0; i--) {\n    digitalWrite(pinler[i], HIGH);\n    delay(50);\n    digitalWrite(pinler[i], LOW);\n  }\n}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D1, D2, D5, D6, D7 (GPIO 5,4,14,12,13)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "GND"}
                ],
                "kod": """// ESP8266 NodeMCU - 5 LED Kara Simsek\nconst int pinler[] = {D1, D2, D5, D6, D7};\nconst int adet = 5;\n\nvoid setup() {\n  for (int i = 0; i < adet; i++) pinMode(pinler[i], OUTPUT);\n}\n\nvoid loop() {\n  for (int i = 0; i < adet; i++) {\n    digitalWrite(pinler[i], HIGH);\n    delay(50);\n    digitalWrite(pinler[i], LOW);\n  }\n  for (int i = adet - 2; i > 0; i--) {\n    digitalWrite(pinler[i], HIGH);\n    delay(50);\n    digitalWrite(pinler[i], LOW);\n  }\n}"""
            }
        }
    },
    "rgb-led-pwm": {
        "kategori": "Temel & LED",
        "baslik": "RGB LED Yumuşak Renk Geçişi (PWM)",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [
            {"adet": "1x", "isim": "Ortak Katot RGB LED", "link": ""},
            {"adet": "3x", "isim": "220Ω / 330Ω Direnç", "link": ""},
            {"adet": "4x", "isim": "Jumper Kablo", "link": ""}
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
                "kod": """// Arduino Uno - RGB LED PWM Renk Gecisi\nconst int red = 9, green = 10, blue = 11;\n\nvoid setup() {\n  pinMode(red, OUTPUT);\n  pinMode(green, OUTPUT);\n  pinMode(blue, OUTPUT);\n}\n\nvoid loop() {\n  for (int i = 0; i < 255; i++) { analogWrite(red, i); analogWrite(green, 255-i); delay(5); }\n  for (int i = 0; i < 255; i++) { analogWrite(green, i); analogWrite(blue, 255-i); delay(5); }\n  for (int i = 0; i < 255; i++) { analogWrite(blue, i); analogWrite(red, 255-i); delay(5); }\n}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "RGB Kırmızı (R)", "pin": "D9 (PWM) (220Ω)"},
                    {"bilesen": "RGB Yeşil (G)", "pin": "D10 (PWM) (220Ω)"},
                    {"bilesen": "RGB Mavi (B)", "pin": "D11 (PWM) (220Ω)"},
                    {"bilesen": "Ortak Katot (-)", "pin": "GND"}
                ],
                "kod": """// Arduino Nano - RGB LED PWM Renk Gecisi\nconst int red = 9, green = 10, blue = 11;\n\nvoid setup() {\n  pinMode(red, OUTPUT);\n  pinMode(green, OUTPUT);\n  pinMode(blue, OUTPUT);\n}\n\nvoid loop() {\n  for (int i = 0; i < 255; i++) { analogWrite(red, i); analogWrite(green, 255-i); delay(5); }\n  for (int i = 0; i < 255; i++) { analogWrite(green, i); analogWrite(blue, 255-i); delay(5); }\n  for (int i = 0; i < 255; i++) { analogWrite(blue, i); analogWrite(red, 255-i); delay(5); }\n}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez (Dahili ledc PWM motoru).",
                "baglanti": [
                    {"bilesen": "RGB Kırmızı (R)", "pin": "GPIO 18 (330Ω)"},
                    {"bilesen": "RGB Yeşil (G)", "pin": "GPIO 19 (330Ω)"},
                    {"bilesen": "RGB Mavi (B)", "pin": "GPIO 21 (330Ω)"},
                    {"bilesen": "Ortak Katot (-)", "pin": "GND"}
                ],
                "kod": """// ESP32 - Donanimsal PWM ile RGB Kontrol\nconst int rPin = 18, gPin = 19, bPin = 21;\n\nvoid setup() {\n  ledcAttach(rPin, 5000, 8);\n  ledcAttach(gPin, 5000, 8);\n  ledcAttach(bPin, 5000, 8);\n}\n\nvoid loop() {\n  for (int i = 0; i < 255; i++) { ledcWrite(rPin, i); ledcWrite(gPin, 255-i); delay(5); }\n  for (int i = 0; i < 255; i++) { ledcWrite(gPin, i); ledcWrite(bPin, 255-i); delay(5); }\n  for (int i = 0; i < 255; i++) { ledcWrite(bPin, i); ledcWrite(rPin, 255-i); delay(5); }\n}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "RGB Kırmızı (R)", "pin": "D1 (GPIO 5) (330Ω)"},
                    {"bilesen": "RGB Yeşil (G)", "pin": "D2 (GPIO 4) (330Ω)"},
                    {"bilesen": "RGB Mavi (B)", "pin": "D5 (GPIO 14) (330Ω)"},
                    {"bilesen": "Ortak Katot (-)", "pin": "GND"}
                ],
                "kod": """// ESP8266 NodeMCU - RGB PWM Kontrol (0-1023)\nconst int rPin = D1, gPin = D2, bPin = D5;\n\nvoid setup() {\n  pinMode(rPin, OUTPUT);\n  pinMode(gPin, OUTPUT);\n  pinMode(bPin, OUTPUT);\n}\n\nvoid loop() {\n  for (int i = 0; i < 1023; i += 4) { analogWrite(rPin, i); analogWrite(gPin, 1023-i); delay(5); }\n  for (int i = 0; i < 1023; i += 4) { analogWrite(gPin, i); analogWrite(bPin, 1023-i); delay(5); }\n  for (int i = 0; i < 1023; i += 4) { analogWrite(bPin, i); analogWrite(rPin, 1023-i); delay(5); }\n}"""
            }
        }
    },
    "hc-sr04-radar": {
        "kategori": "Sensörler",
        "baslik": "HC-SR04 Mesafe Sensörü & Sesli Uyarı",
        "zorluk": "Orta",
        "sure": "15 Dk",
        "goruntulenme": 0,
        "indirme": 0,
        "malzemeler": [
            {"adet": "1x", "isim": "HC-SR04 Ultrasonik Sensör", "link": ""},
            {"adet": "1x", "isim": "5V / 3.3V Buzzer", "link": ""},
            {"adet": "1x", "isim": "Breadboard", "link": ""},
            {"adet": "6x", "isim": "Jumper Kablo", "link": ""},
            {"adet": "2x", "isim": "1kΩ ve 2kΩ Direnç (ESP koruması)", "link": ""}
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
                "kod": """// Arduino Uno - HC-SR04 Park Sensoru\nconst int trig = 9, echo = 10, buzz = 8;\n\nvoid setup() {\n  pinMode(trig, OUTPUT);\n  pinMode(echo, INPUT);\n  pinMode(buzz, OUTPUT);\n  Serial.begin(9600);\n}\n\nvoid loop() {\n  digitalWrite(trig, LOW); delayMicroseconds(2);\n  digitalWrite(trig, HIGH); delayMicroseconds(10);\n  digitalWrite(trig, LOW);\n\n  long sure = pulseIn(echo, HIGH, 30000);\n  int mesafe = (sure * 0.0343) / 2;\n\n  if (mesafe > 0 && mesafe < 20) {\n    digitalWrite(buzz, HIGH); delay(40);\n    digitalWrite(buzz, LOW); delay(40);\n  }\n}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "5V / GND"},
                    {"bilesen": "HC-SR04 Trig", "pin": "D9"},
                    {"bilesen": "HC-SR04 Echo", "pin": "D10"},
                    {"bilesen": "Buzzer (+)", "pin": "D8"}
                ],
                "kod": """// Arduino Nano - HC-SR04 Park Sensoru\nconst int trig = 9, echo = 10, buzz = 8;\n\nvoid setup() {\n  pinMode(trig, OUTPUT);\n  pinMode(echo, INPUT);\n  pinMode(buzz, OUTPUT);\n  Serial.begin(9600);\n}\n\nvoid loop() {\n  digitalWrite(trig, LOW); delayMicroseconds(2);\n  digitalWrite(trig, HIGH); delayMicroseconds(10);\n  digitalWrite(trig, LOW);\n\n  long sure = pulseIn(echo, HIGH, 30000);\n  int mesafe = (sure * 0.0343) / 2;\n\n  if (mesafe > 0 && mesafe < 20) {\n    digitalWrite(buzz, HIGH); delay(40);\n    digitalWrite(buzz, LOW); delay(40);\n  }\n}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "VIN (5V) / GND"},
                    {"bilesen": "HC-SR04 Trig", "pin": "GPIO 5"},
                    {"bilesen": "HC-SR04 Echo", "pin": "GPIO 18 (1k/2k bolucu)"},
                    {"bilesen": "Buzzer (+)", "pin": "GPIO 19"}
                ],
                "kod": """// ESP32 - HC-SR04 (3.3V Lojik Guvenli)\nconst int trig = 5, echo = 18, buzz = 19;\n\nvoid setup() {\n  pinMode(trig, OUTPUT);\n  pinMode(echo, INPUT);\n  pinMode(buzz, OUTPUT);\n  Serial.begin(115200);\n}\n\nvoid loop() {\n  digitalWrite(trig, LOW); delayMicroseconds(2);\n  digitalWrite(trig, HIGH); delayMicroseconds(10);\n  digitalWrite(trig, LOW);\n\n  long sure = pulseIn(echo, HIGH, 30000);\n  int mesafe = (sure * 0.0343) / 2;\n\n  if (mesafe > 0 && mesafe < 20) {\n    digitalWrite(buzz, HIGH); delay(40);\n    digitalWrite(buzz, LOW); delay(40);\n  }\n}"""
            },
            "esp8266": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "HC-SR04 VCC / GND", "pin": "VV (5V) / GND"},
                    {"bilesen": "HC-SR04 Trig", "pin": "D1 (GPIO 5)"},
                    {"bilesen": "HC-SR04 Echo", "pin": "D2 (GPIO 4) (Bolucu)"},
                    {"bilesen": "Buzzer (+)", "pin": "D5 (GPIO 14)"}
                ],
                "kod": """// ESP8266 NodeMCU - HC-SR04 Mesafe\nconst int trig = D1, echo = D2, buzz = D5;\n\nvoid setup() {\n  pinMode(trig, OUTPUT);\n  pinMode(echo, INPUT);\n  pinMode(buzz, OUTPUT);\n  Serial.begin(115200);\n}\n\nvoid loop() {\n  digitalWrite(trig, LOW); delayMicroseconds(2);\n  digitalWrite(trig, HIGH); delayMicroseconds(10);\n  digitalWrite(trig, LOW);\n\n  long sure = pulseIn(echo, HIGH, 30000);\n  int mesafe = (sure * 0.0343) / 2;\n\n  if (mesafe > 0 && mesafe < 20) {\n    digitalWrite(buzz, HIGH); delay(40);\n    digitalWrite(buzz, LOW); delay(40);\n  }\n}"""
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
            return json.load(f)
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

# --- GENEL KULLANICI ROTALARI ---
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
    return jsonify({"durum": "hata", "mesaj": "Proje bulunamadı."})

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
    istekler.append({"mesaj": mesaj, "iletisim": iletisim, "tarih": "Bugün"})
    istek_kaydet(istekler)
    return jsonify({"durum": "basarili", "mesaj": "Geri bildiriminiz iletildi!"})

# --- ADMİN PANELİ ROTALARI ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_giris():
    if session.get("admin_giris"):
        return redirect(url_for('admin_panel'))
    
    hata = ""
    if request.method == 'POST':
        if request.form.get("sifre") == ADMIN_SIFRE:
            session["admin_giris"] = True
            return redirect(url_for('admin_panel'))
        hata = "Hatalı şifre!"
    return render_template('admin_login.html', hata=hata)

@app.route('/admin/cikis')
def admin_cikis():
    session.pop("admin_giris", None)
    return redirect(url_for('admin_giris'))

@app.route('/admin/panel')
def admin_panel():
    if not session.get("admin_giris"):
        return redirect(url_for('admin_giris'))
    projeler = veri_yukle()
    istekler = istek_yukle()
    toplam_goruntulenme = sum(p.get("goruntulenme", 0) for p in projeler.values())
    toplam_indirme = sum(p.get("indirme", 0) for p in projeler.values())
    return render_template('admin_panel.html', projeler=projeler, istekler=istekler, goruntulenme=toplam_goruntulenme, indirme=toplam_indirme)

@app.route('/admin/proje-kaydet', methods=['POST'])
def admin_proje_kaydet():
    if not session.get("admin_giris"):
        return jsonify({"durum": "yetkisiz"}), 403
    
    data = request.get_json()
    p_id = data.get("id")
    if not p_id:
        return jsonify({"durum": "hata", "mesaj": "Proje kimliği (ID) zorunludur."}), 400
    
    projeler = veri_yukle()
    
    # Mevcut veriyi koru veya yeni oluştur
    mevcut = projeler.get(p_id, {"goruntulenme": 0, "indirme": 0})
    
    mevcut["baslik"] = data.get("baslik", "")
    mevcut["kategori"] = data.get("kategori", "Genel")
    mevcut["zorluk"] = data.get("zorluk", "Başlangıç")
    mevcut["sure"] = data.get("sure", "10 Dk")
    mevcut["malzemeler"] = data.get("malzemeler", [])
    mevcut["kartlar"] = data.get("kartlar", {})
    
    projeler[p_id] = mevcut
    veri_kaydet(projeler)
    return jsonify({"durum": "basarili"})

@app.route('/admin/proje-sil/<id>', methods=['POST'])
def admin_proje_sil(id):
    if not session.get("admin_giris"):
        return jsonify({"durum": "yetkisiz"}), 403
    projeler = veri_yukle()
    if id in projeler:
        del projeler[id]
        veri_kaydet(projeler)
        return jsonify({"durum": "basarili"})
    return jsonify({"durum": "hata", "mesaj": "Bulunamadı"}), 404

@app.route('/admin/istek-sil/<int:index>', methods=['POST'])
def admin_istek_sil(index):
    if not session.get("admin_giris"):
        return jsonify({"durum": "yetkisiz"}), 403
    istekler = istek_yukle()
    if 0 <= index < len(istekler):
        istekler.pop(index)
        istek_kaydet(istekler)
        return jsonify({"durum": "basarili"})
    return jsonify({"durum": "hata"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
