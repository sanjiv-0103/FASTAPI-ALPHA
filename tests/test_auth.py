
# 1. Import Libraries
import uuid
import pytest
from app import models, utils

# 2. Generate Unique Test Email
def make_email():
    return f"auth_{uuid.uuid4().hex[:12]}@example.com"

# 3. Register a Test User
def register_user(client, email, password="TestPass123!"):
    return client.post(
        "/users",
        json={"email": email, "password": password}
    )

# 4. Test Successful Registration
def test_register_user(client):
    email = make_email()
    response = register_user(client, email)

    assert response.status_code == 201
    assert response.json()["email"] == email
    assert "password" not in response.json()

# 5. Test Duplicate Email Registration
def test_duplicate_email(client):
    email = make_email()
    first = register_user(client, email)
    second = register_user(client, email)

    assert first.status_code == 201
    assert second.status_code == 409

# 6. Test Password Is Hashed
def test_password_hashing(client, db_session):
    email = make_email()
    password = "TestPass123!"
    response = register_user(client, email, password)

    assert response.status_code == 201

    user = db_session.query(models.User).filter(
        models.User.email == email
    ).first()

    assert user is not None
    assert user.password != password
    assert utils.verify(password, user.password)

# 7. Test Successful Login
def test_valid_login(client):
    email = make_email()
    password = "TestPass123!"
    assert register_user(client, email, password).status_code == 201

    response = client.post(
        "/login",
        data={"username": email, "password": password}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

# 8. Test Incorrect Password
def test_invalid_password(client):
    email = make_email()
    assert register_user(client, email).status_code == 201

    response = client.post(
        "/login",
        data={"username": email, "password": "WrongPassword"}
    )

    assert response.status_code == 401

# 9. Test Unknown Email
def test_unknown_user(client):
    response = client.post(
        "/login",
        data={
            "username": make_email(),
            "password": "TestPass123!"
        }
    )

    assert response.status_code == 401

# 10. Test Missing JWT
def test_missing_token(client):
    response = client.post(
        "/posts",
        json={
            "title": "Protected Post",
            "content": "Testing missing JWT",
            "published": True
        }
    )

    assert response.status_code == 401

# 11. Test Invalid JWT
@pytest.mark.parametrize(
    "token",
    ["invalid.token.value", "not-a-jwt", "abc"]
)
def test_invalid_token(client, token):
    response = client.post(
        "/posts",
        json={
            "title": "Protected Post",
            "content": "Testing invalid JWT",
            "published": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
