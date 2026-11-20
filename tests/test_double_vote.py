
import uuid
import pytest
from sqlalchemy import func
from app import models
from app.oauth2 import create_access_token

# 1. Create a Test Post
@pytest.fixture
def test_post(authorized_client):
    response = authorized_client.post(
        "/posts",
        json={
            "title": "Double Vote Test",
            "content": "Testing duplicate vote prevention",
            "published": True
        }
    )
    assert response.status_code == 201
    return response.json()

# 2. Helper to Add a Vote
def add_vote(client, post_id, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    return client.post(
        "/vote/",
        json={"post_id": post_id, "dir": 1},
        headers=headers
    )

# 3. Test First Vote
def test_first_vote(authorized_client, test_post, test_user, db_session):
    response = add_vote(authorized_client, test_post["id"])

    assert response.status_code == 201

    count = db_session.query(func.count()).select_from(models.Vote).filter(
        models.Vote.post_id == test_post["id"],
        models.Vote.user_id == test_user["id"]
    ).scalar()

    assert count == 1

# 4. Test Duplicate Vote
def test_duplicate_vote(authorized_client, test_post, test_user, db_session):
    first = add_vote(authorized_client, test_post["id"])
    second = add_vote(authorized_client, test_post["id"])

    assert first.status_code == 201
    assert second.status_code == 409

    count = db_session.query(func.count()).select_from(models.Vote).filter(
        models.Vote.post_id == test_post["id"],
        models.Vote.user_id == test_user["id"]
    ).scalar()

    assert count == 1

# 5. Test Multiple Users Voting
def test_different_users_vote(authorized_client, client, test_post, db_session):
    first = add_vote(authorized_client, test_post["id"])
    assert first.status_code == 201

    email = f"voter_{uuid.uuid4().hex[:12]}@example.com"
    response = client.post(
        "/users",
        json={"email": email, "password": "TestPass123!"}
    )
    assert response.status_code == 201

    second_token = create_access_token(
        data={"user_id": response.json()["id"]}
    )

    second = add_vote(client, test_post["id"], second_token)
    assert second.status_code == 201

    count = db_session.query(func.count()).select_from(models.Vote).filter(
        models.Vote.post_id == test_post["id"]
    ).scalar()

    assert count == 2

# 6. Test One User Voting on Different Posts
def test_vote_different_posts(authorized_client, db_session, test_user):
    post_ids = []

    for i in range(2):
        response = authorized_client.post(
            "/posts",
            json={
                "title": f"Post {i + 1}",
                "content": "Multiple post voting test",
                "published": True
            }
        )
        assert response.status_code == 201
        post_ids.append(response.json()["id"])

    for post_id in post_ids:
        response = add_vote(authorized_client, post_id)
        assert response.status_code == 201

    count = db_session.query(func.count()).select_from(models.Vote).filter(
        models.Vote.user_id == test_user["id"]
    ).scalar()

    assert count == 2

# 7. Test Duplicate Vote Does Not Create Extra Row
def test_duplicate_vote_integrity(
    authorized_client, test_post, test_user, db_session
):
    add_vote(authorized_client, test_post["id"])

    for _ in range(3):
        response = add_vote(authorized_client, test_post["id"])
        assert response.status_code == 409

    count = db_session.query(func.count()).select_from(models.Vote).filter(
        models.Vote.post_id == test_post["id"],
        models.Vote.user_id == test_user["id"]
    ).scalar()

    assert count == 1
