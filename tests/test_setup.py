import pytest
@pytest.fixture
def sample_data():
    print("\nSETUP: Creating data")
    data = {"title": "FastAPI", "status": "active"}

    yield data

    print("\nTEARDOWN: Cleaning data")
    data.clear()

def test_title(sample_data):
    assert sample_data["title"] == "FastAPI"

def test_status(sample_data):
    assert sample_data["status"] == "active"