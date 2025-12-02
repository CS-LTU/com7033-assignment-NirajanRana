Flask Expenses Project
======================

What is included:
- Flask app with MySQL user auth (register/login/profile)
- MongoDB (expenses) CRUD + API endpoints
- Templates (Bootstrap 5) and static files (JS for Chart.js)
- Dashboard page with charts

How to run (locally):
1. Create a Python venv and install requirements:
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   pip install -r requirements.txt

2. Create MySQL database and table `login_data`:
   CREATE DATABASE loginvalidation;
   USE loginvalidation;
   CREATE TABLE login_data (
     id INT AUTO_INCREMENT PRIMARY KEY,
     name VARCHAR(255),
     email VARCHAR(255) UNIQUE,
     password VARCHAR(255)
   );

3. Set environment variables if needed:
   export MYSQL_HOST=...
   export MYSQL_USER=...
   export MYSQL_PASSWORD=...
   export MYSQL_DB=loginvalidation
   export MONGO_URI="your_mongo_uri"
   export FLASK_SECRET="a secret"

4. Run:
   python app.py

Files:
- app.py
- templates/
- static/css/style.css
- static/js/main.js