
import pytest
from app import models

# 1. Sample Post Data
POST_DATA = {
    "title": "Original Title",
    "content": "Original Content",
    "published": True
}

UPDATE_DATA = {
    "title": "Updated Title",
    "content": "Updated Content",
    "published": True
}

# 2. Create Reusable Test Post
@pytest.fixture
def test_post(authorized_client):
    response = authorized_client.post(
        "/posts",
        json=POST_DATA
    )
    assert response.status_code == 201
    return response.json()

# 3. Test CREATE
def test_create_post(authorized_client, db_session, test_user):
    response = authorized_client.post(
        "/posts",
        json=POST_DATA
    )

    assert response.status_code == 201
    post_id = response.json()["id"]

    db_session.expire_all()
    post = db_session.get(models.Post, post_id)

    assert post is not None
    assert post.title == POST_DATA["title"]
    assert post.content == POST_DATA["content"]
    assert post.owner_id == test_user["id"]

# 4. Test READ All Posts
def test_get_all_posts(authorized_client, test_post):
    response = authorized_client.get("/posts")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(
        post["id"] == test_post["id"]
        for post in response.json()
    )

# 5. Test READ Single Post
def test_get_single_post(authorized_client, test_post):
    response = authorized_client.get(
        f"/posts/{test_post['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == test_post["id"]
    assert response.json()["title"] == POST_DATA["title"]

# 6. Test UPDATE
def test_update_post(authorized_client, test_post, db_session):
    post_id = test_post["id"]

    response = authorized_client.put(
        f"/posts/{post_id}",
        json=UPDATE_DATA
    )
    assert response.status_code == 200

    db_session.expire_all()
    post = db_session.get(models.Post, post_id)

    assert post is not None
    assert post.title == UPDATE_DATA["title"]
    assert post.content == UPDATE_DATA["content"]

# 7. Test DELETE
def test_delete_post(authorized_client, test_post, db_session):
    post_id = test_post["id"]

    response = authorized_client.delete(
        f"/posts/{post_id}"
    )
    assert response.status_code in (200, 204)

    db_session.expire_all()
    post = db_session.get(models.Post, post_id)

    assert post is None

# 8. Test Full CRUD Lifecycle
def test_complete_crud(authorized_client, db_session):
    # CREATE
    created = authorized_client.post(
        "/posts",
        json=POST_DATA
    )
    assert created.status_code == 201
    post_id = created.json()["id"]

    # READ
    fetched = authorized_client.get(f"/posts/{post_id}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == POST_DATA["title"]

    # UPDATE
    updated = authorized_client.put(
        f"/posts/{post_id}",
        json=UPDATE_DATA
    )
    assert updated.status_code == 200

    db_session.expire_all()
    post = db_session.get(models.Post, post_id)
    assert post is not None
    assert post.title == UPDATE_DATA["title"]

    # DELETE
    deleted = authorized_client.delete(f"/posts/{post_id}")
    assert deleted.status_code in (200, 204)

    db_session.expire_all()
    assert db_session.get(models.Post, post_id) is None

# 9. Test READ Nonexistent Post
def test_read_missing_post(authorized_client):
    response = authorized_client.get("/posts/999999999")
    assert response.status_code == 404
