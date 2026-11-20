
import uuid
import pytest
from app import models
from app.oauth2 import create_access_token

POST_DATA = {
    "title": "Original Post",
    "content": "Original Content",
    "published": True
}

UPDATE_DATA = {
    "title": "Updated Post",
    "content": "Updated Content",
    "published": True
}

# 1. Create an Authenticated Post
@pytest.fixture
def test_post(authorized_client):
    response = authorized_client.post("/posts", json=POST_DATA)
    assert response.status_code == 201
    return response.json()

# 2. Create Another User's Token
@pytest.fixture
def other_token(client):
    email = f"other_{uuid.uuid4().hex[:12]}@example.com"
    response = client.post(
        "/users",
        json={"email": email, "password": "TestPass123!"}
    )
    assert response.status_code == 201

    return create_access_token(
        data={"user_id": response.json()["id"]}
    )

# 3. Test Creating Post Without JWT
def test_create_without_token(client):
    response = client.post("/posts", json=POST_DATA)
    assert response.status_code == 401

# 4. Test Creating Post With Invalid JWT
def test_create_invalid_token(client):
    response = client.post(
        "/posts",
        json=POST_DATA,
        headers={"Authorization": "Bearer invalid.token.value"}
    )
    assert response.status_code == 401

# 5. Test Creating Post With Valid JWT
def test_create_valid_token(authorized_client, test_user):
    response = authorized_client.post("/posts", json=POST_DATA)

    assert response.status_code == 201
    assert response.json()["title"] == POST_DATA["title"]
    assert response.json()["owner_id"] == test_user["id"]

# 6. Test Updating Post Without JWT
def test_update_without_token(authorized_client, test_post):
    response = authorized_client.put(
        f"/posts/{test_post['id']}",
        json=UPDATE_DATA,
        headers={"Authorization": ""}
    )
    assert response.status_code == 401

# 7. Test Deleting Post Without JWT
def test_delete_without_token(authorized_client, test_post):
    response = authorized_client.delete(
        f"/posts/{test_post['id']}",
        headers={"Authorization": ""}
    )
    assert response.status_code == 401

# 8. Test Another User Cannot Update Post
def test_update_other_user(authorized_client, test_post, other_token, db_session):
    response = authorized_client.put(
        f"/posts/{test_post['id']}",
        json=UPDATE_DATA,
        headers={"Authorization": f"Bearer {other_token}"}
    )
    assert response.status_code == 403

    db_session.expire_all()
    saved_post = db_session.query(models.Post).filter(
        models.Post.id == test_post["id"]
    ).first()

    assert saved_post is not None
    assert saved_post.title == POST_DATA["title"]
    assert saved_post.content == POST_DATA["content"]

# 9. Test Another User Cannot Delete Post
def test_delete_other_user(authorized_client, test_post, other_token, db_session):
    response = authorized_client.delete(
        f"/posts/{test_post['id']}",
        headers={"Authorization": f"Bearer {other_token}"}
    )
    assert response.status_code == 403

    db_session.expire_all()
    saved_post = db_session.query(models.Post).filter(
        models.Post.id == test_post["id"]
    ).first()

    assert saved_post is not None
