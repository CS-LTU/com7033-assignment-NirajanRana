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

# MySQL Connection
conn = mysql.connector.connect(**MYSQL_CONFIG)

# ------------------ ROUTES ---------=---------

@app.route("/")
def index():
    return redirect(url_for('login'))

# ------------------ HOME ------------------
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash("Logged out", "info")
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



# ------------------ RUN ------------------
if __name__ == '__main__':
    app.run(debug=True)