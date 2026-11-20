
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app import models
from app.config import settings
from app.oauth2 import create_access_token

# 1. Create Test Post
@pytest.fixture
def test_vote_post(authorized_client):
    response = authorized_client.post(
        "/posts",
        json={
            "title": "Vote Authentication Test",
            "content": "Testing JWT-based voting",
            "published": True
        }
    )

    assert response.status_code == 201
    return response.json()

# 2. Submit Vote Helper
def submit_vote(client, post_id, auth_token=None):
    headers = {
        "Authorization": f"Bearer {auth_token}" if auth_token else ""
    }

    return client.post(
        "/vote/",
        json={"post_id": post_id, "dir": 1},
        headers=headers
    )

# 3. Vote Without JWT
def test_vote_without_token(test_vote_post, client):
    response = submit_vote(
        client,
        test_vote_post["id"]
    )

    assert response.status_code == 401

# 4. Vote With Invalid JWT
@pytest.mark.parametrize(
    "invalid_token",
    ["invalid-token", "abc.def.ghi", "wrong.jwt.value"]
)
def test_vote_invalid_token(test_vote_post, client, invalid_token):
    response = submit_vote(
        client,
        test_vote_post["id"],
        invalid_token
    )

    assert response.status_code == 401

# 5. Vote With Expired JWT
def test_vote_expired_token(test_vote_post, client, test_user):
    expired_token = jwt.encode(
        {
            "user_id": test_user["id"],
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5)
        },
        settings.secret_key,
        algorithm=settings.algorithm
    )

    response = submit_vote(
        client,
        test_vote_post["id"],
        expired_token
    )

    assert response.status_code == 401

# 6. Vote With Valid JWT
def test_vote_valid_token(
    test_vote_post, authorized_client, test_user, db_session
):
    response = authorized_client.post(
        "/vote/",
        json={
            "post_id": test_vote_post["id"],
            "dir": 1
        }
    )

    assert response.status_code == 201

    vote = db_session.query(models.Vote).filter(
        models.Vote.post_id == test_vote_post["id"],
        models.Vote.user_id == test_user["id"]
    ).first()

    assert vote is not None

# 7. Vote Using Another User's JWT
def test_vote_second_user(test_vote_post, client, db_session):
    email = f"voter_{uuid.uuid4().hex[:12]}@example.com"

    response = client.post(
        "/users",
        json={
            "email": email,
            "password": "TestPass123!"
        }
    )

    assert response.status_code == 201

    second_user_id = response.json()["id"]

    second_token = create_access_token(
        data={"user_id": second_user_id}
    )

    response = submit_vote(
        client,
        test_vote_post["id"],
        second_token
    )

    assert response.status_code == 201

    vote = db_session.query(models.Vote).filter(
        models.Vote.post_id == test_vote_post["id"],
        models.Vote.user_id == second_user_id
    ).first()

    assert vote is not None

# 8. Reject Invalid Vote Direction
@pytest.mark.parametrize(
    "direction",
    [-1, 2, 5]
)
def test_vote_invalid_direction(
    test_vote_post, authorized_client, direction
):
    response = authorized_client.post(
        "/vote/",
        json={
            "post_id": test_vote_post["id"],
            "dir": direction
        }
    )

    assert response.status_code == 422
