from flask import Flask, render_template, request, redirect, session
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = "super_secret_key"

# DATABASE CONNECTION
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="newpassword",  # update if needed
    database="lost_and_found"
)

cursor = db.cursor()

# =========================
# AUTH ROUTES
# =========================

# SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first = request.form["first"]
        last = request.form["last"]
        email = request.form["email"]
        password = request.form["password"]

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            cursor.execute(
                "INSERT INTO Users (first_name, last_name, email, password_hash) VALUES (%s, %s, %s, %s)",
                (first, last, email, hashed)
            )
            db.commit()
        except:
            return "User already exists or error occurred"

        return redirect("/login")

    return '''
        <h2>Signup</h2>
        <form method="POST">
            First Name: <input name="first"><br>
            Last Name: <input name="last"><br>
            Email: <input name="email"><br>
            Password: <input type="password" name="password"><br>
            <button type="submit">Sign Up</button>
        </form>
    '''

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            stored_hash = user[4]  # password_hash column

            # handle both bytes and string cases
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')

            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                session["user_id"] = user[0]
                return redirect("/")

        return "Invalid login"

    return '''
        <h2>Login</h2>
        <form method="POST">
            Email: <input name="email"><br>
            Password: <input type="password" name="password"><br>
            <button type="submit">Login</button>
        </form>

        <p>Don't have an account?</p>
        <a href="/signup">
            <button>Sign Up</button>
        </a>
    '''

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# =========================
# MAIN ROUTES (PROTECTED)
# =========================

# VIEW LISTINGS
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")

    cursor.execute("SELECT * FROM listings")
    listings = cursor.fetchall()
    return render_template("index.html", listings=listings)

# ADD LISTING
@app.route("/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect("/login")

    title = request.form["title"]
    description = request.form["description"]
    location = request.form["location"]
    image = request.form["image"]
    user_id = session["user_id"]

    cursor.execute(
        "INSERT INTO listings (user_id, title, description, location_found, image_url) VALUES (%s, %s, %s, %s, %s)",
        (user_id, title, description, location, image)
    )
    db.commit()

    return redirect("/")

# DELETE LISTING
@app.route("/delete/<int:id>")
def delete(id):
    if "user_id" not in session:
        return redirect("/login")

    cursor.execute("DELETE FROM listings WHERE listing_id = %s", (id,))
    db.commit()
    return redirect("/")

# SHOW EDIT FORM
@app.route("/edit/<int:id>")
def edit(id):
    if "user_id" not in session:
        return redirect("/login")

    cursor.execute("SELECT * FROM listings WHERE listing_id = %s", (id,))
    listing = cursor.fetchone()
    return render_template("edit.html", listing=listing)

# UPDATE LISTING
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

    return redirect("/")

@app.route("/account")
def account():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    # Get user info
    cursor.execute(
        "SELECT first_name, last_name, email FROM Users WHERE user_id = %s",
        (user_id,)
    )
    user = cursor.fetchone()

    # Get user's listings
    cursor.execute(
        "SELECT listing_id, location_found, image_url FROM listings WHERE user_id = %s",
        (user_id,)
    )
    listings = cursor.fetchall()

    return render_template("account.html", user=user, listings=listings)

@app.route("/claim/<int:listing_id>", methods=["GET", "POST"])
def claim(listing_id):
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        message = request.form["message"]
        user_id = session["user_id"]

        cursor.execute(
            "INSERT INTO claims (listing_id, claimant_id, message_to_finder) VALUES (%s, %s, %s)",
            (listing_id, user_id, message)
        )
        db.commit()

        return redirect("/")

    return f'''
        <h2>Claim Item</h2>
        <form method="POST">
            <textarea name="message" placeholder="Describe why this item is yours" required></textarea><br>
            <button type="submit">Submit Claim</button>
        </form>
    '''

@app.route("/claims/<int:listing_id>")
def view_claims(listing_id):
    if "user_id" not in session:
        return redirect("/login")

    # Get claims for this listing
    cursor.execute("""
        SELECT c.claim_id, u.first_name, u.last_name, c.message_to_finder
        FROM claims c
        JOIN Users u ON c.claimant_id = u.user_id
        WHERE c.listing_id = %s
    """, (listing_id,))

    claims = cursor.fetchall()

    return render_template("claims.html", claims=claims)
@app.route("/reports")
def reports():
    if "user_id" not in session:
        return redirect("/login")

    # 1. Listings per location
    cursor.execute("""
        SELECT location_found, COUNT(*)
        FROM listings
        GROUP BY location_found
    """)
    listings_per_location = cursor.fetchall()

    # 2. Claims per listing
    cursor.execute("""
        SELECT listing_id, COUNT(*)
        FROM claims
        GROUP BY listing_id
    """)
    claims_per_listing = cursor.fetchall()

    # 3. Listings per user
    cursor.execute("""
        SELECT u.first_name, COUNT(*)
        FROM listings l
        JOIN Users u ON l.user_id = u.user_id
        GROUP BY u.first_name
    """)
    listings_per_user = cursor.fetchall()

    return render_template(
        "reports.html",
        listings_per_location=listings_per_location,
        claims_per_listing=claims_per_listing,
        listings_per_user=listings_per_user
    )

# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)