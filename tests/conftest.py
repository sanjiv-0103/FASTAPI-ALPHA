
import os
import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

# 1. Configure Test Database
os.environ["DB_HOST"] = "127.0.0.1"
os.environ["DB_PORT"] = "5433"
os.environ["DB_NAME"] = "fastapi_test"

# 2. Import Database
from app.database import engine, Base, get_db
from app import models, oauth2

# 3. Verify Test Database
assert engine.url.database == "fastapi_test", "Wrong database!"

with engine.connect() as connection:
    db_name = connection.execute(
        text("SELECT current_database()")
    ).scalar()

assert db_name == "fastapi_test", "Refusing development database!"

# 4. Import FastAPI Application
from app.main import app

# 5. Initialize Test Database
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield

# 6. Database Session Fixture
@pytest.fixture
def db_session(setup_database):
    connection = engine.connect()
    transaction = connection.begin()

    db = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
        autoflush=False
    )

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()

# 7. TestClient Fixture
@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)

# 8. Sample Numbers Fixture
@pytest.fixture
def sample_numbers():
    return 10, 5

# 9. Test User Fixture
@pytest.fixture
def test_user(client):
    response = client.post(
        "/users",
        json={
            "email": "testuser@example.com",
            "password": "TestPass123!"
        }
    )

    assert response.status_code == 201

    return {
        **response.json(),
        "password": "TestPass123!"
    }

# 10. Valid JWT Fixture
@pytest.fixture
def token(test_user):
    return oauth2.create_access_token(
        data={"user_id": test_user["id"]}
    )

# 11. Authorized TestClient Fixture
@pytest.fixture
def authorized_client(client, token):
    original_headers = client.headers.copy()

    client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    try:
        yield client
    finally:
        client.headers.clear()
        client.headers.update(original_headers)
