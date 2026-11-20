
import pytest

# 1. Test Authenticated Post Creation
def test_create_post(authorized_client):
    response = authorized_client.post(
        "/posts",
        json={
            "title": "My First Test Post",
            "content": "Testing post creation",
            "published": True
        }
    )
    assert response.status_code == 201
    assert response.json()["title"] == "My First Test Post"

# 2. Test Create Post Without Authentication
def test_create_post_unauthorized(client):
    response = client.post(
        "/posts",
        json={
            "title": "Unauthorized Post",
            "content": "Testing authentication",
            "published": True
        }
    )
    assert response.status_code == 401

# 3. Test Invalid Post Input
def test_create_post_invalid(authorized_client):
    response = authorized_client.post(
        "/posts",
        json={
            "title": "Missing Content"
        }
    )
    assert response.status_code == 422

# 4. Test Retrieve Posts
def test_get_posts(client):
    response = client.get("/posts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 5. Test Pagination
@pytest.mark.parametrize(
    "limit",
    [1, 2, 5]
)
def test_pagination(client, limit):
    response = client.get(f"/posts?skip=0&limit={limit}")
    assert response.status_code == 200
    assert len(response.json()) <= limit

# 6. Test Nonexistent Post
def test_post_not_found(client):
    response = client.get("/posts/999999999")
    assert response.status_code == 404
