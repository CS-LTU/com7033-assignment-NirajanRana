
# Stroke Patient Management System  
A full-stack Flask-based web application for managing stroke patient data with session-based authentication for Patients and Doctors.

---

## 📌 System Architecture Diagram

```
                       +-----------------------+
                       |       User/Doctor     |
                       +-----------+-----------+
                                   |
                                   v
                         +-------------------+
                         |     Flask App     |
                         |  (app.py logic)   |
                         +----+----------+---+
                              |          |
                     +--------+          +---------+
                     v                          v
         +-----------------------+     +------------------------+
         |   MySQL Database     |     |     MongoDB Atlas      |
         | (Users, Doctors)     |     | (Patient Medical Data) |
         +-----------------------+     +------------------------+
```

---

## 🚀 Features

### 👤 **User (Patient)**
- Register / Login / Logout  
- Update password  
- Add, update, and delete personal patient records  
- View personal dashboard  

### 👨‍⚕️ **Doctor**
- Register with secure doctor key  
- Login / Logout  
- View all patient records  
- Add or update patient data  
- Delete accounts  

### 🔐 **Security**
- Password hashing using `werkzeug.security`  
- Session-based authentication  
- Role-based access (user vs doctor)

---

## 🛠 Installation & Setup Guide

### **1️⃣ Install Python (if not installed)**  
Download from: https://www.python.org/downloads/

---

## **2️⃣ Clone the Project**
```bash
git clone https://github.com/CS-LTU/com7033-assignment-NirajanRana
cd stroke-patient-management
```

---

## **3️⃣ Create a Virtual Environment**
```bash
python -m venv venv
```

### Activate:

#### Windows:
```bash
venv\Scripts\activate
```

#### macOS/Linux:
```bash
source venv/bin/activate
```

---

## **4️⃣ Install Required Libraries**
Install all dependencies using:

```bash
pip install flask mysql-connector-python pymongo werkzeug dnspython
```

Full list of libraries used:
```
flask
mysql-connector-python
pymongo
werkzeug
dnspython
```

---

## **5️⃣ Configure Databases**

### **🔥 MySQL Setup**
Create a database named `loginvalidation`:
```sql
CREATE DATABASE loginvalidation;
```

Tables will be auto-created by the app:
- `login_data`
- `doctor_data`

### **🔥 MongoDB Setup**
Use MongoDB Atlas URI:
```
mongodb+srv://<user>:<password>@cluster0.mongodb.net/
```

Make sure the database exists:
```
patient_data > Patient_data (collection)
```

---

## **6️⃣ Set Environment Variables (Optional)**

Create a `.env` file:
```
FLASK_SECRET=your_secret_key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DB=loginvalidation
MONGO_URI=your_mongo_uri
```

---

## **7️⃣ Run the Application**
```bash
python app.py
```

The app runs at:  
👉 http://127.0.0.1:5000/

---

## 🧪 Testing Instructions

To run unit tests:
```bash
pytest -v
```

Test file included: `test.py`  
This project includes:
- **Session Tests**
- **Route Access Tests**
- **Role Isolation Tests**

---

## 📂 Project Folder Structure

```
/
├── app.py
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── doctor_login.html
│   ├── home.html
│   ├── doctor_home.html
│   ├── profile.html
│   └── ...
├── static/
├── test.py
└── README.md
```

---

## 👨‍💻 Author  
**Nirajan Rana**



