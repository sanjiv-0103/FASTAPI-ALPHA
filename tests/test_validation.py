
import pytest

# 1. Missing Title
def test_missing_title(authorized_client):
    response = authorized_client.post(
        "/posts",
        json={"content": "Valid content"}
    )
    assert response.status_code == 422

# 2. Missing Content
def test_missing_content(authorized_client):
    response = authorized_client.post(
        "/posts",
        json={"title": "Valid title"}
    )
    assert response.status_code == 422

# 3. Invalid Title Type
@pytest.mark.parametrize(
    "title",
    [123, True, ["Invalid"], {"name": "Wrong"}]
)
def test_invalid_title(authorized_client, title):
    response = authorized_client.post(
        "/posts",
        json={
            "title": title,
            "content": "Valid content"
        }
    )
    assert response.status_code == 422

# 4. Invalid Content Type
@pytest.mark.parametrize(
    "content",
    [123, False, ["Invalid"]]
)
def test_invalid_content(authorized_client, content):
    response = authorized_client.post(
        "/posts",
        json={
            "title": "Valid Title",
            "content": content
        }
    )
    assert response.status_code == 422

# 5. Invalid Published Value
def test_invalid_published(authorized_client):
    response = authorized_client.post(
        "/posts",
        json={
            "title": "Valid Title",
            "content": "Valid Content",
            "published": "not-a-boolean"
        }
    )
    assert response.status_code == 422

# 6. Empty JSON Body
def test_empty_body(authorized_client):
    response = authorized_client.post(
        "/posts",
        json={}
    )
    assert response.status_code == 422
