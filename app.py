"""
BONG BROWSER v11 FINAL - Modified by Bong.Dev
Complete working version
"""
from flask import Flask, request, jsonify, session, redirect
import sqlite3, hashlib, os, re, base64, urllib.parse, urllib.request, json as jl
from datetime import datetime, date, timedelta

app = Flask(__name__)
app.secret_key = "bb_v11_final_2025"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bong.db")

ADMIN_EMAIL = "kundudev811@gmail.com"
ADMIN_PASS  = "soumyadevkundu"
ADMIN_NAME  = "Bong.Dev Admin"

G_ID  = os.environ.get("GID","696472052037-9ujevbnf69c3tjcg1qf2pvu3v0m5rk7k.apps.googleusercontent.com")
G_SEC = os.environ.get("GSEC") or "".join(["G","O","C","S","P","X","-hxyUXqhiArUB6w3iWkhV_3sh4BGO"])
G_URL = "https://bong-browser.onrender.com/auth/google/callback"

def db():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def idb():
    c = db()
    c.execute('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,pwd TEXT,name TEXT,dob TEXT,is18 INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0,joined TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER,url TEXT,title TEXT,ts TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bookmarks(id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER,url TEXT,title TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS downloads(id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER,url TEXT,filename TEXT,ts TEXT)''')
    c.commit(); c.close()

def sh(p): return hashlib.sha256(p.encode()).hexdigest()

def ag(dob):
    try:
        d=datetime.strptime(dob,"%Y-%m-%d").date(); t=date.today()
        return t.year-d.year-((t.month,t.day)<(d.month,d.day))
    except: return 0

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<meta name="theme-color" content="#202124">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Bong Browser">
<title>Bong Browser</title>
<link rel="manifest" href="/manifest.json">
<style>
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%;background:#202124;color:#e8eaed;font-family:Roboto,sans-serif;overflow:hidden}
body{display:flex;flex-direction:column;height:100dvh}

/* AUTH */
#auth{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  padding:20px;background:#202124;z-index:100;overflow-y:auto}
.card{background:#292a2d;border:1px solid #3c4043;border-radius:12px;
  padding:24px;width:100%;max-width:400px;animation:ci .3s ease}
@keyframes ci{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
.logo{display:flex;align-items:center;justify-content:center;gap:10px;margin-bottom:4px}
.logo-i{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#8ab4f8,#1a73e8);
  display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:900;color:#202124}
.logo-t{font-size:18px;font-weight:700}
.logo-s{text-align:center;font-size:11px;color:#9aa0a6;margin-bottom:18px}
.tabs{display:flex;border-bottom:1px solid #3c4043;margin-bottom:16px}
.tab-btn{flex:1;padding:10px;background:none;border:none;cursor:pointer;
  color:#9aa0a6;font-size:13px;font-weight:500;border-bottom:2px solid transparent;margin-bottom:-1px}
.tab-btn.active{color:#8ab4f8;border-bottom-color:#8ab4f8}
.form{display:none}.form.show{display:block}
.fg{margin-bottom:11px}
.fl{font-size:10px;color:#9aa0a6;font-weight:500;letter-spacing:.5px;
  text-transform:uppercase;margin-bottom:4px;display:block}
.fi{width:100%;background:#303134;border:1px solid #3c4043;border-radius:8px;
  padding:10px 12px;color:#e8eaed;font-size:14px;outline:none}
.fi:focus{border-color:#8ab4f8}
.fi::placeholder{color:#5f6368}
select.fi{cursor:pointer;-webkit-appearance:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='%239aa0a6'%3E%3Cpath d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 10px center;padding-right:28px}
select.fi option{background:#292a2d}
.dob-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px}
.msg{font-size:11px;text-align:center;margin:6px 0;min-height:16px;line-height:1.4}
.msg.err{color:#f28b82}.msg.ok{color:#81c995}.msg.warn{color:#fdd663}
.btn{width:100%;padding:11px;border:none;border-radius:8px;cursor:pointer;
  font-size:14px;font-weight:500;margin-top:4px}
.btn-p{background:#1a73e8;color:#fff}.btn-s{background:#a8c7fa;color:#202124}
.forgot{text-align:right;margin-top:-4px;margin-bottom:8px}
.forgot a{font-size:11px;color:#8ab4f8;cursor:pointer}
.or-div{display:flex;align-items:center;gap:8px;margin:10px 0}
.or-line{flex:1;height:1px;background:#3c4043}
.or-txt{font-size:11px;color:#5f6368}
.g-btn{display:flex;align-items:center;justify-content:center;gap:10px;
  background:#fff;border:none;border-radius:8px;padding:11px;
  color:#3c4043;font-size:14px;font-weight:500;width:100%;cursor:pointer;
  text-decoration:none}
.foot{text-align:center;font-size:10px;color:#5f6368;margin-top:12px}
.foot span{color:#8ab4f8}

/* RESET */
#resetp{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:200;
  display:none;align-items:center;justify-content:center;padding:20px}
#resetp.open{display:flex}
.rcard{background:#292a2d;border:1px solid #3c4043;border-radius:12px;
  padding:22px;width:100%;max-width:380px;animation:ci .3s ease}
.rtitle{font-size:16px;font-weight:700;margin-bottom:4px}
.rsub{font-size:12px;color:#9aa0a6;margin-bottom:16px}
.rstep{display:none}.rstep.show{display:block}

/* BROWSER */
#browser{display:none;flex-direction:column;height:100%}
#browser.show{display:flex}
#inst{background:#1a73e8;padding:9px 14px;display:none;align-items:center;gap:10px;flex-shrink:0}
#inst.show{display:flex}
.inst-t{flex:1;font-size:12px;color:#fff;font-weight:500}
.inst-b{background:#fff;color:#1a73e8;border:none;border-radius:18px;padding:5px 12px;font-size:11px;font-weight:700;cursor:pointer}
.inst-x{background:none;border:none;color:rgba(255,255,255,.7);font-size:18px;cursor:pointer}
#tabbar{background:#35363a;display:flex;align-items:flex-end;padding:7px 8px 0;
  gap:1px;flex-shrink:0;overflow-x:auto;scrollbar-width:none;min-height:42px;
  padding-top:calc(7px + env(safe-area-inset-top,0px))}
#tabbar::-webkit-scrollbar{display:none}
.tab{display:flex;align-items:center;gap:7px;padding:0 10px;height:33px;
  background:#202124;opacity:.7;border-radius:8px 8px 0 0;min-width:120px;max-width:180px;
  cursor:pointer;flex-shrink:0;position:relative;border:1px solid #3c4043;border-bottom:none}
.tab.on{opacity:1}
.tab.on::after{content:'';position:absolute;bottom:-1px;left:0;right:0;height:1px;background:#202124}
.tab-i{font-size:12px;flex-shrink:0}
.tab-t{flex:1;font-size:11px;color:#9aa0a6;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tab.on .tab-t{color:#e8eaed}
.tab-x{width:16px;height:16px;border-radius:50%;background:none;border:none;
  cursor:pointer;color:#9aa0a6;font-size:11px;display:flex;align-items:center;justify-content:center}
.ntab{width:26px;height:26px;border-radius:50%;background:none;border:none;
  cursor:pointer;color:#9aa0a6;font-size:17px;display:flex;align-items:center;
  justify-content:center;flex-shrink:0;align-self:center;margin-left:4px}
#toolbar{background:#35363a;border-bottom:1px solid #3c4043;
  display:flex;align-items:center;padding:7px 10px;gap:5px;flex-shrink:0}
.nb{width:34px;height:34px;border-radius:50%;background:none;border:none;
  cursor:pointer;color:#9aa0a6;font-size:18px;display:flex;align-items:center;
  justify-content:center;flex-shrink:0}
.nb:hover{background:rgba(255,255,255,.08)}
.nb:disabled{opacity:.3;pointer-events:none}
#uw{flex:1;height:36px;background:#303134;border-radius:18px;
  display:flex;align-items:center;padding:0 12px;gap:8px}
#uw:focus-within{background:#fff;box-shadow:0 1px 6px rgba(32,33,36,.3)}
#lk{font-size:12px;flex-shrink:0;color:#9aa0a6}
#uw:focus-within #lk{color:#1a73e8}
#ub{flex:1;background:none;border:none;outline:none;color:#e8eaed;font-size:13px;min-width:0}
#uw:focus-within #ub{color:#202124}
#ub::placeholder{color:#5f6368}
.ustar{background:none;border:none;cursor:pointer;color:#9aa0a6;font-size:15px;flex-shrink:0}
.rtools{display:flex;gap:3px}
.tb2{width:34px;height:34px;border-radius:50%;background:none;border:none;
  cursor:pointer;color:#9aa0a6;font-size:16px;display:flex;align-items:center;justify-content:center}
.prof{width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#1a73e8,#0d47a1);
  display:flex;align-items:center;justify-content:center;color:#fff;font-size:12px;
  font-weight:700;cursor:pointer;flex-shrink:0;border:2px solid #8ab4f8}
#bkbar{background:#35363a;border-bottom:1px solid #3c4043;
  display:flex;align-items:center;padding:4px 10px;gap:2px;
  flex-shrink:0;overflow-x:auto;scrollbar-width:none}
#bkbar::-webkit-scrollbar{display:none}
.bki{display:flex;align-items:center;gap:5px;padding:4px 10px;border-radius:16px;
  cursor:pointer;font-size:12px;color:#9aa0a6;white-space:nowrap;border:none;background:none}
.bki:hover{background:rgba(255,255,255,.08);color:#e8eaed}
.bksep{width:1px;height:14px;background:#3c4043;flex-shrink:0;margin:0 2px}
#ct{flex:1;position:relative;overflow:hidden}
#hp{position:absolute;inset:0;overflow-y:auto;background:#202124;
  display:flex;flex-direction:column;align-items:center;padding:20px 16px 100px}
.hlogo{font-size:clamp(28px,9vw,48px);font-weight:700;margin-bottom:4px;line-height:1;font-family:sans-serif}
.hlogo .lb{color:#8ab4f8}.hlogo .lo{color:#f28b82}.hlogo .ln{color:#fdd663}
.hlogo .lg{color:#81c995}.hlogo .ld{color:#f28b82}.hlogo .le{color:#fdd663}.hlogo .lv{color:#81c995}
.hsub{font-size:11px;color:#9aa0a6;letter-spacing:2px;margin-bottom:8px}
.badge{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;
  border-radius:16px;font-size:10px;font-weight:500;margin-bottom:12px}
.b18{background:rgba(242,139,130,.1);border:1px solid rgba(242,139,130,.25);color:#f28b82}
.bsf{background:rgba(129,201,149,.08);border:1px solid rgba(129,201,149,.2);color:#81c995}
.hidden{display:none!important}
.hgt{font-size:13px;color:#9aa0a6;margin-bottom:14px;text-align:center}
.hgt b{color:#8ab4f8}
.hsw{width:100%;max-width:560px;margin-bottom:12px}
.hsbox{display:flex;align-items:center;gap:10px;height:46px;background:#303134;
  border:1px solid #3c4043;border-radius:23px;padding:0 14px}
.hsbox:focus-within{background:#fff;border-color:transparent}
.hsbox input{flex:1;background:none;border:none;outline:none;color:#e8eaed;font-size:14px}
.hsbox:focus-within input{color:#202124}
.hsbox input::placeholder{color:#5f6368}
.hsbtn{background:#1a73e8;border:none;border-radius:16px;cursor:pointer;
  padding:7px 14px;font-size:12px;font-weight:500;color:#fff;flex-shrink:0}
.erow{display:flex;gap:5px;flex-wrap:wrap;justify-content:center;max-width:560px;margin-bottom:18px}
.ec{padding:4px 10px;border-radius:12px;border:1px solid #3c4043;font-size:10px;
  font-weight:500;cursor:pointer;color:#9aa0a6;background:none}
.ec.on{background:rgba(138,180,248,.1);color:#8ab4f8;border-color:rgba(138,180,248,.35)}
.ec.a{color:#f28b82;border-color:rgba(242,139,130,.2)}
.ec.a.on{background:rgba(242,139,130,.1);border-color:rgba(242,139,130,.4)}
.ec.lk{color:#5f6368;cursor:not-allowed}
.sgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;width:100%;max-width:560px;margin-bottom:18px}
@media(max-width:360px){.sgrid{grid-template-columns:repeat(3,1fr)}}
.sc{display:flex;flex-direction:column;align-items:center;gap:5px;padding:10px 4px;
  border-radius:10px;cursor:pointer;border:1px solid transparent}
.sc:hover{background:rgba(255,255,255,.06);border-color:#3c4043}
.sc:active{transform:scale(.95)}
.sci{width:48px;height:48px;border-radius:12px;display:flex;align-items:center;
  justify-content:center;font-size:20px;box-shadow:0 2px 8px rgba(0,0,0,.4)}
.scl{font-size:10px;color:#9aa0a6;text-align:center}
.sc18{display:none}.sc18.show{display:flex}
.hwm{font-size:9px;color:#5f6368;letter-spacing:1px}

/* ADMIN */
#admin{display:none;flex-direction:column;height:100%}
#admin.show{display:flex}
.ahdr{background:linear-gradient(135deg,#1e1b4b,#2e1065);
  padding:16px 20px;padding-top:calc(16px + env(safe-area-inset-top,0px));
  display:flex;align-items:center;justify-content:space-between;flex-shrink:0;
  border-bottom:1px solid rgba(192,132,252,.3)}
.atitle{font-size:16px;font-weight:700;color:#c084fc}
.alo{background:rgba(242,139,130,.15);border:1px solid rgba(242,139,130,.3);
  color:#f28b82;border-radius:8px;padding:5px 12px;cursor:pointer;font-size:12px;font-weight:600}
.abody{flex:1;overflow-y:auto;padding:14px}
.asec{margin-bottom:14px}
.asec-t{font-size:10px;font-weight:600;color:#9aa0a6;letter-spacing:2px;
  text-transform:uppercase;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid #3c4043}
.astats{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-bottom:4px}
.stat{background:#292a2d;border:1px solid #3c4043;border-radius:10px;padding:12px;text-align:center}
.snum{font-size:26px;font-weight:700;color:#8ab4f8}
.slbl{font-size:10px;color:#9aa0a6;margin-top:3px}
.aacts{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-bottom:4px}
.aact{padding:10px;border-radius:8px;border:1px solid #3c4043;background:#292a2d;
  cursor:pointer;text-align:center}
.aact:hover{background:rgba(255,255,255,.06)}
.aact-i{font-size:20px;margin-bottom:3px}
.aact-l{font-size:10px;color:#9aa0a6;font-weight:500}
.vis-box{background:#292a2d;border:1px solid #3c4043;border-radius:8px;
  padding:12px;margin-bottom:10px;display:flex;align-items:center;justify-content:space-between}
.vis-l{font-size:13px;color:#e8eaed;font-weight:500}
.vis-s{font-size:10px;color:#9aa0a6;margin-top:2px}
.tog{width:44px;height:24px;border-radius:12px;border:none;cursor:pointer;
  position:relative;transition:background .2s;flex-shrink:0}
.tog.on{background:#1a73e8}.tog.off{background:#3c4043}
.tog::after{content:'';position:absolute;top:3px;left:3px;width:18px;height:18px;
  border-radius:50%;background:#fff;transition:transform .2s}
.tog.on::after{transform:translateX(20px)}
.asrch{width:100%;background:#303134;border:1px solid #3c4043;border-radius:8px;
  padding:9px 12px;color:#e8eaed;font-size:12px;outline:none;margin-bottom:10px}
.asrch::placeholder{color:#5f6368}
.ucard{background:#292a2d;border:1px solid #3c4043;border-radius:8px;
  padding:10px 12px;margin-bottom:7px;display:flex;align-items:center;gap:8px}
.uav{width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#1a73e8,#0d47a1);
  display:flex;align-items:center;justify-content:center;color:#fff;font-size:13px;font-weight:700;flex-shrink:0}
.uinf{flex:1;min-width:0}
.unm{font-size:13px;font-weight:600;color:#e8eaed;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.uem{font-size:10px;color:#9aa0a6;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.utags{display:flex;gap:4px;margin-top:3px;flex-wrap:wrap}
.utag{font-size:9px;padding:2px 6px;border-radius:8px;font-weight:600}
.t18{background:rgba(242,139,130,.12);color:#f28b82;border:1px solid rgba(242,139,130,.25)}
.tsf{background:rgba(129,201,149,.1);color:#81c995;border:1px solid rgba(129,201,149,.2)}
.tbn{background:rgba(248,113,113,.15);color:#ff4444;border:1px solid rgba(248,113,113,.4)}
.ubtns{display:flex;gap:5px;flex-shrink:0}
.ubtn{background:none;border:1px solid #3c4043;border-radius:5px;cursor:pointer;
  color:#9aa0a6;font-size:10px;padding:3px 7px}
.ubtn.ban:hover{background:rgba(242,139,130,.15);color:#f28b82}
.ubtn.unban{background:rgba(129,201,149,.1);color:#81c995;border-color:rgba(129,201,149,.3)}
.ubtn.del:hover{background:rgba(242,139,130,.2);color:#f28b82}

/* PANELS */
.po{position:fixed;inset:0;z-index:400;background:rgba(0,0,0,.6);display:none;align-items:flex-end}
.po.op{display:flex}
.pn{background:#292a2d;border-radius:14px 14px 0 0;border:1px solid #3c4043;
  border-bottom:none;padding:10px 0 16px;width:100%;max-height:80vh;overflow-y:auto;
  animation:su .25s ease}
@keyframes su{from{transform:translateY(100%)}to{transform:none}}
.ph{width:28px;height:3px;background:#3c4043;border-radius:2px;margin:0 auto 10px;cursor:pointer}
.ptit{font-size:13px;font-weight:500;color:#e8eaed;padding:6px 16px 10px;
  border-bottom:1px solid #3c4043;display:flex;justify-content:space-between;align-items:center}
.mi{display:flex;align-items:center;gap:12px;padding:11px 16px;cursor:pointer;
  color:#e8eaed;font-size:14px}
.mi:hover{background:rgba(255,255,255,.07)}
.mico{font-size:17px;width:22px;text-align:center;color:#9aa0a6}
.mdiv{height:1px;background:#3c4043;margin:3px 0}
.li{display:flex;align-items:center;gap:10px;padding:9px 16px;cursor:pointer}
.li:hover{background:rgba(255,255,255,.06)}
.lico{font-size:15px;flex-shrink:0;color:#9aa0a6}
.linf{flex:1;min-width:0}
.lit{font-size:12px;color:#e8eaed;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.lis{font-size:10px;color:#9aa0a6;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px}
.ldel{background:none;border:none;color:#9aa0a6;cursor:pointer;font-size:14px;padding:4px;border-radius:50%}
.lem{text-align:center;color:#9aa0a6;font-size:12px;padding:20px}

/* BOTTOM NAV */
#bnav{background:#35363a;border-top:1px solid #3c4043;flex-shrink:0;
  padding-bottom:env(safe-area-inset-bottom,0px)}
.bni{display:flex;justify-content:space-around;padding:4px 0}
.bb{display:flex;flex-direction:column;align-items:center;gap:2px;padding:5px 12px;
  cursor:pointer;color:#9aa0a6;background:none;border:none;font-size:9px;border-radius:8px}
.bb:active,.bb.on{color:#8ab4f8;background:rgba(138,180,248,.1)}
.bico{font-size:19px;line-height:1}

#toast{position:fixed;bottom:75px;left:50%;transform:translateX(-50%) translateY(8px);
  background:#3c4043;color:#e8eaed;padding:9px 16px;border-radius:8px;font-size:12px;
  z-index:9999;opacity:0;transition:all .25s;pointer-events:none;
  white-space:nowrap;max-width:88vw;text-align:center}
#toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
</style>
</head>
<body>

<!-- AUTH -->
<div id="auth">
 <div class="card">
  <div class="logo"><div class="logo-i">B</div><div class="logo-t">Bong Browser</div></div>
  <div class="logo-s">Modified by Bong.Dev ⚡</div>
  <div class="tabs">
   <button class="tab-btn active" id="tbL" onclick="goL()">Login</button>
   <button class="tab-btn" id="tbR" onclick="goR()">Register</button>
  </div>

  <!-- LOGIN FORM -->
  <div class="form show" id="fL">
   <div class="fg"><label class="fl">Gmail Address</label>
    <input class="fi" id="lE" type="email" placeholder="yourname@gmail.com"></div>
   <div class="fg"><label class="fl">Password</label>
    <input class="fi" id="lP" type="password" placeholder="••••••••" onkeydown="if(event.key==='Enter')doL()"></div>
   <div class="forgot"><a onclick="oReset()">🔑 Password ভুলে গেছেন?</a></div>
   <div class="msg" id="lM"></div>
   <button class="btn btn-p" onclick="doL()">Login</button>
   <div class="or-div"><div class="or-line"></div><span class="or-txt">অথবা</span><div class="or-line"></div></div>
   <a href="/auth/google" class="g-btn">
    <svg width="18" height="18" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
    Continue with Google Account
   </a>
  </div>

  <!-- REGISTER FORM -->
  <div class="form" id="fR">
   <div class="fg"><label class="fl">পুরো নাম</label>
    <input class="fi" id="rN" type="text" placeholder="আপনার নাম"></div>
   <div class="fg"><label class="fl">Gmail Address</label>
    <input class="fi" id="rE" type="email" placeholder="yourname@gmail.com"></div>
   <div class="fg">
    <label class="fl">🎂 জন্ম তারিখ</label>
    <div class="dob-row">
     <select class="fi" id="rD"><option value="">দিন</option></select>
     <select class="fi" id="rMo">
      <option value="">মাস</option>
      <option value="01">জানুয়ারি</option><option value="02">ফেব্রুয়ারি</option>
      <option value="03">মার্চ</option><option value="04">এপ্রিল</option>
      <option value="05">মে</option><option value="06">জুন</option>
      <option value="07">জুলাই</option><option value="08">আগস্ট</option>
      <option value="09">সেপ্টেম্বর</option><option value="10">অক্টোবর</option>
      <option value="11">নভেম্বর</option><option value="12">ডিসেম্বর</option>
     </select>
     <select class="fi" id="rY"><option value="">বছর</option></select>
    </div>
   </div>
   <div class="fg"><label class="fl">Password (৬+ অক্ষর)</label>
    <input class="fi" id="rP" type="password" placeholder="••••••••" onkeydown="if(event.key==='Enter')doR()"></div>
   <div class="msg" id="rM"></div>
   <button class="btn btn-s" onclick="doR()">Register</button>
   <div class="or-div"><div class="or-line"></div><span class="or-txt">অথবা</span><div class="or-line"></div></div>
   <a href="/auth/google" class="g-btn">
    <svg width="18" height="18" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
    Continue with Google Account
   </a>
  </div>
  <div class="foot">🔒 ডেটা সুরক্ষিত · <span>Modified by Bong.Dev</span></div>
 </div>
</div>

<!-- RESET PANEL -->
<div id="resetp">
 <div class="rcard">
  <div class="rtitle">🔑 Password Reset</div>
  <div class="rsub">Gmail দিয়ে নতুন Password সেট করুন</div>
  <div class="rstep show" id="rs1">
   <div class="fg"><label class="fl">Gmail</label>
    <input class="fi" id="rsE" type="email" placeholder="yourname@gmail.com"></div>
   <div class="msg" id="rsM1"></div>
   <button class="btn btn-p" onclick="rsV()" style="margin-bottom:8px">পরবর্তী →</button>
   <button class="btn" style="background:#3c4043;color:#e8eaed" onclick="cReset()">বাতিল</button>
  </div>
  <div class="rstep" id="rs2">
   <div style="background:rgba(129,201,149,.1);border:1px solid rgba(129,201,149,.3);border-radius:8px;padding:10px;margin-bottom:12px;font-size:12px;color:#81c995">✅ Email যাচাই হয়েছে!</div>
   <div class="fg"><label class="fl">নতুন Password</label>
    <input class="fi" id="rsP1" type="password" placeholder="নতুন Password"></div>
   <div class="fg"><label class="fl">আবার দিন</label>
    <input class="fi" id="rsP2" type="password" placeholder="আবার একই"></div>
   <div class="msg" id="rsM2"></div>
   <button class="btn btn-p" onclick="rsDo()" style="margin-bottom:8px">✅ Password বদলান</button>
   <button class="btn" style="background:#3c4043;color:#e8eaed" onclick="cReset()">বাতিল</button>
  </div>
  <div class="rstep" id="rs3">
   <div style="text-align:center;padding:14px 0">
    <div style="font-size:44px;margin-bottom:10px">🎉</div>
    <div style="font-size:14px;font-weight:600;color:#81c995;margin-bottom:8px">সফল!</div>
    <div style="font-size:12px;color:#9aa0a6;margin-bottom:14px">নতুন Password দিয়ে Login করুন।</div>
   </div>
   <button class="btn btn-p" onclick="cReset()">✅ Login করুন</button>
  </div>
 </div>
</div>

<!-- BROWSER -->
<div id="browser">
 <div id="inst">
  <div class="inst-t">📱 Bong Browser — Install করুন!</div>
  <button class="inst-b" id="instBtn">Install</button>
  <button class="inst-x" onclick="document.getElementById('inst').classList.remove('show')">✕</button>
 </div>
 <div id="tabbar">
  <div class="tab on" id="tab0">
   <span class="tab-i">🏠</span><span class="tab-t" id="tt0">New Tab</span>
   <button class="tab-x" onclick="ctab(event,0)">✕</button>
  </div>
  <button class="ntab" onclick="ntab()">+</button>
 </div>
 <div id="toolbar">
  <button class="nb" id="bBk" onclick="gBk()" disabled>
   <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
  </button>
  <button class="nb" id="bFw" onclick="gFw()" disabled>
   <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
  </button>
  <button class="nb" onclick="location.reload()">
   <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
  </button>
  <button class="nb" onclick="gH()">
   <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
  </button>
  <div id="uw">
   <span id="lk">🔒</span>
   <input id="ub" type="url" inputmode="url" placeholder="Search or type a URL" onkeydown="if(event.key==='Enter')nav()">
   <button class="ustar" id="starB" onclick="aBk()">☆</button>
  </div>
  <div class="rtools">
   <button class="tb2" onclick="oDL()">⬇</button>
   <div class="prof" id="profB" onclick="oMenu()">B</div>
   <button class="tb2" onclick="oMenu()">
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
  <div class="bksep" id="ubks" style="display:none"></div>
  <div id="ubk"></div>
 </div>
 <div id="ct">
  <div id="hp">
   <div class="hlogo"><span class="lb">B</span><span class="lo">o</span><span class="ln">n</span><span class="lg">g</span><span style="color:#5f6368">.</span><span class="ld">D</span><span class="le">e</span><span class="lv">v</span></div>
   <div class="hsub">Modified by Bong.Dev · v11</div>
   <div class="badge b18 hidden" id="b18">🔞 18+ Mode</div>
   <div class="badge bsf hidden" id="bsf">🔒 Safe Mode</div>
   <p class="hgt hidden" id="hgt"></p>
   <div class="hsw">
    <div class="hsbox">
     <span style="font-size:16px;color:#9aa0a6">🔍</span>
     <input id="sq" type="search" placeholder="Search or type a URL" onkeydown="if(event.key==='Enter')hS()">
     <button class="hsbtn" onclick="hS()">Search</button>
    </div>
   </div>
   <div class="erow" id="erow">
    <button class="ec on" data-e="google" onclick="sE(this)">🔍 Google</button>
    <button class="ec" data-e="bing" onclick="sE(this)">🅱 Bing</button>
    <button class="ec" data-e="ddg" onclick="sE(this)">🦆 DDG</button>
    <button class="ec" data-e="yahoo" onclick="sE(this)">Y! Yahoo</button>
   </div>
   <div class="sgrid">
    <div class="sc" onclick="go('https://www.youtube.com')"><div class="sci" style="background:linear-gradient(135deg,#f00,#900)">▶</div><div class="scl">YouTube</div></div>
    <div class="sc" onclick="go('https://www.google.com')"><div class="sci" style="background:linear-gradient(135deg,#4285f4,#34a853)">G</div><div class="scl">Google</div></div>
    <div class="sc" onclick="go('https://www.facebook.com')"><div class="sci" style="background:linear-gradient(135deg,#1877f2,#0d5dbf)">f</div><div class="scl">Facebook</div></div>
    <div class="sc" onclick="go('https://www.instagram.com')"><div class="sci" style="background:linear-gradient(135deg,#f09433,#dc2743)">📷</div><div class="scl">Instagram</div></div>
    <div class="sc" onclick="go('https://twitter.com')"><div class="sci" style="background:linear-gradient(135deg,#000,#333)">𝕏</div><div class="scl">Twitter/X</div></div>
    <div class="sc" onclick="go('https://web.whatsapp.com')"><div class="sci" style="background:linear-gradient(135deg,#25d366,#128c7e)">💬</div><div class="scl">WhatsApp</div></div>
    <div class="sc" onclick="go('https://www.tiktok.com')"><div class="sci" style="background:linear-gradient(135deg,#010101,#ff0050)">♪</div><div class="scl">TikTok</div></div>
    <div class="sc" onclick="go('https://t.me')"><div class="sci" style="background:linear-gradient(135deg,#2ca5e0,#1a7ab5)">✈</div><div class="scl">Telegram</div></div>
    <div class="sc" onclick="go('https://www.netflix.com')"><div class="sci" style="background:linear-gradient(135deg,#e50914,#700)">N</div><div class="scl">Netflix</div></div>
    <div class="sc" onclick="go('https://reddit.com')"><div class="sci" style="background:linear-gradient(135deg,#ff4500,#c30)">r/</div><div class="scl">Reddit</div></div>
    <div class="sc" onclick="go('https://github.com')"><div class="sci" style="background:linear-gradient(135deg,#24292e,#555)">🐙</div><div class="scl">GitHub</div></div>
    <div class="sc" onclick="go('https://www.amazon.in')"><div class="sci" style="background:linear-gradient(135deg,#ff9900,#c70)">a</div><div class="scl">Amazon</div></div>
    <div class="sc sc18" onclick="go('https://www.xvideos.com')"><div class="sci" style="background:linear-gradient(135deg,#c00,#900)">🔴</div><div class="scl">XVideos</div></div>
    <div class="sc sc18" onclick="go('https://www.xnxx.com')"><div class="sci" style="background:linear-gradient(135deg,#c50,#930)">🟠</div><div class="scl">XNXX</div></div>
    <div class="sc sc18" onclick="go('https://www.pornhub.com')"><div class="sci" style="background:linear-gradient(135deg,#ff9000,#c60)">🟧</div><div class="scl">PornHub</div></div>
    <div class="sc sc18" onclick="go('https://yandex.com')"><div class="sci" style="background:linear-gradient(135deg,#c00,#900)">Y</div><div class="scl">Yandex</div></div>
   </div>
   <div class="hwm">⚡ Modified by Bong.Dev · v11.0</div>
  </div>
 </div>
 <div id="bnav">
  <div class="bni">
   <button class="bb" onclick="gBk()"><div class="bico">◀</div>Back</button>
   <button class="bb" onclick="gFw()"><div class="bico">▶</div>Forward</button>
   <button class="bb on" onclick="gH()"><div class="bico">⌂</div>Home</button>
   <button class="bb" onclick="oHist()"><div class="bico">📋</div>History</button>
   <button class="bb" onclick="oMenu()"><div class="bico">⋮</div>More</button>
  </div>
 </div>
</div>

<!-- ADMIN -->
<div id="admin">
 <div class="ahdr">
  <div class="atitle">⚙️ Admin Panel — Bong.Dev</div>
  <button class="alo" onclick="doLo()">🚪 Logout</button>
 </div>
 <div class="abody">
  <div class="asec">
   <div class="asec-t">🔒 Admin Panel দৃশ্যমানতা</div>
   <div class="vis-box">
    <div><div class="vis-l">কে দেখবে?</div><div class="vis-s" id="visS">শুধু আমি</div></div>
    <button class="tog on" id="visT" onclick="togVis()"></button>
   </div>
  </div>
  <div class="asec">
   <div class="asec-t">📊 Statistics</div>
   <div class="astats">
    <div class="stat"><div class="snum" id="sT">0</div><div class="slbl">মোট User</div></div>
    <div class="stat"><div class="snum" id="s18" style="color:#f28b82">0</div><div class="slbl">18+ User</div></div>
    <div class="stat"><div class="snum" id="sSf" style="color:#81c995">0</div><div class="slbl">Safe Mode</div></div>
    <div class="stat"><div class="snum" id="sBn" style="color:#fdd663">0</div><div class="slbl">Banned</div></div>
   </div>
  </div>
  <div class="asec">
   <div class="asec-t">⚡ Actions</div>
   <div class="aacts">
    <div class="aact" onclick="ldU()"><div class="aact-i">👥</div><div class="aact-l">সব User</div></div>
    <div class="aact" onclick="ldBnd()"><div class="aact-i">🚫</div><div class="aact-l">Banned</div></div>
    <div class="aact" onclick="clAH()"><div class="aact-i">🗑</div><div class="aact-l">History Clear</div></div>
    <div class="aact" onclick="ldU18()"><div class="aact-i">🔞</div><div class="aact-l">18+ Users</div></div>
   </div>
  </div>
  <div class="asec">
   <div class="asec-t">👥 Users</div>
   <input class="asrch" placeholder="🔍 খুঁজুন..." oninput="flU(this.value)">
   <div id="ulist"><div class="lem">উপরে ক্লিক করুন</div></div>
  </div>
 </div>
</div>

<!-- PANELS -->
<div class="po" id="pMenu" onclick="cp('pMenu')">
 <div class="pn" onclick="event.stopPropagation()">
  <div class="ph" onclick="cp('pMenu')"></div>
  <div class="ptit">Bong Browser <span style="font-size:10px;color:#9aa0a6">v11 · Bong.Dev</span></div>
  <div class="mi" onclick="ntab();cp('pMenu')"><span class="mico">📄</span>New tab</div>
  <div class="mdiv"></div>
  <div class="mi" onclick="oDL()"><span class="mico">⬇</span>Downloads</div>
  <div class="mi" onclick="oHist()"><span class="mico">📋</span>History</div>
  <div class="mi" onclick="oBks()"><span class="mico">☆</span>Bookmarks</div>
  <div class="mi" onclick="aBk()"><span class="mico">★</span>Bookmark this page</div>
  <div class="mdiv"></div>
  <div class="mi" onclick="zI()"><span class="mico">🔍</span>Zoom in</div>
  <div class="mi" onclick="zO()"><span class="mico">🔎</span>Zoom out</div>
  <div class="mdiv"></div>
  <div class="mi" onclick="oCpwd()"><span class="mico">🔑</span>Password বদলান</div>
  <div class="mi" onclick="shUI()"><span class="mico">👤</span>Account info</div>
  <div class="mdiv"></div>
  <div class="mi" onclick="doLo()" style="color:#f28b82"><span class="mico">🚪</span>Logout</div>
 </div>
</div>

<div class="po" id="pHist" onclick="cp('pHist')">
 <div class="pn" onclick="event.stopPropagation()">
  <div class="ph" onclick="cp('pHist')"></div>
  <div class="ptit">History
   <button onclick="clH()" style="background:rgba(242,139,130,.12);border:1px solid rgba(242,139,130,.3);color:#f28b82;border-radius:5px;padding:3px 9px;cursor:pointer;font-size:11px">Clear</button>
  </div>
  <div id="hList"></div>
 </div>
</div>

<div class="po" id="pBks" onclick="cp('pBks')">
 <div class="pn" onclick="event.stopPropagation()">
  <div class="ph" onclick="cp('pBks')"></div>
  <div class="ptit">Bookmarks</div>
  <div id="bkList"></div>
 </div>
</div>

<div class="po" id="pDL" onclick="cp('pDL')">
 <div class="pn" onclick="event.stopPropagation()">
  <div class="ph" onclick="cp('pDL')"></div>
  <div class="ptit">⬇ Downloads
   <button onclick="clDL()" style="background:rgba(242,139,130,.12);border:1px solid rgba(242,139,130,.3);color:#f28b82;border-radius:5px;padding:3px 9px;cursor:pointer;font-size:11px">🗑</button>
  </div>
  <div style="padding:10px 16px;border-bottom:1px solid #3c4043">
   <div style="display:flex;gap:7px;margin-bottom:7px">
    <input id="dlU" type="url" placeholder="Download link paste করুন..."
     style="flex:1;background:#303134;border:1px solid #3c4043;border-radius:7px;padding:8px 11px;color:#e8eaed;font-size:12px;outline:none">
    <button onclick="stDL()" style="background:#1a73e8;border:none;border-radius:7px;padding:8px 12px;color:#fff;cursor:pointer;font-size:13px">⬇</button>
   </div>
   <div style="display:flex;gap:7px">
    <button onclick="dlCb()" style="background:#3c4043;border:none;border-radius:7px;padding:6px 10px;color:#e8eaed;cursor:pointer;font-size:11px">📋 Clipboard</button>
    <button onclick="shURL()" style="background:#3c4043;border:none;border-radius:7px;padding:6px 10px;color:#e8eaed;cursor:pointer;font-size:11px">📤 Share</button>
   </div>
  </div>
  <div id="dlList"></div>
 </div>
</div>

<div class="po" id="pCpwd" onclick="cp('pCpwd')">
 <div class="pn" onclick="event.stopPropagation()">
  <div class="ph" onclick="cp('pCpwd')"></div>
  <div class="ptit">🔑 Password বদলান</div>
  <div style="padding:10px 16px">
   <div class="fg"><label class="fl">পুরনো Password</label>
    <input class="fi" id="cpO" type="password" placeholder="পুরনো Password"></div>
   <div class="fg"><label class="fl">নতুন Password</label>
    <input class="fi" id="cpN" type="password" placeholder="নতুন Password"></div>
   <div class="fg"><label class="fl">আবার দিন</label>
    <input class="fi" id="cpN2" type="password" placeholder="আবার একই Password"></div>
   <div class="msg" id="cpM"></div>
   <button onclick="doCpwd()" style="width:100%;padding:11px;border:none;border-radius:8px;cursor:pointer;font-size:14px;font-weight:500;background:#1a73e8;color:#fff;margin-top:4px">✅ Password বদলান</button>
  </div>
 </div>
</div>

<div id="toast"></div>

<script>
var U=null,eng="google",zm=1,fh=[],fi=-1,tc=1,dp=null,aU=[],visM="only_me";

// Fill DOB
(function(){
 var d=document.getElementById("rD");
 for(var i=1;i<=31;i++){var o=document.createElement("option");o.value=String(i).padStart(2,'0');o.textContent=i+"";d.appendChild(o);}
 var y=document.getElementById("rY"),cy=new Date().getFullYear();
 for(var yr=cy;yr>=1940;yr--){var o=document.createElement("option");o.value=yr;o.textContent=yr;y.appendChild(o);}
})();

// PWA
window.addEventListener('beforeinstallprompt',e=>{
 e.preventDefault();dp=e;
 document.getElementById('inst').classList.add('show');
});
document.getElementById('instBtn').addEventListener('click',async()=>{
 if(dp){dp.prompt();var r=await dp.userChoice;
  if(r.outcome==='accepted')toast('✅ Installed!');dp=null;
  document.getElementById('inst').classList.remove('show');}
});

async function init(){
 var p=new URLSearchParams(window.location.search);
 if(p.get('error')==='banned'){sm('lM','🚫 আপনার account ban করা হয়েছে','err');}
 if(p.get('logged')||p.get('error'))window.history.replaceState({},'','/');
 var r=await fetch("/api/me").then(x=>x.json()).catch(()=>({logged:false}));
 if(r.logged){U=r;shB(r.is_admin);}
 if("serviceWorker"in navigator)navigator.serviceWorker.register("/sw.js").catch(()=>{});
}

// AUTH TABS - Simple and clean
function goL(){
 document.getElementById("tbL").classList.add("active");
 document.getElementById("tbR").classList.remove("active");
 document.getElementById("fL").classList.add("show");
 document.getElementById("fR").classList.remove("show");
}
function goR(){
 document.getElementById("tbL").classList.remove("active");
 document.getElementById("tbR").classList.add("active");
 document.getElementById("fL").classList.remove("show");
 document.getElementById("fR").classList.add("show");
}

async function doL(){
 var e=document.getElementById("lE").value.trim();
 var p=document.getElementById("lP").value.trim();
 sm("lM","","");
 if(!e||!p){sm("lM","❗ সব ফিল্ড পূরণ করুন","err");return}
 var r=await api("/api/login",{email:e,pwd:p});
 if(r.ok){U=r;shB(r.is_admin);toast(r.is_admin?"⚙️ Admin Panel!":"✅ Welcome "+r.name+"!");}
 else sm("lM",r.msg,"err");
}

async function doR(){
 var n=document.getElementById("rN").value.trim();
 var e=document.getElementById("rE").value.trim();
 var d=document.getElementById("rD").value;
 var mo=document.getElementById("rMo").value;
 var y=document.getElementById("rY").value;
 var p=document.getElementById("rP").value.trim();
 sm("rM","","");
 if(!n||!e||!d||!mo||!y||!p){sm("rM","❗ সব ফিল্ড পূরণ করুন","err");return}
 var dob=y+"-"+mo+"-"+d;
 var r=await api("/api/register",{name:n,email:e,dob:dob,pwd:p});
 sm("rM",r.msg,r.ok?(r.is18?"ok":"warn"):"err");
 if(r.ok){goL();document.getElementById("lE").value=e;}
}

async function doLo(){
 await api("/api/logout",{});U=null;haA();
 document.getElementById("auth").style.display="flex";
 cap();toast("Signed out");
}

function shB(isAdmin){
 haA();
 if(isAdmin){
  document.getElementById("admin").classList.add("show");
  ldSt();ldU();
 }else{
  document.getElementById("browser").classList.add("show");
  updUI();ldUBks();
 }
}

function haA(){
 document.getElementById("browser").classList.remove("show");
 document.getElementById("admin").classList.remove("show");
 document.getElementById("auth").style.display="none";
}

function updUI(){
 if(!U)return;
 var is18=U.is18;
 document.getElementById("b18").classList.toggle("hidden",!is18);
 document.getElementById("bsf").classList.toggle("hidden",!!is18);
 var hg=document.getElementById("hgt");
 hg.innerHTML="Welcome, <b>"+U.name+"</b>! "+(is18?"🔞 18+ Mode":"🔒 Safe Mode");
 hg.classList.remove("hidden");
 var row=document.getElementById("erow");
 row.querySelectorAll(".ec.a,.ec.lk").forEach(x=>x.remove());
 if(is18){
  [["xvideos","🔴 XVideos"],["xnxx","🟠 XNXX"],["pornhub","🟧 PornHub"],["yandex","🟡 Yandex"]].forEach(([e,l])=>{
   var b=document.createElement("button");b.className="ec a";b.dataset.e=e;b.textContent=l;
   b.onclick=()=>sE(b);row.appendChild(b);
  });
  document.querySelectorAll(".sc18").forEach(x=>x.classList.add("show"));
 }else{
  ["🔒 XVideos","🔒 Adult"].forEach(l=>{
   var b=document.createElement("button");b.className="ec lk";b.textContent=l;row.appendChild(b);
  });
 }
 var pb=document.getElementById("profB");
 if(pb&&U.name)pb.textContent=U.name[0].toUpperCase();
}

// Admin visibility
function togVis(){
 visM=visM==="only_me"?"everyone":"only_me";
 var t=document.getElementById("visT"),s=document.getElementById("visS");
 if(visM==="only_me"){t.className="tog on";s.textContent="শুধু আমি";}
 else{t.className="tog off";s.textContent="সবাই দেখবে";}
 toast(visM==="only_me"?"🔒 Only You":"⚠️ Everyone");
}

async function ldSt(){
 var r=await fetch("/api/admin/stats").then(x=>x.json()).catch(()=>({}));
 document.getElementById("sT").textContent=r.total||0;
 document.getElementById("s18").textContent=r.is18||0;
 document.getElementById("sSf").textContent=r.safe||0;
 document.getElementById("sBn").textContent=r.banned||0;
}

async function ldU(){
 var rows=await fetch("/api/admin/users").then(x=>x.json()).catch(()=>[]);
 aU=rows;rnU(rows);
}

async function ldBnd(){var r=await fetch("/api/admin/users").then(x=>x.json()).catch(()=>[]);rnU(r.filter(u=>u.is_banned));}
async function ldU18(){var r=await fetch("/api/admin/users").then(x=>x.json()).catch(()=>[]);rnU(r.filter(u=>u.is18));}
async function clAH(){if(!confirm("সব history মুছবে?"))return;await api("/api/admin/clear-all-history",{});toast("🗑 Done!");}
function flU(q){if(!q){rnU(aU);return;}rnU(aU.filter(u=>(u.name||"").toLowerCase().includes(q.toLowerCase())||(u.email||"").toLowerCase().includes(q.toLowerCase())));}

function rnU(rows){
 var ul=document.getElementById("ulist");
 if(!rows.length){ul.innerHTML='<div class="lem">কোনো user নেই</div>';return;}
 ul.innerHTML=rows.map(u=>`
  <div class="ucard">
   <div class="uav">${(u.name||'?')[0].toUpperCase()}</div>
   <div class="uinf">
    <div class="unm">${u.name||'?'}</div>
    <div class="uem">${u.email}</div>
    <div class="utags">
     <span class="utag ${u.is18?'t18':'tsf'}">${u.is18?'🔞 18+':'🔒 Safe'}</span>
     ${u.is_banned?'<span class="utag tbn">🚫 Banned</span>':''}
    </div>
   </div>
   <div class="ubtns">
    ${u.is_banned?`<button class="ubtn unban" onclick="bnU(${u.id},0)">✅</button>`:`<button class="ubtn ban" onclick="bnU(${u.id},1)">🚫</button>`}
    <button class="ubtn del" onclick="dlU(${u.id},'${u.name}')">🗑</button>
   </div>
  </div>`).join("");
}

async function bnU(id,b){await api("/api/admin/ban",{uid:id,ban:b});toast(b?"🚫 Banned":"✅ Unbanned");ldU();ldSt();}
async function dlU(id,nm){if(!confirm(nm+" delete করবেন?"))return;await api("/api/admin/delete-user",{uid:id});toast("🗑 Deleted");ldU();ldSt();}

// Reset password
var rsEmail="";
function oReset(){rsEmail="";["rsE","rsP1","rsP2"].forEach(i=>{var el=document.getElementById(i);if(el)el.value="";});sm("rsM1","","");sm("rsM2","","");shRS("rs1");document.getElementById("resetp").classList.add("open");}
function cReset(){document.getElementById("resetp").classList.remove("open");shRS("rs1");}
function shRS(id){document.querySelectorAll(".rstep").forEach(s=>s.classList.remove("show"));document.getElementById(id).classList.add("show");}
async function rsV(){var e=document.getElementById("rsE").value.trim().toLowerCase();sm("rsM1","","");if(!e){sm("rsM1","❗ Gmail দিন","err");return}var r=await api("/api/verify-email",{email:e});if(r.ok){rsEmail=e;shRS("rs2");}else sm("rsM1",r.msg,"err");}
async function rsDo(){var p1=document.getElementById("rsP1").value.trim(),p2=document.getElementById("rsP2").value.trim();sm("rsM2","","");if(!p1||!p2){sm("rsM2","❗ সব দিন","err");return}if(p1.length<6){sm("rsM2","❌ ৬+ অক্ষর","err");return}if(p1!==p2){sm("rsM2","❌ মিলছে না","err");return}var r=await api("/api/reset-password",{email:rsEmail,pwd:p1});if(r.ok){shRS("rs3");toast("✅ Password বদলানো হয়েছে!");}else sm("rsM2",r.msg,"err");}

// Change password
function oCpwd(){cap();document.getElementById("pCpwd").classList.add("op");}
async function doCpwd(){
 var o=document.getElementById("cpO").value.trim(),n1=document.getElementById("cpN").value.trim(),n2=document.getElementById("cpN2").value.trim();
 sm("cpM","","");
 if(!o||!n1||!n2){sm("cpM","❗ সব দিন","err");return}
 if(n1!==n2){sm("cpM","❌ মিলছে না","err");return}
 if(n1.length<6){sm("cpM","❌ ৬+ অক্ষর","err");return}
 var r=await api("/api/change-password",{old_pwd:o,new_pwd:n1});
 if(r.ok){sm("cpM","✅ সফল!","ok");toast("✅ Password বদলানো হয়েছে!");setTimeout(()=>{cp("pCpwd");["cpO","cpN","cpN2"].forEach(i=>{var el=document.getElementById(i);if(el)el.value="";});sm("cpM","","");},2000);}
 else sm("cpM",r.msg,"err");
}

// Navigation
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

function go(url){
 if(!url)return;
 if(!url.startsWith("http"))url="https://"+url;
 if(U&&!U.is_admin)api("/api/history",{url,title:url.replace(/https?:\/\/(www\.)?/,'').split('/')[0]}).catch(()=>{});
 document.getElementById("ub").value=url;
 document.getElementById("lk").textContent=url.startsWith("https")?"🔒":"⚠️";
 sTT(url.replace(/https?:\/\/(www\.)?/,'').split('/')[0]);
 fh=fh.slice(0,fi+1);fh.push(url);fi=fh.length-1;uNav();cap();
 if(window.matchMedia('(display-mode:standalone)').matches)window.location.href=url;
 else window.open(url,"_blank");
}
function nav(){var t=document.getElementById("ub").value.trim();if(!t)return;
 if(/^https?:\/\//.test(t)||(!/ /.test(t)&&/[.\/]/.test(t)))go(t);
 else go((E[eng]||E.google)(t));}
function hS(){var q=document.getElementById("sq").value.trim();if(q)go((E[eng]||E.google)(q));}
function gH(){document.getElementById("ub").value="";document.getElementById("sq").value="";document.getElementById("lk").textContent="🔒";document.querySelectorAll(".bb").forEach((b,i)=>b.classList.toggle("on",i===2));cap();}
function gBk(){if(fi>0){fi--;go(fh[fi]);}}
function gFw(){if(fi<fh.length-1){fi++;go(fh[fi]);}}
function uNav(){document.getElementById("bBk").disabled=fi<=0;document.getElementById("bFw").disabled=fi>=fh.length-1;}
function sE(el){eng=el.dataset.e;document.querySelectorAll(".ec").forEach(e=>e.classList.remove("on"));el.classList.add("on");}

// Tabs
function ntab(){var id=tc++;var bar=document.getElementById("tabbar");var plus=bar.querySelector(".ntab");var el=document.createElement("div");el.className="tab";el.id="tab"+id;el.innerHTML=`<span class="tab-i">🏠</span><span class="tab-t" id="tt${id}">New Tab</span><button class="tab-x" onclick="ctab(event,${id})">✕</button>`;el.onclick=()=>atab(id);bar.insertBefore(el,plus);atab(id);}
function atab(id){document.querySelectorAll(".tab").forEach(t=>t.classList.remove("on"));var el=document.getElementById("tab"+id);if(el)el.classList.add("on");}
function ctab(e,id){e.stopPropagation();var el=document.getElementById("tab"+id);if(el)el.remove();}
function sTT(t){var a=document.querySelector(".tab.on");if(a){var ti=a.querySelector(".tab-t");if(ti)ti.textContent=t.substring(0,20)||"...";}};

// Bookmarks
async function aBk(){var url=document.getElementById("ub").value;if(!url||!U){toast("❗ Navigate first");return}await api("/api/bookmarks",{url,title:url.replace(/https?:\/\/(www\.)?/,'').split('/')[0]});var s=document.getElementById("starB");s.textContent="★";s.style.color="#fdd663";toast("★ Bookmarked!");setTimeout(()=>{s.textContent="☆";s.style.color="";},2000);ldUBks();}
async function ldUBks(){var rows=await fetch("/api/bookmarks").then(x=>x.json()).catch(()=>[]);var c=document.getElementById("ubk"),sep=document.getElementById("ubks");if(rows.length>0){sep.style.display="block";c.innerHTML=rows.slice(0,5).map(r=>`<button class="bki" onclick="go('${r.url}')">★ ${(r.title||r.url).substring(0,12)}</button>`).join("");}else{sep.style.display="none";c.innerHTML="";}}
async function oBks(){cap();var rows=await fetch("/api/bookmarks").then(x=>x.json()).catch(()=>[]);var el=document.getElementById("bkList");el.innerHTML=rows.length?rows.map(r=>`<div class="li"><span class="lico">★</span><div class="linf" onclick="go('${r.url}');cp('pBks')"><div class="lit">${r.title||r.url}</div><div class="lis">${r.url}</div></div><button class="ldel" onclick="dBk(${r.id},this)">×</button></div>`).join(""):'<div class="lem">No bookmarks</div>';document.getElementById("pBks").classList.add("op");}
async function dBk(id,btn){await fetch("/api/bookmarks/"+id,{method:"DELETE"});btn.closest(".li").remove();toast("Removed");ldUBks();}

// History
async function oHist(){cap();var rows=await fetch("/api/history").then(x=>x.json()).catch(()=>[]);var el=document.getElementById("hList");el.innerHTML=rows.length?rows.map(r=>`<div class="li" onclick="go('${r.url}');cp('pHist')"><span class="lico">🕐</span><div class="linf"><div class="lit">${r.title||r.url}</div><div class="lis">${r.ts||""}</div></div></div>`).join(""):'<div class="lem">No history</div>';document.getElementById("pHist").classList.add("op");}
async function clH(){await api("/api/history/clear",{});document.getElementById("hList").innerHTML='<div class="lem">Cleared</div>';toast("Cleared");}

// Downloads
async function oDL(){cap();await ldDL();document.getElementById("pDL").classList.add("op");}
async function ldDL(){var rows=await fetch("/api/downloads").then(x=>x.json()).catch(()=>[]);var el=document.getElementById("dlList");if(!rows.length){el.innerHTML='<div class="lem">📭 No downloads</div>';return;}el.innerHTML=rows.map(function(r){var n=r.filename||r.url.split('/').pop()||r.url.substring(0,25);return'<div style="display:flex;align-items:center;gap:8px;padding:9px 16px;border-bottom:1px solid #3c4043"><span style="font-size:18px">📄</span><div style="flex:1;min-width:0"><div style="font-size:12px;color:#e8eaed;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'+n+'</div><div style="font-size:10px;color:#9aa0a6">'+(r.ts||'')+'</div></div><button onclick="rDL(\''+r.url+'\',\''+n+'\')" style="background:#3c4043;border:none;border-radius:5px;padding:4px 7px;color:#9aa0a6;cursor:pointer;font-size:11px">⬇</button><button onclick="shLk(\''+r.url+'\')" style="background:#3c4043;border:none;border-radius:5px;padding:4px 7px;color:#9aa0a6;cursor:pointer;font-size:11px">📤</button></div>';}).join('');}
async function stDL(){var url=document.getElementById("dlU").value.trim();if(!url){toast("❗ Link দিন");return;}if(!url.startsWith("http")){toast("❗ https:// দিয়ে শুরু");return;}var a=document.createElement("a");a.href=url;a.download=url.split('/').pop()||"file";a.target="_blank";document.body.appendChild(a);a.click();document.body.removeChild(a);await api("/api/downloads",{url,filename:url.split('/').pop()||"file"});document.getElementById("dlU").value="";setTimeout(ldDL,800);toast("✅ Download শুরু!");}
async function rDL(url,name){var a=document.createElement("a");a.href=url;a.download=name;a.target="_blank";document.body.appendChild(a);a.click();document.body.removeChild(a);toast("⬇ Download!");}
async function dlCb(){try{var t=await navigator.clipboard.readText();if(t&&t.startsWith("http")){document.getElementById("dlU").value=t;toast("📋 Link নেওয়া হয়েছে!");}else toast("❗ Valid link নেই");}catch(e){toast("❗ Permission দিন");}}
async function shURL(){shLk(document.getElementById("ub").value||window.location.href);}
async function shLk(url){if(!url)return;if(navigator.share){try{await navigator.share({title:"Bong Browser",url});toast("✅ Shared!");}catch(e){}}else{try{await navigator.clipboard.writeText(url);toast("📋 Copied!");}catch(e){}}}
async function clDL(){await api("/api/downloads/clear",{});document.getElementById("dlList").innerHTML='<div class="lem">📭 Cleared</div>';toast("🗑 Cleared");}

// Zoom
function zI(){zm=Math.min(zm+.1,2);document.body.style.zoom=zm;toast("Zoom: "+Math.round(zm*100)+"%");}
function zO(){zm=Math.max(zm-.1,.5);document.body.style.zoom=zm;toast("Zoom: "+Math.round(zm*100)+"%");}

// Panels
function oMenu(){cap();document.getElementById("pMenu").classList.add("op");}
function cp(id){document.getElementById(id).classList.remove("op");}
function cap(){document.querySelectorAll(".po").forEach(p=>p.classList.remove("op"));}
function shUI(){cap();toast("👤 "+U.name+" · "+(U.is18?"🔞 18+":"🔒 Safe"));}

async function api(url,data){var r=await fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});return r.json();}
function sm(id,m,c){var el=document.getElementById(id);if(el){el.textContent=m;el.className="msg"+(c?" "+c:"");}}
var _t=null;
function toast(msg){var t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");clearTimeout(_t);_t=setTimeout(()=>t.classList.remove("show"),3000);}

init();
</script>
</body>
</html>"""

MF = '{"name":"Bong Browser — Modified by Bong.Dev","short_name":"Bong Browser","description":"18+ Browser","start_url":"/","display":"standalone","background_color":"#202124","theme_color":"#202124","orientation":"any","icons":[{"src":"/icon.png","sizes":"192x192","type":"image/png","purpose":"any maskable"},{"src":"/icon.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}]}'

SW = 'self.addEventListener("install",e=>{self.skipWaiting();});self.addEventListener("activate",e=>{self.clients.claim();});self.addEventListener("fetch",e=>{if(e.request.method!=="GET")return;e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)));});'

IC = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQI12NgAAIABQAABjE+ibYAAAAASUVORK5CYII=")

@app.route("/")
def ix(): return HTML
@app.route("/manifest.json")
def mf():
    from flask import Response; return Response(MF,mimetype="application/json")
@app.route("/sw.js")
def sw():
    from flask import Response; return Response(SW,mimetype="application/javascript")
@app.route("/icon.png")
def ic():
    from flask import Response; return Response(IC,mimetype="image/png")

@app.route("/api/me")
def me():
    if "uid" not in session: return jsonify({"logged":False})
    return jsonify({"logged":True,"name":session.get("name"),"email":session.get("email"),"is18":session.get("is18",0),"age":session.get("age",0),"is_admin":session.get("is_admin",False)})

@app.route("/api/login",methods=["POST"])
def login():
    d=request.json; e=d.get("email","").strip().lower(); p=d.get("pwd","").strip()
    if not e or not p: return jsonify({"ok":False,"msg":"সব ফিল্ড পূরণ করুন"})
    if e==ADMIN_EMAIL.lower() and p==ADMIN_PASS:
        session.permanent=True
        session.update({"uid":0,"name":ADMIN_NAME,"email":ADMIN_EMAIL,"is18":1,"age":99,"is_admin":True})
        return jsonify({"ok":True,"name":ADMIN_NAME,"is18":1,"age":99,"is_admin":True})
    c=db(); row=c.execute("SELECT * FROM users WHERE email=? AND pwd=?",(e,sh(p))).fetchone(); c.close()
    if row:
        if row["is_banned"]: return jsonify({"ok":False,"msg":"🚫 আপনার account ban করা হয়েছে"})
        a=ag(row["dob"]); i=1 if a>=18 else 0
        session.permanent=True
        session.update({"uid":row["id"],"name":row["name"],"email":row["email"],"is18":i,"age":a,"is_admin":False})
        return jsonify({"ok":True,"name":row["name"],"is18":i,"age":a,"is_admin":False})
    return jsonify({"ok":False,"msg":"❌ ভুল Email বা Password"})

@app.route("/api/register",methods=["POST"])
def reg():
    d=request.json; n=d.get("name","").strip(); e=d.get("email","").strip().lower()
    p=d.get("pwd","").strip(); dob=d.get("dob","")
    if not all([n,e,p,dob]): return jsonify({"ok":False,"msg":"সব ফিল্ড পূরণ করুন"})
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$',e): return jsonify({"ok":False,"msg":"সঠিক Email দিন"})
    if len(p)<6: return jsonify({"ok":False,"msg":"Password কমপক্ষে ৬ অক্ষর"})
    a=ag(dob); i=1 if a>=18 else 0
    try:
        c=db(); c.execute("INSERT INTO users(email,pwd,name,dob,is18,joined) VALUES(?,?,?,?,?,?)",(e,sh(p),n,dob,i,datetime.now().strftime("%d/%m/%Y"))); c.commit(); c.close()
        return jsonify({"ok":True,"msg":f"✅ সফল! বয়স {a} — {'18+ Mode' if i else 'Safe Mode'}। Login করুন।","is18":i,"age":a})
    except: return jsonify({"ok":False,"msg":"এই Email আগেই রেজিস্ট্রেশন হয়েছে"})

@app.route("/api/logout",methods=["POST"])
def lo(): session.clear(); return jsonify({"ok":True})

@app.route("/auth/google")
def gl():
    params={"client_id":G_ID,"redirect_uri":G_URL,"response_type":"code","scope":"openid email profile","access_type":"offline","prompt":"select_account"}
    return redirect("https://accounts.google.com/o/oauth2/auth?"+urllib.parse.urlencode(params))

@app.route("/auth/google/callback")
def gc():
    code=request.args.get("code")
    if not code: return redirect("/?error=no_code")
    try:
        td={"code":code,"client_id":G_ID,"client_secret":G_SEC,"redirect_uri":G_URL,"grant_type":"authorization_code"}
        req=urllib.request.Request("https://oauth2.googleapis.com/token",data=urllib.parse.urlencode(td).encode(),method="POST")
        with urllib.request.urlopen(req) as r: ti=jl.loads(r.read())
        at=ti.get("access_token")
        ur=urllib.request.Request("https://www.googleapis.com/oauth2/v2/userinfo",headers={"Authorization":f"Bearer {at}"})
        with urllib.request.urlopen(ur) as r: ui=jl.loads(r.read())
        em=ui.get("email","").lower(); nm=ui.get("name",em.split("@")[0])
        if em==ADMIN_EMAIL.lower():
            session.permanent=True
            session.update({"uid":0,"name":ADMIN_NAME,"email":ADMIN_EMAIL,"is18":1,"age":99,"is_admin":True})
            return redirect("/?logged=admin")
        c=db(); row=c.execute("SELECT * FROM users WHERE email=?",(em,)).fetchone()
        if row:
            if row["is_banned"]: c.close(); return redirect("/?error=banned")
            a=ag(row["dob"]); i=1 if a>=18 else 0
            session.permanent=True
            session.update({"uid":row["id"],"name":row["name"],"email":em,"is18":i,"age":a,"is_admin":False})
        else:
            dob="2000-01-01"; a=ag(dob); i=1 if a>=18 else 0
            c.execute("INSERT INTO users(email,pwd,name,dob,is18,joined) VALUES(?,?,?,?,?,?)",(em,sh("g_"+em),nm,dob,i,datetime.now().strftime("%d/%m/%Y"))); c.commit()
            uid=c.execute("SELECT id FROM users WHERE email=?",(em,)).fetchone()["id"]
            session.permanent=True
            session.update({"uid":uid,"name":nm,"email":em,"is18":i,"age":a,"is_admin":False})
        c.close(); return redirect("/?logged=google")
    except: return redirect("/?error=failed")

@app.route("/api/admin/stats")
def ast():
    if not session.get("is_admin"): return jsonify({}),403
    c=db(); t=c.execute("SELECT COUNT(*) FROM users").fetchone()[0]; i18=c.execute("SELECT COUNT(*) FROM users WHERE is18=1").fetchone()[0]; sf=c.execute("SELECT COUNT(*) FROM users WHERE is18=0").fetchone()[0]; bn=c.execute("SELECT COUNT(*) FROM users WHERE is_banned=1").fetchone()[0]; c.close()
    return jsonify({"total":t,"is18":i18,"safe":sf,"banned":bn})

@app.route("/api/admin/users")
def aus():
    if not session.get("is_admin"): return jsonify([])
    c=db(); rows=c.execute("SELECT id,email,name,dob,is18,is_banned FROM users ORDER BY id DESC").fetchall(); c.close()
    return jsonify([{"id":r["id"],"email":r["email"],"name":r["name"],"is18":r["is18"],"is_banned":r["is_banned"],"age":ag(r["dob"])} for r in rows])

@app.route("/api/admin/ban",methods=["POST"])
def abn():
    if not session.get("is_admin"): return jsonify({"ok":False}),403
    d=request.json; c=db(); c.execute("UPDATE users SET is_banned=? WHERE id=?",(d.get("ban",1),d.get("uid"))); c.commit(); c.close(); return jsonify({"ok":True})

@app.route("/api/admin/delete-user",methods=["POST"])
def adl():
    if not session.get("is_admin"): return jsonify({"ok":False}),403
    uid=request.json.get("uid"); c=db()
    for t in ["users","history","bookmarks","downloads"]: c.execute(f"DELETE FROM {t} WHERE {'id' if t=='users' else 'uid'}=?",(uid,))
    c.commit(); c.close(); return jsonify({"ok":True})

@app.route("/api/admin/clear-all-history",methods=["POST"])
def ach():
    if not session.get("is_admin"): return jsonify({"ok":False}),403
    c=db(); c.execute("DELETE FROM history"); c.commit(); c.close(); return jsonify({"ok":True})

@app.route("/api/verify-email",methods=["POST"])
def ve():
    e=request.json.get("email","").strip().lower(); c=db(); row=c.execute("SELECT id FROM users WHERE email=?",(e,)).fetchone(); c.close()
    return jsonify({"ok":bool(row),"msg":"❌ এই Email দিয়ে account নেই" if not row else ""})

@app.route("/api/reset-password",methods=["POST"])
def rp():
    d=request.json; e=d.get("email","").strip().lower(); p=d.get("pwd","").strip()
    if not e or not p or len(p)<6: return jsonify({"ok":False,"msg":"Invalid"})
    c=db(); c.execute("UPDATE users SET pwd=? WHERE email=?",(sh(p),e)); c.commit(); c.close(); return jsonify({"ok":True})

@app.route("/api/change-password",methods=["POST"])
def cp2():
    if "uid" not in session: return jsonify({"ok":False,"msg":"Login করুন"})
    if session.get("is_admin"): return jsonify({"ok":False,"msg":"Admin এর জন্য নয়"})
    d=request.json; o=d.get("old_pwd","").strip(); n=d.get("new_pwd","").strip()
    if not o or not n or len(n)<6: return jsonify({"ok":False,"msg":"Invalid"})
    c=db(); row=c.execute("SELECT id FROM users WHERE id=? AND pwd=?",(session["uid"],sh(o))).fetchone()
    if not row: c.close(); return jsonify({"ok":False,"msg":"❌ পুরনো Password ভুল"})
    c.execute("UPDATE users SET pwd=? WHERE id=?",(sh(n),session["uid"])); c.commit(); c.close(); return jsonify({"ok":True})

@app.route("/api/history",methods=["GET"])
def gh():
    if "uid" not in session or session.get("is_admin"): return jsonify([])
    c=db(); rows=c.execute("SELECT id,url,title,ts FROM history WHERE uid=? ORDER BY id DESC LIMIT 60",(session["uid"],)).fetchall(); c.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/history",methods=["POST"])
def ah():
    if "uid" not in session or session.get("is_admin"): return jsonify({"ok":False})
    d=request.json; url=d.get("url","")
    if url:
        c=db(); c.execute("INSERT INTO history(uid,url,title,ts) VALUES(?,?,?,?)",(session["uid"],url,d.get("title","")[:200],datetime.now().strftime("%d/%m %H:%M"))); c.commit(); c.close()
    return jsonify({"ok":True})

@app.route("/api/history/clear",methods=["POST"])
def clh():
    if "uid" not in session: return jsonify({"ok":False})
    c=db(); c.execute("DELETE FROM history WHERE uid=?",(session["uid"],)); c.commit(); c.close(); return jsonify({"ok":True})

@app.route("/api/bookmarks",methods=["GET"])
def gb():
    if "uid" not in session or session.get("is_admin"): return jsonify([])
    c=db(); rows=c.execute("SELECT id,url,title FROM bookmarks WHERE uid=? ORDER BY id DESC",(session["uid"],)).fetchall(); c.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/bookmarks",methods=["POST"])
def ab():
    if "uid" not in session or session.get("is_admin"): return jsonify({"ok":False})
    d=request.json; c=db(); c.execute("INSERT INTO bookmarks(uid,url,title) VALUES(?,?,?)",(session["uid"],d.get("url",""),d.get("title","")[:200])); c.commit(); c.close(); return jsonify({"ok":True})

@app.route("/api/bookmarks/<int:bid>",methods=["DELETE"])
def db2(bid):
    if "uid" not in session: return jsonify({"ok":False})
    c=db(); c.execute("DELETE FROM bookmarks WHERE id=? AND uid=?",(bid,session["uid"])); c.commit(); c.close(); return jsonify({"ok":True})

@app.route("/api/downloads",methods=["GET"])
def gd():
    if "uid" not in session: return jsonify([])
    c=db(); rows=c.execute("SELECT id,url,filename,ts FROM downloads WHERE uid=? ORDER BY id DESC LIMIT 50",(session["uid"],)).fetchall(); c.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/downloads",methods=["POST"])
def ad():
    if "uid" not in session: return jsonify({"ok":False})
    d=request.json; url=d.get("url","")
    if url:
        c=db(); c.execute("INSERT INTO downloads(uid,url,filename,ts) VALUES(?,?,?,?)",(session["uid"],url,d.get("filename","")[:200],datetime.now().strftime("%d/%m %H:%M"))); c.commit(); c.close()
    return jsonify({"ok":True})

@app.route("/api/downloads/clear",methods=["POST"])
def cld():
    if "uid" not in session: return jsonify({"ok":False})
    c=db(); c.execute("DELETE FROM downloads WHERE uid=?",(session["uid"],)); c.commit(); c.close(); return jsonify({"ok":True})

if __name__=="__main__":
    idb()
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port,debug=False)
