# Essential libraries for the project

from flask import Flask, render_template, request, redirect, session, jsonify, flash, url_for
import mysql.connector
from pymongo import MongoClient
import os
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", os.urandom(24))

# ---------------- CONFIG ----------------

# Database configuration
MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", "root"),
    "database": os.environ.get("MYSQL_DB", "loginvalidation"),
}

# Unique key for the doctor to identify or register the doctor only
DOCTOR_KEY = "2513161"

MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://root:root@cluster0.ynbmbkb.mongodb.net/?appName=Cluster0"
)

# ---------------- MYSQL INIT ----------------
def initialize_mysql():
    tmp = mysql.connector.connect(
        host=MYSQL_CONFIG["host"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"]
    )
    tcur = tmp.cursor()
    tcur.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
    tmp.commit()
    tcur.close()
    tmp.close()

    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cur = conn.cursor()

    # Patient users
    # patient table to store patient data
    cur.execute("""
        CREATE TABLE IF NOT EXISTS login_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)

    # Doctors table for the storage of the doctor data
    cur.execute("""
        CREATE TABLE IF NOT EXISTS doctor_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            doctor_key VARCHAR(100) NOT NULL
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

initialize_mysql()
conn = mysql.connector.connect(**MYSQL_CONFIG)

# ---------------- MONGO ----------------
# Mongodb Database connection
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["patient_data"]
collection = mongo_db["Patient_data"]

# ---------------- ROOT ----------------
@app.route("/")
def index():
    if session.get("doctor_id"):
        return redirect(url_for("doctor_home"))
    if session.get("user_id"):
        return redirect(url_for("home"))
    return redirect(url_for("login"))

# ---------------- PATIENT AUTH ----------------

# Patient Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if not (name and email and password):
            flash("Please fill all fields.", "warning")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        with conn.cursor(buffered=True) as cur:
            cur.execute("SELECT id FROM login_data WHERE email=%s", (email,))
            if cur.fetchone():
                flash("Email already registered.", "warning")
                return redirect(url_for("login"))

            hashed = generate_password_hash(password)
            cur.execute("""
                INSERT INTO login_data (name, email, password)
                VALUES (%s, %s, %s)
            """, (name, email, hashed))
            conn.commit()

        flash("Registered successfully. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

#patient Login

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").lower()
        password = request.form.get("password")

        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email, password FROM login_data WHERE email=%s", (email,))
            user = cur.fetchone()

        if user and check_password_hash(user[3], password):
            session.clear()
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            flash("Logged in successfully.", "success")
            return redirect(url_for("home"))

        flash("Invalid credentials.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

# ---------------- DOCTOR AUTH ----------------

# Doctor Registration with the hashing of password and session logout with already registered message if exist
@app.route("/doctor_register", methods=["GET", "POST"])
def doctor_register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email").lower()
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")
        key = request.form.get("key")

        if key != DOCTOR_KEY:
            flash("Invalid doctor key.", "danger")
            return redirect(url_for("doctor_register"))

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("doctor_register"))

        with conn.cursor(buffered=True) as cur:
            cur.execute("SELECT id FROM doctor_data WHERE email=%s", (email,))
            if cur.fetchone():
                flash("Doctor already registered.", "warning")
                return redirect(url_for("doctor_login"))

            hashed = generate_password_hash(password)
            cur.execute("""
                INSERT INTO doctor_data (name, email, password, doctor_key)
                VALUES (%s, %s, %s, %s)
            """, (name, email, hashed, DOCTOR_KEY))
            conn.commit()

        flash("Doctor registered successfully. Please login.", "success")
        return redirect(url_for("doctor_login"))

    return render_template("doctor_register.html")

# Doctor Login validation
@app.route("/doctor_login", methods=["GET", "POST"])
def doctor_login():
    if request.method == "POST":
        email = request.form.get("email").lower()
        password = request.form.get("password")

        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, email, password 
                FROM doctor_data WHERE email=%s
            """, (email,))
            doc = cur.fetchone()

        if doc and check_password_hash(doc[3], password):
            session.clear()
            session["doctor_id"] = doc[0]
            session["doctor_name"] = doc[1]
            flash("Doctor logged in.", "success")
            return redirect(url_for("doctor_home"))

        flash("Invalid doctor credentials.", "danger")

    return render_template("doctor_login.html")

#Doctor Logout
@app.route("/doctor_logout")
def doctor_logout():
    session.clear()
    flash("Doctor logged out.", "info")
    return redirect(url_for("doctor_login"))

# ---------------- DASHBOARDS ----------------
@app.route("/home")
def home():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return render_template("home.html")

# route for the doctor home
@app.route("/doctor_home")
def doctor_home():
    if not session.get("doctor_id"):
        return redirect(url_for("doctor_login"))
    return render_template("doctor_home.html")

# ---------------- PATIENT PROFILE SYSTEM ----------------

# View Profile
@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    with conn.cursor() as cur:
        cur.execute("SELECT id, name, email FROM login_data WHERE id=%s", (session["user_id"],))
        user = cur.fetchone()

    return render_template("profile.html", myuser=user)

# Update Patient Password
@app.route("/update_password", methods=["GET", "POST"])
def update_password():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    if request.method == "POST":
        old = request.form.get("old_password")
        new = request.form.get("new_password")
        confirm = request.form.get("confirm_password")

        with conn.cursor() as cur:
            cur.execute("SELECT password FROM login_data WHERE id=%s", (session["user_id"],))
            hashed = cur.fetchone()[0]

        if not check_password_hash(hashed, old):
            flash("Old password incorrect.", "danger")
            return redirect(url_for("update_password"))

        if new != confirm:
            flash("New passwords do not match.", "danger")
            return redirect(url_for("update_password"))

        new_hash = generate_password_hash(new)
        with conn.cursor() as cur:
            cur.execute("UPDATE login_data SET password=%s WHERE id=%s", (new_hash, session["user_id"]))
            conn.commit()

        flash("Password updated.", "success")
        return redirect(url_for("login"))

    return render_template("update_password.html")

# Delete Patient Account
@app.route("/delete_user/<int:id>")
def delete_user(id):
    if not session.get("user_id"):
        return redirect(url_for("login"))

    if session["user_id"] != id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("home"))

    # Delete patient records
    collection.delete_many({"user_id": id})

    # Delete SQL account
    with conn.cursor() as cur:
        cur.execute("DELETE FROM login_data WHERE id=%s", (id,))
        conn.commit()

    session.clear()
    flash("Your account has been deleted.", "info")
    return redirect(url_for("login"))

# ---------------- PATIENT DATA ----------------

@app.route("/patient_data")
def patient_data():
    if not (session.get("user_id") or session.get("doctor_id")):
        return redirect(url_for("login"))
    return render_template("patient_data.html")


#  JSON API
@app.route("/api/patient_data")
def api_patient_data_json():
    if not (session.get("user_id") or session.get("doctor_id")):
        return jsonify([]), 401

    mine = request.args.get("mine")

    records = []

    if session.get("doctor_id") and not mine:
        for r in collection.find({}):
            r["_id"] = str(r["_id"])
            records.append(r)
    else:
        uid = session.get("user_id")
        for r in collection.find({"user_id": uid}):
            r["_id"] = str(r["_id"])
            records.append(r)

    return jsonify(records)

# Add Patient Data
@app.route("/add_patient_data", methods=["GET", "POST"])
def add_patient_data():
    if not (session.get("user_id") or session.get("doctor_id")):
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            doc = {
                "user_id": session.get("user_id"),
                "id": int(request.form.get("id")) if request.form.get("id") else None,
                "gender": request.form.get("gender"),
                "age": int(request.form.get("age")),
                "hypertension": int(request.form.get("hypertension")),
                "heart_disease": int(request.form.get("heart_disease")),
                "ever_married": request.form.get("ever_married"),
                "work_type": request.form.get("work_type"),
                "Residence_type": request.form.get("Residence_type"),
                "avg_glucose_level": float(request.form.get("avg_glucose_level")),
                "bmi": float(request.form.get("bmi")),
                "smoking_status": request.form.get("smoking_status"),
                "stroke": int(request.form.get("stroke"))
            }
        except:
            flash("Enter valid numeric values.", "danger")
            return redirect(url_for("add_patient_data"))

        collection.insert_one(doc)
        flash("Record added.", "success")
        return redirect(url_for("patient_data"))

    return render_template("add_patient_data.html")

# Update Patient Data
@app.route("/update_patient_data/<id>", methods=["GET", "POST"])
def update_patient_data(id):
    if not (session.get("user_id") or session.get("doctor_id")):
        return redirect(url_for("login"))

    try:
        obj_id = ObjectId(id)
    except:
        flash("Invalid record ID.", "danger")
        return redirect(url_for("patient_data_page"))

    record = collection.find_one({"_id": obj_id})
    if not record:
        flash("Record not found.", "danger")
        return redirect(url_for("patient_data_page"))

    if session.get("user_id") and record["user_id"] != session["user_id"]:
        flash("Not authorized.", "danger")
        return redirect(url_for("patient_data_page"))

    if request.method == "POST":
        try:
            update = {
                "id": int(request.form.get("id")) if request.form.get("id") else None,
                "gender": request.form.get("gender"),
                "age": int(request.form.get("age")),
                "hypertension": int(request.form.get("hypertension")),
                "heart_disease": int(request.form.get("heart_disease")),
                "ever_married": request.form.get("ever_married"),
                "work_type": request.form.get("work_type"),
                "Residence_type": request.form.get("Residence_type"),
                "avg_glucose_level": float(request.form.get("avg_glucose_level")),
                "bmi": float(request.form.get("bmi")),
                "smoking_status": request.form.get("smoking_status"),
                "stroke": int(request.form.get("stroke"))
            }
        except:
            flash("Invalid input.", "danger")
            return redirect(url_for("update_patient_data", id=id))

        collection.update_one({"_id": obj_id}, {"$set": update})
        flash("Record updated.", "success")
        return redirect(url_for("patient_data"))

    record["_id"] = str(record["_id"])
    return render_template("update_patient_data.html", patient=record)

# Delete Patient data
@app.route("/api/patient_data/<id>", methods=["DELETE"])
def api_delete_patient(id):
    if not (session.get("user_id") or session.get("doctor_id")):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        obj_id = ObjectId(id)
    except:
        return jsonify({"error": "Invalid ID"}), 400

    record = collection.find_one({"_id": obj_id})
    if not record:
        return jsonify({"error": "Not found"}), 404

    if session.get("user_id") and record["user_id"] != session["user_id"]:
        return jsonify({"error": "Forbidden"}), 403

    collection.delete_one({"_id": obj_id})
    return jsonify({"success": True}), 200


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True)
