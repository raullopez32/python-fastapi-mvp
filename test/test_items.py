from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_crud_flow():
    r = client.get("/items/")
    assert r.status_code == 200
    assert r.json() == []

    r = client.post("/items/", json={"name": "Laptop", "price": 1200})
    assert r.status_code == 201
    data = r.json()
    item_id = data["id"]
    assert data["name"] == "Laptop"

    r = client.get(f"/items/{item_id}")
    assert r.status_code == 200
    assert r.json()["price"] == 1200

    r = client.delete(f"/items/{item_id}")
    assert r.status_code == 204

    r = client.get(f"/items/{item_id}")
    assert r.status_code == 404
