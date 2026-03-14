"""
BONG BROWSER v5.0 — Modified by Bong.Dev ⚡
সব সাইট, ভিডিও, ছবি চলবে!
"""
from flask import Flask, request, jsonify, session
import sqlite3, hashlib, os, re
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = "bongbrowser_bongdev_2025_v5"
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
<meta name="theme-color" content="#00f5ff">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Bong Browser">
<title>Bong Browser — Modified by Bong.Dev</title>
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/icon.png">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#0d0f18;--bg1:#0f1118;--bg2:#161923;--bg3:#1e2333;
  --cyan:#00f5ff;--purple:#8b5cf6;--pink:#f472b6;
  --red:#f87171;--green:#4ade80;--gold:#fbbf24;--orange:#fb923c;
  --t1:#f0f4ff;--t2:#94a3b8;--t3:#475569;
  --border:rgba(255,255,255,.07);
  --glow:0 0 20px rgba(0,245,255,.25);
  --stb:env(safe-area-inset-top,0px);
  --sbb:env(safe-area-inset-bottom,0px);
}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%;overflow:hidden;background:var(--bg)}
body{font-family:'Syne',sans-serif;color:var(--t1);display:flex;flex-direction:column;height:100dvh}
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-thumb{background:var(--bg3);border-radius:2px}

/* SCREENS */
.scr{position:absolute;inset:0;display:flex;flex-direction:column;transition:opacity .3s,transform .3s}
.scr.off{opacity:0;pointer-events:none;transform:scale(.97)}

/* ── AUTH ── */
#as{background:var(--bg);align-items:center;justify-content:center;overflow-y:auto;padding:16px}
#as::before{content:'';position:fixed;inset:0;pointer-events:none;
  background:radial-gradient(ellipse 70% 50% at 25% 40%,rgba(139,92,246,.1) 0%,transparent 60%),
             radial-gradient(ellipse 50% 60% at 80% 55%,rgba(0,245,255,.07) 0%,transparent 60%)}
#as::after{content:'';position:fixed;inset:0;pointer-events:none;
  background-image:linear-gradient(rgba(0,245,255,.02) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(0,245,255,.02) 1px,transparent 1px);
  background-size:40px 40px}

.acard{position:relative;z-index:1;background:var(--bg1);
  border:1.5px solid rgba(0,245,255,.2);border-radius:22px;
  padding:28px 22px;width:100%;max-width:400px;
  box-shadow:0 0 60px rgba(139,92,246,.1);
  animation:ci .5s cubic-bezier(.175,.885,.32,1.275) both}
@keyframes ci{from{opacity:0;transform:translateY(20px) scale(.97)}to{opacity:1;transform:none}}

.alo{font-family:'Orbitron',monospace;font-size:clamp(18px,5vw,24px);font-weight:900;
  text-align:center;background:linear-gradient(135deg,var(--cyan),var(--purple));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:3px}
.atg{text-align:center;font-family:'JetBrains Mono',monospace;font-size:10px;
  color:var(--purple);letter-spacing:3px;margin-bottom:18px}

.tbs{display:flex;background:rgba(255,255,255,.04);border-radius:10px;padding:3px;margin-bottom:16px}
.tb{flex:1;padding:8px;border:none;border-radius:8px;background:transparent;
  color:var(--t3);font-family:'Syne',sans-serif;font-size:13px;font-weight:700;cursor:pointer;transition:all .2s}
.tb.on{background:var(--bg3);color:var(--cyan)}

.fp{display:none}.fp.on{display:block}
.fl{font-size:10px;font-weight:700;color:var(--t3);letter-spacing:1.5px;
  text-transform:uppercase;margin-bottom:5px;margin-top:12px}
.fl:first-child{margin-top:0}
.fi{width:100%;background:rgba(0,0,0,.3);border:1.5px solid var(--border);
  border-radius:10px;padding:11px 14px;color:var(--t1);
  font-family:'Syne',sans-serif;font-size:14px;outline:none;transition:all .2s}
.fi:focus{border-color:rgba(0,245,255,.45);background:rgba(0,245,255,.04)}
.fi::placeholder{color:var(--t3)}
input[type=date].fi{color-scheme:dark}

.msg{min-height:20px;font-size:11px;text-align:center;margin:8px 0;
  font-family:'JetBrains Mono',monospace;line-height:1.5;padding:0 4px}
.msg.e{color:var(--red)}.msg.ok{color:var(--green)}.msg.w{color:var(--gold)}

.bp{width:100%;padding:13px;border:none;border-radius:12px;cursor:pointer;
  font-family:'Syne',sans-serif;font-size:14px;font-weight:800;
  letter-spacing:.5px;transition:transform .15s,box-shadow .15s;margin-top:4px}
.bp:active{transform:scale(.98)}
.bp1{background:linear-gradient(135deg,var(--cyan),var(--purple));color:#000}
.bp2{background:linear-gradient(135deg,var(--purple),var(--pink));color:#fff}
.afoot{text-align:center;font-family:'JetBrains Mono',monospace;
  font-size:9px;color:rgba(255,255,255,.12);margin-top:14px;letter-spacing:1px}

/* ── BROWSER ── */
#bs{background:var(--bg);flex-direction:column}

#topbar{background:var(--bg1);border-bottom:1px solid var(--border);
  display:flex;align-items:center;padding:8px 10px;gap:6px;flex-shrink:0;
  padding-top:calc(8px + var(--stb))}

.nb{width:32px;height:32px;border-radius:9px;background:none;border:none;
  cursor:pointer;color:var(--t2);font-size:17px;display:flex;align-items:center;
  justify-content:center;transition:all .15s;flex-shrink:0}
.nb:active{background:rgba(0,245,255,.1);color:var(--cyan)}
.nb:disabled{opacity:.25;pointer-events:none}

#uw{flex:1;height:38px;background:rgba(0,0,0,.35);border:1.5px solid var(--border);
  border-radius:28px;display:flex;align-items:center;padding:0 14px;gap:8px;
  transition:all .2s;min-width:0}
#uw:focus-within{border-color:rgba(0,245,255,.5);box-shadow:var(--glow)}
#lk{font-size:12px;flex-shrink:0}
#ub{flex:1;background:none;border:none;outline:none;color:var(--t1);
  font-family:'JetBrains Mono',monospace;font-size:12px;min-width:0}
#ub::placeholder{color:var(--t3)}

.ib{width:30px;height:30px;border-radius:8px;background:rgba(255,255,255,.05);
  border:none;cursor:pointer;color:var(--t2);font-size:14px;display:flex;
  align-items:center;justify-content:center;transition:all .15s;flex-shrink:0}
.ib:active{background:rgba(0,245,255,.12);color:var(--cyan)}

#pb{height:2px;background:linear-gradient(90deg,var(--cyan),var(--purple),var(--pink));
  transform:scaleX(0);transform-origin:left;transition:transform .25s;
  flex-shrink:0;display:none;box-shadow:0 0 8px var(--cyan)}

#ct{flex:1;position:relative;overflow:hidden}

/* ── HOME PAGE ── */
#hp{position:absolute;inset:0;overflow-y:auto;display:flex;
  flex-direction:column;align-items:center;padding:28px 14px 100px}
#hp::before{content:'';position:fixed;inset:0;pointer-events:none;
  background:radial-gradient(ellipse 65% 45% at 30% 35%,rgba(139,92,246,.09) 0%,transparent 60%),
             radial-gradient(ellipse 50% 60% at 75% 60%,rgba(0,245,255,.06) 0%,transparent 60%)}
#hp::after{content:'';position:fixed;inset:0;pointer-events:none;
  background-image:linear-gradient(rgba(0,245,255,.018) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(0,245,255,.018) 1px,transparent 1px);
  background-size:40px 40px}

.hl{font-family:'Orbitron',monospace;font-size:clamp(26px,8vw,50px);font-weight:900;
  letter-spacing:-1px;line-height:1;
  background:linear-gradient(135deg,var(--cyan),var(--purple) 50%,var(--pink));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  animation:up .5s ease both;position:relative;z-index:1}
.ht{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--purple);
  letter-spacing:3px;text-transform:uppercase;margin-top:5px;margin-bottom:7px;
  animation:up .5s .07s ease both;position:relative;z-index:1}
.mb{display:inline-flex;align-items:center;gap:5px;padding:4px 13px;
  border-radius:18px;font-size:10px;font-weight:700;letter-spacing:1px;
  margin-bottom:18px;animation:up .5s .1s ease both;position:relative;z-index:1}
.m18{background:rgba(248,113,113,.12);border:1px solid rgba(248,113,113,.4);color:var(--red)}
.msf{background:rgba(74,222,128,.1);border:1px solid rgba(74,222,128,.3);color:var(--green)}
.hidden{display:none!important}
.hg{font-size:12px;color:var(--t3);margin-bottom:18px;
  animation:up .5s .13s ease both;position:relative;z-index:1}
.hg b{color:var(--cyan)}

/* Search */
.sw{width:100%;max-width:580px;margin-bottom:10px;
  animation:up .5s .16s ease both;position:relative;z-index:1}
.sb{display:flex;align-items:center;gap:9px;height:50px;
  background:rgba(255,255,255,.04);border:1.5px solid rgba(0,245,255,.2);
  border-radius:28px;padding:0 14px;transition:all .25s}
.sb:focus-within{border-color:var(--cyan);background:rgba(255,255,255,.06);
  box-shadow:0 0 0 3px rgba(0,245,255,.07),var(--glow)}
.sb input{flex:1;background:none;border:none;outline:none;color:var(--t1);
  font-family:'Syne',sans-serif;font-size:14px}
.sb input::placeholder{color:var(--t3)}
.sg{background:linear-gradient(135deg,var(--cyan),var(--purple));border:none;
  border-radius:20px;cursor:pointer;padding:7px 16px;font-family:'Syne',sans-serif;
  font-size:11px;font-weight:800;color:#000;flex-shrink:0;transition:transform .15s}
.sg:active{transform:scale(.97)}

/* Engine Pills */
.er{display:flex;gap:5px;flex-wrap:wrap;justify-content:center;max-width:580px;
  margin-bottom:22px;animation:up .5s .2s ease both;position:relative;z-index:1}
.ep{padding:4px 11px;border-radius:18px;border:1px solid var(--border);
  font-size:10px;font-weight:700;cursor:pointer;color:var(--t3);
  font-family:'JetBrains Mono',monospace;transition:all .15s}
.ep:active,.ep.on{color:var(--cyan);border-color:rgba(0,245,255,.4);background:rgba(0,245,255,.08)}
.ep.a{color:var(--red);border-color:rgba(248,113,113,.2)}
.ep.a:active,.ep.a.on{background:rgba(248,113,113,.1);border-color:rgba(248,113,113,.5)}
.ep.lk{color:var(--bg3);border-color:var(--bg3);cursor:not-allowed}

/* Shortcuts */
.sg2{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;width:100%;
  max-width:580px;margin-bottom:22px;animation:up .5s .24s ease both;position:relative;z-index:1}
@media(max-width:360px){.sg2{grid-template-columns:repeat(3,1fr)}}
.sc{display:flex;flex-direction:column;align-items:center;gap:6px;
  padding:11px 4px;border-radius:14px;border:1px solid transparent;
  cursor:pointer;transition:all .2s;text-decoration:none}
.sc:active{background:rgba(255,255,255,.05);transform:scale(.95)}
.si{width:50px;height:50px;border-radius:14px;display:flex;align-items:center;
  justify-content:center;font-size:18px;font-weight:900;
  font-family:'Orbitron',monospace;box-shadow:0 4px 14px rgba(0,0,0,.3)}
.sl{font-size:10px;color:var(--t2);font-weight:700;text-align:center}

/* 18+ adult shortcuts */
.sc18{display:none}
.sc18.show{display:flex}

.wm{font-family:'JetBrains Mono',monospace;font-size:9px;
  color:rgba(139,92,246,.35);letter-spacing:2px;text-transform:uppercase;
  animation:up .5s .28s ease both;position:relative;z-index:1}
.wm span{color:var(--cyan)}

/* Bottom Nav */
#bn{background:var(--bg1);border-top:1px solid var(--border);
  flex-shrink:0;padding-bottom:var(--sbb)}
.bni{display:flex;justify-content:space-around;padding:5px 0}
.bb{display:flex;flex-direction:column;align-items:center;gap:2px;
  padding:5px 12px;cursor:pointer;color:var(--t3);background:none;border:none;
  font-size:9px;font-weight:700;letter-spacing:.5px;
  font-family:'JetBrains Mono',monospace;border-radius:9px;transition:all .15s}
.bb:active,.bb.on{color:var(--cyan);background:rgba(0,245,255,.07)}
.bi{font-size:19px;line-height:1}

/* Panels */
.po{position:fixed;inset:0;z-index:200;background:rgba(0,0,0,.65);
  display:none;align-items:flex-end;backdrop-filter:blur(3px)}
.po.op{display:flex}
.pn{background:var(--bg2);border:1px solid var(--border);
  border-radius:20px 20px 0 0;padding:10px 14px 20px;width:100%;
  max-height:82vh;overflow-y:auto;animation:su .28s ease both}
@keyframes su{from{transform:translateY(100%)}to{transform:translateY(0)}}
.ph{width:34px;height:4px;background:var(--bg3);border-radius:2px;
  margin:0 auto 14px;cursor:pointer}
.pt{font-size:13px;font-weight:800;color:var(--t1);margin-bottom:12px;
  padding-bottom:10px;border-bottom:1px solid var(--border);
  display:flex;justify-content:space-between;align-items:center}
.pr{display:flex;align-items:center;gap:11px;padding:10px 9px;
  border-radius:9px;cursor:pointer;transition:background .12s;color:var(--t2);font-size:13px}
.pr:active{background:rgba(255,255,255,.05);color:var(--t1)}
.pi2{font-size:16px;flex-shrink:0;width:22px;text-align:center}
.pk{margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--t3)}
.ps{height:1px;background:var(--border);margin:5px 0}

/* List items */
.li{display:flex;align-items:center;gap:9px;padding:9px;
  border-radius:9px;cursor:pointer;transition:background .12s}
.li:active{background:rgba(0,245,255,.06)}
.lio{font-size:15px;flex-shrink:0}
.lii{flex:1;min-width:0}
.lit{font-size:12px;color:var(--t1);font-weight:600;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.lis{font-size:10px;color:var(--t3);font-family:'JetBrains Mono',monospace;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ld{background:none;border:none;color:var(--t3);cursor:pointer;
  font-size:15px;padding:3px 5px;border-radius:5px;flex-shrink:0}
.ld:active{color:var(--red)}
.em{text-align:center;color:var(--t3);font-size:11px;
  padding:20px;font-family:'JetBrains Mono',monospace}

/* Install banner */
#install-banner{background:linear-gradient(135deg,rgba(0,245,255,.15),rgba(139,92,246,.15));
  border-top:1px solid rgba(0,245,255,.3);padding:10px 14px;
  display:none;align-items:center;gap:10px;flex-shrink:0}
#install-banner.show{display:flex}
.ib2{flex:1;font-size:12px;color:var(--t1);font-weight:600}
.ib2 span{color:var(--cyan)}
.ibb{background:linear-gradient(135deg,var(--cyan),var(--purple));border:none;
  border-radius:20px;padding:7px 16px;font-family:'Syne',sans-serif;
  font-size:11px;font-weight:800;color:#000;cursor:pointer;flex-shrink:0}
.ibc{background:none;border:none;color:var(--t3);cursor:pointer;
  font-size:18px;padding:0 4px;flex-shrink:0}

/* Toast */
#tt{position:fixed;bottom:80px;left:50%;
  transform:translateX(-50%) translateY(8px);
  background:var(--bg3);border:1px solid rgba(0,245,255,.3);
  color:var(--t1);padding:9px 18px;border-radius:28px;
  font-size:11px;font-family:'JetBrains Mono',monospace;
  z-index:9999;opacity:0;transition:all .28s;pointer-events:none;
  white-space:nowrap;max-width:88vw;text-align:center;
  box-shadow:0 5px 20px rgba(0,0,0,.4)}
#tt.sh{opacity:1;transform:translateX(-50%) translateY(0)}

@keyframes up{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
</style>
</head>
<body>

<!-- ══ AUTH ══ -->
<div class="scr" id="as">
 <div class="acard">
  <div class="alo">🌐 BONG BROWSER</div>
  <div class="atg">▸ Modified by Bong.Dev ◂</div>
  <div class="tbs">
   <button class="tb on" onclick="stab('l')">🔑 Login</button>
   <button class="tb" onclick="stab('r')">📝 Register</button>
  </div>
  <!-- Login -->
  <div class="fp on" id="fl">
   <div class="fl">📧 Gmail Address</div>
   <input class="fi" id="le" type="email" placeholder="yourname@gmail.com" autocomplete="email">
   <div class="fl">🔒 Password</div>
   <input class="fi" id="lp" type="password" placeholder="••••••••" onkeydown="if(event.key==='Enter')dol()">
   <div class="msg" id="lm"></div>
   <button class="bp bp1" onclick="dol()">🔑 &nbsp;LOGIN</button>
  </div>
  <!-- Register -->
  <div class="fp" id="fr">
   <div class="fl">👤 পুরো নাম</div>
   <input class="fi" id="rn" type="text" placeholder="আপনার নাম">
   <div class="fl">📧 Gmail Address</div>
   <input class="fi" id="re" type="email" placeholder="yourname@gmail.com">
   <div class="fl">🎂 জন্ম তারিখ (বয়স যাচাই হবে)</div>
   <input class="fi" id="rd" type="date" max="2099-12-31">
   <div class="fl">🔒 Password (কমপক্ষে ৬ অক্ষর)</div>
   <input class="fi" id="rp" type="password" placeholder="••••••••" onkeydown="if(event.key==='Enter')dor()">
   <div class="msg" id="rm"></div>
   <button class="bp bp2" onclick="dor()">📝 &nbsp;REGISTER</button>
  </div>
  <div class="afoot">🔒 ডেটা সার্ভারে সংরক্ষিত · Modified by Bong.Dev</div>
 </div>
</div>

<!-- ══ BROWSER ══ -->
<div class="scr off" id="bs">

 <!-- Install Banner -->
 <div id="install-banner">
  <div class="ib2">📱 <span>Bong Browser</span> — Home Screen এ Install করুন!</div>
  <button class="ibb" id="install-btn">Install ⬇</button>
  <button class="ibc" onclick="document.getElementById('install-banner').classList.remove('show')">✕</button>
 </div>

 <!-- Top Bar -->
 <div id="topbar">
  <button class="nb" onclick="history.back()">
   <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
  </button>
  <button class="nb" onclick="history.forward()">
   <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
  </button>
  <button class="nb" id="br" onclick="location.reload()">↻</button>
  <div id="uw">
   <span id="lk">🔒</span>
   <input id="ub" type="url" inputmode="url"
     placeholder="সার্চ করুন বা URL লিখুন..."
     onkeydown="if(event.key==='Enter')nfb()">
  </div>
  <button class="ib" id="bkb" onclick="abk()">☆</button>
  <button class="ib" onclick="omn()">⋮</button>
 </div>

 <!-- Progress -->
 <div id="pb"></div>

 <!-- Content -->
 <div id="ct">
  <div id="hp">
   <div class="hl">BONG BROWSER</div>
   <div class="ht">▸ Modified by Bong.Dev ◂</div>
   <div class="mb m18 hidden" id="b18">🔞 18+ Mode Active</div>
   <div class="mb msf hidden" id="bsf">🔒 Safe Mode</div>
   <div class="hg" id="hg">লোড হচ্ছে...</div>

   <!-- Search Box -->
   <div class="sw">
    <div class="sb">
     <span style="font-size:18px;color:var(--t3);flex-shrink:0">🔍</span>
     <input id="hq" type="search" placeholder="যা খুশি লিখুন..." onkeydown="if(event.key==='Enter')hs()">
     <button class="sg" onclick="hs()">যাই →</button>
    </div>
   </div>

   <!-- Engine Pills -->
   <div class="er" id="er">
    <div class="ep on" data-e="google" onclick="se(this)">🔍 Google</div>
    <div class="ep" data-e="bing" onclick="se(this)">🅱 Bing</div>
    <div class="ep" data-e="ddg" onclick="se(this)">🦆 DuckDuckGo</div>
    <div class="ep" data-e="yahoo" onclick="se(this)">Y! Yahoo</div>
   </div>

   <!-- Shortcuts -->
   <div class="sg2">
    <div class="sc" onclick="go('https://www.youtube.com')">
     <div class="si" style="background:linear-gradient(135deg,#f00,#900)">▶</div>
     <div class="sl">YouTube</div></div>
    <div class="sc" onclick="go('https://www.google.com')">
     <div class="si" style="background:linear-gradient(135deg,#4285f4,#34a853)">G</div>
     <div class="sl">Google</div></div>
    <div class="sc" onclick="go('https://www.facebook.com')">
     <div class="si" style="background:linear-gradient(135deg,#1877f2,#0d5dbf)">f</div>
     <div class="sl">Facebook</div></div>
    <div class="sc" onclick="go('https://www.instagram.com')">
     <div class="si" style="background:linear-gradient(135deg,#f09433,#dc2743,#cc2366)">📷</div>
     <div class="sl">Instagram</div></div>
    <div class="sc" onclick="go('https://twitter.com')">
     <div class="si" style="background:linear-gradient(135deg,#000,#333)">𝕏</div>
     <div class="sl">Twitter/X</div></div>
    <div class="sc" onclick="go('https://web.whatsapp.com')">
     <div class="si" style="background:linear-gradient(135deg,#25d366,#128c7e)">💬</div>
     <div class="sl">WhatsApp</div></div>
    <div class="sc" onclick="go('https://www.tiktok.com')">
     <div class="si" style="background:linear-gradient(135deg,#010101,#ff0050)">♪</div>
     <div class="sl">TikTok</div></div>
    <div class="sc" onclick="go('https://t.me')">
     <div class="si" style="background:linear-gradient(135deg,#2ca5e0,#1a7ab5)">✈</div>
     <div class="sl">Telegram</div></div>
    <div class="sc" onclick="go('https://www.netflix.com')">
     <div class="si" style="background:linear-gradient(135deg,#e50914,#700)">N</div>
     <div class="sl">Netflix</div></div>
    <div class="sc" onclick="go('https://reddit.com')">
     <div class="si" style="background:linear-gradient(135deg,#ff4500,#c30)">r/</div>
     <div class="sl">Reddit</div></div>
    <div class="sc" onclick="go('https://github.com')">
     <div class="si" style="background:linear-gradient(135deg,#24292e,#555)">🐙</div>
     <div class="sl">GitHub</div></div>
    <div class="sc" onclick="go('https://www.amazon.in')">
     <div class="si" style="background:linear-gradient(135deg,#ff9900,#c70)">a</div>
     <div class="sl">Amazon</div></div>

    <!-- 18+ Shortcuts (hidden by default) -->
    <div class="sc sc18" id="sc-xv" onclick="go('https://www.xvideos.com')">
     <div class="si" style="background:linear-gradient(135deg,#c00,#900)">🔴</div>
     <div class="sl">XVideos</div></div>
    <div class="sc sc18" id="sc-xn" onclick="go('https://www.xnxx.com')">
     <div class="si" style="background:linear-gradient(135deg,#c50,#930)">🟠</div>
     <div class="sl">XNXX</div></div>
    <div class="sc sc18" id="sc-ph" onclick="go('https://www.pornhub.com')">
     <div class="si" style="background:linear-gradient(135deg,#ff9000,#c60)">🟧</div>
     <div class="sl">PornHub</div></div>
    <div class="sc sc18" id="sc-yn" onclick="go('https://yandex.com')">
     <div class="si" style="background:linear-gradient(135deg,#c00,#a00)">Y</div>
     <div class="sl">Yandex</div></div>
   </div>

   <div class="wm">⚡ <span>Bong Browser</span> · Modified by Bong.Dev · v5.0</div>
  </div>
 </div>

 <!-- Bottom Nav -->
 <div id="bn">
  <div class="bni">
   <button class="bb" onclick="history.back()"><div class="bi">◀</div>Back</button>
   <button class="bb" onclick="history.forward()"><div class="bi">▶</div>Fwd</button>
   <button class="bb on" onclick="gh()"><div class="bi">⌂</div>Home</button>
   <button class="bb" onclick="ohi()"><div class="bi">📋</div>History</button>
   <button class="bb" onclick="omn()"><div class="bi">⋮</div>Menu</button>
  </div>
 </div>
</div>

<!-- ══ MENU PANEL ══ -->
<div class="po" id="om" onclick="cp('om')">
 <div class="pn" onclick="event.stopPropagation()">
  <div class="ph" onclick="cp('om')"></div>
  <div class="pt">⚡ Bong Browser — Modified by Bong.Dev</div>
  <div class="pr" onclick="ohi()"><span class="pi2">📋</span>History<span class="pk">হিস্টরি</span></div>
  <div class="pr" onclick="obk()"><span class="pi2">★</span>Bookmarks<span class="pk">বুকমার্ক</span></div>
  <div class="ps"></div>
  <div class="pr" onclick="uif()"><span class="pi2">👤</span>Account Info</div>
  <div class="pr" onclick="abt()"><span class="pi2">ℹ️</span>About Bong Browser</div>
  <div class="ps"></div>
  <div class="pr" onclick="dlo()" style="color:var(--red)"><span class="pi2">🚪</span>Logout</div>
 </div>
</div>

<!-- ══ HISTORY PANEL ══ -->
<div class="po" id="oh" onclick="cp('oh')">
 <div class="pn" onclick="event.stopPropagation()">
  <div class="ph" onclick="cp('oh')"></div>
  <div class="pt">
   📋 History
   <button onclick="chi()" style="background:rgba(248,113,113,.15);border:1px solid rgba(248,113,113,.3);color:var(--red);border-radius:7px;padding:3px 9px;cursor:pointer;font-size:10px">🗑 Clear</button>
  </div>
  <div id="hl2"></div>
 </div>
</div>

<!-- ══ BOOKMARKS PANEL ══ -->
<div class="po" id="ob2" onclick="cp('ob2')">
 <div class="pn" onclick="event.stopPropagation()">
  <div class="ph" onclick="cp('ob2')"></div>
  <div class="pt">★ Bookmarks</div>
  <div id="bl2"></div>
 </div>
</div>

<div id="tt"></div>

<script>
var U=null, eng="google";
var deferredPrompt=null;

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

// PWA Install
window.addEventListener('beforeinstallprompt', e=>{
 e.preventDefault();
 deferredPrompt=e;
 document.getElementById('install-banner').classList.add('show');
});
document.getElementById('install-btn').addEventListener('click', async()=>{
 if(deferredPrompt){
  deferredPrompt.prompt();
  const {outcome}=await deferredPrompt.userChoice;
  if(outcome==='accepted') toast('✅ Install হয়েছে!');
  deferredPrompt=null;
  document.getElementById('install-banner').classList.remove('show');
 }
});
window.addEventListener('appinstalled',()=>{
 document.getElementById('install-banner').classList.remove('show');
 toast('🎉 Bong Browser Install হয়েছে!');
});

async function init(){
 const r=await fetch("/api/me").then(x=>x.json()).catch(()=>({logged:false}));
 if(r.logged){U=r;showB();}
 if("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(()=>{});
}

function stab(t){
 document.querySelectorAll(".tb").forEach((b,i)=>b.classList.toggle("on",(i===0&&t==="l")||(i===1&&t==="r")));
 document.getElementById("fl").classList.toggle("on",t==="l");
 document.getElementById("fr").classList.toggle("on",t==="r");
}

async function dol(){
 var e=document.getElementById("le").value.trim();
 var p=document.getElementById("lp").value.trim();
 sm("lm","","");
 if(!e||!p){sm("lm","❗ সব ফিল্ড পূরণ করুন","e");return}
 var r=await api("/api/login",{email:e,pwd:p});
 if(r.ok){U=r;showB();toast("✅ স্বাগতম "+r.name+"! বয়স: "+r.age+" বছর");}
 else sm("lm",r.msg,"e");
}

async function dor(){
 var n=document.getElementById("rn").value.trim(),e=document.getElementById("re").value.trim(),
     d=document.getElementById("rd").value,p=document.getElementById("rp").value.trim();
 sm("rm","","");
 if(!n||!e||!d||!p){sm("rm","❗ সব ফিল্ড পূরণ করুন","e");return}
 var r=await api("/api/register",{name:n,email:e,dob:d,pwd:p});
 sm("rm",r.msg,r.ok?(r.is18?"ok":"w"):"e");
 if(r.ok){stab("l");document.getElementById("le").value=e;}
}

async function dlo(){
 await api("/api/logout",{});U=null;
 document.getElementById("bs").classList.add("off");
 document.getElementById("as").classList.remove("off");
 cap2();toast("👋 Logout হয়েছে");
}

function showB(){
 document.getElementById("as").classList.add("off");
 document.getElementById("bs").classList.remove("off");
 hui();
}

function hui(){
 if(!U)return;
 var is18=U.is18;
 document.getElementById("b18").classList.toggle("hidden",!is18);
 document.getElementById("bsf").classList.toggle("hidden",!!is18);
 document.getElementById("hg").innerHTML="স্বাগতম, <b>"+U.name+"</b>! "+(is18?"🔞 18+ সব ফিচার চালু":"🔒 Safe Mode চালু");

 // Engine pills
 var er=document.getElementById("er");
 er.querySelectorAll(".ep.a,.ep.lk").forEach(x=>x.remove());
 if(is18){
  [["xvideos","🔴 XVideos"],["xnxx","🟠 XNXX"],["pornhub","🟧 PornHub"],["yandex","🟡 Yandex"]].forEach(([e,l])=>{
   var d=document.createElement("div");d.className="ep a";d.dataset.e=e;d.textContent=l;
   d.onclick=()=>se(d);er.appendChild(d);
  });
  // Show 18+ shortcuts
  document.querySelectorAll(".sc18").forEach(x=>x.classList.add("show"));
 } else {
  ["🔒 XVideos","🔒 Adult"].forEach(l=>{
   var d=document.createElement("div");d.className="ep lk";d.textContent=l;er.appendChild(d);
  });
 }
}

// Navigate — সরাসরি সাইট খুলবে নতুন tab এ
function go(url){
 if(!url)return;
 if(!url.startsWith("http"))url="https://"+url;
 // Save to history
 if(U) api("/api/history",{url,title:url.replace(/https?:\/\/(www\.)?/,'').split('/')[0]}).catch(()=>{});
 // Open in same window (PWA) or new tab
 if(window.matchMedia('(display-mode: standalone)').matches){
  window.location.href=url;
 } else {
  window.open(url,"_blank");
 }
 document.getElementById("ub").value=url;
}

function nfb(){
 var t=document.getElementById("ub").value.trim();if(!t)return;
 if(/^https?:\/\//.test(t)||(!/ /.test(t)&&/[.\/]/.test(t)))go(t);
 else go((E[eng]||E.google)(t));
}

function hs(){
 var q=document.getElementById("hq").value.trim();
 if(q)go((E[eng]||E.google)(q));
}

function gh(){
 document.getElementById("ub").value="";
 document.getElementById("hq").value="";
 document.querySelectorAll(".bb").forEach((b,i)=>b.classList.toggle("on",i===2));
 cap2();
}

function se(el){
 eng=el.dataset.e;
 document.querySelectorAll(".ep").forEach(e=>e.classList.remove("on"));
 el.classList.add("on");
}

async function abk(){
 var url=document.getElementById("ub").value;
 if(!url||!U){toast("❗ আগে কোনো সাইটে যান");return}
 await api("/api/bookmarks",{url,title:url.replace(/https?:\/\/(www\.)?/,'').split('/')[0]});
 var b=document.getElementById("bkb");
 b.textContent="★";b.style.color="var(--gold)";
 toast("★ বুকমার্ক যোগ হয়েছে!");
 setTimeout(()=>{b.textContent="☆";b.style.color="";},2000);
}

async function ohi(){
 cap2();
 var rows=await fetch("/api/history").then(x=>x.json()).catch(()=>[]);
 var el=document.getElementById("hl2");
 el.innerHTML=rows.length
  ?rows.map(r=>`<div class="li" onclick="go('${r.url}');cp('oh')">
    <span class="lio">🕐</span>
    <div class="lii"><div class="lit">${r.title||r.url}</div><div class="lis">${r.ts||''}</div></div>
   </div>`).join("")
  :'<div class="em">📭 কোনো হিস্টরি নেই</div>';
 document.getElementById("oh").classList.add("op");
}

async function chi(){
 await api("/api/history/clear",{});
 document.getElementById("hl2").innerHTML='<div class="em">📭 হিস্টরি মুছে গেছে</div>';
 toast("🗑 হিস্টরি মুছে গেছে");
}

async function obk(){
 cap2();
 var rows=await fetch("/api/bookmarks").then(x=>x.json()).catch(()=>[]);
 var el=document.getElementById("bl2");
 el.innerHTML=rows.length
  ?rows.map(r=>`<div class="li">
    <span class="lio">★</span>
    <div class="lii" onclick="go('${r.url}');cp('ob2')">
     <div class="lit">${r.title||r.url}</div>
     <div class="lis">${r.url}</div>
    </div>
    <button class="ld" onclick="delbk(${r.id},this)">×</button>
   </div>`).join("")
  :'<div class="em">📭 কোনো বুকমার্ক নেই</div>';
 document.getElementById("ob2").classList.add("op");
}

async function delbk(id,btn){
 await fetch("/api/bookmarks/"+id,{method:"DELETE"});
 btn.closest(".li").remove();
 toast("🗑 বুকমার্ক মুছে গেছে");
}

function omn(){cap2();document.getElementById("om").classList.add("op");}
function cp(id){document.getElementById(id).classList.remove("op");}
function cap2(){document.querySelectorAll(".po").forEach(p=>p.classList.remove("op"));}

function uif(){
 cap2();
 toast("👤 "+U.name+" · বয়স: "+U.age+" বছর · "+(U.is18?"🔞 18+ Mode":"🔒 Safe Mode"));
}
function abt(){
 cap2();
 toast("🌐 Bong Browser v5.0 · Modified by Bong.Dev ⚡");
}

async function api(url,data){
 var r=await fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
 return r.json();
}
function sm(id,msg,cls){var el=document.getElementById(id);el.textContent=msg;el.className="msg"+(cls?" "+cls:"");}

var _tt2=null;
function toast(msg){
 var t=document.getElementById("tt");t.textContent=msg;t.classList.add("sh");
 clearTimeout(_tt2);_tt2=setTimeout(()=>t.classList.remove("sh"),3000);
}

init();
</script>
</body>
</html>"""

MANIFEST = """{
  "name": "Bong Browser — Modified by Bong.Dev",
  "short_name": "Bong Browser",
  "description": "18+ Unrestricted Browser — Modified by Bong.Dev",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0d0f18",
  "theme_color": "#00f5ff",
  "orientation": "any",
  "icons": [
    {"src": "/icon.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
    {"src": "/icon.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
  ]
}"""

SW = """const C="bb-v5";
self.addEventListener("install",e=>{self.skipWaiting();});
self.addEventListener("activate",e=>{self.clients.claim();});
self.addEventListener("fetch",e=>{
  if(e.request.method!=="GET")return;
  e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)));
});"""

import base64
ICON = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQI12NgAAIABQAABjE+ibYAAAAASUVORK5CYII="

@app.route("/")
def index():
    return HTML

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
    return Response(base64.b64decode(ICON), mimetype="image/png")

@app.route("/api/me")
def me():
    if "uid" not in session:
        return jsonify({"logged":False})
    return jsonify({"logged":True,"name":session.get("name"),"email":session.get("email"),"is18":session.get("is18",0),"age":session.get("age",0)})

@app.route("/api/login", methods=["POST"])
def login():
    d=request.json
    e=d.get("email","").strip().lower(); p=d.get("pwd","").strip()
    if not e or not p: return jsonify({"ok":False,"msg":"সব ফিল্ড পূরণ করুন"})
    c=db(); row=c.execute("SELECT * FROM users WHERE email=? AND pwd=?",(e,sha(p))).fetchone(); c.close()
    if row:
        a=age(row["dob"]); i=1 if a>=18 else 0
        session.update({"uid":row["id"],"name":row["name"],"email":row["email"],"is18":i,"age":a})
        return jsonify({"ok":True,"name":row["name"],"is18":i,"age":a})
    return jsonify({"ok":False,"msg":"ভুল Email বা Password"})

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
        msg=f"✅ সফল! বয়স {a} বছর — {'18+ Mode চালু' if i else 'Safe Mode'}। Login করুন।"
        return jsonify({"ok":True,"msg":msg,"is18":i,"age":a})
    except: return jsonify({"ok":False,"msg":"এই Email আগেই রেজিস্ট্রেশন হয়েছে"})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear(); return jsonify({"ok":True})

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
        c=db(); c.execute("INSERT INTO history(uid,url,title,ts) VALUES(?,?,?,?)",(session["uid"],url,title[:200],datetime.now().strftime("%d/%m %H:%M"))); c.commit(); c.close()
    return jsonify({"ok":True})

@app.route("/api/history/clear", methods=["POST"])
def clear_hist():
    if "uid" not in session: return jsonify({"ok":False})
    c=db(); c.execute("DELETE FROM history WHERE uid=?",(session["uid"],)); c.commit(); c.close()
    return jsonify({"ok":True})

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
