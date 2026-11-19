
# 1. Import Libraries
import os
import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

# 2. Select Test Database Before Importing App
os.environ["DB_HOST"] = "127.0.0.1"
os.environ["DB_PORT"] = "5433"
os.environ["DB_NAME"] = "fastapi_test"

# 3. Import Database and Models
from app.database import engine, Base, get_db
from app import models

# 4. Confirm Database Is Safe for Testing
assert engine.url.database == "fastapi_test", "Wrong database!"

with engine.connect() as connection:
    db_name = connection.execute(
        text("SELECT current_database()")
    ).scalar()

assert db_name == "fastapi_test", "Refusing to use development database!"

# 5. Import FastAPI Application
from app.main import app

# 6. Prepare Test Tables
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield

# 7. Create Isolated Test Session
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

# 8. Override Database Dependency
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

# 9. Preserve Previous Lesson Fixture
@pytest.fixture
def sample_numbers():
    return 10, 5
