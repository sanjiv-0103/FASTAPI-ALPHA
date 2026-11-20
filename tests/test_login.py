
import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config import settings

# 1. Test Successful Login
def test_login_success(client, test_user):
    response = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]

# 2. Test Incorrect Password
def test_login_wrong_password(client, test_user):
    response = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": "WrongPassword123"
        }
    )
    assert response.status_code == 401

# 3. Test Unknown Email
def test_login_unknown_user(client):
    response = client.post(
        "/login",
        data={
            "username": "unknown_user@example.com",
            "password": "TestPass123!"
        }
    )
    assert response.status_code == 401

# 4. Test Missing Password
def test_login_missing_password(client, test_user):
    response = client.post(
        "/login",
        data={"username": test_user["email"]}
    )
    assert response.status_code == 422

# 5. Test Missing Username
def test_login_missing_username(client):
    response = client.post(
        "/login",
        data={"password": "TestPass123!"}
    )
    assert response.status_code == 422

# 6. Test Empty Credentials
def test_login_empty_credentials(client):
    response = client.post(
        "/login",
        data={"username": "", "password": ""}
    )
    assert response.status_code == 422

# 7. Test JWT Payload
def test_login_jwt_payload(client, test_user):
    response = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == 200

    token = response.json()["access_token"]
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm]
    )

    assert str(payload["user_id"]) == str(test_user["id"])
    assert "exp" in payload

# 8. Test Authenticated Request After Login
def test_login_protected_route(client, test_user):
    login_response = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/posts",
        json={
            "title": "Login Test Post",
            "content": "Testing JWT protected endpoint",
            "published": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201

# 9. Test Expired JWT
def test_login_expired_token(client, test_user):
    payload = {
        "user_id": test_user["id"],
        "exp": datetime.now(timezone.utc) - timedelta(minutes=5)
    }

    expired_token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    response = client.post(
        "/posts",
        json={
            "title": "Expired Token Post",
            "content": "Testing expired JWT",
            "published": True
        },
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401

# 10. Test Multiple Invalid Passwords
@pytest.mark.parametrize(
    "password",
    ["wrong", "123456", "invalidpassword"]
)
def test_login_invalid_passwords(client, test_user, password):
    response = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": password
        }
    )
    assert response.status_code == 401
