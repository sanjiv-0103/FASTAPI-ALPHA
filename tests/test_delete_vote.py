
import uuid
import pytest
from sqlalchemy import func
from app import models
from app.oauth2 import create_access_token

# 1. Create Test Post
@pytest.fixture
def test_post(authorized_client):
    response = authorized_client.post(
        "/posts",
        json={
            "title": "Delete Vote Test",
            "content": "Testing vote removal",
            "published": True
        }
    )
    assert response.status_code == 201
    return response.json()

# 2. Helper to Send Vote Request
def vote_request(client, post_id, direction, token=None):
    headers = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    return client.post(
        "/vote/",
        json={"post_id": post_id, "dir": direction},
        headers=headers
    )

# 3. Helper to Count Votes
def count_votes(db_session, post_id, user_id):
    return db_session.query(func.count()).select_from(
        models.Vote
    ).filter(
        models.Vote.post_id == post_id,
        models.Vote.user_id == user_id
    ).scalar()

# 4. Remove Existing Vote
def test_delete_vote(authorized_client, test_post, test_user, db_session):
    post_id = test_post["id"]

    added = vote_request(authorized_client, post_id, 1)
    assert added.status_code == 201
    assert count_votes(db_session, post_id, test_user["id"]) == 1

    deleted = vote_request(authorized_client, post_id, 0)
    assert deleted.status_code == 201
    assert count_votes(db_session, post_id, test_user["id"]) == 0

# 5. Remove Nonexistent Vote
def test_delete_missing_vote(authorized_client, test_post):
    response = vote_request(
        authorized_client,
        test_post["id"],
        0
    )
    assert response.status_code == 404

# 6. Remove Vote Without JWT
def test_delete_vote_without_token(authorized_client, test_post):
    post_id = test_post["id"]

    assert vote_request(authorized_client, post_id, 1).status_code == 201

    response = authorized_client.post(
        "/vote/",
        json={"post_id": post_id, "dir": 0},
        headers={"Authorization": ""}
    )
    assert response.status_code == 401

# 7. Remove Vote With Invalid JWT
def test_delete_vote_invalid_token(authorized_client, test_post):
    post_id = test_post["id"]

    assert vote_request(authorized_client, post_id, 1).status_code == 201

    response = vote_request(
        authorized_client,
        post_id,
        0,
        token="invalid.jwt.value"
    )
    assert response.status_code == 401

# 8. Another User Cannot Remove Your Vote
def test_delete_other_users_vote(
    authorized_client, client, test_post, test_user, db_session
):
    post_id = test_post["id"]

    assert vote_request(authorized_client, post_id, 1).status_code == 201

    email = f"other_{uuid.uuid4().hex[:12]}@example.com"
    response = client.post(
        "/users",
        json={"email": email, "password": "TestPass123!"}
    )
    assert response.status_code == 201

    other_token = create_access_token(
        data={"user_id": response.json()["id"]}
    )

    response = vote_request(
        client,
        post_id,
        0,
        token=other_token
    )
    assert response.status_code == 404

    assert count_votes(
        db_session, post_id, test_user["id"]
    ) == 1

# 9. Vote Again After Removal
def test_vote_again_after_delete(authorized_client, test_post, test_user, db_session):
    post_id = test_post["id"]

    first = vote_request(authorized_client, post_id, 1)
    assert first.status_code == 201

    removed = vote_request(authorized_client, post_id, 0)
    assert removed.status_code == 201

    second = vote_request(authorized_client, post_id, 1)
    assert second.status_code == 201

    assert count_votes(
        db_session, post_id, test_user["id"]
    ) == 1

# 10. Delete One User's Vote Without Affecting Another
def test_delete_only_own_vote(
    authorized_client, client, test_post, test_user, db_session
):
    post_id = test_post["id"]

    assert vote_request(authorized_client, post_id, 1).status_code == 201

    email = f"voter_{uuid.uuid4().hex[:12]}@example.com"
    user_response = client.post(
        "/users",
        json={"email": email, "password": "TestPass123!"}
    )
    assert user_response.status_code == 201

    second_user_id = user_response.json()["id"]
    second_token = create_access_token(
        data={"user_id": second_user_id}
    )

    assert vote_request(
        client, post_id, 1, token=second_token
    ).status_code == 201

    deleted = vote_request(authorized_client, post_id, 0)
    assert deleted.status_code == 201

    assert count_votes(
        db_session, post_id, test_user["id"]
    ) == 0

    assert count_votes(
        db_session, post_id, second_user_id
    ) == 1
