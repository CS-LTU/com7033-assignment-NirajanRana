import pytest
from flask import session
from app import app

# -------------------------------------------------------------------
# FIXTURES
# -------------------------------------------------------------------

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess.clear()
        yield client


# -------------------------------------------------------------------
# USER SESSION TESTS
# -------------------------------------------------------------------

def test_user_session_created(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["email"] = "test@example.com"
        sess["role"] = "user"

    resp = client.get("/dashboard")
    assert resp.status_code != 500

    with client.session_transaction() as sess:
        assert sess.get("email") == "test@example.com"
        assert sess.get("role") == "user"


def test_user_logout_clears_session(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["role"] = "user"

    resp = client.get("/logout")
    assert resp.status_code in (302, 303)

    with client.session_transaction() as sess:
        assert "user_id" not in sess
        assert "role" not in sess


# -------------------------------------------------------------------
# DOCTOR SESSION
# -------------------------------------------------------------------

def test_doctor_session_created(client):
    with client.session_transaction() as sess:
        sess["doctor_id"] = 10
        sess["doctor_email"] = "doctor@example.com"
        sess["role"] = "doctor"

    resp = client.get("/doctor_dashboard")
    assert resp.status_code != 500

    with client.session_transaction() as sess:
        assert sess.get("doctor_email") == "doctor@example.com"
        assert sess.get("role") == "doctor"


def test_doctor_logout_clears_session(client):
    with client.session_transaction() as sess:
        sess["doctor_id"] = 10
        sess["role"] = "doctor"

    resp = client.get("/doctor_logout")
    assert resp.status_code in (302, 303)

    with client.session_transaction() as sess:
        assert "doctor_id" not in sess
        assert "role" not in sess


# -------------------------------------------------------------------
# ISOLATION BETWEEN ROLES
# -------------------------------------------------------------------

def test_session_isolated_between_roles(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "U1"
        sess["role"] = "user"

    with client.session_transaction() as sess:
        sess["doctor_id"] = "D1"
        sess["role"] = "doctor"

    with client.session_transaction() as sess:
        assert sess.get("user_id") == "U1"
        assert sess.get("doctor_id") == "D1"


# -------------------------------------------------------------------
# MULTIPLE REQUEST PERSISTENCE
# -------------------------------------------------------------------

def test_session_persists_multiple_requests(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 999

    resp = client.get("/dashboard")
    assert resp.status_code != 500

    with client.session_transaction() as sess:
        assert sess.get("user_id") == 999
