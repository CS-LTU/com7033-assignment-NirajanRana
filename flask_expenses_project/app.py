from flask import Flask, render_template, request, redirect, session, jsonify, Response, flash, url_for
import mysql.connector
from pymongo import MongoClient
import os, json
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", os.urandom(24))

# --- Configuration (edit as needed) ---
MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", "root"),
    "database": os.environ.get("MYSQL_DB", "loginvalidation"),
}
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://root:root@cluster0.ynbmbkb.mongodb.net/?appName=Cluster0")
# --------------------------------------

# MySQL Connection
conn = mysql.connector.connect(**MYSQL_CONFIG)
cursor = conn.cursor()

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client['db1']
collection = db['expenses']

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        cursor.execute("SELECT id, name, email, password FROM login_data WHERE email=%s", (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            return redirect(url_for('home'))
        flash("Invalid credentials", "danger")
    return render_template('login.html')

# Registration and checking of the user whether they are already exist or not
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        #  Check password match
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))

        cursor = conn.cursor(buffered=True)

        #  Check if email already exists
        cursor.execute("SELECT id FROM login_data WHERE email=%s", (email,))
        existing = cursor.fetchone()

        if existing:
            flash("Email already registered!", "warning")
            return redirect(url_for('register'))

        #  Hash password
        hashed = generate_password_hash(password)

        #  Insert user
        cursor.execute(
            "INSERT INTO login_data (name, email, password) VALUES (%s,%s,%s)",
            (name, email, hashed)
        )
        conn.commit()

        flash("Registered successfully! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash("Logged out", "info")
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

# Profile (MySQL)
@app.route('/profile', methods=['GET','POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    if request.method == 'POST':
        name = request.form.get('name')
        cursor.execute("UPDATE login_data SET name=%s WHERE id=%s", (name, user_id))
        conn.commit()
        session['user_name'] = name
        flash("Profile updated", "success")
    cursor.execute("SELECT id, name, email FROM login_data WHERE id=%s", (user_id,))
    myuser = cursor.fetchone()
    return render_template('profile.html', myuser=myuser)

# MongoDB CRUD for expenses
@app.route('/addexpenses', methods=['GET','POST'])
def addexpenses():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        doc = {
            "user_id": session['user_id'],
            "name": request.form.get('dname'),
            "email": request.form.get('demail'),
            "expense": float(request.form.get('expense') or 0),
            "product": request.form.get('Product')
        }
        res = collection.insert_one(doc)
        flash("Expense added", "success")
        return redirect(url_for('view_expenses'))
    return render_template('addexpenses.html')

@app.route('/expenses')
def view_expenses():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('expenses.html')

@app.route('/api/expenses', methods=['GET'])
def api_get_expenses():
    # support query param ?mine=1 to fetch only logged-in user's expenses
    mine = request.args.get('mine')
    query = {}
    if mine and 'user_id' in session:
        query['user_id'] = session['user_id']
    data = []
    for doc in collection.find(query):
        doc['_id'] = str(doc['_id'])
        data.append(doc)
    return jsonify(data)

@app.route('/api/expense', methods=['POST'])
def api_create_expense():
    payload = request.get_json()
    payload['user_id'] = session.get('user_id')
    res = collection.insert_one(payload)
    return jsonify({"id": str(res.inserted_id)}), 201

@app.route('/api/expense/<id>', methods=['PUT','DELETE'])
def api_modify_expense(id):
    if request.method == 'PUT':
        payload = request.get_json()
        # sanitize allowed fields
        allowed = {k: payload[k] for k in ('name','email','expense','product') if k in payload}
        collection.update_one({"_id": ObjectId(id)}, {"$set": allowed})
        return jsonify({"status":"updated"})
    else:
        collection.delete_one({"_id": ObjectId(id)})
        return jsonify({"status":"deleted"})

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Simple search endpoint
@app.route('/get_users', methods=['POST'])
def get_user():
    username = request.form.get("username")
    user = collection.find_one({"name": username})
    if user:
        user["_id"] = str(user["_id"])
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404



# Update of the password
@app.route('/update_password', methods=['GET', 'POST'])
def update_password():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']

        cursor = conn.cursor()

        # Fetch current hashed password
        cursor.execute("SELECT password FROM login_data WHERE id=%s", (user_id,))
        user = cursor.fetchone()

        if not user:
            return "User not found"

        stored_hash = user[0]

        # Check old password match
        if not check_password_hash(stored_hash, old_password):
            return "Old password is incorrect"

        # Check both new passwords match
        if new_password != confirm_new_password:
            return "New passwords do not match"

        # Hash new password
        new_hashed = generate_password_hash(new_password)

        # Update password
        cursor.execute(
            "UPDATE login_data SET password=%s WHERE id=%s",
            (new_hashed, user_id)
        )
        conn.commit()

        flash( "Password updated successfully!","info")
        return redirect('/logout')



    return render_template('update_password.html')

# Update expenses

@app.route('/update_expense/<id>', methods=['GET', 'POST'])
def update_expense(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch expense by id
    expense = collection.find_one({"_id": ObjectId(id)})

    if not expense:
        flash("Expense not found", "danger")
        return redirect(url_for('view_expenses'))

    # POST = Update data
    if request.method == 'POST':
        updated_data = {
            "name": request.form.get("dname"),
            "email": request.form.get("demail"),
            "expense": float(request.form.get("expense") or 0),
            "product": request.form.get("product")
        }

        collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": updated_data}
        )

        flash("Expense updated successfully!", "success")
        return redirect(url_for('view_expenses'))

    # GET = Load form
    return render_template("update_expense.html", expense=expense)





if __name__ == '__main__':
    app.run(debug=True)