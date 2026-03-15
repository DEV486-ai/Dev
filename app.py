"""
BONG BROWSER v6.0 — Chrome Style
Modified by Bong.Dev ⚡
"""
from flask import Flask, request, jsonify, session
import sqlite3, hashlib, os, re, base64
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = "bongbrowser_bongdev_2025_v6"
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
  --chrome-bg:#202124;
  --chrome-toolbar:#35363a;
  --chrome-tab:#292a2d;
  --chrome-tab-active:#202124;
  --chrome-urlbar:#303134;
  --chrome-urlbar-focus:#fff;
  --chrome-border:#3c4043;
  --chrome-text:#e8eaed;
  --chrome-text2:#9aa0a6;
  --chrome-blue:#8ab4f8;
  --chrome-hover:rgba(255,255,255,.1);
  --chrome-pressed:rgba(255,255,255,.15);
  --cyan:#00f5ff;
  --purple:#8b5cf6;
  --red:#f87171;
  --green:#4ade80;
  --gold:#fbbf24;
  --safe-t:env(safe-area-inset-top,0px);
  --safe-b:env(safe-area-inset-bottom,0px);
}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%;overflow:hidden}
body{font-family:'Roboto',sans-serif;background:var(--chrome-bg);color:var(--chrome-text);
  display:flex;flex-direction:column;height:100dvh}

/* ── SCROLLBAR ── */
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-thumb{background:#5f6368;border-radius:2px}

/* ══════════ AUTH ══════════ */
#auth-screen{
  position:absolute;inset:0;display:flex;align-items:center;
  justify-content:center;overflow-y:auto;padding:20px;
  background:#202124;z-index:100;
}
#auth-screen::before{
  content:'';position:fixed;inset:0;pointer-events:none;
  background:radial-gradient(ellipse 60% 40% at 30% 40%,rgba(138,180,248,.08) 0%,transparent 60%),
             radial-gradient(ellipse 40% 50% at 75% 60%,rgba(129,201,149,.05) 0%,transparent 60%);
}

.auth-card{
  position:relative;z-index:1;
  background:#292a2d;
  border:1px solid var(--chrome-border);
  border-radius:12px;
  padding:32px 28px;
  width:100%;max-width:400px;
  box-shadow:0 4px 24px rgba(0,0,0,.5);
  animation:cardIn .4s ease both;
}
@keyframes cardIn{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}

.auth-logo-row{display:flex;align-items:center;justify-content:center;gap:12px;margin-bottom:6px}
.auth-logo-icon{
  width:40px;height:40px;border-radius:50%;
  background:linear-gradient(135deg,var(--cyan),var(--purple));
  display:flex;align-items:center;justify-content:center;
  font-size:20px;font-weight:900;color:#000;
  font-family:'Roboto',sans-serif;
}
.auth-logo-text{font-size:20px;font-weight:700;color:var(--chrome-text);font-family:'Google Sans',sans-serif}
.auth-sub{text-align:center;font-size:12px;color:var(--chrome-text2);margin-bottom:24px;letter-spacing:.5px}

.auth-tabs{display:flex;border-bottom:1px solid var(--chrome-border);margin-bottom:20px;gap:0}
.auth-tab{flex:1;padding:10px;background:none;border:none;cursor:pointer;
  color:var(--chrome-text2);font-family:'Roboto',sans-serif;font-size:13px;
  font-weight:500;transition:all .2s;border-bottom:2px solid transparent;margin-bottom:-1px}
.auth-tab.on{color:var(--chrome-blue);border-bottom-color:var(--chrome-blue)}

.fp{display:none}.fp.on{display:block}

.field-group{margin-bottom:14px}
.field-label{font-size:11px;color:var(--chrome-text2);font-weight:500;
  letter-spacing:.5px;text-transform:uppercase;margin-bottom:5px;display:block}
.field-input{
  width:100%;background:var(--chrome-urlbar);
  border:1px solid var(--chrome-border);border-radius:8px;
  padding:11px 14px;color:var(--chrome-text);
  font-family:'Roboto',sans-serif;font-size:14px;outline:none;transition:all .2s;
}
.field-input:focus{border-color:var(--chrome-blue);background:#3c4043}
.field-input::placeholder{color:#5f6368}
input[type=date].field-input{color-scheme:dark}

.auth-msg{min-height:18px;font-size:11px;text-align:center;margin:8px 0;line-height:1.5}
.auth-msg.e{color:#f28b82}.auth-msg.ok{color:#81c995}.auth-msg.w{color:#fdd663}

.auth-btn{
  width:100%;padding:12px;border:none;border-radius:8px;cursor:pointer;
  font-family:'Google Sans',sans-serif;font-size:14px;font-weight:500;
  transition:all .15s;margin-top:6px;
}
.auth-btn:active{transform:scale(.98)}
.auth-btn-primary{background:var(--chrome-blue);color:#202124}
.auth-btn-primary:hover{background:#aecbfa}
.auth-btn-secondary{background:#a8c7fa;color:#202124}
.auth-btn-secondary:hover{background:#c4d7f5}

.auth-footer{text-align:center;font-size:10px;color:#5f6368;margin-top:16px}
.auth-footer span{color:var(--chrome-blue)}

/* ══════════ BROWSER ══════════ */
#browser-screen{
  display:none;flex-direction:column;height:100%;
  background:var(--chrome-bg);
}
#browser-screen.show{display:flex}

/* INSTALL BANNER */
#install-bar{
  background:linear-gradient(90deg,#1a73e8,#0d47a1);
  padding:10px 14px;display:none;align-items:center;gap:10px;flex-shrink:0;
}
#install-bar.show{display:flex}
.install-text{flex:1;font-size:12px;color:#fff;font-weight:500}
.install-btn{background:#fff;color:#1a73e8;border:none;border-radius:20px;
  padding:6px 14px;font-size:11px;font-weight:700;cursor:pointer;flex-shrink:0}
.install-close{background:none;border:none;color:rgba(255,255,255,.7);
  font-size:18px;cursor:pointer;padding:0 4px;flex-shrink:0}

/* TAB BAR */
#tab-bar{
  background:var(--chrome-toolbar);
  display:flex;align-items:flex-end;
  padding:8px 8px 0;gap:1px;flex-shrink:0;
  padding-top:calc(8px + var(--safe-t));
  overflow-x:auto;scrollbar-width:none;min-height:42px;
}
#tab-bar::-webkit-scrollbar{display:none}

.tab{
  display:flex;align-items:center;gap:8px;
  padding:0 12px;height:34px;
  background:var(--chrome-tab);
  border-radius:10px 10px 0 0;
  min-width:140px;max-width:200px;
  cursor:pointer;flex-shrink:0;
  position:relative;transition:background .15s;
  border:1px solid var(--chrome-border);border-bottom:none;
}
.tab.active{background:var(--chrome-tab-active);border-color:var(--chrome-border)}
.tab.active::after{
  content:'';position:absolute;bottom:-1px;left:0;right:0;
  height:1px;background:var(--chrome-tab-active);
}
.tab-fav{font-size:12px;flex-shrink:0}
.tab-title{flex:1;font-size:11px;color:var(--chrome-text2);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:400}
.tab.active .tab-title{color:var(--chrome-text)}
.tab-close{
  width:16px;height:16px;border-radius:50%;background:none;border:none;
  cursor:pointer;color:var(--chrome-text2);font-size:11px;
  display:flex;align-items:center;justify-content:center;flex-shrink:0;
  transition:all .15s;
}
.tab-close:hover{background:rgba(255,255,255,.15);color:var(--chrome-text)}

.new-tab-btn{
  width:28px;height:28px;border-radius:50%;
  background:none;border:none;cursor:pointer;
  color:var(--chrome-text2);font-size:18px;
  display:flex;align-items:center;justify-content:center;
  flex-shrink:0;align-self:center;margin-left:4px;
  transition:all .15s;
}
.new-tab-btn:hover{background:var(--chrome-hover);color:var(--chrome-text)}

/* TOOLBAR */
#toolbar{
  background:var(--chrome-toolbar);
  border-bottom:1px solid var(--chrome-border);
  display:flex;align-items:center;
  padding:8px 10px;gap:6px;flex-shrink:0;
}

.nav-btn{
  width:34px;height:34px;border-radius:50%;
  background:none;border:none;cursor:pointer;
  color:var(--chrome-text2);font-size:18px;
  display:flex;align-items:center;justify-content:center;
  flex-shrink:0;transition:all .15s;
}
.nav-btn:hover{background:var(--chrome-hover);color:var(--chrome-text)}
.nav-btn:active{background:var(--chrome-pressed)}
.nav-btn:disabled{opacity:.3;pointer-events:none}

/* URL BAR */
#urlbar-wrap{
  flex:1;height:38px;
  background:var(--chrome-urlbar);
  border-radius:20px;
  display:flex;align-items:center;
  padding:0 14px;gap:8px;
  transition:all .2s;cursor:text;
  border:1px solid transparent;
}
#urlbar-wrap:focus-within{
  background:#fff;border-color:transparent;
  box-shadow:0 1px 6px rgba(32,33,36,.28);
}
#lock-icon{font-size:13px;flex-shrink:0;color:#9aa0a6}
#urlbar-wrap:focus-within #lock-icon{color:#1a73e8}
#urlbar{
  flex:1;background:none;border:none;outline:none;
  color:var(--chrome-text);font-family:'Roboto',sans-serif;font-size:14px;min-width:0;
}
#urlbar-wrap:focus-within #urlbar{color:#202124}
#urlbar::placeholder{color:#9aa0a6}
.url-star{
  background:none;border:none;cursor:pointer;
  color:#9aa0a6;font-size:16px;padding:2px;
  flex-shrink:0;transition:color .15s;
}
.url-star:hover{color:#fdd663}

/* RIGHT TOOLS */
.right-tools{display:flex;align-items:center;gap:4px}
.tool-btn{
  width:34px;height:34px;border-radius:50%;
  background:none;border:none;cursor:pointer;
  color:var(--chrome-text2);font-size:17px;
  display:flex;align-items:center;justify-content:center;
  transition:all .15s;flex-shrink:0;
}
.tool-btn:hover{background:var(--chrome-hover);color:var(--chrome-text)}
.tool-btn:active{background:var(--chrome-pressed)}

.profile-btn{
  width:28px;height:28px;border-radius:50%;
  background:linear-gradient(135deg,#1a73e8,#0d47a1);
  display:flex;align-items:center;justify-content:center;
  color:#fff;font-size:12px;font-weight:700;cursor:pointer;
  flex-shrink:0;border:2px solid #8ab4f8;
  font-family:'Google Sans',sans-serif;
}

/* PROGRESS */
#progress-bar{
  height:3px;
  background:linear-gradient(90deg,#1a73e8,#4285f4,#34a853);
  transform:scaleX(0);transform-origin:left;
  transition:transform .25s;flex-shrink:0;
  display:none;
}

/* BOOKMARKS BAR */
#bookmarks-bar{
  background:var(--chrome-toolbar);
  border-bottom:1px solid var(--chrome-border);
  display:flex;align-items:center;
  padding:4px 10px;gap:2px;flex-shrink:0;
  overflow-x:auto;scrollbar-width:none;
}
#bookmarks-bar::-webkit-scrollbar{display:none}
.bk-item{
  display:flex;align-items:center;gap:5px;
  padding:4px 10px;border-radius:20px;
  cursor:pointer;font-size:12px;color:var(--chrome-text2);
  white-space:nowrap;transition:all .15s;border:none;background:none;
  font-family:'Roboto',sans-serif;
}
.bk-item:hover{background:var(--chrome-hover);color:var(--chrome-text)}
.bk-item:active{background:var(--chrome-pressed)}
.bk-fav{font-size:13px}
.bk-sep{width:1px;height:16px;background:var(--chrome-border);flex-shrink:0;margin:0 2px}

/* CONTENT */
#content{flex:1;position:relative;overflow:hidden;background:#fff}

/* HOME PAGE */
#home-page{
  position:absolute;inset:0;overflow-y:auto;
  background:var(--chrome-bg);
  display:flex;flex-direction:column;align-items:center;
  padding:32px 20px 100px;
}

/* Google-style search */
.home-logo-area{display:flex;flex-direction:column;align-items:center;margin-bottom:28px}
.home-bong-logo{
  font-family:'Google Sans',sans-serif;
  font-size:clamp(32px,10vw,56px);font-weight:700;
  margin-bottom:4px;
}
.home-bong-logo .b{color:#8ab4f8}
.home-bong-logo .o1{color:#f28b82}
.home-bong-logo .n{color:#fdd663}
.home-bong-logo .g{color:#81c995}
.home-bong-logo .dot{color:#8ab4f8}
.home-bong-logo .d{color:#f28b82}
.home-bong-logo .e{color:#fdd663}
.home-bong-logo .v{color:#81c995}
.home-sub{font-size:12px;color:var(--chrome-text2);letter-spacing:2px;
  font-family:'Roboto',sans-serif}

/* Mode badge */
.mode-badge{
  display:inline-flex;align-items:center;gap:5px;
  padding:3px 12px;border-radius:20px;font-size:11px;font-weight:500;
  margin-bottom:20px;
}
.badge-18{background:rgba(242,139,130,.12);border:1px solid rgba(242,139,130,.3);color:#f28b82}
.badge-safe{background:rgba(129,201,149,.1);border:1px solid rgba(129,201,149,.25);color:#81c995}
.hidden{display:none!important}

/* Google-style search box */
.home-search-wrap{width:100%;max-width:580px;margin-bottom:16px}
.home-search-box{
  display:flex;align-items:center;gap:12px;height:48px;
  background:#303134;border:1px solid #5f6368;
  border-radius:24px;padding:0 16px;
  transition:all .25s;cursor:text;
}
.home-search-box:focus-within{
  background:#fff;border-color:transparent;
  box-shadow:0 2px 10px rgba(0,0,0,.4);
}
.home-search-box input{
  flex:1;background:none;border:none;outline:none;
  color:var(--chrome-text);font-family:'Roboto',sans-serif;font-size:16px;
}
.home-search-box:focus-within input{color:#202124}
.home-search-box input::placeholder{color:#9aa0a6}
.search-icon{font-size:18px;color:#9aa0a6;flex-shrink:0}
.home-search-box:focus-within .search-icon{color:#1a73e8}
.search-go-btn{
  background:#1a73e8;border:none;border-radius:20px;
  cursor:pointer;padding:7px 16px;
  font-family:'Google Sans',sans-serif;font-size:13px;font-weight:500;
  color:#fff;flex-shrink:0;transition:background .15s;
}
.search-go-btn:hover{background:#1557b0}

/* Engine row */
.engine-row{
  display:flex;gap:5px;flex-wrap:wrap;justify-content:center;
  max-width:580px;margin-bottom:28px;
}
.eng-chip{
  padding:4px 12px;border-radius:16px;
  border:1px solid var(--chrome-border);
  font-size:11px;font-weight:500;cursor:pointer;
  color:var(--chrome-text2);font-family:'Roboto',sans-serif;
  transition:all .15s;background:none;
}
.eng-chip:hover{background:var(--chrome-hover);color:var(--chrome-text);border-color:#9aa0a6}
.eng-chip.on{
  background:rgba(138,180,248,.12);color:var(--chrome-blue);
  border-color:rgba(138,180,248,.4);
}
.eng-chip.adult{color:#f28b82;border-color:rgba(242,139,130,.25)}
.eng-chip.adult:hover{background:rgba(242,139,130,.1)}
.eng-chip.adult.on{background:rgba(242,139,130,.12);border-color:rgba(242,139,130,.5)}
.eng-chip.locked{color:#5f6368;border-color:#3c4043;cursor:not-allowed}

/* Shortcut grid */
.shortcuts-grid{
  display:grid;grid-template-columns:repeat(4,1fr);
  gap:10px;width:100%;max-width:580px;margin-bottom:28px;
}
@media(max-width:380px){.shortcuts-grid{grid-template-columns:repeat(3,1fr)}}
.shortcut{
  display:flex;flex-direction:column;align-items:center;
  gap:6px;padding:12px 6px;border-radius:12px;
  cursor:pointer;transition:all .2s;border:1px solid transparent;
}
.shortcut:hover{background:rgba(255,255,255,.05);border-color:var(--chrome-border)}
.shortcut:active{background:rgba(255,255,255,.08);transform:scale(.95)}
.sc-icon{
  width:52px;height:52px;border-radius:16px;
  display:flex;align-items:center;justify-content:center;
  font-size:22px;box-shadow:0 2px 8px rgba(0,0,0,.4);
}
.sc-label{font-size:11px;color:var(--chrome-text2);font-weight:400;text-align:center}
.sc18{display:none}.sc18.show{display:flex}

.home-watermark{
  font-size:10px;color:#5f6368;letter-spacing:1px;
  font-family:'Roboto',sans-serif;margin-top:8px;
}
.home-watermark b{color:var(--chrome-blue)}

/* PANELS */
.panel-overlay{
  position:fixed;inset:0;z-index:500;
  background:rgba(0,0,0,.6);display:none;
  align-items:flex-end;
}
.panel-overlay.open{display:flex}
.panel{
  background:#292a2d;border-radius:16px 16px 0 0;
  border:1px solid var(--chrome-border);border-bottom:none;
  padding:12px 0 20px;width:100%;max-height:80vh;overflow-y:auto;
  animation:slideUp .25s ease both;
}
@keyframes slideUp{from{transform:translateY(100%)}to{transform:translateY(0)}}

.panel-handle{
  width:32px;height:3px;background:#5f6368;border-radius:2px;
  margin:0 auto 12px;cursor:pointer;
}
.panel-title{
  font-size:13px;font-weight:500;color:var(--chrome-text);
  padding:8px 18px 12px;border-bottom:1px solid var(--chrome-border);
  display:flex;justify-content:space-between;align-items:center;
  font-family:'Google Sans',sans-serif;
}
.menu-item{
  display:flex;align-items:center;gap:14px;
  padding:12px 18px;cursor:pointer;color:var(--chrome-text);
  font-size:14px;transition:background .12s;font-family:'Roboto',sans-serif;
}
.menu-item:hover{background:var(--chrome-hover)}
.menu-item:active{background:var(--chrome-pressed)}
.menu-icon{font-size:18px;width:24px;text-align:center;color:var(--chrome-text2)}
.menu-shortcut{margin-left:auto;font-size:11px;color:#9aa0a6;font-family:'Roboto Mono',monospace}
.menu-divider{height:1px;background:var(--chrome-border);margin:4px 0}

/* History/Bookmark items */
.list-item{
  display:flex;align-items:center;gap:12px;
  padding:10px 18px;cursor:pointer;transition:background .12s;
}
.list-item:hover{background:var(--chrome-hover)}
.list-item:active{background:var(--chrome-pressed)}
.list-icon{font-size:16px;flex-shrink:0;color:var(--chrome-text2)}
.list-info{flex:1;min-width:0}
.list-title{font-size:13px;color:var(--chrome-text);font-weight:400;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.list-sub{font-size:11px;color:#9aa0a6;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px}
.list-del{background:none;border:none;color:#9aa0a6;cursor:pointer;
  font-size:16px;padding:4px 6px;border-radius:50%;flex-shrink:0;transition:all .15s}
.list-del:hover{background:var(--chrome-hover);color:#f28b82}
.list-empty{text-align:center;color:#9aa0a6;font-size:13px;
  padding:24px;font-family:'Roboto',sans-serif}

/* BOTTOM NAV */
#bottom-nav{
  background:var(--chrome-toolbar);
  border-top:1px solid var(--chrome-border);
  flex-shrink:0;padding-bottom:var(--safe-b);
}
.bnav-inner{display:flex;justify-content:space-around;padding:4px 0}
.bnav-btn{
  display:flex;flex-direction:column;align-items:center;gap:3px;
  padding:6px 16px;cursor:pointer;color:var(--chrome-text2);
  background:none;border:none;font-size:10px;font-weight:500;
  font-family:'Roboto',sans-serif;border-radius:10px;transition:all .15s;
}
.bnav-btn:active,.bnav-btn.on{color:var(--chrome-blue);background:rgba(138,180,248,.1)}
.bnav-icon{font-size:20px;line-height:1}

/* TOAST */
#toast{
  position:fixed;bottom:80px;left:50%;
  transform:translateX(-50%) translateY(8px);
  background:#3c4043;color:var(--chrome-text);
  padding:10px 20px;border-radius:8px;
  font-size:13px;font-family:'Roboto',sans-serif;
  z-index:9999;opacity:0;transition:all .25s;
  pointer-events:none;white-space:nowrap;
  max-width:88vw;text-align:center;
  box-shadow:0 4px 16px rgba(0,0,0,.4);
}
#toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
</style>
</head>
<body>

<!-- ══ AUTH SCREEN ══ -->
<div id="auth-screen">
 <div class="auth-card">
  <div class="auth-logo-row">
   <div class="auth-logo-icon">B</div>
   <div class="auth-logo-text">Bong Browser</div>
  </div>
  <div class="auth-sub">Modified by Bong.Dev ⚡</div>

  <div class="auth-tabs">
   <button class="auth-tab on" onclick="stab('l')">Login</button>
   <button class="auth-tab" onclick="stab('r')">Register</button>
  </div>

  <!-- Login -->
  <div class="fp on" id="fp-login">
   <div class="field-group">
    <label class="field-label">Gmail Address</label>
    <input class="field-input" id="l-email" type="email" placeholder="yourname@gmail.com" autocomplete="email">
   </div>
   <div class="field-group">
    <label class="field-label">Password</label>
    <input class="field-input" id="l-pwd" type="password" placeholder="••••••••" onkeydown="if(event.key==='Enter')doLogin()">
   </div>
   <div class="auth-msg" id="l-msg"></div>
   <button class="auth-btn auth-btn-primary" onclick="doLogin()">Login</button>
  </div>

  <!-- Register -->
  <div class="fp" id="fp-reg">
   <div class="field-group">
    <label class="field-label">পুরো নাম</label>
    <input class="field-input" id="r-name" type="text" placeholder="আপনার নাম">
   </div>
   <div class="field-group">
    <label class="field-label">Gmail Address</label>
    <input class="field-input" id="r-email" type="email" placeholder="yourname@gmail.com">
   </div>
   <div class="field-group">
    <label class="field-label">জন্ম তারিখ (বয়স যাচাই হবে)</label>
    <input class="field-input" id="r-dob" type="date" max="2099-12-31">
   </div>
   <div class="field-group">
    <label class="field-label">Password</label>
    <input class="field-input" id="r-pwd" type="password" placeholder="কমপক্ষে ৬ অক্ষর" onkeydown="if(event.key==='Enter')doReg()">
   </div>
   <div class="auth-msg" id="r-msg"></div>
   <button class="auth-btn auth-btn-secondary" onclick="doReg()">Register</button>
  </div>

  <div class="auth-footer">🔒 ডেটা সুরক্ষিত · <span>Modified by Bong.Dev</span></div>
 </div>
</div>

<!-- ══ BROWSER SCREEN ══ -->
<div id="browser-screen">

 <!-- Install Bar -->
 <div id="install-bar">
  <div class="install-text">📱 Bong Browser — Home Screen এ Install করুন!</div>
  <button class="install-btn" id="install-btn-el">Install</button>
  <button class="install-close" onclick="document.getElementById('install-bar').classList.remove('show')">✕</button>
 </div>

 <!-- Tab Bar -->
 <div id="tab-bar">
  <div class="tab active" id="tab-0">
   <span class="tab-fav">🏠</span>
   <span class="tab-title" id="tab-title-0">New Tab</span>
   <button class="tab-close" onclick="closeTab(event,0)">✕</button>
  </div>
  <button class="new-tab-btn" onclick="openNewTab()" title="New Tab">+</button>
 </div>

 <!-- Toolbar -->
 <div id="toolbar">
  <button class="nav-btn" id="btn-back" onclick="goBack()" disabled title="Back">
   <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
  </button>
  <button class="nav-btn" id="btn-fwd" onclick="goFwd()" disabled title="Forward">
   <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
  </button>
  <button class="nav-btn" id="btn-reload" onclick="reloadPage()" title="Reload">
   <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
  </button>
  <button class="nav-btn" onclick="goHome()" title="Home">
   <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
  </button>

  <div id="urlbar-wrap">
   <span id="lock-icon">🔒</span>
   <input id="urlbar" type="url" inputmode="url"
     placeholder="Search or type a URL" onkeydown="if(event.key==='Enter')navFromBar()">
   <button class="url-star" id="star-btn" onclick="addBookmark()">☆</button>
  </div>

  <div class="right-tools">
   <button class="tool-btn" title="Downloads">⬇</button>
   <div class="profile-orb" id="profile-orb" onclick="showMenu()" title="Profile">B</div>
   <button class="tool-btn" onclick="showMenu()" title="More options">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="19" r="1.5"/></svg>
   </button>
  </div>
 </div>

 <!-- Progress -->
 <div id="progress-bar"></div>

 <!-- Bookmarks Bar -->
 <div id="bookmarks-bar">
  <button class="bk-item" onclick="navigate('https://www.google.com')"><span class="bk-fav">G</span>Google</button>
  <div class="bk-sep"></div>
  <button class="bk-item" onclick="navigate('https://www.youtube.com')"><span class="bk-fav">▶</span>YouTube</button>
  <div class="bk-sep"></div>
  <button class="bk-item" onclick="navigate('https://www.facebook.com')"><span class="bk-fav">f</span>Facebook</button>
  <div class="bk-sep"></div>
  <button class="bk-item" onclick="navigate('https://web.whatsapp.com')"><span class="bk-fav">💬</span>WhatsApp</button>
  <div class="bk-sep"></div>
  <button class="bk-item" onclick="navigate('https://www.instagram.com')"><span class="bk-fav">📸</span>Instagram</button>
  <div class="bk-sep"></div>
  <button class="bk-item" onclick="navigate('https://twitter.com')"><span class="bk-fav">𝕏</span>Twitter</button>
  <div class="bk-sep" id="user-bk-sep" style="display:none"></div>
  <div id="user-bookmarks"></div>
 </div>

 <!-- Content -->
 <div id="content">
  <!-- HOME PAGE -->
  <div id="home-page">
   <div class="home-logo-area">
    <div class="home-bong-logo">
     <span class="b">B</span><span class="o1">o</span><span class="n">n</span><span class="g">g</span><span style="color:#9aa0a6">.</span><span class="d">D</span><span class="e">e</span><span class="v">v</span>
    </div>
    <div class="home-sub">Modified by Bong.Dev · Browser v6.0</div>
   </div>

   <div class="mode-badge badge-18 hidden" id="badge-18">🔞 18+ Mode Active</div>
   <div class="mode-badge badge-safe hidden" id="badge-safe">🔒 Safe Mode</div>

   <p style="font-size:13px;color:#9aa0a6;margin-bottom:20px;text-align:center" id="greet-text"></p>

   <!-- Search -->
   <div class="home-search-wrap">
    <div class="home-search-box">
     <span class="search-icon">🔍</span>
     <input id="search-q" type="search" placeholder="Search or type a URL"
       onkeydown="if(event.key==='Enter')homeSearch()">
     <button class="search-go-btn" onclick="homeSearch()">Search</button>
    </div>
   </div>

   <!-- Engines -->
   <div class="engine-row" id="engine-row">
    <button class="eng-chip on" data-e="google" onclick="setEng(this)">🔍 Google</button>
    <button class="eng-chip" data-e="bing" onclick="setEng(this)">🅱 Bing</button>
    <button class="eng-chip" data-e="ddg" onclick="setEng(this)">🦆 DDG</button>
    <button class="eng-chip" data-e="yahoo" onclick="setEng(this)">Y! Yahoo</button>
   </div>

   <!-- Shortcuts -->
   <div class="shortcuts-grid">
    <div class="shortcut" onclick="navigate('https://www.youtube.com')">
     <div class="sc-icon" style="background:linear-gradient(135deg,#f00,#900)">▶</div>
     <div class="sc-label">YouTube</div></div>
    <div class="shortcut" onclick="navigate('https://www.google.com')">
     <div class="sc-icon" style="background:linear-gradient(135deg,#4285f4,#34a853)">G</div>
     <div class="sc-label">Google</div></div>
    <div class="shortcut" onclick="navigate('https://www.facebook.com')">
     <div class="sc-icon" style="background:linear-gradient(135deg,#1877f2,#0d5dbf)">f</div>
     <div class="sc-label">Facebook</div></div>
    <div class="shortcut" onclick="navigate('https://www.instagram.com')">
     <div class="sc-icon" style="background:linear-gradient(135deg,#f09433,#dc2743,#cc2366)">📷</div>
     <div class="sc-label">Instagram</div></div>
    <div class="shortcut" onclick="navigate('https://twitter.com')">
     <div class="sc-icon" style="background:linear-gradient(135deg,#000,#333)">𝕏</div>
     <div class="sc-label">Twitter/X</div></div>
    <div class="shortcut" onclick="navigate('https://web.whatsapp.com')">
     <div class="sc-icon" style="background:linear-gradient(135deg,#25d366,#128c7e)">💬</div>
     <div class="sc-label">WhatsApp</div></div>
    <div class="shortcut" onclick="navigate('https://www.tiktok.com')">
     <div class="sc-icon" style="background:linear-gradient(135deg,#010101,#ff0050)">♪</div>
     <div class="sc-label">TikTok</div></div>
    <div class="shortcut" onclick="navigate('https://t.me')">
     <div class="sc-icon" style="background:linear-gradient(135deg,#2ca5e0,#1a7ab5)">✈</div>
     <div class="sc-label">Telegram</div></div>
    <div class="shortcut" onclick="navigate('https://www.netflix.com')">
     <div class="sc-icon" style="background:linear-gradient(135deg,#e50914,#700)">N</div>
     <div class="sc-label">Netflix</div></div>
    <div class="shortcut" onclick="navigate('https://reddit.com')">
     <div class="sc-icon" style="background:linear-gradient(135deg,#ff4500,#c30)">r/</div>
     <div class="sc-label">Reddit</div></div>
    <div class="shortcut" onclick="navigate('https://github.com')">
     <div class="sc-icon" style="background:linear-gradient(135deg,#24292e,#555)">🐙</div>
     <div class="sc-label">GitHub</div></div>
    <div class="shortcut" onclick="navigate('https://www.amazon.in')">
     <div class="sc-icon" style="background:linear-gradient(135deg,#ff9900,#c70)">a</div>
     <div class="sc-label">Amazon</div></div>
    <!-- 18+ -->
    <div class="shortcut sc18" onclick="navigate('https://www.xvideos.com')">
     <div class="sc-icon" style="background:linear-gradient(135deg,#c00,#900)">🔴</div>
     <div class="sc-label">XVideos</div></div>
    <div class="shortcut sc18" onclick="navigate('https://www.xnxx.com')">
     <div class="sc-icon" style="background:linear-gradient(135deg,#c50,#930)">🟠</div>
     <div class="sc-label">XNXX</div></div>
    <div class="shortcut sc18" onclick="navigate('https://www.pornhub.com')">
     <div class="sc-icon" style="background:linear-gradient(135deg,#ff9000,#c60)">🟧</div>
     <div class="sc-label">PornHub</div></div>
    <div class="shortcut sc18" onclick="navigate('https://yandex.com')">
     <div class="sc-icon" style="background:linear-gradient(135deg,#c00,#900)">Y</div>
     <div class="sc-label">Yandex</div></div>
   </div>
   <div class="home-watermark">⚡ <b>Modified by Bong.Dev</b> · v6.0 · 18+ Edition</div>
  </div>
 </div>

 <!-- Bottom Nav -->
 <div id="bottom-nav">
  <div class="bnav-inner">
   <button class="bnav-btn" onclick="goBack()"><div class="bnav-icon">◀</div>Back</button>
   <button class="bnav-btn" onclick="goFwd()"><div class="bnav-icon">▶</div>Forward</button>
   <button class="bnav-btn on" id="btn-home-nav" onclick="goHome()"><div class="bnav-icon">⌂</div>Home</button>
   <button class="bnav-btn" onclick="openHistory()"><div class="bnav-icon">📋</div>History</button>
   <button class="bnav-btn" onclick="showMenu()"><div class="bnav-icon">⋮</div>More</button>
  </div>
 </div>
</div>

<!-- ══ MENU PANEL ══ -->
<div class="panel-overlay" id="menu-panel" onclick="closePanel('menu-panel')">
 <div class="panel" onclick="event.stopPropagation()">
  <div class="panel-handle" onclick="closePanel('menu-panel')"></div>
  <div class="panel-title">
   Bong Browser
   <span style="font-size:11px;color:#9aa0a6">Modified by Bong.Dev ⚡</span>
  </div>
  <div class="menu-item" onclick="openNewTab();closePanel('menu-panel')">
   <span class="menu-icon">📄</span>New tab<span class="menu-shortcut">Ctrl+T</span></div>
  <div class="menu-item" onclick="openIncognito()">
   <span class="menu-icon">🕵️</span>New Incognito tab<span class="menu-shortcut">Ctrl+Shift+N</span></div>
  <div class="menu-divider"></div>
  <div class="menu-item" onclick="openHistory()">
   <span class="menu-icon">📋</span>History<span class="menu-shortcut">Ctrl+H</span></div>
  <div class="menu-item" onclick="openBookmarks()">
   <span class="menu-icon">☆</span>Bookmarks<span class="menu-shortcut">Ctrl+D</span></div>
  <div class="menu-item" onclick="addBookmark()">
   <span class="menu-icon">★</span>Bookmark this page</div>
  <div class="menu-divider"></div>
  <div class="menu-item" onclick="zoomIn()">
   <span class="menu-icon">🔍</span>Zoom in<span class="menu-shortcut">Ctrl++</span></div>
  <div class="menu-item" onclick="zoomOut()">
   <span class="menu-icon">🔎</span>Zoom out<span class="menu-shortcut">Ctrl+-</span></div>
  <div class="menu-divider"></div>
  <div class="menu-item" onclick="showUserInfo()">
   <span class="menu-icon">👤</span>Account info</div>
  <div class="menu-item" onclick="showAbout()">
   <span class="menu-icon">ℹ️</span>About Bong Browser</div>
  <div class="menu-divider"></div>
  <div class="menu-item" onclick="doLogout()" style="color:#f28b82">
   <span class="menu-icon">🚪</span>Logout</div>
 </div>
</div>

<!-- ══ HISTORY PANEL ══ -->
<div class="panel-overlay" id="history-panel" onclick="closePanel('history-panel')">
 <div class="panel" onclick="event.stopPropagation()">
  <div class="panel-handle" onclick="closePanel('history-panel')"></div>
  <div class="panel-title">
   History
   <button onclick="clearHistory()" style="background:rgba(242,139,130,.12);border:1px solid rgba(242,139,130,.3);color:#f28b82;border-radius:6px;padding:4px 10px;cursor:pointer;font-size:11px;font-family:'Roboto',sans-serif">Clear all</button>
  </div>
  <div id="history-list"></div>
 </div>
</div>

<!-- ══ BOOKMARKS PANEL ══ -->
<div class="panel-overlay" id="bookmarks-panel" onclick="closePanel('bookmarks-panel')">
 <div class="panel" onclick="event.stopPropagation()">
  <div class="panel-handle" onclick="closePanel('bookmarks-panel')"></div>
  <div class="panel-title">Bookmarks</div>
  <div id="bookmarks-list"></div>
 </div>
</div>

<div id="toast"></div>

<script>
var U=null, eng="google", zoom=1;
var frameHist=[], frameIdx=-1, tabCnt=1;
var deferredPrompt=null;

var ENGINES={
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
 e.preventDefault(); deferredPrompt=e;
 document.getElementById('install-bar').classList.add('show');
});
document.getElementById('install-btn-el').addEventListener('click',async()=>{
 if(deferredPrompt){
  deferredPrompt.prompt();
  const {outcome}=await deferredPrompt.userChoice;
  if(outcome==='accepted') toast('✅ Bong Browser installed!');
  deferredPrompt=null;
  document.getElementById('install-bar').classList.remove('show');
 }
});

async function init(){
 const r=await fetch("/api/me").then(x=>x.json()).catch(()=>({logged:false}));
 if(r.logged){U=r;showBrowser();}
 if("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(()=>{});
}

// AUTH
function stab(t){
 document.querySelectorAll(".auth-tab").forEach((b,i)=>b.classList.toggle("on",(i===0&&t==="l")||(i===1&&t==="r")));
 document.getElementById("fp-login").classList.toggle("on",t==="l");
 document.getElementById("fp-reg").classList.toggle("on",t==="r");
}

async function doLogin(){
 var e=document.getElementById("l-email").value.trim();
 var p=document.getElementById("l-pwd").value.trim();
 setMsg("l-msg","","");
 if(!e||!p){setMsg("l-msg","❗ সব ফিল্ড পূরণ করুন","e");return}
 var r=await api("/api/login",{email:e,pwd:p});
 if(r.ok){U=r;showBrowser();toast("Welcome "+r.name+"! Age: "+r.age);}
 else setMsg("l-msg",r.msg,"e");
}

async function doReg(){
 var n=document.getElementById("r-name").value.trim(),e=document.getElementById("r-email").value.trim(),
     d=document.getElementById("r-dob").value,p=document.getElementById("r-pwd").value.trim();
 setMsg("r-msg","","");
 if(!n||!e||!d||!p){setMsg("r-msg","❗ সব ফিল্ড পূরণ করুন","e");return}
 var r=await api("/api/register",{name:n,email:e,dob:d,pwd:p});
 setMsg("r-msg",r.msg,r.ok?(r.is18?"ok":"w"):"e");
 if(r.ok){stab("l");document.getElementById("l-email").value=e;}
}

async function doLogout(){
 await api("/api/logout",{});U=null;
 document.getElementById("browser-screen").classList.remove("show");
 document.getElementById("auth-screen").style.display="flex";
 closeAllPanels();toast("Signed out");
}

function showBrowser(){
 document.getElementById("auth-screen").style.display="none";
 document.getElementById("browser-screen").classList.add("show");
 updateHomeUI();
 loadUserBookmarks();
}

function updateHomeUI(){
 if(!U)return;
 var is18=U.is18;
 document.getElementById("badge-18").classList.toggle("hidden",!is18);
 document.getElementById("badge-safe").classList.toggle("hidden",!!is18);
 document.getElementById("greet-text").textContent="Welcome, "+U.name+"! "+(is18?"🔞 18+ Mode active — all features unlocked":"🔒 Safe Mode");

 var row=document.getElementById("engine-row");
 row.querySelectorAll(".eng-chip.adult,.eng-chip.locked").forEach(x=>x.remove());
 if(is18){
  [["xvideos","🔴 XVideos"],["xnxx","🟠 XNXX"],["pornhub","🟧 PornHub"],["yandex","🟡 Yandex"]].forEach(([e,l])=>{
   var b=document.createElement("button");b.className="eng-chip adult";
   b.dataset.e=e;b.textContent=l;b.onclick=()=>setEng(b);row.appendChild(b);
  });
  document.querySelectorAll(".sc18").forEach(x=>x.classList.add("show"));
 }else{
  ["🔒 XVideos","🔒 Adult"].forEach(l=>{
   var b=document.createElement("button");b.className="eng-chip locked";b.textContent=l;row.appendChild(b);
  });
 }
 // Profile initial
 var po=document.getElementById("profile-orb");
 if(po&&U.name) po.textContent=U.name[0].toUpperCase();
}

// NAVIGATION
function navigate(url){
 if(!url)return;
 if(!url.startsWith("http"))url="https://"+url;
 if(U) api("/api/history",{url,title:url.replace(/https?:\/\/(www\.)?/,'').split('/')[0]}).catch(()=>{});
 document.getElementById("urlbar").value=url;
 document.getElementById("lock-icon").textContent=url.startsWith("https")?"🔒":"⚠️";
 // Update tab title
 var t=url.replace(/https?:\/\/(www\.)?/,'').split('/')[0];
 setTabTitle(t);
 // PWA standalone or new tab
 if(window.matchMedia('(display-mode:standalone)').matches||window.matchMedia('(display-mode:fullscreen)').matches){
  window.location.href=url;
 }else{
  window.open(url,"_blank");
 }
 frameHist=frameHist.slice(0,frameIdx+1);
 frameHist.push(url);frameIdx=frameHist.length-1;
 updateNavBtns();
 closeAllPanels();
}

function navFromBar(){
 var t=document.getElementById("urlbar").value.trim();if(!t)return;
 if(/^https?:\/\//.test(t)||(!/ /.test(t)&&/[.\/]/.test(t)))navigate(t);
 else navigate((ENGINES[eng]||ENGINES.google)(t));
}

function homeSearch(){
 var q=document.getElementById("search-q").value.trim();
 if(q)navigate((ENGINES[eng]||ENGINES.google)(q));
}

function goHome(){
 document.getElementById("urlbar").value="";
 document.getElementById("lock-icon").textContent="🔒";
 document.getElementById("search-q").value="";
 document.querySelectorAll(".bnav-btn").forEach((b,i)=>b.classList.toggle("on",i===2));
 closeAllPanels();
}

function goBack(){if(frameIdx>0){frameIdx--;navigate(frameHist[frameIdx]);}}
function goFwd(){if(frameIdx<frameHist.length-1){frameIdx++;navigate(frameHist[frameIdx]);}}
function reloadPage(){window.location.reload();}
function updateNavBtns(){
 document.getElementById("btn-back").disabled=frameIdx<=0;
 document.getElementById("btn-fwd").disabled=frameIdx>=frameHist.length-1;
}

function setEng(el){
 eng=el.dataset.e;
 document.querySelectorAll(".eng-chip").forEach(e=>e.classList.remove("on"));
 el.classList.add("on");
}

// TABS
function openNewTab(){
 var id=tabCnt++;
 var bar=document.getElementById("tab-bar");
 var plus=bar.querySelector(".new-tab-btn");
 var el=document.createElement("div");
 el.className="tab";el.id="tab-"+id;
 el.innerHTML=`<span class="tab-fav">🏠</span><span class="tab-title" id="tab-title-${id}">New Tab</span><button class="tab-close" onclick="closeTab(event,${id})">✕</button>`;
 el.onclick=()=>activateTab(id);
 bar.insertBefore(el,plus);
 activateTab(id);
 toast("New tab opened");
}

function activateTab(id){
 document.querySelectorAll(".tab").forEach(t=>t.classList.remove("active"));
 var el=document.getElementById("tab-"+id);
 if(el)el.classList.add("active");
}

function closeTab(e,id){
 e.stopPropagation();
 var el=document.getElementById("tab-"+id);
 if(el)el.remove();
 toast("Tab closed");
}

function setTabTitle(t){
 var active=document.querySelector(".tab.active");
 if(active){
  var ti=active.querySelector(".tab-title");
  if(ti)ti.textContent=t.substring(0,20)||"Loading...";
 }
}

function openIncognito(){
 closeAllPanels();
 window.open("https://www.google.com","_blank");
 toast("🕵️ Incognito — history won't be saved");
}

// BOOKMARKS
async function addBookmark(){
 var url=document.getElementById("urlbar").value;
 if(!url||!U){toast("❗ Navigate to a page first");return}
 await api("/api/bookmarks",{url,title:url.replace(/https?:\/\/(www\.)?/,'').split('/')[0]});
 var s=document.getElementById("star-btn");
 s.textContent="★";s.style.color="#fdd663";
 toast("★ Bookmarked!");
 setTimeout(()=>{s.textContent="☆";s.style.color="";},2000);
 loadUserBookmarks();
}

async function loadUserBookmarks(){
 var rows=await fetch("/api/bookmarks").then(x=>x.json()).catch(()=>[]);
 var cont=document.getElementById("user-bookmarks");
 var sep=document.getElementById("user-bk-sep");
 if(rows.length>0){
  sep.style.display="block";
  cont.innerHTML=rows.slice(0,6).map(r=>`
   <button class="bk-item" onclick="navigate('${r.url}')">
    <span class="bk-fav">★</span>${(r.title||r.url).substring(0,12)}
   </button>`).join("");
 }else{sep.style.display="none";cont.innerHTML="";}
}

async function openBookmarks(){
 closeAllPanels();
 var rows=await fetch("/api/bookmarks").then(x=>x.json()).catch(()=>[]);
 var el=document.getElementById("bookmarks-list");
 el.innerHTML=rows.length
  ?rows.map(r=>`<div class="list-item">
    <span class="list-icon">★</span>
    <div class="list-info" onclick="navigate('${r.url}');closePanel('bookmarks-panel')">
     <div class="list-title">${r.title||r.url}</div>
     <div class="list-sub">${r.url}</div>
    </div>
    <button class="list-del" onclick="delBookmark(${r.id},this)">×</button>
   </div>`).join("")
  :'<div class="list-empty">No bookmarks yet</div>';
 document.getElementById("bookmarks-panel").classList.add("open");
}

async function delBookmark(id,btn){
 await fetch("/api/bookmarks/"+id,{method:"DELETE"});
 btn.closest(".list-item").remove();
 toast("Bookmark removed");
 loadUserBookmarks();
}

// HISTORY
async function openHistory(){
 closeAllPanels();
 var rows=await fetch("/api/history").then(x=>x.json()).catch(()=>[]);
 var el=document.getElementById("history-list");
 el.innerHTML=rows.length
  ?rows.map(r=>`<div class="list-item" onclick="navigate('${r.url}');closePanel('history-panel')">
    <span class="list-icon">🕐</span>
    <div class="list-info">
     <div class="list-title">${r.title||r.url}</div>
     <div class="list-sub">${r.ts||""} · ${r.url}</div>
    </div>
   </div>`).join("")
  :'<div class="list-empty">No history yet</div>';
 document.getElementById("history-panel").classList.add("open");
}

async function clearHistory(){
 await api("/api/history/clear",{});
 document.getElementById("history-list").innerHTML='<div class="list-empty">History cleared</div>';
 toast("History cleared");
}

// ZOOM
function zoomIn(){zoom=Math.min(zoom+.1,2);document.body.style.zoom=zoom;toast("Zoom: "+Math.round(zoom*100)+"%");}
function zoomOut(){zoom=Math.max(zoom-.1,.5);document.body.style.zoom=zoom;toast("Zoom: "+Math.round(zoom*100)+"%");}

// PANELS
function showMenu(){closeAllPanels();document.getElementById("menu-panel").classList.add("open");}
function closePanel(id){document.getElementById(id).classList.remove("open");}
function closeAllPanels(){document.querySelectorAll(".panel-overlay").forEach(p=>p.classList.remove("open"));}

function showUserInfo(){
 closeAllPanels();
 toast("👤 "+U.name+" · Age: "+U.age+" · "+(U.is18?"🔞 18+ Mode":"🔒 Safe Mode"));
}
function showAbout(){
 closeAllPanels();
 toast("🌐 Bong Browser v6.0 · Modified by Bong.Dev ⚡");
}

async function api(url,data){
 var r=await fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
 return r.json();
}
function setMsg(id,m,c){var el=document.getElementById(id);el.textContent=m;el.className="auth-msg"+(c?" "+c:"");}

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
  "background_color":"#202124","theme_color":"#202124",
  "orientation":"any",
  "icons":[
    {"src":"/icon.png","sizes":"192x192","type":"image/png","purpose":"any maskable"},
    {"src":"/icon.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}
  ]
}"""

SW="""const C="bb-v6";
self.addEventListener("install",e=>{self.skipWaiting();});
self.addEventListener("activate",e=>{self.clients.claim();});
self.addEventListener("fetch",e=>{
  if(e.request.method!=="GET")return;
  e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)));
});"""

ICON=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQI12NgAAIABQAABjE+ibYAAAAASUVORK5CYII=")

@app.route("/")
def index(): return HTML

@app.route("/manifest.json")
def manifest():
    from flask import Response
    return Response(MANIFEST,mimetype="application/json")

@app.route("/sw.js")
def sw():
    from flask import Response
    return Response(SW,mimetype="application/javascript")

@app.route("/icon.png")
def icon():
    from flask import Response
    return Response(ICON,mimetype="image/png")

@app.route("/api/me")
def me():
    if "uid" not in session: return jsonify({"logged":False})
    return jsonify({"logged":True,"name":session.get("name"),"email":session.get("email"),"is18":session.get("is18",0),"age":session.get("age",0)})

@app.route("/api/login",methods=["POST"])
def login():
    d=request.json; e=d.get("email","").strip().lower(); p=d.get("pwd","").strip()
    if not e or not p: return jsonify({"ok":False,"msg":"সব ফিল্ড পূরণ করুন"})
    c=db(); row=c.execute("SELECT * FROM users WHERE email=? AND pwd=?",(e,sha(p))).fetchone(); c.close()
    if row:
        a=age(row["dob"]); i=1 if a>=18 else 0
        session.update({"uid":row["id"],"name":row["name"],"email":row["email"],"is18":i,"age":a})
        return jsonify({"ok":True,"name":row["name"],"is18":i,"age":a})
    return jsonify({"ok":False,"msg":"ভুল Email বা Password"})

@app.route("/api/register",methods=["POST"])
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
        return jsonify({"ok":True,"msg":f"✅ সফল! বয়স {a} — {'18+ Mode' if i else 'Safe Mode'}। Login করুন।","is18":i,"age":a})
    except: return jsonify({"ok":False,"msg":"এই Email আগেই রেজিস্ট্রেশন হয়েছে"})

@app.route("/api/logout",methods=["POST"])
def logout(): session.clear(); return jsonify({"ok":True})

@app.route("/api/history",methods=["GET"])
def get_hist():
    if "uid" not in session: return jsonify([])
    c=db(); rows=c.execute("SELECT id,url,title,ts FROM history WHERE uid=? ORDER BY id DESC LIMIT 60",(session["uid"],)).fetchall(); c.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/history",methods=["POST"])
def add_hist():
    if "uid" not in session: return jsonify({"ok":False})
    d=request.json; url=d.get("url",""); title=d.get("title","")
    if url:
        c=db(); c.execute("INSERT INTO history(uid,url,title,ts) VALUES(?,?,?,?)",(session["uid"],url,title[:200],datetime.now().strftime("%d/%m %H:%M"))); c.commit(); c.close()
    return jsonify({"ok":True})

@app.route("/api/history/clear",methods=["POST"])
def clear_hist():
    if "uid" not in session: return jsonify({"ok":False})
    c=db(); c.execute("DELETE FROM history WHERE uid=?",(session["uid"],)); c.commit(); c.close()
    return jsonify({"ok":True})

@app.route("/api/bookmarks",methods=["GET"])
def get_bk():
    if "uid" not in session: return jsonify([])
    c=db(); rows=c.execute("SELECT id,url,title FROM bookmarks WHERE uid=? ORDER BY id DESC",(session["uid"],)).fetchall(); c.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/bookmarks",methods=["POST"])
def add_bk():
    if "uid" not in session: return jsonify({"ok":False})
    d=request.json; c=db()
    c.execute("INSERT INTO bookmarks(uid,url,title) VALUES(?,?,?)",(session["uid"],d.get("url",""),d.get("title","")[:200])); c.commit(); c.close()
    return jsonify({"ok":True})

@app.route("/api/bookmarks/<int:bid>",methods=["DELETE"])
def del_bk(bid):
    if "uid" not in session: return jsonify({"ok":False})
    c=db(); c.execute("DELETE FROM bookmarks WHERE id=? AND uid=?",(bid,session["uid"])); c.commit(); c.close()
    return jsonify({"ok":True})

if __name__=="__main__":
    init_db()
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port,debug=False)
