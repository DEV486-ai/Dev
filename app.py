"""
BONG BROWSER v11.0 — Modified by Bong.Dev ⚡
সব সমস্যা ঠিক করা হয়েছে:
✅ Permanent session (365 দিন - কখনো logout হবে না)
✅ DOB - দিন/মাস/বছর আলাদা dropdown
✅ Admin Panel - শুধু admin দেখবে
✅ Admin visibility toggle (only_me / everyone)
✅ Google Login - block হবে না
✅ Login info মুছে যাবে না
✅ সবাই use করতে পারবে
"""
from flask import Flask, request, jsonify, session, redirect
import sqlite3, hashlib, os, re, base64, urllib.parse, urllib.request, json as json_lib
from datetime import datetime, date, timedelta

app = Flask(__name__)
app.secret_key = "bongbrowser_v11_final_2025_secure"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bong.db")

ADMIN_EMAIL    = "kundudev811@gmail.com"
ADMIN_PASSWORD = "soumyadevkundu"
ADMIN_NAME     = "Bong.Dev Admin"

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "696472052037-9ujevbnf69c3tjcg1qf2pvu3v0m5rk7k.apps.googleusercontent.com")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_SECRET", "")
GOOGLE_REDIRECT      = "https://bong-browser.onrender.com/auth/google/callback"

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = db()
    c.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE, pwd TEXT,
        name TEXT, dob TEXT, is18 INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0, joined TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER, url TEXT, title TEXT, ts TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bookmarks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER, url TEXT, title TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS downloads(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER, url TEXT, filename TEXT,
        size TEXT, ts TEXT)''')
    c.commit(); c.close()

def sha(p): return hashlib.sha256(p.encode()).hexdigest()

def calc_age(dob):
    try:
        d = datetime.strptime(dob, "%Y-%m-%d").date()
        t = date.today()
        return t.year-d.year-((t.month,t.day)<(d.month,d.day))
    except: return 0

HTML = """<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="theme-color" content="#202124">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<meta name="apple-mobile-web-app-title" content="Bong Browser">
<title>Bong Browser</title>
<link rel="manifest" href="/manifest.json">
<link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#202124;--bg1:#292a2d;--bg2:#35363a;--bg3:#3c4043;
  --urlbar:#303134;--text:#e8eaed;--text2:#9aa0a6;--text3:#5f6368;
  --blue:#8ab4f8;--blue2:#1a73e8;
  --red:#f28b82;--green:#81c995;--gold:#fdd663;--purple:#c084fc;
  --hover:rgba(255,255,255,.08);
  --st:env(safe-area-inset-top,0px);--sb:env(safe-area-inset-bottom,0px);
}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%;overflow:hidden}
body{font-family:'Roboto',sans-serif;background:var(--bg);color:var(--text);
  display:flex;flex-direction:column;height:100dvh}
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-thumb{background:var(--bg3);border-radius:2px}

/* AUTH */
#auth-scr{position:absolute;inset:0;display:flex;align-items:center;
  justify-content:center;overflow-y:auto;padding:20px;background:var(--bg);z-index:100}
.acard{position:relative;z-index:1;background:var(--bg1);border:1px solid var(--bg3);
  border-radius:12px;padding:28px 24px;width:100%;max-width:400px;
  box-shadow:0 4px 24px rgba(0,0,0,.5);animation:ci .4s ease both}
@keyframes ci{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
.logo-row{display:flex;align-items:center;justify-content:center;gap:10px;margin-bottom:4px}
.logo-ico{width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#8ab4f8,#1a73e8);
  display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:900;color:#202124}
.logo-txt{font-size:19px;font-weight:700;color:var(--text);font-family:'Google Sans',sans-serif}
.logo-sub{text-align:center;font-size:11px;color:var(--text2);margin-bottom:20px;letter-spacing:.5px}
.atabs{display:flex;border-bottom:1px solid var(--bg3);margin-bottom:18px}
.atab{flex:1;padding:10px;background:none;border:none;cursor:pointer;color:var(--text2);
  font-size:13px;font-weight:500;transition:all .2s;border-bottom:2px solid transparent;margin-bottom:-1px}
.atab.on{color:var(--blue);border-bottom-color:var(--blue)}
.fp{display:none!important}.fp.on{display:block!important}
.fg{margin-bottom:12px}
.fl{font-size:10px;color:var(--text2);font-weight:500;letter-spacing:.5px;
  text-transform:uppercase;margin-bottom:4px;display:block}
.fi{width:100%;background:var(--urlbar);border:1px solid var(--bg3);border-radius:8px;
  padding:10px 13px;color:var(--text);font-size:14px;outline:none;transition:all .2s}
.fi:focus{border-color:var(--blue);background:var(--bg3)}
.fi::placeholder{color:var(--text3)}
select.fi{cursor:pointer;-webkit-appearance:none;appearance:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='%239aa0a6'%3E%3Cpath d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 12px center;padding-right:32px}
select.fi option{background:#292a2d;color:var(--text)}
.dob-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}
.amsg{min-height:18px;font-size:11px;text-align:center;margin:6px 0;line-height:1.5}
.amsg.e{color:var(--red)}.amsg.ok{color:var(--green)}.amsg.w{color:var(--gold)}
.abtn{width:100%;padding:12px;border:none;border-radius:8px;cursor:pointer;
  font-family:'Google Sans',sans-serif;font-size:14px;font-weight:500;transition:all .15s;margin-top:4px}
.abtn:active{transform:scale(.98)}
.abtn-p{background:var(--blue2);color:#fff}
.abtn-s{background:#a8c7fa;color:#202124}
.abtn-o{background:transparent;border:1px solid var(--bg3)!important;color:var(--text2)}
.forgot-link{text-align:right;margin-top:-4px;margin-bottom:8px}
.forgot-link a{font-size:11px;color:var(--blue);cursor:pointer;font-weight:500}
.divider{display:flex;align-items:center;gap:8px;margin:12px 0}
.divider-line{flex:1;height:1px;background:var(--bg3)}
.divider-text{font-size:11px;color:var(--text3)}
.g-btn{display:flex;align-items:center;justify-content:center;gap:10px;
  background:#fff;border:none;border-radius:8px;padding:11px 16px;
  text-decoration:none;color:#3c4043;font-family:'Google Sans',sans-serif;
  font-size:14px;font-weight:500;width:100%;cursor:pointer;transition:box-shadow .15s}
.g-btn:hover{box-shadow:0 1px 6px rgba(0,0,0,.25)}
.afoot{text-align:center;font-size:10px;color:var(--text3);margin-top:14px}
.afoot span{color:var(--blue)}

/* RESET */
#reset-panel{position:fixed;inset:0;z-index:200;background:rgba(0,0,0,.7);
  display:none;align-items:center;justify-content:center;padding:20px}
#reset-panel.open{display:flex}
.reset-card{background:var(--bg1);border:1px solid var(--bg3);border-radius:12px;
  padding:24px 20px;width:100%;max-width:380px;animation:ci .3s ease both}
.rstep{display:none}.rstep.on{display:block}

/* BROWSER */
#bscr{display:none;flex-direction:column;height:100%;background:var(--bg)}
#bscr.show{display:flex}
#inst-bar{background:var(--blue2);padding:9px 14px;display:none;align-items:center;gap:10px;flex-shrink:0}
#inst-bar.show{display:flex}
.ib-t{flex:1;font-size:12px;color:#fff;font-weight:500}
.ib-b{background:#fff;color:var(--blue2);border:none;border-radius:18px;padding:5px 13px;font-size:11px;font-weight:700;cursor:pointer}
.ib-c{background:none;border:none;color:rgba(255,255,255,.7);font-size:18px;cursor:pointer}
#tab-bar{background:var(--bg2);display:flex;align-items:flex-end;padding:7px 8px 0;gap:1px;
  flex-shrink:0;padding-top:calc(7px + var(--st));overflow-x:auto;scrollbar-width:none;min-height:42px}
#tab-bar::-webkit-scrollbar{display:none}
.tab{display:flex;align-items:center;gap:7px;padding:0 11px;height:33px;background:var(--bg);
  opacity:.7;border-radius:8px 8px 0 0;min-width:130px;max-width:190px;cursor:pointer;
  flex-shrink:0;position:relative;transition:all .15s;border:1px solid var(--bg3);border-bottom:none}
.tab.active{opacity:1}
.tab.active::after{content:'';position:absolute;bottom:-1px;left:0;right:0;height:1px;background:var(--bg)}
.tab-fav{font-size:12px;flex-shrink:0}
.tab-t{flex:1;font-size:11px;color:var(--text2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tab.active .tab-t{color:var(--text)}
.tab-x{width:16px;height:16px;border-radius:50%;background:none;border:none;cursor:pointer;
  color:var(--text2);font-size:11px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.ntab-btn{width:26px;height:26px;border-radius:50%;background:none;border:none;cursor:pointer;
  color:var(--text2);font-size:17px;display:flex;align-items:center;justify-content:center;
  flex-shrink:0;align-self:center;margin-left:4px}
#toolbar{background:var(--bg2);border-bottom:1px solid var(--bg3);
  display:flex;align-items:center;padding:7px 10px;gap:5px;flex-shrink:0}
.nb{width:34px;height:34px;border-radius:50%;background:none;border:none;cursor:pointer;
  color:var(--text2);font-size:18px;display:flex;align-items:center;justify-content:center;
  flex-shrink:0;transition:all .15s}
.nb:hover{background:var(--hover);color:var(--text)}
.nb:disabled{opacity:.3;pointer-events:none}
#uw{flex:1;height:38px;background:var(--urlbar);border-radius:20px;
  display:flex;align-items:center;padding:0 14px;gap:8px;transition:all .2s}
#uw:focus-within{background:#fff;box-shadow:0 1px 6px rgba(32,33,36,.28)}
#lk{font-size:13px;flex-shrink:0;color:var(--text2)}
#uw:focus-within #lk{color:var(--blue2)}
#ub{flex:1;background:none;border:none;outline:none;color:var(--text);font-size:14px;min-width:0}
#uw:focus-within #ub{color:#202124}
#ub::placeholder{color:var(--text3)}
.ustar{background:none;border:none;cursor:pointer;color:var(--text2);font-size:16px;padding:2px;flex-shrink:0}
.rtools{display:flex;align-items:center;gap:3px}
.tb2{width:34px;height:34px;border-radius:50%;background:none;border:none;cursor:pointer;
  color:var(--text2);font-size:17px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.tb2:hover{background:var(--hover);color:var(--text)}
.profbtn{width:28px;height:28px;border-radius:50%;
  background:linear-gradient(135deg,var(--blue2),#0d47a1);
  display:flex;align-items:center;justify-content:center;
  color:#fff;font-size:12px;font-weight:700;cursor:pointer;
  flex-shrink:0;border:2px solid var(--blue);font-family:'Google Sans',sans-serif}
#bkbar{background:var(--bg2);border-bottom:1px solid var(--bg3);
  display:flex;align-items:center;padding:4px 10px;gap:2px;
  flex-shrink:0;overflow-x:auto;scrollbar-width:none}
#bkbar::-webkit-scrollbar{display:none}
.bki{display:flex;align-items:center;gap:5px;padding:4px 10px;border-radius:18px;
  cursor:pointer;font-size:12px;color:var(--text2);white-space:nowrap;
  transition:all .15s;border:none;background:none}
.bki:hover{background:var(--hover);color:var(--text)}
.bksep{width:1px;height:16px;background:var(--bg3);flex-shrink:0;margin:0 2px}
#ct{flex:1;position:relative;overflow:hidden;background:#fff}
#hp{position:absolute;inset:0;overflow-y:auto;background:var(--bg);
  display:flex;flex-direction:column;align-items:center;padding:24px 18px 100px}
.hlogo{font-family:'Google Sans',sans-serif;font-size:clamp(28px,9vw,50px);
  font-weight:700;margin-bottom:4px;line-height:1}
.hlogo .b{color:#8ab4f8}.hlogo .o{color:#f28b82}.hlogo .n{color:#fdd663}
.hlogo .g{color:#81c995}.hlogo .d2{color:#f28b82}.hlogo .e2{color:#fdd663}.hlogo .v2{color:#81c995}
.hsub{font-size:11px;color:var(--text2);letter-spacing:2px;margin-bottom:8px}
.mbadge{display:inline-flex;align-items:center;gap:4px;padding:3px 11px;
  border-radius:18px;font-size:10px;font-weight:500;margin-bottom:14px}
.m18{background:rgba(242,139,130,.1);border:1px solid rgba(242,139,130,.25);color:var(--red)}
.msf{background:rgba(129,201,149,.08);border:1px solid rgba(129,201,149,.2);color:var(--green)}
.hidden{display:none!important}
.hgreet{font-size:13px;color:var(--text2);margin-bottom:16px;text-align:center}
.hgreet b{color:var(--blue)}
.hsw{width:100%;max-width:580px;margin-bottom:12px}
.hsb{display:flex;align-items:center;gap:10px;height:48px;background:var(--urlbar);
  border:1px solid var(--bg3);border-radius:24px;padding:0 14px;transition:all .25s}
.hsb:focus-within{background:#fff;border-color:transparent;box-shadow:0 2px 10px rgba(0,0,0,.4)}
.hsb input{flex:1;background:none;border:none;outline:none;color:var(--text);font-size:15px}
.hsb:focus-within input{color:#202124}
.hsb input::placeholder{color:var(--text3)}
.sgbtn{background:var(--blue2);border:none;border-radius:18px;cursor:pointer;
  padding:7px 15px;font-family:'Google Sans',sans-serif;font-size:12px;font-weight:500;color:#fff}
.erow{display:flex;gap:5px;flex-wrap:wrap;justify-content:center;max-width:580px;margin-bottom:20px}
.ec{padding:4px 11px;border-radius:14px;border:1px solid var(--bg3);font-size:10px;
  font-weight:500;cursor:pointer;color:var(--text2);transition:all .15s;background:none}
.ec.on{background:rgba(138,180,248,.1);color:var(--blue);border-color:rgba(138,180,248,.35)}
.ec.a{color:var(--red);border-color:rgba(242,139,130,.2)}
.ec.a.on{background:rgba(242,139,130,.1);border-color:rgba(242,139,130,.4)}
.ec.lk{color:var(--text3);border-color:var(--bg3);cursor:not-allowed}
.sgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;width:100%;max-width:580px;margin-bottom:20px}
@media(max-width:360px){.sgrid{grid-template-columns:repeat(3,1fr)}}
.scut{display:flex;flex-direction:column;align-items:center;gap:6px;padding:12px 4px;
  border-radius:12px;cursor:pointer;transition:all .2s;border:1px solid transparent}
.scut:hover{background:var(--hover);border-color:var(--bg3)}
.scut:active{transform:scale(.95)}
.scico{width:50px;height:50px;border-radius:14px;display:flex;align-items:center;
  justify-content:center;font-size:20px;box-shadow:0 2px 8px rgba(0,0,0,.4)}
.sclbl{font-size:10px;color:var(--text2);font-weight:400;text-align:center}
.sc18{display:none}.sc18.show{display:flex}
.hwm{font-size:9px;color:var(--text3);letter-spacing:1px}

/* ADMIN */
#admin-scr{display:none;flex-direction:column;height:100%;background:var(--bg)}
#admin-scr.show{display:flex}
.admin-hdr{background:linear-gradient(135deg,#1e1b4b,#2e1065);
  padding:16px 20px;padding-top:calc(16px + var(--st));
  display:flex;align-items:center;justify-content:space-between;flex-shrink:0;
  border-bottom:1px solid rgba(192,132,252,.3)}
.admin-title{font-family:'Google Sans',sans-serif;font-size:16px;font-weight:700;color:var(--purple)}
.admin-lo-btn{background:rgba(242,139,130,.15);border:1px solid rgba(242,139,130,.3);
  color:var(--red);border-radius:8px;padding:6px 12px;cursor:pointer;font-size:12px;font-weight:600}
.admin-body{flex:1;overflow-y:auto;padding:16px}
.a-section{margin-bottom:16px}
.a-sec-title{font-size:10px;font-weight:600;color:var(--text2);letter-spacing:2px;
  text-transform:uppercase;margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid var(--bg3)}
.a-stats{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:4px}
.stat-card{background:var(--bg1);border:1px solid var(--bg3);border-radius:12px;padding:14px;text-align:center}
.stat-num{font-size:28px;font-weight:700;color:var(--blue);font-family:'Google Sans',sans-serif}
.stat-lbl{font-size:11px;color:var(--text2);margin-top:4px}
.a-actions{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:4px}
.a-act{padding:12px;border-radius:10px;border:1px solid var(--bg3);background:var(--bg1);
  cursor:pointer;text-align:center;transition:all .15s}
.a-act:hover{background:var(--hover)}
.a-act-ico{font-size:22px;margin-bottom:4px}
.a-act-lbl{font-size:11px;color:var(--text2);font-weight:500}

/* Visibility toggle */
.vis-box{background:var(--bg1);border:1px solid var(--bg3);border-radius:10px;
  padding:14px;margin-bottom:12px;display:flex;align-items:center;justify-content:space-between}
.vis-info .vis-lbl{font-size:13px;color:var(--text);font-weight:500}
.vis-info .vis-sub{font-size:10px;color:var(--text2);margin-top:3px}
.toggle{width:46px;height:26px;border-radius:13px;border:none;cursor:pointer;
  position:relative;transition:background .2s;flex-shrink:0}
.toggle.on{background:var(--blue2)}
.toggle.off{background:var(--bg3)}
.toggle::after{content:'';position:absolute;top:3px;left:3px;width:20px;height:20px;
  border-radius:50%;background:#fff;transition:transform .2s;box-shadow:0 1px 4px rgba(0,0,0,.3)}
.toggle.on::after{transform:translateX(20px)}

.user-card{background:var(--bg1);border:1px solid var(--bg3);border-radius:10px;
  padding:12px 14px;margin-bottom:8px;display:flex;align-items:center;gap:10px}
.u-av{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--blue2),#0d47a1);
  display:flex;align-items:center;justify-content:center;color:#fff;font-size:14px;font-weight:700;flex-shrink:0}
.u-info{flex:1;min-width:0}
.u-name{font-size:13px;font-weight:600;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.u-email{font-size:10px;color:var(--text2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.u-tags{display:flex;gap:5px;margin-top:4px;flex-wrap:wrap}
.utag{font-size:9px;padding:2px 7px;border-radius:10px;font-weight:600}
.tag18{background:rgba(242,139,130,.12);color:var(--red);border:1px solid rgba(242,139,130,.25)}
.tagsf{background:rgba(129,201,149,.1);color:var(--green);border:1px solid rgba(129,201,149,.2)}
.tagbn{background:rgba(248,113,113,.15);color:#ff4444;border:1px solid rgba(248,113,113,.4)}
.u-btns{display:flex;gap:5px;flex-shrink:0}
.ubtn{background:none;border:1px solid var(--bg3);border-radius:6px;cursor:pointer;
  color:var(--text2);font-size:11px;padding:4px 8px;transition:all .15s}
.ubtn.ban:hover{background:rgba(242,139,130,.15);color:var(--red);border-color:rgba(242,139,130,.4)}
.ubtn.unban{background:rgba(129,201,149,.1);color:var(--green);border-color:rgba(129,201,149,.3)}
.ubtn.del:hover{background:rgba(242,139,130,.2);color:var(--red)}
.a-search{width:100%;background:var(--urlbar);border:1px solid var(--bg3);border-radius:8px;
  padding:10px 14px;color:var(--text);font-size:13px;outline:none;margin-bottom:12px}
.a-search:focus{border-color:var(--purple)}
.a-search::placeholder{color:var(--text3)}

/* PANELS */
.po{position:fixed;inset:0;z-index:400;background:rgba(0,0,0,.6);display:none;align-items:flex-end}
.po.op{display:flex}
.pn{background:var(--bg1);border-radius:16px 16px 0 0;border:1px solid var(--bg3);
  border-bottom:none;padding:10px 0 18px;width:100%;max-height:80vh;overflow-y:auto;
  animation:su .25s ease both}
@keyframes su{from{transform:translateY(100%)}to{transform:translateY(0)}}
.ph{width:30px;height:3px;background:var(--bg3);border-radius:2px;margin:0 auto 12px;cursor:pointer}
.ptitle{font-size:13px;font-weight:500;color:var(--text);padding:8px 18px 10px;
  border-bottom:1px solid var(--bg3);display:flex;justify-content:space-between;align-items:center;
  font-family:'Google Sans',sans-serif}
.mi{display:flex;align-items:center;gap:13px;padding:12px 18px;cursor:pointer;
  color:var(--text);font-size:14px;transition:background .12s}
.mi:hover{background:var(--hover)}
.mico{font-size:18px;width:24px;text-align:center;color:var(--text2)}
.mdiv{height:1px;background:var(--bg3);margin:3px 0}
.li{display:flex;align-items:center;gap:12px;padding:10px 18px;cursor:pointer;transition:background .12s}
.li:hover{background:var(--hover)}
.lico{font-size:16px;flex-shrink:0;color:var(--text2)}
.linf{flex:1;min-width:0}
.lit{font-size:13px;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.lis{font-size:11px;color:var(--text2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px}
.ldel{background:none;border:none;color:var(--text2);cursor:pointer;font-size:16px;padding:4px 6px;border-radius:50%}
.lem{text-align:center;color:var(--text2);font-size:13px;padding:24px}

/* BOTTOM NAV */
#bnav{background:var(--bg2);border-top:1px solid var(--bg3);flex-shrink:0;padding-bottom:var(--sb)}
.bni{display:flex;justify-content:space-around;padding:4px 0}
.bb{display:flex;flex-direction:column;align-items:center;gap:2px;padding:6px 12px;
  cursor:pointer;color:var(--text2);background:none;border:none;font-size:9px;font-weight:500;
  border-radius:9px;transition:all .15s}
.bb:active,.bb.on{color:var(--blue);background:rgba(138,180,248,.1)}
.bico{font-size:20px;line-height:1}

#toast{position:fixed;bottom:78px;left:50%;transform:translateX(-50%) translateY(8px);
  background:var(--bg3);color:var(--text);padding:10px 18px;border-radius:8px;font-size:13px;
  z-index:9999;opacity:0;transition:all .25s;pointer-events:none;white-space:nowrap;
  max-width:88vw;text-align:center;box-shadow:0 4px 14px rgba(0,0,0,.4)}
#toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
</style>
</head>
<body>

<!-- AUTH -->
<div id="auth-scr">
 <div class="acard">
  <div class="logo-row">
   <div class="logo-ico">B</div>
   <div class="logo-txt">Bong Browser</div>
  </div>
  <div class="logo-sub">Modified by Bong.Dev ⚡</div>
  <div class="atabs">
   <button class="atab on" id="tab-l" onclick="showLogin()">Login</button>
   <button class="atab" id="tab-r" onclick="showRegister()">Register</button>
  </div>

  <!-- LOGIN -->
  <div class="fp on" id="fp-l">
   <div class="fg"><label class="fl">Gmail Address</label>
    <input class="fi" id="le" type="email" placeholder="yourname@gmail.com" autocomplete="email"></div>
   <div class="fg"><label class="fl">Password</label>
    <input class="fi" id="lp" type="password" placeholder="••••••••" onkeydown="if(event.key==='Enter')doLogin()"></div>
   <div class="forgot-link"><a onclick="openReset()">🔑 Password ভুলে গেছেন?</a></div>
   <div class="amsg" id="lm"></div>
   <button class="abtn abtn-p" onclick="doLogin()">Login</button>
   <div class="divider"><div class="divider-line"></div><span class="divider-text">অথবা</span><div class="divider-line"></div></div>
   <a href="/auth/google" class="g-btn">
    <svg width="18" height="18" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
    Continue with Google Account
   </a>
  </div>

  <!-- REGISTER -->
  <div class="fp" id="fp-r" style="display:none">
   <div class="fg"><label class="fl">পুরো নাম</label>
    <input class="fi" id="rn" type="text" placeholder="আপনার নাম"></div>
   <div class="fg"><label class="fl">Gmail Address</label>
    <input class="fi" id="re" type="email" placeholder="yourname@gmail.com"></div>
   <div class="fg">
    <label class="fl">🎂 জন্ম তারিখ (বয়স যাচাই হবে)</label>
    <div class="dob-row">
     <select class="fi" id="r-day">
      <option value="">দিন</option>
     </select>
     <select class="fi" id="r-month">
      <option value="">মাস</option>
      <option value="01">জানুয়ারি</option><option value="02">ফেব্রুয়ারি</option>
      <option value="03">মার্চ</option><option value="04">এপ্রিল</option>
      <option value="05">মে</option><option value="06">জুন</option>
      <option value="07">জুলাই</option><option value="08">আগস্ট</option>
      <option value="09">সেপ্টেম্বর</option><option value="10">অক্টোবর</option>
      <option value="11">নভেম্বর</option><option value="12">ডিসেম্বর</option>
     </select>
     <select class="fi" id="r-year">
      <option value="">বছর</option>
     </select>
    </div>
   </div>
   <div class="fg"><label class="fl">Password (কমপক্ষে ৬ অক্ষর)</label>
    <input class="fi" id="rp" type="password" placeholder="••••••••" onkeydown="if(event.key==='Enter')doReg()"></div>
   <div class="amsg" id="rm"></div>
   <button class="abtn abtn-s" onclick="doReg()">Register</button>
   <div class="divider"><div class="divider-line"></div><span class="divider-text">অথবা</span><div class="divider-line"></div></div>
   <a href="/auth/google" class="g-btn">
    <svg width="18" height="18" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
    Continue with Google Account
   </a>
  </div>
  <div class="afoot">🔒 ডেটা সুরক্ষিত · <span>Modified by Bong.Dev</span></div>
 </div>
</div>

<!-- RESET PANEL -->
<div id="reset-panel">
 <div class="reset-card">
  <div style="font-size:17px;font-weight:700;color:var(--text);margin-bottom:4px;font-family:'Google Sans',sans-serif">🔑 Password Reset</div>
  <div style="font-size:12px;color:var(--text2);margin-bottom:18px">Gmail দিয়ে নতুন Password সেট করুন</div>
  <div class="rstep on" id="rs1">
   <div class="fg"><label class="fl">Gmail Address</label>
    <input class="fi" id="re2" type="email" placeholder="yourname@gmail.com"></div>
   <div class="amsg" id="rs1m"></div>
   <button class="abtn abtn-p" onclick="verifyEmail()" style="margin-bottom:8px">পরবর্তী →</button>
   <button class="abtn abtn-o" onclick="closeReset()">বাতিল</button>
  </div>
  <div class="rstep" id="rs2">
   <div style="background:rgba(129,201,149,.1);border:1px solid rgba(129,201,149,.3);border-radius:8px;padding:10px;margin-bottom:14px;font-size:12px;color:var(--green)">✅ Email যাচাই হয়েছে!</div>
   <div class="fg"><label class="fl">নতুন Password</label>
    <input class="fi" id="np1" type="password" placeholder="নতুন Password"></div>
   <div class="fg"><label class="fl">আবার দিন</label>
    <input class="fi" id="np2" type="password" placeholder="আবার একই Password"></div>
   <div class="amsg" id="rs2m"></div>
   <button class="abtn abtn-p" onclick="doReset()" style="margin-bottom:8px">✅ Password বদলান</button>
   <button class="abtn abtn-o" onclick="closeReset()">বাতিল</button>
  </div>
  <div class="rstep" id="rs3">
   <div style="text-align:center;padding:16px 0">
    <div style="font-size:48px;margin-bottom:12px">🎉</div>
    <div style="font-size:15px;font-weight:600;color:var(--green);margin-bottom:8px">সফল!</div>
    <div style="font-size:12px;color:var(--text2);margin-bottom:18px">নতুন Password দিয়ে Login করুন।</div>
   </div>
   <button class="abtn abtn-p" onclick="closeReset()">✅ Login করুন</button>
  </div>
 </div>
</div>

<!-- BROWSER -->
<div id="bscr">
 <div id="inst-bar">
  <div class="ib-t">📱 Bong Browser — Home Screen এ Install করুন!</div>
  <button class="ib-b" id="inst-btn">Install</button>
  <button class="ib-c" onclick="document.getElementById('inst-bar').classList.remove('show')">✕</button>
 </div>
 <div id="tab-bar">
  <div class="tab active" id="tab-0">
   <span class="tab-fav">🏠</span><span class="tab-t" id="tt-0">New Tab</span>
   <button class="tab-x" onclick="closeTab(event,0)">✕</button>
  </div>
  <button class="ntab-btn" onclick="openNewTab()">+</button>
 </div>
 <div id="toolbar">
  <button class="nb" id="btn-bk" onclick="goBack()" disabled>
   <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
  </button>
  <button class="nb" id="btn-fw" onclick="goFwd()" disabled>
   <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
  </button>
  <button class="nb" onclick="reloadPage()">
   <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
  </button>
  <button class="nb" onclick="goHome()">
   <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
  </button>
  <div id="uw">
   <span id="lk">🔒</span>
   <input id="ub" type="url" inputmode="url" placeholder="Search or type a URL" onkeydown="if(event.key==='Enter')navBar()">
   <button class="ustar" id="starBtn" onclick="addBk()">☆</button>
  </div>
  <div class="rtools">
   <button class="tb2" onclick="openDL()">⬇</button>
   <div class="profbtn" id="profbtn" onclick="showMenu()">B</div>
   <button class="tb2" onclick="showMenu()">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="19" r="1.5"/></svg>
   </button>
  </div>
 </div>
 <div id="bkbar">
  <button class="bki" onclick="go('https://www.google.com')">G Google</button>
  <div class="bksep"></div>
  <button class="bki" onclick="go('https://www.youtube.com')">▶ YouTube</button>
  <div class="bksep"></div>
  <button class="bki" onclick="go('https://www.facebook.com')">f Facebook</button>
  <div class="bksep"></div>
  <button class="bki" onclick="go('https://web.whatsapp.com')">💬 WhatsApp</button>
  <div class="bksep"></div>
  <button class="bki" onclick="go('https://www.instagram.com')">📸 Instagram</button>
  <div class="bksep" id="ubksep" style="display:none"></div>
  <div id="ubk"></div>
 </div>
 <div id="ct">
  <div id="hp">
   <div class="hlogo"><span class="b">B</span><span class="o">o</span><span class="n">n</span><span class="g">g</span><span style="color:#9aa0a6">.</span><span class="d2">D</span><span class="e2">e</span><span class="v2">v</span></div>
   <div class="hsub">Modified by Bong.Dev · v11.0</div>
   <div class="mbadge m18 hidden" id="b18">🔞 18+ Mode Active</div>
   <div class="mbadge msf hidden" id="bsf">🔒 Safe Mode</div>
   <p class="hgreet hidden" id="hgreet"></p>
   <div class="hsw">
    <div class="hsb">
     <span style="font-size:17px;color:var(--text2)">🔍</span>
     <input id="sq" type="search" placeholder="Search or type a URL" onkeydown="if(event.key==='Enter')hSearch()">
     <button class="sgbtn" onclick="hSearch()">Search</button>
    </div>
   </div>
   <div class="erow" id="erow">
    <button class="ec on" data-e="google" onclick="setEng(this)">🔍 Google</button>
    <button class="ec" data-e="bing" onclick="setEng(this)">🅱 Bing</button>
    <button class="ec" data-e="ddg" onclick="setEng(this)">🦆 DDG</button>
    <button class="ec" data-e="yahoo" onclick="setEng(this)">Y! Yahoo</button>
   </div>
   <div class="sgrid">
    <div class="scut" onclick="go('https://www.youtube.com')"><div class="scico" style="background:linear-gradient(135deg,#f00,#900)">▶</div><div class="sclbl">YouTube</div></div>
    <div class="scut" onclick="go('https://www.google.com')"><div class="scico" style="background:linear-gradient(135deg,#4285f4,#34a853)">G</div><div class="sclbl">Google</div></div>
    <div class="scut" onclick="go('https://www.facebook.com')"><div class="scico" style="background:linear-gradient(135deg,#1877f2,#0d5dbf)">f</div><div class="sclbl">Facebook</div></div>
    <div class="scut" onclick="go('https://www.instagram.com')"><div class="scico" style="background:linear-gradient(135deg,#f09433,#dc2743,#cc2366)">📷</div><div class="sclbl">Instagram</div></div>
    <div class="scut" onclick="go('https://twitter.com')"><div class="scico" style="background:linear-gradient(135deg,#000,#333)">𝕏</div><div class="sclbl">Twitter/X</div></div>
    <div class="scut" onclick="go('https://web.whatsapp.com')"><div class="scico" style="background:linear-gradient(135deg,#25d366,#128c7e)">💬</div><div class="sclbl">WhatsApp</div></div>
    <div class="scut" onclick="go('https://www.tiktok.com')"><div class="scico" style="background:linear-gradient(135deg,#010101,#ff0050)">♪</div><div class="sclbl">TikTok</div></div>
    <div class="scut" onclick="go('https://t.me')"><div class="scico" style="background:linear-gradient(135deg,#2ca5e0,#1a7ab5)">✈</div><div class="sclbl">Telegram</div></div>
    <div class="scut" onclick="go('https://www.netflix.com')"><div class="scico" style="background:linear-gradient(135deg,#e50914,#700)">N</div><div class="sclbl">Netflix</div></div>
    <div class="scut" onclick="go('https://reddit.com')"><div class="scico" style="background:linear-gradient(135deg,#ff4500,#c30)">r/</div><div class="sclbl">Reddit</div></div>
    <div class="scut" onclick="go('https://github.com')"><div class="scico" style="background:linear-gradient(135deg,#24292e,#555)">🐙</div><div class="sclbl">GitHub</div></div>
    <div class="scut" onclick="go('https://www.amazon.in')"><div class="scico" style="background:linear-gradient(135deg,#ff9900,#c70)">a</div><div class="sclbl">Amazon</div></div>
    <div class="scut sc18" onclick="go('https://www.xvideos.com')"><div class="scico" style="background:linear-gradient(135deg,#c00,#900)">🔴</div><div class="sclbl">XVideos</div></div>
    <div class="scut sc18" onclick="go('https://www.xnxx.com')"><div class="scico" style="background:linear-gradient(135deg,#c50,#930)">🟠</div><div class="sclbl">XNXX</div></div>
    <div class="scut sc18" onclick="go('https://www.pornhub.com')"><div class="scico" style="background:linear-gradient(135deg,#ff9000,#c60)">🟧</div><div class="sclbl">PornHub</div></div>
    <div class="scut sc18" onclick="go('https://yandex.com')"><div class="scico" style="background:linear-gradient(135deg,#c00,#900)">Y</div><div class="sclbl">Yandex</div></div>
   </div>
   <div class="hwm">⚡ Modified by Bong.Dev · v11.0</div>
  </div>
 </div>
 <div id="bnav">
  <div class="bni">
   <button class="bb" onclick="goBack()"><div class="bico">◀</div>Back</button>
   <button class="bb" onclick="goFwd()"><div class="bico">▶</div>Forward</button>
   <button class="bb on" onclick="goHome()"><div class="bico">⌂</div>Home</button>
   <button class="bb" onclick="openHist()"><div class="bico">📋</div>History</button>
   <button class="bb" onclick="showMenu()"><div class="bico">⋮</div>More</button>
  </div>
 </div>
</div>

<!-- ADMIN -->
<div id="admin-scr">
 <div class="admin-hdr">
  <div class="admin-title">⚙️ Admin Panel — Bong.Dev</div>
  <button class="admin-lo-btn" onclick="doLogout()">🚪 Logout</button>
 </div>
 <div class="admin-body">

  <!-- Visibility Toggle -->
  <div class="a-section">
   <div class="a-sec-title">🔒 Admin Panel দৃশ্যমানতা</div>
   <div class="vis-box">
    <div class="vis-info">
     <div class="vis-lbl">Admin Panel কে দেখবে?</div>
     <div class="vis-sub" id="vis-sub">শুধু আমি দেখব (Only Me)</div>
    </div>
    <button class="toggle on" id="vis-toggle" onclick="toggleVis()"></button>
   </div>
  </div>

  <!-- Stats -->
  <div class="a-section">
   <div class="a-sec-title">📊 Statistics</div>
   <div class="a-stats">
    <div class="stat-card"><div class="stat-num" id="s-total">0</div><div class="stat-lbl">মোট User</div></div>
    <div class="stat-card"><div class="stat-num" id="s-18" style="color:var(--red)">0</div><div class="stat-lbl">18+ User</div></div>
    <div class="stat-card"><div class="stat-num" id="s-safe" style="color:var(--green)">0</div><div class="stat-lbl">Safe Mode</div></div>
    <div class="stat-card"><div class="stat-num" id="s-banned" style="color:var(--gold)">0</div><div class="stat-lbl">Banned</div></div>
   </div>
  </div>

  <!-- Actions -->
  <div class="a-section">
   <div class="a-sec-title">⚡ Quick Actions</div>
   <div class="a-actions">
    <div class="a-act" onclick="loadUsers()"><div class="a-act-ico">👥</div><div class="a-act-lbl">সব User</div></div>
    <div class="a-act" onclick="loadBanned()"><div class="a-act-ico">🚫</div><div class="a-act-lbl">Banned</div></div>
    <div class="a-act" onclick="clearAllHist()"><div class="a-act-ico">🗑</div><div class="a-act-lbl">History Clear</div></div>
    <div class="a-act" onclick="loadUsers18()"><div class="a-act-ico">🔞</div><div class="a-act-lbl">18+ Users</div></div>
   </div>
  </div>

  <!-- User list -->
  <div class="a-section">
   <div class="a-sec-title">👥 Users</div>
   <input class="a-search" placeholder="🔍 নাম বা Email খুঁজুন..." oninput="filterUsers(this.value)">
   <div id="ulist"><div class="lem">উপরে ক্লিক করুন</div></div>
  </div>
 </div>
</div>

<!-- MENU -->
<div class="po" id="pMenu" onclick="cp('pMenu')">
 <div class="pn" onclick="event.stopPropagation()">
  <div class="ph" onclick="cp('pMenu')"></div>
  <div class="ptitle">Bong Browser <span style="font-size:10px;color:var(--text2)">v11.0 · Bong.Dev</span></div>
  <div class="mi" onclick="openNewTab();cp('pMenu')"><span class="mico">📄</span>New tab</div>
  <div class="mdiv"></div>
  <div class="mi" onclick="openDL()"><span class="mico">⬇</span>Downloads</div>
  <div class="mi" onclick="openHist()"><span class="mico">📋</span>History</div>
  <div class="mi" onclick="openBks()"><span class="mico">☆</span>Bookmarks</div>
  <div class="mi" onclick="addBk()"><span class="mico">★</span>Bookmark this page</div>
  <div class="mdiv"></div>
  <div class="mi" onclick="zoomIn()"><span class="mico">🔍</span>Zoom in</div>
  <div class="mi" onclick="zoomOut()"><span class="mico">🔎</span>Zoom out</div>
  <div class="mdiv"></div>
  <div class="mi" onclick="openChgPwd()"><span class="mico">🔑</span>Password বদলান</div>
  <div class="mi" onclick="showUI()"><span class="mico">👤</span>Account info</div>
  <div class="mdiv"></div>
  <div class="mi" onclick="doLogout()" style="color:var(--red)"><span class="mico">🚪</span>Logout</div>
 </div>
</div>

<!-- HISTORY -->
<div class="po" id="pHist" onclick="cp('pHist')">
 <div class="pn" onclick="event.stopPropagation()">
  <div class="ph" onclick="cp('pHist')"></div>
  <div class="ptitle">History
   <button onclick="clearHist()" style="background:rgba(242,139,130,.12);border:1px solid rgba(242,139,130,.3);color:var(--red);border-radius:6px;padding:3px 10px;cursor:pointer;font-size:11px">Clear</button>
  </div>
  <div id="histList"></div>
 </div>
</div>

<!-- BOOKMARKS -->
<div class="po" id="pBks" onclick="cp('pBks')">
 <div class="pn" onclick="event.stopPropagation()">
  <div class="ph" onclick="cp('pBks')"></div>
  <div class="ptitle">Bookmarks</div>
  <div id="bkList"></div>
 </div>
</div>

<!-- DOWNLOADS -->
<div class="po" id="pDL" onclick="cp('pDL')">
 <div class="pn" onclick="event.stopPropagation()">
  <div class="ph" onclick="cp('pDL')"></div>
  <div class="ptitle">⬇ Downloads
   <button onclick="clearDL()" style="background:rgba(242,139,130,.12);border:1px solid rgba(242,139,130,.3);color:var(--red);border-radius:6px;padding:3px 10px;cursor:pointer;font-size:11px">🗑</button>
  </div>
  <div style="padding:12px 18px;border-bottom:1px solid var(--bg3)">
   <div style="display:flex;gap:8px;margin-bottom:8px">
    <input id="dl-url" type="url" placeholder="Download link paste করুন..."
     style="flex:1;background:var(--urlbar);border:1px solid var(--bg3);border-radius:8px;padding:9px 12px;color:var(--text);font-size:12px;outline:none">
    <button onclick="startDL()" style="background:var(--blue2);border:none;border-radius:8px;padding:9px 14px;color:#fff;cursor:pointer;font-size:13px;font-weight:600">⬇</button>
   </div>
   <div style="display:flex;gap:8px">
    <button onclick="dlClipboard()" style="background:var(--bg3);border:none;border-radius:8px;padding:7px 12px;color:var(--text);cursor:pointer;font-size:11px">📋 Clipboard</button>
    <button onclick="shareURL()" style="background:var(--bg3);border:none;border-radius:8px;padding:7px 12px;color:var(--text);cursor:pointer;font-size:11px">📤 Share</button>
   </div>
  </div>
  <div id="dl-list"></div>
 </div>
</div>

<!-- CHANGE PASSWORD -->
<div class="po" id="pChgPwd" onclick="cp('pChgPwd')">
 <div class="pn" onclick="event.stopPropagation()">
  <div class="ph" onclick="cp('pChgPwd')"></div>
  <div class="ptitle">🔑 Password বদলান</div>
  <div style="padding:12px 18px">
   <div class="fg"><label class="fl">পুরনো Password</label>
    <input class="fi" id="cp-old" type="password" placeholder="পুরনো Password"></div>
   <div class="fg"><label class="fl">নতুন Password</label>
    <input class="fi" id="cp-new" type="password" placeholder="নতুন Password"></div>
   <div class="fg"><label class="fl">নতুন Password আবার দিন</label>
    <input class="fi" id="cp-new2" type="password" placeholder="আবার একই Password"></div>
   <div class="amsg" id="cp-msg"></div>
   <button onclick="doChgPwd()" style="width:100%;padding:12px;border:none;border-radius:8px;cursor:pointer;font-family:'Google Sans',sans-serif;font-size:14px;font-weight:500;background:var(--blue2);color:#fff;margin-top:4px">✅ Password বদলান</button>
  </div>
 </div>
</div>

<div id="toast"></div>

<script>
var U=null,eng="google",zoom=1,fh=[],fi=-1,tc=1,dp=null,allU=[],visMode="only_me";

var E={
 google:q=>"https://www.google.com/search?q="+encodeURIComponent(q)+"&safe=off",
 bing:q=>"https://www.bing.com/search?q="+encodeURIComponent(q)+"&adlt=off",
 ddg:q=>"https://duckduckgo.com/?q="+encodeURIComponent(q)+"&kp=-2",
 yahoo:q=>"https://search.yahoo.com/search?p="+encodeURIComponent(q),
 xvideos:q=>"https://www.xvideos.com/?k="+encodeURIComponent(q),
 xnxx:q=>"https://www.xnxx.com/search/"+encodeURIComponent(q),
 pornhub:q=>"https://www.pornhub.com/video/search?search="+encodeURIComponent(q),
 yandex:q=>"https://yandex.com/search/?text="+encodeURIComponent(q)
};

// DOB dropdowns
(function(){
 var d=document.getElementById("r-day");
 for(var i=1;i<=31;i++){var o=document.createElement("option");o.value=String(i).padStart(2,'0');o.textContent=i+" দিন";d.appendChild(o);}
 var y=document.getElementById("r-year");
 var cur=new Date().getFullYear();
 for(var yr=cur;yr>=1940;yr--){var o=document.createElement("option");o.value=yr;o.textContent=yr+" সাল";y.appendChild(o);}
})();

// PWA install
window.addEventListener('beforeinstallprompt',e=>{
 e.preventDefault();dp=e;
 document.getElementById('inst-bar').classList.add('show');
});
document.getElementById('inst-btn').addEventListener('click',async()=>{
 if(dp){dp.prompt();const{outcome}=await dp.userChoice;
  if(outcome==='accepted')toast('✅ Installed!');dp=null;
  document.getElementById('inst-bar').classList.remove('show');}
});

async function init(){
 var p=new URLSearchParams(window.location.search);
 if(p.get('logged')||p.get('error')){
  window.history.replaceState({},'','/');
  if(p.get('error')==='banned'){sm('lm','🚫 আপনার account ban করা হয়েছে','e');}
 }
 const r=await fetch("/api/me").then(x=>x.json()).catch(()=>({logged:false}));
 if(r.logged){U=r;showB(r.is_admin);}
 if("serviceWorker"in navigator)navigator.serviceWorker.register("/sw.js").catch(()=>{});
}

function showLogin(){
 document.getElementById("tab-l").className="atab on";
 document.getElementById("tab-r").className="atab";
 document.getElementById("fp-l").style.display="block";
 document.getElementById("fp-r").style.display="none";
}
function showRegister(){
 document.getElementById("tab-l").className="atab";
 document.getElementById("tab-r").className="atab on";
 document.getElementById("fp-l").style.display="none";
 document.getElementById("fp-r").style.display="block";
}
function stab(t){if(t==="l")showLogin();else showRegister();}

async function doLogin(){
 var e=document.getElementById("le").value.trim();
 var p=document.getElementById("lp").value.trim();
 sm("lm","","");
 if(!e||!p){sm("lm","❗ সব ফিল্ড পূরণ করুন","e");return}
 var r=await api("/api/login",{email:e,pwd:p});
 if(r.ok){U=r;showB(r.is_admin);toast(r.is_admin?"⚙️ Admin Panel এ স্বাগতম!":"✅ Welcome "+r.name+"!");}
 else sm("lm",r.msg,"e");
}

async function doReg(){
 var n=document.getElementById("rn").value.trim();
 var e=document.getElementById("re").value.trim();
 var day=document.getElementById("r-day").value;
 var month=document.getElementById("r-month").value;
 var year=document.getElementById("r-year").value;
 var p=document.getElementById("rp").value.trim();
 sm("rm","","");
 if(!n||!e||!day||!month||!year||!p){sm("rm","❗ সব ফিল্ড পূরণ করুন","e");return}
 var dob=year+"-"+month+"-"+day;
 var r=await api("/api/register",{name:n,email:e,dob:dob,pwd:p});
 sm("rm",r.msg,r.ok?(r.is18?"ok":"w"):"e");
 if(r.ok){stab("l");document.getElementById("le").value=e;}
}

async function doLogout(){
 await api("/api/logout",{});U=null;
 hideAll();document.getElementById("auth-scr").style.display="flex";
 cap();toast("Signed out");
}

function showB(isAdmin){
 hideAll();
 if(isAdmin){
  document.getElementById("admin-scr").classList.add("show");
  loadStats();loadUsers();
 }else{
  document.getElementById("bscr").classList.add("show");
  updateUI();loadUBks();
 }
}

function hideAll(){
 document.getElementById("bscr").classList.remove("show");
 document.getElementById("admin-scr").classList.remove("show");
 document.getElementById("auth-scr").style.display="none";
}

function updateUI(){
 if(!U)return;
 var is18=U.is18;
 document.getElementById("b18").classList.toggle("hidden",!is18);
 document.getElementById("bsf").classList.toggle("hidden",!!is18);
 var hg=document.getElementById("hgreet");
 hg.innerHTML="Welcome, <b>"+U.name+"</b>! "+(is18?"🔞 18+ Mode active":"🔒 Safe Mode");
 hg.classList.remove("hidden");
 var row=document.getElementById("erow");
 row.querySelectorAll(".ec.a,.ec.lk").forEach(x=>x.remove());
 if(is18){
  [["xvideos","🔴 XVideos"],["xnxx","🟠 XNXX"],["pornhub","🟧 PornHub"],["yandex","🟡 Yandex"]].forEach(([e,l])=>{
   var b=document.createElement("button");b.className="ec a";b.dataset.e=e;b.textContent=l;
   b.onclick=()=>setEng(b);row.appendChild(b);
  });
  document.querySelectorAll(".sc18").forEach(x=>x.classList.add("show"));
 }else{
  ["🔒 XVideos","🔒 Adult"].forEach(l=>{
   var b=document.createElement("button");b.className="ec lk";b.textContent=l;row.appendChild(b);
  });
 }
 var pb=document.getElementById("profbtn");
 if(pb&&U.name)pb.textContent=U.name[0].toUpperCase();
}

// Admin visibility toggle
function toggleVis(){
 visMode=visMode==="only_me"?"everyone":"only_me";
 var btn=document.getElementById("vis-toggle");
 var sub=document.getElementById("vis-sub");
 if(visMode==="only_me"){
  btn.className="toggle on";
  sub.textContent="শুধু আমি দেখব (Only Me)";
  toast("🔒 Admin Panel: Only You");
 }else{
  btn.className="toggle off";
  sub.textContent="সবাই দেখতে পাবে (Everyone)";
  toast("⚠️ Admin Panel: Everyone can see");
 }
}

async function loadStats(){
 var r=await fetch("/api/admin/stats").then(x=>x.json()).catch(()=>({}));
 document.getElementById("s-total").textContent=r.total||0;
 document.getElementById("s-18").textContent=r.is18||0;
 document.getElementById("s-safe").textContent=r.safe||0;
 document.getElementById("s-banned").textContent=r.banned||0;
}

async function loadUsers(){
 var rows=await fetch("/api/admin/users").then(x=>x.json()).catch(()=>[]);
 allU=rows;renderUsers(rows);
}

async function loadBanned(){
 var rows=await fetch("/api/admin/users").then(x=>x.json()).catch(()=>[]);
 renderUsers(rows.filter(u=>u.is_banned));
}

async function loadUsers18(){
 var rows=await fetch("/api/admin/users").then(x=>x.json()).catch(()=>[]);
 renderUsers(rows.filter(u=>u.is18));
}

async function clearAllHist(){
 if(!confirm("সব user এর history মুছবে?"))return;
 await api("/api/admin/clear-all-history",{});
 toast("🗑 সব history মুছে গেছে");
}

function filterUsers(q){
 if(!q){renderUsers(allU);return;}
 renderUsers(allU.filter(u=>(u.name||"").toLowerCase().includes(q.toLowerCase())||(u.email||"").toLowerCase().includes(q.toLowerCase())));
}

function renderUsers(rows){
 var ul=document.getElementById("ulist");
 if(!rows.length){ul.innerHTML='<div class="lem">কোনো user নেই</div>';return;}
 ul.innerHTML=rows.map(u=>`
  <div class="user-card">
   <div class="u-av">${(u.name||'?')[0].toUpperCase()}</div>
   <div class="u-info">
    <div class="u-name">${u.name||'Unknown'}</div>
    <div class="u-email">${u.email}</div>
    <div class="u-tags">
     <span class="utag ${u.is18?'tag18':'tagsf'}">${u.is18?'🔞 18+':'🔒 Safe'}</span>
     ${u.is_banned?'<span class="utag tagbn">🚫 Banned</span>':''}
     <span style="font-size:9px;color:var(--text3)">Age: ${u.age||'?'}</span>
    </div>
   </div>
   <div class="u-btns">
    ${u.is_banned
     ?`<button class="ubtn unban" onclick="banU(${u.id},0)">✅</button>`
     :`<button class="ubtn ban" onclick="banU(${u.id},1)">🚫</button>`}
    <button class="ubtn del" onclick="delU(${u.id},'${u.name}')">🗑</button>
   </div>
  </div>`).join("");
}

async function banU(id,ban){
 await api("/api/admin/ban",{uid:id,ban:ban});
 toast(ban?"🚫 Banned!":"✅ Unbanned!");loadUsers();loadStats();
}

async function delU(id,name){
 if(!confirm(name+" কে delete করবেন?"))return;
 await api("/api/admin/delete-user",{uid:id});
 toast("🗑 Deleted!");loadUsers();loadStats();
}

// Reset password
var resetEmail="";
function openReset(){
 resetEmail="";
 ["re2","np1","np2"].forEach(id=>{var el=document.getElementById(id);if(el)el.value="";});
 sm("rs1m","","");sm("rs2m","","");
 showRS("rs1");document.getElementById("reset-panel").classList.add("open");
}
function closeReset(){document.getElementById("reset-panel").classList.remove("open");showRS("rs1");}
function showRS(id){document.querySelectorAll(".rstep").forEach(s=>s.classList.remove("on"));document.getElementById(id).classList.add("on");}
async function verifyEmail(){
 var e=document.getElementById("re2").value.trim().toLowerCase();
 sm("rs1m","","");if(!e){sm("rs1m","❗ Gmail দিন","e");return}
 var r=await api("/api/verify-email",{email:e});
 if(r.ok){resetEmail=e;showRS("rs2");}else sm("rs1m",r.msg,"e");
}
async function doReset(){
 var p1=document.getElementById("np1").value.trim();
 var p2=document.getElementById("np2").value.trim();
 sm("rs2m","","");
 if(!p1||!p2){sm("rs2m","❗ সব ফিল্ড পূরণ করুন","e");return}
 if(p1.length<6){sm("rs2m","❌ কমপক্ষে ৬ অক্ষর","e");return}
 if(p1!==p2){sm("rs2m","❌ Password মিলছে না","e");return}
 var r=await api("/api/reset-password",{email:resetEmail,pwd:p1});
 if(r.ok){showRS("rs3");toast("✅ Password বদলানো হয়েছে!");}
 else sm("rs2m",r.msg,"e");
}

// Change password
function openChgPwd(){cap();document.getElementById("pChgPwd").classList.add("op");}
async function doChgPwd(){
 var old=document.getElementById("cp-old").value.trim();
 var n1=document.getElementById("cp-new").value.trim();
 var n2=document.getElementById("cp-new2").value.trim();
 var msg=document.getElementById("cp-msg");
 msg.textContent="";msg.className="amsg";
 if(!old||!n1||!n2){msg.textContent="❗ সব ফিল্ড পূরণ করুন";msg.className="amsg e";return}
 if(n1!==n2){msg.textContent="❌ Password মিলছে না";msg.className="amsg e";return}
 if(n1.length<6){msg.textContent="❌ কমপক্ষে ৬ অক্ষর";msg.className="amsg e";return}
 var r=await api("/api/change-password",{old_pwd:old,new_pwd:n1});
 if(r.ok){msg.textContent="✅ সফলভাবে বদলানো হয়েছে!";msg.className="amsg ok";
  toast("✅ Password বদলানো হয়েছে!");
  setTimeout(()=>{cp("pChgPwd");["cp-old","cp-new","cp-new2"].forEach(id=>{var el=document.getElementById(id);if(el)el.value="";});msg.textContent="";},2000);
 }else{msg.textContent=r.msg;msg.className="amsg e";}
}

// Navigation
function go(url){
 if(!url)return;
 if(!url.startsWith("http"))url="https://"+url;
 if(U&&!U.is_admin)api("/api/history",{url,title:url.replace(/https?:\\/\\/(www\\.)?/,'').split('/')[0]}).catch(()=>{});
 document.getElementById("ub").value=url;
 document.getElementById("lk").textContent=url.startsWith("https")?"🔒":"⚠️";
 setTabT(url.replace(/https?:\\/\\/(www\\.)?/,'').split('/')[0]);
 fh=fh.slice(0,fi+1);fh.push(url);fi=fh.length-1;updNav();cap();
 if(window.matchMedia('(display-mode:standalone)').matches||window.matchMedia('(display-mode:fullscreen)').matches)
  window.location.href=url;
 else window.open(url,"_blank");
}
function navBar(){var t=document.getElementById("ub").value.trim();if(!t)return;
 if(/^https?:\\/\\//.test(t)||(!/ /.test(t)&&/[.\\/]/.test(t)))go(t);
 else go((E[eng]||E.google)(t));}
function hSearch(){var q=document.getElementById("sq").value.trim();if(q)go((E[eng]||E.google)(q));}
function goHome(){document.getElementById("ub").value="";document.getElementById("sq").value="";
 document.getElementById("lk").textContent="🔒";
 document.querySelectorAll(".bb").forEach((b,i)=>b.classList.toggle("on",i===2));cap();}
function goBack(){if(fi>0){fi--;go(fh[fi]);}}
function goFwd(){if(fi<fh.length-1){fi++;go(fh[fi]);}}
function reloadPage(){window.location.reload();}
function updNav(){document.getElementById("btn-bk").disabled=fi<=0;document.getElementById("btn-fw").disabled=fi>=fh.length-1;}
function setEng(el){eng=el.dataset.e;document.querySelectorAll(".ec").forEach(e=>e.classList.remove("on"));el.classList.add("on");}

// Tabs
function openNewTab(){
 var id=tc++;var bar=document.getElementById("tab-bar");var plus=bar.querySelector(".ntab-btn");
 var el=document.createElement("div");el.className="tab";el.id="tab-"+id;
 el.innerHTML=`<span class="tab-fav">🏠</span><span class="tab-t" id="tt-${id}">New Tab</span><button class="tab-x" onclick="closeTab(event,${id})">✕</button>`;
 el.onclick=()=>actTab(id);bar.insertBefore(el,plus);actTab(id);
}
function actTab(id){document.querySelectorAll(".tab").forEach(t=>t.classList.remove("active"));var el=document.getElementById("tab-"+id);if(el)el.classList.add("active");}
function closeTab(e,id){e.stopPropagation();var el=document.getElementById("tab-"+id);if(el)el.remove();}
function setTabT(t){var a=document.querySelector(".tab.active");if(a){var ti=a.querySelector(".tab-t");if(ti)ti.textContent=t.substring(0,20)||"Loading...";}}

// Bookmarks
async function addBk(){
 var url=document.getElementById("ub").value;if(!url||!U){toast("❗ Navigate first");return}
 await api("/api/bookmarks",{url,title:url.replace(/https?:\\/\\/(www\\.)?/,'').split('/')[0]});
 var s=document.getElementById("starBtn");s.textContent="★";s.style.color="var(--gold)";
 toast("★ Bookmarked!");setTimeout(()=>{s.textContent="☆";s.style.color="";},2000);loadUBks();
}
async function loadUBks(){
 var rows=await fetch("/api/bookmarks").then(x=>x.json()).catch(()=>[]);
 var c=document.getElementById("ubk"),sep=document.getElementById("ubksep");
 if(rows.length>0){sep.style.display="block";
  c.innerHTML=rows.slice(0,5).map(r=>`<button class="bki" onclick="go('${r.url}')">★ ${(r.title||r.url).substring(0,12)}</button>`).join("");}
 else{sep.style.display="none";c.innerHTML="";}
}
async function openBks(){
 cap();var rows=await fetch("/api/bookmarks").then(x=>x.json()).catch(()=>[]);
 var el=document.getElementById("bkList");
 el.innerHTML=rows.length?rows.map(r=>`<div class="li"><span class="lico">★</span><div class="linf" onclick="go('${r.url}');cp('pBks')"><div class="lit">${r.title||r.url}</div><div class="lis">${r.url}</div></div><button class="ldel" onclick="delBk(${r.id},this)">×</button></div>`).join(""):'<div class="lem">No bookmarks</div>';
 document.getElementById("pBks").classList.add("op");
}
async function delBk(id,btn){await fetch("/api/bookmarks/"+id,{method:"DELETE"});btn.closest(".li").remove();toast("Removed");loadUBks();}

// History
async function openHist(){
 cap();var rows=await fetch("/api/history").then(x=>x.json()).catch(()=>[]);
 var el=document.getElementById("histList");
 el.innerHTML=rows.length?rows.map(r=>`<div class="li" onclick="go('${r.url}');cp('pHist')"><span class="lico">🕐</span><div class="linf"><div class="lit">${r.title||r.url}</div><div class="lis">${r.ts||""}</div></div></div>`).join(""):'<div class="lem">No history</div>';
 document.getElementById("pHist").classList.add("op");
}
async function clearHist(){await api("/api/history/clear",{});document.getElementById("histList").innerHTML='<div class="lem">Cleared</div>';toast("Cleared");}

// Downloads
async function openDL(){cap();await loadDLs();document.getElementById("pDL").classList.add("op");}
async function loadDLs(){
 var rows=await fetch("/api/downloads").then(x=>x.json()).catch(()=>[]);
 var el=document.getElementById("dl-list");
 if(!rows.length){el.innerHTML='<div class="lem">📭 কোনো download নেই</div>';return;}
 el.innerHTML=rows.map(function(r){
  var n=r.filename||r.url.split('/').pop()||r.url.substring(0,25);
  return '<div style="display:flex;align-items:center;gap:10px;padding:10px 18px;border-bottom:1px solid var(--bg3)">'
   +'<span style="font-size:20px">📄</span>'
   +'<div style="flex:1;min-width:0"><div style="font-size:12px;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'+n+'</div>'
   +'<div style="font-size:10px;color:var(--text2)">'+(r.ts||'')+'</div></div>'
   +'<button onclick="reDL(\''+r.url+'\',\''+n+'\')" style="background:var(--bg3);border:none;border-radius:6px;padding:5px 8px;color:var(--text2);cursor:pointer;font-size:12px">⬇</button>'
   +'<button onclick="shareLink(\''+r.url+'\')" style="background:var(--bg3);border:none;border-radius:6px;padding:5px 8px;color:var(--text2);cursor:pointer;font-size:12px">📤</button>'
   +'</div>';
 }).join('');
}
async function startDL(){
 var url=document.getElementById("dl-url").value.trim();
 if(!url){toast("❗ Link দিন");return;}
 if(!url.startsWith("http")){toast("❗ https:// দিয়ে শুরু করুন");return;}
 var a=document.createElement("a");a.href=url;a.download=url.split('/').pop()||"file";a.target="_blank";
 document.body.appendChild(a);a.click();document.body.removeChild(a);
 await api("/api/downloads",{url,filename:url.split('/').pop()||"file"});
 document.getElementById("dl-url").value="";
 setTimeout(loadDLs,800);toast("✅ Download শুরু হয়েছে!");
}
async function reDL(url,name){
 var a=document.createElement("a");a.href=url;a.download=name;a.target="_blank";
 document.body.appendChild(a);a.click();document.body.removeChild(a);toast("⬇ Download!");
}
async function dlClipboard(){
 try{var t=await navigator.clipboard.readText();
  if(t&&t.startsWith("http")){document.getElementById("dl-url").value=t;toast("📋 Link নেওয়া হয়েছে!");}
  else toast("❗ Valid link নেই");
 }catch(e){toast("❗ Permission দিন");}
}
async function shareURL(){shareLink(document.getElementById("ub").value||window.location.href);}
async function shareLink(url){
 if(!url)return;
 if(navigator.share){try{await navigator.share({title:"Bong Browser",url});toast("✅ Shared!");}catch(e){}}
 else{try{await navigator.clipboard.writeText(url);toast("📋 Copied!");}catch(e){}}
}
async function clearDL(){await api("/api/downloads/clear",{});document.getElementById("dl-list").innerHTML='<div class="lem">📭 Cleared</div>';toast("🗑 Cleared");}

// Zoom
function zoomIn(){zoom=Math.min(zoom+.1,2);document.body.style.zoom=zoom;toast("Zoom: "+Math.round(zoom*100)+"%");}
function zoomOut(){zoom=Math.max(zoom-.1,.5);document.body.style.zoom=zoom;toast("Zoom: "+Math.round(zoom*100)+"%");}

// Panels
function showMenu(){cap();document.getElementById("pMenu").classList.add("op");}
function cp(id){document.getElementById(id).classList.remove("op");}
function cap(){document.querySelectorAll(".po").forEach(p=>p.classList.remove("op"));}
function showUI(){cap();toast("👤 "+U.name+" · "+(U.is18?"🔞 18+":"🔒 Safe"));}

async function api(url,data){
 var r=await fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
 return r.json();
}
function sm(id,m,c){var el=document.getElementById(id);if(el){el.textContent=m;el.className="amsg"+(c?" "+c:"");}}
var _tt=null;
function toast(msg){var t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");clearTimeout(_tt);_tt=setTimeout(()=>t.classList.remove("show"),3000);}

init();
</script>
</body>
</html>"""

MANIFEST = """{
  "name": "Bong Browser — Modified by Bong.Dev",
  "short_name": "Bong Browser",
  "description": "18+ Browser — Modified by Bong.Dev",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#202124",
  "theme_color": "#202124",
  "orientation": "any",
  "icons": [
    {"src": "/icon.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
    {"src": "/icon.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
  ]
}"""

SW = """const C="bb-v11";
self.addEventListener("install",e=>{self.skipWaiting();});
self.addEventListener("activate",e=>{self.clients.claim();});
self.addEventListener("fetch",e=>{
  if(e.request.method!=="GET")return;
  e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)));
});"""

ICON = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQI12NgAAIABQAABjE+ibYAAAAASUVORK5CYII=")

@app.route("/")
def index(): return HTML

@app.route("/manifest.json")
def manifest():
    from flask import Response
    return Response(MANIFEST, mimetype="application/json")

@app.route("/sw.js")
def sw():
    from flask import Response
    return Response(SW, mimetype="application/javascript")

@app.route("/icon.png")
def icon():
    from flask import Response
    return Response(ICON, mimetype="image/png")

@app.route("/api/me")
def me():
    if "uid" not in session: return jsonify({"logged": False})
    return jsonify({
        "logged": True, "name": session.get("name"),
        "email": session.get("email"), "is18": session.get("is18", 0),
        "age": session.get("age", 0), "is_admin": session.get("is_admin", False)
    })

@app.route("/api/login", methods=["POST"])
def login():
    d = request.json
    e = d.get("email", "").strip().lower()
    p = d.get("pwd", "").strip()
    if not e or not p:
        return jsonify({"ok": False, "msg": "সব ফিল্ড পূরণ করুন"})
    # Admin check
    if e == ADMIN_EMAIL.lower() and p == ADMIN_PASSWORD:
        session.permanent = True
        session.update({"uid": 0, "name": ADMIN_NAME, "email": ADMIN_EMAIL,
                        "is18": 1, "age": 99, "is_admin": True})
        return jsonify({"ok": True, "name": ADMIN_NAME, "is18": 1, "age": 99, "is_admin": True})
    # Normal user
    c = db()
    row = c.execute("SELECT * FROM users WHERE email=? AND pwd=?", (e, sha(p))).fetchone()
    c.close()
    if row:
        if row["is_banned"]:
            return jsonify({"ok": False, "msg": "🚫 আপনার account ban করা হয়েছে"})
        a = calc_age(row["dob"]); i = 1 if a >= 18 else 0
        session.permanent = True
        session.update({"uid": row["id"], "name": row["name"], "email": row["email"],
                        "is18": i, "age": a, "is_admin": False})
        return jsonify({"ok": True, "name": row["name"], "is18": i, "age": a, "is_admin": False})
    return jsonify({"ok": False, "msg": "❌ ভুল Email বা Password\n🔑 Password ভুলে গেলে Reset করুন"})

@app.route("/api/register", methods=["POST"])
def register():
    d = request.json
    n = d.get("name", "").strip()
    e = d.get("email", "").strip().lower()
    p = d.get("pwd", "").strip()
    dob = d.get("dob", "")
    if not all([n, e, p, dob]):
        return jsonify({"ok": False, "msg": "সব ফিল্ড পূরণ করুন"})
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', e):
        return jsonify({"ok": False, "msg": "সঠিক Email দিন"})
    if len(p) < 6:
        return jsonify({"ok": False, "msg": "Password কমপক্ষে ৬ অক্ষর"})
    a = calc_age(dob); i = 1 if a >= 18 else 0
    try:
        c = db()
        c.execute("INSERT INTO users(email,pwd,name,dob,is18,joined) VALUES(?,?,?,?,?,?)",
                  (e, sha(p), n, dob, i, datetime.now().strftime("%d/%m/%Y")))
        c.commit(); c.close()
        return jsonify({"ok": True, "msg": f"✅ সফল! বয়স {a} বছর — {'18+ Mode' if i else 'Safe Mode'}। Login করুন।", "is18": i, "age": a})
    except:
        return jsonify({"ok": False, "msg": "এই Email আগেই রেজিস্ট্রেশন হয়েছে"})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})

# Google OAuth
@app.route("/auth/google")
def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account"
    }
    return redirect("https://accounts.google.com/o/oauth2/auth?" + urllib.parse.urlencode(params))

@app.route("/auth/google/callback")
def google_callback():
    code = request.args.get("code")
    if not code: return redirect("/?error=no_code")
    try:
        token_data = {
            "code": code, "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT, "grant_type": "authorization_code"
        }
        req = urllib.request.Request(
            "https://oauth2.googleapis.com/token",
            data=urllib.parse.urlencode(token_data).encode(), method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            token_info = json_lib.loads(resp.read())
        access_token = token_info.get("access_token")
        user_req = urllib.request.Request(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        with urllib.request.urlopen(user_req) as resp:
            user_info = json_lib.loads(resp.read())
        email = user_info.get("email", "").lower()
        name = user_info.get("name", email.split("@")[0])
        # Admin check
        if email == ADMIN_EMAIL.lower():
            session.permanent = True
            session.update({"uid": 0, "name": ADMIN_NAME, "email": ADMIN_EMAIL,
                            "is18": 1, "age": 99, "is_admin": True})
            return redirect("/?logged=admin")
        # Normal user
        c = db()
        row = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if row:
            if row["is_banned"]: c.close(); return redirect("/?error=banned")
            a = calc_age(row["dob"]); i = 1 if a >= 18 else 0
            session.permanent = True
            session.update({"uid": row["id"], "name": row["name"], "email": email,
                            "is18": i, "age": a, "is_admin": False})
        else:
            dob = "2000-01-01"; a = calc_age(dob); i = 1 if a >= 18 else 0
            c.execute("INSERT INTO users(email,pwd,name,dob,is18,joined) VALUES(?,?,?,?,?,?)",
                      (email, sha("google_" + email), name, dob, i, datetime.now().strftime("%d/%m/%Y")))
            c.commit()
            uid = c.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()["id"]
            session.permanent = True
            session.update({"uid": uid, "name": name, "email": email,
                            "is18": i, "age": a, "is_admin": False})
        c.close()
        return redirect("/?logged=google")
    except Exception as ex:
        return redirect("/?error=google_failed")

# Admin routes
@app.route("/api/admin/stats")
def admin_stats():
    if not session.get("is_admin"): return jsonify({}), 403
    c = db()
    total = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    is18  = c.execute("SELECT COUNT(*) FROM users WHERE is18=1").fetchone()[0]
    safe  = c.execute("SELECT COUNT(*) FROM users WHERE is18=0").fetchone()[0]
    banned = c.execute("SELECT COUNT(*) FROM users WHERE is_banned=1").fetchone()[0]
    c.close()
    return jsonify({"total": total, "is18": is18, "safe": safe, "banned": banned})

@app.route("/api/admin/users")
def admin_users():
    if not session.get("is_admin"): return jsonify([])
    c = db()
    rows = c.execute("SELECT id,email,name,dob,is18,is_banned FROM users ORDER BY id DESC").fetchall()
    c.close()
    return jsonify([{"id": r["id"], "email": r["email"], "name": r["name"],
                     "is18": r["is18"], "is_banned": r["is_banned"], "age": calc_age(r["dob"])} for r in rows])

@app.route("/api/admin/ban", methods=["POST"])
def admin_ban():
    if not session.get("is_admin"): return jsonify({"ok": False}), 403
    d = request.json
    c = db()
    c.execute("UPDATE users SET is_banned=? WHERE id=?", (d.get("ban", 1), d.get("uid")))
    c.commit(); c.close()
    return jsonify({"ok": True})

@app.route("/api/admin/delete-user", methods=["POST"])
def admin_delete():
    if not session.get("is_admin"): return jsonify({"ok": False}), 403
    uid = request.json.get("uid")
    c = db()
    for tbl in ["users", "history", "bookmarks", "downloads"]:
        c.execute(f"DELETE FROM {tbl} WHERE {'id' if tbl=='users' else 'uid'}=?", (uid,))
    c.commit(); c.close()
    return jsonify({"ok": True})

@app.route("/api/admin/clear-all-history", methods=["POST"])
def admin_clear_hist():
    if not session.get("is_admin"): return jsonify({"ok": False}), 403
    c = db(); c.execute("DELETE FROM history"); c.commit(); c.close()
    return jsonify({"ok": True})

# Password
@app.route("/api/verify-email", methods=["POST"])
def verify_email():
    e = request.json.get("email", "").strip().lower()
    c = db(); row = c.execute("SELECT id FROM users WHERE email=?", (e,)).fetchone(); c.close()
    return jsonify({"ok": bool(row), "msg": "❌ এই Email দিয়ে account নেই" if not row else ""})

@app.route("/api/reset-password", methods=["POST"])
def reset_password():
    d = request.json; e = d.get("email", "").strip().lower(); p = d.get("pwd", "").strip()
    if not e or not p or len(p) < 6: return jsonify({"ok": False, "msg": "Invalid"})
    c = db(); c.execute("UPDATE users SET pwd=? WHERE email=?", (sha(p), e)); c.commit(); c.close()
    return jsonify({"ok": True})

@app.route("/api/change-password", methods=["POST"])
def change_password():
    if "uid" not in session: return jsonify({"ok": False, "msg": "Login করুন"})
    if session.get("is_admin"): return jsonify({"ok": False, "msg": "Admin এর জন্য নয়"})
    d = request.json
    old = d.get("old_pwd", "").strip(); new = d.get("new_pwd", "").strip()
    if not old or not new or len(new) < 6: return jsonify({"ok": False, "msg": "Invalid"})
    uid = session["uid"]
    c = db()
    row = c.execute("SELECT id FROM users WHERE id=? AND pwd=?", (uid, sha(old))).fetchone()
    if not row: c.close(); return jsonify({"ok": False, "msg": "❌ পুরনো Password ভুল"})
    c.execute("UPDATE users SET pwd=? WHERE id=?", (sha(new), uid)); c.commit(); c.close()
    return jsonify({"ok": True})

# History
@app.route("/api/history", methods=["GET"])
def get_hist():
    if "uid" not in session or session.get("is_admin"): return jsonify([])
    c = db()
    rows = c.execute("SELECT id,url,title,ts FROM history WHERE uid=? ORDER BY id DESC LIMIT 60",
                     (session["uid"],)).fetchall(); c.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/history", methods=["POST"])
def add_hist():
    if "uid" not in session or session.get("is_admin"): return jsonify({"ok": False})
    d = request.json; url = d.get("url", ""); title = d.get("title", "")
    if url:
        c = db()
        c.execute("INSERT INTO history(uid,url,title,ts) VALUES(?,?,?,?)",
                  (session["uid"], url, title[:200], datetime.now().strftime("%d/%m %H:%M")))
        c.commit(); c.close()
    return jsonify({"ok": True})

@app.route("/api/history/clear", methods=["POST"])
def clear_hist():
    if "uid" not in session: return jsonify({"ok": False})
    c = db(); c.execute("DELETE FROM history WHERE uid=?", (session["uid"],)); c.commit(); c.close()
    return jsonify({"ok": True})

# Bookmarks
@app.route("/api/bookmarks", methods=["GET"])
def get_bk():
    if "uid" not in session or session.get("is_admin"): return jsonify([])
    c = db()
    rows = c.execute("SELECT id,url,title FROM bookmarks WHERE uid=? ORDER BY id DESC",
                     (session["uid"],)).fetchall(); c.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/bookmarks", methods=["POST"])
def add_bk():
    if "uid" not in session or session.get("is_admin"): return jsonify({"ok": False})
    d = request.json; c = db()
    c.execute("INSERT INTO bookmarks(uid,url,title) VALUES(?,?,?)",
              (session["uid"], d.get("url", ""), d.get("title", "")[:200]))
    c.commit(); c.close()
    return jsonify({"ok": True})

@app.route("/api/bookmarks/<int:bid>", methods=["DELETE"])
def del_bk(bid):
    if "uid" not in session: return jsonify({"ok": False})
    c = db(); c.execute("DELETE FROM bookmarks WHERE id=? AND uid=?", (bid, session["uid"])); c.commit(); c.close()
    return jsonify({"ok": True})

# Downloads
@app.route("/api/downloads", methods=["GET"])
def get_downloads():
    if "uid" not in session: return jsonify([])
    c = db()
    rows = c.execute("SELECT id,url,filename,ts FROM downloads WHERE uid=? ORDER BY id DESC LIMIT 50",
                     (session["uid"],)).fetchall(); c.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/downloads", methods=["POST"])
def add_download():
    if "uid" not in session: return jsonify({"ok": False})
    d = request.json; url = d.get("url", ""); filename = d.get("filename", "")
    if url:
        c = db()
        c.execute("INSERT INTO downloads(uid,url,filename,ts) VALUES(?,?,?,?)",
                  (session["uid"], url, filename[:200], datetime.now().strftime("%d/%m %H:%M")))
        c.commit(); c.close()
    return jsonify({"ok": True})

@app.route("/api/downloads/clear", methods=["POST"])
def clear_downloads():
    if "uid" not in session: return jsonify({"ok": False})
    c = db(); c.execute("DELETE FROM downloads WHERE uid=?", (session["uid"],)); c.commit(); c.close()
    return jsonify({"ok": True})

@app.route("/api/downloads/<int:did>", methods=["DELETE"])
def del_download(did):
    if "uid" not in session: return jsonify({"ok": False})
    c = db(); c.execute("DELETE FROM downloads WHERE id=? AND uid=?", (did, session["uid"])); c.commit(); c.close()
    return jsonify({"ok": True})

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
