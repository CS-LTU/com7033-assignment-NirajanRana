# Stroke Patient Management System

A full-stack Flask application for managing user registrations, logins, and **Patient Data** storage. This system uses a **dual database architecture**: **MySQL** for user authentication and **MongoDB** for patient records.

---

## 🚀 Features

* **User Registration & Login (MySQL):** Secure user authentication using email and hashed passwords.
* **Profile Management:** Users can update their name and change their password.
* **Patient Data Management (MongoDB):** Users can Add, View , Update, and Delete patient records.
* **Dual Database System:** Uses MySQL for user credentials and MongoDB for flexible patient data storage.
* **REST API:** Endpoints for fetching and managing patient data (`/api/patient_data`).
* **Secure Password Hashing** using `werkzeug.security`.

---

## 📦 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone <repository_url> # Replace with your actual repository URL
cd <project_directory>
```

### 2️⃣ Install Required Libraries

Install all dependencies using:

```bash
pip install -r requirements.txt
```

(Key dependencies include: Flask, mysql-connector-python, pymongo, werkzeug).

### 3️⃣ Configuration

The application uses environment variables for database connection details.

| Variable Name  | Default Value (in app.py) | Description                    |
| -------------- | ------------------------- | ------------------------------ |
| FLASK_SECRET   | os.urandom(24)            | Secret key for Flask sessions. |
| MYSQL_HOST     | localhost                 | MySQL server host.             |
| MYSQL_USER     | root                      | MySQL user.                    |
| MYSQL_PASSWORD | root                      | MySQL password.                |
| MYSQL_DB       | loginvalidation           | MySQL database name.           |
| MONGO_URI      | mongodb+srv://...         | MongoDB connection string.     |

### 🗄️ Database Setup

#### 🟦 MySQL (User Authentication)

Create the database (e.g., `loginvalidation`):

```sql
CREATE DATABASE loginvalidation;
USE loginvalidation;
```

Create the `login_data` table for user credentials:

```sql
CREATE TABLE login_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255)
);
```

#### 🍃 MongoDB (Patient Records)

The application connects to the database `patient_data` and stores records in the collection `Patient_data`.
The patient data document structure includes attributes like: `id`, `gender`, `age`, `hypertension`, `heart_disease`, and is linked to the user via `user_id`.

### ▶️ Running the Application

Ensure your MySQL and MongoDB servers are running and configured before starting the application.

```bash
python app.py
```

The application will be accessible at:

```
http://127.0.0.1:5000/
```

## 🖼 System Design Architecture

Below is a high-level **System Architecture Diagram** representing the dual-database workflow:

```
                 ┌───────────────────────┐
                 │        Client         │
                 │  (Browser / UI)       │
                 └──────────┬────────────┘
                            │ HTTP Requests
                            ▼
                 ┌────────────────────────┐
                 │        Flask App       │
                 │  (Routing + Logic)     │
                 └──────────┬────────────┘
        ┌────────────────────┼─────────────────────┐
        │                    │                     │
        ▼                    ▼                     ▼
┌──────────────┐     ┌────────────────┐     ┌────────────────┐
│ Flask Session │     │   MySQL DB     │     │   MongoDB       │
│  (user_id)    │     │(login_data tbl)│     │(Patient_data col)│
└──────────────┘     └────────────────┘     └────────────────┘
        │                    │                     │
        │ Stores login       │ Stores hashed       │ CRUD Patient
        │ session state      │ user credentials    │ Data per user
        ▼                    ▼                     ▼
        └────────────────────┴─────────────────────┘
```

### Data Flow Summary

The application uses a Dual Database Architecture, separating user authentication from patient data storage for security and flexibility.

**Data Flow Summary**

* **Authentication:** User login/registration interacts with the MySQL database to verify/store hashed credentials.
* **Session Management:** Upon successful login, the `user_id` is stored in the secure Flask session.
* **Data Persistence:** CRUD operations on patient records (Add, Update, Delete) are executed by Flask endpoints, which communicate with the MongoDB collection. Records are typically associated with the current user's `user_id`.

## 📁 Project Structure

```
patient_management_project/
│── app.py                # Main Flask application file (Routes, DB connections, Logic)
│── requirements.txt      # Project dependencies
│── README.md             # This file
│── templates/
│   ├── base.html         # Base template with navigation and layout
│   ├── login.html        # User login form
│   ├── register.html     # User registration form
│   ├── home.html         # Application homepage
│   ├── profile.html      # User profile update form
│   ├── patient_data.html # Page to view/list patient data
│   └── add_patient_data.html # Form to add new patient record
│── static/
│   ├── css/
│   └── js/
│       └── main.js       # Client-side JavaScript for fetching/displaying data
```

---

## 👨‍💻 Author

Nirajan Rana
