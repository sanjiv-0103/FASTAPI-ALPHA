
# 1. Import Libraries
import uuid

# 2. Generate Unique Test Email
def make_email():
    return f"test_{uuid.uuid4().hex[:12]}@example.com"

# 3. Register Test User
def register_user(client, email, password="TestPass123!"):
    return client.post(
        "/users",
        json={"email": email, "password": password}
    )

# 4. Login Test User
def login_user(client, email, password="TestPass123!"):
    response = client.post(
        "/login",
        data={"username": email, "password": password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

# 5. Test Root Endpoint
def test_root_api(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

# 6. Test User Registration
def test_register_user(client):
    email = make_email()
    response = register_user(client, email)

    assert response.status_code == 201
    assert response.json()["email"] == email
    assert "password" not in response.json()

# 7. Test Login and JWT Token
def test_login(client):
    email = make_email()
    register_response = register_user(client, email)
    assert register_response.status_code == 201

    token = login_user(client, email)

    assert isinstance(token, str)
    assert len(token) > 0

# 8. Test Unauthorized Post Creation
def test_create_post_without_login(client):
    response = client.post(
        "/posts",
        json={
            "title": "Unauthorized Post",
            "content": "Testing JWT authentication",
            "published": True
        }
    )
    assert response.status_code == 401

# 9. Test Authenticated Post Creation
def test_create_post_with_login(client, db_session):
    email = make_email()
    user_response = register_user(client, email)
    assert user_response.status_code == 201

    user_id = user_response.json()["id"]
    token = login_user(client, email)

    response = client.post(
        "/posts",
        json={
            "title": "My Test Post",
            "content": "Testing post creation",
            "published": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    assert response.json()["title"] == "My Test Post"

    from app import models
    saved_post = db_session.query(models.Post).filter(
        models.Post.id == response.json()["id"]
    ).first()

    assert saved_post is not None
    assert saved_post.owner_id == user_id

# 10. Test Post Pagination
def test_get_posts_pagination(client):
    response = client.get("/posts?skip=0&limit=2")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 2

# 11. Test Adding and Removing Vote
def test_vote(client):
    email = make_email()
    register_response = register_user(client, email)
    assert register_response.status_code == 201

    token = login_user(client, email)
    headers = {"Authorization": f"Bearer {token}"}

    post_response = client.post(
        "/posts",
        json={
            "title": "Voting Test",
            "content": "Testing votes",
            "published": True
        },
        headers=headers
    )
    assert post_response.status_code == 201

    post_id = post_response.json()["id"]

    add_vote = client.post(
        "/vote/",
        json={"post_id": post_id, "dir": 1},
        headers=headers
    )
    assert add_vote.status_code == 201

    duplicate_vote = client.post(
        "/vote/",
        json={"post_id": post_id, "dir": 1},
        headers=headers
    )
    assert duplicate_vote.status_code == 409

    remove_vote = client.post(
        "/vote/",
        json={"post_id": post_id, "dir": 0},
        headers=headers
    )
    assert remove_vote.status_code == 201
