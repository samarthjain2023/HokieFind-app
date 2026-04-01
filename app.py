from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # or "password" if needed
    database="lost_and_found"
)

cursor = db.cursor()

# VIEW LISTINGS
@app.route("/")
def index():
    cursor.execute("SELECT * FROM listings")
    listings = cursor.fetchall()
    return render_template("index.html", listings=listings)

# ADD LISTING
@app.route("/add", methods=["POST"])
def add():
    location = request.form["location"]
    image = request.form["image"]

    cursor.execute(
        "INSERT INTO listings (location_found, image_url) VALUES (%s, %s)",
        (location, image)
    )
    db.commit()

    return redirect("/")

# DELETE LISTING
@app.route("/delete/<int:id>")
def delete(id):
    cursor.execute("DELETE FROM listings WHERE listing_id = %s", (id,))
    db.commit()
    return redirect("/")

# SHOW EDIT FORM
@app.route("/edit/<int:id>")
def edit(id):
    cursor.execute("SELECT * FROM listings WHERE listing_id = %s", (id,))
    listing = cursor.fetchone()
    return render_template("edit.html", listing=listing)

# UPDATE LISTING
@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    location = request.form["location"]
    image = request.form["image"]

    cursor.execute(
        "UPDATE listings SET location_found = %s, image_url = %s WHERE listing_id = %s",
        (location, image, id)
    )
    db.commit()

    return redirect("/")

app.run(debug=True)

