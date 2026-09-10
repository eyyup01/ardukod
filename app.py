import os
import json
from flask import Flask, request, jsonify, session, redirect, render_template_string

app = Flask(__name__)
app.secret_key = "ardukod_gizli_anahtar_ozel_2026"
ADMIN_SIFRE = "admin123"

# ==============================================================================
# %100 ÇALIŞAN DOĞRULANMIŞ PROJELER VE EKSİKSİZ KODLAR
# ==============================================================================
PROJELER = {
    "kara-simsek": {
        "kategori": "Temel & LED",
        "baslik": "5 LED Kademeli Kara Şimşek (Knight Rider)",
        "zorluk": "Başlangıç",
        "sure": "10 Dk",
        "malzemeler": [
            {"adet": "5x", "isim": "5mm Kırmızı LED", "link": "https://www.direnc.net"},
            {"adet": "5x", "isim": "220Ω / 330Ω Direnç", "link": "https://www.direnc.net"},
            {"adet": "1x", "isim": "Breadboard", "link": "https://www.direnc.net"},
            {"adet": "6x", "isim": "Jumper Kablo", "link": "https://www.direnc.net"}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D2, D3, D4, D5, D6 (220Ω seri)"},
                    {"bilesen": "LED 1-5 Katotları (-)", "pin": "GND"}
                ],
                "kod": """/* ArduKod - 5 LED Kara Simsek (Arduino Uno) */
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
                    {"bilesen": "LED 1-5 Anotları (+)", "pin": "D1, D2, D5, D6, D7 (GPIO 5,4,14,12,13)"},
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
            {"adet": "3x", "isim": "220Ω / 330Ω Direnç", "link": ""},
            {"adet": "4x", "isim": "Jumper Kablo", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "D9 / D10 / D11 (PWM)"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": """/* ArduKod - RGB LED PWM (Arduino Uno) */
const int red = 9, green = 10, blue = 11;

void setup() {
  pinMode(red, OUTPUT);
  pinMode(green, OUTPUT);
  pinMode(blue, OUTPUT);
}

void loop() {
  for (int i = 0; i < 255; i++) { analogWrite(red, i); analogWrite(green, 255 - i); delay(5); }
  for (int i = 0; i < 255; i++) { analogWrite(green, i); analogWrite(blue, 255 - i); delay(5); }
  for (int i = 0; i < 255; i++) { analogWrite(blue, i); analogWrite(red, 255 - i); delay(5); }
}"""
            },
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "RGB R / G / B", "pin": "D9 / D10 / D11 (PWM)"}, {"bilesen": "Katot (-)", "pin": "GND"}],
                "kod": """/* ArduKod - RGB LED PWM (Arduino Nano) */
const int red = 9, green = 10, blue = 11;

void setup() {
  pinMode(red, OUTPUT);
  pinMode(green, OUTPUT);
  pinMode(blue, OUTPUT);
}

void loop() {
  for (int i = 0; i < 255; i++) { analogWrite(red, i); analogWrite(green, 255 - i); delay(5); }
  for (int i = 0; i < 255; i++) { analogWrite(green, i); analogWrite(blue, 255 - i); delay(5); }
  for (int i = 0; i < 255; i++) { analogWrite(blue, i); analogWrite(red, 255 - i); delay(5); }
}"""
            },
            "esp32": {
                "kutuphaneler": "Harici kütüphane gerekmez (Dahili ledc PWM motoru).",
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
            {"adet": "1x", "isim": "HC-SR04 Mesafe Sensörü", "link": "https://www.direnc.net"},
            {"adet": "1x", "isim": "5V Aktif Buzzer", "link": "https://www.direnc.net"},
            {"adet": "2x", "isim": "1kΩ ve 2kΩ Direnç (ESP koruması)", "link": ""}
        ],
        "kartlar": {
            "uno": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "D9 / D10"}, {"bilesen": "Buzzer (+)", "pin": "D8"}],
                "kod": """/* ArduKod - HC-SR04 Park Sensoru (Uno) */
const int trigPin = 9, echoPin = 10, buzzerPin = 8;

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
            "nano": {
                "kutuphaneler": "Harici kütüphane gerekmez.",
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "D9 / D10"}, {"bilesen": "Buzzer (+)", "pin": "D8"}],
                "kod": """/* ArduKod - HC-SR04 Park Sensoru (Nano) */
const int trigPin = 9, echoPin = 10, buzzerPin = 8;

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
                "baglanti": [{"bilesen": "Trig / Echo", "pin": "GPIO 5 / GPIO 18 (1k/2k Bölücü)"}, {"bilesen": "Buzzer (+)", "pin": "GPIO 19"}],
                "kod": """/* ArduKod - HC-SR04 (ESP32 - 3.3V Guvenli) */
const int trigPin = 5, echoPin = 18, buzzerPin = 19;

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
const int trigPin = D1, echoPin = D2, buzzerPin = D5;

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

# ==============================================================================
# DOĞRUDAN GÖMÜLÜ ANA SAYFA HTML (FETCH YOK, ASLA TAKILMAZ)
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
    <div class="brand">⚡ ArduKod</div>
    <div class="nav-actions">
        <a href="/admin" class="hub-btn" style="color:var(--accent-blue); border-color:var(--accent-blue);">🔐 Admin</a>
    </div>
</div>

<div class="main-container">
    <div id="workspaceView" class="view-section active">
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
    // VERİLER DOĞRUDAN PYTHON TARAFINDAN ENJEKTE EDİLDİ (AĞ İSTEĞİ BEKLEMEZ)
    const VERI_HAVUZU = {{ projeler_json | safe }};
    let aktifKart = 'uno';
    let aktifProjeId = '';

    window.onload = () => {
        listeyiOlustur(VERI_HAVUZU);
        const ilkId = Object.keys(VERI_HAVUZU)[0];
        if (ilkId) projeSec(ilkId);
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
        kodEl.textContent = kartBilgisi.kod || '// Kod hazirlaniyor...';
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
</script>
</body>
</html>
"""

# DOĞRUDAN PYTHON İÇİNDEN VERİ ENJEKSİYONU
@app.route('/')
def index():
    return render_template_string(ANA_SAYFA_HTML, projeler_json=json.dumps(PROJELER))

# ==============================================================================
# GİZLİ ŞİFRELİ ADMİN PANELİ (EKRANDA ŞİFRE ASLA YAZMAZ)
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
