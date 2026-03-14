"""
╔══════════════════════════════════════════════════════╗
║        BONG BROWSER  v4.0  —  Flask PWA              ║
║           Modified by Bong.Dev  ⚡                    ║
║   Android + Windows — Chrome থেকেই Install হবে      ║
╚══════════════════════════════════════════════════════╝
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3, hashlib, os, re
from datetime import datetime, date
from functools import wraps

app = Flask(__name__)
app.secret_key = "bongbrowser_secret_bongdev_2024_xk9m"

DB = os.path.join(os.path.dirname(__file__), "bongbrowser.db")

# ═══════════════════════════════════════
#  DATABASE
# ═══════════════════════════════════════
def get_db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = get_db()
    c.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        pwd TEXT NOT NULL,
        name TEXT NOT NULL,
        dob TEXT NOT NULL,
        is18 INTEGER DEFAULT 0,
        joined TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER, url TEXT, title TEXT,
        ts TEXT DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bookmarks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER, url TEXT, title TEXT,
        ts TEXT DEFAULT CURRENT_TIMESTAMP)''')
    c.commit(); c.close()

def sha(p):
    return hashlib.sha256(p.encode()).hexdigest()

def calc_age(dob):
    try:
        d = datetime.strptime(dob, "%Y-%m-%d").date()
        t = date.today()
        return t.year - d.year - ((t.month,t.day) < (d.month,d.day))
    except:
        return 0

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "uid" not in session:
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated

# ═══════════════════════════════════════
#  AUTH ROUTES
# ═══════════════════════════════════════
@app.route("/api/register", methods=["POST"])
def register():
    d = request.json
    name  = d.get("name","").strip()
    email = d.get("email","").strip().lower()
    pwd   = d.get("pwd","").strip()
    dob   = d.get("dob","")

    if not all([name, email, pwd, dob]):
        return jsonify({"ok": False, "msg": "সব ফিল্ড পূরণ করুন"})
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({"ok": False, "msg": "সঠিক Email দিন"})
    if len(pwd) < 6:
        return jsonify({"ok": False, "msg": "Password কমপক্ষে ৬ অক্ষর হবে"})

    age = calc_age(dob)
    is18 = 1 if age >= 18 else 0

    try:
        c = get_db()
        c.execute("INSERT INTO users(email,pwd,name,dob,is18,joined) VALUES(?,?,?,?,?,?)",
            (email, sha(pwd), name, dob, is18, datetime.now().isoformat()))
        c.commit(); c.close()
        msg = f"✅ সফল! বয়স {age} বছর — {'18+ Mode চালু হবে' if is18 else 'Safe Mode থাকবে'}। Login করুন।"
        return jsonify({"ok": True, "msg": msg, "is18": is18, "age": age})
    except sqlite3.IntegrityError:
        return jsonify({"ok": False, "msg": "এই Email দিয়ে আগেই রেজিস্ট্রেশন হয়েছে"})

@app.route("/api/login", methods=["POST"])
def login():
    d = request.json
    email = d.get("email","").strip().lower()
    pwd   = d.get("pwd","").strip()

    if not email or not pwd:
        return jsonify({"ok": False, "msg": "সব ফিল্ড পূরণ করুন"})

    c = get_db()
    row = c.execute("SELECT * FROM users WHERE email=? AND pwd=?",
        (email, sha(pwd))).fetchone()
    c.close()

    if row:
        age = calc_age(row["dob"])
        is18 = 1 if age >= 18 else 0
        # update is18 in case birthday passed
        c = get_db()
        c.execute("UPDATE users SET is18=? WHERE id=?", (is18, row["id"]))
        c.commit(); c.close()

        session["uid"]   = row["id"]
        session["name"]  = row["name"]
        session["email"] = row["email"]
        session["is18"]  = is18
        session["age"]   = age
        return jsonify({"ok": True, "name": row["name"], "is18": is18, "age": age})
    return jsonify({"ok": False, "msg": "ভুল Email বা Password"})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/me")
def me():
    if "uid" not in session:
        return jsonify({"logged": False})
    return jsonify({
        "logged": True,
        "name":  session.get("name"),
        "email": session.get("email"),
        "is18":  session.get("is18", 0),
        "age":   session.get("age", 0)
    })

# ═══════════════════════════════════════
#  HISTORY ROUTES
# ═══════════════════════════════════════
@app.route("/api/history", methods=["GET"])
@login_required
def get_history():
    c = get_db()
    rows = c.execute(
        "SELECT id,url,title,ts FROM history WHERE uid=? ORDER BY id DESC LIMIT 60",
        (session["uid"],)).fetchall()
    c.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/history", methods=["POST"])
@login_required
def add_history():
    d = request.json
    url = d.get("url",""); title = d.get("title","")
    if url and url not in ("about:blank",""):
        c = get_db()
        c.execute("INSERT INTO history(uid,url,title,ts) VALUES(?,?,?,?)",
            (session["uid"], url, title[:200], datetime.now().strftime("%d/%m %H:%M")))
        c.commit(); c.close()
    return jsonify({"ok": True})

@app.route("/api/history/clear", methods=["POST"])
@login_required
def clear_history():
    c = get_db()
    c.execute("DELETE FROM history WHERE uid=?", (session["uid"],))
    c.commit(); c.close()
    return jsonify({"ok": True})

# ═══════════════════════════════════════
#  BOOKMARKS ROUTES
# ═══════════════════════════════════════
@app.route("/api/bookmarks", methods=["GET"])
@login_required
def get_bookmarks():
    c = get_db()
    rows = c.execute(
        "SELECT id,url,title,ts FROM bookmarks WHERE uid=? ORDER BY id DESC",
        (session["uid"],)).fetchall()
    c.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/bookmarks", methods=["POST"])
@login_required
def add_bookmark():
    d = request.json
    url = d.get("url",""); title = d.get("title","")
    if url:
        c = get_db()
        c.execute("INSERT INTO bookmarks(uid,url,title) VALUES(?,?,?)",
            (session["uid"], url, title[:200]))
        c.commit(); c.close()
    return jsonify({"ok": True})

@app.route("/api/bookmarks/<int:bid>", methods=["DELETE"])
@login_required
def del_bookmark(bid):
    c = get_db()
    c.execute("DELETE FROM bookmarks WHERE id=? AND uid=?", (bid, session["uid"]))
    c.commit(); c.close()
    return jsonify({"ok": True})

# ═══════════════════════════════════════
#  MAIN ROUTE
# ═══════════════════════════════════════
@app.route("/")
def index():
    return render_template("index.html")

# ═══════════════════════════════════════
#  RUN
# ═══════════════════════════════════════
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
