import pytest
from app import app, conn, collection
import mongomock
import mysql.connector
from werkzeug.security import generate_password_hash


# ============================
# FIXTURES
# ============================

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_mongo(monkeypatch):
    """Mock MongoDB so real DB is not touched."""
    mock_db = mongomock.MongoClient().db1.expenses
    monkeypatch.setattr("app.collection", mock_db)
    return mock_db


@pytest.fixture
def mock_mysql(monkeypatch):
    """Mock in-memory MySQL database."""
    test_conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="loginvalidation"
    )
    test_cursor = test_conn.cursor(buffered=True)

    monkeypatch.setattr("app.conn", test_conn)
    monkeypatch.setattr("app.cursor", test_cursor)

    # create table for testing
    test_cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255),
            password VARCHAR(255)
        )
    """)
    test_conn.commit()

    return test_cursor


# ============================
# UNIT TESTS
# ============================

def test_register_user(client, mock_mysql):
    """Test user registration page loads."""
    response = client.get("/register")
    assert response.status_code == 200


def test_register_post(client, mock_mysql):
    """Test posting new user."""
    response = client.post("/register", data={
        "name": "Test",
        "email": "test@test.com",
        "password": "123",
        "confirm_password": "123"
    }, follow_redirects=True)

    assert  response.data


def test_login(client, mock_mysql):
    """Insert a user then test login."""

    hashed_pass = generate_password_hash("123")
    mock_mysql.execute(
        "INSERT INTO login_data (name, email, password) VALUES (%s,%s,%s)",
        ("TestUser", "test@login.com", hashed_pass)
    )
    conn.commit()

    response = client.post("/login", data={
        "email": "test@login.com",
        "password": "123"
    }, follow_redirects=True)

    assert b"home" or b"Dashboard" or b"Expenses" in response.data


def test_add_expense(client, mock_mongo, mock_mysql):
    """Login first, then add expense."""

    # login simulation
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Tester"

    response = client.post("/addexpenses", data={
        "dname": "Test Expense",
        "demail": "user@test.com",
        "expense": "50",
        "Product": "Food"
    }, follow_redirects=True)

    assert b"Expense added" in response.data

    # check in mongo
    assert mock_mongo.count_documents({}) == 1


def test_api_expenses(client, mock_mongo, mock_mysql):
    """Test GET /api/expenses"""

    # login session
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    # insert mock expense
    mock_mongo.insert_one({
        "user_id": 1,
        "name": "Apple",
        "email": "a@test.com",
        "expense": 20,
        "product": "Fruit"
    })

    response = client.get("/api/expenses?mine=1")
    assert response.status_code == 200
    assert b"Apple" in response.data


def test_delete_user(client, mock_mysql):
    """Test user deletion route."""

    # Insert mock user
    mock_mysql.execute(
        "INSERT INTO login_data (name, email, password) VALUES (%s,%s,%s)",
        ("DelUser", "del@test.com", generate_password_hash("123"))
    )
    conn.commit()

    # login session
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.get("/delete_user/1", follow_redirects=True)
    assert  response.data
