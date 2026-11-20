
import uuid
import pytest
from app import models
from app.oauth2 import create_access_token

# 1. Create Test Post
@pytest.fixture
def test_post(authorized_client):
    response = authorized_client.post(
        "/posts",
        json={
            "title": "Original Title",
            "content": "Original Content",
            "published": True
        }
    )
    assert response.status_code == 201
    return response.json()

# 2. Helper for Updating Post
def update_post(client, post_id, token, data):
    return client.put(
        f"/posts/{post_id}",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )

# 3. Test Successful Update
def test_update_post(authorized_client, test_post):
    response = authorized_client.put(
        f"/posts/{test_post['id']}",
        json={
            "title": "Updated Title",
            "content": "Updated Content",
            "published": True
        }
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["content"] == "Updated Content"

# 4. Test Updated Post in Database
def test_update_database(authorized_client, test_post, db_session):
    response = authorized_client.put(
        f"/posts/{test_post['id']}",
        json={
            "title": "Database Update",
            "content": "Checking SQLAlchemy",
            "published": True
        }
    )
    assert response.status_code == 200

    saved_post = db_session.query(models.Post).filter(
        models.Post.id == test_post["id"]
    ).first()

    assert saved_post is not None
    assert saved_post.title == "Database Update"
    assert saved_post.content == "Checking SQLAlchemy"

# 5. Test Nonexistent Post
def test_update_missing_post(authorized_client):
    response = authorized_client.put(
        "/posts/999999999",
        json={
            "title": "Missing Post",
            "content": "Does not exist",
            "published": True
        }
    )
    assert response.status_code == 404

# 6. Test Missing JWT
def test_update_without_token(authorized_client, test_post):
    response = authorized_client.put(
        f"/posts/{test_post['id']}",
        json={
            "title": "Unauthorized Update",
            "content": "Missing JWT",
            "published": True
        },
        headers={"Authorization": ""}
    )
    assert response.status_code == 401

# 7. Test Invalid JWT
def test_update_invalid_token(authorized_client, test_post):
    response = authorized_client.put(
        f"/posts/{test_post['id']}",
        json={
            "title": "Invalid JWT",
            "content": "Testing authentication",
            "published": True
        },
        headers={"Authorization": "Bearer invalid.token.value"}
    )
    assert response.status_code == 401

# 8. Test Another User Cannot Update
def test_update_other_user(authorized_client, client, test_post):
    email = f"update_{uuid.uuid4().hex[:12]}@example.com"

    user_response = client.post(
        "/users",
        json={
            "email": email,
            "password": "TestPass123!"
        }
    )
    assert user_response.status_code == 201

    other_user = user_response.json()
    other_token = create_access_token(
        data={"user_id": other_user["id"]}
    )

    response = update_post(
        client,
        test_post["id"],
        other_token,
        {
            "title": "Hacked Title",
            "content": "Unauthorized modification",
            "published": True
        }
    )

    assert response.status_code == 403

# 9. Test Missing Required Content
def test_update_missing_content(authorized_client, test_post):
    response = authorized_client.put(
        f"/posts/{test_post['id']}",
        json={"title": "Only Title"}
    )
    assert response.status_code == 422

# 10. Test Invalid Title Type
@pytest.mark.parametrize(
    "title",
    [123, True, ["Invalid"], {"value": "Wrong"}]
)
def test_update_invalid_title(authorized_client, test_post, title):
    response = authorized_client.put(
        f"/posts/{test_post['id']}",
        json={
            "title": title,
            "content": "Valid content",
            "published": True
        }
    )
    assert response.status_code == 422

