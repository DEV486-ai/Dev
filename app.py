"""
BONG BROWSER v7.0 — Modified by Bong.Dev ⚡
Password Reset Feature Added!
"""
from flask import Flask, request, jsonify, session
import sqlite3, hashlib, os, re, base64
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = "bongbrowser_bongdev_2025_v7"
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bong.db")

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = db()
    c.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE, pwd TEXT,
        name TEXT, dob TEXT, is18 INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER, url TEXT, title TEXT, ts TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bookmarks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER, url TEXT, title TEXT)''')
    c.commit(); c.close()

def sha(p): return hashlib.sha256(p.encode()).hexdigest()

def age(dob):
    try:
        d = datetime.strptime(dob, "%Y-%m-%d").date()
        t = date.today()
        return t.year-d.year-((t.month,t.day)<(d.month,d.day))
    except: return 0

HTML = r"""<!DOCTYPE html>
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
<link rel="apple-touch-icon" href="/icon.png">
<link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#202124;--bg1:#292a2d;--bg2:#35363a;--bg3:#3c4043;
  --urlbar:#303134;--border:#5f6368;
  --text:#e8eaed;--text2:#9aa0a6;--text3:#5f6368;
  --blue:#8ab4f8;--blue2:#1a73e8;
  --red:#f28b82;--green:#81c995;--gold:#fdd663;
  --hover:rgba(255,255,255,.08);--pressed:rgba(255,255,255,.12);
  --st:env(safe-area-inset-top,0px);--sb:env(safe-area-inset-bottom,0px);
}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%;overflow:hidden}
body{font-family:'Roboto',sans-serif;background:var(--bg);color:var(--text);
  display:flex;flex-direction:column;height:100dvh}
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-thumb{background:var(--bg3);border-radius:2px}

/* ══ AUTH ══ */
#auth-scr{position:absolute;inset:0;display:flex;align-items:center;
  justify-content:center;overflow-y:auto;padding:20px;background:var(--bg);z-index:100}
#auth-scr::before{content:'';position:fixed;inset:0;pointer-events:none;
  background:radial-gradient(ellipse 60% 40% at 30% 40%,rgba(138,180,248,.07) 0%,transparent 60%),
             radial-gradient(ellipse 40% 50% at 75% 60%,rgba(129,201,149,.05) 0%,transparent 60%)}

.acard{position:relative;z-index:1;background:var(--bg1);
  border:1px solid var(--bg3);border-radius:12px;
  padding:28px 24px;width:100%;max-width:400px;
  box-shadow:0 4px 24px rgba(0,0,0,.5);
  animation:cardIn .4s ease both}
@keyframes cardIn{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}

.logo-row{display:flex;align-items:center;justify-content:center;gap:10px;margin-bottom:4px}
.logo-ico{width:38px;height:38px;border-radius:50%;
  background:linear-gradient(135deg,#8ab4f8,#1a73e8);
  display:flex;align-items:center;justify-content:center;
  font-size:18px;font-weight:900;color:#202124;font-family:'Google Sans',sans-serif}
.logo-txt{font-size:19px;font-weight:700;color:var(--text);font-family:'Google Sans',sans-serif}
.logo-sub{text-align:center;font-size:11px;color:var(--text2);margin-bottom:20px;letter-spacing:.5px}

/* Tab buttons */
.atabs{display:flex;border-bottom:1px solid var(--bg3);margin-bottom:18px}
.atab{flex:1;padding:10px;background:none;border:none;cursor:pointer;
  color:var(--text2);font-family:'Roboto',sans-serif;font-size:13px;font-weight:500;
  transition:all .2s;border-bottom:2px solid transparent;margin-bottom:-1px}
.atab.on{color:var(--blue);border-bottom-color:var(--blue)}

.fp{display:none}.fp.on{display:block}

.fg{margin-bottom:12px}
.fl{font-size:10px;color:var(--text2);font-weight:500;letter-spacing:.5px;
  text-transform:uppercase;margin-bottom:4px;display:block}
.fi{width:100%;background:var(--urlbar);border:1px solid var(--bg3);
  border-radius:8px;padding:10px 13px;color:var(--text);
  font-family:'Roboto',sans-serif;font-size:14px;outline:none;transition:all .2s}
.fi:focus{border-color:var(--blue);background:var(--bg3)}
.fi::placeholder{color:var(--text3)}
input[type=date].fi{color-scheme:dark}

.amsg{min-height:18px;font-size:11px;text-align:center;margin:6px 0;line-height:1.5}
.amsg.e{color:var(--red)}.amsg.ok{color:var(--green)}.amsg.w{color:var(--gold)}

.abtn{width:100%;padding:12px;border:none;border-radius:8px;cursor:pointer;
  font-family:'Google Sans',sans-serif;font-size:14px;font-weight:500;
  transition:all .15s;margin-top:4px}
.abtn:active{transform:scale(.98)}
.abtn-p{background:var(--blue2);color:#fff}
.abtn-p:hover{background:#1557b0}
.abtn-s{background:#a8c7fa;color:#202124}
.abtn-s:hover{background:#c4d7f5}
.abtn-o{background:transparent;border:1px solid var(--bg3)!important;color:var(--text2)}
.abtn-o:hover{background:var(--hover);color:var(--text)}
.abtn-r{background:rgba(242,139,130,.15);border:1px solid rgba(242,139,130,.3)!important;color:var(--red)}
.abtn-r:hover{background:rgba(242,139,130,.25)}

/* Forgot password link */
.forgot-link{text-align:right;margin-top:-4px;margin-bottom:8px}
.forgot-link a{font-size:11px;color:var(--blue);cursor:pointer;text-decoration:none;font-weight:500}
.forgot-link a:hover{text-decoration:underline}

.afoot{text-align:center;font-size:10px;color:var(--text3);margin-top:14px}
.afoot span{color:var(--blue)}

/* Reset password panel */
#reset-panel{
  position:fixed;inset:0;z-index:200;
  background:rgba(0,0,0,.7);display:none;
  align-items:center;justify-content:center;padding:20px;
}
#reset-panel.open{display:flex}
.reset-card{
  background:var(--bg1);border:1px solid var(--bg3);
  border-radius:12px;padding:24px 20px;
  width:100%;max-width:380px;
  box-shadow:0 8px 32px rgba(0,0,0,.6);
  animation:cardIn .3s ease both;
}
.reset-title{font-family:'Google Sans',sans-serif;font-size:17px;font-weight:700;
  color:var(--text);margin-bottom:4px}
.reset-sub{font-size:12px;color:var(--text2);margin-bottom:18px;line-height:1.5}
.reset-step{display:none}.reset-step.on{display:block}

/* ══ BROWSER ══ */
#bscr{display:none;flex-direction:column;height:100%;background:var(--bg)}
#bscr.show{display:flex}

/* Install bar */
#inst-bar{background:var(--blue2);padding:9px 14px;
  display:none;align-items:center;gap:10px;flex-shrink:0}
#inst-bar.show{display:flex}
.ib-txt{flex:1;font-size:12px;color:#fff;font-weight:500}
.ib-btn{background:#fff;color:var(--blue2);border:none;border-radius:18px;
  padding:5px 13px;font-size:11px;font-weight:700;cursor:pointer;flex-shrink:0}
.ib-cls{background:none;border:none;color:rgba(255,255,255,.7);
  font-size:18px;cursor:pointer;flex-shrink:0}

/* Tab bar */
#tab-bar{background:var(--bg2);display:flex;align-items:flex-end;
  padding:7px 8px 0;gap:1px;flex-shrink:0;
  padding-top:calc(7px + var(--st));
  overflow-x:auto;scrollbar-width:none;min-height:42px}
#tab-bar::-webkit-scrollbar{display:none}
.tab{display:flex;align-items:center;gap:7px;padding:0 11px;height:33px;
  background:var(--bg);opacity:.7;border-radius:8px 8px 0 0;
  min-width:130px;max-width:190px;cursor:pointer;flex-shrink:0;
  position:relative;transition:all .15s;border:1px solid var(--bg3);border-bottom:none}
.tab.active{background:var(--bg);opacity:1;border-color:var(--bg3)}
.tab.active::after{content:'';position:absolute;bottom:-1px;left:0;right:0;
  height:1px;background:var(--bg)}
.tab-fav{font-size:12px;flex-shrink:0}
.tab-title{flex:1;font-size:11px;color:var(--text2);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tab.active .tab-title{color:var(--text)}
.tab-x{width:16px;height:16px;border-radius:50%;background:none;border:none;
  cursor:pointer;color:var(--text2);font-size:11px;
  display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:all .15s}
.tab-x:hover{background:var(--hover);color:var(--text)}
.newtab-btn{width:26px;height:26px;border-radius:50%;background:none;border:none;
  cursor:pointer;color:var(--text2);font-size:17px;
  display:flex;align-items:center;justify-content:center;
  flex-shrink:0;align-self:center;margin-left:4px;transition:all .15s}
.newtab-btn:hover{background:var(--hover);color:var(--text)}

/* Toolbar */
#toolbar{background:var(--bg2);border-bottom:1px solid var(--bg3);
  display:flex;align-items:center;padding:7px 10px;gap:5px;flex-shrink:0}
.nb{width:34px;height:34px;border-radius:50%;background:none;border:none;
  cursor:pointer;color:var(--text2);font-size:18px;
  display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:all .15s}
.nb:hover{background:var(--hover);color:var(--text)}
.nb:active{background:var(--pressed)}
.nb:disabled{opacity:.3;pointer-events:none}

#uw{flex:1;height:38px;background:var(--urlbar);border-radius:20px;
  display:flex;align-items:center;padding:0 14px;gap:8px;
  transition:all .2s;border:1px solid transparent}
#uw:focus-within{background:#fff;box-shadow:0 1px 6px rgba(32,33,36,.28)}
#lk{font-size:13px;flex-shrink:0;color:var(--text2)}
#uw:focus-within #lk{color:var(--blue2)}
#ub{flex:1;background:none;border:none;outline:none;color:var(--text);
  font-family:'Roboto',sans-serif;font-size:14px;min-width:0}
#uw:focus-within #ub{color:#202124}
#ub::placeholder{color:var(--text3)}
.ustar{background:none;border:none;cursor:pointer;color:var(--text2);
  font-size:16px;padding:2px;flex-shrink:0;transition:color .15s}
.ustar:hover{color:var(--gold)}

.rtools{display:flex;align-items:center;gap:3px}
.tb2{width:34px;height:34px;border-radius:50%;background:none;border:none;
  cursor:pointer;color:var(--text2);font-size:17px;
  display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:all .15s}
.tb2:hover{background:var(--hover);color:var(--text)}
.profbtn{width:28px;height:28px;border-radius:50%;
  background:linear-gradient(135deg,var(--blue2),#0d47a1);
  display:flex;align-items:center;justify-content:center;
  color:#fff;font-size:12px;font-weight:700;cursor:pointer;
  flex-shrink:0;border:2px solid var(--blue);font-family:'Google Sans',sans-serif}

/* Progress */
#prog{height:3px;background:linear-gradient(90deg,var(--blue2),#4285f4,#34a853);
  transform:scaleX(0);transform-origin:left;transition:transform .25s;
  flex-shrink:0;display:none}

/* Bookmarks bar */
#bkbar{background:var(--bg2);border-bottom:1px solid var(--bg3);
  display:flex;align-items:center;padding:4px 10px;gap:2px;
  flex-shrink:0;overflow-x:auto;scrollbar-width:none}
#bkbar::-webkit-scrollbar{display:none}
.bki{display:flex;align-items:center;gap:5px;padding:4px 10px;border-radius:18px;
  cursor:pointer;font-size:12px;color:var(--text2);white-space:nowrap;
  transition:all .15s;border:none;background:none;font-family:'Roboto',sans-serif}
.bki:hover{background:var(--hover);color:var(--text)}
.bki:active{background:var(--pressed)}
.bksep{width:1px;height:16px;background:var(--bg3);flex-shrink:0;margin:0 2px}

/* Content */
#ct{flex:1;position:relative;overflow:hidden;background:#fff}

/* Home */
#hp{position:absolute;inset:0;overflow-y:auto;background:var(--bg);
  display:flex;flex-direction:column;align-items:center;padding:28px 18px 100px}
#hp::before{content:'';position:fixed;inset:0;pointer-events:none;
  background:radial-gradient(ellipse 60% 40% at 30% 35%,rgba(138,180,248,.08) 0%,transparent 60%),
             radial-gradient(ellipse 40% 50% at 75% 60%,rgba(129,201,149,.05) 0%,transparent 60%)}

.hlogo{font-family:'Google Sans',sans-serif;font-size:clamp(30px,9vw,52px);
  font-weight:700;margin-bottom:4px;line-height:1}
.hlogo .b{color:#8ab4f8}.hlogo .o{color:#f28b82}.hlogo .n{color:#fdd663}
.hlogo .g{color:#81c995}.hlogo .d2{color:#f28b82}.hlogo .e2{color:#fdd663}.hlogo .v2{color:#81c995}
.hsub{font-size:11px;color:var(--text2);letter-spacing:2px;margin-bottom:8px}
.mbadge{display:inline-flex;align-items:center;gap:4px;padding:3px 11px;
  border-radius:18px;font-size:10px;font-weight:500;margin-bottom:16px}
.m18{background:rgba(242,139,130,.1);border:1px solid rgba(242,139,130,.25);color:var(--red)}
.msf{background:rgba(129,201,149,.08);border:1px solid rgba(129,201,149,.2);color:var(--green)}
.hidden{display:none!important}
.hgreet{font-size:13px;color:var(--text2);margin-bottom:18px;text-align:center}
.hgreet b{color:var(--blue)}

/* Search */
.hsw{width:100%;max-width:580px;margin-bottom:14px}
.hsb{display:flex;align-items:center;gap:10px;height:48px;
  background:var(--urlbar);border:1px solid var(--bg3);
  border-radius:24px;padding:0 14px;transition:all .25s}
.hsb:focus-within{background:#fff;border-color:transparent;
  box-shadow:0 2px 10px rgba(0,0,0,.4)}
.hsb input{flex:1;background:none;border:none;outline:none;color:var(--text);
  font-family:'Roboto',sans-serif;font-size:15px}
.hsb:focus-within input{color:#202124}
.hsb input::placeholder{color:var(--text3)}
.sico{font-size:17px;color:var(--text2);flex-shrink:0}
.hsb:focus-within .sico{color:var(--blue2)}
.sgbtn{background:var(--blue2);border:none;border-radius:18px;cursor:pointer;
  padding:7px 15px;font-family:'Google Sans',sans-serif;font-size:12px;
  font-weight:500;color:#fff;flex-shrink:0;transition:background .15s}
.sgbtn:hover{background:#1557b0}

/* Engine row */
.erow{display:flex;gap:5px;flex-wrap:wrap;justify-content:center;
  max-width:580px;margin-bottom:24px}
.ec{padding:4px 11px;border-radius:14px;border:1px solid var(--bg3);
  font-size:10px;font-weight:500;cursor:pointer;color:var(--text2);
  font-family:'Roboto',sans-serif;transition:all .15s;background:none}
.ec:hover{background:var(--hover);color:var(--text);border-color:var(--text3)}
.ec.on{background:rgba(138,180,248,.1);color:var(--blue);border-color:rgba(138,180,248,.35)}
.ec.a{color:var(--red);border-color:rgba(242,139,130,.2)}
.ec.a.on{background:rgba(242,139,130,.1);border-color:rgba(242,139,130,.4)}
.ec.lk{color:var(--text3);border-color:var(--bg3);cursor:not-allowed}

/* Shortcuts */
.sgrid{display:grid;grid-template-columns:repeat(4,1fr);
  gap:10px;width:100%;max-width:580px;margin-bottom:24px}
@media(max-width:360px){.sgrid{grid-template-columns:repeat(3,1fr)}}
.scut{display:flex;flex-direction:column;align-items:center;
  gap:6px;padding:12px 4px;border-radius:12px;cursor:pointer;
  transition:all .2s;border:1px solid transparent}
.scut:hover{background:var(--hover);border-color:var(--bg3)}
.scut:active{transform:scale(.95)}
.scico{width:50px;height:50px;border-radius:14px;display:flex;align-items:center;
  justify-content:center;font-size:20px;box-shadow:0 2px 8px rgba(0,0,0,.4)}
.sclbl{font-size:10px;color:var(--text2);font-weight:400;text-align:center}
.sc18{display:none}.sc18.show{display:flex}

.hwm{font-size:9px;color:var(--text3);letter-spacing:1px;font-family:'Roboto',sans-serif}
.hwm b{color:var(--blue)}

/* Panels */
.po{position:fixed;inset:0;z-index:400;background:rgba(0,0,0,.6);
  display:none;align-items:flex-end}
.po.op{display:flex}
.pn{background:var(--bg1);border-radius:16px 16px 0 0;border:1px solid var(--bg3);
  border-bottom:none;padding:10px 0 18px;width:100%;max-height:80vh;overflow-y:auto;
  animation:su .25s ease both}
@keyframes su{from{transform:translateY(100%)}to{transform:translateY(0)}}
.ph{width:30px;height:3px;background:var(--bg3);border-radius:2px;
  margin:0 auto 12px;cursor:pointer}
.ptitle{font-size:13px;font-weight:500;color:var(--text);
  padding:8px 18px 10px;border-bottom:1px solid var(--bg3);
  display:flex;justify-content:space-between;align-items:center;
  font-family:'Google Sans',sans-serif}
.mi{display:flex;align-items:center;gap:13px;padding:12px 18px;
  cursor:pointer;color:var(--text);font-size:14px;transition:background .12s;
  font-family:'Roboto',sans-serif}
.mi:hover{background:var(--hover)}
.mi:active{background:var(--pressed)}
.mico{font-size:18px;width:24px;text-align:center;color:var(--text2)}
.msc{margin-left:auto;font-size:10px;color:var(--text3)}
.mdiv{height:1px;background:var(--bg3);margin:3px 0}

/* List items */
.li{display:flex;align-items:center;gap:12px;padding:10px 18px;
  cursor:pointer;transition:background .12s}
.li:hover{background:var(--hover)}
.li:active{background:var(--pressed)}
.lico{font-size:16px;flex-shrink:0;color:var(--text2)}
.linf{flex:1;min-width:0}
.lit{font-size:13px;color:var(--text);font-weight:400;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.lis{font-size:11px;color:var(--text2);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px}
.ldel{background:none;border:none;color:var(--text2);cursor:pointer;
  font-size:16px;padding:4px 6px;border-radius:50%;flex-shrink:0;transition:all .15s}
.ldel:hover{background:var(--hover);color:var(--red)}
.lem{text-align:center;color:var(--text2);font-size:13px;padding:24px}

/* Bottom nav */
#bnav{background:var(--bg2);border-top:1px solid var(--bg3);
  flex-shrink:0;padding-bottom:var(--sb)}
.bni{display:flex;justify-content:space-around;padding:4px 0}
.bb{display:flex;flex-direction:column;align-items:center;gap:2px;
  padding:6px 14px;cursor:pointer;color:var(--text2);background:none;border:none;
  font-size:9px;font-weight:500;font-family:'Roboto',sans-serif;
  border-radius:9px;transition:all .15s}
.bb:active,.bb.on{color:var(--blue);background:rgba(138,180,248,.1)}
.bico{font-size:20px;line-height:1}

/* Toast */
#toast{position:fixed;bottom:78px;left:50%;
  transform:translateX(-50%) translateY(8px);
  background:var(--bg3);color:var(--text);padding:10px 18px;
  border-radius:8px;font-size:13px;font-family:'Roboto',sans-serif;
  z-index:9999;opacity:0;transition:all .25s;pointer-events:none;
  white-space:nowrap;max-width:88vw;text-align:center;
  box-shadow:0 4px 14px rgba(0,0,0,.4)}
#toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
</style>
</head>
<body>

<!-- ══ AUTH ══ -->
<div id="auth-scr">
 <div class="acard">
  <div class="logo-row">
   <div class="logo-ico">B</div>
   <div class="logo-txt">Bong Browser</div>
  </div>
  <div class="logo-sub">Modified by Bong.Dev ⚡</div>

  <div class="atabs">
   <button class="atab on" onclick="stab('l')">Login</button>
   <button class="atab" onclick="stab('r')">Register</button>
  </div>

  <!-- LOGIN -->
  <div class="fp on" id="fp-l">
   <div class="fg">
    <label class="fl">Gmail Address</label>
    <input class="fi" id="le" type="email" placeholder="yourname@gmail.com" autocomplete="email">
   </div>
   <div class="fg">
    <label class="fl">Password</label>
    <input class="fi" id="lp" type="password" placeholder="••••••••" onkeydown="if(event.key==='Enter')doLogin()">
   </div>
   <!-- FORGOT PASSWORD LINK -->
   <div class="forgot-link">
    <a onclick="openReset()">🔑 Password ভুলে গেছেন?</a>
   </div>
   <div class="amsg" id="lm"></div>
   <button class="abtn abtn-p" onclick="doLogin()">Login</button>
  </div>

  <!-- REGISTER -->
  <div class="fp" id="fp-r">
   <div class="fg">
    <label class="fl">পুরো নাম</label>
    <input class="fi" id="rn" type="text" placeholder="আপনার নাম">
   </div>
   <div class="fg">
    <label class="fl">Gmail Address</label>
    <input class="fi" id="re" type="email" placeholder="yourname@gmail.com">
   </div>
   <div class="fg">
    <label class="fl">জন্ম তারিখ (বয়স যাচাই হবে)</label>
    <input class="fi" id="rd" type="date" max="2099-12-31">
   </div>
   <div class="fg">
    <label class="fl">Password (কমপক্ষে ৬ অক্ষর)</label>
    <input class="fi" id="rp" type="password" placeholder="••••••••" onkeydown="if(event.key==='Enter')doReg()">
   </div>
   <div class="amsg" id="rm"></div>
   <button class="abtn abtn-s" onclick="doReg()">Register</button>
  </div>

  <div class="afoot">🔒 ডেটা সুরক্ষিত · <span>Modified by Bong.Dev</span></div>
 </div>
</div>

<!-- ══ PASSWORD RESET PANEL ══ -->
<div id="reset-panel">
 <div class="reset-card">
  <div class="reset-title">🔑 Password Reset</div>
  <div class="reset-sub">আপনার Gmail দিয়ে নতুন Password সেট করুন</div>

  <!-- Step 1: Email verify -->
  <div class="reset-step on" id="rs1">
   <div class="fg">
    <label class="fl">আপনার Gmail Address</label>
    <input class="fi" id="reset-email" type="email" placeholder="yourname@gmail.com">
   </div>
   <div class="amsg" id="rs1-msg"></div>
   <button class="abtn abtn-p" onclick="verifyResetEmail()" style="margin-bottom:8px">পরবর্তী →</button>
   <button class="abtn abtn-o" onclick="closeReset()">বাতিল</button>
  </div>

  <!-- Step 2: New password -->
  <div class="reset-step" id="rs2">
   <div style="background:rgba(129,201,149,.1);border:1px solid rgba(129,201,149,.3);
     border-radius:8px;padding:10px 12px;margin-bottom:14px;font-size:12px;color:var(--green)">
    ✅ Email যাচাই হয়েছে! এখন নতুন Password দিন।
   </div>
   <div class="fg">
    <label class="fl">নতুন Password (কমপক্ষে ৬ অক্ষর)</label>
    <input class="fi" id="new-pwd" type="password" placeholder="নতুন Password">
   </div>
   <div class="fg">
    <label class="fl">নতুন Password আবার দিন</label>
    <input class="fi" id="new-pwd2" type="password" placeholder="আবার একই Password" onkeydown="if(event.key==='Enter')doReset()">
   </div>
   <div class="amsg" id="rs2-msg"></div>
   <button class="abtn abtn-p" onclick="doReset()" style="margin-bottom:8px">✅ Password পরিবর্তন করুন</button>
   <button class="abtn abtn-o" onclick="closeReset()">বাতিল</button>
  </div>

  <!-- Step 3: Success -->
  <div class="reset-step" id="rs3">
   <div style="text-align:center;padding:16px 0">
    <div style="font-size:48px;margin-bottom:12px">🎉</div>
    <div style="font-size:15px;font-weight:600;color:var(--green);margin-bottom:8px">Password পরিবর্তন সফল!</div>
    <div style="font-size:12px;color:var(--text2);margin-bottom:18px">এখন নতুন Password দিয়ে Login করুন।</div>
   </div>
   <button class="abtn abtn-p" onclick="closeReset()">✅ Login করুন</button>
  </div>
 </div>
</div>

<!-- ══ BROWSER ══ -->
<div id="bscr">

 <!-- Install bar -->
 <div id="inst-bar">
  <div class="ib-txt">📱 Bong Browser — Home Screen এ Install করুন!</div>
  <button class="ib-btn" id="inst-btn">Install</button>
  <button class="ib-cls" onclick="document.getElementById('inst-bar').classList.remove('show')">✕</button>
 </div>

 <!-- Tab bar -->
 <div id="tab-bar">
  <div class="tab active" id="tab-0">
   <span class="tab-fav">🏠</span>
   <span class="tab-title" id="tt-0">New Tab</span>
   <button class="tab-x" onclick="closeTab(event,0)">✕</button>
  </div>
  <button class="newtab-btn" onclick="openNewTab()">+</button>
 </div>

 <!-- Toolbar -->
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
   <button class="tb2" title="Downloads">⬇</button>
   <div class="profbtn" id="profbtn" onclick="showMenu()">B</div>
   <button class="tb2" onclick="showMenu()">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="19" r="1.5"/></svg>
   </button>
  </div>
 </div>

 <!-- Progress -->
 <div id="prog"></div>

 <!-- Bookmarks bar -->
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
  <div class="bksep"></div>
  <button class="bki" onclick="go('https://twitter.com')">𝕏 Twitter</button>
  <div class="bksep" id="ubksep" style="display:none"></div>
  <div id="ubk"></div>
 </div>

 <!-- Content / Home -->
 <div id="ct">
  <div id="hp">
   <div class="hlogo">
    <span class="b">B</span><span class="o">o</span><span class="n">n</span><span class="g">g</span><span style="color:#9aa0a6">.</span><span class="d2">D</span><span class="e2">e</span><span class="v2">v</span>
   </div>
   <div class="hsub">Modified by Bong.Dev · v7.0</div>
   <div class="mbadge m18 hidden" id="b18">🔞 18+ Mode Active</div>
   <div class="mbadge msf hidden" id="bsf">🔒 Safe Mode</div>
   <p class="hgreet hidden" id="hgreet"></p>

   <div class="hsw">
    <div class="hsb">
     <span class="sico">🔍</span>
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
   <div class="hwm">⚡ <b>Modified by Bong.Dev</b> · Bong Browser v7.0</div>
  </div>
 </div>

 <!-- Bottom nav -->
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

<!-- MENU PANEL -->
<div class="po" id="pMenu" onclick="cp('pMenu')">
 <div class="pn" onclick="event.stopPropagation()">
  <div class="ph" onclick="cp('pMenu')"></div>
  <div class="ptitle">Bong Browser <span style="font-size:10px;color:var(--text2)">Modified by Bong.Dev ⚡</span></div>
  <div class="mi" onclick="openNewTab();cp('pMenu')"><span class="mico">📄</span>New tab<span class="msc">Ctrl+T</span></div>
  <div class="mi" onclick="openIncognito()"><span class="mico">🕵️</span>New Incognito tab</div>
  <div class="mdiv"></div>
  <div class="mi" onclick="openHist()"><span class="mico">📋</span>History</div>
  <div class="mi" onclick="openBks()"><span class="mico">☆</span>Bookmarks</div>
  <div class="mi" onclick="addBk()"><span class="mico">★</span>Bookmark this page</div>
  <div class="mdiv"></div>
  <div class="mi" onclick="zoomIn()"><span class="mico">🔍</span>Zoom in</div>
  <div class="mi" onclick="zoomOut()"><span class="mico">🔎</span>Zoom out</div>
  <div class="mdiv"></div>
  <div class="mi" onclick="showUI()"><span class="mico">👤</span>Account info</div>
  <div class="mi" onclick="showAbout()"><span class="mico">ℹ️</span>About Bong Browser</div>
  <div class="mdiv"></div>
  <div class="mi" onclick="doLogout()" style="color:var(--red)"><span class="mico">🚪</span>Logout</div>
 </div>
</div>

<!-- HISTORY PANEL -->
<div class="po" id="pHist" onclick="cp('pHist')">
 <div class="pn" onclick="event.stopPropagation()">
  <div class="ph" onclick="cp('pHist')"></div>
  <div class="ptitle">History
   <button onclick="clearHist()" style="background:rgba(242,139,130,.12);border:1px solid rgba(242,139,130,.3);color:var(--red);border-radius:6px;padding:3px 10px;cursor:pointer;font-size:11px;font-family:'Roboto',sans-serif">Clear all</button>
  </div>
  <div id="histList"></div>
 </div>
</div>

<!-- BOOKMARKS PANEL -->
<div class="po" id="pBks" onclick="cp('pBks')">
 <div class="pn" onclick="event.stopPropagation()">
  <div class="ph" onclick="cp('pBks')"></div>
  <div class="ptitle">Bookmarks</div>
  <div id="bkList"></div>
 </div>
</div>

<div id="toast"></div>

<script>
var U=null,eng="google",zoom=1,fh=[],fi=-1,tc=1;
var dp=null;

var E={
 google: q=>"https://www.google.com/search?q="+encodeURIComponent(q)+"&safe=off",
 bing:   q=>"https://www.bing.com/search?q="+encodeURIComponent(q)+"&adlt=off",
 ddg:    q=>"https://duckduckgo.com/?q="+encodeURIComponent(q)+"&kp=-2",
 yahoo:  q=>"https://search.yahoo.com/search?p="+encodeURIComponent(q),
 xvideos:q=>"https://www.xvideos.com/?k="+encodeURIComponent(q),
 xnxx:   q=>"https://www.xnxx.com/search/"+encodeURIComponent(q),
 pornhub:q=>"https://www.pornhub.com/video/search?search="+encodeURIComponent(q),
 yandex: q=>"https://yandex.com/search/?text="+encodeURIComponent(q)
};

// PWA
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
 const r=await fetch("/api/me").then(x=>x.json()).catch(()=>({logged:false}));
 if(r.logged){U=r;showB();}
 if("serviceWorker"in navigator)navigator.serviceWorker.register("/sw.js").catch(()=>{});
}

// AUTH TABS
function stab(t){
 document.querySelectorAll(".atab").forEach((b,i)=>b.classList.toggle("on",(i===0&&t==="l")||(i===1&&t==="r")));
 document.getElementById("fp-l").classList.toggle("on",t==="l");
 document.getElementById("fp-r").classList.toggle("on",t==="r");
}

// LOGIN
async function doLogin(){
 var e=document.getElementById("le").value.trim();
 var p=document.getElementById("lp").value.trim();
 sm("lm","","");
 if(!e||!p){sm("lm","❗ সব ফিল্ড পূরণ করুন","e");return}
 var r=await api("/api/login",{email:e,pwd:p});
 if(r.ok){U=r;showB();toast("Welcome "+r.name+"!");}
 else sm("lm",r.msg,"e");
}

// REGISTER
async function doReg(){
 var n=document.getElementById("rn").value.trim(),e=document.getElementById("re").value.trim(),
     d=document.getElementById("rd").value,p=document.getElementById("rp").value.trim();
 sm("rm","","");
 if(!n||!e||!d||!p){sm("rm","❗ সব ফিল্ড পূরণ করুন","e");return}
 var r=await api("/api/register",{name:n,email:e,dob:d,pwd:p});
 sm("rm",r.msg,r.ok?(r.is18?"ok":"w"):"e");
 if(r.ok){stab("l");document.getElementById("le").value=e;}
}

// ══════════════════════════════
//  PASSWORD RESET
// ══════════════════════════════
var resetEmail="";

function openReset(){
 resetEmail="";
 document.getElementById("reset-email").value="";
 document.getElementById("new-pwd").value="";
 document.getElementById("new-pwd2").value="";
 sm("rs1-msg","","");sm("rs2-msg","","");
 showRStep("rs1");
 document.getElementById("reset-panel").classList.add("open");
}

function closeReset(){
 document.getElementById("reset-panel").classList.remove("open");
 showRStep("rs1");
}

function showRStep(id){
 document.querySelectorAll(".reset-step").forEach(s=>s.classList.remove("on"));
 document.getElementById(id).classList.add("on");
}

async function verifyResetEmail(){
 var e=document.getElementById("reset-email").value.trim().toLowerCase();
 sm("rs1-msg","","");
 if(!e){sm("rs1-msg","❗ Gmail দিন","e");return}
 sm("rs1-msg","⏳ যাচাই হচ্ছে...","");
 var r=await api("/api/verify-email",{email:e});
 if(r.ok){
  resetEmail=e;
  sm("rs1-msg","","");
  showRStep("rs2");
 }else{
  sm("rs1-msg",r.msg,"e");
 }
}

async function doReset(){
 var p1=document.getElementById("new-pwd").value.trim();
 var p2=document.getElementById("new-pwd2").value.trim();
 sm("rs2-msg","","");
 if(!p1||!p2){sm("rs2-msg","❗ দুটো ফিল্ড পূরণ করুন","e");return}
 if(p1.length<6){sm("rs2-msg","❗ Password কমপক্ষে ৬ অক্ষর","e");return}
 if(p1!==p2){sm("rs2-msg","❌ দুটো Password মিলছে না","e");return}
 var r=await api("/api/reset-password",{email:resetEmail,pwd:p1});
 if(r.ok){
  showRStep("rs3");
  toast("✅ Password পরিবর্তন হয়েছে!");
 }else{
  sm("rs2-msg",r.msg,"e");
 }
}

// LOGOUT
async function doLogout(){
 await api("/api/logout",{});U=null;
 document.getElementById("bscr").classList.remove("show");
 document.getElementById("auth-scr").style.display="flex";
 cap();toast("Signed out");
}

function showB(){
 document.getElementById("auth-scr").style.display="none";
 document.getElementById("bscr").classList.add("show");
 updateUI();loadUBks();
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

// NAVIGATE
function go(url){
 if(!url)return;
 if(!url.startsWith("http"))url="https://"+url;
 if(U)api("/api/history",{url,title:url.replace(/https?:\/\/(www\.)?/,'').split('/')[0]}).catch(()=>{});
 document.getElementById("ub").value=url;
 document.getElementById("lk").textContent=url.startsWith("https")?"🔒":"⚠️";
 setTabT(url.replace(/https?:\/\/(www\.)?/,'').split('/')[0]);
 fh=fh.slice(0,fi+1);fh.push(url);fi=fh.length-1;
 updNav();cap();
 if(window.matchMedia('(display-mode:standalone)').matches||window.matchMedia('(display-mode:fullscreen)').matches)
  window.location.href=url;
 else window.open(url,"_blank");
}

function navBar(){
 var t=document.getElementById("ub").value.trim();if(!t)return;
 if(/^https?:\/\//.test(t)||(!/ /.test(t)&&/[.\/]/.test(t)))go(t);
 else go((E[eng]||E.google)(t));
}

function hSearch(){
 var q=document.getElementById("sq").value.trim();
 if(q)go((E[eng]||E.google)(q));
}

function goHome(){
 document.getElementById("ub").value="";
 document.getElementById("sq").value="";
 document.getElementById("lk").textContent="🔒";
 document.querySelectorAll(".bb").forEach((b,i)=>b.classList.toggle("on",i===2));
 cap();
}

function goBack(){if(fi>0){fi--;go(fh[fi]);}}
function goFwd(){if(fi<fh.length-1){fi++;go(fh[fi]);}}
function reloadPage(){window.location.reload();}
function updNav(){
 document.getElementById("btn-bk").disabled=fi<=0;
 document.getElementById("btn-fw").disabled=fi>=fh.length-1;
}

function setEng(el){
 eng=el.dataset.e;
 document.querySelectorAll(".ec").forEach(e=>e.classList.remove("on"));
 el.classList.add("on");
}

// TABS
function openNewTab(){
 var id=tc++;
 var bar=document.getElementById("tab-bar");
 var plus=bar.querySelector(".newtab-btn");
 var el=document.createElement("div");el.className="tab";el.id="tab-"+id;
 el.innerHTML=`<span class="tab-fav">🏠</span><span class="tab-title" id="tt-${id}">New Tab</span><button class="tab-x" onclick="closeTab(event,${id})">✕</button>`;
 el.onclick=()=>actTab(id);bar.insertBefore(el,plus);actTab(id);
 toast("New tab opened");
}
function actTab(id){
 document.querySelectorAll(".tab").forEach(t=>t.classList.remove("active"));
 var el=document.getElementById("tab-"+id);if(el)el.classList.add("active");
}
function closeTab(e,id){e.stopPropagation();var el=document.getElementById("tab-"+id);if(el)el.remove();toast("Tab closed");}
function setTabT(t){var a=document.querySelector(".tab.active");if(a){var ti=a.querySelector(".tab-title");if(ti)ti.textContent=t.substring(0,20)||"Loading...";}}

function openIncognito(){cap();window.open("https://www.google.com","_blank");toast("🕵️ Incognito — history not saved");}

// BOOKMARKS
async function addBk(){
 var url=document.getElementById("ub").value;
 if(!url||!U){toast("❗ Navigate to a page first");return}
 await api("/api/bookmarks",{url,title:url.replace(/https?:\/\/(www\.)?/,'').split('/')[0]});
 var s=document.getElementById("starBtn");
 s.textContent="★";s.style.color="var(--gold)";
 toast("★ Bookmarked!");
 setTimeout(()=>{s.textContent="☆";s.style.color="";},2000);
 loadUBks();
}

async function loadUBks(){
 var rows=await fetch("/api/bookmarks").then(x=>x.json()).catch(()=>[]);
 var c=document.getElementById("ubk"),sep=document.getElementById("ubksep");
 if(rows.length>0){
  sep.style.display="block";
  c.innerHTML=rows.slice(0,5).map(r=>`<button class="bki" onclick="go('${r.url}')">★ ${(r.title||r.url).substring(0,12)}</button>`).join("");
 }else{sep.style.display="none";c.innerHTML="";}
}

async function openBks(){
 cap();
 var rows=await fetch("/api/bookmarks").then(x=>x.json()).catch(()=>[]);
 var el=document.getElementById("bkList");
 el.innerHTML=rows.length
  ?rows.map(r=>`<div class="li"><span class="lico">★</span>
    <div class="linf" onclick="go('${r.url}');cp('pBks')">
     <div class="lit">${r.title||r.url}</div><div class="lis">${r.url}</div>
    </div>
    <button class="ldel" onclick="delBk(${r.id},this)">×</button></div>`).join("")
  :'<div class="lem">No bookmarks yet</div>';
 document.getElementById("pBks").classList.add("op");
}

async function delBk(id,btn){
 await fetch("/api/bookmarks/"+id,{method:"DELETE"});
 btn.closest(".li").remove();toast("Bookmark removed");loadUBks();
}

// HISTORY
async function openHist(){
 cap();
 var rows=await fetch("/api/history").then(x=>x.json()).catch(()=>[]);
 var el=document.getElementById("histList");
 el.innerHTML=rows.length
  ?rows.map(r=>`<div class="li" onclick="go('${r.url}');cp('pHist')">
    <span class="lico">🕐</span>
    <div class="linf"><div class="lit">${r.title||r.url}</div><div class="lis">${r.ts||""}</div></div>
   </div>`).join("")
  :'<div class="lem">No history yet</div>';
 document.getElementById("pHist").classList.add("op");
}

async function clearHist(){
 await api("/api/history/clear",{});
 document.getElementById("histList").innerHTML='<div class="lem">History cleared</div>';
 toast("History cleared");
}

// ZOOM
function zoomIn(){zoom=Math.min(zoom+.1,2);document.body.style.zoom=zoom;toast("Zoom: "+Math.round(zoom*100)+"%");}
function zoomOut(){zoom=Math.max(zoom-.1,.5);document.body.style.zoom=zoom;toast("Zoom: "+Math.round(zoom*100)+"%");}

// PANELS
function showMenu(){cap();document.getElementById("pMenu").classList.add("op");}
function cp(id){document.getElementById(id).classList.remove("op");}
function cap(){document.querySelectorAll(".po").forEach(p=>p.classList.remove("op"));}
function showUI(){cap();toast("👤 "+U.name+" · Age: "+U.age+" · "+(U.is18?"🔞 18+":"🔒 Safe Mode"));}
function showAbout(){cap();toast("🌐 Bong Browser v7.0 · Modified by Bong.Dev ⚡");}

async function api(url,data){
 var r=await fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
 return r.json();
}
function sm(id,m,c){var el=document.getElementById(id);el.textContent=m;el.className="amsg"+(c?" "+c:"");}

var _tt=null;
function toast(msg){
 var t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");
 clearTimeout(_tt);_tt=setTimeout(()=>t.classList.remove("show"),3000);
}

init();
</script>
</body>
</html>"""

MANIFEST="""{
  "name":"Bong Browser — Modified by Bong.Dev",
  "short_name":"Bong Browser",
  "description":"18+ Browser — Modified by Bong.Dev",
  "start_url":"/","display":"standalone",
  "background_color":"#202124","theme_color":"#202124","orientation":"any",
  "icons":[
    {"src":"/icon.png","sizes":"192x192","type":"image/png","purpose":"any maskable"},
    {"src":"/icon.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}
  ]
}"""

SW="""const C="bb-v7";
self.addEventListener("install",e=>{self.skipWaiting();});
self.addEventListener("activate",e=>{self.clients.claim();});
self.addEventListener("fetch",e=>{
  if(e.request.method!=="GET")return;
  e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)));
});"""

ICON=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQI12NgAAIABQAABjE+ibYAAAAASUVORK5CYII=")

# ═══════════ ROUTES ═══════════

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
    if "uid" not in session: return jsonify({"logged":False})
    return jsonify({"logged":True,"name":session.get("name"),
        "email":session.get("email"),"is18":session.get("is18",0),"age":session.get("age",0)})

@app.route("/api/login", methods=["POST"])
def login():
    d=request.json; e=d.get("email","").strip().lower(); p=d.get("pwd","").strip()
    if not e or not p: return jsonify({"ok":False,"msg":"সব ফিল্ড পূরণ করুন"})
    c=db(); row=c.execute("SELECT * FROM users WHERE email=? AND pwd=?",(e,sha(p))).fetchone(); c.close()
    if row:
        a=age(row["dob"]); i=1 if a>=18 else 0
        session.update({"uid":row["id"],"name":row["name"],"email":row["email"],"is18":i,"age":a})
        return jsonify({"ok":True,"name":row["name"],"is18":i,"age":a})
    return jsonify({"ok":False,"msg":"❌ ভুল Email বা Password\n🔑 Password ভুলে গেলে নিচে Reset করুন"})

@app.route("/api/register", methods=["POST"])
def register():
    d=request.json
    n=d.get("name","").strip(); e=d.get("email","").strip().lower()
    p=d.get("pwd","").strip(); dob=d.get("dob","")
    if not all([n,e,p,dob]): return jsonify({"ok":False,"msg":"সব ফিল্ড পূরণ করুন"})
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$',e): return jsonify({"ok":False,"msg":"সঠিক Email দিন"})
    if len(p)<6: return jsonify({"ok":False,"msg":"Password কমপক্ষে ৬ অক্ষর"})
    a=age(dob); i=1 if a>=18 else 0
    try:
        c=db(); c.execute("INSERT INTO users(email,pwd,name,dob,is18) VALUES(?,?,?,?,?)",(e,sha(p),n,dob,i)); c.commit(); c.close()
        return jsonify({"ok":True,"msg":f"✅ সফল! বয়স {a} বছর — {'18+ Mode' if i else 'Safe Mode'}। Login করুন।","is18":i,"age":a})
    except: return jsonify({"ok":False,"msg":"এই Email আগেই রেজিস্ট্রেশন হয়েছে"})

@app.route("/api/logout", methods=["POST"])
def logout(): session.clear(); return jsonify({"ok":True})

# ═══ PASSWORD RESET ═══

@app.route("/api/verify-email", methods=["POST"])
def verify_email():
    """Step 1: Check if email exists"""
    d=request.json; e=d.get("email","").strip().lower()
    if not e: return jsonify({"ok":False,"msg":"Gmail দিন"})
    c=db(); row=c.execute("SELECT id FROM users WHERE email=?",(e,)).fetchone(); c.close()
    if row:
        return jsonify({"ok":True})
    return jsonify({"ok":False,"msg":"❌ এই Email দিয়ে কোনো account নেই"})

@app.route("/api/reset-password", methods=["POST"])
def reset_password():
    """Step 2: Set new password"""
    d=request.json; e=d.get("email","").strip().lower(); p=d.get("pwd","").strip()
    if not e or not p: return jsonify({"ok":False,"msg":"সব ফিল্ড পূরণ করুন"})
    if len(p)<6: return jsonify({"ok":False,"msg":"Password কমপক্ষে ৬ অক্ষর"})
    c=db()
    row=c.execute("SELECT id FROM users WHERE email=?",(e,)).fetchone()
    if not row: c.close(); return jsonify({"ok":False,"msg":"Email পাওয়া যায়নি"})
    c.execute("UPDATE users SET pwd=? WHERE email=?",(sha(p),e)); c.commit(); c.close()
    return jsonify({"ok":True})

# ═══ HISTORY ═══

@app.route("/api/history", methods=["GET"])
def get_hist():
    if "uid" not in session: return jsonify([])
    c=db(); rows=c.execute("SELECT id,url,title,ts FROM history WHERE uid=? ORDER BY id DESC LIMIT 60",(session["uid"],)).fetchall(); c.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/history", methods=["POST"])
def add_hist():
    if "uid" not in session: return jsonify({"ok":False})
    d=request.json; url=d.get("url",""); title=d.get("title","")
    if url:
        c=db(); c.execute("INSERT INTO history(uid,url,title,ts) VALUES(?,?,?,?)",
            (session["uid"],url,title[:200],datetime.now().strftime("%d/%m %H:%M"))); c.commit(); c.close()
    return jsonify({"ok":True})

@app.route("/api/history/clear", methods=["POST"])
def clear_hist():
    if "uid" not in session: return jsonify({"ok":False})
    c=db(); c.execute("DELETE FROM history WHERE uid=?",(session["uid"],)); c.commit(); c.close()
    return jsonify({"ok":True})

# ═══ BOOKMARKS ═══

@app.route("/api/bookmarks", methods=["GET"])
def get_bk():
    if "uid" not in session: return jsonify([])
    c=db(); rows=c.execute("SELECT id,url,title FROM bookmarks WHERE uid=? ORDER BY id DESC",(session["uid"],)).fetchall(); c.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/bookmarks", methods=["POST"])
def add_bk():
    if "uid" not in session: return jsonify({"ok":False})
    d=request.json; c=db()
    c.execute("INSERT INTO bookmarks(uid,url,title) VALUES(?,?,?)",(session["uid"],d.get("url",""),d.get("title","")[:200])); c.commit(); c.close()
    return jsonify({"ok":True})

@app.route("/api/bookmarks/<int:bid>", methods=["DELETE"])
def del_bk(bid):
    if "uid" not in session: return jsonify({"ok":False})
    c=db(); c.execute("DELETE FROM bookmarks WHERE id=? AND uid=?",(bid,session["uid"])); c.commit(); c.close()
    return jsonify({"ok":True})

if __name__ == "__main__":
    init_db()
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port,debug=False)
