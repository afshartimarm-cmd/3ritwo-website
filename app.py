# -*- coding: utf-8 -*-
import os
import sqlite3
import secrets
from flask import Flask, request, redirect, session, send_from_directory, render_template_string
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-before-publishing-" + secrets.token_hex(16))
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
DB_PATH = os.path.join(BASE_DIR, "music.db")
os.makedirs(MEDIA_DIR, exist_ok=True)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "12345678")

ALLOWED = {
    "cover": {"jpg", "jpeg", "png", "webp"},
    "audio": {"mp3", "wav", "ogg", "m4a", "aac", "flac"},
    "video": {"mp4", "webm", "mov"},
}

def db():
    return sqlite3.connect(DB_PATH)

def init_db():
    with db() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                cover TEXT,
                audio TEXT,
                lyrics TEXT,
                video TEXT
            )
        """)

init_db()

PAGE = """
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#090909">
<title>3RITWO — OFFICIAL ARCHIVE</title>
<style>
:root{--bg:#090909;--panel:#11100e;--line:#302a23;--text:#f2eee7;--muted:#a59d92;--hot:#ff5a1f;--gold:#d8a45c}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--text);font-family:Tahoma,Arial,sans-serif;overflow-x:hidden}
body:before{content:"";position:fixed;inset:0;pointer-events:none;z-index:5;opacity:.09;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.92' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.38'/%3E%3C/svg%3E")}
a{color:inherit;text-decoration:none}.topline{height:4px;background:linear-gradient(90deg,#090909,var(--hot),var(--gold),#090909)}
header{position:relative;z-index:2;display:flex;align-items:center;justify-content:space-between;padding:22px 7%;border-bottom:1px solid var(--line);background:#090909e8}
.logo{font-family:Impact,'Arial Black',sans-serif;direction:ltr;font-size:30px;letter-spacing:2px;color:var(--text)}.logo span{color:var(--hot)}.nav{font-size:11px;letter-spacing:2px;color:var(--muted)}.nav a{border:1px solid #45382e;padding:10px 14px;transition:.2s}.nav a:hover{background:var(--hot);color:#100b08;border-color:var(--hot)}
.hero{position:relative;min-height:490px;display:flex;flex-direction:column;justify-content:center;align-items:flex-start;padding:76px 9% 68px;overflow:hidden;border-bottom:1px solid var(--line);background:radial-gradient(ellipse at 75% 42%,#4b1b0d 0,transparent 38%),linear-gradient(115deg,#090909 15%,#15100d 65%,#0b0908)}
.hero:after{content:"3R";position:absolute;direction:ltr;right:-2%;top:50%;transform:translateY(-50%) rotate(-8deg);font:clamp(200px,36vw,500px)/.8 Impact,'Arial Black',sans-serif;color:#ffffff06;letter-spacing:-.08em;white-space:nowrap;pointer-events:none}
.eyebrow{position:relative;z-index:1;color:var(--hot);font-size:11px;letter-spacing:4px;font-weight:bold;margin-bottom:20px}.hero h1{position:relative;z-index:1;direction:ltr;text-align:left;font:clamp(70px,15vw,168px)/.78 Impact,'Arial Black',sans-serif;letter-spacing:-.025em;margin:0;color:#f2eee7;text-shadow:5px 5px 0 #6b2412;max-width:100%;overflow-wrap:anywhere}.hero h1 span{color:var(--hot)}.hero p{position:relative;z-index:1;max-width:440px;line-height:2;color:#b8afa3;font-size:14px;margin:30px 0 22px}.hero-actions{position:relative;z-index:1;display:flex;gap:10px;flex-wrap:wrap}.btn{display:inline-flex;align-items:center;justify-content:center;background:var(--hot);color:#100b08;padding:13px 19px;font-size:12px;font-weight:bold;border:1px solid var(--hot);transition:.2s}.btn:hover{background:var(--gold);border-color:var(--gold);transform:translateY(-2px)}.btn.secondary{background:transparent;color:var(--text);border-color:#55463a}.hero-stamp{position:absolute;z-index:1;left:8%;bottom:38px;direction:ltr;border:1px solid #7a3a22;color:#b66a42;padding:11px 14px;font:12px Impact,sans-serif;letter-spacing:2px;transform:rotate(-7deg)}
.marquee{overflow:hidden;border-bottom:1px solid var(--line);padding:13px 0;color:#82766a;font:12px Impact,'Arial Black',sans-serif;letter-spacing:4px;direction:ltr;white-space:nowrap}.marquee span{display:inline-block;padding-left:35px}
section{padding:58px 7%}.section-head{display:flex;align-items:end;justify-content:space-between;gap:15px;margin-bottom:25px}.section-head h2{margin:0;font-size:clamp(24px,4vw,39px);font-weight:900}.section-head h2 span{color:var(--hot)}.section-head small{color:var(--muted);font-size:11px;letter-spacing:2px;direction:ltr}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:17px}.card{position:relative;background:linear-gradient(145deg,#171411,#0e0d0c);border:1px solid var(--line);padding:12px;overflow:hidden;transition:transform .25s,border-color .25s}.card:hover{transform:translateY(-5px);border-color:#8a3c20}.cover{width:100%;aspect-ratio:1;object-fit:cover;display:block;background:linear-gradient(135deg,#20150f,#080808);filter:saturate(.8) contrast(1.08)}.cover-placeholder{width:100%;aspect-ratio:1;display:flex;align-items:center;justify-content:center;background:radial-gradient(circle at 65% 25%,#6b2916,transparent 40%),linear-gradient(135deg,#1c1712,#080808);font:clamp(65px,12vw,110px)/1 Impact,sans-serif;color:#ff5a1f;direction:ltr;text-shadow:4px 4px #32150c}
.track-meta{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:16px}.track-meta h3{margin:0;font-size:19px}.track-no{direction:ltr;font:12px Impact,sans-serif;color:var(--hot);letter-spacing:2px}.artist{display:block;color:var(--muted);font-size:12px;margin-top:8px}audio,video{width:100%;margin:15px 0 8px;accent-color:var(--hot)}details{margin-top:14px;border-top:1px solid var(--line);padding-top:12px;color:var(--gold);font-size:13px;cursor:pointer}details p{color:#c6bdb1;line-height:2}.lyrics{white-space:pre-wrap}.download{display:inline-block;margin-top:5px;color:var(--hot);font-size:12px;border-bottom:1px solid #78341d;padding-bottom:5px}.empty{grid-column:1/-1;text-align:center;color:#a59d92;padding:55px 15px;border:1px dashed #44372c;line-height:2}
footer{border-top:1px solid var(--line);padding:30px 7%;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;color:#777067;font-size:11px;letter-spacing:1px}footer b{direction:ltr;color:var(--hot);font-family:Impact,sans-serif;font-size:15px}
@media(max-width:600px){header{padding:18px 5%}.logo{font-size:25px}.nav{font-size:9px}.nav a{padding:9px}.hero{min-height:430px;padding:65px 6%}.hero h1{font-size:clamp(62px,17vw,100px)}.hero-stamp{left:6%;bottom:22px;font-size:10px}.section-head{align-items:start;flex-direction:column}section{padding:42px 5%}.grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.card{padding:8px}.track-meta h3{font-size:15px}.artist{font-size:10px}.btn{padding:12px 14px}}
</style></head><body>
<div class="topline"></div>
<header><a class="logo" href="/">3R<span>ITWO</span></a><div class="nav"><a href="#music">MUSIC ARCHIVE ↘</a> &nbsp; <a href="/admin">مدیریت ↗</a></div></header>
<main>
<div class="hero"><div class="eyebrow">INDEPENDENT ARTIST · MASHHAD, IR</div><h1>3R<span>ITWO</span></h1><p>صدا از دل تاریکی؛ بی‌قانون، خام و واقعی.<br>به آرشیو رسمی موسیقی 3RITWO خوش اومدی.</p><div class="hero-actions"><a class="btn" href="#music">گوش دادن به آثار ↙</a><a class="btn secondary" href="#about">درباره صدا</a></div><div class="hero-stamp">NO RULES / JUST SOUND</div></div>
<div class="marquee"><span>3RITWO ✳ RAW SOUND ✳ INDEPENDENT MUSIC ✳ NO RULES ✳ 3RITWO ✳ RAW SOUND ✳ INDEPENDENT MUSIC ✳</span></div>
<section id="music"><div class="section-head"><h2>آرشیو <span>آثار</span></h2><small>THE SOUND ARCHIVE / 001—∞</small></div><div class="grid">
{% for s in songs %}
<div class="card">
{% if s[3] %}<img class="cover" src="/media/{{ s[3] }}" alt="{{ s[1] }}">{% else %}<div class="cover-placeholder">3R</div>{% endif %}
<div class="track-meta"><h3>{{ s[1] }}</h3><span class="track-no">NO. {{ '%02d' % loop.index }}</span></div><small class="artist">{{ s[2] }}</small>
{% if s[4] %}<audio controls preload="none" src="/media/{{ s[4] }}"></audio><a class="download" href="/media/{{ s[4] }}" download>↓ دانلود ترک</a>{% endif %}
{% if s[5] %}<details><summary>متن آهنگ +</summary><p class="lyrics">{{ s[5] }}</p></details>{% endif %}
{% if s[6] %}<details><summary>موزیک ویدیو +</summary><video controls preload="none" src="/media/{{ s[6] }}"></video></details>{% endif %}
</div>
{% else %}<div class="empty">هنوز ترکی منتشر نشده.<br><span style="color:#ff5a1f">THE ARCHIVE IS WAITING.</span><br>به‌زودی...</div>{% endfor %}
</div></section>
<section id="about" style="padding-top:0"><div style="border-top:1px solid #302a23;padding-top:25px;display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap"><div><div class="eyebrow">ABOUT THE ARTIST</div><h2 style="font-size:27px;margin:0 0 12px">صدا، بدون فیلتر.</h2><p style="color:#a59d92;line-height:2;max-width:520px;font-size:13px">3RITWO — موسیقی مستقل، حال‌وهوای دارک و روایت‌های شخصی. اینجا خانه‌ی رسمی ترک‌ها، متن‌ها و ویدیوهاست.</p></div><div style="direction:ltr;text-align:left;color:#655b50;font:12px/2 Impact,sans-serif;letter-spacing:2px">INDEPENDENT BY NATURE<br>BUILT FROM THE UNDERGROUND<br>© 3RITWO</div></div></section>
</main><footer><span>© 3RITWO — OFFICIAL ARCHIVE</span><b>KEEP IT RAW.</b></footer></body></html>
"""

ADMIN_PAGE = """
<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#090909"><title>پنل مدیریت 3RITWO</title>
<style>
:root{--bg:#090909;--panel:#14110e;--line:#382c22;--hot:#ff5a1f;--text:#f2eee7;--muted:#a59d92}*{box-sizing:border-box}body{background:radial-gradient(ellipse at top,#30170e 0,transparent 45%),var(--bg);color:var(--text);font-family:Tahoma,Arial,sans-serif;max-width:720px;margin:0 auto;padding:24px 16px;min-height:100vh}h1,h2{color:var(--hot)}h1{font:38px Impact,'Arial Black',sans-serif;direction:ltr;text-align:right;letter-spacing:1px}h2{font-size:20px}input,textarea{width:100%;padding:13px;margin:8px 0 15px;background:#0d0c0b;color:#fff;border:1px solid #45372b;border-radius:2px;font:14px Tahoma,Arial,sans-serif}input:focus,textarea:focus{outline:1px solid var(--hot);border-color:var(--hot)}button{padding:12px 18px;background:var(--hot);color:#100b08;border:1px solid var(--hot);border-radius:2px;cursor:pointer;font-weight:bold}button:hover{background:#d8a45c;border-color:#d8a45c}.card{background:var(--panel);border:1px solid var(--line);padding:15px;margin:12px 0}a{color:var(--hot);text-decoration:none}label{color:var(--muted);font-size:13px}hr{border:0;border-top:1px solid var(--line);margin:28px 0}.sub{color:var(--muted);line-height:2;font-size:13px}
</style></head><body><a href="/" style="font:22px Impact,sans-serif;direction:ltr;display:inline-block">3RITWO ↗</a><h1>CONTROL ROOM</h1><p class="sub">پنل انتشار و مدیریت آرشیو موسیقی</p>
{% if not logged %}<p>رمز عبور مدیر را وارد کن.</p><form method="post"><input type="hidden" name="action" value="login"><input type="password" name="password" placeholder="رمز عبور مدیر" required><button type="submit">ورود به پنل ↗</button></form>
{% else %}<h2>انتشار ترک جدید</h2><form method="post" enctype="multipart/form-data"><input type="hidden" name="action" value="add"><label>نام آهنگ</label><input name="title" placeholder="مثلاً Dejavu" required><label>نام هنرمند</label><input name="artist" value="3RITWO" required><label>کاور آهنگ</label><input type="file" name="cover" accept=".jpg,.jpeg,.png,.webp"><label>فایل صوتی</label><input type="file" name="audio" accept=".mp3,.wav,.ogg,.m4a,.aac,.flac"><label>متن ترانه</label><textarea name="lyrics" rows="7" placeholder="متن آهنگ را اینجا بنویس..."></textarea><label>موزیک ویدیو</label><input type="file" name="video" accept=".mp4,.webm,.mov"><button type="submit">انتشار در آرشیو +</button></form><hr><h2>ترک‌های منتشرشده</h2>
{% for s in songs %}<div class="card"><b>{{ s[1] }}</b><p class="sub">{{ s[2] }}</p><form method="post" onsubmit="return confirm('آهنگ حذف شود؟')"><input type="hidden" name="action" value="delete"><input type="hidden" name="id" value="{{ s[0] }}"><button type="submit">حذف ترک</button></form></div>{% else %}<p>هنوز آهنگی اضافه نکرده‌ای.</p>{% endfor %}<br><a href="/logout">خروج از پنل</a>{% endif %}<hr><a href="/">بازگشت به سایت ←</a></body></html>
"""


def is_admin():
    return session.get("admin") is True

def save_upload(field):
    file = request.files.get(field)
    if not file or not file.filename:
        return None
    filename = secure_filename(file.filename)
    if not filename or "." not in filename:
        raise ValueError("نام فایل معتبر نیست.")
    extension = filename.rsplit(".", 1)[1].lower()
    if extension not in ALLOWED[field]:
        raise ValueError("فرمت فایل مجاز نیست: " + field)
    filename = secrets.token_hex(8) + "_" + filename
    file.save(os.path.join(MEDIA_DIR, filename))
    return filename

@app.route("/")
def home():
    with db() as con:
        songs = con.execute("SELECT * FROM songs ORDER BY id DESC").fetchall()
    return render_template_string(PAGE, songs=songs)

@app.route("/media/<path:filename>")
def media(filename):
    return send_from_directory(MEDIA_DIR, filename)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        action = request.form.get("action", "")
        if action == "login":
            password = request.form.get("password", "")
            if secrets.compare_digest(password, ADMIN_PASSWORD):
                session.clear()
                session["admin"] = True
                return redirect("/admin")
            return "رمز اشتباه است. <a href='/admin'>تلاش دوباره</a>", 401

        if not is_admin():
            return "ابتدا وارد پنل مدیریت شو.", 403

        if action == "add":
            title = request.form.get("title", "").strip()
            artist = request.form.get("artist", "3RITWO").strip()
            if not title or not artist:
                return "نام آهنگ و هنرمند الزامی است.", 400

            uploaded = {"cover": None, "audio": None, "video": None}
            try:
                for field in ("cover", "audio", "video"):
                    uploaded[field] = save_upload(field)
                with db() as con:
                    con.execute(
                        """INSERT INTO songs (title, artist, cover, audio, lyrics, video)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                        (title, artist, uploaded["cover"], uploaded["audio"],
                         request.form.get("lyrics", ""), uploaded["video"])
                    )
            except ValueError as error:
                for filename in uploaded.values():
                    if filename:
                        try:
                            os.remove(os.path.join(MEDIA_DIR, filename))
                        except OSError:
                            pass
                return str(error), 400
            return redirect("/admin")

        if action == "delete":
            song_id = request.form.get("id", "")
            with db() as con:
                row = con.execute(
                    "SELECT cover, audio, video FROM songs WHERE id = ?", (song_id,)
                ).fetchone()
                con.execute("DELETE FROM songs WHERE id = ?", (song_id,))
            if row:
                for filename in row:
                    if filename:
                        try:
                            os.remove(os.path.join(MEDIA_DIR, filename))
                        except OSError:
                            pass
            return redirect("/admin")

    songs = []
    if is_admin():
        with db() as con:
            songs = con.execute("SELECT * FROM songs ORDER BY id DESC").fetchall()
    return render_template_string(ADMIN_PAGE, logged=is_admin(), songs=songs)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin")

if __name__ == "__main__":
    print("3RITWO Website Started!")
    print("Website: http://127.0.0.1:5000")
    print("Admin: http://127.0.0.1:5000/admin")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
