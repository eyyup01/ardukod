# -*- coding: utf-8 -*-
"""
ArduKod - Arduino Geliştirici Kütüphanesi
==========================================
Tek dosyalık Flask uygulaması.

Özellikler:
- Board kategorileri (Uno / Nano / Mega / ESP32 / ESP8266) kutucuklu ana sayfa
- Her board için kod listesi -> kod detay sayfası (pin tablosu + kod + ürün linkleri)
- Admin paneli (şifreli giriş) ile kod ekleme / düzenleme / silme
- Direnç renk kodu hesaplayıcı (4 ve 5 bant)
- Kondansatör kodu (EIA 3 haneli) ve birim çevirici
- SQLite veritabanı (ilk çalıştırmada otomatik oluşur ve örnek kodlarla doldurulur)

Çalıştırma:
    pip install -r requirements.txt
    python app.py

Ortam değişkenleri (güvenlik için ÖNERİLİR, Render -> Environment kısmından ayarlayın):
    ADMIN_USERNAME   -> admin kullanıcı adı (varsayılan: admin)
    ADMIN_PASSWORD   -> admin şifresi     (varsayılan: ArduKod2026!)
    SECRET_KEY       -> flask session anahtarı (verilmezse her başlatmada rastgele üretilir,
                         bu da sunucu her yeniden başladığında oturumların düşmesine sebep olur.
                         Render'da sabit bir SECRET_KEY tanımlamanız tavsiye edilir.)
"""

import os
import sqlite3
import secrets
from datetime import datetime, timezone
from functools import wraps

from flask import (
    Flask, request, redirect, url_for, session,
    render_template_string, g, flash, abort
)
from werkzeug.security import generate_password_hash, check_password_hash

# ----------------------------------------------------------------------------
# Yapılandırma
# ----------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ardukod.db")

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = generate_password_hash(
    os.environ.get("ADMIN_PASSWORD", "ArduKod2026!")
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(32))

BOARDS = [
    {"key": "uno", "name": "Arduino Uno", "icon": "🟦"},
    {"key": "nano", "name": "Arduino Nano", "icon": "🟩"},
    {"key": "mega", "name": "Arduino Mega", "icon": "🟥"},
    {"key": "esp32", "name": "ESP32", "icon": "🟪"},
    {"key": "esp8266", "name": "ESP8266", "icon": "🟧"},
]
BOARD_KEYS = [b["key"] for b in BOARDS]
BOARD_MAP = {b["key"]: b for b in BOARDS}


# ----------------------------------------------------------------------------
# Veritabanı yardımcıları
# ----------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            board TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            code_text TEXT NOT NULL,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS pins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_id INTEGER NOT NULL,
            component TEXT,
            connection TEXT,
            FOREIGN KEY(code_id) REFERENCES codes(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_id INTEGER NOT NULL,
            label TEXT,
            url TEXT,
            FOREIGN KEY(code_id) REFERENCES codes(id) ON DELETE CASCADE
        );
        """
    )
    db.commit()

    count = db.execute("SELECT COUNT(*) AS c FROM codes").fetchone()[0]
    if count == 0:
        seed_database(db)
    else:
        sync_new_seed_entries(db)
    db.close()


def seed_database(db):
    now = datetime.now(timezone.utc).isoformat()
    for item in SEED_DATA:
        cur = db.execute(
            "INSERT INTO codes (board, title, description, code_text, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (item["board"], item["title"], item["description"], item["code"], now),
        )
        code_id = cur.lastrowid
        for comp, conn in item.get("pins", []):
            db.execute(
                "INSERT INTO pins (code_id, component, connection) VALUES (?, ?, ?)",
                (code_id, comp, conn),
            )
        for label, url in item.get("links", []):
            db.execute(
                "INSERT INTO links (code_id, label, url) VALUES (?, ?, ?)",
                (code_id, label, url),
            )
    db.commit()


def sync_new_seed_entries(db):
    """
    Veritabanı zaten doluysa (ilk kurulumdan sonra app.py'ye yeni SEED_DATA
    kodları eklendiyse) bu fonksiyon sadece EKSİK olan başlıkları tespit edip
    ekler. Var olan kodlara veya admin panelinden yapılmış değişikliklere
    dokunmaz, hiçbir şeyi silmez veya güncellemez - sadece yenileri tamamlar.
    """
    existing_titles = {
        row["title"] for row in db.execute("SELECT title FROM codes").fetchall()
    }
    now = datetime.now(timezone.utc).isoformat()
    added = 0
    for item in SEED_DATA:
        if item["title"] in existing_titles:
            continue
        cur = db.execute(
            "INSERT INTO codes (board, title, description, code_text, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (item["board"], item["title"], item["description"], item["code"], now),
        )
        code_id = cur.lastrowid
        for comp, conn in item.get("pins", []):
            db.execute(
                "INSERT INTO pins (code_id, component, connection) VALUES (?, ?, ?)",
                (code_id, comp, conn),
            )
        for label, url in item.get("links", []):
            db.execute(
                "INSERT INTO links (code_id, label, url) VALUES (?, ?, ?)",
                (code_id, label, url),
            )
        added += 1
    if added:
        db.commit()
        print(f"[ArduKod] {added} yeni seed kodu veritabanına eklendi.")


# ----------------------------------------------------------------------------
# Admin giriş kontrolü
# ----------------------------------------------------------------------------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


# ----------------------------------------------------------------------------
# Ortak sayfa şablonu (layout) - tüm sayfalar bunun içine gömülür
# ----------------------------------------------------------------------------

LAYOUT_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ title }} | ArduKod</title>
<style>
  :root{
    --bg:#0b0f14; --bg2:#111823; --card:#151d29; --border:#22303f;
    --text:#e7eef7; --muted:#8fa3b8; --accent:#3ddc97; --accent2:#4da6ff;
    --danger:#ff5d5d; --warn:#ffb454;
  }
  *{box-sizing:border-box;}
  body{
    margin:0; font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
    background:linear-gradient(180deg,var(--bg),var(--bg2)); color:var(--text);
    min-height:100vh;
  }
  a{color:inherit; text-decoration:none;}
  header.top{
    display:flex; align-items:center; justify-content:space-between;
    padding:14px 24px; border-bottom:1px solid var(--border);
    position:sticky; top:0; background:rgba(11,15,20,0.9); backdrop-filter:blur(6px);
    z-index:50; flex-wrap:wrap; gap:10px;
  }
  .brand{font-size:1.3rem; font-weight:700; display:flex; align-items:center; gap:8px;}
  .brand span.bolt{color:var(--accent);}
  nav.mainnav{display:flex; gap:6px; flex-wrap:wrap;}
  nav.mainnav a{
    padding:8px 14px; border-radius:8px; font-size:0.92rem; color:var(--muted);
    border:1px solid transparent;
  }
  nav.mainnav a.active, nav.mainnav a:hover{
    color:var(--text); border-color:var(--border); background:var(--card);
  }
  main{max-width:1100px; margin:0 auto; padding:28px 20px 60px;}
  .grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:16px;}
  .box{
    background:var(--card); border:1px solid var(--border); border-radius:14px;
    padding:20px; transition:.15s ease; cursor:pointer;
  }
  .box:hover{border-color:var(--accent); transform:translateY(-2px);}
  .box .icon{font-size:2rem;}
  .box h3{margin:10px 0 4px; font-size:1.1rem;}
  .box p{margin:0; color:var(--muted); font-size:0.85rem;}
  h1{font-size:1.7rem; margin-bottom:4px;}
  .subtitle{color:var(--muted); margin-top:0; margin-bottom:26px;}
  .card{
    background:var(--card); border:1px solid var(--border); border-radius:12px;
    padding:18px; margin-bottom:14px;
  }
  table{width:100%; border-collapse:collapse; margin:10px 0;}
  table th, table td{
    border-bottom:1px solid var(--border); padding:8px 10px; text-align:left; font-size:0.92rem;
  }
  table th{color:var(--muted); font-weight:600;}
  pre.codebox{
    background:#0a0e13; border:1px solid var(--border); border-radius:10px;
    padding:16px; overflow-x:auto; font-size:0.85rem; line-height:1.5;
    font-family:'Cascadia Code','Fira Code',Consolas,monospace; position:relative;
  }
  .code-wrap{position:relative;}
  .copy-btn{
    position:absolute; top:10px; right:10px; background:var(--accent); color:#04150d;
    border:none; padding:6px 12px; border-radius:6px; font-size:0.8rem; cursor:pointer;
    font-weight:600;
  }
  .copy-btn:hover{opacity:0.85;}
  .badge{
    display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.75rem;
    background:rgba(61,220,151,0.12); color:var(--accent); border:1px solid rgba(61,220,151,0.35);
  }
  .btn{
    display:inline-block; padding:9px 16px; border-radius:8px; border:1px solid var(--border);
    background:var(--bg2); color:var(--text); cursor:pointer; font-size:0.9rem;
  }
  .btn:hover{border-color:var(--accent);}
  .btn.primary{background:var(--accent); color:#04150d; border-color:var(--accent); font-weight:600;}
  .btn.primary:hover{opacity:0.9;}
  .btn.danger{background:transparent; color:var(--danger); border-color:var(--danger);}
  .btn.danger:hover{background:rgba(255,93,93,0.1);}
  .btn.small{padding:5px 10px; font-size:0.8rem;}
  form label{display:block; margin:14px 0 6px; font-size:0.88rem; color:var(--muted);}
  input[type=text], input[type=url], input[type=password], textarea, select{
    width:100%; padding:10px 12px; border-radius:8px; border:1px solid var(--border);
    background:var(--bg2); color:var(--text); font-size:0.92rem; font-family:inherit;
  }
  textarea.codearea{font-family:'Cascadia Code','Fira Code',Consolas,monospace; font-size:0.85rem;}
  input:focus, textarea:focus, select:focus{outline:none; border-color:var(--accent);}
  .row-repeat{display:flex; gap:8px; margin-bottom:8px; align-items:center;}
  .row-repeat input{flex:1;}
  .flash{
    padding:10px 14px; border-radius:8px; margin-bottom:16px; font-size:0.9rem;
  }
  .flash.error{background:rgba(255,93,93,0.12); border:1px solid rgba(255,93,93,0.4); color:#ffb3b3;}
  .flash.ok{background:rgba(61,220,151,0.12); border:1px solid rgba(61,220,151,0.4); color:var(--accent);}
  .footer{text-align:center; padding:24px; color:var(--muted); font-size:0.78rem;}
  .footer a{opacity:0.55;}
  .footer a:hover{opacity:1;}
  .toolbar{display:flex; justify-content:space-between; align-items:center; margin-bottom:18px; flex-wrap:wrap; gap:10px;}
  .adminlist td.actions{display:flex; gap:8px;}
  .empty{color:var(--muted); text-align:center; padding:40px 0;}
  .calc-grid{display:grid; grid-template-columns:1fr 1fr; gap:24px;}
  @media (max-width:720px){ .calc-grid{grid-template-columns:1fr;} }
  .swatch{width:22px; height:22px; border-radius:4px; display:inline-block; vertical-align:middle; margin-right:6px; border:1px solid #0006;}
  .result-box{
    margin-top:16px; padding:16px; border-radius:10px; background:var(--bg2);
    border:1px solid var(--border); font-size:1.1rem; font-weight:700; color:var(--accent2);
  }
  .link-list a{color:var(--accent2); word-break:break-all;}
  .link-list li{margin-bottom:6px;}
</style>
</head>
<body>
<header class="top">
  <a class="brand" href="{{ url_for('home') }}"><span class="bolt">⚡</span> ArduKod</a>
  <nav class="mainnav">
    <a href="{{ url_for('home') }}" class="{{ 'active' if active=='home' else '' }}">Ana Sayfa</a>
    <a href="{{ url_for('tools') }}" class="{{ 'active' if active=='tools' else '' }}">Hesaplama Araçları</a>
    {% if session.get('is_admin') %}
      <a href="{{ url_for('admin_dashboard') }}" class="{{ 'active' if active=='admin' else '' }}">Panel</a>
      <a href="{{ url_for('admin_logout') }}">Çıkış</a>
    {% endif %}
  </nav>
</header>
<main>
  {{ body|safe }}
</main>
<div class="footer">
  ArduKod &copy; {{ year }} &middot; <a href="{{ url_for('admin_login') }}">Yönetici</a>
</div>
</body>
</html>
"""


def render_page(title, active, inner_tpl, **ctx):
    body = render_template_string(inner_tpl, **ctx)
    return render_template_string(
        LAYOUT_TEMPLATE,
        title=title,
        active=active,
        body=body,
        year=datetime.now(timezone.utc).year,
    )


# ----------------------------------------------------------------------------
# Genel (public) sayfalar
# ----------------------------------------------------------------------------

HOME_TEMPLATE = """
<h1>⚡ ArduKod</h1>
<p class="subtitle">Board'unu seç, hazır kodlara, pin bağlantılarına ve kullanılan ürünlere ulaş.</p>
<div class="grid">
  {% for b in boards %}
  <a class="box" href="{{ url_for('board_page', board_key=b['key']) }}">
    <div class="icon">{{ b['icon'] }}</div>
    <h3>{{ b['name'] }}</h3>
    <p>{{ b['count'] }} hazır kod</p>
  </a>
  {% endfor %}
</div>
"""


@app.route("/")
def home():
    db = get_db()
    boards = []
    for b in BOARDS:
        c = db.execute(
            "SELECT COUNT(*) FROM codes WHERE board=?", (b["key"],)
        ).fetchone()[0]
        boards.append({**b, "count": c})
    return render_page("Ana Sayfa", "home", HOME_TEMPLATE, boards=boards)


BOARD_TEMPLATE = """
<div class="toolbar">
  <h1>{{ board['icon'] }} {{ board['name'] }}</h1>
  <a class="btn" href="{{ url_for('home') }}">&larr; Board Seçimi</a>
</div>
{% if codes|length == 0 %}
  <div class="empty">Bu board için henüz kod eklenmemiş.</div>
{% else %}
<div class="grid">
  {% for c in codes %}
  <a class="box" href="{{ url_for('code_detail', code_id=c['id']) }}">
    <span class="badge">{{ board['name'] }}</span>
    <h3>{{ c['title'] }}</h3>
    <p>{{ c['description'] }}</p>
  </a>
  {% endfor %}
</div>
{% endif %}
"""


@app.route("/board/<board_key>")
def board_page(board_key):
    if board_key not in BOARD_MAP:
        abort(404)
    db = get_db()
    codes = db.execute(
        "SELECT * FROM codes WHERE board=? ORDER BY id DESC", (board_key,)
    ).fetchall()
    board = BOARD_MAP[board_key]
    return render_page(board["name"], "home", BOARD_TEMPLATE, board=board, codes=codes)


DETAIL_TEMPLATE = """
<div class="toolbar">
  <div>
    <span class="badge">{{ board['icon'] }} {{ board['name'] }}</span>
    <h1>{{ c['title'] }}</h1>
  </div>
  <a class="btn" href="{{ url_for('board_page', board_key=c['board']) }}">&larr; Geri</a>
</div>
<p>{{ c['description'] }}</p>

{% if pins|length > 0 %}
<div class="card">
  <h3>🔌 Pin Bağlantı Tablosu</h3>
  <table>
    <tr><th>Bileşen / Pin</th><th>Arduino Bağlantısı</th></tr>
    {% for p in pins %}
    <tr><td>{{ p['component'] }}</td><td>{{ p['connection'] }}</td></tr>
    {% endfor %}
  </table>
</div>
{% endif %}

<div class="card">
  <h3>💻 Arduino Kodu</h3>
  <div class="code-wrap">
    <button class="copy-btn" onclick="copyCode()">Kopyala</button>
    <pre class="codebox" id="codeblock">{{ c['code_text'] }}</pre>
  </div>
</div>

{% if links|length > 0 %}
<div class="card">
  <h3>🛒 Kullanılan Ürünler</h3>
  <ul class="link-list">
    {% for l in links %}
    <li><a href="{{ l['url'] }}" target="_blank" rel="noopener">{{ l['label'] }}</a></li>
    {% endfor %}
  </ul>
</div>
{% endif %}

<script>
function copyCode(){
  const text = document.getElementById('codeblock').innerText;
  navigator.clipboard.writeText(text).then(()=>{
    const btn = document.querySelector('.copy-btn');
    const old = btn.innerText;
    btn.innerText = 'Kopyalandı!';
    setTimeout(()=>{ btn.innerText = old; }, 1500);
  });
}
</script>
"""


@app.route("/code/<int:code_id>")
def code_detail(code_id):
    db = get_db()
    c = db.execute("SELECT * FROM codes WHERE id=?", (code_id,)).fetchone()
    if not c:
        abort(404)
    pins = db.execute(
        "SELECT * FROM pins WHERE code_id=? ORDER BY id", (code_id,)
    ).fetchall()
    links = db.execute(
        "SELECT * FROM links WHERE code_id=? ORDER BY id", (code_id,)
    ).fetchall()
    board = BOARD_MAP.get(c["board"], {"name": c["board"], "icon": "🔧"})
    return render_page(c["title"], "home", DETAIL_TEMPLATE, c=c, pins=pins, links=links, board=board)


# ----------------------------------------------------------------------------
# Hesaplama Araçları (Direnç + Kondansatör)
# ----------------------------------------------------------------------------

TOOLS_TEMPLATE = """
<h1>🧮 Hesaplama Araçları</h1>
<p class="subtitle">Direnç renk kodu ve kondansatör değeri hesaplayıcıları.</p>

<div class="calc-grid">

<div class="card">
  <h3>🎨 Direnç Renk Kodu Hesaplayıcı</h3>
  <label>Bant Sayısı</label>
  <select id="bandCount" onchange="renderBands()">
    <option value="4">4 Bant</option>
    <option value="5">5 Bant</option>
  </select>
  <div id="bandSelectors"></div>
  <div class="result-box" id="resistorResult">Değer: -</div>
</div>

<div class="card">
  <h3>⚡ Kondansatör Kodu / Birim Çevirici</h3>
  <label>EIA 3 Haneli Kod (örn: 104, 223, 471)</label>
  <input type="text" id="capCode" placeholder="Örn: 104" maxlength="4" oninput="calcCapCode()">
  <div class="result-box" id="capCodeResult">Değer: -</div>

  <label style="margin-top:22px;">Birim Çevirici</label>
  <div class="row-repeat">
    <input type="text" id="capValue" placeholder="Değer" oninput="calcCapConvert()">
    <select id="capUnit" onchange="calcCapConvert()" style="max-width:110px;">
      <option value="pF">pF</option>
      <option value="nF" selected>nF</option>
      <option value="uF">µF</option>
      <option value="mF">mF</option>
    </select>
  </div>
  <div class="result-box" id="capConvertResult">-</div>
</div>

</div>

<script>
const COLORS = [
  {name:'Siyah', hex:'#111111', value:0, mult:1, tol:null},
  {name:'Kahverengi', hex:'#7a4a2b', value:1, mult:10, tol:1},
  {name:'Kırmızı', hex:'#d1332e', value:2, mult:100, tol:2},
  {name:'Turuncu', hex:'#e07b1e', value:3, mult:1000, tol:null},
  {name:'Sarı', hex:'#e8d31c', value:4, mult:10000, tol:null},
  {name:'Yeşil', hex:'#2fa84f', value:5, mult:100000, tol:0.5},
  {name:'Mavi', hex:'#2f6fe0', value:6, mult:1000000, tol:0.25},
  {name:'Mor', hex:'#8a3fe0', value:7, mult:10000000, tol:0.1},
  {name:'Gri', hex:'#9a9a9a', value:8, mult:100000000, tol:0.05},
  {name:'Beyaz', hex:'#f5f5f5', value:9, mult:1000000000, tol:null},
  {name:'Altın', hex:'#d4af37', value:null, mult:0.1, tol:5},
  {name:'Gümüş', hex:'#c0c0c0', value:null, mult:0.01, tol:10},
];

function colorOptions(filterFn, selectedIdx){
  return COLORS.map((c,i)=>{
    if(filterFn && !filterFn(c)) return '';
    return `<option value="${i}" ${i===selectedIdx?'selected':''}>${c.name}</option>`;
  }).join('');
}

function renderBands(){
  const n = parseInt(document.getElementById('bandCount').value);
  const container = document.getElementById('bandSelectors');
  let html = '';
  const digitBands = n === 5 ? 3 : 2;
  for(let i=0;i<digitBands;i++){
    html += `<label>${i+1}. Bant (Basamak)</label>
      <select onchange="calcResistor()" class="digitBand">
        ${colorOptions(c=>c.value!==null, i===0?1:0)}
      </select>`;
  }
  html += `<label>Çarpan Bandı</label>
    <select onchange="calcResistor()" id="multBand">
      ${colorOptions(null, 1)}
    </select>`;
  html += `<label>Tolerans Bandı</label>
    <select onchange="calcResistor()" id="tolBand">
      ${colorOptions(c=>c.tol!==null, 1)}
    </select>`;
  container.innerHTML = html;
  calcResistor();
}

function formatOhms(v){
  if(v >= 1000000) return (v/1000000).toFixed(2).replace(/\\.00$/,'') + ' MΩ';
  if(v >= 1000) return (v/1000).toFixed(2).replace(/\\.00$/,'') + ' kΩ';
  return v.toFixed(2).replace(/\\.00$/,'') + ' Ω';
}

function calcResistor(){
  const digitSelects = document.querySelectorAll('.digitBand');
  let digits = '';
  digitSelects.forEach(s=>{ digits += COLORS[parseInt(s.value)].value; });
  const mult = COLORS[parseInt(document.getElementById('multBand').value)].mult;
  const tolColor = COLORS[parseInt(document.getElementById('tolBand').value)];
  const base = parseInt(digits);
  const ohms = base * mult;
  const tol = tolColor.tol !== null ? tolColor.tol : 20;
  document.getElementById('resistorResult').innerText =
    `Değer: ${formatOhms(ohms)} ± %${tol}`;
}

function calcCapCode(){
  const raw = document.getElementById('capCode').value.trim();
  const el = document.getElementById('capCodeResult');
  if(!/^[0-9]{3,4}$/.test(raw)){ el.innerText = 'Değer: -'; return; }
  const digits = raw.slice(0, raw.length-1);
  const mult = parseInt(raw.slice(-1));
  const pF = parseInt(digits) * Math.pow(10, mult);
  const nF = pF/1000, uF = pF/1e6;
  el.innerText = `Değer: ${pF.toLocaleString('tr-TR')} pF = ${nF.toLocaleString('tr-TR')} nF = ${uF.toLocaleString('tr-TR', {maximumFractionDigits:6})} µF`;
}

function calcCapConvert(){
  const val = parseFloat(document.getElementById('capValue').value);
  const unit = document.getElementById('capUnit').value;
  const el = document.getElementById('capConvertResult');
  if(isNaN(val)){ el.innerText = '-'; return; }
  const toPF = {pF:1, nF:1000, uF:1e6, mF:1e9};
  const pF = val * toPF[unit];
  el.innerText = `${pF.toLocaleString('tr-TR')} pF  |  ${(pF/1000).toLocaleString('tr-TR')} nF  |  ${(pF/1e6).toLocaleString('tr-TR',{maximumFractionDigits:6})} µF  |  ${(pF/1e9).toLocaleString('tr-TR',{maximumFractionDigits:9})} mF`;
}

renderBands();
</script>
"""


@app.route("/tools")
def tools():
    return render_page("Hesaplama Araçları", "tools", TOOLS_TEMPLATE)


# ----------------------------------------------------------------------------
# Admin: giriş / çıkış
# ----------------------------------------------------------------------------

LOGIN_TEMPLATE = """
<h1>🔐 Yönetici Girişi</h1>
{% if error %}<div class="flash error">{{ error }}</div>{% endif %}
<div class="card" style="max-width:380px;">
  <form method="post">
    <label>Kullanıcı Adı</label>
    <input type="text" name="username" required>
    <label>Şifre</label>
    <input type="password" name="password" required>
    <div style="margin-top:20px;">
      <button class="btn primary" type="submit">Giriş Yap</button>
    </div>
  </form>
</div>
"""


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session["is_admin"] = True
            nxt = request.args.get("next") or url_for("admin_dashboard")
            return redirect(nxt)
        error = "Kullanıcı adı veya şifre hatalı."
    return render_page("Yönetici Girişi", "admin", LOGIN_TEMPLATE, error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("home"))


# ----------------------------------------------------------------------------
# Admin: dashboard (listeleme)
# ----------------------------------------------------------------------------

DASHBOARD_TEMPLATE = """
<div class="toolbar">
  <h1>🛠 Yönetici Paneli</h1>
  <a class="btn primary" href="{{ url_for('admin_new') }}">+ Yeni Kod Ekle</a>
</div>
{% if codes|length == 0 %}
  <div class="empty">Henüz kod eklenmemiş.</div>
{% else %}
<table class="adminlist">
  <tr><th>Board</th><th>Başlık</th><th>Pin</th><th>Link</th><th></th></tr>
  {% for c in codes %}
  <tr>
    <td><span class="badge">{{ board_map[c['board']]['icon'] }} {{ board_map[c['board']]['name'] }}</span></td>
    <td>{{ c['title'] }}</td>
    <td>{{ c['pin_count'] }}</td>
    <td>{{ c['link_count'] }}</td>
    <td class="actions">
      <a class="btn small" href="{{ url_for('code_detail', code_id=c['id']) }}" target="_blank">Görüntüle</a>
      <a class="btn small" href="{{ url_for('admin_edit', code_id=c['id']) }}">Düzenle</a>
      <form method="post" action="{{ url_for('admin_delete', code_id=c['id']) }}"
            onsubmit="return confirm('Bu kodu silmek istediğine emin misin?');" style="display:inline;">
        <button class="btn small danger" type="submit">Sil</button>
      </form>
    </td>
  </tr>
  {% endfor %}
</table>
{% endif %}
"""


@app.route("/admin")
@login_required
def admin_dashboard():
    db = get_db()
    rows = db.execute("SELECT * FROM codes ORDER BY id DESC").fetchall()
    codes = []
    for r in rows:
        pin_count = db.execute("SELECT COUNT(*) FROM pins WHERE code_id=?", (r["id"],)).fetchone()[0]
        link_count = db.execute("SELECT COUNT(*) FROM links WHERE code_id=?", (r["id"],)).fetchone()[0]
        d = dict(r)
        d["pin_count"] = pin_count
        d["link_count"] = link_count
        codes.append(d)
    return render_page("Yönetici Paneli", "admin", DASHBOARD_TEMPLATE, codes=codes, board_map=BOARD_MAP)


# ----------------------------------------------------------------------------
# Admin: kod ekleme / düzenleme formu
# ----------------------------------------------------------------------------

FORM_TEMPLATE = """
<div class="toolbar">
  <h1>{{ 'Kod Düzenle' if c else 'Yeni Kod Ekle' }}</h1>
  <a class="btn" href="{{ url_for('admin_dashboard') }}">&larr; Panele Dön</a>
</div>
<form method="post">
  <div class="card">
    <label>Board</label>
    <select name="board" id="fBoard" required>
      {% for b in boards %}
        <option value="{{ b['key'] }}" {{ 'selected' if c and c['board']==b['key'] else '' }}>{{ b['icon'] }} {{ b['name'] }}</option>
      {% endfor %}
    </select>
    <label>Başlık</label>
    <input type="text" name="title" id="fTitle" required value="{{ c['title'] if c else '' }}">
    <label>Açıklama</label>
    <input type="text" name="description" id="fDescription" value="{{ c['description'] if c else '' }}">
    <label>Arduino Kodu</label>
    <textarea class="codearea" name="code_text" id="fCodeText" rows="16" required>{{ c['code_text'] if c else '' }}</textarea>
  </div>

  <div class="card">
    <h3>🔌 Pin Bağlantıları</h3>
    <div id="pinRows">
      {% for p in pins %}
      <div class="row-repeat">
        <input type="text" name="pin_component[]" placeholder="Bileşen / Pin" value="{{ p['component'] }}">
        <input type="text" name="pin_connection[]" placeholder="Arduino Bağlantısı" value="{{ p['connection'] }}">
        <button type="button" class="btn small danger" onclick="this.parentElement.remove()">Sil</button>
      </div>
      {% endfor %}
    </div>
    <button type="button" class="btn small" onclick="addPinRow()">+ Pin Ekle</button>
  </div>

  <div class="card">
    <h3>🛒 Ürün Linkleri</h3>
    <div id="linkRows">
      {% for l in links %}
      <div class="row-repeat">
        <input type="text" name="link_label[]" placeholder="Ürün Adı" value="{{ l['label'] }}">
        <input type="url" name="link_url[]" placeholder="https://..." value="{{ l['url'] }}">
        <button type="button" class="btn small danger" onclick="this.parentElement.remove()">Sil</button>
      </div>
      {% endfor %}
    </div>
    <button type="button" class="btn small" onclick="addLinkRow()">+ Link Ekle</button>
  </div>

  <button class="btn primary" type="submit">Kaydet</button>
</form>

<script>
function addPinRow(){
  const div = document.createElement('div');
  div.className = 'row-repeat';
  div.innerHTML = `<input type="text" name="pin_component[]" placeholder="Bileşen / Pin">
    <input type="text" name="pin_connection[]" placeholder="Arduino Bağlantısı">
    <button type="button" class="btn small danger" onclick="this.parentElement.remove()">Sil</button>`;
  document.getElementById('pinRows').appendChild(div);
}
function addLinkRow(){
  const div = document.createElement('div');
  div.className = 'row-repeat';
  div.innerHTML = `<input type="text" name="link_label[]" placeholder="Ürün Adı">
    <input type="url" name="link_url[]" placeholder="https://...">
    <button type="button" class="btn small danger" onclick="this.parentElement.remove()">Sil</button>`;
  document.getElementById('linkRows').appendChild(div);
}
</script>
"""


def save_code_form(code_id=None):
    board = request.form.get("board")
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    code_text = request.form.get("code_text", "")

    if board not in BOARD_KEYS or not title or not code_text:
        flash("Lütfen zorunlu alanları doldurun.")
        return None

    db = get_db()
    if code_id is None:
        cur = db.execute(
            "INSERT INTO codes (board, title, description, code_text, created_at) VALUES (?,?,?,?,?)",
            (board, title, description, code_text, datetime.now(timezone.utc).isoformat()),
        )
        code_id = cur.lastrowid
    else:
        db.execute(
            "UPDATE codes SET board=?, title=?, description=?, code_text=? WHERE id=?",
            (board, title, description, code_text, code_id),
        )
        db.execute("DELETE FROM pins WHERE code_id=?", (code_id,))
        db.execute("DELETE FROM links WHERE code_id=?", (code_id,))

    components = request.form.getlist("pin_component[]")
    connections = request.form.getlist("pin_connection[]")
    for comp, conn in zip(components, connections):
        if comp.strip() or conn.strip():
            db.execute(
                "INSERT INTO pins (code_id, component, connection) VALUES (?,?,?)",
                (code_id, comp.strip(), conn.strip()),
            )

    labels = request.form.getlist("link_label[]")
    urls = request.form.getlist("link_url[]")
    for label, url in zip(labels, urls):
        if label.strip() and url.strip():
            db.execute(
                "INSERT INTO links (code_id, label, url) VALUES (?,?,?)",
                (code_id, label.strip(), url.strip()),
            )

    db.commit()
    return code_id


@app.route("/admin/new", methods=["GET", "POST"])
@login_required
def admin_new():
    if request.method == "POST":
        code_id = save_code_form()
        if code_id:
            return redirect(url_for("admin_dashboard"))
    return render_page(
        "Yeni Kod Ekle", "admin", FORM_TEMPLATE, c=None, pins=[], links=[], boards=BOARDS
    )


@app.route("/admin/edit/<int:code_id>", methods=["GET", "POST"])
@login_required
def admin_edit(code_id):
    db = get_db()
    c = db.execute("SELECT * FROM codes WHERE id=?", (code_id,)).fetchone()
    if not c:
        abort(404)
    if request.method == "POST":
        if save_code_form(code_id):
            return redirect(url_for("admin_dashboard"))
    pins = db.execute("SELECT * FROM pins WHERE code_id=? ORDER BY id", (code_id,)).fetchall()
    links = db.execute("SELECT * FROM links WHERE code_id=? ORDER BY id", (code_id,)).fetchall()
    return render_page(
        "Kod Düzenle", "admin", FORM_TEMPLATE, c=c, pins=pins, links=links, boards=BOARDS
    )


@app.route("/admin/delete/<int:code_id>", methods=["POST"])
@login_required
def admin_delete(code_id):
    db = get_db()
    db.execute("DELETE FROM codes WHERE id=?", (code_id,))
    db.commit()
    return redirect(url_for("admin_dashboard"))



# ----------------------------------------------------------------------------
# 404
# ----------------------------------------------------------------------------

NOT_FOUND_TEMPLATE = """
<div class="empty">
  <h1>404</h1>
  <p>Aradığınız sayfa bulunamadı.</p>
  <a class="btn primary" href="{{ url_for('home') }}">Ana Sayfaya Dön</a>
</div>
"""


@app.errorhandler(404)
def not_found(e):
    return render_page("Bulunamadı", "home", NOT_FOUND_TEMPLATE), 404


# ----------------------------------------------------------------------------
# Seed verisi: 30 gerçek / çalışan Arduino kodu
# ----------------------------------------------------------------------------

SEED_DATA = [

# ============================== UNO / NANO / MEGA (AVR ortak) ==============================

{
"board": "uno",
"title": "LED Yakıp Söndürme (Blink)",
"description": "Dijital pin ile bir LED'i 1 saniye aralıklarla yakıp söndürür.",
"pins": [("LED Anot (+)", "Dijital Pin 13 (220Ω direnç ile)"), ("LED Katot (-)", "GND")],
"links": [],
"code": """const int LED_PIN = 13;

void setup() {
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_PIN, HIGH);
  delay(1000);
  digitalWrite(LED_PIN, LOW);
  delay(1000);
}
"""
},

{
"board": "nano",
"title": "Buton ile LED Kontrolü (Debounce)",
"description": "Butona her basıldığında LED durumunu değiştirir, yazılımsal debounce içerir.",
"pins": [("Buton Bacak 1", "Dijital Pin 2"), ("Buton Bacak 2", "GND"), ("LED Anot (+)", "Dijital Pin 8 (220Ω direnç ile)"), ("LED Katot (-)", "GND")],
"links": [],
"code": """const int BUTTON_PIN = 2;
const int LED_PIN = 8;

int ledState = LOW;
int lastButtonState = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, ledState);
}

void loop() {
  int reading = digitalRead(BUTTON_PIN);

  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading == LOW && lastButtonState == HIGH) {
      ledState = !ledState;
      digitalWrite(LED_PIN, ledState);
    }
  }

  lastButtonState = reading;
}
"""
},

{
"board": "uno",
"title": "Potansiyometre ile LED Parlaklığı (PWM)",
"description": "Potansiyometreden okunan analog değeri PWM ile LED parlaklığına dönüştürür.",
"pins": [("Potansiyometre Orta Pin", "Analog Pin A0"), ("Potansiyometre Uç Pinler", "5V ve GND"), ("LED Anot (+)", "Dijital PWM Pin 9 (220Ω direnç ile)"), ("LED Katot (-)", "GND")],
"links": [],
"code": """const int POT_PIN = A0;
const int LED_PIN = 9;

void setup() {
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  int potValue = analogRead(POT_PIN);       // 0 - 1023
  int brightness = map(potValue, 0, 1023, 0, 255);
  analogWrite(LED_PIN, brightness);
}
"""
},

{
"board": "nano",
"title": "DHT11 Sıcaklık ve Nem Sensörü",
"description": "DHT11 sensöründen sıcaklık ve nem verisini okuyup Seri Port'a yazdırır.",
"pins": [("VCC", "5V"), ("DATA", "Dijital Pin 2 (10K pull-up direnç ile)"), ("GND", "GND")],
"links": [],
"code": """#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  delay(2000);

  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("DHT11 sensöründen veri okunamadı!");
    return;
  }

  Serial.print("Nem: ");
  Serial.print(humidity);
  Serial.print(" %\\t");
  Serial.print("Sicaklik: ");
  Serial.print(temperature);
  Serial.println(" *C");
}
"""
},

{
"board": "uno",
"title": "HC-SR04 Ultrasonik Mesafe Sensörü",
"description": "Ultrasonik sensör ile santimetre cinsinden mesafe ölçümü yapar.",
"pins": [("VCC", "5V"), ("TRIG", "Dijital Pin 9"), ("ECHO", "Dijital Pin 10"), ("GND", "GND")],
"links": [],
"code": """const int TRIG_PIN = 9;
const int ECHO_PIN = 10;

void setup() {
  Serial.begin(9600);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
}

void loop() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);
  float distanceCm = duration * 0.0343 / 2;

  Serial.print("Mesafe: ");
  Serial.print(distanceCm);
  Serial.println(" cm");

  delay(300);
}
"""
},

{
"board": "nano",
"title": "Servo Motor Kontrolü",
"description": "Servo motoru 0-180 derece arasında yavaşça hareket ettirir.",
"pins": [("Sinyal (Turuncu/Sarı)", "Dijital PWM Pin 9"), ("VCC (Kırmızı)", "5V (harici besleme önerilir)"), ("GND (Kahverengi/Siyah)", "GND")],
"links": [],
"code": """#include <Servo.h>

Servo myServo;
const int SERVO_PIN = 9;

void setup() {
  myServo.attach(SERVO_PIN);
}

void loop() {
  for (int pos = 0; pos <= 180; pos++) {
    myServo.write(pos);
    delay(15);
  }
  for (int pos = 180; pos >= 0; pos--) {
    myServo.write(pos);
    delay(15);
  }
}
"""
},

{
"board": "uno",
"title": "16x2 LCD I2C Ekran",
"description": "I2C modüllü 16x2 LCD ekrana metin ve sayaç yazdırır.",
"pins": [("VCC", "5V"), ("GND", "GND"), ("SDA", "A4 (Uno/Nano)"), ("SCL", "A5 (Uno/Nano)")],
"links": [],
"code": """#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2); // Adres 0x27 veya 0x3F olabilir
int counter = 0;

void setup() {
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("ArduKod Hazir!");
}

void loop() {
  lcd.setCursor(0, 1);
  lcd.print("Sayac: ");
  lcd.print(counter);
  lcd.print("   ");
  counter++;
  delay(1000);
}
"""
},

{
"board": "nano",
"title": "RGB LED Renk Kontrolü",
"description": "Ortak katotlu RGB LED'de PWM kullanarak renk geçişleri yapar.",
"pins": [("Kırmızı (R)", "PWM Pin 9"), ("Yeşil (G)", "PWM Pin 10"), ("Mavi (B)", "PWM Pin 11"), ("Katot (-)", "GND")],
"links": [],
"code": """const int RED_PIN = 9;
const int GREEN_PIN = 10;
const int BLUE_PIN = 11;

void setColor(int r, int g, int b) {
  analogWrite(RED_PIN, r);
  analogWrite(GREEN_PIN, g);
  analogWrite(BLUE_PIN, b);
}

void setup() {
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);
}

void loop() {
  setColor(255, 0, 0);   delay(1000); // Kırmızı
  setColor(0, 255, 0);   delay(1000); // Yeşil
  setColor(0, 0, 255);   delay(1000); // Mavi
  setColor(255, 255, 0); delay(1000); // Sarı
  setColor(0, 255, 255); delay(1000); // Camgöbeği
  setColor(255, 0, 255); delay(1000); // Magenta
}
"""
},

{
"board": "uno",
"title": "IR Alıcı ile Kumanda Kodu Okuma",
"description": "IR alıcı modülü ile kumandadan gelen kodları Seri Port'a yazdırır (IRremote kütüphanesi v3+).",
"pins": [("VCC", "5V"), ("GND", "GND"), ("OUT", "Dijital Pin 11")],
"links": [],
"code": """#include <IRremote.hpp>

const int IR_RECEIVE_PIN = 11;

void setup() {
  Serial.begin(9600);
  IrReceiver.begin(IR_RECEIVE_PIN, ENABLE_LED_FEEDBACK);
}

void loop() {
  if (IrReceiver.decode()) {
    Serial.print("Alinan Kod (HEX): ");
    Serial.println(IrReceiver.decodedIRData.decodedRawData, HEX);
    IrReceiver.resume();
  }
}
"""
},

{
"board": "uno",
"title": "PIR Hareket Sensörü",
"description": "PIR sensörü hareket algıladığında LED'i yakar ve Seri Port'a bildirim yazar.",
"pins": [("VCC", "5V"), ("OUT", "Dijital Pin 3"), ("GND", "GND"), ("LED Anot (+)", "Dijital Pin 13")],
"links": [],
"code": """const int PIR_PIN = 3;
const int LED_PIN = 13;

void setup() {
  Serial.begin(9600);
  pinMode(PIR_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  int motion = digitalRead(PIR_PIN);
  if (motion == HIGH) {
    digitalWrite(LED_PIN, HIGH);
    Serial.println("Hareket algilandi!");
  } else {
    digitalWrite(LED_PIN, LOW);
  }
  delay(200);
}
"""
},

{
"board": "uno",
"title": "Buzzer ile Melodi Çalma",
"description": "Pasif buzzer kullanarak basit bir nota dizisi (melodi) çalar.",
"pins": [("+ (Sinyal)", "Dijital Pin 8"), ("- (GND)", "GND")],
"links": [],
"code": """const int BUZZER_PIN = 8;

int melody[] = {262, 294, 330, 349, 392, 440, 494, 523};
int noteDuration = 300;

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  for (int i = 0; i < 8; i++) {
    tone(BUZZER_PIN, melody[i], noteDuration);
    delay(noteDuration + 50);
  }
  noTone(BUZZER_PIN);
  delay(2000);
}
"""
},

{
"board": "uno",
"title": "Tek Haneli 7 Segment Sayaç",
"description": "Ortak katotlu 7 segment display üzerinde 0'dan 9'a sayar.",
"pins": [("a,b,c,d,e,f,g", "Dijital Pin 2-8 (her biri 220Ω direnç ile)"), ("Ortak Katot", "GND")],
"links": [],
"code": """// Segment pinleri: a,b,c,d,e,f,g -> 2,3,4,5,6,7,8
const int segPins[7] = {2, 3, 4, 5, 6, 7, 8};

// 0-9 rakamları icin segment tablosu (1 = yanik)
const byte digits[10][7] = {
  {1,1,1,1,1,1,0}, // 0
  {0,1,1,0,0,0,0}, // 1
  {1,1,0,1,1,0,1}, // 2
  {1,1,1,1,0,0,1}, // 3
  {0,1,1,0,0,1,1}, // 4
  {1,0,1,1,0,1,1}, // 5
  {1,0,1,1,1,1,1}, // 6
  {1,1,1,0,0,0,0}, // 7
  {1,1,1,1,1,1,1}, // 8
  {1,1,1,1,0,1,1}  // 9
};

void showDigit(int d) {
  for (int i = 0; i < 7; i++) {
    digitalWrite(segPins[i], digits[d][i]);
  }
}

void setup() {
  for (int i = 0; i < 7; i++) pinMode(segPins[i], OUTPUT);
}

void loop() {
  for (int d = 0; d <= 9; d++) {
    showDigit(d);
    delay(800);
  }
}
"""
},

{
"board": "uno",
"title": "Röle Modülü ile Cihaz Kontrolü",
"description": "Röle modülü üzerinden 220V bir cihazı (lamba, motor vb.) açıp kapatır.",
"pins": [("VCC", "5V"), ("GND", "GND"), ("IN", "Dijital Pin 7")],
"links": [],
"code": """const int RELAY_PIN = 7;

void setup() {
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH); // Çoğu röle modülünde LOW = aktif (NC/NO'ya dikkat)
}

void loop() {
  digitalWrite(RELAY_PIN, LOW);  // Röleyi aktif et (cihazı aç)
  delay(3000);
  digitalWrite(RELAY_PIN, HIGH); // Röleyi pasif et (cihazı kapat)
  delay(3000);
}
"""
},

{
"board": "uno",
"title": "28BYJ-48 Step Motor Kontrolü (ULN2003)",
"description": "ULN2003 sürücü kartı ile 28BYJ-48 step motoru saat yönünde ve tersine döndürür.",
"pins": [("IN1-IN4", "Dijital Pin 8, 9, 10, 11"), ("VCC", "5V (harici besleme önerilir)"), ("GND", "GND")],
"links": [],
"code": """#include <Stepper.h>

const int STEPS_PER_REV = 2048;
Stepper myStepper(STEPS_PER_REV, 8, 10, 9, 11);

void setup() {
  myStepper.setSpeed(10); // RPM
}

void loop() {
  myStepper.step(STEPS_PER_REV / 4); // 90 derece saat yönü
  delay(1000);
  myStepper.step(-STEPS_PER_REV / 4); // 90 derece ters yön
  delay(1000);
}
"""
},

{
"board": "nano",
"title": "Joystick Modülü Okuma",
"description": "Analog joystick modülünün X, Y eksenlerini ve buton durumunu okur.",
"pins": [("VRx", "Analog Pin A0"), ("VRy", "Analog Pin A1"), ("SW", "Dijital Pin 2"), ("VCC", "5V"), ("GND", "GND")],
"links": [],
"code": """const int VRX_PIN = A0;
const int VRY_PIN = A1;
const int SW_PIN = 2;

void setup() {
  Serial.begin(9600);
  pinMode(SW_PIN, INPUT_PULLUP);
}

void loop() {
  int xValue = analogRead(VRX_PIN);
  int yValue = analogRead(VRY_PIN);
  int buttonState = digitalRead(SW_PIN);

  Serial.print("X: "); Serial.print(xValue);
  Serial.print(" | Y: "); Serial.print(yValue);
  Serial.print(" | Buton: "); Serial.println(buttonState == LOW ? "Basili" : "Serbest");

  delay(200);
}
"""
},

{
"board": "uno",
"title": "4x4 Keypad Okuma",
"description": "4x4 matris keypad üzerinden basılan tuşu okuyup Seri Port'a yazdırır.",
"pins": [("R1-R4", "Dijital Pin 9, 8, 7, 6"), ("C1-C4", "Dijital Pin 5, 4, 3, 2")],
"links": [],
"code": """#include <Keypad.h>

const byte ROWS = 4;
const byte COLS = 4;

char keys[ROWS][COLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};

byte rowPins[ROWS] = {9, 8, 7, 6};
byte colPins[COLS] = {5, 4, 3, 2};

Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

void setup() {
  Serial.begin(9600);
}

void loop() {
  char key = keypad.getKey();
  if (key) {
    Serial.print("Basilan tus: ");
    Serial.println(key);
  }
}
"""
},

{
"board": "nano",
"title": "LDR (Fotodirenç) ile Karanlık Sensörü",
"description": "Ortam ışığını LDR ile ölçer, karanlıkta otomatik olarak LED yakar.",
"pins": [("LDR Bacak 1", "5V"), ("LDR Bacak 2", "A0 + 10K direnç ile GND'ye"), ("LED Anot (+)", "Dijital Pin 8")],
"links": [],
"code": """const int LDR_PIN = A0;
const int LED_PIN = 8;
const int THRESHOLD = 400; // Ortama göre ayarlayın

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  int lightLevel = analogRead(LDR_PIN);
  Serial.println(lightLevel);

  if (lightLevel < THRESHOLD) {
    digitalWrite(LED_PIN, HIGH); // Karanlık -> LED yak
  } else {
    digitalWrite(LED_PIN, LOW);  // Aydınlık -> LED söndür
  }
  delay(200);
}
"""
},

{
"board": "uno",
"title": "RFID RC522 Kart Okuma",
"description": "MFRC522 modülü ile RFID kart/anahtarlık UID'sini okuyup Seri Port'a yazdırır.",
"pins": [("SDA(SS)", "Pin 10"), ("SCK", "Pin 13"), ("MOSI", "Pin 11"), ("MISO", "Pin 12"), ("RST", "Pin 9"), ("VCC", "3.3V"), ("GND", "GND")],
"links": [],
"code": """#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  Serial.println("Kart okutunuz...");
}

void loop() {
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  Serial.print("Kart UID: ");
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(mfrc522.uid.uidByte[i], HEX);
  }
  Serial.println();

  mfrc522.PICC_HaltA();
}
"""
},

{
"board": "uno",
"title": "DS18B20 Su Geçirmez Sıcaklık Sensörü",
"description": "OneWire haberleşme protokolü ile DS18B20 sıcaklık sensöründen veri okur.",
"pins": [("VCC", "5V"), ("DATA", "Dijital Pin 2 (4.7K pull-up direnç ile)"), ("GND", "GND")],
"links": [],
"code": """#include <OneWire.h>
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
  float tempC = sensors.getTempCByIndex(0);

  Serial.print("Sicaklik: ");
  Serial.print(tempC);
  Serial.println(" *C");

  delay(1000);
}
"""
},

{
"board": "uno",
"title": "Alev Sensörü (Flame Sensor)",
"description": "IR alev sensörü ile yangın/alev algılar ve buzzer ile alarm çalar.",
"pins": [("VCC", "5V"), ("DO", "Dijital Pin 4"), ("GND", "GND"), ("Buzzer +", "Dijital Pin 8")],
"links": [],
"code": """const int FLAME_PIN = 4;
const int BUZZER_PIN = 8;

void setup() {
  Serial.begin(9600);
  pinMode(FLAME_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  int flameDetected = digitalRead(FLAME_PIN); // Çoğu modülde LOW = alev algılandı

  if (flameDetected == LOW) {
    Serial.println("UYARI: Alev algilandi!");
    tone(BUZZER_PIN, 1000);
  } else {
    noTone(BUZZER_PIN);
  }
  delay(200);
}
"""
},

{
"board": "uno",
"title": "Toprak Nem Sensörü (Soil Moisture)",
"description": "Toprak nem seviyesini analog olarak okur, kuruduğunda uyarı verir (otomatik sulama sistemleri için temel).",
"pins": [("VCC", "5V"), ("AOUT", "Analog Pin A0"), ("GND", "GND"), ("LED (Uyarı)", "Dijital Pin 8")],
"links": [],
"code": """const int SOIL_PIN = A0;
const int LED_PIN = 8;
const int DRY_THRESHOLD = 500; // Kalibre edilmeli

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  int moisture = analogRead(SOIL_PIN);
  Serial.print("Nem seviyesi: ");
  Serial.println(moisture);

  if (moisture > DRY_THRESHOLD) {
    digitalWrite(LED_PIN, HIGH); // Toprak kuru -> uyar
  } else {
    digitalWrite(LED_PIN, LOW);
  }
  delay(1000);
}
"""
},

{
"board": "nano",
"title": "Ses Sensörü ile Alkışla Açma",
"description": "Ses sensörü modülü ile belirli bir ses seviyesi algılandığında LED'i tetikler (alkışla aç/kapa mantığı).",
"pins": [("VCC", "5V"), ("DO", "Dijital Pin 3"), ("GND", "GND"), ("LED Anot (+)", "Dijital Pin 13")],
"links": [],
"code": """const int SOUND_PIN = 3;
const int LED_PIN = 13;

bool ledState = false;
unsigned long lastTrigger = 0;
const unsigned long cooldown = 800;

void setup() {
  pinMode(SOUND_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  int sound = digitalRead(SOUND_PIN);

  if (sound == HIGH && (millis() - lastTrigger) > cooldown) {
    ledState = !ledState;
    digitalWrite(LED_PIN, ledState);
    lastTrigger = millis();
  }
}
"""
},

{
"board": "mega",
"title": "MPU6050 Jiroskop / İvme Ölçer",
"description": "MPU6050 sensöründen ivme ve açısal hız verilerini I2C üzerinden okur.",
"pins": [("VCC", "5V"), ("GND", "GND"), ("SCL", "Pin 21 (Mega)"), ("SDA", "Pin 20 (Mega)")],
"links": [],
"code": """#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  mpu.initialize();

  if (mpu.testConnection()) {
    Serial.println("MPU6050 baglandi!");
  } else {
    Serial.println("MPU6050 baglanti hatasi!");
  }
}

void loop() {
  int16_t ax, ay, az, gx, gy, gz;
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  Serial.print("Ivme X/Y/Z: ");
  Serial.print(ax); Serial.print(" / ");
  Serial.print(ay); Serial.print(" / ");
  Serial.println(az);

  delay(300);
}
"""
},

{
"board": "mega",
"title": "L298N ile DC Motor Kontrolü",
"description": "L298N motor sürücü kartı ile iki DC motorun yön ve hızını kontrol eder.",
"pins": [("ENA", "PWM Pin 5"), ("IN1", "Pin 6"), ("IN2", "Pin 7"), ("ENB", "PWM Pin 9"), ("IN3", "Pin 8"), ("IN4", "Pin 10"), ("VCC (Motor)", "Harici Güç Kaynağı"), ("GND", "Ortak GND")],
"links": [],
"code": """// Motor A
const int ENA = 5;
const int IN1 = 6;
const int IN2 = 7;
// Motor B
const int ENB = 9;
const int IN3 = 8;
const int IN4 = 10;

void motorA(int speed, bool forward) {
  digitalWrite(IN1, forward ? HIGH : LOW);
  digitalWrite(IN2, forward ? LOW : HIGH);
  analogWrite(ENA, speed);
}

void motorB(int speed, bool forward) {
  digitalWrite(IN3, forward ? HIGH : LOW);
  digitalWrite(IN4, forward ? LOW : HIGH);
  analogWrite(ENB, speed);
}

void setup() {
  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
}

void loop() {
  motorA(200, true);
  motorB(200, true);
  delay(2000);

  motorA(200, false);
  motorB(200, false);
  delay(2000);
}
"""
},

{
"board": "mega",
"title": "HX711 ile Load Cell Ağırlık Ölçümü",
"description": "HX711 amplifikatör modülü ve load cell kullanarak gram cinsinden ağırlık ölçer.",
"pins": [("VCC", "5V"), ("GND", "GND"), ("DT", "Pin 3"), ("SCK", "Pin 2")],
"links": [],
"code": """#include <HX711.h>

const int LOADCELL_DOUT_PIN = 3;
const int LOADCELL_SCK_PIN = 2;
const float CALIBRATION_FACTOR = 2280.0; // Kendi hücrenize göre kalibre edin

HX711 scale;

void setup() {
  Serial.begin(9600);
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  scale.set_scale(CALIBRATION_FACTOR);
  scale.tare(); // Sıfırlama
  Serial.println("Terazi hazir, tartmaya baslayabilirsiniz.");
}

void loop() {
  Serial.print("Agirlik: ");
  Serial.print(scale.get_units(10), 1);
  Serial.println(" gram");
  delay(500);
}
"""
},

# ============================== ESP32 / ESP8266 ==============================

{
"board": "esp32",
"title": "ESP32 WiFi Web Sunucu ile LED Kontrolü",
"description": "ESP32 üzerinde web sunucu açarak tarayıcıdan bir LED'i uzaktan aç/kapat.",
"pins": [("LED Anot (+)", "GPIO 2 (dahili LED çoğu kartta GPIO2)"), ("LED Katot (-)", "GND")],
"links": [],
"code": """#include <WiFi.h>

const char* ssid = "WIFI_ADINIZ";
const char* password = "WIFI_SIFRENIZ";
const int LED_PIN = 2;

WiFiServer server(80);

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\\nBaglandi! IP adresi: ");
  Serial.println(WiFi.localIP());

  server.begin();
}

void loop() {
  WiFiClient client = server.available();
  if (!client) return;

  String request = client.readStringUntil('\\r');
  client.flush();

  if (request.indexOf("/LED=ON") != -1) digitalWrite(LED_PIN, HIGH);
  if (request.indexOf("/LED=OFF") != -1) digitalWrite(LED_PIN, LOW);

  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: text/html");
  client.println();
  client.println("<h1>ArduKod ESP32</h1>");
  client.println("<a href=\\"/LED=ON\\">LED AC</a><br>");
  client.println("<a href=\\"/LED=OFF\\">LED KAPAT</a>");

  client.stop();
}
"""
},

{
"board": "esp8266",
"title": "ESP8266 WiFi Bağlantısı ve HTTP GET İsteği",
"description": "ESP8266 (NodeMCU) ile WiFi ağına bağlanıp bir web sunucusundan veri çeker.",
"pins": [("Kart üzerinde harici pin bağlantısı gerekmez (WiFi haberleşmesi dahili)", "-")],
"links": [],
"code": """#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* ssid = "WIFI_ADINIZ";
const char* password = "WIFI_SIFRENIZ";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\\nWiFi baglandi!");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;

    http.begin(client, "http://example.com");
    int httpCode = http.GET();

    if (httpCode > 0) {
      String payload = http.getString();
      Serial.println(payload);
    }
    http.end();
  }
  delay(10000);
}
"""
},

{
"board": "esp32",
"title": "ESP32 Bluetooth Classic Seri Haberleşme",
"description": "ESP32'nin dahili Bluetooth'unu kullanarak telefonla kablosuz seri haberleşme kurar.",
"pins": [("Kart üzerinde harici pin bağlantısı gerekmez (Bluetooth dahili)", "-")],
"links": [],
"code": """#include <BluetoothSerial.h>

BluetoothSerial SerialBT;

void setup() {
  Serial.begin(115200);
  SerialBT.begin("ArduKod_ESP32"); // Bluetooth cihaz adı
  Serial.println("Bluetooth baslatildi, eslesmeye hazir.");
}

void loop() {
  if (SerialBT.available()) {
    char c = SerialBT.read();
    Serial.write(c);
  }
  if (Serial.available()) {
    char c = Serial.read();
    SerialBT.write(c);
  }
}
"""
},

{
"board": "esp32",
"title": "ESP32 ile MQTT Yayını (PubSubClient)",
"description": "ESP32'den bir MQTT broker'a sıcaklık verisi gibi bir değer yayınlar.",
"pins": [("Kart üzerinde harici pin bağlantısı gerekmez (WiFi/MQTT dahili)", "-")],
"links": [],
"code": """#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "WIFI_ADINIZ";
const char* password = "WIFI_SIFRENIZ";
const char* mqtt_server = "broker.hivemq.com";

WiFiClient espClient;
PubSubClient client(espClient);

void setupWifi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("ArduKodESP32Client")) {
      client.subscribe("ardukod/komut");
    } else {
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setupWifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  float sicaklik = 24.5; // örnek sensör verisi
  char msg[10];
  dtostrf(sicaklik, 4, 1, msg);
  client.publish("ardukod/sicaklik", msg);

  delay(5000);
}
"""
},

{
"board": "esp8266",
"title": "ESP8266 Web Sunucu ile Röle Kontrolü",
"description": "NodeMCU üzerinde web sayfası açarak röle modülünü uzaktan kontrol eder.",
"pins": [("Röle IN", "GPIO 5 (D1)"), ("Röle VCC", "3.3V/5V"), ("Röle GND", "GND")],
"links": [],
"code": """#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "WIFI_ADINIZ";
const char* password = "WIFI_SIFRENIZ";
const int RELAY_PIN = 5; // D1

ESP8266WebServer server(80);

void handleRoot() {
  String html = "<h1>ArduKod Role Kontrol</h1>"
                "<a href=\\"/on\\"><button>AC</button></a> "
                "<a href=\\"/off\\"><button>KAPAT</button></a>";
  server.send(200, "text/html", html);
}

void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH); // Pasif başlangıç

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.on("/on", []() { digitalWrite(RELAY_PIN, LOW); handleRoot(); });
  server.on("/off", []() { digitalWrite(RELAY_PIN, HIGH); handleRoot(); });
  server.begin();
}

void loop() {
  server.handleClient();
}
"""
},

# ============================== EK UNO PROJELERİ ==============================

{
"board": "uno",
"title": "LM35 Analog Sıcaklık Sensörü",
"description": "LM35 sensöründen analog voltaj okuyup santigrat dereceye çevirir.",
"pins": [("VCC", "5V"), ("GND", "GND"), ("OUT", "Analog Pin A0")],
"links": [],
"code": """const int LM35_PIN = A0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int reading = analogRead(LM35_PIN);
  float voltage = reading * (5.0 / 1023.0);
  float tempC = voltage * 100.0; // LM35: 10mV / °C

  Serial.print("Sicaklik: ");
  Serial.print(tempC);
  Serial.println(" *C");
  delay(1000);
}
"""
},

{
"board": "uno",
"title": "MQ-2 Gaz/Duman Sensörü + Buzzer Alarm",
"description": "MQ-2 sensörü ile gaz/duman seviyesini ölçer, eşik aşıldığında buzzer ile alarm çalar.",
"pins": [("VCC", "5V"), ("GND", "GND"), ("AOUT", "Analog Pin A0"), ("Buzzer +", "Dijital Pin 8")],
"links": [],
"code": """const int MQ2_PIN = A0;
const int BUZZER_PIN = 8;
const int GAS_THRESHOLD = 400; // Ortama göre kalibre edin

void setup() {
  Serial.begin(9600);
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  int gasLevel = analogRead(MQ2_PIN);
  Serial.print("Gaz seviyesi: ");
  Serial.println(gasLevel);

  if (gasLevel > GAS_THRESHOLD) {
    tone(BUZZER_PIN, 1000);
    Serial.println("UYARI: Gaz/Duman algilandi!");
  } else {
    noTone(BUZZER_PIN);
  }
  delay(500);
}
"""
},

{
"board": "uno",
"title": "Yağmur Sensörü (Rain Sensor)",
"description": "Yağmur sensörü ile ıslaklık seviyesini ölçer, yağmur algılandığında LED yakar.",
"pins": [("VCC", "5V"), ("GND", "GND"), ("AO", "Analog Pin A0"), ("LED Anot (+)", "Dijital Pin 8")],
"links": [],
"code": """const int RAIN_PIN = A0;
const int LED_PIN = 8;

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  int value = analogRead(RAIN_PIN); // Kuruken yüksek, ıslakken düşük değer verir
  Serial.print("Yagmur sensoru: ");
  Serial.println(value);

  if (value < 500) {
    digitalWrite(LED_PIN, HIGH); // Yağmur algılandı
    Serial.println("Yagmur algilandi!");
  } else {
    digitalWrite(LED_PIN, LOW);
  }
  delay(500);
}
"""
},

{
"board": "uno",
"title": "SW-420 Titreşim (Vibration) Sensörü",
"description": "Titreşim sensörü ile darbe/sarsıntı algılar ve LED ile bildirir.",
"pins": [("VCC", "5V"), ("GND", "GND"), ("DO", "Dijital Pin 3"), ("LED Anot (+)", "Dijital Pin 8")],
"links": [],
"code": """const int VIBRATION_PIN = 3;
const int LED_PIN = 8;

void setup() {
  Serial.begin(9600);
  pinMode(VIBRATION_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  int vibration = digitalRead(VIBRATION_PIN);
  if (vibration == HIGH) {
    digitalWrite(LED_PIN, HIGH);
    Serial.println("Titresim algilandi!");
  } else {
    digitalWrite(LED_PIN, LOW);
  }
  delay(100);
}
"""
},

{
"board": "uno",
"title": "DS3231 RTC Modülü ile Saat Okuma",
"description": "DS3231 gerçek zamanlı saat modülünden tarih ve saat bilgisini I2C üzerinden okur (RTClib kütüphanesi gerekir).",
"pins": [("VCC", "5V"), ("GND", "GND"), ("SDA", "A4 (Uno/Nano)"), ("SCL", "A5 (Uno/Nano)")],
"links": [],
"code": """#include <Wire.h>
#include <RTClib.h>

RTC_DS3231 rtc;

void setup() {
  Serial.begin(9600);
  if (!rtc.begin()) {
    Serial.println("RTC modulu bulunamadi!");
    while (1);
  }
  // Modülü bilgisayar saatine ayarlamak için (sadece ilk yüklemede) alttaki satırı açın:
  // rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
}

void loop() {
  DateTime now = rtc.now();
  Serial.print(now.year()); Serial.print('/');
  Serial.print(now.month()); Serial.print('/');
  Serial.print(now.day()); Serial.print(' ');
  Serial.print(now.hour()); Serial.print(':');
  Serial.print(now.minute()); Serial.print(':');
  Serial.println(now.second());
  delay(1000);
}
"""
},

{
"board": "uno",
"title": "WS2812 (NeoPixel) LED Şerit Renk Efekti",
"description": "Adafruit NeoPixel kütüphanesi ile WS2812 LED şeridinde kayan ışık efekti oluşturur.",
"pins": [("VCC", "5V"), ("GND", "GND"), ("DIN", "Dijital Pin 6")],
"links": [],
"code": """#include <Adafruit_NeoPixel.h>

#define LED_PIN 6
#define LED_COUNT 8

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  strip.begin();
  strip.show();
  strip.setBrightness(80);
}

void loop() {
  for (int i = 0; i < LED_COUNT; i++) {
    strip.clear();
    strip.setPixelColor(i, strip.Color(0, 150, 255));
    strip.show();
    delay(100);
  }
}
"""
},

{
"board": "uno",
"title": "İki IR Sensörlü Çizgi İzleyen Robot (L298N)",
"description": "İki IR sensör ve L298N motor sürücü kullanarak basit bir çizgi izleyen robot mantığı.",
"pins": [("IR Sol", "Dijital Pin 2"), ("IR Sağ", "Dijital Pin 4"), ("ENA", "PWM Pin 5"), ("IN1", "Pin 6"), ("IN2", "Pin 7"), ("ENB", "PWM Pin 9"), ("IN3", "Pin 8"), ("IN4", "Pin 10")],
"links": [],
"code": """// IR sensörler: çizgi üzerinde LOW, dışında HIGH varsayımı - sensörünüze göre kontrol edin
const int IR_LEFT = 2;
const int IR_RIGHT = 4;
const int ENA = 5, IN1 = 6, IN2 = 7;
const int ENB = 9, IN3 = 8, IN4 = 10;
const int SPEED = 150;

void motorLeft(bool forward, int speed) {
  digitalWrite(IN1, forward ? HIGH : LOW);
  digitalWrite(IN2, forward ? LOW : HIGH);
  analogWrite(ENA, speed);
}
void motorRight(bool forward, int speed) {
  digitalWrite(IN3, forward ? HIGH : LOW);
  digitalWrite(IN4, forward ? LOW : HIGH);
  analogWrite(ENB, speed);
}

void setup() {
  pinMode(IR_LEFT, INPUT);
  pinMode(IR_RIGHT, INPUT);
  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
}

void loop() {
  bool leftOnLine = digitalRead(IR_LEFT) == LOW;
  bool rightOnLine = digitalRead(IR_RIGHT) == LOW;

  if (leftOnLine && rightOnLine) {
    motorLeft(true, SPEED); motorRight(true, SPEED);      // düz git
  } else if (leftOnLine && !rightOnLine) {
    motorLeft(false, SPEED); motorRight(true, SPEED);     // sola dön
  } else if (!leftOnLine && rightOnLine) {
    motorLeft(true, SPEED); motorRight(false, SPEED);     // sağa dön
  } else {
    motorLeft(false, 0); motorRight(false, 0);            // dur
  }
}
"""
},

]


# ----------------------------------------------------------------------------
# Uygulama başlangıcı
# ----------------------------------------------------------------------------

init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
