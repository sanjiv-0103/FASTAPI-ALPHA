
# 1. Test User Fixture
def test_user_creation(test_user):
    assert test_user["email"] == "testuser@example.com"
    assert test_user["id"] > 0

# 2. Test Token Fixture
def test_token_generation(token):
    assert isinstance(token, str)
    assert len(token) > 0

# 3. Test Authorized Client
def test_authorized_client(authorized_client):
    response = authorized_client.post(
        "/posts",
        json={
            "title": "Authenticated Test",
            "content": "Testing reusable JWT fixtures",
            "published": True
        }
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Authenticated Test"

# 4. Test Client Without Token
def test_unauthorized_client(client):
    response = client.post(
        "/posts",
        json={
            "title": "Unauthorized Test",
            "content": "Testing missing authentication",
            "published": True
        }
    )

    assert response.status_code == 401
