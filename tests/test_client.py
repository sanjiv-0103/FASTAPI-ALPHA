
# 1. Import Libraries
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
import pytest

# 2. Create Test Application
app = FastAPI()

class Item(BaseModel):
    title: str
    price: float

# 3. Define Test Endpoints
@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/items/{id}")
def get_item(id: int):
    if id != 1:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": id, "title": "Python Book"}

@app.post("/items", status_code=201)
def create_item(item: Item):
    return item

# 4. Initialize TestClient
client = TestClient(app)

# 5. Test Root Endpoint
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

# 6. Test Existing Item
def test_get_item():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Python Book"

# 7. Test Missing Item
def test_get_invalid_item():
    response = client.get("/items/99")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

# 8. Test Item Creation
def test_create_item():
    data = {"title": "FastAPI Guide", "price": 299}
    response = client.post("/items", json=data)
    assert response.status_code == 201
    assert response.json()["title"] == "FastAPI Guide"

# 9. Test Invalid Input
def test_invalid_item():
    data = {"title": "FastAPI Guide", "price": "invalid"}
    response = client.post("/items", json=data)
    assert response.status_code == 422

# 10. Test Multiple Item IDs
@pytest.mark.parametrize(
    "item_id,expected",
    [
        (1, 200),
        (2, 404),
        (99, 404)
    ]
)
def test_item_ids(item_id, expected):
    response = client.get(f"/items/{item_id}")
    assert response.status_code == expected
