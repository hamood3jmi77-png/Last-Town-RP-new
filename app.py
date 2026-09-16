import os
import functools
import uuid

from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, g
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from db import get_db, init_db, get_content_dict

BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXT = {"png", "jpg", "jpeg", "webp", "gif", "svg", "ico"}

app = Flask(__name__)
app.secret_key = os.environ.get("LASTTOWN_SECRET_KEY", "dev-secret-change-in-production")

init_db()

def get_all_content():
    if "content" not in g:
        g.content = get_content_dict()
    return g.content

@app.context_processor
def inject_globals():
    conn = get_db()
    social_links = conn.execute(
        "SELECT * FROM social_links ORDER BY sort_order, id"
    ).fetchall()
    conn.close()
    return {
        "c": get_all_content(),
        "social_links": social_links,
    }

def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

def save_upload(file_storage):
    if not file_storage or file_storage.filename == "":
        return None
    filename = secure_filename(file_storage.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXT:
        return None
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_storage.save(os.path.join(UPLOAD_DIR, unique_name))
    return f"/static/uploads/{unique_name}"

@app.route("/")
def home():
    conn = get_db()
    timeline = conn.execute(
        "SELECT * FROM timeline_items ORDER BY sort_order, id"
    ).fetchall()
    events = conn.execute("SELECT * FROM events ORDER BY sort_order, id").fetchall()
    servers = conn.execute("SELECT * FROM servers ORDER BY sort_order, id").fetchall()
    conn.close()
    return render_template(
        "home.html", timeline=timeline, events=events, servers=servers
    )

@app.route("/faq")
def faq():
    conn = get_db()
    faqs = conn.execute("SELECT * FROM faqs ORDER BY sort_order, id").fetchall()
    conn.close()
    return render_template("faq.html", faqs=faqs)

@app.route("/team")
def team():
    conn = get_db()
    members = conn.execute(
        "SELECT * FROM team_members ORDER BY sort_order, id"
    ).fetchall()
    conn.close()
    return render_template("team.html", members=members)

@app.route("/careers")
def careers():
    conn = get_db()
    jobs = conn.execute("SELECT * FROM jobs ORDER BY sort_order, id").fetchall()
    conn.close()
    return render_template("careers.html", jobs=jobs)

@app.route("/roster")
def roster():
    conn = get_db()
    creators = conn.execute(
        "SELECT * FROM roster_creators ORDER BY sort_order, id"
    ).fetchall()
    conn.close()
    return render_template("roster.html", creators=creators)

@app.route("/leaderboard")
def leaderboard():
    conn = get_db()
    entries = conn.execute(
        "SELECT * FROM leaderboard_entries ORDER BY rank, sort_order, id"
    ).fetchall()
    conn.close()
    return render_template("leaderboard.html", entries=entries)

@app.route("/live")
def live():
    conn = get_db()
    streams = conn.execute(
        "SELECT * FROM streams WHERE is_live = 1 ORDER BY sort_order, id"
    ).fetchall()
    conn.close()
    return render_template("live.html", streams=streams)

@app.route("/login")
@app.route("/onboarding")
def onboarding():
    return render_template("onboarding.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM admin_users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["admin_id"] = user["id"]
            session["admin_username"] = user["username"]
            flash("تم تسجيل الدخول بنجاح", "success")
            return redirect(request.args.get("next") or url_for("admin_dashboard"))
        flash("اسم المستخدم أو كلمة المرور غير صحيحة", "error")
    return render_template("admin/login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

@app.route("/admin")
@login_required
def admin_dashboard():
    conn = get_db()
    counts = {
        "team": conn.execute("SELECT COUNT(*) c FROM team_members").fetchone()["c"],
        "roster": conn.execute("SELECT COUNT(*) c FROM roster_creators").fetchone()["c"],
        "jobs": conn.execute("SELECT COUNT(*) c FROM jobs").fetchone()["c"],
        "faqs": conn.execute("SELECT COUNT(*) c FROM faqs").fetchone()["c"],
        "events": conn.execute("SELECT COUNT(*) c FROM events").fetchone()["c"],
        "streams": conn.execute("SELECT COUNT(*) c FROM streams").fetchone()["c"],
        "timeline": conn.execute("SELECT COUNT(*) c FROM timeline_items").fetchone()["c"],
        "servers": conn.execute("SELECT COUNT(*) c FROM servers").fetchone()["c"],
        "leaderboard": conn.execute("SELECT COUNT(*) c FROM leaderboard_entries").fetchone()["c"],
    }
    conn.close()
    return render_template("admin/dashboard.html", counts=counts)

CONTENT_GROUPS = {
    "site": "هوية الموقع (Site Identity)",
    "nav": "شريط التنقل (Navbar)",
    "home": "الصفحة الرئيسية (Home)",
    "shared": "نصوص مشتركة (Shared)",
    "faq": "الأسئلة الشائعة (FAQ)",
    "team": "الفريق (Team)",
    "careers": "الوظائف (Careers)",
    "auth": "تسجيل الدخول (Sign In)",
    "leaderboard": "لوحة المتصدرين (Leaderboard)",
    "live": "البث المباشر (Live)",
    "roster": "قائمة صناع المحتوى (Roster)",
    "footer": "التذييل (Footer)",
}

@app.route("/admin/content/<group>", methods=["GET", "POST"])
@login_required
def admin_content_group(group):
    if group not in CONTENT_GROUPS:
        flash("قسم غير موجود", "error")
        return redirect(url_for("admin_dashboard"))

    conn = get_db()
    if request.method == "POST":
        for key, value in request.form.items():
            if key.startswith(f"{group}."):
                conn.execute(
                    "UPDATE content SET value = ? WHERE key = ?", (value, key)
                )
        conn.commit()
        flash("تم الحفظ بنجاح", "success")

    rows = conn.execute(
        "SELECT * FROM content WHERE key LIKE ? ORDER BY key", (f"{group}.%",)
    ).fetchall()
    conn.close()
    return render_template(
        "admin/content_group.html",
        group=group,
        group_label=CONTENT_GROUPS[group],
        rows=rows,
        groups=CONTENT_GROUPS,
    )

@app.route("/admin/content/<group>/upload/<key>", methods=["POST"])
@login_required
def admin_content_upload(group, key):
    path = save_upload(request.files.get("file"))
    if path:
        conn = get_db()
        conn.execute("UPDATE content SET value = ? WHERE key = ?", (path, key))
        conn.commit()
        conn.close()
        flash("تم رفع الصورة", "success")
    else:
        flash("فشل رفع الصورة - تأكد من نوع الملف", "error")
    return redirect(url_for("admin_content_group", group=group))

COLLECTIONS = {
    "team": {
        "table": "team_members",
        "label": "أعضاء الفريق",
        "fields": [
            ("name", "text", "الاسم"),
            ("role", "text", "المنصب"),
            ("image", "image", "الصورة"),
            ("sort_order", "number", "الترتيب"),
        ],
    },
    "roster": {
        "table": "roster_creators",
        "label": "صناع المحتوى والقضاة",
        "fields": [
            ("name", "text", "الاسم"),
            ("platform", "text", "المنصة"),
            ("image", "image", "الصورة"),
            ("url", "text", "الرابط"),
            ("sort_order", "number", "الترتيب"),
        ],
    },
    "jobs": {
        "table": "jobs",
        "label": "الوظائف الشاغرة",
        "fields": [
            ("title", "text", "المسمى الوظيفي"),
            ("department", "text", "القسم"),
            ("location", "text", "الموقع"),
            ("job_type", "text", "نوع الدوام"),
            ("description", "textarea", "الوصف"),
            ("sort_order", "number", "الترتيب"),
        ],
    },
    "faqs": {
        "table": "faqs",
        "label": "الأسئلة الشائعة",
        "fields": [
            ("question", "text", "السؤال"),
            ("answer", "textarea", "الجواب"),
            ("sort_order", "number", "الترتيب"),
        ],
    },
    "events": {
        "table": "events",
        "label": "أحداث LAST TOWN",
        "fields": [
            ("title", "text", "العنوان"),
            ("category", "text", "التصنيف (War/Rivalry/Racing/Heist/Event)"),
            ("image", "image", "الصورة"),
            ("event_date", "text", "التاريخ"),
            ("sort_order", "number", "الترتيب"),
        ],
    },
    "streams": {
        "table": "streams",
        "label": "البثوث المباشرة",
        "fields": [
            ("creator_name", "text", "اسم الصانع"),
            ("platform", "text", "المنصة"),
            ("url", "text", "الرابط"),
            ("thumbnail", "image", "الصورة المصغرة"),
            ("is_live", "checkbox", "مباشر الآن؟"),
            ("sort_order", "number", "الترتيب"),
        ],
    },
    "timeline": {
        "table": "timeline_items",
        "label": "الجدول الزمني (THE JOURNEY)",
        "fields": [
            ("year", "text", "السنة"),
            ("title", "text", "العنوان"),
            ("description", "textarea", "الوصف"),
            ("sort_order", "number", "الترتيب"),
        ],
    },
    "servers": {
        "table": "servers",
        "label": "السيرفرات (Choose Your Adventure)",
        "fields": [
            ("name", "text", "الاسم"),
            ("description", "textarea", "الوصف"),
            ("image", "image", "الصورة"),
            ("join_url", "text", "رابط الانضمام"),
            ("sort_order", "number", "الترتيب"),
        ],
    },
    "leaderboard": {
        "table": "leaderboard_entries",
        "label": "لوحة المتصدرين (يدوي)",
        "fields": [
            ("rank", "number", "الترتيب"),
            ("player_name", "text", "اسم اللاعب"),
            ("playtime", "text", "وقت اللعب"),
            ("sort_order", "number", "ترتيب العرض"),
        ],
    },
    "social": {
        "table": "social_links",
        "label": "روابط التواصل الاجتماعي",
        "fields": [
            ("platform", "text", "المنصة (youtube/tiktok/instagram/x/discord)"),
            ("url", "text", "الرابط"),
            ("sort_order", "number", "الترتيب"),
        ],
    },
}

def _coerce_field(field_type, raw_value, existing_value=None):
    if field_type == "checkbox":
        return 1 if raw_value is not None else 0
    if field_type == "number":
        try:
            return int(raw_value)
        except (TypeError, ValueError):
            return 0
    return raw_value or ""

@app.route("/admin/collection/<key>")
@login_required
def admin_collection_list(key):
    if key not in COLLECTIONS:
        flash("قسم غير موجود", "error")
        return redirect(url_for("admin_dashboard"))
    cfg = COLLECTIONS[key]
    conn = get_db()
    items = conn.execute(
        f"SELECT * FROM {cfg['table']} ORDER BY sort_order, id"
    ).fetchall()
    conn.close()
    return render_template(
        "admin/collection_list.html", key=key, cfg=cfg, items=items
    )

@app.route("/admin/collection/<key>/new", methods=["GET", "POST"])
@app.route("/admin/collection/<key>/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def admin_collection_edit(key, item_id=None):
    if key not in COLLECTIONS:
        flash("قسم غير موجود", "error")
        return redirect(url_for("admin_dashboard"))
    cfg = COLLECTIONS[key]
    conn = get_db()
    item = None
    if item_id:
        item = conn.execute(
            f"SELECT * FROM {cfg['table']} WHERE id = ?", (item_id,)
        ).fetchone()
        if not item:
            conn.close()
            flash("العنصر غير موجود", "error")
            return redirect(url_for("admin_collection_list", key=key))

    if request.method == "POST":
        values = {}
        for field_name, field_type, _label in cfg["fields"]:
            if field_type == "image":
                uploaded = save_upload(request.files.get(field_name))
                if uploaded:
                    values[field_name] = uploaded
                else:
                    values[field_name] = request.form.get(
                        field_name + "_existing", ""
                    )
            else:
                values[field_name] = _coerce_field(
                    field_type, request.form.get(field_name)
                )

        if item_id:
            set_clause = ", ".join(f"{f} = ?" for f in values)
            conn.execute(
                f"UPDATE {cfg['table']} SET {set_clause} WHERE id = ?",
                (*values.values(), item_id),
            )
        else:
            cols = ", ".join(values.keys())
            placeholders = ", ".join("?" for _ in values)
            conn.execute(
                f"INSERT INTO {cfg['table']} ({cols}) VALUES ({placeholders})",
                tuple(values.values()),
            )
        conn.commit()
        conn.close()
        flash("تم الحفظ بنجاح", "success")
        return redirect(url_for("admin_collection_list", key=key))

    conn.close()
    return render_template(
        "admin/collection_edit.html", key=key, cfg=cfg, item=item
    )

@app.route("/admin/collection/<key>/<int:item_id>/delete", methods=["POST"])
@login_required
def admin_collection_delete(key, item_id):
    if key not in COLLECTIONS:
        flash("قسم غير موجود", "error")
        return redirect(url_for("admin_dashboard"))
    cfg = COLLECTIONS[key]
    conn = get_db()
    conn.execute(f"DELETE FROM {cfg['table']} WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    flash("تم الحذف", "success")
    return redirect(url_for("admin_collection_list", key=key))

@app.route("/admin/account", methods=["GET", "POST"])
@login_required
def admin_account():
    conn = get_db()
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_username = request.form.get("username", "").strip()
        new_password = request.form.get("new_password", "")

        user = conn.execute(
            "SELECT * FROM admin_users WHERE id = ?", (session["admin_id"],)
        ).fetchone()

        if not check_password_hash(user["password_hash"], current_password):
            flash("كلمة المرور الحالية غير صحيحة", "error")
        else:
            if new_username:
                conn.execute(
                    "UPDATE admin_users SET username = ? WHERE id = ?",
                    (new_username, user["id"]),
                )
                session["admin_username"] = new_username
            if new_password:
                conn.execute(
                    "UPDATE admin_users SET
