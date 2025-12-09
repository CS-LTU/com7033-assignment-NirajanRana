from flask import Flask, render_template, request, redirect, session, jsonify, flash, url_for
import mysql.connector
from pymongo import MongoClient
import os
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", os.urandom(24))

# --- Configuration ---
MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", "root"),
    "database": os.environ.get("MYSQL_DB", "loginvalidation"),
}

# ============================================
#      AUTO CREATE MYSQL DATABASE + TABLES
# ============================================
def initialize_mysql():
    # Connect without database to create it
    conn = mysql.connector.connect(
        host=MYSQL_CONFIG["host"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"]
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
    conn.commit()
    cursor.close()
    conn.close()

    #  Connect with database to create tables
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            password VARCHAR(255)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


# Initialize MySQL before creating global conn
initialize_mysql()

# Now create MySQL connection (DATABASE EXISTS)
conn = mysql.connector.connect(**MYSQL_CONFIG)

MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://root:root@cluster0.ynbmbkb.mongodb.net/?appName=Cluster0")

# MySQL Connection
conn = mysql.connector.connect(**MYSQL_CONFIG)

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client['patient_data']
collection = db['Patient_data']


# ------------------ ROUTES ------------------

@app.route("/")
def index():
    return redirect(url_for('login'))


# ------------------ LOGIN ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, email, password FROM login_data WHERE email=%s", (email,))
            user = cursor.fetchone()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            return redirect(url_for('home'))
        flash("Invalid credentials", "danger")
    return render_template('login.html')


# ------------------ REGISTER ------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))

        with conn.cursor(buffered=True) as cursor:
            cursor.execute("SELECT id FROM login_data WHERE email=%s", (email,))
            existing = cursor.fetchone()
            if existing:
                flash("Email already registered!", "warning")
                return redirect(url_for('login'))

            hashed = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO login_data (name, email, password) VALUES (%s,%s,%s)",
                (name, email, hashed)
            )
            conn.commit()

        flash("Registered successfully! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash("Logged out", "info")
    return redirect(url_for('login'))


# ------------------ HOME ------------------
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')


# ------------------ PROFILE ------------------
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']

    if request.method == 'POST':
        name = request.form.get('name')
        with conn.cursor() as cursor:
            cursor.execute("UPDATE login_data SET name=%s WHERE id=%s", (name, user_id))
            conn.commit()
        session['user_name'] = name
        flash("Profile updated", "success")

    with conn.cursor() as cursor:
        cursor.execute("SELECT id, name, email FROM login_data WHERE id=%s", (user_id,))
        myuser = cursor.fetchone()
    return render_template('profile.html', myuser=myuser)


# ------------------ PASSWORD UPDATE ------------------
@app.route('/update_password', methods=['GET', 'POST'])
def update_password():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']

    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')

        with conn.cursor() as cursor:
            cursor.execute("SELECT password FROM login_data WHERE id=%s", (user_id,))
            user = cursor.fetchone()
            if not user:
                flash("User not found", "danger")
                return redirect(url_for('update_password'))

            if not check_password_hash(user[0], old_password):
                flash("Old password is incorrect", "danger")
                return redirect(url_for('update_password'))

            if new_password != confirm_new_password:
                flash("New passwords do not match", "danger")
                return redirect(url_for('update_password'))

            new_hashed = generate_password_hash(new_password)
            cursor.execute("UPDATE login_data SET password=%s WHERE id=%s", (new_hashed, user_id))
            conn.commit()

        flash("Password updated successfully!", "success")
        return redirect(url_for('logout'))

    return render_template('update_password.html')


# ------------------ PATIENT DATA ------------------
@app.route('/patient_data')
def view_patient_data():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('patient_data.html')


@app.route('/add_patient_data', methods=['GET', 'POST'])
def add_patient_data():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            doc = {
                "user_id": session['user_id'],
                "id": int(request.form.get('id')),
                "gender": request.form.get('gender'),
                "age": int(request.form.get('age')),
                "hypertension": int(request.form.get('hypertension')),
                "heart_disease": int(request.form.get('heart_disease')),
                "ever_married": request.form.get('ever_married'),
                "work_type": request.form.get('work_type'),
                "Residence_type": request.form.get('Residence_type'),
                "avg_glucose_level": float(request.form.get('avg_glucose_level')),
                "bmi": float(request.form.get('bmi')),
                "smoking_status": request.form.get('smoking_status'),
                "stroke": int(request.form.get('stroke'))
            }
        except ValueError:
            flash("Please enter valid numeric values", "danger")
            return redirect(url_for('add_patient_data'))

        collection.insert_one(doc)
        flash("Record added successfully", "success")
        return redirect(url_for('view_patient_data'))

    return render_template('add_patient_data.html')


# ------------------ UPDATE PATIENT DATA ------------------
@app.route('/update_patient_data/<id>', methods=['GET', 'POST'])
def update_patient_data(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    patient = collection.find_one({"_id": ObjectId(id)})
    if not patient:
        flash("Record not found", "danger")
        return redirect(url_for('view_patient_data'))

    if request.method == 'POST':
        try:
            updated_data = {
                "id": int(request.form.get("id")),
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
        except ValueError:
            flash("Please enter valid numeric values", "danger")
            return redirect(url_for('update_patient_data', id=id))

        collection.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
        flash("Record updated successfully!", "success")
        return redirect(url_for('view_patient_data'))

    return render_template("update_patient_data.html", patient=patient)

# delete patient_data
@app.route('/api/patient_data/<id>', methods=['DELETE'])
def api_delete_patient(id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        obj_id = ObjectId(id)
    except:
        return jsonify({"error": "Invalid ID format"}), 400

    # Ensure user only deletes their own records
    record = collection.find_one({"_id": obj_id})

    if not record:
        return jsonify({"error": "Record not found"}), 404

    if record.get("user_id") != session['user_id']:
        return jsonify({"error": "Not allowed"}), 403

    collection.delete_one({"_id": obj_id})

    return jsonify({"success": True}), 200


# ------------------ DELETE USER ------------------
@app.route('/delete_user/<int:id>', methods=['GET'])
def delete_user(id):
    if 'user_id' not in session:
        flash("You must be logged in.", "danger")
        return redirect(url_for('login'))

    with conn.cursor(buffered=True) as cursor:
        cursor.execute("SELECT id FROM login_data WHERE id=%s", (id,))
        user = cursor.fetchone()
        if not user:
            flash("User not found!", "danger")
            return redirect(url_for('login'))

        cursor.execute("DELETE FROM login_data WHERE id=%s", (id,))
        conn.commit()

    flash("User deleted successfully", "success")
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('login'))


# ------------------ API ENDPOINTS ------------------
@app.route('/api/patient_data', methods=['GET'])
def api_get_patient_data():
    mine = request.args.get('mine')
    query = {}
    if mine == '1' and 'user_id' in session:
        query['user_id'] = session['user_id']

    data = []
    for doc in collection.find(query):
        doc['_id'] = str(doc['_id'])
        data.append(doc)

    return jsonify(data)


@app.route('/api/patient_data', methods=['POST'])
def api_create_patient_data():
    payload = request.get_json()
    payload['user_id'] = session.get('user_id')
    res = collection.insert_one(payload)
    return jsonify({"id": str(res.inserted_id)}), 201


@app.route('/get_users', methods=['POST'])
def get_user():
    username = request.form.get("username")
    user = collection.find_one({"name": username})
    if user:
        user["_id"] = str(user["_id"])
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

# For the doctor

# Doctor Login
@app.route('/doctor_login',methods=['GET','POST'])
def doctor_login():
    return render_template("doctor_login.html")

# Doctor Register
@app.route('/doctor_register',methods=['GET','POST'])
def doctor_register():
    return render_template("doctor_register.html")


# ------------------ RUN ------------------
if __name__ == '__main__':
    app.run(debug=True)
