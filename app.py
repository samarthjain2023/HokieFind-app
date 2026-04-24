import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session
import mysql.connector
import bcrypt

load_dotenv()

app = Flask(__name__, template_folder="frontend")
app.secret_key = "super_secret_key"

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

# =========================
# AUTH ROUTES
# =========================

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first = request.form["first"]
        last = request.form["last"]
        email = request.form["email"]
        password = request.form["password"]

        if not first or not last or not email or not password:
            return redirect("/signup?error=missing_fields")

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
            return redirect("/signup?error=user_exists")

        return redirect("/login")

    return render_template("sign_up.html")


@app.route("/login", methods=["GET", "POST"])
def login():
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

        return redirect("/login?error=invalid")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# =========================
# MAIN ROUTES
# =========================

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")

    cursor.execute("SELECT * FROM listings")
    listings = cursor.fetchall()

    return render_template("index.html", listings=listings)


@app.route("/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect("/login")

    title = request.form["title"]
    description = request.form["description"]
    location = request.form["location"]
    image = request.form["image"]
    user_id = session["user_id"]

    if not title.strip() or not description.strip() or not location.strip():
        return redirect("/?error=missing_fields")

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
        return redirect("/login")

    cursor.execute("DELETE FROM listings WHERE listing_id = %s", (id,))
    db.commit()
    return redirect("/?success=deleted")


@app.route("/edit/<int:id>")
def edit(id):
    if "user_id" not in session:
        return redirect("/login")

    cursor.execute("SELECT * FROM listings WHERE listing_id = %s", (id,))
    listing = cursor.fetchone()
    return render_template("edit.html", listing=listing)


@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    if "user_id" not in session:
        return redirect("/login")

    location = request.form["location"]
    image = request.form["image"]

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
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    cursor.execute(
        "SELECT first_name, last_name, email FROM Users WHERE user_id = %s",
        (user_id,)
    )
    user = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM listings WHERE user_id = %s",
        (user_id,)
    )
    listings = cursor.fetchall()

    return render_template("account.html", user=user, listings=listings)


@app.route("/change_password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        return redirect("/login")

    current_password = request.form["current_password"]
    new_password = request.form["new_password"]

    if not current_password or not new_password:
        return redirect("/account?error=password_missing")

    cursor.execute(
        "SELECT password_hash FROM Users WHERE user_id = %s",
        (session["user_id"],)
    )
    result = cursor.fetchone()

    if result is None:
        return redirect("/login")

    stored_hash = result[0]

    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode('utf-8')

    if not bcrypt.checkpw(current_password.encode('utf-8'), stored_hash):
        return redirect("/account?error=wrong_password")

    new_hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    cursor.execute(
        "UPDATE Users SET password_hash = %s WHERE user_id = %s",
        (new_hashed, session["user_id"])
    )
    db.commit()

    return redirect("/account?success=password_updated")


# =========================
# ADMIN
# =========================

@app.route("/admin")
def admin():
    if "user_id" not in session or session.get("role") != "admin":
        return "Access denied"

    return render_template("admin.html")


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

    return redirect("/admin?success=user_created")


# =========================
# CLAIMS
# =========================

@app.route("/claim/<int:listing_id>", methods=["GET", "POST"])
def claim(listing_id):
    if "user_id" not in session:
        return redirect("/login")

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

    return render_template("claim_form.html", listing_id=listing_id)


@app.route("/claims/<int:listing_id>")
def view_claims(listing_id):
    if "user_id" not in session:
        return redirect("/login")

    cursor.execute(
        """
        SELECT c.claim_id, u.first_name, u.last_name, c.message_to_finder, c.claim_date
        FROM claims c
        JOIN Users u ON c.claimant_id = u.user_id
        WHERE c.listing_id = %s
        ORDER BY c.claim_date DESC
        """,
        (listing_id,)
    )

    claims = cursor.fetchall()

    return render_template("claims.html", claims=claims)


@app.route("/reports")
def reports():
    if "user_id" not in session:
        return redirect("/login")

    cursor.execute(
        """
        SELECT u.first_name, u.last_name, COUNT(l.listing_id) AS total_listings
        FROM Users u
        JOIN listings l ON u.user_id = l.user_id
        GROUP BY u.user_id, u.first_name, u.last_name
        ORDER BY total_listings DESC
        """
    )
    most_active_finders = cursor.fetchall()

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
    active_claims = cursor.fetchall()

    return render_template(
        "reports.html",
        most_active_finders=most_active_finders,
        active_claims=active_claims,
    )


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)