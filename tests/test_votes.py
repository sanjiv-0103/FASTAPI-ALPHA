
import uuid
import pytest
from app import models
from app.oauth2 import create_access_token

# 1. Create a Post for Voting
@pytest.fixture
def test_post(authorized_client):
    response = authorized_client.post(
        "/posts",
        json={
            "title": "Voting Test Post",
            "content": "Testing voting functionality",
            "published": True
        }
    )
    assert response.status_code == 201
    return response.json()

# 2. Add Vote
def test_add_vote(authorized_client, test_post, db_session, test_user):
    response = authorized_client.post(
        "/vote/",
        json={"post_id": test_post["id"], "dir": 1}
    )

    assert response.status_code == 201

    vote = db_session.query(models.Vote).filter(
        models.Vote.post_id == test_post["id"],
        models.Vote.user_id == test_user["id"]
    ).first()

    assert vote is not None

# 3. Prevent Duplicate Vote
def test_duplicate_vote(authorized_client, test_post):
    data = {"post_id": test_post["id"], "dir": 1}

    first = authorized_client.post("/vote/", json=data)
    second = authorized_client.post("/vote/", json=data)

    assert first.status_code == 201
    assert second.status_code == 409

# 4. Remove Existing Vote
def test_remove_vote(authorized_client, test_post, db_session, test_user):
    data = {"post_id": test_post["id"], "dir": 1}
    authorized_client.post("/vote/", json=data)

    response = authorized_client.post(
        "/vote/",
        json={"post_id": test_post["id"], "dir": 0}
    )

    assert response.status_code == 201

    vote = db_session.query(models.Vote).filter(
        models.Vote.post_id == test_post["id"],
        models.Vote.user_id == test_user["id"]
    ).first()

    assert vote is None

# 5. Remove Nonexistent Vote
def test_remove_missing_vote(authorized_client, test_post):
    response = authorized_client.post(
        "/vote/",
        json={"post_id": test_post["id"], "dir": 0}
    )
    assert response.status_code == 404

# 6. Vote Without Authentication
def test_vote_unauthorized(client, test_post):
    response = client.post(
    "/vote/",
    json={"post_id": test_post["id"], "dir": 1},
    headers={"Authorization": ""}
    )
    assert response.status_code == 401

# 7. Vote on Nonexistent Post
def test_vote_missing_post(authorized_client):
    response = authorized_client.post(
        "/vote/",
        json={"post_id": 999999999, "dir": 1}
    )
    assert response.status_code == 404

# 8. Invalid Vote Direction
@pytest.mark.parametrize("direction", [-1, 2, 5])
def test_invalid_vote_direction(authorized_client, test_post, direction):
    response = authorized_client.post(
        "/vote/",
        json={"post_id": test_post["id"], "dir": direction}
    )
    assert response.status_code == 422

# 9. Different Users Can Vote
def test_multiple_users_vote(client, test_post):
    email = f"voter_{uuid.uuid4().hex[:12]}@example.com"

    user_response = client.post(
        "/users",
        json={"email": email, "password": "TestPass123!"}
    )
    assert user_response.status_code == 201

    second_user = user_response.json()
    second_token = create_access_token(
        data={"user_id": second_user["id"]}
    )

    response = client.post(
        "/vote/",
        json={"post_id": test_post["id"], "dir": 1},
        headers={"Authorization": f"Bearer {second_token}"}
    )

    assert response.status_code == 201
