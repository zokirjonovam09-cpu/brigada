import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template_string, request, redirect, session
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "brigada_secret_2025"

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:npg_mDRK9IObMF8o@ep-orange-bonus-aqu7b7s7-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    conn = get_db(); cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rahbar (
            id SERIAL PRIMARY KEY,
            login VARCHAR(100) UNIQUE,
            parol VARCHAR(100)
        );
        CREATE TABLE IF NOT EXISTS ishchilar (
            id SERIAL PRIMARY KEY,
            ism VARCHAR(100) UNIQUE,
            kunlik_maosh INTEGER DEFAULT 0,
            parol VARCHAR(100),
            rol VARCHAR(20) DEFAULT 'ishchi',
            foiz FLOAT DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS loyihalar (
            id SERIAL PRIMARY KEY,
            nom VARCHAR(200),
            manzil VARCHAR(200),
            boshlanish VARCHAR(20),
            tugash VARCHAR(20),
            tugagan BOOLEAN DEFAULT FALSE
        );
        CREATE TABLE IF NOT EXISTS mijoz_tolovlar (
            id SERIAL PRIMARY KEY,
            loyiha_id INTEGER,
            sana VARCHAR(20),
            kimdan VARCHAR(200),
            miqdor BIGINT DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS davomat (
            id SERIAL PRIMARY KEY,
            sana VARCHAR(20),
            ishchi_id INTEGER,
            loyiha_id INTEGER,
            holat VARCHAR(10) DEFAULT 'YOQ',
            izoh VARCHAR(300) DEFAULT '',
            UNIQUE(sana, ishchi_id, loyiha_id)
        );
        CREATE TABLE IF NOT EXISTS kunlik_xarajatlar (
            id SERIAL PRIMARY KEY,
            sana VARCHAR(20),
            ishchi_id INTEGER,
            loyiha_id INTEGER,
            miqdor BIGINT DEFAULT 0,
            tavsif VARCHAR(200) DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS avanslar (
            id SERIAL PRIMARY KEY,
            sana VARCHAR(20),
            ishchi_id INTEGER,
            loyiha_id INTEGER,
            miqdor BIGINT DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS xarajatlar (
            id SERIAL PRIMARY KEY,
            sana VARCHAR(20),
            tavsif VARCHAR(200),
            loyiha_id INTEGER,
            miqdor BIGINT DEFAULT 0
        );
    """)
    cur.execute("INSERT INTO rahbar (login, parol) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                ("Usta Ziynatulloh", "masterHuseyin"))
    for ism, maosh, parol in [
        ("Muhammad Ali", 160000, "ali2026"),
        ("Muhammad Ziyo", 150000, "ziyobek2711"),
        ("Abdulhodiy", 150000, "bek2007"),
    ]:
        cur.execute("INSERT INTO ishchilar (ism, kunlik_maosh, parol, rol, foiz) VALUES (%s,%s,%s,'ishchi',0) ON CONFLICT DO NOTHING",
                    (ism, maosh, parol))
    conn.commit(); cur.close(); conn.close()

try:
    init_db()
except Exception as e:
    print(f"DB init error: {e}")

HAFTA_KUNLARI = {0:"Dushanba",1:"Seshanba",2:"Chorshanba",3:"Payshanba",4:"Juma",5:"Shanba",6:"Yakshanba"}

def hafta_kuni(sana_str):
    try:
        parts = sana_str.replace(",",".").split(".")
        if len(parts) == 2:
            kun, oy = int(parts[0]), int(parts[1])
            yil = 2025
            d = datetime(yil, oy, kun)
            return HAFTA_KUNLARI[d.weekday()]
    except:
        pass
    return ""

STIL = """<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Brigada Tizimi</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: Arial, sans-serif; background: #f0f0f0; font-size: 14px; }
  .header { background: #BA7517; color: white; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; }
  .header a { color: white; text-decoration: none; font-size: 13px; }
  .nav { background: #9e6313; padding: 6px 20px; display: flex; gap: 4px; flex-wrap: wrap; }
  .nav a { color: white; text-decoration: none; font-size: 12px; padding: 5px 10px; border-radius: 4px; white-space: nowrap; }
  .nav a:hover { background: rgba(255,255,255,0.2); }
  .content { padding: 16px; max-width: 1100px; }
  .card { background: white; border-radius: 8px; padding: 16px; margin-bottom: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  .card h2 { margin-bottom: 14px; font-size: 15px; color: #333; }
  table { width: 100%; border-collapse: collapse; }
  th { background: #BA7517; color: white; padding: 8px 10px; text-align: left; font-size: 12px; white-space: nowrap; }
  td { padding: 8px 10px; border-bottom: 1px solid #eee; font-size: 13px; }
  tr:last-child td { border-bottom: none; }
  .btn { display: inline-block; background: #BA7517; color: white; border: none; padding: 7px 14px; border-radius: 5px; cursor: pointer; font-size: 13px; text-decoration: none; margin: 2px; }
  .btn:hover { background: #9e6313; }
  .btn-red { background: #c0392b; } .btn-red:hover { background: #a93226; }
  .btn-green { background: #27ae60; } .btn-green:hover { background: #219a52; }
  .btn-blue { background: #2980b9; } .btn-blue:hover { background: #2471a3; }
  .btn-sm { padding: 4px 8px; font-size: 11px; }
  input, select, textarea { padding: 7px 10px; border: 1px solid #ccc; border-radius: 5px; font-size: 13px; width: 100%; margin-bottom: 8px; }
  .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .form-row3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
  .form-row4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 12px; }
  label { font-size: 12px; font-weight: bold; color: #555; display: block; margin-bottom: 3px; }
  .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-bottom: 14px; }
  .metric { background: white; border-radius: 8px; padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  .metric-label { font-size: 11px; color: #999; text-transform: uppercase; margin-bottom: 5px; }
  .metric-value { font-size: 18px; font-weight: bold; color: #BA7517; }
  .badge { display: inline-block; padding: 2px 7px; border-radius: 99px; font-size: 11px; font-weight: bold; }
  .badge-sherik { background: #e8f5e9; color: #2e7d32; }
  .badge-ishchi { background: #e3f2fd; color: #1565c0; }
  .alert { padding: 10px 14px; border-radius: 5px; margin-bottom: 12px; font-size: 13px; }
  .alert-red { background: #fde8e8; color: #c0392b; }
  .alert-green { background: #e8f5e9; color: #2e7d32; }
  .r1 td { background: #fffde7 !important; }
  .r2 td { background: #f5f5f5 !important; }
  .r3 td { background: #fff5ee !important; }
  /* Davomat jadval */
  .dav-table { overflow-x: auto; }
  .dav-table table { min-width: 800px; }
  .dav-table th, .dav-table td { padding: 6px 8px; font-size: 12px; text-align: center; }
  .dav-table td:first-child, .dav-table td:nth-child(2) { text-align: left; background: #f9f9f9; }
  .dav-table th:first-child, .dav-table th:nth-child(2) { text-align: left; }
  .dav-ha { color: #27ae60; font-weight: bold; }
  .dav-yoq { color: #c0392b; }
  .dav-yarim { color: #e67e22; font-weight: bold; }
  .jami-row td { background: #fff8f0 !important; font-weight: bold; border-top: 2px solid #BA7517; }
  select.dav-sel { padding: 3px; font-size: 12px; width: auto; margin: 0; }
  input.izoh-inp { padding: 3px; font-size: 11px; width: 100px; margin: 0; }
  input.xarajat-inp { padding: 3px; font-size: 11px; width: 70px; margin: 0; }
</style></head><body>"""

def H(s):
    return f'<div class="header"><b>🏗️ Brigada — {s}</b><span>{session.get("login","")} | <a href="/chiqish">Chiqish</a></span></div>'

def NR():
    return '<div class="nav"><a href="/">🏠 Bosh sahifa</a><a href="/ishchilar">👷 Ishchilar</a><a href="/loyihalar">🏗️ Loyihalar</a><a href="/davomat">📅 Davomat</a><a href="/avanslar">💸 Avanslar</a><a href="/xarajatlar">🔧 Xarajatlar</a><a href="/tolovlar">💰 Mijoz to\'lovlar</a><a href="/hisobot">📊 Hisobot</a><a href="/arxiv">📦 Arxiv</a><a href="/reyting">🏆 Reyting</a><a href="/sozlamalar">⚙️ Sozlamalar</a></div>'

def NI():
    return '<div class="nav"><a href="/mening_hisobim">📋 Hisobim</a><a href="/reyting">🏆 Reyting</a></div>'

def NS():
    return '<div class="nav"><a href="/sherik_hisobi">💰 Daromadim</a><a href="/mening_hisobim">📋 Hisobim</a><a href="/reyting">🏆 Reyting</a></div>'

# ============================================================
# LOGIN
# ============================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    xato = ""
    if request.method == "POST":
        l = request.form.get("login", "").strip()
        p = request.form.get("parol", "").strip()
        try:
            conn = get_db(); cur = conn.cursor()
            cur.execute("SELECT * FROM rahbar WHERE login=%s AND parol=%s", (l, p))
            if cur.fetchone():
                session["login"] = l; session["rol"] = "rahbar"
                cur.close(); conn.close(); return redirect("/")
            cur.execute("SELECT * FROM ishchilar WHERE ism=%s AND parol=%s", (l, p))
            ishchi = cur.fetchone()
            cur.close(); conn.close()
            if ishchi:
                session["login"] = l; session["rol"] = ishchi["rol"]; session["ishchi_id"] = ishchi["id"]
                return redirect("/")
            xato = "Login yoki parol noto'g'ri!"
        except Exception as e:
            xato = f"Xato: {e}"
    return render_template_string(STIL + f"""
    <div style="display:flex;justify-content:center;align-items:center;min-height:100vh;">
      <div style="background:white;padding:36px;border-radius:10px;width:320px;box-shadow:0 4px 12px rgba(0,0,0,0.15);">
        <h2 style="text-align:center;color:#BA7517;margin-bottom:20px;">🏗️ Brigada Tizimi</h2>
        {"<div class='alert alert-red'>"+xato+"</div>" if xato else ""}
        <form method="POST">
          <label>Login</label><input name="login" placeholder="Ismingiz">
          <label>Parol</label><input name="parol" type="password">
          <button class="btn" type="submit" style="width:100%;margin-top:4px;">Kirish</button>
        </form>
      </div>
    </div></body></html>""")

@app.route("/chiqish")
def chiqish():
    session.clear(); return redirect("/login")

# ============================================================
# BOSH SAHIFA
# ============================================================
@app.route("/")
def bosh():
    if "login" not in session: return redirect("/login")
    rol = session.get("rol")
    if rol == "rahbar":
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as n FROM ishchilar"); ji = cur.fetchone()["n"]
        cur.execute("SELECT COUNT(*) as n FROM loyihalar WHERE tugagan=FALSE"); jl = cur.fetchone()["n"]
        cur.execute("SELECT nom FROM loyihalar WHERE tugagan=FALSE ORDER BY id DESC LIMIT 1")
        faol = cur.fetchone(); faol_nom = faol["nom"] if faol else "Yo'q"
        cur.close(); conn.close()
        return render_template_string(STIL + H("Dashboard") + NR() + f"""
        <div class="content">
          <div class="metric-grid">
            <div class="metric"><div class="metric-label">Ishchilar</div><div class="metric-value">{ji}</div></div>
            <div class="metric"><div class="metric-label">Faol loyihalar</div><div class="metric-value">{jl}</div></div>
            <div class="metric"><div class="metric-label">Oxirgi loyiha</div><div class="metric-value" style="font-size:13px">{faol_nom}</div></div>
          </div>
          <div class="card"><h2>Tezkor havolalar</h2>
            <a class="btn" href="/davomat">📅 Davomat</a>
            <a class="btn" href="/avanslar">💸 Avans</a>
            <a class="btn" href="/tolovlar">💰 Mijoz to'lov</a>
            <a class="btn" href="/hisobot">📊 Hisobot</a>
            <a class="btn btn-green" href="/ishchilar">👷 Ishchilar</a>
          </div>
        </div></body></html>""")
    elif rol == "sherik": return redirect("/sherik_hisobi")
    else: return redirect("/mening_hisobim")

# ============================================================
# SOZLAMALAR (login/parol o'zgartirish)
# ============================================================
@app.route("/sozlamalar", methods=["GET", "POST"])
def sozlamalar():
    if session.get("rol") != "rahbar": return redirect("/")
    xabar = ""
    if request.method == "POST":
        yangi_login = request.form.get("login", "").strip()
        yangi_parol = request.form.get("parol", "").strip()
        if yangi_login and yangi_parol:
            conn = get_db(); cur = conn.cursor()
            cur.execute("UPDATE rahbar SET login=%s, parol=%s WHERE login=%s",
                        (yangi_login, yangi_parol, session.get("login")))
            conn.commit(); cur.close(); conn.close()
            session["login"] = yangi_login
            xabar = "✅ Login va parol yangilandi!"
    return render_template_string(STIL + H("Sozlamalar") + NR() + f"""
    <div class="content">
      {"<div class='alert alert-green'>"+xabar+"</div>" if xabar else ""}
      <div class="card"><h2>⚙️ Login va parolni o'zgartirish</h2>
        <form method="POST">
          <div class="form-row">
            <div><label>Yangi login</label><input name="login" value="{session.get('login','')}" required></div>
            <div><label>Yangi parol</label><input name="parol" type="password" placeholder="Yangi parol" required></div>
          </div>
          <button class="btn btn-green" type="submit">💾 Saqlash</button>
        </form>
      </div>
    </div></body></html>""")

# ============================================================
# ISHCHILAR
# ============================================================
@app.route("/ishchilar", methods=["GET", "POST"])
def ishchilar_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    xabar = ""
    conn = get_db(); cur = conn.cursor()
    if request.method == "POST":
        amal = request.form.get("amal")
        if amal == "qoshish":
            cur.execute("INSERT INTO ishchilar (ism,kunlik_maosh,parol,rol,foiz) VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                (request.form.get("ism","").strip(), int(request.form.get("maosh",0)),
                 request.form.get("parol","").strip(), request.form.get("rol","ishchi"),
                 float(request.form.get("foiz",0))))
            xabar = f"✅ {request.form.get('ism')} qo'shildi!"
        elif amal == "tahrirlash":
            cur.execute("UPDATE ishchilar SET kunlik_maosh=%s,parol=%s,rol=%s,foiz=%s WHERE id=%s",
                (int(request.form.get("maosh",0)), request.form.get("parol",""),
                 request.form.get("rol","ishchi"), float(request.form.get("foiz",0)),
                 int(request.form.get("ishchi_id"))))
            xabar = "✅ Yangilandi!"
        elif amal == "ochirish":
            cur.execute("DELETE FROM ishchilar WHERE id=%s", (int(request.form.get("ishchi_id")),))
            xabar = "✅ O'chirildi!"
        conn.commit()
    cur.execute("SELECT * FROM ishchilar ORDER BY id")
    ishchilar = cur.fetchall()
    cur.close(); conn.close()

    qatorlar = ""
    for i in ishchilar:
        foiz_text = f"{i['foiz']}%" if i["rol"]=="sherik" else "—"
        qatorlar += f"""<tr>
          <td>{i['ism']}</td><td>{i['kunlik_maosh']:,} so'm</td>
          <td><span class="badge badge-{i['rol']}">{i['rol']}</span></td>
          <td>{foiz_text}</td>
          <td>
            <button class="btn btn-blue btn-sm" onclick="tahr({i['id']},'{i['ism']}',{i['kunlik_maosh']},'{i['rol']}',{i['foiz']},'{i['parol']}')">✏️</button>
            <form method="POST" style="display:inline" onsubmit="return confirm('O\\'chirasizmi?')">
              <input type="hidden" name="amal" value="ochirish">
              <input type="hidden" name="ishchi_id" value="{i['id']}">
              <button class="btn btn-red btn-sm">🗑️</button>
            </form>
          </td></tr>"""

    return render_template_string(STIL + H("Ishchilar") + NR() + f"""
    <div class="content">
      {"<div class='alert alert-green'>"+xabar+"</div>" if xabar else ""}
      <div class="card"><h2>➕ Yangi ishchi</h2>
        <form method="POST"><input type="hidden" name="amal" value="qoshish">
          <div class="form-row4">
            <div><label>Ism</label><input name="ism" placeholder="Muhammad Ali" required></div>
            <div><label>Kunlik maosh</label><input name="maosh" type="number" placeholder="150000" required></div>
            <div><label>Parol</label><input name="parol" placeholder="ali2026" required></div>
            <div><label>Rol</label><select name="rol"><option value="ishchi">👷 Ishchi</option><option value="sherik">🤝 Sherik</option></select></div>
          </div>
          <div class="form-row"><div><label>Foiz % (sherik uchun)</label><input name="foiz" type="number" step="0.1" value="0"></div></div>
          <button class="btn" type="submit">➕ Qo'shish</button>
        </form>
      </div>
      <div class="card" id="tc" style="display:none"><h2>✏️ Tahrirlash</h2>
        <form method="POST"><input type="hidden" name="amal" value="tahrirlash"><input type="hidden" name="ishchi_id" id="ti">
          <div class="form-row4">
            <div><label>Ism</label><input id="tn" disabled style="background:#f5f5f5"></div>
            <div><label>Kunlik maosh</label><input name="maosh" id="tm" type="number"></div>
            <div><label>Parol</label><input name="parol" id="tp"></div>
            <div><label>Rol</label><select name="rol" id="tr"><option value="ishchi">👷 Ishchi</option><option value="sherik">🤝 Sherik</option></select></div>
          </div>
          <div class="form-row"><div><label>Foiz %</label><input name="foiz" id="tf" type="number" step="0.1"></div></div>
          <button class="btn btn-green" type="submit">💾 Saqlash</button>
          <button class="btn btn-red" type="button" onclick="document.getElementById('tc').style.display='none'">Bekor</button>
        </form>
      </div>
      <div class="card"><h2>👷 Ishchilar ro'yxati</h2>
        <table><tr><th>Ism</th><th>Kunlik maosh</th><th>Rol</th><th>Foiz</th><th>Amallar</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='5' style='text-align:center;color:#999'>Hali ishchi yo'q</td></tr>"}
        </table>
      </div>
    </div>
    <script>
    function tahr(id,ism,maosh,rol,foiz,parol){{
      document.getElementById('tc').style.display='block';
      document.getElementById('ti').value=id; document.getElementById('tn').value=ism;
      document.getElementById('tm').value=maosh; document.getElementById('tp').value=parol;
      document.getElementById('tf').value=foiz; document.getElementById('tr').value=rol;
      document.getElementById('tc').scrollIntoView();
    }}
    </script></body></html>""")

# ============================================================
# LOYIHALAR
# ============================================================
@app.route("/loyihalar", methods=["GET", "POST"])
def loyihalar_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    conn = get_db(); cur = conn.cursor()
    xabar = ""
    if request.method == "POST":
        amal = request.form.get("amal")
        if amal == "qoshish":
            cur.execute("INSERT INTO loyihalar (nom,manzil,boshlanish,tugash,tugagan) VALUES (%s,%s,%s,%s,FALSE)",
                (request.form.get("nom"), request.form.get("manzil"),
                 request.form.get("boshlanish"), request.form.get("tugash")))
            xabar = "✅ Loyiha qo'shildi!"
        elif amal == "tahrirlash":
            cur.execute("UPDATE loyihalar SET nom=%s,manzil=%s,boshlanish=%s,tugash=%s WHERE id=%s",
                (request.form.get("nom"), request.form.get("manzil"),
                 request.form.get("boshlanish"), request.form.get("tugash"),
                 int(request.form.get("loyiha_id"))))
            xabar = "✅ Yangilandi!"
        elif amal == "tugash":
            cur.execute("UPDATE loyihalar SET tugagan=TRUE WHERE id=%s", (int(request.form.get("loyiha_id")),))
            xabar = "✅ Loyiha tugatildi!"
        elif amal == "ochirish":
            lid = int(request.form.get("loyiha_id"))
            cur.execute("DELETE FROM davomat WHERE loyiha_id=%s", (lid,))
            cur.execute("DELETE FROM avanslar WHERE loyiha_id=%s", (lid,))
            cur.execute("DELETE FROM xarajatlar WHERE loyiha_id=%s", (lid,))
            cur.execute("DELETE FROM kunlik_xarajatlar WHERE loyiha_id=%s", (lid,))
            cur.execute("DELETE FROM mijoz_tolovlar WHERE loyiha_id=%s", (lid,))
            cur.execute("DELETE FROM loyihalar WHERE id=%s", (lid,))
            xabar = "✅ Loyiha o'chirildi!"
        conn.commit()

    cur.execute("SELECT * FROM loyihalar WHERE tugagan=FALSE ORDER BY id DESC")
    loyihalar = cur.fetchall()
    cur.close(); conn.close()

    qatorlar = ""
    for l in loyihalar:
        qatorlar += f"""<tr>
          <td>{l['nom']}</td><td>{l['manzil'] or ''}</td>
          <td>{l['boshlanish'] or ''}</td><td>{l['tugash'] or ''}</td>
          <td>
            <button class="btn btn-blue btn-sm" onclick="tahr_l({l['id']},'{l['nom']}','{l['manzil'] or ''}','{l['boshlanish'] or ''}','{l['tugash'] or ''}')">✏️</button>
            <form method="POST" style="display:inline">
              <input type="hidden" name="amal" value="tugash">
              <input type="hidden" name="loyiha_id" value="{l['id']}">
              <button class="btn btn-green btn-sm">✅ Tugatish</button>
            </form>
            <form method="POST" style="display:inline" onsubmit="return confirm('O\\'chirasizmi? Barcha ma\\'lumotlar o\\'chadi!')">
              <input type="hidden" name="amal" value="ochirish">
              <input type="hidden" name="loyiha_id" value="{l['id']}">
              <button class="btn btn-red btn-sm">🗑️</button>
            </form>
          </td></tr>"""

    return render_template_string(STIL + H("Loyihalar") + NR() + f"""
    <div class="content">
      {"<div class='alert alert-green'>"+xabar+"</div>" if xabar else ""}
      <div class="card"><h2>➕ Yangi loyiha</h2>
        <form method="POST"><input type="hidden" name="amal" value="qoshish">
          <div class="form-row"><div><label>Loyiha nomi</label><input name="nom" required></div><div><label>Manzil</label><input name="manzil"></div></div>
          <div class="form-row"><div><label>Boshlanish</label><input name="boshlanish" type="date"></div><div><label>Tugash</label><input name="tugash" type="date"></div></div>
          <button class="btn" type="submit">➕ Qo'shish</button>
        </form>
      </div>
      <div class="card" id="tl" style="display:none"><h2>✏️ Loyihani tahrirlash</h2>
        <form method="POST"><input type="hidden" name="amal" value="tahrirlash"><input type="hidden" name="loyiha_id" id="tl-id">
          <div class="form-row"><div><label>Nom</label><input name="nom" id="tl-nom"></div><div><label>Manzil</label><input name="manzil" id="tl-manzil"></div></div>
          <div class="form-row"><div><label>Boshlanish</label><input name="boshlanish" id="tl-bosh" type="date"></div><div><label>Tugash</label><input name="tugash" id="tl-tug" type="date"></div></div>
          <button class="btn btn-green" type="submit">💾 Saqlash</button>
          <button class="btn btn-red" type="button" onclick="document.getElementById('tl').style.display='none'">Bekor</button>
        </form>
      </div>
      <div class="card"><h2>🏗️ Faol loyihalar</h2>
        <table><tr><th>Nom</th><th>Manzil</th><th>Boshlanish</th><th>Tugash</th><th>Amallar</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='5' style='text-align:center;color:#999'>Hali loyiha yo'q</td></tr>"}
        </table>
      </div>
    </div>
    <script>
    function tahr_l(id,nom,manzil,bosh,tug){{
      document.getElementById('tl').style.display='block';
      document.getElementById('tl-id').value=id;
      document.getElementById('tl-nom').value=nom;
      document.getElementById('tl-manzil').value=manzil;
      document.getElementById('tl-bosh').value=bosh;
      document.getElementById('tl-tug').value=tug;
      document.getElementById('tl').scrollIntoView();
    }}
    </script></body></html>""")

# ============================================================
# DAVOMAT - JADVAL KO'RINISHI
# ============================================================
@app.route("/davomat", methods=["GET", "POST"])
def davomat_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    conn = get_db(); cur = conn.cursor()

    if request.method == "POST":
        loyiha_id = int(request.form.get("loyiha_id", 0))
        sana = request.form.get("sana", "")
        cur.execute("SELECT * FROM ishchilar ORDER BY id")
        ishchilar = cur.fetchall()
        for i in ishchilar:
            holat = request.form.get(f"h_{i['id']}", "YOQ")
            izoh = request.form.get(f"iz_{i['id']}", "")
            xarajat = request.form.get(f"x_{i['id']}", "0") or "0"
            xarajat_tavsif = request.form.get(f"xt_{i['id']}", "")
            cur.execute("""INSERT INTO davomat (sana,ishchi_id,loyiha_id,holat,izoh)
                VALUES (%s,%s,%s,%s,%s) ON CONFLICT (sana,ishchi_id,loyiha_id)
                DO UPDATE SET holat=%s, izoh=%s""",
                (sana, i["id"], loyiha_id, holat, izoh, holat, izoh))
            if int(xarajat) > 0:
                cur.execute("""INSERT INTO kunlik_xarajatlar (sana,ishchi_id,loyiha_id,miqdor,tavsif)
                    VALUES (%s,%s,%s,%s,%s)""",
                    (sana, i["id"], loyiha_id, int(xarajat), xarajat_tavsif))
        conn.commit()

    cur.execute("SELECT * FROM loyihalar WHERE tugagan=FALSE ORDER BY id DESC")
    loyihalar = cur.fetchall()
    cur.execute("SELECT * FROM ishchilar ORDER BY id")
    ishchilar = cur.fetchall()
    cur.close(); conn.close()

    loyiha_id = int(request.args.get("loyiha_id", loyihalar[0]["id"] if loyihalar else 0))
    loyiha_opts = "".join([f"<option value='{l['id']}' {'selected' if l['id']==loyiha_id else ''}>{l['nom']}</option>" for l in loyihalar])

    # Barcha sanalarni olish
    conn2 = get_db(); cur2 = conn2.cursor()
    cur2.execute("SELECT DISTINCT sana FROM davomat WHERE loyiha_id=%s ORDER BY SPLIT_PART(sana, ',', 2)::int, SPLIT_PART(sana, ',', 1)::int", (loyiha_id,))
    sanalar = [r["sana"] for r in cur2.fetchall()]

    # Davomat ma'lumotlarini olish
    cur2.execute("SELECT * FROM davomat WHERE loyiha_id=%s", (loyiha_id,))
    dav_rows = cur2.fetchall()
    dav_map = {(d["sana"], d["ishchi_id"]): d for d in dav_rows}

    # Kunlik xarajatlar
    cur2.execute("SELECT * FROM kunlik_xarajatlar WHERE loyiha_id=%s", (loyiha_id,))
    xar_rows = cur2.fetchall()
    xar_map = {}
    for x in xar_rows:
        key = (x["sana"], x["ishchi_id"])
        xar_map[key] = xar_map.get(key, 0) + x["miqdor"]

    cur2.close(); conn2.close()

    # Jadval sarlavhasi
    ishchi_headers = "".join([f"<th>{i['ism']}<br><small>{i['kunlik_maosh']:,}</small></th>" for i in ishchilar])

    # Jadval qatorlari - inline tahrirlash bilan
    jadval_qatorlar = ""
    for sana in sanalar:
        hk = hafta_kuni(sana)
        qator = f"<td><b>{sana}</b></td><td>{hk}</td>"
        for i in ishchilar:
            d = dav_map.get((sana, i["id"]))
            holat = d["holat"] if d else "YOQ"
            izoh = d["izoh"] if d else ""
            xarajat = xar_map.get((sana, i["id"]), 0)
            if holat == "HA": rang = "#27ae60"; belgi = "+"
            elif holat == "0.5": rang = "#e67e22"; belgi = "0.5"
            else: rang = "#c0392b"; belgi = "-"
            xar_text = f"<br><small style='color:#c0392b'>{xarajat:,}</small>" if xarajat > 0 else ""
            izoh_text = f"<br><small style='color:#888'>{izoh}</small>" if izoh else ""
            onclick_str = "tahrir_och('%s', %d, '%s', '%s', %d)" % (sana, i['id'], holat, izoh, xarajat)
            qator += f"<td style='cursor:pointer' onclick='{onclick_str}'><span style='color:{rang};font-weight:bold'>{belgi}</span>{xar_text}{izoh_text}</td>" 
        jadval_qatorlar += f"<tr>{qator}</tr>"

    # Jami hisob
    jami_row = "<td colspan='2'><b>JAMI</b></td>"
    for i in ishchilar:
        jami_kun = sum(
            (1 if dav_map.get((s, i["id"]), {}).get("holat") == "HA" else
             0.5 if dav_map.get((s, i["id"]), {}).get("holat") == "0.5" else 0)
            for s in sanalar
        )
        jami_maosh = jami_kun * i["kunlik_maosh"]
        jami_xarajat = sum(xar_map.get((s, i["id"]), 0) for s in sanalar)
        jami_row += f"<td colspan='2'><b>{jami_kun} kun</b><br>{jami_maosh:,} so'm<br><small style='color:#c0392b'>-{jami_xarajat:,}</small></td>"

    # Yangi kun qo'shish formasi
    ishchi_inputs = ""
    for i in ishchilar:
        ishchi_inputs += f"""
        <tr>
          <td colspan="2"><b>{i['ism']}</b></td>
          <td>
            <select name="h_{i['id']}" class="dav-sel">
              <option value="HA">+ Keldi</option>
              <option value="YOQ">- Kelmadi</option>
              <option value="0.5">0.5 Yarim</option>
            </select>
          </td>
          <td><input class="izoh-inp" name="iz_{i['id']}" placeholder="Izoh"></td>
          <td><input class="xarajat-inp" name="x_{i['id']}" type="number" placeholder="Xarajat" value="0"></td>
          <td><input class="izoh-inp" name="xt_{i['id']}" placeholder="Xarajat tavsifi"></td>
        </tr>"""

    return render_template_string(STIL + H("Davomat") + NR() + f"""
    <div class="content">
      <div class="card">
        <div class="form-row" style="margin-bottom:12px">
          <div>
            <label>Loyiha</label>
            <select onchange="window.location='/davomat?loyiha_id='+this.value">{loyiha_opts}</select>
          </div>
        </div>

        <h2>➕ Kun qo'shish</h2>
        <form method="POST">
          <input type="hidden" name="loyiha_id" value="{loyiha_id}">
          <div class="form-row" style="margin-bottom:8px">
            <div><label>Sana</label><input name="sana" placeholder="25,04" required></div>
          </div>
          <table>
            <tr><th>Ishchi</th><th></th><th>Holat</th><th>Izoh</th><th>Shaxsiy xarajat</th><th>Xarajat tavsifi</th></tr>
            {ishchi_inputs}
          </table>
          <br><button class="btn" type="submit">💾 Saqlash</button>
        </form>
      </div>

      <div class="card">
        <h2>📅 Davomat jadvali <small style="font-weight:normal;color:#999">(katakni bosib tahrirlang)</small></h2>
        <div class="dav-table">
          <table>
            <tr>
              <th>Sana</th><th>Kun</th>
              {ishchi_headers}
            </tr>
            {jadval_qatorlar if jadval_qatorlar else "<tr><td colspan='20' style='text-align:center;color:#999'>Hali davomat kiritilmagan</td></tr>"}
            <tr class="jami-row">
              {jami_row}
            </tr>
          </table>
        </div>
      </div>
    </div>

    <!-- Tahrirlash modali -->
    <div id="modal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:1000">
      <div style="background:white;border-radius:10px;padding:24px;max-width:400px;margin:100px auto;position:relative">
        <h3 style="margin-bottom:16px;color:#BA7517">✏️ Davomat tahrirlash</h3>
        <form method="POST" id="tahrir-form">
          <input type="hidden" name="loyiha_id" value="{loyiha_id}">
          <input type="hidden" name="sana" id="m-sana">
          <input type="hidden" name="ishchi_id" id="m-ishchi">
          <label>Holat</label>
          <select name="holat" id="m-holat" style="margin-bottom:12px">
            <option value="HA">✅ + Keldi</option>
            <option value="YOQ">❌ - Kelmadi</option>
            <option value="0.5">🌗 0.5 Yarim kun</option>
          </select>
          <label>Izoh</label>
          <input name="izoh" id="m-izoh" placeholder="Izoh..." style="margin-bottom:12px">
          <label>Shaxsiy xarajat (so'm)</label>
          <input name="xarajat" id="m-xarajat" type="number" value="0" style="margin-bottom:16px">
          <div style="display:flex;gap:8px">
            <button class="btn btn-green" type="submit">💾 Saqlash</button>
            <button class="btn btn-red" type="button" onclick="document.getElementById('modal').style.display='none'">Bekor</button>
          </div>
        </form>
      </div>
    </div>

    <script>
    function tahrir_och(sana, ishchi_id, holat, izoh, xarajat) {{
      document.getElementById('modal').style.display = 'block';
      document.getElementById('m-sana').value = sana;
      document.getElementById('m-ishchi').value = ishchi_id;
      document.getElementById('m-holat').value = holat;
      document.getElementById('m-izoh').value = izoh;
      document.getElementById('m-xarajat').value = xarajat;
      document.getElementById('tahrir-form').onsubmit = function(e) {{
        e.preventDefault();
        var fd = new FormData(this);
        fd.append('tahrir_mode', '1');
        fetch('/davomat', {{method:'POST', body:fd}}).then(function() {{
          window.location.reload();
        }});
      }};
    }}
    </script>
    </body></html>""")

# ============================================================
# AVANSLAR
# ============================================================
@app.route("/avanslar", methods=["GET", "POST"])
def avanslar_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    conn = get_db(); cur = conn.cursor()
    if request.method == "POST":
        cur.execute("INSERT INTO avanslar (sana,ishchi_id,loyiha_id,miqdor) VALUES (%s,%s,%s,%s)",
            (request.form.get("sana"), int(request.form.get("ishchi_id")),
             int(request.form.get("loyiha_id")), int(request.form.get("miqdor"))))
        conn.commit(); cur.close(); conn.close()
        return redirect("/avanslar")

    cur.execute("SELECT * FROM ishchilar ORDER BY ism")
    ishchilar = cur.fetchall()
    cur.execute("SELECT * FROM loyihalar ORDER BY id DESC")
    loyihalar = cur.fetchall()
    cur.execute("""SELECT a.*, i.ism, l.nom as lnom FROM avanslar a
        JOIN ishchilar i ON a.ishchi_id=i.id
        JOIN loyihalar l ON a.loyiha_id=l.id ORDER BY a.id DESC""")
    avanslar = cur.fetchall()
    cur.close(); conn.close()

    jami = sum(a["miqdor"] for a in avanslar)
    i_opts = "".join([f"<option value='{i['id']}'>{i['ism']}</option>" for i in ishchilar])
    l_opts = "".join([f"<option value='{l['id']}'>{l['nom']}</option>" for l in loyihalar])
    qatorlar = "".join([f"<tr><td>{a['sana']}</td><td>{a['ism']}</td><td>{a['lnom']}</td><td>{a['miqdor']:,} so'm</td></tr>" for a in avanslar])

    return render_template_string(STIL + H("Avanslar") + NR() + f"""
    <div class="content">
      <div class="card"><h2>💸 Avans berish</h2>
        <form method="POST">
          <div class="form-row"><div><label>Sana</label><input name="sana" type="date" required></div><div><label>Ishchi</label><select name="ishchi_id">{i_opts}</select></div></div>
          <div class="form-row"><div><label>Loyiha</label><select name="loyiha_id">{l_opts}</select></div><div><label>Miqdor (so'm)</label><input name="miqdor" type="number" required></div></div>
          <button class="btn" type="submit">💾 Saqlash</button>
        </form>
      </div>
      <div class="card"><h2>Avanslar tarixi &nbsp;<span style="color:#BA7517">Jami: {jami:,} so'm</span></h2>
        <table><tr><th>Sana</th><th>Ishchi</th><th>Loyiha</th><th>Miqdor</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='4' style='text-align:center;color:#999'>Hali avans yo'q</td></tr>"}
        </table>
      </div>
    </div></body></html>""")

# ============================================================
# XARAJATLAR (umumiy, loyiha xarajatlari)
# ============================================================
@app.route("/xarajatlar", methods=["GET", "POST"])
def xarajatlar_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    conn = get_db(); cur = conn.cursor()
    if request.method == "POST":
        cur.execute("INSERT INTO xarajatlar (sana,tavsif,loyiha_id,miqdor) VALUES (%s,%s,%s,%s)",
            (request.form.get("sana"), request.form.get("tavsif"),
             int(request.form.get("loyiha_id")), int(request.form.get("miqdor"))))
        conn.commit(); cur.close(); conn.close()
        return redirect("/xarajatlar")

    cur.execute("SELECT * FROM loyihalar ORDER BY id DESC")
    loyihalar = cur.fetchall()
    cur.execute("""SELECT x.*, l.nom as lnom FROM xarajatlar x
        JOIN loyihalar l ON x.loyiha_id=l.id ORDER BY x.id DESC""")
    xarajatlar = cur.fetchall()
    cur.close(); conn.close()

    jami = sum(x["miqdor"] for x in xarajatlar)
    l_opts = "".join([f"<option value='{l['id']}'>{l['nom']}</option>" for l in loyihalar])
    qatorlar = "".join([f"<tr><td>{x['sana']}</td><td>{x['tavsif']}</td><td>{x['lnom']}</td><td>{x['miqdor']:,} so'm</td></tr>" for x in xarajatlar])

    return render_template_string(STIL + H("Xarajatlar") + NR() + f"""
    <div class="content">
      <div class="card"><h2>🔧 Loyiha xarajati qo'shish</h2>
        <form method="POST">
          <div class="form-row"><div><label>Sana</label><input name="sana" type="date" required></div><div><label>Tavsif</label><input name="tavsif" placeholder="Transport, asbob..." required></div></div>
          <div class="form-row"><div><label>Loyiha</label><select name="loyiha_id">{l_opts}</select></div><div><label>Miqdor (so'm)</label><input name="miqdor" type="number" required></div></div>
          <button class="btn" type="submit">💾 Saqlash</button>
        </form>
      </div>
      <div class="card"><h2>Xarajatlar &nbsp;<span style="color:#c0392b">Jami: {jami:,} so'm</span></h2>
        <table><tr><th>Sana</th><th>Tavsif</th><th>Loyiha</th><th>Miqdor</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='4' style='text-align:center;color:#999'>Hali xarajat yo'q</td></tr>"}
        </table>
      </div>
    </div></body></html>""")

# ============================================================
# MIJOZ TO'LOVLARI
# ============================================================
@app.route("/tolovlar", methods=["GET", "POST"])
def tolovlar_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    conn = get_db(); cur = conn.cursor()
    if request.method == "POST":
        cur.execute("INSERT INTO mijoz_tolovlar (loyiha_id,sana,kimdan,miqdor) VALUES (%s,%s,%s,%s)",
            (int(request.form.get("loyiha_id")), request.form.get("sana"),
             request.form.get("kimdan"), int(request.form.get("miqdor"))))
        conn.commit(); cur.close(); conn.close()
        return redirect("/tolovlar")

    cur.execute("SELECT * FROM loyihalar ORDER BY id DESC")
    loyihalar = cur.fetchall()
    cur.execute("""SELECT t.*, l.nom as lnom FROM mijoz_tolovlar t
        JOIN loyihalar l ON t.loyiha_id=l.id ORDER BY t.id DESC""")
    tolovlar = cur.fetchall()
    cur.close(); conn.close()

    jami = sum(t["miqdor"] for t in tolovlar)
    l_opts = "".join([f"<option value='{l['id']}'>{l['nom']}</option>" for l in loyihalar])
    qatorlar = "".join([f"<tr><td>{t['sana']}</td><td>{t['kimdan']}</td><td>{t['lnom']}</td><td>{t['miqdor']:,} so'm</td></tr>" for t in tolovlar])

    return render_template_string(STIL + H("Mijoz to'lovlar") + NR() + f"""
    <div class="content">
      <div class="card"><h2>💰 Mijozdan to'lov kiritish</h2>
        <form method="POST">
          <div class="form-row"><div><label>Sana</label><input name="sana" type="date" required></div><div><label>Kimdan (ism)</label><input name="kimdan" placeholder="Toshmatov" required></div></div>
          <div class="form-row"><div><label>Loyiha</label><select name="loyiha_id">{l_opts}</select></div><div><label>Miqdor (so'm)</label><input name="miqdor" type="number" required></div></div>
          <button class="btn" type="submit">💾 Saqlash</button>
        </form>
      </div>
      <div class="card"><h2>To'lovlar tarixi &nbsp;<span style="color:#27ae60">Jami: {jami:,} so'm</span></h2>
        <table><tr><th>Sana</th><th>Kimdan</th><th>Loyiha</th><th>Miqdor</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='4' style='text-align:center;color:#999'>Hali to'lov yo'q</td></tr>"}
        </table>
      </div>
    </div></body></html>""")

# ============================================================
# HISOBOT
# ============================================================
@app.route("/hisobot")
def hisobot_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM loyihalar ORDER BY id DESC")
    loyihalar = cur.fetchall()
    if not loyihalar:
        cur.close(); conn.close()
        return render_template_string(STIL + H("Hisobot") + NR() + '<div class="content"><div class="card"><p>Hali loyiha yo\'q.</p><a class="btn" href="/loyihalar">Loyiha qo\'shish</a></div></div></body></html>')

    loyiha_id = int(request.args.get("loyiha_id", loyihalar[0]["id"]))
    loyiha = next((l for l in loyihalar if l["id"]==loyiha_id), loyihalar[0])

    cur.execute("SELECT * FROM ishchilar ORDER BY id")
    ishchilar = cur.fetchall()
    cur.execute("SELECT COALESCE(SUM(miqdor),0) as s FROM xarajatlar WHERE loyiha_id=%s", (loyiha_id,))
    jami_xarajat = cur.fetchone()["s"]
    cur.execute("SELECT COALESCE(SUM(miqdor),0) as s FROM mijoz_tolovlar WHERE loyiha_id=%s", (loyiha_id,))
    jami_tushgan = cur.fetchone()["s"]
    cur.execute("SELECT DISTINCT sana FROM davomat WHERE loyiha_id=%s ORDER BY SPLIT_PART(sana, ',', 2)::int, SPLIT_PART(sana, ',', 1)::int", (loyiha_id,))
    sanalar = [r["sana"] for r in cur.fetchall()]
    cur.execute("SELECT * FROM davomat WHERE loyiha_id=%s", (loyiha_id,))
    dav_rows = cur.fetchall()
    dav_map = {(d["sana"], d["ishchi_id"]): d for d in dav_rows}
    cur.execute("SELECT * FROM kunlik_xarajatlar WHERE loyiha_id=%s", (loyiha_id,))
    xar_rows = cur.fetchall()
    xar_map = {}
    for x in xar_rows:
        key = (x["sana"], x["ishchi_id"])
        xar_map[key] = xar_map.get(key, 0) + x["miqdor"]
    cur.close(); conn.close()

    jami_maosh = 0
    ishchi_data = []
    for i in ishchilar:
        jami_kun = sum(
            (1 if dav_map.get((s, i["id"]), {}).get("holat") == "HA" else
             0.5 if dav_map.get((s, i["id"]), {}).get("holat") == "0.5" else 0)
            for s in sanalar
        )
        conn2 = get_db(); cur2 = conn2.cursor()
        cur2.execute("SELECT COALESCE(SUM(miqdor),0) as s FROM avanslar WHERE ishchi_id=%s AND loyiha_id=%s", (i["id"], loyiha_id))
        avans = cur2.fetchone()["s"]
        cur2.close(); conn2.close()
        jami_shaxsiy_xarajat = sum(xar_map.get((s, i["id"]), 0) for s in sanalar)
        maosh = jami_kun * i["kunlik_maosh"]
        jami_maosh += maosh
        qolgan = maosh - avans - jami_shaxsiy_xarajat
        ishchi_data.append({"i": i, "kun": jami_kun, "maosh": maosh, "avans": avans, "xarajat": jami_shaxsiy_xarajat, "qolgan": qolgan})

    sof_oldin = jami_tushgan - jami_maosh - jami_xarajat
    jami_sherik = sum(d["i"]["foiz"]/100 * sof_oldin for d in ishchi_data if d["i"]["rol"]=="sherik")
    sof_foyda = sof_oldin - jami_sherik

    l_opts = "".join([f"<option value='{l['id']}' {'selected' if l['id']==loyiha_id else ''}>{l['nom']}</option>" for l in loyihalar])

    ishchi_qatorlar = ""
    for d in ishchi_data:
        foiz_text = f"{sof_oldin * d['i']['foiz']/100:,.0f}" if d["i"]["rol"]=="sherik" else "—"
        ishchi_qatorlar += f"""<tr>
          <td>{d['i']['ism']} <span class="badge badge-{d['i']['rol']}">{d['i']['rol']}</span></td>
          <td>{d['kun']}</td><td>{d['maosh']:,}</td><td>{d['avans']:,}</td>
          <td>{d['xarajat']:,}</td><td><b>{d['qolgan']:,}</b></td><td>{foiz_text}</td>
        </tr>"""

    # Davomat jadvali hisobotda
    ishchi_headers = "".join([f"<th>{i['ism']}</th>" for i in ishchilar])
    dav_jadval = ""
    for sana in sanalar:
        hk = hafta_kuni(sana)
        qator = f"<td>{sana}</td><td>{hk}</td>"
        for i in ishchilar:
            d = dav_map.get((sana, i["id"]))
            holat = d["holat"] if d else "YOQ"
            if holat == "HA": t = '<span class="dav-ha">+</span>'
            elif holat == "0.5": t = '<span class="dav-yarim">0.5</span>'
            else: t = '<span class="dav-yoq">-</span>'
            qator += f"<td>{t}</td>"
        dav_jadval += f"<tr>{qator}</tr>"

    foyda_rang = "#27ae60" if sof_foyda >= 0 else "#c0392b"
    return render_template_string(STIL + H("Hisobot") + NR() + f"""
    <div class="content">
      <div class="card">
        <form method="GET"><select name="loyiha_id" onchange="this.form.submit()" style="max-width:300px">{l_opts}</select></form>
      </div>
      <div class="metric-grid">
        <div class="metric"><div class="metric-label">Mijozdan tushgan</div><div class="metric-value" style="color:#27ae60">{jami_tushgan:,}</div></div>
        <div class="metric"><div class="metric-label">Ishchilar maoshi</div><div class="metric-value" style="color:#333">{jami_maosh:,}</div></div>
        <div class="metric"><div class="metric-label">Loyiha xarajati</div><div class="metric-value" style="color:#c0392b">{jami_xarajat:,}</div></div>
        <div class="metric"><div class="metric-label">Sherik foizi</div><div class="metric-value" style="color:#2980b9">{jami_sherik:,.0f}</div></div>
        <div class="metric"><div class="metric-label">Sizning foydangiz</div><div class="metric-value" style="color:{foyda_rang}">{sof_foyda:,.0f}</div></div>
      </div>
      <div class="card"><h2>👷 Ishchilar hisobi</h2>
        <table><tr><th>Ism</th><th>Kun</th><th>Maosh</th><th>Avans</th><th>Shaxsiy xarajat</th><th>Qo'lga oladi</th><th>Foiz ulushi</th></tr>
          {ishchi_qatorlar}
        </table>
      </div>
      <div class="card"><h2>📅 Davomat jadvali</h2>
        <div class="dav-table">
          <table><tr><th>Sana</th><th>Kun</th>{ishchi_headers}</tr>
            {dav_jadval if dav_jadval else "<tr><td colspan='10' style='text-align:center;color:#999'>Hali davomat yo'q</td></tr>"}
          </table>
        </div>
      </div>
    </div></body></html>""")

# ============================================================
# ARXIV
# ============================================================
@app.route("/arxiv")
def arxiv_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM loyihalar WHERE tugagan=TRUE ORDER BY id DESC")
    loyihalar = cur.fetchall()
    cur.close(); conn.close()

    qatorlar = ""
    for l in loyihalar:
        qatorlar += f"""<tr>
          <td>{l['nom']}</td><td>{l['manzil'] or ''}</td>
          <td>{l['boshlanish'] or ''}</td><td>{l['tugash'] or ''}</td>
          <td><a class="btn btn-sm" href="/hisobot?loyiha_id={l['id']}">📊 Hisobot</a></td>
        </tr>"""

    return render_template_string(STIL + H("Arxiv") + NR() + f"""
    <div class="content">
      <div class="card"><h2>📦 Tugagan loyihalar</h2>
        <table><tr><th>Nom</th><th>Manzil</th><th>Boshlanish</th><th>Tugash</th><th>Amal</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='5' style='text-align:center;color:#999'>Hali tugagan loyiha yo'q</td></tr>"}
        </table>
      </div>
    </div></body></html>""")

# ============================================================
# REYTING
# ============================================================
@app.route("/reyting")
def reyting_sahifa():
    if "login" not in session: return redirect("/login")
    conn = get_db(); cur = conn.cursor()
    cur.execute("""SELECT i.ism, i.rol,
        SUM(CASE WHEN d.holat='HA' THEN 1 WHEN d.holat='0.5' THEN 0.5 ELSE 0 END) as kunlar
        FROM ishchilar i LEFT JOIN davomat d ON d.ishchi_id=i.id
        GROUP BY i.id, i.ism, i.rol ORDER BY kunlar DESC""")
    ishchilar = cur.fetchall()
    cur.close(); conn.close()

    medallar = ["🥇","🥈","🥉"]
    sinflar = ["r1","r2","r3"]
    qatorlar = ""
    for idx, i in enumerate(ishchilar):
        sinf = sinflar[idx] if idx < 3 else ""
        medal = medallar[idx] if idx < 3 else str(idx+1)+"."
        kunlar = float(i["kunlar"] or 0)
        qatorlar += f"<tr class='{sinf}'><td>{medal}</td><td>{i['ism']} <span class='badge badge-{i['rol']}'>{i['rol']}</span></td><td><b>{kunlar} kun</b></td></tr>"

    rol = session.get("rol")
    nav = NR() if rol=="rahbar" else (NS() if rol=="sherik" else NI())
    return render_template_string(STIL + H("Reyting") + nav + f"""
    <div class="content"><div class="card"><h2>🏆 Eng ko'p ishlagan ishchilar</h2>
      <table><tr><th>#</th><th>Ism</th><th>Ishlagan kun</th></tr>
        {qatorlar if qatorlar else "<tr><td colspan='3' style='text-align:center;color:#999'>Hali davomat kiritilmagan</td></tr>"}
      </table>
    </div></div></body></html>""")

# ============================================================
# ISHCHI SHAXSIY HISOBI
# ============================================================
@app.route("/mening_hisobim")
def mening_hisobim():
    if "login" not in session: return redirect("/login")
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM ishchilar WHERE ism=%s", (session.get("login"),))
    ishchi = cur.fetchone()
    if not ishchi: cur.close(); conn.close(); return redirect("/")
    cur.execute("SELECT * FROM loyihalar ORDER BY id DESC")
    loyihalar = cur.fetchall()
    cur.close(); conn.close()

    qatorlar = ""; jami_qolgan = 0
    for l in loyihalar:
        conn2 = get_db(); cur2 = conn2.cursor()
        cur2.execute("SELECT * FROM davomat WHERE ishchi_id=%s AND loyiha_id=%s", (ishchi["id"], l["id"]))
        davomatlar = cur2.fetchall()
        jami_kun = sum(1 if d["holat"]=="HA" else 0.5 if d["holat"]=="0.5" else 0 for d in davomatlar)
        cur2.execute("SELECT COALESCE(SUM(miqdor),0) as s FROM avanslar WHERE ishchi_id=%s AND loyiha_id=%s", (ishchi["id"], l["id"]))
        avans = cur2.fetchone()["s"]
        cur2.execute("SELECT COALESCE(SUM(miqdor),0) as s FROM kunlik_xarajatlar WHERE ishchi_id=%s AND loyiha_id=%s", (ishchi["id"], l["id"]))
        shaxsiy_xarajat = cur2.fetchone()["s"]
        cur2.close(); conn2.close()
        maosh = jami_kun * ishchi["kunlik_maosh"]
        qolgan = maosh - avans - shaxsiy_xarajat
        jami_qolgan += qolgan
        qatorlar += f"<tr><td>{l['nom']}</td><td>{jami_kun}</td><td>{maosh:,}</td><td>{avans:,}</td><td>{shaxsiy_xarajat:,}</td><td><b>{qolgan:,}</b></td></tr>"

    conn3 = get_db(); cur3 = conn3.cursor()
    cur3.execute("SELECT * FROM davomat WHERE ishchi_id=%s", (ishchi["id"],))
    all_dav = cur3.fetchall()
    jami_kun_umumiy = sum(1 if d["holat"]=="HA" else 0.5 if d["holat"]=="0.5" else 0 for d in all_dav)
    cur3.execute("SELECT COALESCE(SUM(miqdor),0) as s FROM avanslar WHERE ishchi_id=%s", (ishchi["id"],))
    jami_avans = cur3.fetchone()["s"]
    cur3.close(); conn3.close()

    rol = ishchi["rol"]
    nav = NS() if rol=="sherik" else NI()
    return render_template_string(STIL + H("Mening hisobim") + nav + f"""
    <div class="content">
      <div class="metric-grid">
        <div class="metric"><div class="metric-label">Jami kun</div><div class="metric-value">{jami_kun_umumiy}</div></div>
        <div class="metric"><div class="metric-label">Kunlik maosh</div><div class="metric-value" style="font-size:15px">{ishchi['kunlik_maosh']:,}</div></div>
        <div class="metric"><div class="metric-label">Jami avans</div><div class="metric-value" style="color:#e67e22">{jami_avans:,}</div></div>
        <div class="metric"><div class="metric-label">Qo'lga oladi</div><div class="metric-value" style="color:#27ae60">{jami_qolgan:,}</div></div>
      </div>
      <div class="card"><h2>📋 Loyihalar bo'yicha hisobim</h2>
        <table><tr><th>Loyiha</th><th>Kun</th><th>Maosh</th><th>Avans</th><th>Shaxsiy xarajat</th><th>Qo'lga oladi</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='6' style='text-align:center;color:#999'>Hali ma'lumot yo'q</td></tr>"}
          <tr style="background:#fff8f0;font-weight:bold;"><td colspan="5">UMUMIY:</td><td style="color:#27ae60">{jami_qolgan:,} so'm</td></tr>
        </table>
      </div>
    </div></body></html>""")

# ============================================================
# SHERIK HISOBI
# ============================================================
@app.route("/sherik_hisobi")
def sherik_hisobi():
    if "login" not in session: return redirect("/login")
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM ishchilar WHERE ism=%s", (session.get("login"),))
    ishchi = cur.fetchone()
    if not ishchi or ishchi["rol"] != "sherik":
        cur.close(); conn.close(); return redirect("/mening_hisobim")
    cur.execute("SELECT * FROM loyihalar ORDER BY id DESC")
    loyihalar = cur.fetchall()
    cur.close(); conn.close()

    foiz = ishchi["foiz"]
    qatorlar = ""; jami_daromad = 0
    for l in loyihalar:
        conn2 = get_db(); cur2 = conn2.cursor()
        cur2.execute("SELECT COALESCE(SUM(miqdor),0) as s FROM xarajatlar WHERE loyiha_id=%s", (l["id"],))
        jami_xarajat = cur2.fetchone()["s"]
        cur2.execute("SELECT COALESCE(SUM(miqdor),0) as s FROM mijoz_tolovlar WHERE loyiha_id=%s", (l["id"],))
        jami_tushgan = cur2.fetchone()["s"]
        cur2.execute("SELECT * FROM ishchilar")
        barcha_ishchilar = cur2.fetchall()
        cur2.execute("SELECT * FROM davomat WHERE loyiha_id=%s", (l["id"],))
        davomatlar = cur2.fetchall()
        jami_maosh = sum(
            i["kunlik_maosh"] * sum(1 if d["holat"]=="HA" else 0.5 if d["holat"]=="0.5" else 0
                for d in davomatlar if d["ishchi_id"]==i["id"])
            for i in barcha_ishchilar
        )
        cur2.close(); conn2.close()
        sof = jami_tushgan - jami_maosh - jami_xarajat
        daromad = sof * foiz / 100; jami_daromad += daromad
        qatorlar += f"<tr><td>{l['nom']}</td><td>{jami_tushgan:,}</td><td>{jami_maosh:,}</td><td>{jami_xarajat:,}</td><td>{sof:,.0f}</td><td style='color:#2e7d32'><b>{daromad:,.0f}</b></td></tr>"

    return render_template_string(STIL + H("Sherik hisobi") + NS() + f"""
    <div class="content">
      <div class="metric-grid">
        <div class="metric"><div class="metric-label">Foiz ulushim</div><div class="metric-value">{foiz}%</div></div>
        <div class="metric"><div class="metric-label">Jami daromadim</div><div class="metric-value" style="color:#27ae60">{jami_daromad:,.0f}</div></div>
      </div>
      <div class="card"><h2>💰 Loyihalar bo'yicha daromadim ({foiz}%)</h2>
        <table><tr><th>Loyiha</th><th>Tushgan pul</th><th>Maosh</th><th>Xarajat</th><th>Sof foyda</th><th>Mening ulushim</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='6' style='text-align:center;color:#999'>Hali loyiha yo'q</td></tr>"}
          <tr style="background:#e8f5e9;font-weight:bold;"><td colspan="5">JAMI:</td><td style="color:#27ae60">{jami_daromad:,.0f} so'm</td></tr>
        </table>
      </div>
    </div></body></html>""")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8080)