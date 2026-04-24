import os
import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, redirect, session, send_from_directory
from werkzeug.exceptions import RequestEntityTooLarge
import mysql.connector
import bcrypt

load_dotenv()

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_UPLOAD_FOLDER = os.path.join(_BASE_DIR, "static", "uploads")
_UI_KIT_DIR = os.path.join(_BASE_DIR, "frontend", "ui_kits", "hokiefind-web")
_FRONTEND_DIR = os.path.join(_BASE_DIR, "frontend")
os.makedirs(_UPLOAD_FOLDER, exist_ok=True)

_ALLOWED_IMAGE_EXT = frozenset({"png", "jpg", "jpeg", "gif", "webp"})
_MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MiB

app = Flask(__name__, template_folder="frontend")
app.secret_key = "super_secret_key"
app.config["MAX_CONTENT_LENGTH"] = _MAX_IMAGE_BYTES


def _image_ext(filename: str) -> str | None:
    if not filename or "." not in filename:
        return None
    ext = filename.rsplit(".", 1)[1].lower()
    return ext if ext in _ALLOWED_IMAGE_EXT else None


def _save_listing_image_file(file_storage):
    """
    Save uploaded image to static/uploads. Returns relative URL path for image_url, or None if invalid.
    """
    if not file_storage or not file_storage.filename:
        return None
    ext = _image_ext(file_storage.filename)
    if not ext:
        return None
    ct = (file_storage.content_type or "").lower()
    if ct and not ct.startswith("image/"):
        return None
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    dest = os.path.join(_UPLOAD_FOLDER, stored_name)
    file_storage.save(dest)
    return f"/static/uploads/{stored_name}"


@app.errorhandler(RequestEntityTooLarge)
def _handle_file_too_large(_e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "file_too_large", "message": "File exceeds 5 MB limit."}), 413
    if request.path.startswith("/update"):
        tail = request.path.replace("/update/", "", 1).split("/", 1)[0]
        if tail.isdigit():
            return redirect(f"/edit/{tail}?error=file_too_large")
    return redirect("/?error=file_too_large")

# DATABASE CONNECTION
for _key in ("MYSQL_USER", "MYSQL_DATABASE"):
    if not os.getenv(_key):
        raise RuntimeError(
            f"Set {_key} in .env (copy from .env.example). MYSQL_PASSWORD may be empty for local dev."
        )

db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    user=os.environ["MYSQL_USER"],
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.environ["MYSQL_DATABASE"],
)

cursor = db.cursor()


def _status_slug(status_name):
    if not status_name:
        return "active"
    n = (status_name or "").strip().lower()
    if n in ("approved", "closed"):
        return "returned"
    if n in ("pending", "under review", "rejected"):
        return "pending"
    return "active"


def _listing_row_to_dict(row, current_user_id):
    (
        listing_id,
        user_id,
        _item_id,
        location_found,
        date_posted,
        _status_id,
        image_url,
        title,
        description,
        status_name,
    ) = row
    posted = date_posted.isoformat() if hasattr(date_posted, "isoformat") else str(date_posted or "")
    date_s = posted[:10] if len(posted) >= 10 else posted
    return {
        "id": listing_id,
        "title": title or "",
        "description": description or "",
        "location": location_found or "",
        "photo": image_url or None,
        "date": date_s,
        "status": _status_slug(status_name),
        "mine": user_id == current_user_id,
        "userId": user_id,
    }


def _require_login_json():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401
    return None


# =========================
# JSON API (React UI)
# =========================


@app.route("/api/me", methods=["GET"])
def api_me():
    if "user_id" not in session:
        return jsonify({"authenticated": False}), 200

    uid = session["user_id"]
    cursor.execute(
        "SELECT first_name, last_name, email FROM Users WHERE user_id = %s",
        (uid,),
    )
    row = cursor.fetchone()
    if not row:
        session.clear()
        return jsonify({"authenticated": False}), 200

    return jsonify(
        {
            "authenticated": True,
            "user_id": uid,
            "first_name": row[0],
            "last_name": row[1],
            "email": row[2],
            "role": session.get("role", "user"),
        }
    )


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"ok": False, "error": "missing_fields"}), 400

    cursor.execute(
        """
        SELECT u.user_id, u.password_hash, COALESCE(r.role_name, 'user')
        FROM Users u
        LEFT JOIN roles r ON u.role_id = r.role_id
        WHERE u.email = %s
        """,
        (email,),
    )
    user = cursor.fetchone()

    if not user:
        return jsonify({"ok": False, "error": "invalid"}), 401

    user_id, stored_hash, role = user
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode("utf-8")

    if not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        return jsonify({"ok": False, "error": "invalid"}), 401

    session["user_id"] = user_id
    session["role"] = role.lower()
    return jsonify({"ok": True, "role": session["role"]})


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"ok": True})


@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json(silent=True) or {}
    first = (data.get("first") or "").strip()
    last = (data.get("last") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not first or not last or not email or not password:
        return jsonify({"ok": False, "error": "missing_fields"}), 400

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    try:
        cursor.execute(
            """
            INSERT INTO Users (first_name, last_name, email, password_hash, role_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (first, last, email, hashed, 3),
        )
        db.commit()
    except Exception:
        return jsonify({"ok": False, "error": "user_exists"}), 400

    return jsonify({"ok": True})


@app.route("/api/listings", methods=["GET"])
def api_listings():
    err = _require_login_json()
    if err:
        return err

    uid = session["user_id"]
    cursor.execute(
        """
        SELECT l.listing_id, l.user_id, l.item_id, l.location_found, l.date_posted, l.status_id,
               l.image_url, l.title, l.description, COALESCE(cs.status_name, '')
        FROM listings l
        LEFT JOIN claim_status cs ON l.status_id = cs.status_id
        WHERE l.title IS NOT NULL AND l.description IS NOT NULL
        ORDER BY l.date_posted DESC
        """
    )
    rows = cursor.fetchall()
    return jsonify({"listings": [_listing_row_to_dict(r, uid) for r in rows]})


@app.route("/api/listings", methods=["POST"])
def api_listings_create():
    err = _require_login_json()
    if err:
        return err

    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()
    location = (request.form.get("location") or "").strip()
    user_id = session["user_id"]

    if not title or not description or not location:
        return jsonify({"error": "missing_fields"}), 400

    upload = request.files.get("image_file")
    saved = _save_listing_image_file(upload)
    if upload and upload.filename and saved is None:
        return jsonify({"error": "invalid_image"}), 400
    image = saved if saved else (request.form.get("image") or "").strip()

    cursor.execute(
        """
        INSERT INTO listings (user_id, title, description, location_found, image_url)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, title, description, location, image),
    )
    db.commit()
    new_id = cursor.lastrowid

    cursor.execute(
        """
        SELECT l.listing_id, l.user_id, l.item_id, l.location_found, l.date_posted, l.status_id,
               l.image_url, l.title, l.description, COALESCE(cs.status_name, '')
        FROM listings l
        LEFT JOIN claim_status cs ON l.status_id = cs.status_id
        WHERE l.listing_id = %s
        """,
        (new_id,),
    )
    row = cursor.fetchone()
    return jsonify({"listing": _listing_row_to_dict(row, user_id)}), 201


@app.route(
    "/api/listings/<int:listing_id>",
    methods=["GET", "DELETE", "PUT", "PATCH"],
)
def api_listing_by_id(listing_id):
    err = _require_login_json()
    if err:
        return err

    uid = session["user_id"]

    if request.method == "GET":
        cursor.execute(
            """
            SELECT l.listing_id, l.user_id, l.item_id, l.location_found, l.date_posted, l.status_id,
                   l.image_url, l.title, l.description, COALESCE(cs.status_name, '')
            FROM listings l
            LEFT JOIN claim_status cs ON l.status_id = cs.status_id
            WHERE l.listing_id = %s
            """,
            (listing_id,),
        )
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "not_found"}), 404
        return jsonify({"listing": _listing_row_to_dict(row, uid)})

    if request.method == "DELETE":
        cursor.execute("DELETE FROM listings WHERE listing_id = %s", (listing_id,))
        db.commit()
        return jsonify({"ok": True})

    # PUT / PATCH — multipart form (location, optional image_file, optional image URL)
    location = (request.form.get("location") or "").strip()
    if not location:
        return jsonify({"error": "missing_fields"}), 400

    upload = request.files.get("image_file")
    saved = _save_listing_image_file(upload)
    if upload and upload.filename and saved is None:
        return jsonify({"error": "invalid_image"}), 400
    if saved:
        image = saved
    else:
        image = (request.form.get("image") or "").strip()

    cursor.execute(
        "UPDATE listings SET location_found = %s, image_url = %s WHERE listing_id = %s",
        (location, image, listing_id),
    )
    db.commit()

    cursor.execute(
        """
        SELECT l.listing_id, l.user_id, l.item_id, l.location_found, l.date_posted, l.status_id,
               l.image_url, l.title, l.description, COALESCE(cs.status_name, '')
        FROM listings l
        LEFT JOIN claim_status cs ON l.status_id = cs.status_id
        WHERE l.listing_id = %s
        """,
        (listing_id,),
    )
    row = cursor.fetchone()
    return jsonify({"listing": _listing_row_to_dict(row, uid) if row else None})


@app.route("/api/listings/<int:listing_id>/claims", methods=["GET"])
def api_listing_claims(listing_id):
    err = _require_login_json()
    if err:
        return err

    cursor.execute("SELECT title FROM listings WHERE listing_id = %s", (listing_id,))
    lt = cursor.fetchone()
    item_title = lt[0] if lt else ""

    cursor.execute(
        """
        SELECT c.claim_id, u.first_name, u.last_name, c.message_to_finder, c.claim_date,
               COALESCE(cs.status_name, 'Pending')
        FROM claims c
        JOIN Users u ON c.claimant_id = u.user_id
        LEFT JOIN claim_status cs ON c.status_id = cs.status_id
        WHERE c.listing_id = %s
        ORDER BY c.claim_date DESC
        """,
        (listing_id,),
    )
    out = []
    for r in cursor.fetchall():
        cid, fn, ln, msg, cdate, stname = r
        ds = cdate.isoformat(sep=" ")[:19] if hasattr(cdate, "isoformat") else str(cdate)
        slug = "returned" if (stname or "").lower() in ("approved", "closed") else "pending"
        out.append(
            {
                "id": cid,
                "firstName": fn,
                "lastName": ln,
                "message": msg or "",
                "date": ds,
                "status": slug,
                "itemTitle": item_title or "",
            }
        )
    return jsonify({"claims": out})


@app.route("/api/listings/<int:listing_id>/claims", methods=["POST"])
def api_listing_claim_create(listing_id):
    err = _require_login_json()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    user_id = session["user_id"]

    if not message:
        return jsonify({"error": "empty"}), 400

    cursor.execute(
        """
        INSERT INTO claims (listing_id, claimant_id, message_to_finder, status_id)
        VALUES (%s, %s, %s, %s)
        """,
        (listing_id, user_id, message, 1),
    )
    db.commit()
    return jsonify({"ok": True}), 201


@app.route("/api/account/listings", methods=["GET"])
def api_account_listings():
    err = _require_login_json()
    if err:
        return err

    uid = session["user_id"]
    cursor.execute(
        """
        SELECT l.listing_id, l.user_id, l.item_id, l.location_found, l.date_posted, l.status_id,
               l.image_url, l.title, l.description, COALESCE(cs.status_name, '')
        FROM listings l
        LEFT JOIN claim_status cs ON l.status_id = cs.status_id
        WHERE l.user_id = %s AND l.title IS NOT NULL AND l.description IS NOT NULL
        ORDER BY l.date_posted DESC
        """,
        (uid,),
    )
    rows = cursor.fetchall()
    return jsonify({"listings": [_listing_row_to_dict(r, uid) for r in rows]})


@app.route("/api/account/password", methods=["POST"])
def api_account_password():
    err = _require_login_json()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    current_password = data.get("current_password") or ""
    new_password = data.get("new_password") or ""

    if not current_password or not new_password:
        return jsonify({"error": "password_missing"}), 400

    cursor.execute(
        "SELECT password_hash FROM Users WHERE user_id = %s",
        (session["user_id"],),
    )
    result = cursor.fetchone()

    if result is None:
        return jsonify({"error": "unauthorized"}), 401

    stored_hash = result[0]
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode("utf-8")

    if not bcrypt.checkpw(current_password.encode("utf-8"), stored_hash):
        return jsonify({"error": "wrong_password"}), 400

    new_hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
    cursor.execute(
        "UPDATE Users SET password_hash = %s WHERE user_id = %s",
        (new_hashed, session["user_id"]),
    )
    db.commit()
    return jsonify({"ok": True})


@app.route("/api/reports", methods=["GET"])
def api_reports():
    err = _require_login_json()
    if err:
        return err

    cursor.execute(
        """
        SELECT u.first_name, u.last_name, COUNT(l.listing_id) AS total_listings
        FROM Users u
        JOIN listings l ON u.user_id = l.user_id
        GROUP BY u.user_id, u.first_name, u.last_name
        ORDER BY total_listings DESC
        """
    )
    finders = [
        {"first_name": r[0], "last_name": r[1], "total_listings": int(r[2])}
        for r in cursor.fetchall()
    ]

    cursor.execute(
        """
        SELECT u.first_name, u.last_name, i.item_name, cs.status_name, c.claim_date
        FROM claims c
        JOIN Users u ON c.claimant_id = u.user_id
        JOIN listings l ON c.listing_id = l.listing_id
        JOIN items i ON l.item_id = i.item_id
        JOIN claim_status cs ON c.status_id = cs.status_id
        ORDER BY c.claim_date DESC
        """
    )
    active = []
    for r in cursor.fetchall():
        cd = r[4]
        ds = cd.isoformat(sep=" ")[:19] if hasattr(cd, "isoformat") else str(cd)
        active.append(
            {
                "first_name": r[0],
                "last_name": r[1],
                "item_name": r[2],
                "status_name": r[3],
                "claim_date": ds,
            }
        )

    return jsonify({"most_active_finders": finders, "active_claims": active})


@app.route("/api/admin/users", methods=["POST"])
def api_admin_create_user():
    err = _require_login_json()
    if err:
        return err
    if session.get("role") != "admin":
        return jsonify({"error": "forbidden"}), 403

    data = request.get_json(silent=True) or {}
    first = (data.get("first") or "").strip()
    last = (data.get("last") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not first or not last or not email or not password:
        return jsonify({"error": "missing_fields"}), 400

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    try:
        cursor.execute(
            """
            INSERT INTO Users (first_name, last_name, email, password_hash, role_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (first, last, email, hashed, 3),
        )
        db.commit()
    except Exception:
        return jsonify({"error": "user_exists"}), 400

    return jsonify({"ok": True}), 201


# =========================
# AUTH ROUTES
# =========================

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return redirect("/")

    if request.method == "POST":
        first = request.form["first"]
        last = request.form["last"]
        email = request.form["email"]
        password = request.form["password"]

        if not first or not last or not email or not password:
            return redirect("/?error=signup_missing_fields")

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            cursor.execute(
                """
                INSERT INTO Users (first_name, last_name, email, password_hash, role_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (first, last, email, hashed, 3)
            )
            db.commit()
        except:
            return redirect("/?error=signup_user_exists")

        return redirect("/")

    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return redirect("/")

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            """
            SELECT u.user_id, u.password_hash, COALESCE(r.role_name, 'user')
            FROM Users u
            LEFT JOIN roles r ON u.role_id = r.role_id
            WHERE u.email = %s
            """,
            (email,)
        )
        user = cursor.fetchone()

        if user:
            user_id, stored_hash, role = user

            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')

            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                session["user_id"] = user_id
                session["role"] = role.lower()
                return redirect("/")

        return redirect("/?error=invalid_login")

    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =========================
# MAIN ROUTES (SPA shell + legacy form posts)
# =========================

@app.route("/")
def index():
    return send_from_directory(_UI_KIT_DIR, "index.html")


@app.route("/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect("/")

    title = request.form["title"]
    description = request.form["description"]
    location = request.form["location"]
    user_id = session["user_id"]

    if not title.strip() or not description.strip() or not location.strip():
        return redirect("/?error=missing_fields")

    upload = request.files.get("image_file")
    saved = _save_listing_image_file(upload)
    if upload and upload.filename and saved is None:
        return redirect("/?error=invalid_image")
    image = saved if saved else (request.form.get("image") or "").strip()

    cursor.execute(
        """
        INSERT INTO listings (user_id, title, description, location_found, image_url)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, title, description, location, image)
    )
    db.commit()

    return redirect("/?success=added")


@app.route("/delete/<int:id>")
def delete(id):
    if "user_id" not in session:
        return redirect("/")

    cursor.execute("DELETE FROM listings WHERE listing_id = %s", (id,))
    db.commit()
    return redirect("/?success=deleted")


@app.route("/edit/<int:id>")
def edit(id):
    return redirect("/")


@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    if "user_id" not in session:
        return redirect("/")

    location = request.form["location"]

    upload = request.files.get("image_file")
    saved = _save_listing_image_file(upload)
    if upload and upload.filename and saved is None:
        return redirect(f"/edit/{id}?error=invalid_image")
    if saved:
        image = saved
    else:
        image = (request.form.get("image") or "").strip()

    cursor.execute(
        "UPDATE listings SET location_found = %s, image_url = %s WHERE listing_id = %s",
        (location, image, id)
    )
    db.commit()

    return redirect("/?success=updated")


# =========================
# ACCOUNT + PASSWORD
# =========================

@app.route("/account")
def account():
    return redirect("/")


@app.route("/change_password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        return redirect("/")

    current_password = request.form["current_password"]
    new_password = request.form["new_password"]

    if not current_password or not new_password:
        return redirect("/?error=password_missing")

    cursor.execute(
        "SELECT password_hash FROM Users WHERE user_id = %s",
        (session["user_id"],)
    )
    result = cursor.fetchone()

    if result is None:
        return redirect("/")

    stored_hash = result[0]

    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode('utf-8')

    if not bcrypt.checkpw(current_password.encode('utf-8'), stored_hash):
        return redirect("/?error=wrong_password")

    new_hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    cursor.execute(
        "UPDATE Users SET password_hash = %s WHERE user_id = %s",
        (new_hashed, session["user_id"])
    )
    db.commit()

    return redirect("/?success=password_updated")


# =========================
# ADMIN
# =========================

@app.route("/admin")
def admin():
    return redirect("/")


@app.route("/admin/create_user", methods=["POST"])
def create_user():
    if "user_id" not in session or session.get("role") != "admin":
        return "Access denied"

    first = request.form["first"]
    last = request.form["last"]
    email = request.form["email"]
    password = request.form["password"]

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    cursor.execute(
        """
        INSERT INTO Users (first_name, last_name, email, password_hash, role_id)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (first, last, email, hashed, 3)
    )
    db.commit()

    return redirect("/?success=user_created")


# =========================
# CLAIMS
# =========================

@app.route("/claim/<int:listing_id>", methods=["GET", "POST"])
def claim(listing_id):
    if "user_id" not in session:
        return redirect("/")

    if request.method == "POST":
        message = request.form["message"]
        user_id = session["user_id"]

        if not message.strip():
            return redirect(f"/claim/{listing_id}?error=empty")

        cursor.execute(
            """
            INSERT INTO claims (listing_id, claimant_id, message_to_finder, status_id)
            VALUES (%s, %s, %s, %s)
            """,
            (listing_id, user_id, message, 1)
        )
        db.commit()

        return redirect("/?success=claim_submitted")

    return redirect("/")


@app.route("/claims/<int:_listing_id>")
def view_claims(_listing_id):
    return redirect("/")


@app.route("/reports")
def reports():
    return redirect("/")


@app.route("/colors_and_type.css")
def serve_design_tokens_css():
    """kit.css @imports ../../colors_and_type.css → resolves to /colors_and_type.css when kit is at /ui-kit/."""
    return send_from_directory(_FRONTEND_DIR, "colors_and_type.css")


@app.route("/fonts/<path:filename>")
def serve_frontend_fonts(filename):
    """@font-face in colors_and_type.css uses url(fonts/...) → /fonts/... from site root."""
    return send_from_directory(os.path.join(_FRONTEND_DIR, "fonts"), filename)


@app.route("/ui-kit")
def ui_kit_redirect():
    return redirect("/ui-kit/")


@app.route("/ui-kit/")
def ui_kit_index():
    """SPA is served at `/`; keep assets under `/ui-kit/<file>`."""
    return redirect("/")


@app.route("/ui-kit/<path:asset>")
def ui_kit_asset(asset):
    return send_from_directory(_UI_KIT_DIR, asset)


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)