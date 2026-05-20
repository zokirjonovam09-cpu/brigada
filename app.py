import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template_string, request, redirect, session

app = Flask(__name__)
app.secret_key = "brigada_secret_2025"

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:npg_mDRK9IObMF8o@ep-orange-bonus-aqu7b7s7-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    conn = get_db()
    cur = conn.cursor()
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
            mijoz_puli BIGINT DEFAULT 0,
            tugagan BOOLEAN DEFAULT FALSE
        );
        CREATE TABLE IF NOT EXISTS davomat (
            id SERIAL PRIMARY KEY,
            sana VARCHAR(20),
            ishchi_id INTEGER,
            loyiha_id INTEGER,
            holat VARCHAR(10) DEFAULT 'YOQ',
            UNIQUE(sana, ishchi_id, loyiha_id)
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
    # Default rahbar
    cur.execute("INSERT INTO rahbar (login, parol) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                ("Usta Ziynatulloh", "masterHuseyin"))
    # Default ishchilar
    for ism, maosh, parol in [
        ("Muhammad Ali", 160000, "ali2026"),
        ("Muhammad Ziyo", 150000, "ziyobek2711"),
        ("Abdulhodiy", 150000, "bek2007"),
    ]:
        cur.execute("INSERT INTO ishchilar (ism, kunlik_maosh, parol, rol, foiz) VALUES (%s,%s,%s,'ishchi',0) ON CONFLICT DO NOTHING",
                    (ism, maosh, parol))
    conn.commit()
    cur.close()
    conn.close()

try:
    init_db()
except Exception as e:
    print(f"DB init error: {e}")

# ============================================================
# STIL
# ============================================================
STIL = """<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Brigada Tizimi</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: Arial, sans-serif; background: #f0f0f0; }
  .header { background: #BA7517; color: white; padding: 14px 24px; display: flex; justify-content: space-between; align-items: center; }
  .header a { color: white; text-decoration: none; font-size: 13px; }
  .nav { background: #9e6313; padding: 8px 24px; display: flex; gap: 8px; flex-wrap: wrap; }
  .nav a { color: white; text-decoration: none; font-size: 13px; padding: 5px 12px; border-radius: 4px; }
  .nav a:hover { background: rgba(255,255,255,0.2); }
  .content { padding: 20px; max-width: 960px; }
  .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  .card h2 { margin-bottom: 16px; font-size: 16px; color: #333; }
  table { width: 100%; border-collapse: collapse; }
  th { background: #BA7517; color: white; padding: 10px 12px; text-align: left; font-size: 13px; }
  td { padding: 10px 12px; border-bottom: 1px solid #eee; font-size: 14px; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #fff8f0; }
  .btn { display: inline-block; background: #BA7517; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; font-size: 13px; text-decoration: none; margin: 2px; }
  .btn:hover { background: #9e6313; }
  .btn-red { background: #c0392b; } .btn-red:hover { background: #a93226; }
  .btn-green { background: #27ae60; } .btn-green:hover { background: #219a52; }
  .btn-blue { background: #2980b9; } .btn-blue:hover { background: #2471a3; }
  input, select { padding: 8px 10px; border: 1px solid #ccc; border-radius: 5px; font-size: 13px; width: 100%; margin-bottom: 8px; }
  .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .form-row3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
  .form-row4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 12px; }
  label { font-size: 12px; font-weight: bold; color: #555; display: block; margin-bottom: 3px; }
  .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 16px; }
  .metric { background: white; border-radius: 8px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  .metric-label { font-size: 11px; color: #999; text-transform: uppercase; margin-bottom: 6px; }
  .metric-value { font-size: 20px; font-weight: bold; color: #BA7517; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 99px; font-size: 11px; font-weight: bold; }
  .badge-sherik { background: #e8f5e9; color: #2e7d32; }
  .badge-ishchi { background: #e3f2fd; color: #1565c0; }
  .alert { padding: 12px; border-radius: 5px; margin-bottom: 12px; font-size: 14px; }
  .alert-red { background: #fde8e8; color: #c0392b; }
  .alert-green { background: #e8f5e9; color: #2e7d32; }
  .r1 td { background: #fffde7 !important; }
  .r2 td { background: #f5f5f5 !important; }
  .r3 td { background: #fff5ee !important; }
</style></head><body>"""

def H(s):
    return f'<div class="header"><b>🏗️ Brigada — {s}</b><span>{session.get("login","")} | <a href="/chiqish">Chiqish</a></span></div>'

def NR():
    return '<div class="nav"><a href="/">🏠 Bosh sahifa</a><a href="/ishchilar">👷 Ishchilar</a><a href="/loyihalar">🏗️ Loyihalar</a><a href="/davomat">📅 Davomat</a><a href="/avanslar">💸 Avanslar</a><a href="/xarajatlar">🔧 Xarajatlar</a><a href="/hisobot">📊 Hisobot</a><a href="/reyting">🏆 Reyting</a></div>'

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
                cur.close(); conn.close()
                return redirect("/")
            cur.execute("SELECT * FROM ishchilar WHERE ism=%s AND parol=%s", (l, p))
            ishchi = cur.fetchone()
            cur.close(); conn.close()
            if ishchi:
                session["login"] = l; session["rol"] = ishchi["rol"]; session["ishchi_id"] = ishchi["id"]
                return redirect("/")
        except Exception as e:
            xato = f"Xato: {e}"
        if not xato:
            xato = "Login yoki parol noto'g'ri!"

    return render_template_string(STIL + f"""
    <div style="display:flex;justify-content:center;align-items:center;min-height:100vh;">
      <div style="background:white;padding:40px;border-radius:10px;width:340px;box-shadow:0 4px 12px rgba(0,0,0,0.15);">
        <h2 style="text-align:center;color:#BA7517;margin-bottom:24px;">🏗️ Brigada Tizimi</h2>
        {"<div class='alert alert-red'>"+xato+"</div>" if xato else ""}
        <form method="POST">
          <label>Login (ismingiz)</label><input name="login" placeholder="Ism Familiya">
          <label>Parol</label><input name="parol" type="password" placeholder="Parol">
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
        cur.execute("SELECT COUNT(*) as n FROM ishchilar"); jami_ishchi = cur.fetchone()["n"]
        cur.execute("SELECT COUNT(*) as n FROM loyihalar"); jami_loyiha = cur.fetchone()["n"]
        cur.execute("SELECT nom FROM loyihalar WHERE tugagan=FALSE LIMIT 1")
        faol = cur.fetchone()
        faol_nom = faol["nom"] if faol else "Yo'q"
        cur.close(); conn.close()
        return render_template_string(STIL + H("Dashboard") + NR() + f"""
        <div class="content">
          <div class="metric-grid">
            <div class="metric"><div class="metric-label">Ishchilar</div><div class="metric-value">{jami_ishchi}</div></div>
            <div class="metric"><div class="metric-label">Loyihalar</div><div class="metric-value">{jami_loyiha}</div></div>
            <div class="metric"><div class="metric-label">Faol loyiha</div><div class="metric-value" style="font-size:14px">{faol_nom}</div></div>
          </div>
          <div class="card"><h2>Tezkor havolalar</h2>
            <a class="btn" href="/davomat">📅 Davomat</a>
            <a class="btn" href="/avanslar">💸 Avans</a>
            <a class="btn" href="/hisobot">📊 Hisobot</a>
            <a class="btn btn-green" href="/ishchilar">👷 Ishchilar</a>
          </div>
        </div></body></html>""")
    elif rol == "sherik": return redirect("/sherik_hisobi")
    else: return redirect("/mening_hisobim")

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
            cur.execute("INSERT INTO ishchilar (ism, kunlik_maosh, parol, rol, foiz) VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                (request.form.get("ism","").strip(), int(request.form.get("maosh",0)),
                 request.form.get("parol","").strip(), request.form.get("rol","ishchi"),
                 float(request.form.get("foiz",0))))
            xabar = f"✅ {request.form.get('ism')} qo'shildi!"
        elif amal == "tahrirlash":
            cur.execute("UPDATE ishchilar SET kunlik_maosh=%s, parol=%s, rol=%s, foiz=%s WHERE id=%s",
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
        foiz_text = f"{i['foiz']}%" if i["rol"] == "sherik" else "—"
        qatorlar += f"""<tr>
          <td>{i['ism']}</td><td>{i['kunlik_maosh']:,} so'm</td>
          <td><span class="badge badge-{i['rol']}">{i['rol']}</span></td>
          <td>{foiz_text}</td>
          <td>
            <button class="btn btn-blue" style="font-size:11px;padding:4px 8px"
              onclick="tahr({i['id']},'{i['ism']}',{i['kunlik_maosh']},'{i['rol']}',{i['foiz']},'{i['parol']}')">✏️</button>
            <form method="POST" style="display:inline" onsubmit="return confirm('O\\'chirasizmi?')">
              <input type="hidden" name="amal" value="ochirish">
              <input type="hidden" name="ishchi_id" value="{i['id']}">
              <button class="btn btn-red" style="font-size:11px;padding:4px 8px">🗑️</button>
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
    if request.method == "POST":
        amal = request.form.get("amal")
        if amal == "qoshish":
            cur.execute("INSERT INTO loyihalar (nom,manzil,boshlanish,tugash,mijoz_puli,tugagan) VALUES (%s,%s,%s,%s,%s,FALSE)",
                (request.form.get("nom"), request.form.get("manzil"),
                 request.form.get("boshlanish"), request.form.get("tugash"),
                 int(request.form.get("mijoz_puli",0))))
        elif amal == "tugash":
            cur.execute("UPDATE loyihalar SET tugagan=TRUE WHERE id=%s", (int(request.form.get("loyiha_id")),))
        conn.commit(); cur.close(); conn.close()
        return redirect("/loyihalar")

    cur.execute("SELECT * FROM loyihalar ORDER BY id DESC")
    loyihalar = cur.fetchall()
    cur.close(); conn.close()

    qatorlar = ""
    for l in loyihalar:
        holat = "✅ Tugagan" if l["tugagan"] else "🔄 Davom etmoqda"
        btn = "" if l["tugagan"] else f'<form method="POST" style="display:inline"><input type="hidden" name="amal" value="tugash"><input type="hidden" name="loyiha_id" value="{l["id"]}"><button class="btn btn-red" style="font-size:11px;padding:4px 8px">✅ Tugatish</button></form>'
        qatorlar += f"<tr><td>{l['nom']}</td><td>{l['manzil']}</td><td>{l['mijoz_puli']:,} so'm</td><td>{l['boshlanish'] or ''}</td><td>{holat}</td><td>{btn}</td></tr>"

    return render_template_string(STIL + H("Loyihalar") + NR() + f"""
    <div class="content">
      <div class="card"><h2>➕ Yangi loyiha</h2>
        <form method="POST"><input type="hidden" name="amal" value="qoshish">
          <div class="form-row"><div><label>Nom</label><input name="nom" required></div><div><label>Manzil</label><input name="manzil"></div></div>
          <div class="form-row3"><div><label>Boshlanish</label><input name="boshlanish" type="date"></div><div><label>Tugash</label><input name="tugash" type="date"></div><div><label>Mijoz puli (so'm)</label><input name="mijoz_puli" type="number"></div></div>
          <button class="btn" type="submit">➕ Qo'shish</button>
        </form>
      </div>
      <div class="card"><h2>🏗️ Loyihalar</h2>
        <table><tr><th>Nom</th><th>Manzil</th><th>Mijoz puli</th><th>Boshlanish</th><th>Holat</th><th>Amal</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='6' style='text-align:center;color:#999'>Hali loyiha yo'q</td></tr>"}
        </table>
      </div>
    </div></body></html>""")

# ============================================================
# DAVOMAT
# ============================================================
@app.route("/davomat", methods=["GET", "POST"])
def davomat_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    conn = get_db(); cur = conn.cursor()
    if request.method == "POST":
        sana = request.form.get("sana")
        loyiha_id = int(request.form.get("loyiha_id"))
        cur.execute("SELECT * FROM ishchilar ORDER BY id")
        ishchilar = cur.fetchall()
        for i in ishchilar:
            holat = request.form.get(f"h_{i['id']}", "YOQ")
            cur.execute("""INSERT INTO davomat (sana, ishchi_id, loyiha_id, holat)
                VALUES (%s,%s,%s,%s) ON CONFLICT (sana,ishchi_id,loyiha_id)
                DO UPDATE SET holat=%s""", (sana, i["id"], loyiha_id, holat, holat))
        conn.commit(); cur.close(); conn.close()
        return redirect("/davomat")

    cur.execute("SELECT * FROM ishchilar ORDER BY id")
    ishchilar = cur.fetchall()
    cur.execute("SELECT * FROM loyihalar WHERE tugagan=FALSE ORDER BY id")
    loyihalar = cur.fetchall()
    cur.close(); conn.close()

    loyiha_opts = "".join([f"<option value='{l['id']}'>{l['nom']}</option>" for l in loyihalar])
    ishchi_rows = "".join([f"<tr><td>{i['ism']} <span class='badge badge-{i['rol']}'>{i['rol']}</span></td><td><select name='h_{i['id']}'><option value='HA'>✅ Keldi</option><option value='YOQ'>❌ Kelmadi</option></select></td></tr>" for i in ishchilar])

    return render_template_string(STIL + H("Davomat") + NR() + f"""
    <div class="content"><div class="card"><h2>📅 Davomat belgilash</h2>
      <form method="POST">
        <div class="form-row">
          <div><label>Sana</label><input name="sana" type="date" required></div>
          <div><label>Loyiha</label><select name="loyiha_id">{loyiha_opts if loyiha_opts else "<option>Loyiha yo'q</option>"}</select></div>
        </div>
        <table><tr><th>Ishchi</th><th>Holat</th></tr>{ishchi_rows}</table>
        <br><button class="btn" type="submit">💾 Saqlash</button>
      </form>
    </div></div></body></html>""")

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
    cur.execute("""SELECT a.*, i.ism, l.nom as loyiha_nom FROM avanslar a
        JOIN ishchilar i ON a.ishchi_id=i.id
        JOIN loyihalar l ON a.loyiha_id=l.id ORDER BY a.id DESC""")
    avanslar = cur.fetchall()
    cur.close(); conn.close()

    jami = sum(a["miqdor"] for a in avanslar)
    i_opts = "".join([f"<option value='{i['id']}'>{i['ism']}</option>" for i in ishchilar])
    l_opts = "".join([f"<option value='{l['id']}'>{l['nom']}</option>" for l in loyihalar])
    qatorlar = "".join([f"<tr><td>{a['sana']}</td><td>{a['ism']}</td><td>{a['loyiha_nom']}</td><td>{a['miqdor']:,} so'm</td></tr>" for a in avanslar])

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
# XARAJATLAR
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
    cur.execute("""SELECT x.*, l.nom as loyiha_nom FROM xarajatlar x
        JOIN loyihalar l ON x.loyiha_id=l.id ORDER BY x.id DESC""")
    xarajatlar = cur.fetchall()
    cur.close(); conn.close()

    jami = sum(x["miqdor"] for x in xarajatlar)
    l_opts = "".join([f"<option value='{l['id']}'>{l['nom']}</option>" for l in loyihalar])
    qatorlar = "".join([f"<tr><td>{x['sana']}</td><td>{x['tavsif']}</td><td>{x['loyiha_nom']}</td><td>{x['miqdor']:,} so'm</td></tr>" for x in xarajatlar])

    return render_template_string(STIL + H("Xarajatlar") + NR() + f"""
    <div class="content">
      <div class="card"><h2>🔧 Xarajat qo'shish</h2>
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
        return render_template_string(STIL + H("Hisobot") + NR() + '<div class="content"><div class="card"><p style="color:#999">Hali loyiha yo\'q.</p><a class="btn" href="/loyihalar">Loyiha qo\'shish</a></div></div></body></html>')

    loyiha_id = int(request.args.get("loyiha_id", loyihalar[0]["id"]))
    loyiha = next((l for l in loyihalar if l["id"]==loyiha_id), loyihalar[0])

    cur.execute("SELECT * FROM ishchilar ORDER BY id")
    ishchilar = cur.fetchall()
    cur.execute("SELECT SUM(miqdor) as s FROM xarajatlar WHERE loyiha_id=%s", (loyiha_id,))
    jami_xarajat = cur.fetchone()["s"] or 0
    cur.close(); conn.close()

    mijoz_puli = loyiha["mijoz_puli"]
    jami_maosh = 0
    ishchi_data = []
    for i in ishchilar:
        conn2 = get_db(); cur2 = conn2.cursor()
        cur2.execute("SELECT COUNT(*) as n FROM davomat WHERE ishchi_id=%s AND loyiha_id=%s AND holat='HA'", (i["id"], loyiha_id))
        kunlar = cur2.fetchone()["n"]
        cur2.execute("SELECT COALESCE(SUM(miqdor),0) as s FROM avanslar WHERE ishchi_id=%s AND loyiha_id=%s", (i["id"], loyiha_id))
        avans = cur2.fetchone()["s"]
        cur2.close(); conn2.close()
        maosh = i["kunlik_maosh"] * kunlar
        jami_maosh += maosh
        ishchi_data.append({"i": i, "kunlar": kunlar, "maosh": maosh, "avans": avans, "qolgan": maosh-avans})

    sof_oldin = mijoz_puli - jami_maosh - jami_xarajat
    jami_sherik = sum(d["i"]["foiz"]/100 * sof_oldin for d in ishchi_data if d["i"]["rol"]=="sherik")
    sof_foyda = sof_oldin - jami_sherik

    l_opts = "".join([f"<option value='{l['id']}' {'selected' if l['id']==loyiha_id else ''}>{l['nom']}</option>" for l in loyihalar])
    qatorlar = ""
    for d in ishchi_data:
        foiz_text = f"{sof_oldin * d['i']['foiz']/100:,.0f}" if d["i"]["rol"]=="sherik" else "—"
        qatorlar += f"<tr><td>{d['i']['ism']} <span class='badge badge-{d['i']['rol']}'>{d['i']['rol']}</span></td><td>{d['kunlar']}</td><td>{d['maosh']:,}</td><td>{d['avans']:,}</td><td>{d['qolgan']:,}</td><td>{foiz_text}</td></tr>"

    foyda_rang = "#27ae60" if sof_foyda >= 0 else "#c0392b"
    return render_template_string(STIL + H("Hisobot") + NR() + f"""
    <div class="content">
      <div class="card"><form method="GET"><select name="loyiha_id" onchange="this.form.submit()" style="max-width:300px">{l_opts}</select></form></div>
      <div class="metric-grid">
        <div class="metric"><div class="metric-label">Mijozdan tushgan</div><div class="metric-value">{mijoz_puli:,}</div></div>
        <div class="metric"><div class="metric-label">Ishchilar maoshi</div><div class="metric-value" style="color:#333">{jami_maosh:,}</div></div>
        <div class="metric"><div class="metric-label">Xarajatlar</div><div class="metric-value" style="color:#c0392b">{jami_xarajat:,}</div></div>
        <div class="metric"><div class="metric-label">Sherik foizi</div><div class="metric-value" style="color:#2980b9">{jami_sherik:,.0f}</div></div>
        <div class="metric"><div class="metric-label">Sizning foydangiz</div><div class="metric-value" style="color:{foyda_rang}">{sof_foyda:,.0f}</div></div>
      </div>
      <div class="card"><h2>👷 Ishchilar hisobi</h2>
        <table><tr><th>Ism</th><th>Kun</th><th>Maosh</th><th>Avans</th><th>Qo'lga oladi</th><th>Foiz ulushi</th></tr>
          {qatorlar}
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
    cur.execute("""SELECT i.ism, i.rol, COUNT(d.id) as kunlar FROM ishchilar i
        LEFT JOIN davomat d ON d.ishchi_id=i.id AND d.holat='HA'
        GROUP BY i.id, i.ism, i.rol ORDER BY kunlar DESC""")
    ishchilar = cur.fetchall()
    cur.close(); conn.close()

    medallar = ["🥇","🥈","🥉"]
    sinflar = ["r1","r2","r3"]
    qatorlar = ""
    for idx, i in enumerate(ishchilar):
        sinf = sinflar[idx] if idx < 3 else ""
        medal = medallar[idx] if idx < 3 else str(idx+1)+"."
        qatorlar += f"<tr class='{sinf}'><td>{medal}</td><td>{i['ism']} <span class='badge badge-{i['rol']}'>{i['rol']}</span></td><td><b>{i['kunlar']} kun</b></td></tr>"

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
        cur2.execute("SELECT COUNT(*) as n FROM davomat WHERE ishchi_id=%s AND loyiha_id=%s AND holat='HA'", (ishchi["id"], l["id"]))
        kunlar = cur2.fetchone()["n"]
        cur2.execute("SELECT COALESCE(SUM(miqdor),0) as s FROM avanslar WHERE ishchi_id=%s AND loyiha_id=%s", (ishchi["id"], l["id"]))
        avans = cur2.fetchone()["s"]
        cur2.close(); conn2.close()
        maosh = ishchi["kunlik_maosh"] * kunlar
        qolgan = maosh - avans; jami_qolgan += qolgan
        qatorlar += f"<tr><td>{l['nom']}</td><td>{kunlar}</td><td>{maosh:,}</td><td>{avans:,}</td><td><b>{qolgan:,}</b></td></tr>"

    conn3 = get_db(); cur3 = conn3.cursor()
    cur3.execute("SELECT COUNT(*) as n FROM davomat WHERE ishchi_id=%s AND holat='HA'", (ishchi["id"],))
    jami_kun = cur3.fetchone()["n"]
    cur3.execute("SELECT COALESCE(SUM(miqdor),0) as s FROM avanslar WHERE ishchi_id=%s", (ishchi["id"],))
    jami_avans = cur3.fetchone()["s"]
    cur3.close(); conn3.close()

    rol = ishchi["rol"]
    nav = NS() if rol=="sherik" else NI()
    return render_template_string(STIL + H("Mening hisobim") + nav + f"""
    <div class="content">
      <div class="metric-grid">
        <div class="metric"><div class="metric-label">Jami kun</div><div class="metric-value">{jami_kun}</div></div>
        <div class="metric"><div class="metric-label">Kunlik maosh</div><div class="metric-value" style="font-size:16px">{ishchi['kunlik_maosh']:,}</div></div>
        <div class="metric"><div class="metric-label">Jami avans</div><div class="metric-value" style="color:#e67e22">{jami_avans:,}</div></div>
        <div class="metric"><div class="metric-label">Qo'lga oladi</div><div class="metric-value" style="color:#27ae60">{jami_qolgan:,}</div></div>
      </div>
      <div class="card"><h2>📋 Loyihalar bo'yicha hisobim</h2>
        <table><tr><th>Loyiha</th><th>Kun</th><th>Maosh</th><th>Avans</th><th>Qo'lga oladi</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='5' style='text-align:center;color:#999'>Hali ma'lumot yo'q</td></tr>"}
          <tr style="background:#fff8f0;font-weight:bold;"><td colspan="4">UMUMIY:</td><td style="color:#27ae60">{jami_qolgan:,} so'm</td></tr>
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
        cur2.execute("""SELECT COALESCE(SUM(i.kunlik_maosh * sub.kunlar),0) as s FROM ishchilar i
            JOIN (SELECT ishchi_id, COUNT(*) as kunlar FROM davomat WHERE loyiha_id=%s AND holat='HA' GROUP BY ishchi_id) sub ON i.id=sub.ishchi_id""", (l["id"],))
        jami_maosh = cur2.fetchone()["s"] or 0
        cur2.close(); conn2.close()
        sof = l["mijoz_puli"] - jami_maosh - jami_xarajat
        daromad = sof * foiz / 100; jami_daromad += daromad
        qatorlar += f"<tr><td>{l['nom']}</td><td>{l['mijoz_puli']:,}</td><td>{jami_maosh:,}</td><td>{jami_xarajat:,}</td><td>{sof:,.0f}</td><td style='color:#2e7d32'><b>{daromad:,.0f}</b></td></tr>"

    return render_template_string(STIL + H("Sherik hisobi") + NS() + f"""
    <div class="content">
      <div class="metric-grid">
        <div class="metric"><div class="metric-label">Foiz ulushim</div><div class="metric-value">{foiz}%</div></div>
        <div class="metric"><div class="metric-label">Jami daromadim</div><div class="metric-value" style="color:#27ae60">{jami_daromad:,.0f}</div></div>
      </div>
      <div class="card"><h2>💰 Loyihalar bo'yicha daromadim ({foiz}%)</h2>
        <table><tr><th>Loyiha</th><th>Mijoz puli</th><th>Maosh</th><th>Xarajat</th><th>Sof foyda</th><th>Mening ulushim</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='6' style='text-align:center;color:#999'>Hali loyiha yo'q</td></tr>"}
          <tr style="background:#e8f5e9;font-weight:bold;"><td colspan="5">JAMI:</td><td style="color:#27ae60">{jami_daromad:,.0f} so'm</td></tr>
        </table>
      </div>
    </div></body></html>""")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8080)
