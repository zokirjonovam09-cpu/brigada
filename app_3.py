from flask import Flask, render_template_string, request, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = "brigada_secret_2025"

# ============================================================
# FOYDALANUVCHILAR
# ============================================================
foydalanuvchilar = {
    "Usta Ziynatulloh": {"parol": "masterHuseyin", "rol": "rahbar"},
    "Muhammad Ali":     {"parol": "ali2026",        "rol": "ishchi"},
    "Abdulhodiy":       {"parol": "bek2007",        "rol": "ishchi"},
    "Muhammad Ziyo":    {"parol": "ziyobek2711",    "rol": "ishchi"},
}

# ============================================================
# MA'LUMOTLAR (fayl orqali saqlanadi)
# ============================================================
FAYL = "malumotlar.json"

def malumot_yuklash():
    if os.path.exists(FAYL):
        with open(FAYL, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "ishchilar": [
            {"id": 1, "ism": "Muhammad Ali",  "kunlik_maosh": 160000},
            {"id": 2, "ism": "Muhammad Ziyo", "kunlik_maosh": 150000},
            {"id": 3, "ism": "Abdulhodiy",    "kunlik_maosh": 150000},
        ],
        "loyihalar": [],
        "avanslar": [],
        "xarajatlar": [],
        "davomat": [],
    }

def malumot_saqlash(data):
    with open(FAYL, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ============================================================
# STIL
# ============================================================
STIL = """
<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Brigada Tizimi</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: Arial, sans-serif; background: #f0f0f0; }
  .header {
    background: #BA7517; color: white;
    padding: 14px 24px;
    display: flex; justify-content: space-between; align-items: center;
  }
  .header a { color: white; text-decoration: none; font-size: 13px; }
  .header a:hover { text-decoration: underline; }
  .nav {
    background: #9e6313; padding: 8px 24px;
    display: flex; gap: 16px; flex-wrap: wrap;
  }
  .nav a {
    color: white; text-decoration: none;
    font-size: 13px; padding: 4px 10px;
    border-radius: 4px;
  }
  .nav a:hover { background: rgba(255,255,255,0.2); }
  .content { padding: 24px; max-width: 900px; }
  .card {
    background: white; border-radius: 8px;
    padding: 20px; margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }
  .card h2 { margin-bottom: 16px; font-size: 16px; color: #333; }
  table { width: 100%; border-collapse: collapse; }
  th {
    background: #BA7517; color: white;
    padding: 10px 12px; text-align: left; font-size: 13px;
  }
  td { padding: 10px 12px; border-bottom: 1px solid #eee; font-size: 14px; }
  tr:hover td { background: #fff8f0; }
  .btn {
    display: inline-block;
    background: #BA7517; color: white;
    border: none; padding: 9px 18px;
    border-radius: 5px; cursor: pointer;
    font-size: 14px; text-decoration: none;
    margin-top: 8px;
  }
  .btn:hover { background: #9e6313; }
  .btn-red { background: #c0392b; }
  .btn-red:hover { background: #a93226; }
  .btn-green { background: #27ae60; }
  input, select {
    padding: 8px 10px; border: 1px solid #ccc;
    border-radius: 5px; font-size: 13px;
    width: 100%; margin-bottom: 10px;
  }
  .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .form-row3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
  label { font-size: 12px; font-weight: bold; color: #555; display: block; margin-bottom: 4px; }
  .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 16px; }
  .metric { background: white; border-radius: 8px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  .metric-label { font-size: 11px; color: #999; text-transform: uppercase; margin-bottom: 6px; }
  .metric-value { font-size: 22px; font-weight: bold; color: #BA7517; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 99px; font-size: 11px; font-weight: bold; }
  .badge-gold { background: #fff3cd; color: #856404; }
  .badge-silver { background: #e2e3e5; color: #383d41; }
  .badge-bronze { background: #ffe8d6; color: #8B4513; }
  .alert { padding: 12px 16px; border-radius: 5px; margin-bottom: 16px; font-size: 14px; }
  .alert-red { background: #fde8e8; color: #c0392b; border: 1px solid #f5bbb7; }
  .reyting-1 { background: #fff9e6; }
  .reyting-2 { background: #f5f5f5; }
  .reyting-3 { background: #fff5ee; }
</style>
</head>
<body>
"""

def nav_rahbar():
    return """
    <div class="nav">
      <a href="/">🏠 Bosh sahifa</a>
      <a href="/ishchilar">👷 Ishchilar</a>
      <a href="/loyihalar">🏗️ Loyihalar</a>
      <a href="/davomat">📅 Davomat</a>
      <a href="/avanslar">💸 Avanslar</a>
      <a href="/xarajatlar">🔧 Xarajatlar</a>
      <a href="/hisobot">📊 Hisobot</a>
      <a href="/reyting">🏆 Reyting</a>
    </div>"""

def nav_ishchi():
    return """
    <div class="nav">
      <a href="/mening_hisobim">📋 Mening hisobim</a>
      <a href="/reyting">🏆 Reyting</a>
    </div>"""

def header(sarlavha):
    login = session.get("login", "")
    return f"""
    <div class="header">
      <b>🏗️ Brigada Tizimi — {sarlavha}</b>
      <span>{login} &nbsp;|&nbsp; <a href="/chiqish">Chiqish</a></span>
    </div>"""

# ============================================================
# LOGIN
# ============================================================
@app.route("/", methods=["GET"])
def bosh():
    if "login" not in session:
        return redirect("/login")
    rol = session.get("rol")
    login = session.get("login")
    data = malumot_yuklash()

    if rol == "rahbar":
        ishchilar = data["ishchilar"]
        loyihalar = data["loyihalar"]
        jami_ishchi = len(ishchilar)
        jami_loyiha = len(loyihalar)
        faol_loyiha = next((l["nom"] for l in loyihalar if not l.get("tugagan")), "Yo'q")

        return render_template_string(STIL + header("Dashboard") + nav_rahbar() + f"""
        <div class="content">
          <div class="metric-grid">
            <div class="metric"><div class="metric-label">Ishchilar</div><div class="metric-value">{jami_ishchi}</div></div>
            <div class="metric"><div class="metric-label">Loyihalar</div><div class="metric-value">{jami_loyiha}</div></div>
            <div class="metric"><div class="metric-label">Faol loyiha</div><div class="metric-value" style="font-size:15px">{faol_loyiha}</div></div>
          </div>
          <div class="card">
            <h2>Tezkor havolalar</h2>
            <a class="btn" href="/davomat">📅 Davomat belgilash</a> &nbsp;
            <a class="btn" href="/avanslar">💸 Avans berish</a> &nbsp;
            <a class="btn" href="/hisobot">📊 Hisobotni ko'rish</a>
          </div>
        </div>
        </body></html>""")
    else:
        return redirect("/mening_hisobim")

@app.route("/login", methods=["GET", "POST"])
def login():
    xato = ""
    if request.method == "POST":
        foydalanuvchi = request.form.get("login", "").strip()
        parol = request.form.get("parol", "").strip()
        if foydalanuvchi in foydalanuvchilar and foydalanuvchilar[foydalanuvchi]["parol"] == parol:
            session["login"] = foydalanuvchi
            session["rol"] = foydalanuvchilar[foydalanuvchi]["rol"]
            return redirect("/")
        else:
            xato = "Login yoki parol noto'g'ri!"

    return render_template_string(STIL + f"""
    <div style="display:flex; justify-content:center; align-items:center; min-height:100vh;">
      <div style="background:white; padding:40px; border-radius:10px; width:340px; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
        <h2 style="text-align:center; color:#BA7517; margin-bottom:24px;">🏗️ Brigada Tizimi</h2>
        {"<div class='alert alert-red'>" + xato + "</div>" if xato else ""}
        <form method="POST">
          <label>Login</label>
          <input name="login" placeholder="Ismingizni kiriting">
          <label>Parol</label>
          <input name="parol" type="password" placeholder="Parolingizni kiriting">
          <button class="btn" type="submit" style="width:100%; margin-top:8px;">Kirish</button>
        </form>
      </div>
    </div>
    </body></html>""")

@app.route("/chiqish")
def chiqish():
    session.clear()
    return redirect("/login")

# ============================================================
# ISHCHILAR
# ============================================================
@app.route("/ishchilar")
def ishchilar_sahifa():
    if session.get("rol") != "rahbar":
        return redirect("/")
    data = malumot_yuklash()
    qatorlar = ""
    for i in data["ishchilar"]:
        qatorlar += f"<tr><td>{i['ism']}</td><td>{i['kunlik_maosh']:,} so'm</td></tr>"

    return render_template_string(STIL + header("Ishchilar") + nav_rahbar() + f"""
    <div class="content">
      <div class="card">
        <h2>👷 Ishchilar ro'yxati</h2>
        <table>
          <tr><th>Ism</th><th>Kunlik maosh</th></tr>
          {qatorlar}
        </table>
      </div>
    </div>
    </body></html>""")

# ============================================================
# LOYIHALAR
# ============================================================
@app.route("/loyihalar", methods=["GET", "POST"])
def loyihalar_sahifa():
    if session.get("rol") != "rahbar":
        return redirect("/")
    data = malumot_yuklash()

    if request.method == "POST":
        yangi = {
            "id": len(data["loyihalar"]) + 1,
            "nom": request.form.get("nom"),
            "manzil": request.form.get("manzil"),
            "boshlanish": request.form.get("boshlanish"),
            "tugash": request.form.get("tugash"),
            "mijoz_puli": int(request.form.get("mijoz_puli", 0)),
            "tugagan": False
        }
        data["loyihalar"].append(yangi)
        malumot_saqlash(data)
        return redirect("/loyihalar")

    qatorlar = ""
    for l in data["loyihalar"]:
        holat = "✅ Tugagan" if l.get("tugagan") else "🔄 Davom etmoqda"
        qatorlar += f"<tr><td>{l['nom']}</td><td>{l['manzil']}</td><td>{l['mijoz_puli']:,} so'm</td><td>{l['boshlanish']}</td><td>{holat}</td></tr>"

    return render_template_string(STIL + header("Loyihalar") + nav_rahbar() + f"""
    <div class="content">
      <div class="card">
        <h2>➕ Yangi loyiha</h2>
        <form method="POST">
          <div class="form-row">
            <div><label>Loyiha nomi</label><input name="nom" placeholder="Toshmatov uyi" required></div>
            <div><label>Manzil</label><input name="manzil" placeholder="Chilonzor"></div>
          </div>
          <div class="form-row3">
            <div><label>Boshlanish</label><input name="boshlanish" type="date"></div>
            <div><label>Tugash</label><input name="tugash" type="date"></div>
            <div><label>Mijozdan tushgan (so'm)</label><input name="mijoz_puli" type="number" placeholder="5000000"></div>
          </div>
          <button class="btn" type="submit">➕ Qo'shish</button>
        </form>
      </div>
      <div class="card">
        <h2>🏗️ Loyihalar ro'yxati</h2>
        <table>
          <tr><th>Nom</th><th>Manzil</th><th>Mijoz puli</th><th>Boshlanish</th><th>Holat</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='5' style='text-align:center;color:#999'>Hali loyiha yo'q</td></tr>"}
        </table>
      </div>
    </div>
    </body></html>""")

# ============================================================
# DAVOMAT
# ============================================================
@app.route("/davomat", methods=["GET", "POST"])
def davomat_sahifa():
    if session.get("rol") != "rahbar":
        return redirect("/")
    data = malumot_yuklash()

    if request.method == "POST":
        sana = request.form.get("sana")
        loyiha_id = int(request.form.get("loyiha_id"))
        for i in data["ishchilar"]:
            holat = request.form.get(f"holat_{i['id']}", "YOQ")
            mavjud = next((d for d in data["davomat"] if d["sana"]==sana and d["ishchi_id"]==i["id"] and d["loyiha_id"]==loyiha_id), None)
            if mavjud:
                mavjud["holat"] = holat
            else:
                data["davomat"].append({"sana": sana, "ishchi_id": i["id"], "loyiha_id": loyiha_id, "holat": holat})
        malumot_saqlash(data)
        return redirect("/davomat")

    loyiha_options = "".join([f"<option value='{l['id']}'>{l['nom']}</option>" for l in data["loyihalar"]])
    ishchi_inputs = ""
    for i in data["ishchilar"]:
        ishchi_inputs += f"""
        <tr>
          <td>{i['ism']}</td>
          <td>
            <select name="holat_{i['id']}">
              <option value="HA">✅ Keldi</option>
              <option value="YOQ">❌ Kelmadi</option>
            </select>
          </td>
        </tr>"""

    return render_template_string(STIL + header("Davomat") + nav_rahbar() + f"""
    <div class="content">
      <div class="card">
        <h2>📅 Davomat belgilash</h2>
        <form method="POST">
          <div class="form-row">
            <div><label>Sana</label><input name="sana" type="date" required></div>
            <div><label>Loyiha</label><select name="loyiha_id">{loyiha_options}</select></div>
          </div>
          <table>
            <tr><th>Ishchi</th><th>Holat</th></tr>
            {ishchi_inputs}
          </table>
          <button class="btn" type="submit">💾 Saqlash</button>
        </form>
      </div>
    </div>
    </body></html>""")

# ============================================================
# AVANSLAR
# ============================================================
@app.route("/avanslar", methods=["GET", "POST"])
def avanslar_sahifa():
    if session.get("rol") != "rahbar":
        return redirect("/")
    data = malumot_yuklash()

    if request.method == "POST":
        data["avanslar"].append({
            "sana": request.form.get("sana"),
            "ishchi_id": int(request.form.get("ishchi_id")),
            "loyiha_id": int(request.form.get("loyiha_id")),
            "miqdor": int(request.form.get("miqdor")),
        })
        malumot_saqlash(data)
        return redirect("/avanslar")

    ishchi_options = "".join([f"<option value='{i['id']}'>{i['ism']}</option>" for i in data["ishchilar"]])
    loyiha_options = "".join([f"<option value='{l['id']}'>{l['nom']}</option>" for l in data["loyihalar"]])

    qatorlar = ""
    for a in reversed(data["avanslar"]):
        ishchi = next((i["ism"] for i in data["ishchilar"] if i["id"]==a["ishchi_id"]), "?")
        loyiha = next((l["nom"] for l in data["loyihalar"] if l["id"]==a["loyiha_id"]), "?")
        qatorlar += f"<tr><td>{a['sana']}</td><td>{ishchi}</td><td>{loyiha}</td><td>{a['miqdor']:,} so'm</td></tr>"

    return render_template_string(STIL + header("Avanslar") + nav_rahbar() + f"""
    <div class="content">
      <div class="card">
        <h2>💸 Avans berish</h2>
        <form method="POST">
          <div class="form-row">
            <div><label>Sana</label><input name="sana" type="date" required></div>
            <div><label>Ishchi</label><select name="ishchi_id">{ishchi_options}</select></div>
          </div>
          <div class="form-row">
            <div><label>Loyiha</label><select name="loyiha_id">{loyiha_options}</select></div>
            <div><label>Miqdor (so'm)</label><input name="miqdor" type="number" placeholder="200000" required></div>
          </div>
          <button class="btn" type="submit">💾 Saqlash</button>
        </form>
      </div>
      <div class="card">
        <h2>Avanslar tarixi</h2>
        <table>
          <tr><th>Sana</th><th>Ishchi</th><th>Loyiha</th><th>Miqdor</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='4' style='text-align:center;color:#999'>Hali avans yo'q</td></tr>"}
        </table>
      </div>
    </div>
    </body></html>""")

# ============================================================
# XARAJATLAR
# ============================================================
@app.route("/xarajatlar", methods=["GET", "POST"])
def xarajatlar_sahifa():
    if session.get("rol") != "rahbar":
        return redirect("/")
    data = malumot_yuklash()

    if request.method == "POST":
        data["xarajatlar"].append({
            "sana": request.form.get("sana"),
            "tavsif": request.form.get("tavsif"),
            "loyiha_id": int(request.form.get("loyiha_id")),
            "miqdor": int(request.form.get("miqdor")),
        })
        malumot_saqlash(data)
        return redirect("/xarajatlar")

    loyiha_options = "".join([f"<option value='{l['id']}'>{l['nom']}</option>" for l in data["loyihalar"]])

    qatorlar = ""
    for x in reversed(data["xarajatlar"]):
        loyiha = next((l["nom"] for l in data["loyihalar"] if l["id"]==x["loyiha_id"]), "?")
        qatorlar += f"<tr><td>{x['sana']}</td><td>{x['tavsif']}</td><td>{loyiha}</td><td>{x['miqdor']:,} so'm</td></tr>"

    return render_template_string(STIL + header("Xarajatlar") + nav_rahbar() + f"""
    <div class="content">
      <div class="card">
        <h2>🔧 Xarajat qo'shish</h2>
        <form method="POST">
          <div class="form-row">
            <div><label>Sana</label><input name="sana" type="date" required></div>
            <div><label>Tavsif</label><input name="tavsif" placeholder="Transport, asbob..." required></div>
          </div>
          <div class="form-row">
            <div><label>Loyiha</label><select name="loyiha_id">{loyiha_options}</select></div>
            <div><label>Miqdor (so'm)</label><input name="miqdor" type="number" placeholder="50000" required></div>
          </div>
          <button class="btn" type="submit">💾 Saqlash</button>
        </form>
      </div>
      <div class="card">
        <h2>Xarajatlar tarixi</h2>
        <table>
          <tr><th>Sana</th><th>Tavsif</th><th>Loyiha</th><th>Miqdor</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='4' style='text-align:center;color:#999'>Hali xarajat yo'q</td></tr>"}
        </table>
      </div>
    </div>
    </body></html>""")

# ============================================================
# HISOBOT
# ============================================================
@app.route("/hisobot")
def hisobot_sahifa():
    if session.get("rol") != "rahbar":
        return redirect("/")
    data = malumot_yuklash()

    loyiha_options = "".join([f"<option value='{l['id']}'>{l['nom']}</option>" for l in data["loyihalar"]])
    loyiha_id = request.args.get("loyiha_id", None)

    if not data["loyihalar"]:
        return render_template_string(STIL + header("Hisobot") + nav_rahbar() + """
        <div class="content"><div class="card">
          <p style="color:#999">Hali loyiha yo'q. Avval loyiha qo'shing.</p>
          <a class="btn" href="/loyihalar">🏗️ Loyiha qo'shish</a>
        </div></div></body></html>""")

    if not loyiha_id:
        loyiha_id = data["loyihalar"][0]["id"]
    loyiha_id = int(loyiha_id)
    loyiha = next((l for l in data["loyihalar"] if l["id"]==loyiha_id), None)

    ishchi_qatorlar = ""
    jami_maosh = 0
    for i in data["ishchilar"]:
        kunlar = len([d for d in data["davomat"] if d["ishchi_id"]==i["id"] and d["loyiha_id"]==loyiha_id and d["holat"]=="HA"])
        maosh = i["kunlik_maosh"] * kunlar
        avans = sum(a["miqdor"] for a in data["avanslar"] if a["ishchi_id"]==i["id"] and a["loyiha_id"]==loyiha_id)
        qolgan = maosh - avans
        jami_maosh += maosh
        ishchi_qatorlar += f"""<tr>
          <td>{i['ism']}</td>
          <td>{kunlar} kun</td>
          <td>{maosh:,} so'm</td>
          <td>{avans:,} so'm</td>
          <td><b>{qolgan:,} so'm</b></td>
        </tr>"""

    jami_xarajat = sum(x["miqdor"] for x in data["xarajatlar"] if x["loyiha_id"]==loyiha_id)
    mijoz_puli = loyiha["mijoz_puli"] if loyiha else 0
    foyda = mijoz_puli - jami_maosh - jami_xarajat
    foyda_rang = "#27ae60" if foyda >= 0 else "#c0392b"

    return render_template_string(STIL + header("Hisobot") + nav_rahbar() + f"""
    <div class="content">
      <div class="card">
        <h2>Loyiha tanlash</h2>
        <form method="GET">
          <select name="loyiha_id" onchange="this.form.submit()">{loyiha_options}</select>
        </form>
      </div>
      <div class="metric-grid">
        <div class="metric"><div class="metric-label">Mijozdan tushgan</div><div class="metric-value">{mijoz_puli:,}</div></div>
        <div class="metric"><div class="metric-label">Umumiy maosh</div><div class="metric-value" style="color:#333">{jami_maosh:,}</div></div>
        <div class="metric"><div class="metric-label">Xarajatlar</div><div class="metric-value" style="color:#c0392b">{jami_xarajat:,}</div></div>
        <div class="metric"><div class="metric-label">Sizning foydangiz</div><div class="metric-value" style="color:{foyda_rang}">{foyda:,}</div></div>
      </div>
      <div class="card">
        <h2>👷 Ishchilar hisobi</h2>
        <table>
          <tr><th>Ism</th><th>Kun</th><th>Jami maosh</th><th>Avans</th><th>Qo'lga oladi</th></tr>
          {ishchi_qatorlar}
        </table>
      </div>
    </div>
    </body></html>""")

# ============================================================
# REYTING
# ============================================================
@app.route("/reyting")
def reyting_sahifa():
    if "login" not in session:
        return redirect("/login")
    data = malumot_yuklash()

    ishchi_kunlar = []
    for i in data["ishchilar"]:
        kunlar = len([d for d in data["davomat"] if d["ishchi_id"]==i["id"] and d["holat"]=="HA"])
        ishchi_kunlar.append({"ism": i["ism"], "kunlar": kunlar})

    ishchi_kunlar.sort(key=lambda x: x["kunlar"], reverse=True)

    qatorlar = ""
    medallar = ["🥇", "🥈", "🥉"]
    sinflar = ["reyting-1", "reyting-2", "reyting-3"]
    for idx, i in enumerate(ishchi_kunlar):
        medal = medallar[idx] if idx < 3 else f"{idx+1}."
        sinf = sinflar[idx] if idx < 3 else ""
        qatorlar += f"<tr class='{sinf}'><td>{medal}</td><td>{i['ism']}</td><td><b>{i['kunlar']} kun</b></td></tr>"

    nav = nav_rahbar() if session.get("rol") == "rahbar" else nav_ishchi()
    return render_template_string(STIL + header("Reyting") + nav + f"""
    <div class="content">
      <div class="card">
        <h2>🏆 Eng ko'p ishlagan ishchilar</h2>
        <table>
          <tr><th>#</th><th>Ism</th><th>Ishlagan kun</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='3' style='text-align:center;color:#999'>Hali davomat kiritilmagan</td></tr>"}
        </table>
      </div>
    </div>
    </body></html>""")

# ============================================================
# ISHCHI SHAXSIY HISOBI
# ============================================================
@app.route("/mening_hisobim")
def mening_hisobim():
    if "login" not in session:
        return redirect("/login")
    login = session.get("login")
    data = malumot_yuklash()

    ishchi = next((i for i in data["ishchilar"] if i["ism"]==login), None)
    if not ishchi:
        return redirect("/")

    hisobot_qatorlar = ""
    jami_qolgan = 0
    for l in data["loyihalar"]:
        kunlar = len([d for d in data["davomat"] if d["ishchi_id"]==ishchi["id"] and d["loyiha_id"]==l["id"] and d["holat"]=="HA"])
        maosh = ishchi["kunlik_maosh"] * kunlar
        avans = sum(a["miqdor"] for a in data["avanslar"] if a["ishchi_id"]==ishchi["id"] and a["loyiha_id"]==l["id"])
        qolgan = maosh - avans
        jami_qolgan += qolgan
        hisobot_qatorlar += f"""<tr>
          <td>{l['nom']}</td>
          <td>{kunlar} kun</td>
          <td>{maosh:,} so'm</td>
          <td>{avans:,} so'm</td>
          <td><b>{qolgan:,} so'm</b></td>
        </tr>"""

    jami_kun = len([d for d in data["davomat"] if d["ishchi_id"]==ishchi["id"] and d["holat"]=="HA"])
    jami_avans = sum(a["miqdor"] for a in data["avanslar"] if a["ishchi_id"]==ishchi["id"])

    return render_template_string(STIL + header("Mening hisobim") + nav_ishchi() + f"""
    <div class="content">
      <div class="metric-grid">
        <div class="metric"><div class="metric-label">Jami ishlagan kun</div><div class="metric-value">{jami_kun}</div></div>
        <div class="metric"><div class="metric-label">Kunlik maosh</div><div class="metric-value" style="font-size:16px">{ishchi['kunlik_maosh']:,}</div></div>
        <div class="metric"><div class="metric-label">Jami avans</div><div class="metric-value" style="color:#e67e22">{jami_avans:,}</div></div>
        <div class="metric"><div class="metric-label">Umumiy qo'lga oladi</div><div class="metric-value" style="color:#27ae60">{jami_qolgan:,}</div></div>
      </div>
      <div class="card">
        <h2>📋 Loyihalar bo'yicha hisobim</h2>
        <table>
          <tr><th>Loyiha</th><th>Kun</th><th>Maosh</th><th>Avans</th><th>Qo'lga oladi</th></tr>
          {hisobot_qatorlar if hisobot_qatorlar else "<tr><td colspan='5' style='text-align:center;color:#999'>Hali ma'lumot yo'q</td></tr>"}
          <tr style="background:#fff8f0; font-weight:bold;">
            <td colspan="4">UMUMIY QO'LGA OLADI:</td>
            <td style="color:#27ae60">{jami_qolgan:,} so'm</td>
          </tr>
        </table>
      </div>
    </div>
    </body></html>""")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8080)
