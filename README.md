# com7033-assignment-NirajanRana
com7033-assignment-NirajanRana created by GitHub Classroom
# Flask Expenses Manager

A complete **Flask Full-Stack Application** integrating **MySQL (User Management)** and **MongoDB (Expenses CRUD)** with Bootstrap UI, Chart.js dashboards, and REST APIs.

---

# 🏗️ System Design

## 🔶 Architecture Overview

```
          ┌────────────────────┐
          │      Browser       │
          │  (User Interface)  │
          └─────────┬──────────┘
                    │
                    ▼
        ┌──────────────────────────┐
        │        Flask App         │
        │  Routing + Controllers   │
        └──────┬──────────┬───────┘
               │          │
   ┌───────────┘          └────────────┐
   ▼                                   ▼
┌────────────┐                 ┌─────────────────┐
│   MySQL     │                 │    MongoDB      │
│ login_data  │                 │  expenses CRUD  │
└────────────┘                 └─────────────────┘
```

---

## 🔶 Component Breakdown

### **1️⃣ Frontend (Presentation Layer)**
- HTML templates (Jinja2)
- Bootstrap 5 UI
- JavaScript Fetch API (AJAX)
- Chart.js dashboard for expense analytics

### **2️⃣ Backend (Application Layer)**
- Flask routing
- User authentication (session-based)
- Password hashing (Werkzeug)
- CRUD handlers for:
  - Users (MySQL)
  - Expenses (MongoDB)

### **3️⃣ Databases (Storage Layer)**

#### **MySQL – User Management**
Stores:
- ID  
- Name  
- Email  
- Password Hash  

Used for:
- Register  
- Login  
- Profile  
- Password update  
- User CRUD  

#### **MongoDB – Expenses Data**
Stores:
- _id  
- user_id  
- name  
- email  
- product  
- expense amount  

Used for:
- Add/Edit/Delete expenses  
- Fetch expenses via REST API  

---

# 🧱 Data Flow Diagram (DFD)

```
User → UI Form → Flask Route → MySQL/MongoDB → Response → Browser
```

### Example: Register Flow

```
User → /register → Flask → Validate → Hash Password → MySQL → Success → Redirect
```

### Example: Add Expense Flow

```
User → /addexpenses → Flask → Validate → MongoDB Insert → Redirect → View Expenses
```

---

# 🧰 Technologies Used

| Layer | Technology |
|------|------------|
| Backend | Flask, Python |
| User Auth | MySQL + Werkzeug hashing |
| Expenses DB | MongoDB + PyMongo |
| Frontend | HTML, Bootstrap, JS |
| Charts | Chart.js |
| API | Flask JSON API |

---

# 🚀 Features

### 🔐 **User Authentication (MySQL)**
- Register with hashed password  
- Prevent duplicate email  
- Login / Logout  
- Update profile  
- Update password  
- Full user CRUD  

### 💰 **Expense Management (MongoDB)**
- Add expenses  
- Edit expenses  
- Delete expenses  
- Fetch all or personal expenses  
- API support  

### 📊 **Dashboard**
- Chart.js visualizations  
- AJAX-driven dynamic content  

---

# 📦 Project Structure

```
app.py
templates/
    login.html
    register.html
    profile.html
    home.html
    addexpenses.html
    expenses.html
    update_expense.html
    update_password.html

static/
    css/style.css
    js/main.js

requirements.txt
README.md
```

---

# 🛠️ Setup Instructions

### 1️⃣ Create Virtual Environment
```
python -m venv venv
source venv/bin/activate   # Windows → venv\Scripts\activate
```

### 2️⃣ Install Dependencies
```
pip install -r requirements.txt
```

### 3️⃣ Setup MySQL
```
CREATE DATABASE loginvalidation;

CREATE TABLE login_data (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  password VARCHAR(255)
);
```

### 4️⃣ Run App
```
python app.py
```

---

# 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/expenses` | Fetch all expenses |
| GET | `/api/expenses?mine=1` | Fetch logged-in user expenses |
| POST | `/api/expense` | Add expense |
| PUT | `/api/expense/<id>` | Update expense |
| DELETE | `/api/expense/<id>` | Delete expense |

---

# 👤 Author
**Nirajan Rana**  
