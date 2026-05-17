from flask import Flask, render_template_string, request, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = "brigada_secret_2025"

FAYL = "malumotlar.json"

def malumot_yuklash():
    if os.path.exists(FAYL):
        with open(FAYL, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "ishchilar": [
            {"id": 1, "ism": "Muhammad Ali",  "kunlik_maosh": 160000, "parol": "ali2026",     "rol": "ishchi", "foiz": 0},
            {"id": 2, "ism": "Muhammad Ziyo", "kunlik_maosh": 150000, "parol": "ziyobek2711", "rol": "ishchi", "foiz": 0},
            {"id": 3, "ism": "Abdulhodiy",    "kunlik_maosh": 150000, "parol": "bek2007",     "rol": "ishchi", "foiz": 0},
        ],
        "rahbar": {"login": "Usta Ziynatulloh", "parol": "masterHuseyin"},
        "loyihalar": [],
        "avanslar": [],
        "xarajatlar": [],
        "davomat": [],
    }

def malumot_saqlash(data):
    with open(FAYL, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
  .nav a { color: white; text-decoration: none; font-size: 13px; padding: 5px 12px; border-radius: 4px; white-space: nowrap; }
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
  .badge-rahbar { background: #fff3e0; color: #e65100; }
  .alert { padding: 12px; border-radius: 5px; margin-bottom: 12px; font-size: 14px; }
  .alert-red { background: #fde8e8; color: #c0392b; border: 1px solid #f5bbb7; }
  .alert-green { background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }
  .reyting-1 td { background: #fffde7 !important; }
  .reyting-2 td { background: #f5f5f5 !important; }
  .reyting-3 td { background: #fff5ee !important; }
</style></head><body>"""

def header(s):
    return f'<div class="header"><b>🏗️ Brigada Tizimi — {s}</b><span>{session.get("login","")} &nbsp;|&nbsp; <a href="/chiqish">Chiqish</a></span></div>'

def nav_rahbar():
    return '<div class="nav"><a href="/">🏠 Bosh sahifa</a><a href="/ishchilar">👷 Ishchilar</a><a href="/loyihalar">🏗️ Loyihalar</a><a href="/davomat">📅 Davomat</a><a href="/avanslar">💸 Avanslar</a><a href="/xarajatlar">🔧 Xarajatlar</a><a href="/hisobot">📊 Hisobot</a><a href="/reyting">🏆 Reyting</a></div>'

def nav_ishchi():
    return '<div class="nav"><a href="/mening_hisobim">📋 Mening hisobim</a><a href="/reyting">🏆 Reyting</a></div>'

def nav_sherik():
    return '<div class="nav"><a href="/sherik_hisobi">💰 Daromadim</a><a href="/mening_hisobim">📋 Ishchi hisobim</a><a href="/reyting">🏆 Reyting</a></div>'

@app.route("/login", methods=["GET", "POST"])
def login():
    xato = ""
    if request.method == "POST":
        l = request.form.get("login", "").strip()
        p = request.form.get("parol", "").strip()
        data = malumot_yuklash()
        if l == data["rahbar"]["login"] and p == data["rahbar"]["parol"]:
            session["login"] = l; session["rol"] = "rahbar"
            return redirect("/")
        ishchi = next((i for i in data["ishchilar"] if i["ism"]==l and i["parol"]==p), None)
        if ishchi:
            session["login"] = l; session["rol"] = ishchi["rol"]; session["ishchi_id"] = ishchi["id"]
            return redirect("/")
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

@app.route("/")
def bosh():
    if "login" not in session: return redirect("/login")
    rol = session.get("rol")
    if rol == "rahbar":
        data = malumot_yuklash()
        faol = next((l["nom"] for l in data["loyihalar"] if not l.get("tugagan")), "Yo'q")
        return render_template_string(STIL + header("Dashboard") + nav_rahbar() + f"""
        <div class="content">
          <div class="metric-grid">
            <div class="metric"><div class="metric-label">Ishchilar</div><div class="metric-value">{len(data["ishchilar"])}</div></div>
            <div class="metric"><div class="metric-label">Loyihalar</div><div class="metric-value">{len(data["loyihalar"])}</div></div>
            <div class="metric"><div class="metric-label">Faol loyiha</div><div class="metric-value" style="font-size:14px">{faol}</div></div>
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

@app.route("/ishchilar", methods=["GET", "POST"])
def ishchilar_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    data = malumot_yuklash()
    xabar = ""
    if request.method == "POST":
        amal = request.form.get("amal")
        if amal == "qoshish":
            yangi_id = max([i["id"] for i in data["ishchilar"]], default=0) + 1
            data["ishchilar"].append({
                "id": yangi_id, "ism": request.form.get("ism","").strip(),
                "kunlik_maosh": int(request.form.get("maosh",0)),
                "parol": request.form.get("parol","").strip(),
                "rol": request.form.get("rol","ishchi"),
                "foiz": float(request.form.get("foiz",0))
            })
            xabar = f"✅ {request.form.get('ism')} qo'shildi!"
        elif amal == "tahrirlash":
            ishchi = next((i for i in data["ishchilar"] if i["id"]==int(request.form.get("ishchi_id"))), None)
            if ishchi:
                ishchi["kunlik_maosh"] = int(request.form.get("maosh", ishchi["kunlik_maosh"]))
                ishchi["parol"] = request.form.get("parol", ishchi["parol"])
                ishchi["rol"] = request.form.get("rol", ishchi["rol"])
                ishchi["foiz"] = float(request.form.get("foiz", ishchi.get("foiz",0)))
                xabar = f"✅ {ishchi['ism']} yangilandi!"
        elif amal == "ochirish":
            data["ishchilar"] = [i for i in data["ishchilar"] if i["id"]!=int(request.form.get("ishchi_id"))]
            xabar = "✅ Ishchi o'chirildi!"
        malumot_saqlash(data); data = malumot_yuklash()

    qatorlar = ""
    for i in data["ishchilar"]:
        foiz_text = f"{i.get('foiz',0)}%" if i.get("rol")=="sherik" else "—"
        qatorlar += f"""<tr>
          <td>{i['ism']}</td><td>{i['kunlik_maosh']:,} so'm</td>
          <td><span class='badge badge-{i["rol"]}'>{i["rol"]}</span></td>
          <td>{foiz_text}</td>
          <td>
            <button class="btn btn-blue" style="font-size:11px;padding:4px 8px"
              onclick="tahrirlash({i['id']},'{i['ism']}',{i['kunlik_maosh']},'{i['rol']}',{i.get('foiz',0)},'{i['parol']}')">✏️</button>
            <form method="POST" style="display:inline" onsubmit="return confirm('O\\'chirishni tasdiqlaysizmi?')">
              <input type="hidden" name="amal" value="ochirish">
              <input type="hidden" name="ishchi_id" value="{i['id']}">
              <button class="btn btn-red" style="font-size:11px;padding:4px 8px" type="submit">🗑️</button>
            </form>
          </td></tr>"""

    return render_template_string(STIL + header("Ishchilar") + nav_rahbar() + f"""
    <div class="content">
      {"<div class='alert alert-green'>"+xabar+"</div>" if xabar else ""}
      <div class="card">
        <h2>➕ Yangi ishchi qo'shish</h2>
        <form method="POST"><input type="hidden" name="amal" value="qoshish">
          <div class="form-row4">
            <div><label>Ism Familiya</label><input name="ism" placeholder="Muhammad Ali" required></div>
            <div><label>Kunlik maosh (so'm)</label><input name="maosh" type="number" placeholder="150000" required></div>
            <div><label>Parol</label><input name="parol" placeholder="ali2026" required></div>
            <div><label>Rol</label><select name="rol"><option value="ishchi">👷 Ishchi</option><option value="sherik">🤝 Sherik</option></select></div>
          </div>
          <div class="form-row">
            <div><label>Foiz % (faqat sherik uchun)</label><input name="foiz" type="number" step="0.1" placeholder="0" value="0"></div>
          </div>
          <button class="btn" type="submit">➕ Qo'shish</button>
        </form>
      </div>
      <div class="card" id="t-card" style="display:none">
        <h2>✏️ Tahrirlash</h2>
        <form method="POST"><input type="hidden" name="amal" value="tahrirlash">
          <input type="hidden" name="ishchi_id" id="t-id">
          <div class="form-row4">
            <div><label>Ism</label><input id="t-ism" disabled style="background:#f5f5f5"></div>
            <div><label>Kunlik maosh</label><input name="maosh" id="t-maosh" type="number"></div>
            <div><label>Parol</label><input name="parol" id="t-parol"></div>
            <div><label>Rol</label><select name="rol" id="t-rol"><option value="ishchi">👷 Ishchi</option><option value="sherik">🤝 Sherik</option></select></div>
          </div>
          <div class="form-row">
            <div><label>Foiz %</label><input name="foiz" id="t-foiz" type="number" step="0.1"></div>
          </div>
          <button class="btn btn-green" type="submit">💾 Saqlash</button>
          <button class="btn btn-red" type="button" onclick="document.getElementById('t-card').style.display='none'">Bekor</button>
        </form>
      </div>
      <div class="card">
        <h2>👷 Ishchilar ro'yxati</h2>
        <table><tr><th>Ism</th><th>Kunlik maosh</th><th>Rol</th><th>Foiz</th><th>Amallar</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='5' style='text-align:center;color:#999'>Hali ishchi yo'q</td></tr>"}
        </table>
      </div>
    </div>
    <script>
    function tahrirlash(id,ism,maosh,rol,foiz,parol){{
      document.getElementById('t-card').style.display='block';
      document.getElementById('t-id').value=id;
      document.getElementById('t-ism').value=ism;
      document.getElementById('t-maosh').value=maosh;
      document.getElementById('t-parol').value=parol;
      document.getElementById('t-foiz').value=foiz;
      document.getElementById('t-rol').value=rol;
      document.getElementById('t-card').scrollIntoView();
    }}
    </script></body></html>""")

@app.route("/loyihalar", methods=["GET", "POST"])
def loyihalar_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    data = malumot_yuklash()
    if request.method == "POST":
        amal = request.form.get("amal")
        if amal == "qoshish":
            yangi_id = max([l["id"] for l in data["loyihalar"]], default=0) + 1
            data["loyihalar"].append({"id": yangi_id, "nom": request.form.get("nom"), "manzil": request.form.get("manzil"),
                "boshlanish": request.form.get("boshlanish"), "tugash": request.form.get("tugash"),
                "mijoz_puli": int(request.form.get("mijoz_puli",0)), "tugagan": False})
        elif amal == "tugash":
            loyiha = next((l for l in data["loyihalar"] if l["id"]==int(request.form.get("loyiha_id"))), None)
            if loyiha: loyiha["tugagan"] = True
        malumot_saqlash(data); return redirect("/loyihalar")

    qatorlar = ""
    for l in data["loyihalar"]:
        holat = "✅ Tugagan" if l.get("tugagan") else "🔄 Davom etmoqda"
        btn = "" if l.get("tugagan") else f'<form method="POST" style="display:inline"><input type="hidden" name="amal" value="tugash"><input type="hidden" name="loyiha_id" value="{l["id"]}"><button class="btn btn-red" style="font-size:11px;padding:4px 8px">✅ Tugatish</button></form>'
        qatorlar += f"<tr><td>{l['nom']}</td><td>{l['manzil']}</td><td>{l['mijoz_puli']:,} so'm</td><td>{l['boshlanish']}</td><td>{holat}</td><td>{btn}</td></tr>"

    return render_template_string(STIL + header("Loyihalar") + nav_rahbar() + f"""
    <div class="content">
      <div class="card"><h2>➕ Yangi loyiha</h2>
        <form method="POST"><input type="hidden" name="amal" value="qoshish">
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
      <div class="card"><h2>🏗️ Loyihalar</h2>
        <table><tr><th>Nom</th><th>Manzil</th><th>Mijoz puli</th><th>Boshlanish</th><th>Holat</th><th>Amal</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='6' style='text-align:center;color:#999'>Hali loyiha yo'q</td></tr>"}
        </table>
      </div>
    </div></body></html>""")

@app.route("/davomat", methods=["GET", "POST"])
def davomat_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    data = malumot_yuklash()
    if request.method == "POST":
        sana = request.form.get("sana")
        loyiha_id = int(request.form.get("loyiha_id"))
        for i in data["ishchilar"]:
            holat = request.form.get(f"holat_{i['id']}", "YOQ")
            mavjud = next((d for d in data["davomat"] if d["sana"]==sana and d["ishchi_id"]==i["id"] and d["loyiha_id"]==loyiha_id), None)
            if mavjud: mavjud["holat"] = holat
            else: data["davomat"].append({"sana": sana, "ishchi_id": i["id"], "loyiha_id": loyiha_id, "holat": holat})
        malumot_saqlash(data); return redirect("/davomat")

    loyiha_options = "".join([f"<option value='{l['id']}'>{l['nom']}</option>" for l in data["loyihalar"] if not l.get("tugagan")])
    ishchi_inputs = "".join([f"<tr><td>{i['ism']} <span class='badge badge-{i['rol']}'>{i['rol']}</span></td><td><select name='holat_{i['id']}'><option value='HA'>✅ Keldi</option><option value='YOQ'>❌ Kelmadi</option></select></td></tr>" for i in data["ishchilar"]])

    return render_template_string(STIL + header("Davomat") + nav_rahbar() + f"""
    <div class="content"><div class="card"><h2>📅 Davomat belgilash</h2>
      <form method="POST">
        <div class="form-row">
          <div><label>Sana</label><input name="sana" type="date" required></div>
          <div><label>Loyiha</label><select name="loyiha_id">{loyiha_options if loyiha_options else "<option>Loyiha yo'q</option>"}</select></div>
        </div>
        <table><tr><th>Ishchi</th><th>Holat</th></tr>{ishchi_inputs}</table>
        <br><button class="btn" type="submit">💾 Saqlash</button>
      </form>
    </div></div></body></html>""")

@app.route("/avanslar", methods=["GET", "POST"])
def avanslar_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    data = malumot_yuklash()
    if request.method == "POST":
        data["avanslar"].append({"sana": request.form.get("sana"), "ishchi_id": int(request.form.get("ishchi_id")),
            "loyiha_id": int(request.form.get("loyiha_id")), "miqdor": int(request.form.get("miqdor"))})
        malumot_saqlash(data); return redirect("/avanslar")

    ishchi_options = "".join([f"<option value='{i['id']}'>{i['ism']}</option>" for i in data["ishchilar"]])
    loyiha_options = "".join([f"<option value='{l['id']}'>{l['nom']}</option>" for l in data["loyihalar"]])
    qatorlar = ""; jami = 0
    for a in reversed(data["avanslar"]):
        ishchi = next((i["ism"] for i in data["ishchilar"] if i["id"]==a["ishchi_id"]), "?")
        loyiha = next((l["nom"] for l in data["loyihalar"] if l["id"]==a["loyiha_id"]), "?")
        jami += a["miqdor"]
        qatorlar += f"<tr><td>{a['sana']}</td><td>{ishchi}</td><td>{loyiha}</td><td>{a['miqdor']:,} so'm</td></tr>"

    return render_template_string(STIL + header("Avanslar") + nav_rahbar() + f"""
    <div class="content">
      <div class="card"><h2>💸 Avans berish</h2>
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
      <div class="card"><h2>Avanslar tarixi &nbsp;<span style="color:#BA7517">Jami: {jami:,} so'm</span></h2>
        <table><tr><th>Sana</th><th>Ishchi</th><th>Loyiha</th><th>Miqdor</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='4' style='text-align:center;color:#999'>Hali avans yo'q</td></tr>"}
        </table>
      </div>
    </div></body></html>""")

@app.route("/xarajatlar", methods=["GET", "POST"])
def xarajatlar_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    data = malumot_yuklash()
    if request.method == "POST":
        data["xarajatlar"].append({"sana": request.form.get("sana"), "tavsif": request.form.get("tavsif"),
            "loyiha_id": int(request.form.get("loyiha_id")), "miqdor": int(request.form.get("miqdor"))})
        malumot_saqlash(data); return redirect("/xarajatlar")

    loyiha_options = "".join([f"<option value='{l['id']}'>{l['nom']}</option>" for l in data["loyihalar"]])
    qatorlar = ""; jami = 0
    for x in reversed(data["xarajatlar"]):
        loyiha = next((l["nom"] for l in data["loyihalar"] if l["id"]==x["loyiha_id"]), "?")
        jami += x["miqdor"]
        qatorlar += f"<tr><td>{x['sana']}</td><td>{x['tavsif']}</td><td>{loyiha}</td><td>{x['miqdor']:,} so'm</td></tr>"

    return render_template_string(STIL + header("Xarajatlar") + nav_rahbar() + f"""
    <div class="content">
      <div class="card"><h2>🔧 Xarajat qo'shish</h2>
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
      <div class="card"><h2>Xarajatlar &nbsp;<span style="color:#c0392b">Jami: {jami:,} so'm</span></h2>
        <table><tr><th>Sana</th><th>Tavsif</th><th>Loyiha</th><th>Miqdor</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='4' style='text-align:center;color:#999'>Hali xarajat yo'q</td></tr>"}
        </table>
      </div>
    </div></body></html>""")

@app.route("/hisobot")
def hisobot_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    data = malumot_yuklash()
    if not data["loyihalar"]:
        return render_template_string(STIL + header("Hisobot") + nav_rahbar() + '<div class="content"><div class="card"><p style="color:#999">Hali loyiha yo\'q.</p><a class="btn" href="/loyihalar">🏗️ Loyiha qo\'shish</a></div></div></body></html>')

    loyiha_id = int(request.args.get("loyiha_id", data["loyihalar"][0]["id"]))
    loyiha = next((l for l in data["loyihalar"] if l["id"]==loyiha_id), None)
    loyiha_options = "".join([f"<option value='{l['id']}' {'selected' if l['id']==loyiha_id else ''}>{l['nom']}</option>" for l in data["loyihalar"]])

    mijoz_puli = loyiha["mijoz_puli"] if loyiha else 0
    jami_xarajat = sum(x["miqdor"] for x in data["xarajatlar"] if x["loyiha_id"]==loyiha_id)
    jami_maosh = sum(i["kunlik_maosh"] * len([d for d in data["davomat"] if d["ishchi_id"]==i["id"] and d["loyiha_id"]==loyiha_id and d["holat"]=="HA"]) for i in data["ishchilar"])
    sof_foyda_oldin = mijoz_puli - jami_maosh - jami_xarajat
    jami_sherik_foiz = sum(sof_foyda_oldin * i.get("foiz",0) / 100 for i in data["ishchilar"] if i.get("rol")=="sherik")
    sof_foyda = sof_foyda_oldin - jami_sherik_foiz

    qatorlar = ""
    for i in data["ishchilar"]:
        kunlar = len([d for d in data["davomat"] if d["ishchi_id"]==i["id"] and d["loyiha_id"]==loyiha_id and d["holat"]=="HA"])
        maosh = i["kunlik_maosh"] * kunlar
        avans = sum(a["miqdor"] for a in data["avanslar"] if a["ishchi_id"]==i["id"] and a["loyiha_id"]==loyiha_id)
        qolgan = maosh - avans
        foiz_text = f"{sof_foyda_oldin * i.get('foiz',0) / 100:,.0f} so'm" if i.get("rol")=="sherik" else "—"
        qatorlar += f"<tr><td>{i['ism']} <span class='badge badge-{i['rol']}'>{i['rol']}</span></td><td>{kunlar}</td><td>{maosh:,}</td><td>{avans:,}</td><td>{qolgan:,}</td><td>{foiz_text}</td></tr>"

    foyda_rang = "#27ae60" if sof_foyda >= 0 else "#c0392b"
    return render_template_string(STIL + header("Hisobot") + nav_rahbar() + f"""
    <div class="content">
      <div class="card"><h2>Loyiha tanlang</h2>
        <form method="GET"><select name="loyiha_id" onchange="this.form.submit()" style="max-width:300px">{loyiha_options}</select></form>
      </div>
      <div class="metric-grid">
        <div class="metric"><div class="metric-label">Mijozdan tushgan</div><div class="metric-value">{mijoz_puli:,}</div></div>
        <div class="metric"><div class="metric-label">Ishchilar maoshi</div><div class="metric-value" style="color:#333">{jami_maosh:,}</div></div>
        <div class="metric"><div class="metric-label">Xarajatlar</div><div class="metric-value" style="color:#c0392b">{jami_xarajat:,}</div></div>
        <div class="metric"><div class="metric-label">Sherik foizi</div><div class="metric-value" style="color:#2980b9">{jami_sherik_foiz:,.0f}</div></div>
        <div class="metric"><div class="metric-label">Sizning foydangiz</div><div class="metric-value" style="color:{foyda_rang}">{sof_foyda:,.0f}</div></div>
      </div>
      <div class="card"><h2>👷 Ishchilar hisobi</h2>
        <table><tr><th>Ism</th><th>Kun</th><th>Maosh</th><th>Avans</th><th>Qo'lga oladi</th><th>Foiz ulushi</th></tr>
          {qatorlar}
        </table>
      </div>
    </div></body></html>""")

@app.route("/reyting")
def reyting_sahifa():
    if "login" not in session: return redirect("/login")
    data = malumot_yuklash()
    ishchi_kunlar = sorted([{"ism": i["ism"], "kunlar": len([d for d in data["davomat"] if d["ishchi_id"]==i["id"] and d["holat"]=="HA"]), "rol": i.get("rol","ishchi")} for i in data["ishchilar"]], key=lambda x: x["kunlar"], reverse=True)
    medallar = ["🥇","🥈","🥉"]; sinflar = ["reyting-1","reyting-2","reyting-3"]
    qatorlar = "".join([f"<tr class='{sinflar[idx] if idx<3 else ''}'><td>{medallar[idx] if idx<3 else str(idx+1)+'.'}</td><td>{i['ism']} <span class='badge badge-{i[\"rol\"]}'>{i['rol']}</span></td><td><b>{i['kunlar']} kun</b></td></tr>" for idx, i in enumerate(ishchi_kunlar)])
    rol = session.get("rol")
    nav = nav_rahbar() if rol=="rahbar" else (nav_sherik() if rol=="sherik" else nav_ishchi())
    return render_template_string(STIL + header("Reyting") + nav + f"""
    <div class="content"><div class="card"><h2>🏆 Eng ko'p ishlagan ishchilar</h2>
      <table><tr><th>#</th><th>Ism</th><th>Ishlagan kun</th></tr>
        {qatorlar if qatorlar else "<tr><td colspan='3' style='text-align:center;color:#999'>Hali davomat kiritilmagan</td></tr>"}
      </table>
    </div></div></body></html>""")

@app.route("/mening_hisobim")
def mening_hisobim():
    if "login" not in session: return redirect("/login")
    data = malumot_yuklash()
    ishchi = next((i for i in data["ishchilar"] if i["ism"]==session.get("login")), None)
    if not ishchi: return redirect("/")
    rol = ishchi.get("rol","ishchi")
    nav = nav_sherik() if rol=="sherik" else nav_ishchi()
    qatorlar = ""; jami_qolgan = 0
    for l in data["loyihalar"]:
        kunlar = len([d for d in data["davomat"] if d["ishchi_id"]==ishchi["id"] and d["loyiha_id"]==l["id"] and d["holat"]=="HA"])
        maosh = ishchi["kunlik_maosh"] * kunlar
        avans = sum(a["miqdor"] for a in data["avanslar"] if a["ishchi_id"]==ishchi["id"] and a["loyiha_id"]==l["id"])
        qolgan = maosh - avans; jami_qolgan += qolgan
        qatorlar += f"<tr><td>{l['nom']}</td><td>{kunlar}</td><td>{maosh:,}</td><td>{avans:,}</td><td><b>{qolgan:,}</b></td></tr>"
    jami_kun = len([d for d in data["davomat"] if d["ishchi_id"]==ishchi["id"] and d["holat"]=="HA"])
    jami_avans = sum(a["miqdor"] for a in data["avanslar"] if a["ishchi_id"]==ishchi["id"])
    return render_template_string(STIL + header("Mening hisobim") + nav + f"""
    <div class="content">
      <div class="metric-grid">
        <div class="metric"><div class="metric-label">Jami ishlagan kun</div><div class="metric-value">{jami_kun}</div></div>
        <div class="metric"><div class="metric-label">Kunlik maosh</div><div class="metric-value" style="font-size:16px">{ishchi['kunlik_maosh']:,}</div></div>
        <div class="metric"><div class="metric-label">Jami avans</div><div class="metric-value" style="color:#e67e22">{jami_avans:,}</div></div>
        <div class="metric"><div class="metric-label">Qo'lga oladi</div><div class="metric-value" style="color:#27ae60">{jami_qolgan:,}</div></div>
      </div>
      <div class="card"><h2>📋 Loyihalar bo'yicha hisobim</h2>
        <table><tr><th>Loyiha</th><th>Kun</th><th>Maosh</th><th>Avans</th><th>Qo'lga oladi</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='5' style='text-align:center;color:#999'>Hali ma'lumot yo'q</td></tr>"}
          <tr style="background:#fff8f0;font-weight:bold;"><td colspan="4">UMUMIY QO'LGA OLADI:</td><td style="color:#27ae60">{jami_qolgan:,} so'm</td></tr>
        </table>
      </div>
    </div></body></html>""")

@app.route("/sherik_hisobi")
def sherik_hisobi():
    if "login" not in session: return redirect("/login")
    data = malumot_yuklash()
    ishchi = next((i for i in data["ishchilar"] if i["ism"]==session.get("login")), None)
    if not ishchi or ishchi.get("rol") != "sherik": return redirect("/mening_hisobim")
    foiz = ishchi.get("foiz", 0)
    qatorlar = ""; jami_daromad = 0
    for l in data["loyihalar"]:
        mijoz_puli = l["mijoz_puli"]
        jami_xarajat = sum(x["miqdor"] for x in data["xarajatlar"] if x["loyiha_id"]==l["id"])
        jami_maosh = sum(i["kunlik_maosh"] * len([d for d in data["davomat"] if d["ishchi_id"]==i["id"] and d["loyiha_id"]==l["id"] and d["holat"]=="HA"]) for i in data["ishchilar"])
        sof_foyda = mijoz_puli - jami_maosh - jami_xarajat
        daromad = sof_foyda * foiz / 100; jami_daromad += daromad
        qatorlar += f"<tr><td>{l['nom']}</td><td>{mijoz_puli:,}</td><td>{jami_maosh:,}</td><td>{jami_xarajat:,}</td><td>{sof_foyda:,.0f}</td><td style='color:#2e7d32'><b>{daromad:,.0f}</b></td></tr>"
    return render_template_string(STIL + header("Sherik hisobi") + nav_sherik() + f"""
    <div class="content">
      <div class="metric-grid">
        <div class="metric"><div class="metric-label">Foiz ulushim</div><div class="metric-value">{foiz}%</div></div>
        <div class="metric"><div class="metric-label">Jami daromadim</div><div class="metric-value" style="color:#27ae60">{jami_daromad:,.0f}</div></div>
      </div>
      <div class="card"><h2>💰 Loyihalar bo'yicha daromadim ({foiz}%)</h2>
        <table><tr><th>Loyiha</th><th>Mijoz puli</th><th>Maosh</th><th>Xarajat</th><th>Sof foyda</th><th>Mening ulushim</th></tr>
          {qatorlar if qatorlar else "<tr><td colspan='6' style='text-align:center;color:#999'>Hali loyiha yo'q</td></tr>"}
          <tr style="background:#e8f5e9;font-weight:bold;"><td colspan="5">JAMI DAROMADIM:</td><td style="color:#27ae60">{jami_daromad:,.0f} so'm</td></tr>
        </table>
      </div>
    </div></body></html>""")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8080)
