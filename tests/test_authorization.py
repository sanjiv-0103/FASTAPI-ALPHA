
import uuid
import pytest

def create_user(client):
    email = f"user_{uuid.uuid4().hex[:12]}@example.com"
    response = client.post(
        "/users",
        json={"email": email, "password": "TestPass123!"}
    )
    assert response.status_code == 201
    return response.json()

def get_token(client, user_id):
    from app.oauth2 import create_access_token
    return create_access_token(data={"user_id": user_id})

def create_post(client, token):
    response = client.post(
        "/posts",
        json={
            "title": "Authorization Test",
            "content": "Testing post ownership",
            "published": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    return response.json()

# 1. Missing JWT
def test_missing_jwt(client):
    response = client.post(
        "/posts",
        json={"title": "Test", "content": "No token"}
    )
    assert response.status_code == 401

# 2. Invalid JWT
@pytest.mark.parametrize(
    "token",
    ["invalid-token", "abc.def.ghi", "expired.invalid.token"]
)
def test_invalid_jwt(client, token):
    response = client.post(
        "/posts",
        json={"title": "Test", "content": "Invalid token"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401

# 3. Valid JWT
def test_valid_jwt(client):
    user = create_user(client)
    token = get_token(client, user["id"])
    post = create_post(client, token)
    assert post["title"] == "Authorization Test"

# 4. Cannot Update Another User's Post
def test_update_other_users_post(client):
    user1 = create_user(client)
    user2 = create_user(client)

    token1 = get_token(client, user1["id"])
    token2 = get_token(client, user2["id"])

    post = create_post(client, token1)

    response = client.put(
        f"/posts/{post['id']}",
        json={
            "title": "Unauthorized Update",
            "content": "Changed by another user",
            "published": True
        },
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 403

# 5. Cannot Delete Another User's Post
def test_delete_other_users_post(client):
    user1 = create_user(client)
    user2 = create_user(client)

    token1 = get_token(client, user1["id"])
    token2 = get_token(client, user2["id"])

    post = create_post(client, token1)

    response = client.delete(
        f"/posts/{post['id']}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 403

# 6. Nonexistent Post
def test_missing_post(client):
    response = client.get("/posts/999999999")
    assert response.status_code == 404
