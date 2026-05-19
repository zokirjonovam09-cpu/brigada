import os
from flask import Flask, render_template_string, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "brigada_secret_2026")

# --- BAZA BILAN ULANISH ---
db_url = os.environ.get("POSTGRES_URL")

# Vercel bergan postgres:// URLni Flask-SQLAlchemy o'qishi uchun postgresql:// ga o'giramiz
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Agar baza topilmasa, vaqtincha xato bermasligi uchun sqlite ishlatadi (crash oldini olish uchun)
if not db_url:
    db_url = "sqlite:///vaqtinchalik.db"

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MA'LUMOTLAR MODELLARI ---
class Ishchi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ism = db.Column(db.String(100), unique=True, nullable=False)
    kunlik_maosh = db.Column(db.Integer, default=0)
    parol = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), default="ishchi")
    foiz = db.Column(db.Float, default=0.0)

class Loyiha(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    manzil = db.Column(db.String(200))
    boshlanish = db.Column(db.String(20))
    tugash = db.Column(db.String(20))
    mijoz_puli = db.Column(db.Integer, default=0)
    tugagan = db.Column(db.Boolean, default=False)

class Davomat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sana = db.Column(db.String(20), nullable=False)
    ishchi_id = db.Column(db.Integer, db.ForeignKey('ishchi.id'))
    loyiha_id = db.Column(db.Integer, db.ForeignKey('loyiha.id'))
    holat = db.Column(db.String(10))

class Avans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sana = db.Column(db.String(20))
    ishchi_id = db.Column(db.Integer, db.ForeignKey('ishchi.id'))
    loyiha_id = db.Column(db.Integer, db.ForeignKey('loyiha.id'))
    miqdor = db.Column(db.Integer, default=0)

class Xarajat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sana = db.Column(db.String(20))
    tavsif = db.Column(db.String(200))
    loyiha_id = db.Column(db.Integer, db.ForeignKey('loyiha.id'))
    miqdor = db.Column(db.Integer, default=0)

# --- BAZANI YARATISH ---
try:
    with app.app_context():
        db.create_all()
        if not Ishchi.query.first():
            standard_ishchilar = [
                Ishchi(ism="Muhammad Ali", kunlik_maosh=160000, parol="ali2026", rol="ishchi"),
                Ishchi(ism="Muhammad Ziyo", kunlik_maosh=150000, parol="ziyobek2711", rol="ishchi"),
                Ishchi(ism="Abdulhodiy", kunlik_maosh=150000, parol="bek2007", rol="ishchi")
            ]
            db.session.bulk_save_objects(standard_ishchilar)
            db.session.commit()
except Exception as e:
    print(f"Baza yaratishda xato: {e}")

RAHBAR_USER = {"login": "Usta Ziynatulloh", "parol": "masterHuseyin"}

# --- DIZAYN VA STIL ---
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
  .content { padding: 20px; max-width: 960px; }
  .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  table { width: 100%; border-collapse: collapse; }
  th { background: #BA7517; color: white; padding: 10px 12px; text-align: left; font-size: 13px; }
  td { padding: 10px 12px; border-bottom: 1px solid #eee; font-size: 14px; }
  .btn { display: inline-block; background: #BA7517; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; font-size: 13px; text-decoration: none; }
  .btn-red { background: #c0392b; }
  input, select { padding: 8px 10px; border: 1px solid #ccc; border-radius: 5px; font-size: 13px; width: 100%; margin-bottom: 8px; }
  .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .form-row4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 12px; }
  .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 16px; }
  .metric { background: white; border-radius: 8px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  .metric-label { font-size: 11px; color: #999; text-transform: uppercase; margin-bottom: 6px; }
  .metric-value { font-size: 20px; font-weight: bold; color: #BA7517; }
  .alert { padding: 12px; border-radius: 5px; margin-bottom: 12px; font-size: 14px; }
  .alert-red { background: #fde8e8; color: #c0392b; }
  .alert-green { background: #e8f5e9; color: #2e7d32; }
</style></head><body>"""

def header(s):
    return f'<div class="header"><b>🏗️ Brigada Tizimi — {s}</b><span>{session.get("login","")} &nbsp;|&nbsp; <a href="/chiqish">Chiqish</a></span></div>'

def nav_rahbar():
    return '<div class="nav"><a href="/">🏠 Bosh sahifa</a><a href="/ishchilar">👷 Ishchilar</a><a href="/loyihalar">🏗️ Loyihalar</a><a href="/davomat">📅 Davomat</a><a href="/avanslar">💸 Avanslar</a><a href="/xarajatlar">🔧 Xarajatlar</a><a href="/hisobot">📊 Hisobot</a><a href="/reyting">🏆 Reyting</a></div>'

def nav_ishchi():
    return '<div class="nav"><a href="/mening_hisobim">📋 Mening hisobim</a><a href="/reyting">🏆 Reyting</a></div>'

# --- ROUTING LOGIKA ---

@app.route("/login", methods=["GET", "POST"])
def login():
    xato = ""
    # Agar Vercel Postgres ulanmagan bo'lsa, ogohlantirish ko'rsatadi
    if "sqlite" in app.config['SQLALCHEMY_DATABASE_URI']:
        xato = "⚠️ Diqqat: Vercel Storage (Postgres) hali loyihaga ulanmagan!"
        
    if request.method == "POST":
        l = request.form.get("login", "").strip()
        p = request.form.get("parol", "").strip()
        if l == RAHBAR_USER["login"] and p == RAHBAR_USER["parol"]:
            session["login"] = l; session["rol"] = "rahbar"
            return redirect("/")
        try:
            ishchi = Ishchi.query.filter_by(ism=l, parol=p).first()
            if ishchi:
                session["login"] = l; session["rol"] = ishchi.rol; session["ishchi_id"] = ishchi.id
                return redirect("/")
            xato = "Login yoki parol noto'g'ri!"
        except Exception as e:
            xato = f"Baza bilan bog'lanishda xatolik: {str(e)}"
            
    return render_template_string(STIL + f"""
    <div style="display:flex;justify-content:center;align-items:center;min-height:100vh;">
      <div style="background:white;padding:40px;border-radius:10px;width:340px;box-shadow:0 4px 12px rgba(0,0,0,0.15);">
        <h2 style="text-align:center;color:#BA7517;margin-bottom:24px;">🏗️ Brigada Tizimi</h2>
        {"<div class='alert alert-red'>"+xato+"</div>" if xato else ""}
        <form method="POST">
          <label>Login (Ism)</label><input name="login" placeholder="Ism Familiya" required>
          <label>Parol</label><input name="parol" type="password" placeholder="Parol" required>
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
        try:
            ishchilar_soni = Ishchi.query.count()
            loyihalar_soni = Loyiha.query.count()
            faol_loyiha = Loyiha.query.filter_by(tugagan=False).first()
            faol_nom = faol_loyiha.nom if faol_loyiha else "Yo'q"
        except:
            ishchilar_soni, loyihalar_soni, faol_nom = 0, 0, "Baza xatosi"
            
        return render_template_string(STIL + header("Dashboard") + nav_rahbar() + f"""
        <div class="content">
          <div class="metric-grid">
            <div class="metric"><div class="metric-label">Ishchilar</div><div class="metric-value">{ishchilar_soni}</div></div>
            <div class="metric"><div class="metric-label">Loyihalar</div><div class="metric-value">{loyihalar_soni}</div></div>
            <div class="metric"><div class="metric-label">Faol loyiha</div><div class="metric-value" style="font-size:14px">{faol_nom}</div></div>
          </div>
          <div class="card"><h2>Tezkor havolalar</h2>
            <a class="btn" href="/davomat">📅 Davomat</a>
            <a class="btn" href="/avanslar">💸 Avans</a>
            <a class="btn" href="/hisobot">📊 Hisobot</a>
          </div>
        </div></body></html>""")
    else: return redirect("/mening_hisobim")

@app.route("/ishchilar", methods=["GET", "POST"])
def ishchilar_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    xabar = ""
    if request.method == "POST":
        amal = request.form.get("amal")
        if amal == "qoshish":
            yangi = Ishchi(ism=request.form.get("ism"), kunlik_maosh=int(request.form.get("maosh", 0)), parol=request.form.get("parol"), rol=request.form.get("rol"))
            db.session.add(yangi); db.session.commit()
            xabar = "✅ Qo'shildi!"
        elif amal == "ochirish":
            Ishchi.query.filter_by(id=request.form.get("ishchi_id")).delete()
            db.session.commit()
            xabar = "✅ O'chirildi!"
            
    ishchilar = Ishchi.query.all()
    qatorlar = "".join([f"<tr><td>{i.ism}</td><td>{i.kunlik_maosh:,}</td><td>{i.rol}</td><td><form method='POST' style='display:inline'><input type='hidden' name='amal' value='ochirish'><input type='hidden' name='ishchi_id' value='{i.id}'><button class='btn btn-red' type='submit'>🗑️</button></form></td></tr>" for i in ishchilar])
    return render_template_string(STIL + header("Ishchilar") + nav_rahbar() + f"""<div class="content">{"<div class='alert alert-green'>"+xabar+"</div>" if xabar else ""}<div class="card"><h2>➕ Yangi ishchi</h2><form method="POST"><input type="hidden" name="amal" value="qoshish"><div class="form-row4"><input name="ism" placeholder="Ism Familiya" required><input name="maosh" type="number" placeholder="Maosh" required><input name="parol" placeholder="Parol" required><select name="rol"><option value="ishchi">Ishchi</option><option value="sherik">Sherik</option></select></div><button class="btn" type="submit">➕ Qo'shish</button></form></div><div class="card"><table><tr><th>Ism</th><th>Maosh</th><th>Rol</th><th>Amal</th></tr>{qatorlar}</table></div></div></body></html>""")

@app.route("/loyihalar", methods=["GET", "POST"])
def loyihalar_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    if request.method == "POST":
        amal = request.form.get("amal")
        if amal == "qoshish":
            yangi = Loyiha(nom=request.form.get("nom"), manzil=request.form.get("manzil"), mijoz_puli=int(request.form.get("mijoz_puli",0)))
            db.session.add(yangi); db.session.commit()
        elif amal == "tugatish":
            l = Loyiha.query.get(request.form.get("loyiha_id"))
            if l: l.tugagan = True; db.session.commit()
    loyihalar = Loyiha.query.all()
    qatorlar = "".join([f"<tr><td>{l.nom}</td><td>{l.mijoz_puli:,}</td><td>{'Tugagan' if l.tugagan else 'Faol'}</td><td><form method='POST'><input type='hidden' name='amal' value='tugatish'><input type='hidden' name='loyiha_id' value='{l.id}'><button class='btn btn-red'>Tugatish</button></form></td></tr>" for l in loyihalar])
    return render_template_string(STIL + header("Loyihalar") + nav_rahbar() + f"""<div class="content"><div class="card"><form method="POST"><input type="hidden" name="amal" value="qoshish"><div class="form-row"><input name="nom" placeholder="Loyiha nomi" required><input name="mijoz_puli" type="number" placeholder="Mijoz puli"></div><button class="btn" type="submit">➕ Qo'shish</button></form></div><div class="card"><table><tr><th>Nom</th><th>Mijoz puli</th><th>Holat</th><th>Amal</th></tr>{qatorlar}</table></div></div></body></html>""")

@app.route("/davomat", methods=["GET", "POST"])
def davomat_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    if request.method == "POST":
        sana = request.form.get("sana")
        loyiha_id = int(request.form.get("loyiha_id"))
        for i in Ishchi.query.all():
            holat = request.form.get(f"holat_{i.id}", "YOQ")
            Davomat.query.filter_by(sana=sana, ishchi_id=i.id, loyiha_id=loyiha_id).delete()
            db.session.add(Davomat(sana=sana, ishchi_id=i.id, loyiha_id=loyiha_id, holat=holat))
        db.session.commit()
    loyihalar = Loyiha.query.filter_by(tugagan=False).all()
    ishchilar = Ishchi.query.all()
    loyiha_options = "".join([f"<option value='{l.id}'>{l.nom}</option>" for l in loyihalar])
    ishchi_rows = "".join([f"<tr><td>{i.ism}</td><td><select name='holat_{i.id}'><option value='HA'>Keldi</option><option value='YOQ'>Kelmadi</option></select></td></tr>" for i in ishchilar])
    return render_template_string(STIL + header("Davomat") + nav_rahbar() + f"""<div class="content"><div class="card"><form method="POST"><label>Sana</label><input name="sana" type="date" required><label>Loyiha</label><select name="loyiha_id">{loyiha_options}</select><table>{ishchi_rows}</table><button class="btn" type="submit">💾 Saqlash</button></form></div></div></body></html>""")

@app.route("/avanslar", methods=["GET", "POST"])
def avanslar_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    if request.method == "POST":
        db.session.add(Avans(sana=request.form.get("sana"), ishchi_id=int(request.form.get("ishchi_id")), loyiha_id=int(request.form.get("loyiha_id")), miqdor=int(request.form.get("miqdor"))))
        db.session.commit()
    ishchilar = Ishchi.query.all()
    loyihalar = Loyiha.query.all()
    avanslar = Avans.query.order_by(Avans.id.desc()).limit(10).all()
    ishchi_opt = "".join([f"<option value='{i.id}'>{i.ism}</option>" for i in ishchilar])
    loyiha_opt = "".join([f"<option value='{l.id}'>{l.nom}</option>" for l in loyihalar])
    qatorlar = "".join([f"<tr><td>{a.sana}</td><td>{Ishchi.query.get(a.ishchi_id).ism if Ishchi.query.get(a.ishchi_id) else ''}</td><td>{a.miqdor:,}</td></tr>" for a in avanslar])
    return render_template_string(STIL + header("Avanslar") + nav_rahbar() + f"""<div class="content"><div class="card"><form method="POST"><input name="sana" type="date" required><select name="ishchi_id">{ishchi_opt}</select><select name="loyiha_id">{loyiha_opt}</select><input name="miqdor" type="number" placeholder="Summa" required><button class="btn" type="submit">Berish</button></form></div><div class="card"><table><tr><th>Sana</th><th>Ishchi</th><th>Summa</th></tr>{qatorlar}</table></div></div></body></html>""")

@app.route("/xarajatlar", methods=["GET", "POST"])
def xarajatlar_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    if request.method == "POST":
        db.session.add(Xarajat(sana=request.form.get("sana"), tavsif=request.form.get("tavsif"), loyiha_id=int(request.form.get("loyiha_id")), miqdor=int(request.form.get("miqdor"))))
        db.session.commit()
    loyihalar = Loyiha.query.all()
    loyiha_opt = "".join([f"<option value='{l.id}'>{l.nom}</option>" for l in loyihalar])
    xarajatlar = Xarajat.query.order_by(Xarajat.id.desc()).all()
    qatorlar = "".join([f"<tr><td>{x.sana}</td><td>{x.tavsif}</td><td>{x.miqdor:,}</td></tr>" for x in xarajatlar])
    return render_template_string(STIL + header("Xarajatlar") + nav_rahbar() + f"""<div class="content"><div class="card"><form method="POST"><input name="sana" type="date" required><input name="tavsif" placeholder="Nima uchun"><select name="loyiha_id">{loyiha_opt}</select><input name="miqdor" type="number" placeholder="Summa"><button class="btn" type="submit">Qo'shish</button></form></div><div class="card"><table>{qatorlar}</table></div></div></body></html>""")

@app.route("/hisobot")
def hisobot_sahifa():
    if session.get("rol") != "rahbar": return redirect("/")
    loyihalar = Loyiha.query.all()
    if not loyihalar: return "Loyiha yaratilmagan"
    l_id = int(request.args.get("loyiha_id", loyihalar[0].id))
    loyiha = Loyiha.query.get(l_id)
    mijoz_puli = loyiha.mijoz_puli
    jami_xarajat = db.session.query(func.sum(Xarajat.miqdor)).filter_by(loyiha_id=l_id).scalar() or 0
    jami_maosh = 0
    ishchi_details = ""
    for i in Ishchi.query.all():
        kunlar = Davomat.query.filter_by(ishchi_id=i.id, loyiha_id=l_id, holat="HA").count()
        maosh = i.kunlik_maosh * kunlar
        avans = db.session.query(func.sum(Avans.miqdor)).filter_by(ishchi_id=i.id, loyiha_id=l_id).scalar() or 0
        jami_maosh += maosh
        ishchi_details += f"<tr><td>{i.ism}</td><td>{kunlar}</td><td>{maosh:,}</td><td>{avans:,}</td><td>{maosh-avans:,}</td></tr>"
    sof_foyda = mijoz_puli - jami_maosh - jami_xarajat
    loyiha_opt = "".join([f"<option value='{l.id}' {'selected' if l.id==l_id else ''}>{l.nom}</option>" for l in loyihalar])
    return render_template_string(STIL + header("Hisobot") + nav_rahbar() + f"""<div class="content"><form><select name="loyiha_id" onchange="this.form.submit()">{loyiha_opt}</select></form><div class="metric-grid"><div class="metric"><div class="metric-label">Mijoz puli</div><div class="metric-value">{mijoz_puli:,}</div></div><div class="metric"><div class="metric-label">Xarajat</div><div class="metric-value">{jami_xarajat:,}</div></div><div class="metric"><div class="metric-label">Maoshlar</div><div class="metric-value">{jami_maosh:,}</div></div><div class="metric"><div class="metric-label">Sof foyda</div><div class="metric-value">{sof_foyda:,}</div></div></div><div class="card"><table><tr><th>Ism</th><th>Kun</th><th>Maosh</th><th>Avans</th><th>Qolgan</th></tr>{ishchi_details}</table></div></div></body></html>""")

@app.route("/reyting")
def reyting_sahifa():
    if "login" not in session: return redirect("/login")
    data = [{"ism": i.ism, "kunlar": Davomat.query.filter_by(ishchi_id=i.id, holat="HA").count()} for i in Ishchi.query.all()]
    data = sorted(data, key=lambda x: x["kunlar"], reverse=True)
    qatorlar = "".join([f"<tr><td>{idx+1}</td><td>{i['ism']}</td><td>{i['kunlar']} kun</td></tr>" for idx, i in enumerate(data)])
    return render_template_string(STIL + header("Reyting") + (nav_rahbar() if session.get("rol")=="rahbar" else nav_ishchi()) + f"<div class='content'><div class='card'><table>{qatorlar}</table></div></div></body></html>")

@app.route("/mening_hisobim")
def mening_hisobim():
    if "login" not in session: return redirect("/login")
    ishchi_id = session.get("ishchi_id")
    ishchi = Ishchi.query.get(ishchi_id)
    if not ishchi: return redirect("/login")
    qatorlar = ""
    jami_qolgan = 0
    for l in Loyiha.query.all():
        kunlar = Davomat.query.filter_by(ishchi_id=ishchi_id, loyiha_id=l.id, holat="HA").count()
        maosh = ishchi.kunlik_maosh * kunlar
        avans = db.session.query(func.sum(Avans.miqdor)).filter_by(ishchi_id=ishchi_id, loyiha_id=l.id).scalar() or 0
        qolgan = maosh - avans
        jami_qolgan += qolgan
        qatorlar += f"<tr><td>{l.nom}</td><td>{kunlar}</td><td>{maosh:,}</td><td>{avans:,}</td><td>{qolgan:,}</td></tr>"
    return render_template_string(STIL + header("Mening hisobim") + nav_ishchi() + f"""<div class="content"><div class="metric-grid"><div class="metric"><div class="metric-label">Qolgan maosh</div><div class="metric-value">{jami_qolgan:,}</div></div></div><div class="card"><table><tr><th>Loyiha</th><th>Kun</th><th>Maosh</th><th>Avans</th><th>Qolgan</th></tr>{qatorlar}</table></div></div></body></html>""")

if __name__ == "__main__":
    app.run()